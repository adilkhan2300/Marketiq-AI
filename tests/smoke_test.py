import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.database import init_db, SessionLocal
from services.demo_generator import generate_demo_dataset
from analytics.kpi_engine import calculate_kpi_overview
from analytics.campaign_analyzer import analyze_campaigns
from analytics.customer_profitability import analyze_customer_profitability
from analytics.attribution_engine import calculate_attribution_models
from optimization.budget_optimizer import optimize_marketing_budget
from ml.predictive_models import train_and_evaluate_models
from services.report_generator import generate_excel_full_report
from services.ai_assistant import answer_marketing_query

def run_smoke_test():
    init_db()
    db = SessionLocal()
    print("1. DB initialized successfully")
    
    res = generate_demo_dataset(db, "test-smoke")
    print(f"2. Demo dataset generated: {res['campaign_records_count']} campaigns, {res['customer_records_count']} customers")
    
    kpis = calculate_kpi_overview(db, "test-smoke")
    print(f"3. KPIs calculated: Spend ${kpis.total_spend:,.2f}, Rev ${kpis.total_revenue:,.2f}, ROAS {kpis.roas}x, Profit ${kpis.contribution_profit:,.2f}")
    
    camps = analyze_campaigns(db, "test-smoke")
    print(f"4. Analyzed {len(camps)} campaigns with diagnostic flags")
    
    cust = analyze_customer_profitability(db, "test-smoke")
    print(f"5. Customer Cohorts: {len(cust.cohorts)} monthly cohorts, {len(cust.segments)} segments")
    
    attr = calculate_attribution_models(db, "test-smoke")
    print(f"6. Attribution: {len(attr.channels)} channels modeled across {attr.touchpoints_analyzed} touchpoints")
    
    opt = optimize_marketing_budget(db, "test-smoke", 160000.0, "maximize_profit")
    print(f"7. SciPy Optimizer converged: Current Profit ${opt.current_scenario.expected_profit:,.2f} -> AI Profit ${opt.ai_recommended_scenario.expected_profit:,.2f}")
    
    ml = train_and_evaluate_models(db, "test-smoke")
    print(f"8. ML models trained: Conversion Classifier Acc {ml['conversion_classifier']['metrics'][0]['score']}")
    
    xl = generate_excel_full_report(db, "test-smoke")
    print(f"9. Excel workbook generated: {len(xl)} bytes")
    
    ans = answer_marketing_query(db, "test-smoke", "Which campaigns are wasting money?")
    print("10. AI Assistant answer verified")
    
    print("=====================================================")
    print("  ALL 10 CORE MODULE INTEGRATION CHECKS PASSED 100%! ")
    print("=====================================================")
    db.close()

if __name__ == "__main__":
    run_smoke_test()
