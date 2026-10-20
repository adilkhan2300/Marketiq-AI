from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class ChannelBreakdown:
    channel: str
    spend: float
    revenue: float
    profit: float
    roas: float
    conversions: int
    cac: float
    spend_share: float
    revenue_share: float

@dataclass
class MonthlyTrend:
    month: str
    spend: float
    revenue: float
    profit: float
    conversions: int
    roas: float
    cac: float

@dataclass
class KPIOverview:
    total_spend: float
    total_revenue: float
    gross_profit: float
    contribution_profit: float
    marketing_net_profit: float
    roas: float
    cac: float
    acquired_customers: int
    clv: float
    ltv_cac_ratio: float
    marketing_roi: float
    overall_ctr: float
    overall_cpc: float
    overall_cvr: float
    overall_cpa: float
    budget_utilization: float
    target_budget: float
    currency_symbol: str
    channels: List[ChannelBreakdown]
    monthly_trends: List[MonthlyTrend]
    top_campaigns: List[Dict[str, Any]]
    underperforming_campaigns: List[Dict[str, Any]]
    ai_executive_summary: str

@dataclass
class CampaignFlag:
    type: str  # warning, danger, success, info
    label: str
    reason: str

@dataclass
class CampaignIntelligenceItem:
    campaign_id: str
    campaign_name: str
    channel: str
    impressions: int
    clicks: int
    ctr: float
    cpc: float
    spend: float
    conversions: int
    cvr: float
    cpa: float
    attributed_revenue: float
    roas: float
    gross_margin_rate: float
    contribution_profit: float
    campaign_roi: float
    performance_status: str
    flags: List[CampaignFlag] = field(default_factory=list)

@dataclass
class CustomerSegment:
    segment_name: str
    customer_count: int
    percentage: float
    total_revenue: float
    avg_order_value: float
    avg_clv: float
    repeat_rate: float
    avg_churn_risk: float

@dataclass
class CohortData:
    cohort_month: str
    initial_customers: int
    m1_retention: float
    m2_retention: float
    m3_retention: float
    m4_retention: float
    m5_retention: float
    m6_retention: float
    cumulative_revenue: float
    avg_clv: float

@dataclass
class CampaignCustomerQuality:
    campaign_id: str
    campaign_name: str
    channel: str
    customers_acquired: int
    cac: float
    repeat_purchase_rate: float
    avg_order_value: float
    avg_clv: float
    ltv_cac: float

@dataclass
class CustomerProfitabilityOverview:
    total_customers: int
    overall_repeat_rate: float
    overall_aov: float
    overall_clv: float
    overall_cac: float
    ltv_cac_ratio: float
    retention_rate: float
    segments: List[CustomerSegment]
    cohorts: List[CohortData]
    campaign_quality: List[CampaignCustomerQuality]
    data_limitation_note: Optional[str] = None

@dataclass
class ChannelAttribution:
    channel: str
    first_touch_revenue: float
    first_touch_share: float
    last_touch_revenue: float
    last_touch_share: float
    linear_revenue: float
    linear_share: float
    first_touch_acquisitions: int
    last_touch_acquisitions: int
    linear_acquisitions: float
    assisted_conversions: int
    touchpoint_frequency: float

@dataclass
class AttributionOverview:
    channels: List[ChannelAttribution]
    total_observed_revenue: float
    touchpoints_analyzed: int
    insights: List[str]
    overlap_analysis: List[Dict[str, Any]]
    causal_disclaimer: str

@dataclass
class ScenarioAllocation:
    campaign_id: str
    campaign_name: str
    channel: str
    current_spend: float
    proposed_spend: float
    spend_diff: float
    spend_diff_percent: float
    expected_revenue: float
    expected_profit: float
    expected_conversions: int
    expected_roas: float
    expected_cpa: float
    confidence: str
    rationale: str

@dataclass
class OptimizationScenario:
    name: str
    total_budget: float
    expected_revenue: float
    expected_profit: float
    expected_conversions: int
    expected_roas: float
    blended_cpa: float
    expected_roi: float
    allocations: List[ScenarioAllocation]

@dataclass
class OptimizationResponse:
    objective: str
    total_budget: float
    current_scenario: OptimizationScenario
    conservative_scenario: OptimizationScenario
    ai_recommended_scenario: OptimizationScenario
    methodology: str
    assumptions_and_limitations: List[str]
