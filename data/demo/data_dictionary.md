# MARKETIQ AI — Analytical Data Dictionary

This document specifies the supported schema and analytical definitions for importing marketing performance data into MARKETIQ AI.

| Field Name | Type | Description | Mandatory? | Example |
| :--- | :--- | :--- | :--- | :--- |
| `date` | String / Date | The date of advertising activity (YYYY-MM-DD) | Optional | `2024-05-15` |
| `campaign_id` | String | Unique system identifier for the campaign | Optional | `CMP-GGL-001` |
| `campaign_name` | String | Human-readable name of the marketing initiative | **Recommended** | `Google Search - Brand Intent` |
| `channel` | String | Marketing network/channel | **Recommended** | `Google Ads`, `Meta Ads`, `Email` |
| `impressions` | Integer | Total ad exposures served | Optional | `5200` |
| `clicks` | Integer | Total ad clicks or visits received | Optional | `198` |
| `spend` | Numeric | Total advertising expenditure in local currency | **Mandatory** | `110.00` |
| `conversions` | Integer | Successful actions (orders, signups, leads) | **Mandatory** | `14` |
| `attributed_revenue` | Numeric | Gross sales or revenue credited to the campaign | **Mandatory** | `2240.00` |
| `gross_margin_rate` | Numeric | Gross product margin decimal (e.g. 0.65 for 65%) | Optional (Default 0.60) | `0.72` |

---

### Core Formula Definitions

1. **ROAS (Return on Ad Spend)**:
   $$\text{ROAS} = \frac{\text{Attributed Revenue}}{\text{Advertising Spend}}$$

2. **CAC (Customer Acquisition Cost)**:
   $$\text{CAC} = \frac{\text{Spend}}{\text{Conversions}}$$

3. **Contribution Profit**:
   $$\text{Contribution Profit} = (\text{Attributed Revenue} \times \text{Gross Margin}) - \text{Spend}$$

4. **Marketing ROI**:
   $$\text{Marketing ROI} = \frac{\text{Contribution Profit} - \text{Spend}}{\text{Spend}} \times 100$$
