import pandas as pd
import numpy as np
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models.db_models import CustomerRecord, CampaignRecord
from models.schemas import AttributionOverview, ChannelAttribution

def calculate_attribution_models(
    db: Session,
    workspace_id: str
) -> AttributionOverview:
    cust_records = db.query(CustomerRecord).filter(CustomerRecord.workspace_id == workspace_id).all()
    cmp_records = db.query(CampaignRecord).filter(CampaignRecord.workspace_id == workspace_id).all()

    disclaimer = (
        "Methodological Note on Causal Impact: Attribution models observe touchpoints along historical conversion paths "
        "and algorithmically partition credited revenue (First-Touch, Last-Touch, Linear). They do NOT establish true counterfactual "
        "causality (incremental lift). High attribution share does not prove that revenue would disappear if the campaign were eliminated."
    )

    if not cust_records:
        if not cmp_records:
            return AttributionOverview(
                channels=[],
                total_observed_revenue=0.0,
                touchpoints_analyzed=0,
                insights=["No customer touchpoint or campaign data available."],
                overlap_analysis=[],
                causal_disclaimer=disclaimer
            )
        
        # Aggregate fallback when touchpoints are missing
        df_cmp = pd.DataFrame([{
            "channel": c.channel,
            "revenue": c.attributed_revenue,
            "conversions": c.conversions
        } for c in cmp_records])
        tot_rev = df_cmp["revenue"].sum()
        ch_grp = df_cmp.groupby("channel").sum().reset_index()
        channels = []
        for _, row in ch_grp.iterrows():
            rev = float(row["revenue"])
            share = round((rev / tot_rev) * 100, 1) if tot_rev > 0 else 0.0
            conv = int(row["conversions"])
            channels.append(ChannelAttribution(
                channel=str(row["channel"]),
                first_touch_revenue=round(rev, 2),
                first_touch_share=share,
                last_touch_revenue=round(rev, 2),
                last_touch_share=share,
                linear_revenue=round(rev, 2),
                linear_share=share,
                first_touch_acquisitions=conv,
                last_touch_acquisitions=conv,
                linear_acquisitions=float(conv),
                assisted_conversions=0,
                touchpoint_frequency=1.0
            ))
        return AttributionOverview(
            channels=channels,
            total_observed_revenue=round(float(tot_rev), 2),
            touchpoints_analyzed=int(df_cmp["conversions"].sum()),
            insights=["Showing single-touch campaign records. Upload multi-touch customer journey logs for full path comparison."],
            overlap_analysis=[],
            causal_disclaimer=disclaimer
        )

    # Full multi-touch journey attribution
    df_cust = pd.DataFrame([{
        "customer_id": c.customer_id,
        "first_touch": c.first_touch_channel or c.acquisition_channel,
        "last_touch": c.last_touch_channel or c.acquisition_channel,
        "journey": c.journey_touchpoints or c.acquisition_channel,
        "revenue": c.total_revenue
    } for c in cust_records])

    total_rev = float(df_cust["revenue"].sum())
    all_channels = sorted(list(set(df_cust["first_touch"].unique().tolist() + df_cust["last_touch"].unique().tolist())))

    # 1. First Touch
    ft_rev = df_cust.groupby("first_touch")["revenue"].sum().to_dict()
    ft_cnt = df_cust.groupby("first_touch")["customer_id"].count().to_dict()

    # 2. Last Touch
    lt_rev = df_cust.groupby("last_touch")["revenue"].sum().to_dict()
    lt_cnt = df_cust.groupby("last_touch")["customer_id"].count().to_dict()

    # 3. Linear Attribution & Assisted Conversions
    linear_rev = {ch: 0.0 for ch in all_channels}
    linear_cnt = {ch: 0.0 for ch in all_channels}
    assisted_conv = {ch: 0 for ch in all_channels}
    touch_freq = {ch: 0 for ch in all_channels}
    total_touchpoints = 0

    for _, row in df_cust.iterrows():
        path = [p.strip() for p in str(row["journey"]).split(">") if p.strip()]
        if not path:
            path = [row["last_touch"]]
        n_touch = len(path)
        total_touchpoints += n_touch
        cust_rev = float(row["revenue"])

        # Assisted conversions: touchpoint is in path but not the last touch
        for idx, touch in enumerate(path):
            if touch in touch_freq:
                touch_freq[touch] += 1
            if touch in linear_rev:
                linear_rev[touch] += cust_rev / n_touch
                linear_cnt[touch] += 1.0 / n_touch
            if idx < n_touch - 1 and touch in assisted_conv:
                assisted_conv[touch] += 1

    channels_list: List[ChannelAttribution] = []
    for ch in all_channels:
        f_rev = float(ft_rev.get(ch, 0.0))
        l_rev = float(lt_rev.get(ch, 0.0))
        lin_rev = float(linear_rev.get(ch, 0.0))

        f_share = round((f_rev / total_rev) * 100, 1) if total_rev > 0 else 0.0
        l_share = round((l_rev / total_rev) * 100, 1) if total_rev > 0 else 0.0
        lin_share = round((lin_rev / total_rev) * 100, 1) if total_rev > 0 else 0.0

        channels_list.append(ChannelAttribution(
            channel=ch,
            first_touch_revenue=round(f_rev, 2),
            first_touch_share=f_share,
            last_touch_revenue=round(l_rev, 2),
            last_touch_share=l_share,
            linear_revenue=round(lin_rev, 2),
            linear_share=lin_share,
            first_touch_acquisitions=int(ft_cnt.get(ch, 0)),
            last_touch_acquisitions=int(lt_cnt.get(ch, 0)),
            linear_acquisitions=round(float(linear_cnt.get(ch, 0.0)), 1),
            assisted_conversions=int(assisted_conv.get(ch, 0)),
            touchpoint_frequency=round(touch_freq.get(ch, 0) / max(len(df_cust), 1), 2)
        ))

    channels_list.sort(key=lambda x: x.linear_revenue, reverse=True)

    # Channel overlap analysis (e.g. Meta -> Google, Google -> Email)
    overlap = []
    for _, row in df_cust.iterrows():
        path = [p.strip() for p in str(row["journey"]).split(">") if p.strip()]
        if len(path) > 1:
            overlap.append(f"{path[0]} → {path[-1]}")
    
    top_paths = pd.Series(overlap).value_counts().head(5).to_dict()
    overlap_analysis = [{"path": k, "conversions": int(v)} for k, v in top_paths.items()]

    # Generated attribution insights
    insights = []
    # Find channel with biggest delta between First and Last touch
    deltas = [(ch.channel, ch.first_touch_revenue - ch.last_touch_revenue) for ch in channels_list]
    deltas.sort(key=lambda x: abs(x[1]), reverse=True)
    if deltas:
        top_d_channel, top_d_val = deltas[0]
        if top_d_val > 0:
            insights.append(
                f"{top_d_channel} acts predominantly as an upper-funnel discovery driver: "
                f"it claims {abs(top_d_val):,.0f} more revenue under First-Touch than Last-Touch."
            )
        else:
            insights.append(
                f"{top_d_channel} functions as a closing channel: "
                f"it captures {abs(top_d_val):,.0f} more credit under Last-Touch than First-Touch."
            )

    insights.append(
        f"Linear attribution distributes credit equally across {total_touchpoints:,} recorded customer touchpoints, "
        f"reducing bias against mid-funnel nurturing channels."
    )

    return AttributionOverview(
        channels=channels_list,
        total_observed_revenue=round(total_rev, 2),
        touchpoints_analyzed=total_touchpoints,
        insights=insights,
        overlap_analysis=overlap_analysis,
        causal_disclaimer=disclaimer
    )
