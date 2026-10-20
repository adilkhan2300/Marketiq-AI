import pytest
from core.database import SessionLocal, init_db
from models.db_models import Workspace, CampaignRecord
from optimization.budget_optimizer import optimize_marketing_budget

@pytest.fixture(scope="module")
def setup_optimizer_db():
    init_db()
    db = SessionLocal()
    test_ws = Workspace(
        id="test-workspace-opt",
        name="Test Optimization Org",
        target_budget=5000.0,
        is_demo=False
    )
    db.merge(test_ws)
    db.query(CampaignRecord).filter(CampaignRecord.workspace_id == "test-workspace-opt").delete()

    # Create 3 distinct campaigns
    c1 = CampaignRecord(
        workspace_id="test-workspace-opt",
        date="2024-05-01",
        campaign_id="OPT-001",
        campaign_name="Super ROAS Campaign",
        channel="Google Ads",
        spend=1000.0,
        conversions=50,
        attributed_revenue=5000.0,
        gross_margin_rate=0.70,
        cogs=1500.0,
        contribution_profit=2500.0
    )
    c2 = CampaignRecord(
        workspace_id="test-workspace-opt",
        date="2024-05-01",
        campaign_id="OPT-002",
        campaign_name="Average Campaign",
        channel="Meta Ads",
        spend=2000.0,
        conversions=40,
        attributed_revenue=4000.0,
        gross_margin_rate=0.60,
        cogs=1600.0,
        contribution_profit=400.0
    )
    c3 = CampaignRecord(
        workspace_id="test-workspace-opt",
        date="2024-05-01",
        campaign_id="OPT-003",
        campaign_name="Poor Campaign",
        channel="LinkedIn Ads",
        spend=2000.0,
        conversions=8,
        attributed_revenue=1200.0,
        gross_margin_rate=0.40,
        cogs=720.0,
        contribution_profit=-1520.0
    )
    db.add_all([c1, c2, c3])
    db.commit()
    yield db
    db.close()

def test_budget_optimizer_respects_constraints(setup_optimizer_db):
    db = setup_optimizer_db
    target_budget = 6000.0

    res = optimize_marketing_budget(
        db,
        "test-workspace-opt",
        target_budget=target_budget,
        objective="maximize_profit",
        protected_campaigns=["OPT-001"]
    )

    assert res is not None
    # 1. Total recommended budget must not exceed target budget (allowing 0.5 floating point tolerance)
    total_ai_spend = sum(a.proposed_spend for a in res.ai_recommended_scenario.allocations)
    assert total_ai_spend <= target_budget + 1.0
    assert abs(total_ai_spend - target_budget) < 2.0

    # 2. Protected campaign OPT-001 should not be cut below current baseline
    opt1_alloc = next(a for a in res.ai_recommended_scenario.allocations if a.campaign_id == "OPT-001")
    assert opt1_alloc.proposed_spend >= opt1_alloc.current_spend * 0.99

    # 3. Super ROAS Campaign should receive a proposed increase or stable budget
    assert opt1_alloc.proposed_spend > 1000.0

    # 4. Poor campaign should receive reduced or controlled allocation
    opt3_alloc = next(a for a in res.ai_recommended_scenario.allocations if a.campaign_id == "OPT-003")
    assert opt3_alloc.proposed_spend < 2400.0
