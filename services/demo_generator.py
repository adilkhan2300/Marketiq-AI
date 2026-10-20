import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from models.db_models import Workspace, CampaignRecord, CustomerRecord

DEMO_CAMPAIGNS_DEF = [
    {
        "campaign_id": "CMP-GGL-001",
        "campaign_name": "Google Search - Brand Intent",
        "channel": "Google Ads",
        "base_daily_spend": 110.0,
        "base_ctr": 0.082,
        "base_cvr": 0.065,
        "avg_order_val": 160.0,
        "gross_margin": 0.72,
        "efficiency_tier": "super_efficient",
        "notes": "Core branded search terms with exceptionally high intent and ROAS."
    },
    {
        "campaign_id": "CMP-GGL-002",
        "campaign_name": "Google Search - Non-Brand High Intent",
        "channel": "Google Ads",
        "base_daily_spend": 260.0,
        "base_ctr": 0.038,
        "base_cvr": 0.034,
        "avg_order_val": 145.0,
        "gross_margin": 0.65,
        "efficiency_tier": "strong_performer",
        "notes": "Targeted generic keywords driving solid mid-funnel customer acquisition."
    },
    {
        "campaign_id": "CMP-GGL-003",
        "campaign_name": "Google Performance Max - Dynamic",
        "channel": "Google Ads",
        "base_daily_spend": 210.0,
        "base_ctr": 0.021,
        "base_cvr": 0.025,
        "avg_order_val": 125.0,
        "gross_margin": 0.60,
        "efficiency_tier": "moderate",
        "notes": "Automated cross-network Google inventory driving balanced volume."
    },
    {
        "campaign_id": "CMP-META-001",
        "campaign_name": "Meta Retargeting - Cart Abandoners",
        "channel": "Meta Ads",
        "base_daily_spend": 140.0,
        "base_ctr": 0.045,
        "base_cvr": 0.052,
        "avg_order_val": 150.0,
        "gross_margin": 0.68,
        "efficiency_tier": "super_efficient",
        "notes": "Dynamic catalog retargeting for users with abandoned checkouts."
    },
    {
        "campaign_id": "CMP-META-002",
        "campaign_name": "Meta Top-of-Funnel - Video Promo",
        "channel": "Meta Ads",
        "base_daily_spend": 380.0,
        "base_ctr": 0.015,
        "base_cvr": 0.012,
        "avg_order_val": 95.0,
        "gross_margin": 0.28, # Intentionally low margin (deep discounts)
        "efficiency_tier": "high_waste_low_margin",
        "notes": "Generates apparent revenue via heavy discounting but negative contribution profit."
    },
    {
        "campaign_id": "CMP-META-003",
        "campaign_name": "Meta Lookalike 2% - Growth Expansion",
        "channel": "Meta Ads",
        "base_daily_spend": 220.0,
        "base_ctr": 0.024,
        "base_cvr": 0.022,
        "avg_order_val": 130.0,
        "gross_margin": 0.62,
        "efficiency_tier": "moderate",
        "notes": "Lookalike audience based on past high-LTV purchasers."
    },
    {
        "campaign_id": "CMP-LNK-001",
        "campaign_name": "LinkedIn Sponsored Content - B2B Execs",
        "channel": "LinkedIn Ads",
        "base_daily_spend": 310.0,
        "base_ctr": 0.009,
        "base_cvr": 0.008,
        "avg_order_val": 220.0,
        "gross_margin": 0.65,
        "efficiency_tier": "money_waster",
        "notes": "Very high CPC ($8.50+) with weak conversion rate leading to low ROAS."
    },
    {
        "campaign_id": "CMP-LNK-002",
        "campaign_name": "LinkedIn InMail & Lead Gen Forms",
        "channel": "LinkedIn Ads",
        "base_daily_spend": 180.0,
        "base_ctr": 0.018,
        "base_cvr": 0.026,
        "avg_order_val": 250.0,
        "gross_margin": 0.70,
        "efficiency_tier": "strong_b2b",
        "notes": "Targeted direct outreach to marketing directors with solid deal size."
    },
    {
        "campaign_id": "CMP-EML-001",
        "campaign_name": "Email Lifecycle & Automated Nurture",
        "channel": "Email Marketing",
        "base_daily_spend": 35.0,
        "base_ctr": 0.075,
        "base_cvr": 0.070,
        "avg_order_val": 140.0,
        "gross_margin": 0.75,
        "efficiency_tier": "super_efficient",
        "notes": "Extremely low acquisition cost with stellar repeat engagement."
    },
    {
        "campaign_id": "CMP-EML-002",
        "campaign_name": "Email VIP Winback & Re-engagement",
        "channel": "Email Marketing",
        "base_daily_spend": 25.0,
        "base_ctr": 0.062,
        "base_cvr": 0.058,
        "avg_order_val": 175.0,
        "gross_margin": 0.74,
        "efficiency_tier": "super_efficient",
        "notes": "Targeting dormant high-value customers with tailored offers."
    },
    {
        "campaign_id": "CMP-AFF-001",
        "campaign_name": "Affiliate - Curated Review Portals",
        "channel": "Affiliate Marketing",
        "base_daily_spend": 150.0,
        "base_ctr": 0.032,
        "base_cvr": 0.038,
        "avg_order_val": 155.0,
        "gross_margin": 0.58,
        "efficiency_tier": "strong_performer",
        "notes": "Performance-based payout structure aligning incentives with conversion volume."
    },
    {
        "campaign_id": "CMP-AFF-002",
        "campaign_name": "Influencer Tech Partner Pilot",
        "channel": "Affiliate Marketing",
        "base_daily_spend": 40.0,
        "base_ctr": 0.019,
        "base_cvr": 0.020,
        "avg_order_val": 130.0,
        "gross_margin": 0.60,
        "efficiency_tier": "insufficient_data",
        "notes": "Recently launched exploratory test with 3 micro-influencers; low sample size."
    }
]

def generate_demo_dataset(db: Session, workspace_id: str = "demo-workspace"):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        workspace = Workspace(
            id=workspace_id,
            name="Apex Retail & Tech Direct",
            industry="E-commerce & SaaS",
            currency="USD",
            currency_symbol="$",
            target_budget=160000.0,
            reporting_period="Last 180 Days (H1 Performance)",
            is_demo=True
        )
        db.add(workspace)
        db.commit()
    else:
        db.query(CampaignRecord).filter(CampaignRecord.workspace_id == workspace_id).delete()
        db.query(CustomerRecord).filter(CustomerRecord.workspace_id == workspace_id).delete()
        db.commit()

    end_date = datetime(2024, 6, 30)
    start_date = end_date - timedelta(days=179)

    random.seed(42)
    np.random.seed(42)

    campaign_records = []
    customer_records = []
    customer_counter = 1000

    touchpoint_pool = [
        "Google Ads", "Meta Ads", "LinkedIn Ads", "Email Marketing", "Affiliate Marketing"
    ]

    for day_idx in range(180):
        current_date = start_date + timedelta(days=day_idx)
        date_str = current_date.strftime("%Y-%m-%d")
        day_of_week = current_date.weekday()
        weekend_mult = 0.85 if day_of_week in [5, 6] else 1.05

        for c_def in DEMO_CAMPAIGNS_DEF:
            if c_def["efficiency_tier"] == "insufficient_data" and day_idx < 166:
                continue

            spend_noise = random.uniform(0.88, 1.14)
            daily_spend = round(c_def["base_daily_spend"] * weekend_mult * spend_noise, 2)

            cpc = random.uniform(1.2, 4.5)
            if "LinkedIn" in c_def["channel"]:
                cpc = random.uniform(6.5, 9.8)
            elif "Email" in c_def["channel"]:
                cpc = random.uniform(0.3, 0.7)
            elif "Meta" in c_def["channel"]:
                cpc = random.uniform(1.1, 2.8)

            clicks = max(1, int(daily_spend / cpc))
            ctr = c_def["base_ctr"] * random.uniform(0.85, 1.15)
            impressions = max(clicks + 10, int(clicks / ctr))

            cvr = c_def["base_cvr"] * random.uniform(0.82, 1.18)
            conversions = int(clicks * cvr)
            if conversions == 0 and random.random() < 0.25:
                conversions = 1

            aov = c_def["avg_order_val"] * random.uniform(0.9, 1.12)
            revenue = round(conversions * aov, 2)

            margin_rate = c_def["gross_margin"]
            cogs = round(revenue * (1.0 - margin_rate), 2)
            contribution_profit = round((revenue - cogs) - daily_spend, 2)

            campaign_records.append(CampaignRecord(
                workspace_id=workspace_id,
                date=date_str,
                campaign_id=c_def["campaign_id"],
                campaign_name=c_def["campaign_name"],
                channel=c_def["channel"],
                impressions=impressions,
                clicks=clicks,
                spend=daily_spend,
                conversions=conversions,
                attributed_revenue=revenue,
                gross_margin_rate=margin_rate,
                cogs=cogs,
                contribution_profit=contribution_profit
            ))

            if conversions > 0 and (day_idx % 3 == 0 or c_def["efficiency_tier"] == "super_efficient"):
                cust_to_add = min(conversions, random.randint(1, 3))
                for _ in range(cust_to_add):
                    customer_counter += 1
                    cust_id = f"CUST-{customer_counter}"

                    first_channel = c_def["channel"]
                    if random.random() < 0.4:
                        first_channel = random.choice(touchpoint_pool)

                    last_channel = c_def["channel"]
                    journey = f"{first_channel} > {last_channel}" if first_channel != last_channel else first_channel
                    if random.random() < 0.3:
                        mid = random.choice(touchpoint_pool)
                        journey = f"{first_channel} > {mid} > {last_channel}"

                    repeat_prob = 0.25
                    if "Email" in c_def["channel"]:
                        repeat_prob = 0.65
                    elif "Brand Intent" in c_def["campaign_name"]:
                        repeat_prob = 0.50
                    elif "high_waste" in c_def["efficiency_tier"]:
                        repeat_prob = 0.08

                    is_repeat = random.random() < repeat_prob
                    total_orders = random.randint(2, 6) if is_repeat else 1
                    total_cust_rev = round(aov * total_orders * random.uniform(0.95, 1.2), 2)
                    total_cust_profit = round(total_cust_rev * margin_rate - (daily_spend / max(conversions, 1)), 2)
                    acq_cost = round(daily_spend / max(conversions, 1), 2)

                    if total_cust_rev > 650 or total_orders >= 4:
                        seg = "High-Value"
                        churn_risk = random.uniform(0.08, 0.25)
                    elif total_orders > 1:
                        seg = "Repeat"
                        churn_risk = random.uniform(0.18, 0.45)
                    elif (end_date - current_date).days < 45:
                        seg = "New"
                        churn_risk = random.uniform(0.20, 0.50)
                    elif (end_date - current_date).days > 110:
                        seg = "At-Risk"
                        churn_risk = random.uniform(0.65, 0.92)
                    else:
                        seg = "Low-Engagement"
                        churn_risk = random.uniform(0.48, 0.75)

                    customer_records.append(CustomerRecord(
                        workspace_id=workspace_id,
                        customer_id=cust_id,
                        acquisition_date=date_str,
                        acquisition_campaign_id=c_def["campaign_id"],
                        acquisition_channel=c_def["channel"],
                        first_touch_channel=first_channel,
                        last_touch_channel=last_channel,
                        journey_touchpoints=journey,
                        total_orders=total_orders,
                        total_revenue=total_cust_rev,
                        total_profit=total_cust_profit,
                        acquisition_cost=acq_cost,
                        segment=seg,
                        churn_risk=round(churn_risk, 3),
                        is_churned=churn_risk > 0.70
                    ))

    db.bulk_save_objects(campaign_records)
    db.bulk_save_objects(customer_records)
    db.commit()

    return {
        "status": "success",
        "workspace_id": workspace_id,
        "campaign_records_count": len(campaign_records),
        "customer_records_count": len(customer_records)
    }
