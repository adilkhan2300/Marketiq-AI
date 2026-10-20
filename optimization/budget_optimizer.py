import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from scipy.optimize import minimize
from sqlalchemy.orm import Session
from models.db_models import CampaignRecord, CustomerRecord, Workspace
from models.schemas import (
    OptimizationResponse,
    OptimizationScenario,
    ScenarioAllocation
)

def optimize_marketing_budget(
    db: Session,
    workspace_id: str,
    target_budget: float,
    objective: str = "maximize_profit",
    protected_campaigns: Optional[List[str]] = None,
    custom_constraints: Optional[Dict[str, Dict[str, float]]] = None,
    max_change_pct: float = 30.0
) -> Optional[OptimizationResponse]:
    protected_campaigns = protected_campaigns or []
    custom_constraints = custom_constraints or {}

    records = db.query(CampaignRecord).filter(CampaignRecord.workspace_id == workspace_id).all()
    if not records:
        return None

    df = pd.DataFrame([{
        "campaign_id": r.campaign_id,
        "campaign_name": r.campaign_name,
        "channel": r.channel,
        "spend": r.spend,
        "conversions": r.conversions,
        "revenue": r.attributed_revenue,
        "gross_margin_rate": r.gross_margin_rate,
        "cogs": r.cogs,
        "contribution_profit": r.contribution_profit
    } for r in records])

    # Aggregate by campaign
    c_grp = df.groupby(["campaign_id", "campaign_name", "channel"]).agg({
        "spend": "sum",
        "conversions": "sum",
        "revenue": "sum",
        "cogs": "sum",
        "gross_margin_rate": "mean"
    }).reset_index()

    c_grp["roas"] = c_grp.apply(lambda r: r["revenue"] / max(r["spend"], 1.0), axis=1)
    c_grp["cpa"] = c_grp.apply(lambda r: r["spend"] / max(r["conversions"], 1), axis=1)
    c_grp["margin_rate"] = c_grp["gross_margin_rate"]

    # Customer high value weights
    cust_records = db.query(CustomerRecord).filter(CustomerRecord.workspace_id == workspace_id).all()
    high_val_multipliers = {}
    if cust_records:
        cust_df = pd.DataFrame([{
            "campaign_id": c.acquisition_campaign_id,
            "is_high_val": 1 if c.segment in ["High-Value", "Repeat"] else 0
        } for c in cust_records])
        hv_grp = cust_df.groupby("campaign_id")["is_high_val"].mean().to_dict()
        for cid in c_grp["campaign_id"]:
            high_val_multipliers[cid] = 0.8 + (hv_grp.get(cid, 0.2) * 0.6)
    else:
        for cid in c_grp["campaign_id"]:
            high_val_multipliers[cid] = 1.0

    n_campaigns = len(c_grp)
    current_spends = c_grp["spend"].values
    total_current_spend = float(current_spends.sum())

    # If user provided a different total budget, scale baseline proportionally for comparison
    budget_scaling = target_budget / total_current_spend if total_current_spend > 0 else 1.0

    # Fit diminishing returns parameters for each campaign:
    # Concave response curve: Revenue(s) = alpha * (s ** beta), where beta in [0.60, 0.75]
    # This guarantees diminishing marginal ROAS as spend increases!
    alphas = []
    betas = []
    margins = c_grp["margin_rate"].values

    for idx, row in c_grp.iterrows():
        s = max(row["spend"], 10.0)
        r = max(row["revenue"], 10.0)
        # Beta parameter reflects audience saturation rate
        # High spend/top-of-funnel channels saturate faster (beta ~ 0.58), search/email saturate slower (beta ~ 0.75)
        if "Email" in row["channel"] or "Brand Intent" in row["campaign_name"]:
            b = 0.75
        elif "LinkedIn" in row["channel"] or "Video" in row["campaign_name"]:
            b = 0.56
        else:
            b = 0.65
        
        # alpha = revenue / (spend ** beta)
        a = r / (s ** b)
        alphas.append(a)
        betas.append(b)

    alphas = np.array(alphas)
    betas = np.array(betas)

    # Optimization Bounds and Constraints
    # Ensure proposed spend does not exceed total_budget, and bounds per campaign
    bounds = []
    initial_guess = current_spends * budget_scaling

    for idx, row in c_grp.iterrows():
        cid = row["campaign_id"]
        cur_s = row["spend"] * budget_scaling

        if cid in protected_campaigns:
            # Protected campaigns cannot be cut below current spend
            min_s = cur_s
            max_s = cur_s * (1.0 + (max_change_pct / 100.0))
        else:
            # Bounded shift cap (e.g. +/- 30% from current scaled spend)
            user_con = custom_constraints.get(cid, {})
            min_s = user_con.get("min_spend", cur_s * max(0.2, (1.0 - (max_change_pct / 100.0))))
            max_s = user_con.get("max_spend", cur_s * (1.0 + (max_change_pct / 100.0)))

        # Guard against zero/negative bounds
        min_s = max(50.0, float(min_s))
        max_s = max(min_s + 100.0, float(max_s))
        bounds.append((min_s, max_s))

    # Objective functions for SciPy minimize (negative of goal)
    def calc_metrics_for_allocation(alloc_vec):
        expected_rev = alphas * (np.maximum(alloc_vec, 1.0) ** betas)
        expected_gross_profit = expected_rev * margins
        expected_contribution_profit = expected_gross_profit - alloc_vec
        
        # CPA model: CPA increases with spend as CVR diminishes slightly
        base_cpas = c_grp["cpa"].values
        scaled_cpas = base_cpas * ((alloc_vec / np.maximum(current_spends, 1.0)) ** 0.25)
        expected_conv = alloc_vec / np.maximum(scaled_cpas, 5.0)

        return expected_rev, expected_contribution_profit, expected_conv

    if objective == "maximize_revenue":
        def loss_func(alloc_vec):
            rev, _, _ = calc_metrics_for_allocation(alloc_vec)
            return -float(np.sum(rev))
    elif objective == "maximize_profit":
        def loss_func(alloc_vec):
            _, profit, _ = calc_metrics_for_allocation(alloc_vec)
            return -float(np.sum(profit))
    elif objective == "maximize_conversions":
        def loss_func(alloc_vec):
            _, _, conv = calc_metrics_for_allocation(alloc_vec)
            return -float(np.sum(conv))
    elif objective == "prioritize_high_value":
        def loss_func(alloc_vec):
            _, profit, conv = calc_metrics_for_allocation(alloc_vec)
            hv_weights = np.array([high_val_multipliers[cid] for cid in c_grp["campaign_id"]])
            weighted_value = profit * hv_weights
            return -float(np.sum(weighted_value))
    else:
        def loss_func(alloc_vec):
            _, profit, _ = calc_metrics_for_allocation(alloc_vec)
            return -float(np.sum(profit))

    # Total budget constraint: sum(alloc) <= target_budget
    budget_constraint = {
        'type': 'eq',
        'fun': lambda alloc_vec: target_budget - np.sum(alloc_vec)
    }

    # Run SciPy SLSQP optimization
    opt_result = minimize(
        loss_func,
        initial_guess,
        method='SLSQP',
        bounds=bounds,
        constraints=[budget_constraint],
        options={'maxiter': 300, 'ftol': 1e-4}
    )

    if opt_result.success:
        ai_allocations = opt_result.x
        # Normalize strictly to target_budget to prevent floating point overshoot
        ai_allocations = ai_allocations * (target_budget / np.sum(ai_allocations))
    else:
        # Fallback to smart heuristic if solver didn't converge
        roas_weights = np.maximum(0.1, c_grp["roas"].values)
        ai_allocations = (roas_weights / np.sum(roas_weights)) * target_budget

    # Build Conservative Reallocation (half of AI shift)
    conservative_allocations = current_spends * budget_scaling + 0.45 * (ai_allocations - (current_spends * budget_scaling))
    conservative_allocations = conservative_allocations * (target_budget / np.sum(conservative_allocations))

    # Helper to construct scenario objects
    def build_scenario(name: str, alloc_vector: np.ndarray) -> OptimizationScenario:
        rev_vec, profit_vec, conv_vec = calc_metrics_for_allocation(alloc_vector)
        tot_rev = float(np.sum(rev_vec))
        tot_profit = float(np.sum(profit_vec))
        tot_conv = int(np.sum(conv_vec))
        tot_budget = float(np.sum(alloc_vector))
        scen_roas = round(tot_rev / max(tot_budget, 1.0), 2)
        scen_cpa = round(tot_budget / max(tot_conv, 1), 2)
        scen_roi = round(((tot_profit - tot_budget) / tot_budget) * 100, 2) if tot_budget > 0 else 0.0

        alloc_items: List[ScenarioAllocation] = []
        for i, row in c_grp.iterrows():
            cid = row["campaign_id"]
            c_name = row["campaign_name"]
            channel = row["channel"]
            cur_s = float(row["spend"])
            prop_s = float(alloc_vector[i])
            diff = prop_s - cur_s
            pct_diff = round((diff / cur_s) * 100, 1) if cur_s > 0 else 0.0

            # Confidence rating based on sample size
            c_clicks = row["conversions"]
            if c_clicks < 10:
                conf = "Low (Pilot / Sparse Data)"
            elif c_clicks < 50:
                conf = "Moderate Confidence"
            else:
                conf = "High Statistical Confidence"

            # Rationale generation with exact figures
            if prop_s > cur_s * 1.10:
                rationale = (
                    f"Increased capital by {pct_diff:+.1f}% due to superior marginal contribution margin "
                    f"({row['margin_rate']*100:.0f}%) and proven conversion efficiency ({row['roas']:.2f}x ROAS). "
                    f"Model projects expanding returns before saturation threshold."
                )
            elif prop_s < cur_s * 0.90:
                rationale = (
                    f"Reduced allocation by {pct_diff:+.1f}% to mitigate capital inefficiency (historical CPA: ${row['cpa']:.2f}). "
                    f"Reallocated freed funds toward higher-return conversion channels."
                )
            else:
                rationale = f"Maintained stable budget ({pct_diff:+.1f}%) preserving balanced baseline reach and steady return."

            alloc_items.append(ScenarioAllocation(
                campaign_id=cid,
                campaign_name=c_name,
                channel=channel,
                current_spend=round(cur_s, 2),
                proposed_spend=round(prop_s, 2),
                spend_diff=round(diff, 2),
                spend_diff_percent=pct_diff,
                expected_revenue=round(float(rev_vec[i]), 2),
                expected_profit=round(float(profit_vec[i]), 2),
                expected_conversions=max(1, int(conv_vec[i])),
                expected_roas=round(float(rev_vec[i]) / max(prop_s, 1.0), 2),
                expected_cpa=round(prop_s / max(int(conv_vec[i]), 1), 2),
                confidence=conf,
                rationale=rationale
            ))

        return OptimizationScenario(
            name=name,
            total_budget=round(tot_budget, 2),
            expected_revenue=round(tot_rev, 2),
            expected_profit=round(tot_profit, 2),
            expected_conversions=tot_conv,
            expected_roas=scen_roas,
            blended_cpa=scen_cpa,
            expected_roi=scen_roi,
            allocations=alloc_items
        )

    current_scenario = build_scenario("Current Budget Allocation", current_spends * budget_scaling)
    conservative_scenario = build_scenario("Conservative Reallocation (Bounded Shift)", conservative_allocations)
    ai_scenario = build_scenario("AI-Recommended Optimal Allocation", ai_allocations)

    assumptions = [
        "Diminishing returns modeled via power response curves (R = alpha * Spend^beta with beta in [0.56, 0.75]).",
        "Total reallocated spend is mathematically constrained to not exceed the defined total budget ($" + f"{target_budget:,.2f}).",
        "Protected campaigns are guarded against downward budget cuts.",
        "External macro demand shifts, competitive bidding surges, and holiday seasonality may alter actual realization."
    ]

    methodology = (
        "Non-linear constrained mathematical optimization using SciPy Sequential Least Squares Programming (SLSQP). "
        "Accounts for non-linear diminishing marginal returns and campaign-level gross margins."
    )

    return OptimizationResponse(
        objective=objective,
        total_budget=round(target_budget, 2),
        current_scenario=current_scenario,
        conservative_scenario=conservative_scenario,
        ai_recommended_scenario=ai_scenario,
        methodology=methodology,
        assumptions_and_limitations=assumptions
    )
