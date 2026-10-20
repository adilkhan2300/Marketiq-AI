import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.db_models import CampaignRecord, Workspace
from models.schemas import CampaignIntelligenceItem, CampaignFlag

def analyze_campaigns(
    db: Session,
    workspace_id: str,
    channel_filter: Optional[str] = None,
    sort_by: str = "spend",
    sort_desc: bool = True
) -> List[CampaignIntelligenceItem]:
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    currency_symbol = workspace.currency_symbol if workspace else "$"

    query = db.query(CampaignRecord).filter(CampaignRecord.workspace_id == workspace_id)
    if channel_filter and channel_filter != "All Channels":
        query = query.filter(CampaignRecord.channel == channel_filter)

    records = query.all()
    if not records:
        return []

    df = pd.DataFrame([{
        "date": r.date,
        "campaign_id": r.campaign_id,
        "campaign_name": r.campaign_name,
        "channel": r.channel,
        "impressions": r.impressions,
        "clicks": r.clicks,
        "spend": r.spend,
        "conversions": r.conversions,
        "revenue": r.attributed_revenue,
        "gross_margin_rate": r.gross_margin_rate,
        "cogs": r.cogs,
        "contribution_profit": r.contribution_profit
    } for r in records])

    avg_spend = df.groupby("campaign_id")["spend"].sum().mean()
    avg_cpa = df["spend"].sum() / max(df["conversions"].sum(), 1)

    campaign_groups = df.groupby(["campaign_id", "campaign_name", "channel"])
    results: List[CampaignIntelligenceItem] = []

    for (c_id, c_name, channel), group in campaign_groups:
        impressions = int(group["impressions"].sum())
        clicks = int(group["clicks"].sum())
        spend = float(group["spend"].sum())
        conversions = int(group["conversions"].sum())
        revenue = float(group["revenue"].sum())
        cogs = float(group["cogs"].sum())
        gross_margin_rate = float(group["gross_margin_rate"].mean())
        contribution_profit = float((revenue - cogs) - spend)

        ctr = round((clicks / impressions) * 100, 2) if impressions > 0 else 0.0
        cpc = round(spend / clicks, 2) if clicks > 0 else 0.0
        cvr = round((conversions / clicks) * 100, 2) if clicks > 0 else 0.0
        cpa = round(spend / conversions, 2) if conversions > 0 else 0.0
        roas = round(revenue / spend, 2) if spend > 0 else 0.0
        campaign_roi = round(((contribution_profit - spend) / spend) * 100, 2) if spend > 0 else 0.0

        flags: List[CampaignFlag] = []

        # 1. Insufficient data flag
        if clicks < 50 or len(group) < 15:
            flags.append(CampaignFlag(
                type="info",
                label="Insufficient Data",
                reason=f"Only {clicks} clicks and {conversions} conversions recorded across {len(group)} days. Statistical significance too low for aggressive decisions."
            ))

        # 2. Revenue positive but negative contribution profit
        if revenue > 5000 and contribution_profit < 0:
            flags.append(CampaignFlag(
                type="danger",
                label="Negative Contribution Profit",
                reason=f"Generated {currency_symbol}{revenue:,.2f} revenue, but incurred {currency_symbol}{spend:,.2f} ad spend and {currency_symbol}{cogs:,.2f} COGS, producing a net loss of {currency_symbol}{abs(contribution_profit):,.2f}."
            ))

        # 3. High spend with low conversions
        if spend > (avg_spend * 0.8) and conversions < 25:
            flags.append(CampaignFlag(
                type="danger",
                label="High Spend, Low Conversions",
                reason=f"Spent {currency_symbol}{spend:,.2f} but acquired only {conversions} conversions (CPA: {currency_symbol}{cpa:,.2f} vs portfolio avg {currency_symbol}{avg_cpa:,.2f})."
            ))

        # 4. Low ROAS campaign
        if roas < 1.4 and spend > 1500:
            flags.append(CampaignFlag(
                type="warning",
                label="Low ROAS",
                reason=f"Current ROAS of {roas}x is below the 1.8x sustainability threshold, returning less capital than required to cover marketing and product overhead."
            ))

        # 5. Rising acquisition costs
        if len(group) >= 30:
            sorted_grp = group.sort_values("date")
            half = len(sorted_grp) // 2
            h1 = sorted_grp.iloc[:half]
            h2 = sorted_grp.iloc[half:]
            h1_cpa = h1["spend"].sum() / max(h1["conversions"].sum(), 1)
            h2_cpa = h2["spend"].sum() / max(h2["conversions"].sum(), 1)
            if h2_cpa > h1_cpa * 1.30 and h2["spend"].sum() > 1000:
                pct_rise = round(((h2_cpa - h1_cpa) / h1_cpa) * 100, 1)
                flags.append(CampaignFlag(
                    type="warning",
                    label="Rising CPA Trend",
                    reason=f"CPA accelerated by {pct_rise}% from {currency_symbol}{h1_cpa:,.2f} in H1 to {currency_symbol}{h2_cpa:,.2f} in H2."
                ))

        # 6. High conversion rate but low conversion volume
        if cvr > 4.5 and conversions < 20 and clicks < 200:
            flags.append(CampaignFlag(
                type="success",
                label="High CVR, Scalable Potential",
                reason=f"High conversion rate ({cvr}%), but limited volume ({conversions} conversions). Scalable candidate if audience reach can be expanded."
            ))

        # Performance Status
        if len(group) < 15 or clicks < 50:
            perf_status = "Low Data / Pilot"
        elif contribution_profit < 0 and spend > 3000:
            perf_status = "High Waste"
        elif roas >= 3.5 and contribution_profit > 10000:
            perf_status = "Top Performer"
        elif roas >= 2.0 and contribution_profit > 0:
            perf_status = "Profitable Growth"
        elif roas < 1.5:
            perf_status = "Underperforming"
        else:
            perf_status = "Balanced Performer"

        results.append(CampaignIntelligenceItem(
            campaign_id=c_id,
            campaign_name=c_name,
            channel=channel,
            impressions=impressions,
            clicks=clicks,
            ctr=ctr,
            cpc=cpc,
            spend=round(spend, 2),
            conversions=conversions,
            cvr=cvr,
            cpa=cpa,
            attributed_revenue=round(revenue, 2),
            roas=roas,
            gross_margin_rate=round(gross_margin_rate, 2),
            contribution_profit=round(contribution_profit, 2),
            campaign_roi=campaign_roi,
            performance_status=perf_status,
            flags=flags
        ))

    reverse = sort_desc
    if sort_by == "spend":
        results.sort(key=lambda x: x.spend, reverse=reverse)
    elif sort_by == "revenue":
        results.sort(key=lambda x: x.attributed_revenue, reverse=reverse)
    elif sort_by == "roas":
        results.sort(key=lambda x: x.roas, reverse=reverse)
    elif sort_by == "profit":
        results.sort(key=lambda x: x.contribution_profit, reverse=reverse)
    elif sort_by == "cpa":
        results.sort(key=lambda x: x.cpa, reverse=reverse)

    return results
