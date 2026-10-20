import pytest
from core.database import SessionLocal, init_db
from models.db_models import Workspace, CampaignRecord
from analytics.kpi_engine import calculate_kpi_overview
from analytics.campaign_analyzer import analyze_campaigns

@pytest.fixture(scope="module")
def setup_test_db():
    init_db()
    db = SessionLocal()
    # Create test workspace
    test_ws = Workspace(
        id="test-workspace-kpi",
        name="Test Analytics Org",
        currency="USD",
        currency_symbol="$",
        target_budget=10000.0,
        is_demo=False
    )
    db.merge(test_ws)
    db.query(CampaignRecord).filter(CampaignRecord.workspace_id == "test-workspace-kpi").delete()
    
    # Add known test records
    # Campaign A: Spend $1000, Revenue $4000, Margin 60%, Conversions 20, Clicks 200, Impressions 2000
    # Expected: ROAS = 4.0, CAC = 50.0, Gross Profit = 2400, Contribution Profit = 1400, ROI = 40%
    rec_a = CampaignRecord(
        workspace_id="test-workspace-kpi",
        date="2024-05-01",
        campaign_id="TEST-001",
        campaign_name="Test High ROAS",
        channel="Google Ads",
        impressions=2000,
        clicks=200,
        spend=1000.0,
        conversions=20,
        attributed_revenue=4000.0,
        gross_margin_rate=0.60,
        cogs=1600.0,
        contribution_profit=1400.0
    )
    # Campaign B: Spend $2000, Revenue $1000, Margin 40%, Conversions 5, Clicks 100, Impressions 1000
    # Expected: ROAS = 0.5, CAC = 400.0, Gross Profit = 400, Contribution Profit = -1600
    rec_b = CampaignRecord(
        workspace_id="test-workspace-kpi",
        date="2024-05-01",
        campaign_id="TEST-002",
        campaign_name="Test High Waste",
        channel="LinkedIn Ads",
        impressions=1000,
        clicks=100,
        spend=2000.0,
        conversions=5,
        attributed_revenue=1000.0,
        gross_margin_rate=0.40,
        cogs=600.0,
        contribution_profit=-1600.0
    )
    db.add_all([rec_a, rec_b])
    db.commit()
    yield db
    db.close()

def test_kpi_overview_calculations(setup_test_db):
    db = setup_test_db
    kpis = calculate_kpi_overview(db, "test-workspace-kpi")
    
    # Total spend = 1000 + 2000 = 3000
    assert kpis.total_spend == 3000.0
    # Total revenue = 4000 + 1000 = 5000
    assert kpis.total_revenue == 5000.0
    # Blended ROAS = 5000 / 3000 = 1.67
    assert kpis.roas == 1.67
    # Total conversions = 25
    # Blended CAC = 3000 / 25 = 120.0
    assert kpis.cac == 120.0
    # Gross Profit = 2400 + 400 = 2800
    assert kpis.gross_profit == 2800.0
    # Contribution Profit = 2800 - 3000 = -200
    assert kpis.contribution_profit == -200.0
    # Overall CTR = (300 / 3000) * 100 = 10.0%
    assert kpis.overall_ctr == 10.0

def test_campaign_flags_detection(setup_test_db):
    db = setup_test_db
    items = analyze_campaigns(db, "test-workspace-kpi")
    assert len(items) == 2
    
    # Find test high waste campaign
    waste_camp = next(c for c in items if c.campaign_id == "TEST-002")
    assert waste_camp.roas == 0.5
    assert waste_camp.contribution_profit == -1600.0
    # Must flag low ROAS or negative contribution profit
    flag_labels = [f.label for f in waste_camp.flags]
    assert any("Low ROAS" in l or "Negative Contribution" in l for l in flag_labels)
