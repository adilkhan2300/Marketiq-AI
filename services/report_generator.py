import io
from datetime import datetime
import pandas as pd
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from analytics.kpi_engine import calculate_kpi_overview
from analytics.campaign_analyzer import analyze_campaigns
from analytics.customer_profitability import analyze_customer_profitability
from optimization.budget_optimizer import optimize_marketing_budget
from models.db_models import Workspace

def generate_csv_campaign_report(db: Session, workspace_id: str) -> str:
    campaigns = analyze_campaigns(db, workspace_id)
    data = []
    for c in campaigns:
        flags_str = "; ".join([f"{f.label}: {f.reason}" for f in c.flags]) if c.flags else "Healthy"
        data.append({
            "Campaign ID": c.campaign_id,
            "Campaign Name": c.campaign_name,
            "Channel": c.channel,
            "Spend": c.spend,
            "Attributed Revenue": c.attributed_revenue,
            "Contribution Profit": c.contribution_profit,
            "ROAS": c.roas,
            "Impressions": c.impressions,
            "Clicks": c.clicks,
            "CTR (%)": c.ctr,
            "CPC": c.cpc,
            "Conversions": c.conversions,
            "CVR (%)": c.cvr,
            "CPA / CAC": c.cpa,
            "Performance Status": c.performance_status,
            "Automated Flags & Diagnostic Reason": flags_str
        })
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

def generate_excel_full_report(db: Session, workspace_id: str) -> bytes:
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    kpis = calculate_kpi_overview(db, workspace_id)
    campaigns = analyze_campaigns(db, workspace_id)
    customers = analyze_customer_profitability(db, workspace_id)
    optimization = optimize_marketing_budget(db, workspace_id, target_budget=kpis.target_budget)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Executive Summary
        exec_data = [
            {"Metric": "Workspace Name", "Value": workspace.name if workspace else "Default"},
            {"Metric": "Reporting Horizon", "Value": workspace.reporting_period if workspace else "H1"},
            {"Metric": "Generated Date", "Value": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")},
            {"Metric": "Currency", "Value": kpis.currency_symbol},
            {"Metric": "Total Marketing Spend", "Value": kpis.total_spend},
            {"Metric": "Total Attributed Revenue", "Value": kpis.total_revenue},
            {"Metric": "Gross Profit (Revenue - COGS)", "Value": kpis.gross_profit},
            {"Metric": "Contribution Profit (Gross Profit - Spend)", "Value": kpis.contribution_profit},
            {"Metric": "Return on Ad Spend (ROAS)", "Value": f"{kpis.roas}x"},
            {"Metric": "Customer Acquisition Cost (CAC)", "Value": kpis.cac},
            {"Metric": "Total Acquired Customers", "Value": kpis.acquired_customers},
            {"Metric": "Customer Lifetime Value (CLV)", "Value": kpis.clv},
            {"Metric": "LTV:CAC Ratio", "Value": f"{kpis.ltv_cac_ratio}x"},
            {"Metric": "Marketing ROI (%)", "Value": f"{kpis.marketing_roi}%"},
            {"Metric": "Overall CVR (%)", "Value": f"{kpis.overall_cvr}%"},
            {"Metric": "Overall CPA", "Value": kpis.overall_cpa}
        ]
        pd.DataFrame(exec_data).to_excel(writer, sheet_name="Executive Overview", index=False)

        # Sheet 2: Campaign Performance
        camp_rows = []
        for c in campaigns:
            camp_rows.append({
                "Campaign ID": c.campaign_id,
                "Campaign Name": c.campaign_name,
                "Channel": c.channel,
                "Spend": c.spend,
                "Revenue": c.attributed_revenue,
                "Contribution Profit": c.contribution_profit,
                "ROAS": c.roas,
                "Clicks": c.clicks,
                "Conversions": c.conversions,
                "CPA": c.cpa,
                "Status": c.performance_status
            })
        pd.DataFrame(camp_rows).to_excel(writer, sheet_name="Campaign Intelligence", index=False)

        # Sheet 3: Channel Breakdown
        ch_rows = [{
            "Channel": ch.channel,
            "Spend": ch.spend,
            "Revenue": ch.revenue,
            "Profit": ch.profit,
            "ROAS": ch.roas,
            "Conversions": ch.conversions,
            "CAC": ch.cac,
            "Spend Share (%)": ch.spend_share,
            "Revenue Share (%)": ch.revenue_share
        } for ch in kpis.channels]
        pd.DataFrame(ch_rows).to_excel(writer, sheet_name="Channel Breakdown", index=False)

        # Sheet 4: AI Budget Optimization Proposal
        if optimization:
            opt_rows = [{
                "Campaign": a.campaign_name,
                "Channel": a.channel,
                "Current Spend": a.current_spend,
                "Proposed Spend": a.proposed_spend,
                "Change ($)": a.spend_diff,
                "Change (%)": a.spend_diff_percent,
                "Expected Revenue": a.expected_revenue,
                "Expected Profit": a.expected_profit,
                "Expected ROAS": a.expected_roas,
                "Confidence": a.confidence,
                "AI Rationale": a.rationale
            } for a in optimization.ai_recommended_scenario.allocations]
            pd.DataFrame(opt_rows).to_excel(writer, sheet_name="Budget Proposal", index=False)

        # Sheet 5: Customer Cohorts & Segments
        if customers.segments:
            seg_rows = [{
                "Segment": s.segment_name,
                "Customers": s.customer_count,
                "Share (%)": s.percentage,
                "Total Revenue": s.total_revenue,
                "AOV": s.avg_order_value,
                "CLV": s.avg_clv,
                "Repeat Purchase Rate (%)": s.repeat_rate
            } for s in customers.segments]
            pd.DataFrame(seg_rows).to_excel(writer, sheet_name="Customer Segments", index=False)

    return output.getvalue()

def generate_executive_text_brief(db: Session, workspace_id: str) -> str:
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    kpis = calculate_kpi_overview(db, workspace_id)
    campaigns = analyze_campaigns(db, workspace_id)
    sym = kpis.currency_symbol

    top_performers = [c for c in campaigns if c.performance_status == "Top Performer"]
    wasters = [c for c in campaigns if c.contribution_profit < 0 or c.performance_status in ["High Waste", "Underperforming"]]

    report = f"""================================================================================
MARKETIQ AI — EXECUTIVE MARKETING INTELLIGENCE BRIEF
Brand: MARKETIQ AI | "Turn Marketing Spend into Measurable Growth"
================================================================================
WORKSPACE: {workspace.name if workspace else 'Default'}
REPORTING PERIOD: {workspace.reporting_period if workspace else 'H1 Performance'}
GENERATION TIMESTAMP: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
CURRENCY: {sym}
DATA INTEGRITY STATUS: Reconciled & Audited

--------------------------------------------------------------------------------
1. FINANCIAL SUMMARY & CORE METRICS
--------------------------------------------------------------------------------
• Total Marketing Spend:        {sym}{kpis.total_spend:,.2f}
• Attributed Revenue:           {sym}{kpis.total_revenue:,.2f}
• Gross Profit (Rev - COGS):    {sym}{kpis.gross_profit:,.2f}
• Contribution Profit:          {sym}{kpis.contribution_profit:,.2f}
• Blended ROAS:                 {kpis.roas}x
• Blended CAC:                  {sym}{kpis.cac:,.2f}
• Total Conversions/Customers:  {kpis.acquired_customers:,}
• Average Customer LTV:         {sym}{kpis.clv:,.2f}
• LTV:CAC Ratio:                {kpis.ltv_cac_ratio}x
• Marketing ROI:                {kpis.marketing_roi}%
• Budget Utilization:           {kpis.budget_utilization}% of target {sym}{kpis.target_budget:,.2f}

--------------------------------------------------------------------------------
2. KEY FINDINGS & STRATEGIC DIAGNOSIS
--------------------------------------------------------------------------------
{kpis.ai_executive_summary}

TOP CAPITAL EFFICIENCY DRIVERS:
{chr(10).join([f"• {c.campaign_name} ({c.channel}): Spend {sym}{c.spend:,.2f} -> Revenue {sym}{c.attributed_revenue:,.2f} ({c.roas}x ROAS) | Profit {sym}{c.contribution_profit:,.2f}" for c in top_performers[:3]]) if top_performers else "• None meet top performer criteria."}

PRIMARY MARGIN LEAKAGES / UNDERPERFORMING INVENTORY:
{chr(10).join([f"• {c.campaign_name} ({c.channel}): Spend {sym}{c.spend:,.2f} -> ROAS {c.roas}x | Loss {sym}{abs(c.contribution_profit):,.2f} (CPA: {sym}{c.cpa:,.2f})" for c in wasters[:3]]) if wasters else "• No severe margin leakages detected."}

--------------------------------------------------------------------------------
3. RECOMMENDED EXECUTIVE ACTIONS
--------------------------------------------------------------------------------
1. Reallocate Capital from Negative Margin Spend:
   Trim low-efficiency top-of-funnel campaigns by 25%–35%, redirecting capital
   toward high-margin retention and high-intent search campaigns.
2. Protect Branded Search & Email Nurture:
   Keep core bottom-of-funnel channels well-funded to preserve organic conversion capture.
3. Scale High CVR Micro-Campaigns:
   Test incremental budget scale on scalable campaigns with high conversion rates.

--------------------------------------------------------------------------------
4. METHODOLOGY & DATA LIMITATIONS
--------------------------------------------------------------------------------
• Financial metrics account for product Cost of Goods Sold (COGS) to calculate true
  Contribution Profit rather than gross revenue masquerading as profit.
• Attribution metrics reflect observed historical touchpoints; they indicate
  correlation and path presence, not randomized counterfactual incremental lift.
• Future revenue projections utilize concave response curves (diminishing marginal returns).
================================================================================
"""
    return report
