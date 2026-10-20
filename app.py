import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

from core.database import init_db, SessionLocal
from core.config import PROJECT_NAME, TAGLINE, VERSION
from models.db_models import Workspace, CampaignRecord, CustomerRecord
from services.demo_generator import generate_demo_dataset
from services.data_importer import validate_and_parse_dataset, import_mapped_dataset
from services.ai_assistant import answer_marketing_query
from services.report_generator import (
    generate_csv_campaign_report,
    generate_excel_full_report,
    generate_executive_text_brief
)
from analytics.kpi_engine import calculate_kpi_overview
from analytics.campaign_analyzer import analyze_campaigns
from analytics.customer_profitability import analyze_customer_profitability
from analytics.attribution_engine import calculate_attribution_models
from optimization.budget_optimizer import optimize_marketing_budget
from ml.predictive_models import train_and_evaluate_models

# ---------------------------------------------------------
# Page Configuration & SaaS Enterprise Theme Injection
# ---------------------------------------------------------
st.set_page_config(
    page_title="MARKETIQ AI — Marketing ROI & Budget Optimization",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database Schema
init_db()

# Custom Executive CSS
st.markdown("""
<style>
    /* Global Styling */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0B1329 !important;
        color: #E2E8F0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #94A3B8;
    }
    [data-testid="stSidebar"] hr {
        border-color: #1E293B;
    }
    
    /* Header Brand Card */
    .brand-container {
        padding: 12px 0px 20px 0px;
        border-bottom: 1px solid #1E293B;
        margin-bottom: 20px;
    }
    .brand-title {
        font-size: 22px;
        font-weight: 800;
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .brand-tagline {
        font-size: 11px;
        color: #94A3B8;
        font-weight: 500;
        margin-top: 4px;
        letter-spacing: 0.2px;
    }
    
    /* KPI Metric Cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    .kpi-label {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #64748B;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }
    .kpi-formula {
        font-size: 11px;
        color: #94A3B8;
        font-style: italic;
    }
    .kpi-badge-positive {
        display: inline-block;
        background-color: #DCFCE7;
        color: #15803D;
        font-size: 11px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 9999px;
        margin-top: 4px;
    }
    .kpi-badge-warning {
        display: inline-block;
        background-color: #FEF3C7;
        color: #B45309;
        font-size: 11px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 9999px;
        margin-top: 4px;
    }
    .kpi-badge-danger {
        display: inline-block;
        background-color: #FEE2E2;
        color: #B91C1C;
        font-size: 11px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 9999px;
        margin-top: 4px;
    }

    /* AI Executive Banner */
    .ai-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%);
        border: 1px solid #312E81;
        border-radius: 12px;
        padding: 20px 24px;
        color: #F8FAFC;
        margin-bottom: 24px;
    }
    .ai-banner-title {
        font-size: 14px;
        font-weight: 700;
        color: #38BDF8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
    }
    .ai-banner-text {
        font-size: 14px;
        line-height: 1.6;
        color: #CBD5E1;
        margin: 0;
    }

    /* Flag Badges */
    .flag-tag-danger {
        background-color: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FCA5A5;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 4px;
        display: block;
    }
    .flag-tag-warning {
        background-color: #FFFBEB;
        color: #92400E;
        border: 1px solid #FCD34D;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 4px;
        display: block;
    }
    .flag-tag-info {
        background-color: #EFF6FF;
        color: #1E40AF;
        border: 1px solid #93C5FD;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 4px;
        display: block;
    }
    .flag-tag-success {
        background-color: #F0FDF4;
        color: #166534;
        border: 1px solid #86EFAC;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 4px;
        display: block;
    }

    /* Modern Table headers */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State Management & Data Isolation
# ---------------------------------------------------------
db = SessionLocal()

if "workspace_id" not in st.session_state:
    st.session_state.workspace_id = "default-org"

# Check if active workspace exists in DB
active_ws = db.query(Workspace).filter(Workspace.id == st.session_state.workspace_id).first()
if not active_ws:
    # Fresh empty workspace by default
    active_ws = Workspace(
        id=st.session_state.workspace_id,
        name="Enterprise Growth Lab",
        industry="E-commerce & SaaS",
        currency="USD",
        currency_symbol="$",
        target_budget=160000.0,
        reporting_period="Last 180 Days (H1)",
        is_demo=False
    )
    db.add(active_ws)
    db.commit()

# ---------------------------------------------------------
# Sidebar: Brand, Navigation, Workspace Controls & Filters
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
    <div class="brand-container">
        <h1 class="brand-title">📈 {PROJECT_NAME}</h1>
        <div class="brand-tagline">{TAGLINE}</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation menu
    nav_selection = st.radio(
        "Navigation Modules",
        [
            "1. Executive Overview",
            "2. Campaign Intelligence",
            "3. Customer Profitability",
            "4. Attribution Analytics",
            "5. AI Budget Optimizer",
            "6. Predictive Insights",
            "7. AI Marketing Assistant",
            "8. Reports & Exports",
            "9. 📤 Upload Data & Settings"
        ],
        index=0,
        label_visibility="collapsed"
    )

    # Compute records count early for dynamic expanders & badges
    records_count = db.query(CampaignRecord).filter(CampaignRecord.workspace_id == st.session_state.workspace_id).count()

    st.markdown("---")
    st.markdown("### 📤 Upload Data File")
    with st.expander("Upload CSV / Excel File", expanded=(records_count == 0)):
        sidebar_file = st.file_uploader("Drop your dataset here", type=["csv", "xlsx", "xls"], key="sidebar_quick_uploader")
        if sidebar_file:
            sb_bytes = sidebar_file.read()
            sb_val = validate_and_parse_dataset(sb_bytes, sidebar_file.name)
            if sb_val["success"]:
                st.caption(f"✅ **{sb_val['total_rows']:,} rows** detected (Quality: {sb_val['quality_score']}%)")
                if st.button("🚀 Import Into Workspace", key="sidebar_ingest_btn", type="primary", use_container_width=True):
                    with st.spinner("Ingesting file..."):
                        import_mapped_dataset(db, st.session_state.workspace_id, sb_bytes, sidebar_file.name, sb_val["mapped_columns"])
                        st.success("Dataset successfully imported!")
                        st.rerun()
            else:
                st.error(sb_val["error"])
        
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
        with open("data/demo/sample_campaigns.csv", "r", encoding="utf-8") as f_samp:
            samp_csv_content = f_samp.read()
        st.download_button(
            "📥 Get Template CSV",
            data=samp_csv_content,
            file_name="sample_campaigns.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("---")
    st.markdown("### 🎛️ Workspace & Demo Controls")

    # Workspace status badge
    if records_count == 0:
        st.info("🌱 **Fresh Workspace**: No records loaded. Explore Demo Mode or upload CSV.")
        if st.button("🚀 Load Realistic Demo Data", use_container_width=True, type="primary"):
            with st.spinner("Generating 180-day multi-channel demo dataset..."):
                generate_demo_dataset(db, st.session_state.workspace_id)
                active_ws.is_demo = True
                db.commit()
                st.success("Demo dataset loaded!")
                st.rerun()
    else:
        status_label = "Demo Dataset Active (12 Campaigns)" if active_ws.is_demo else f"{records_count:,} Custom Records"
        st.success(f"📊 **Data Source**: {status_label}")
        
        col_demo_1, col_demo_2 = st.columns(2)
        with col_demo_1:
            if st.button("🔄 Reset Demo", use_container_width=True):
                with st.spinner("Rebuilding demo data..."):
                    generate_demo_dataset(db, st.session_state.workspace_id)
                    st.rerun()
        with col_demo_2:
            if st.button("🗑️ Clear Data", use_container_width=True):
                db.query(CampaignRecord).filter(CampaignRecord.workspace_id == st.session_state.workspace_id).delete()
                db.query(CustomerRecord).filter(CustomerRecord.workspace_id == st.session_state.workspace_id).delete()
                active_ws.is_demo = False
                db.commit()
                st.warning("Workspace data wiped.")
                st.rerun()

    st.markdown("---")
    st.markdown("### 🔍 Global Filters")

    # Channels filter
    distinct_channels = ["All Channels"]
    if records_count > 0:
        db_channels = [r[0] for r in db.query(CampaignRecord.channel).filter(CampaignRecord.workspace_id == st.session_state.workspace_id).distinct().all()]
        distinct_channels.extend(sorted(db_channels))
    
    selected_channel = st.selectbox("Marketing Channel", distinct_channels, index=0)

    # Date range filters if data exists
    start_filter_date = None
    end_filter_date = None
    if records_count > 0:
        min_date_str = db.query(CampaignRecord.date).filter(CampaignRecord.workspace_id == st.session_state.workspace_id).order_by(CampaignRecord.date.asc()).first()[0]
        max_date_str = db.query(CampaignRecord.date).filter(CampaignRecord.workspace_id == st.session_state.workspace_id).order_by(CampaignRecord.date.desc()).first()[0]
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_filter_date = st.text_input("From Date", value=min_date_str)
        with col_d2:
            end_filter_date = st.text_input("To Date", value=max_date_str)

    st.markdown("---")
    st.caption(f"{PROJECT_NAME} Enterprise v{VERSION} | Local SQLite Isolated")

# Currency Symbol & Target Budget shortcut
sym = active_ws.currency_symbol or "$"
target_budget = active_ws.target_budget or 160000.0

# -----------------------------------------------------------------------------
# MODULE 1: EXECUTIVE OVERVIEW
# -----------------------------------------------------------------------------
if nav_selection == "1. Executive Overview":
    st.title("Executive Overview")
    st.markdown(f"**Target Period:** {active_ws.reporting_period} | **Currency:** {active_ws.currency} ({sym})")

    # Quick Upload Option on Dashboard
    with st.expander("📤 Upload Custom Marketing Data File (CSV / Excel)", expanded=(records_count == 0)):
        col_up1, col_up2 = st.columns([7, 3])
        with col_up1:
            exec_file = st.file_uploader("Upload your campaign performance or transaction file", type=["csv", "xlsx", "xls"], key="exec_main_uploader")
            if exec_file:
                e_bytes = exec_file.read()
                e_val = validate_and_parse_dataset(e_bytes, exec_file.name)
                if e_val["success"]:
                    st.success(f"File **{exec_file.name}** verified: {e_val['total_rows']:,} rows detected with Data Quality Score of **{e_val['quality_score']}%**.")
                    if st.button("🚀 Ingest & Refresh Dashboard", key="exec_ingest_btn", type="primary"):
                        with st.spinner("Ingesting dataset..."):
                            import_mapped_dataset(db, st.session_state.workspace_id, e_bytes, exec_file.name, e_val["mapped_columns"])
                            st.success("Dataset successfully imported!")
                            st.rerun()
                else:
                    st.error(e_val["error"])
        with col_up2:
            st.markdown("**Need a Template?**")
            st.caption("Download our sample dataset formatted with standard marketing columns:")
            with open("data/demo/sample_campaigns.csv", "r", encoding="utf-8") as f_samp2:
                sc_txt = f_samp2.read()
            st.download_button("📥 Download Sample CSV", data=sc_txt, file_name="sample_campaigns.csv", mime="text/csv", use_container_width=True, key="exec_dl_samp")

    kpi = calculate_kpi_overview(
        db,
        st.session_state.workspace_id,
        channel_filter=selected_channel if selected_channel != "All Channels" else None,
        start_date=start_filter_date,
        end_date=end_filter_date
    )

    # AI Executive Summary Banner
    st.markdown(f"""
    <div class="ai-banner">
        <div class="ai-banner-title">🤖 AI-Generated Executive Summary & Attribution Analysis</div>
        <div class="ai-banner-text">{kpi.ai_executive_summary}</div>
    </div>
    """, unsafe_allow_html=True)

    # Core Financial KPI Cards (Grid of 4x2)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Marketing Spend</div>
            <div class="kpi-value">{sym}{kpi.total_spend:,.2f}</div>
            <div class="kpi-formula">Budget Used: {kpi.budget_utilization}% of {sym}{kpi.target_budget:,.0f}</div>
            <span class="kpi-badge-warning">{len(kpi.channels)} Channels Active</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Attributed Revenue</div>
            <div class="kpi-value">{sym}{kpi.total_revenue:,.2f}</div>
            <div class="kpi-formula">Gross Revenue credited to marketing</div>
            <span class="kpi-badge-positive">Blended ROAS: {kpi.roas:.2f}x</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Contribution Profit</div>
            <div class="kpi-value">{sym}{kpi.contribution_profit:,.2f}</div>
            <div class="kpi-formula">Gross Profit ({sym}{kpi.gross_profit:,.0f}) − Ad Spend</div>
            <span class="{'kpi-badge-positive' if kpi.contribution_profit > 0 else 'kpi-badge-danger'}">Marketing Net Margin</span>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Marketing ROI</div>
            <div class="kpi-value">{kpi.marketing_roi:+.1f}%</div>
            <div class="kpi-formula">(Net Profit − Spend) / Spend × 100</div>
            <span class="{'kpi-badge-positive' if kpi.marketing_roi > 0 else 'kpi-badge-danger'}">Capital Efficiency</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Return on Ad Spend (ROAS)</div>
            <div class="kpi-value">{kpi.roas:.2f}x</div>
            <div class="kpi-formula">Attributed Revenue / Spend</div>
            <span class="{'kpi-badge-positive' if kpi.roas >= 2.0 else 'kpi-badge-warning'}">Benchmark: 2.0x+</span>
        </div>
        """, unsafe_allow_html=True)
    with c6:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Customer Acquisition Cost</div>
            <div class="kpi-value">{sym}{kpi.cac:,.2f}</div>
            <div class="kpi-formula">Total Spend / Acquired Customers</div>
            <span class="kpi-badge-warning">{kpi.acquired_customers:,} Acquisitions</span>
        </div>
        """, unsafe_allow_html=True)
    with c7:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Customer Lifetime Value (CLV)</div>
            <div class="kpi-value">{sym}{kpi.clv:,.2f}</div>
            <div class="kpi-formula">Avg Lifetime Gross Revenue / Customer</div>
            <span class="kpi-badge-positive">LTV:CAC Ratio: {kpi.ltv_cac_ratio:.1f}x</span>
        </div>
        """, unsafe_allow_html=True)
    with c8:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Conversion Funnel CVR</div>
            <div class="kpi-value">{kpi.overall_cvr:.2f}%</div>
            <div class="kpi-formula">CTR: {kpi.overall_ctr:.2f}% | CPC: {sym}{kpi.overall_cpc:.2f}</div>
            <span class="kpi-badge-positive">Blended CPA: {sym}{kpi.overall_cpa:.2f}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    if records_count > 0:
        # Charts Row 1: Revenue vs Spend Trend & Channel Contribution
        col_g1, col_g2 = st.columns([6, 4])
        with col_g1:
            st.subheader("📈 Revenue, Marketing Spend & Profit Trajectory")
            trend_df = pd.DataFrame([{
                "Month": m.month,
                "Spend": m.spend,
                "Revenue": m.revenue,
                "Contribution Profit": m.profit,
                "ROAS": m.roas
            } for m in kpi.monthly_trends])

            fig_trend = go.Figure()
            fig_trend.add_trace(go.Bar(
                x=trend_df["Month"],
                y=trend_df["Spend"],
                name="Marketing Spend",
                marker_color="#94A3B8",
                opacity=0.75
            ))
            fig_trend.add_trace(go.Scatter(
                x=trend_df["Month"],
                y=trend_df["Revenue"],
                name="Attributed Revenue",
                mode="lines+markers",
                line=dict(color="#3B82F6", width=3)
            ))
            fig_trend.add_trace(go.Scatter(
                x=trend_df["Month"],
                y=trend_df["Contribution Profit"],
                name="Contribution Profit",
                mode="lines+markers",
                line=dict(color="#10B981", width=3, dash="dot")
            ))
            fig_trend.update_layout(
                barmode="group",
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=20, r=20, t=30, b=20),
                height=340
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_g2:
            st.subheader("🥧 Channel Spend vs Revenue Share")
            ch_df = pd.DataFrame([{
                "Channel": ch.channel,
                "Spend": ch.spend,
                "Revenue": ch.revenue,
                "ROAS": ch.roas
            } for ch in kpi.channels])

            fig_donut = px.pie(
                ch_df,
                values="Spend",
                names="Channel",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_donut.update_layout(
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                margin=dict(l=10, r=10, t=10, b=10),
                height=340
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        # Charts Row 2: Channel ROAS & CAC Comparison
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("⚡ Return on Ad Spend (ROAS) by Channel")
            fig_roas = px.bar(
                ch_df.sort_values("ROAS", ascending=True),
                x="ROAS",
                y="Channel",
                orientation="h",
                text="ROAS",
                color="ROAS",
                color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"]
            )
            fig_roas.add_vline(x=2.0, line_dash="dash", line_color="#EF4444", annotation_text="2.0x Target")
            fig_roas.update_layout(plot_bgcolor="#FFFFFF", height=280, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_roas, use_container_width=True)

        with col_c2:
            st.subheader("🎯 Customer Acquisition Cost (CAC) by Channel")
            cac_df = pd.DataFrame([{
                "Channel": ch.channel,
                "CAC": ch.cac,
                "Conversions": ch.conversions
            } for ch in kpi.channels])
            fig_cac = px.bar(
                cac_df.sort_values("CAC", ascending=False),
                x="Channel",
                y="CAC",
                text="CAC",
                color="CAC",
                color_continuous_scale=["#10B981", "#F59E0B", "#EF4444"]
            )
            fig_cac.update_layout(plot_bgcolor="#FFFFFF", height=280, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_cac, use_container_width=True)

    else:
        st.warning("No records found in this workspace. Click 'Load Realistic Demo Data' in the sidebar or upload files in Data Management.")

# -----------------------------------------------------------------------------
# MODULE 2: CAMPAIGN INTELLIGENCE
# -----------------------------------------------------------------------------
elif nav_selection == "2. Campaign Intelligence":
    st.title("Campaign Intelligence Module")
    st.markdown("Granular campaign performance metrics, unit economics, conversion funnels, and automated diagnostic flags.")

    camp_items = analyze_campaigns(
        db,
        st.session_state.workspace_id,
        channel_filter=selected_channel if selected_channel != "All Channels" else None
    )

    if not camp_items:
        st.warning("No campaigns found for current filters.")
    else:
        # Diagnostic Flag Counters
        danger_count = sum(1 for c in camp_items if any(f.type == "danger" for f in c.flags))
        warn_count = sum(1 for c in camp_items if any(f.type == "warning" for f in c.flags))
        top_count = sum(1 for c in camp_items if c.performance_status == "Top Performer")

        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        col_f1.metric("Total Analyzed Campaigns", len(camp_items))
        col_f2.metric("Top Performers", top_count)
        col_f3.metric("Margin Leakages (Danger Flags)", danger_count)
        col_f4.metric("Efficiency Alerts (Warnings)", warn_count)

        st.markdown("---")

        # Interactive Filter and Sort controls
        c_sort1, c_sort2, c_search = st.columns([3, 3, 4])
        with c_sort1:
            sort_criterion = st.selectbox("Sort Table By", ["spend", "revenue", "roas", "profit", "cpa"], index=0)
        with c_sort2:
            status_filter = st.selectbox("Performance Tier", ["All Tiers", "Top Performer", "Profitable Growth", "High Waste", "Underperforming", "Low Data / Pilot"], index=0)
        with c_search:
            search_query = st.text_input("Search Campaign Name", "")

        # Filter items
        filtered_items = camp_items
        if status_filter != "All Tiers":
            filtered_items = [c for c in filtered_items if c.performance_status == status_filter]
        if search_query:
            filtered_items = [c for c in filtered_items if search_query.lower() in c.campaign_name.lower()]

        # Main Campaign Performance Table
        table_rows = []
        for c in filtered_items:
            table_rows.append({
                "Campaign Name": c.campaign_name,
                "Channel": c.channel,
                "Spend ($)": f"${c.spend:,.2f}",
                "Revenue ($)": f"${c.attributed_revenue:,.2f}",
                "ROAS": f"{c.roas:.2f}x",
                "Profit ($)": f"${c.contribution_profit:,.2f}",
                "Clicks": f"{c.clicks:,}",
                "CTR": f"{c.ctr:.2f}%",
                "Conversions": c.conversions,
                "CVR": f"{c.cvr:.2f}%",
                "CPA ($)": f"${c.cpa:.2f}",
                "Status": c.performance_status
            })

        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, height=350)

        st.markdown("---")
        st.subheader("🚨 Automated Actionable Flags & Root Cause Diagnostics")
        st.caption("Flags are mathematically generated using exact calculated thresholds (no speculative classifications).")

        flag_cols = st.columns(2)
        for idx, c in enumerate(filtered_items):
            if c.flags:
                col = flag_cols[idx % 2]
                with col:
                    st.markdown(f"**{c.campaign_name}** (`{c.channel}`)")
                    for f in c.flags:
                        css_class = f"flag-tag-{f.type}"
                        st.markdown(f"""
                        <div class="{css_class}">
                            <strong>{f.label}:</strong> {f.reason}
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        st.markdown("---")
        # Visual Funnel & Spend vs Revenue Scatter
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.subheader("📊 Spend vs Attributed Revenue Efficiency")
            df_scatter = pd.DataFrame([{
                "Campaign": c.campaign_name,
                "Channel": c.channel,
                "Spend": c.spend,
                "Revenue": c.attributed_revenue,
                "ROAS": c.roas,
                "Conversions": c.conversions
            } for c in filtered_items])
            
            fig_scat = px.scatter(
                df_scatter,
                x="Spend",
                y="Revenue",
                size="Conversions",
                color="Channel",
                hover_name="Campaign",
                text="Campaign"
            )
            # 2.0x break-even line
            max_val = max(df_scatter["Spend"].max(), 1000)
            fig_scat.add_trace(go.Scatter(
                x=[0, max_val],
                y=[0, max_val * 2.0],
                mode="lines",
                name="2.0x ROAS Boundary",
                line=dict(color="#94A3B8", dash="dash")
            ))
            fig_scat.update_layout(plot_bgcolor="#FFFFFF", height=380)
            st.plotly_chart(fig_scat, use_container_width=True)

        with col_v2:
            st.subheader("🔻 Macro Conversion Funnel")
            tot_impr = sum(c.impressions for c in filtered_items)
            tot_clk = sum(c.clicks for c in filtered_items)
            tot_cnv = sum(c.conversions for c in filtered_items)

            fig_funnel = go.Figure(go.Funnel(
                y=["Impressions", "Clicks (Traffic)", "Conversions (Customers)"],
                x=[tot_impr, tot_clk, tot_cnv],
                textinfo="value+percent initial",
                marker=dict(color=["#3B82F6", "#6366F1", "#10B981"])
            ))
            fig_funnel.update_layout(plot_bgcolor="#FFFFFF", height=380)
            st.plotly_chart(fig_funnel, use_container_width=True)

# -----------------------------------------------------------------------------
# MODULE 3: CUSTOMER PROFITABILITY & COHORTS
# -----------------------------------------------------------------------------
elif nav_selection == "3. Customer Profitability":
    st.title("Customer Profitability & Cohort Intelligence")
    st.markdown("Evaluation of customer quality, repeat purchase behavior, monthly retention decay, and acquisition channel LTV:CAC.")

    cust_overview = analyze_customer_profitability(
        db,
        st.session_state.workspace_id,
        channel_filter=selected_channel if selected_channel != "All Channels" else None
    )

    if cust_overview.data_limitation_note:
        st.info(cust_overview.data_limitation_note)

    # Unit Economics Overview Cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Profiled Customers", f"{cust_overview.total_customers:,}")
    c2.metric("Repeat Purchase Rate", f"{cust_overview.overall_repeat_rate:.1f}%")
    c3.metric("Average Customer CLV", f"{sym}{cust_overview.overall_clv:,.2f}")
    c4.metric("LTV : CAC Ratio", f"{cust_overview.ltv_cac_ratio:.1f}x", delta="Healthy (>= 3.0x)" if cust_overview.ltv_cac_ratio >= 3.0 else "Warning (< 3.0x)")

    st.markdown("---")

    if cust_overview.segments:
        col_s1, col_s2 = st.columns([5, 5])
        with col_s1:
            st.subheader("👥 Customer Segment Breakdown")
            seg_df = pd.DataFrame([{
                "Segment": s.segment_name,
                "Customer Count": f"{s.customer_count:,}",
                "Share (%)": f"{s.percentage:.1f}%",
                "Total Revenue": f"{sym}{s.total_revenue:,.2f}",
                "AOV": f"{sym}{s.avg_order_value:.2f}",
                "CLV": f"{sym}{s.avg_clv:.2f}",
                "Repeat Rate": f"{s.repeat_rate:.1f}%",
                "Avg Churn Risk": f"{s.avg_churn_risk:.2f}"
            } for s in cust_overview.segments])
            st.dataframe(seg_df, use_container_width=True, height=260)

        with col_s2:
            st.subheader("📊 Revenue Contribution by Segment")
            pie_df = pd.DataFrame([{
                "Segment": s.segment_name,
                "Revenue": s.total_revenue
            } for s in cust_overview.segments])
            fig_seg_pie = px.pie(
                pie_df,
                names="Segment",
                values="Revenue",
                color_discrete_sequence=["#10B981", "#3B82F6", "#F59E0B", "#94A3B8", "#EF4444"]
            )
            fig_seg_pie.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_seg_pie, use_container_width=True)

    if cust_overview.cohorts:
        st.markdown("---")
        st.subheader("📅 Customer Retention Cohort Matrix (% Retained Over Time)")
        cohort_table = []
        for c in cust_overview.cohorts:
            cohort_table.append({
                "Cohort Month": c.cohort_month,
                "Acquired Users": c.initial_customers,
                "M1 (%)": f"{c.m1_retention}%",
                "M2 (%)": f"{c.m2_retention}%",
                "M3 (%)": f"{c.m3_retention}%",
                "M4 (%)": f"{c.m4_retention}%",
                "M5 (%)": f"{c.m5_retention}%",
                "M6 (%)": f"{c.m6_retention}%",
                "Cumulative Rev": f"{sym}{c.cumulative_revenue:,.2f}",
                "Avg CLV": f"{sym}{c.avg_clv:.2f}"
            })
        st.dataframe(pd.DataFrame(cohort_table), use_container_width=True)

    if cust_overview.campaign_quality:
        st.markdown("---")
        st.subheader("🏆 Campaign Customer Quality Ranking (LTV : CAC)")
        st.caption("Identifies which advertising sources acquire customers that generate recurring orders vs one-and-done churners.")
        
        cq_table = []
        for cq in cust_overview.campaign_quality:
            cq_table.append({
                "Campaign": cq.campaign_name,
                "Channel": cq.channel,
                "Users Acquired": cq.customers_acquired,
                "CAC ($)": f"${cq.cac:.2f}",
                "Repeat Rate": f"{cq.repeat_purchase_rate:.1f}%",
                "AOV ($)": f"${cq.avg_order_value:.2f}",
                "Avg CLV ($)": f"${cq.avg_clv:.2f}",
                "LTV : CAC": f"{cq.ltv_cac:.2f}x"
            })
        st.dataframe(pd.DataFrame(cq_table), use_container_width=True)

# -----------------------------------------------------------------------------
# MODULE 4: ATTRIBUTION ANALYTICS
# -----------------------------------------------------------------------------
elif nav_selection == "4. Attribution Analytics":
    st.title("Attribution Analytics & Multi-Touch Modeling")
    st.markdown("Cross-model comparison: **First-Touch** (Upper-Funnel Discovery), **Last-Touch** (Conversion Closing), and **Linear** (Shared Multi-Touch).")

    attr = calculate_attribution_models(db, st.session_state.workspace_id)

    # Causal Disclaimer Alert Callout
    st.info(f"⚖️ {attr.causal_disclaimer}")

    if not attr.channels:
        st.warning("No touchpoint data available.")
    else:
        # Comparison Table
        st.subheader("📊 Cross-Model Channel Revenue Attribution")
        attr_rows = []
        for ch in attr.channels:
            attr_rows.append({
                "Channel": ch.channel,
                "First-Touch Rev ($)": f"${ch.first_touch_revenue:,.2f}",
                "First-Touch Share": f"{ch.first_touch_share:.1f}%",
                "Last-Touch Rev ($)": f"${ch.last_touch_revenue:,.2f}",
                "Last-Touch Share": f"{ch.last_touch_share:.1f}%",
                "Linear Rev ($)": f"${ch.linear_revenue:,.2f}",
                "Linear Share": f"{ch.linear_share:.1f}%",
                "Assisted Conversions": ch.assisted_conversions,
                "Avg Path Touchpoints": ch.touchpoint_frequency
            })
        st.dataframe(pd.DataFrame(attr_rows), use_container_width=True)

        st.markdown("---")
        # Visual Comparison Bar Chart
        col_a1, col_a2 = st.columns([6, 4])
        with col_a1:
            st.subheader("📈 Attribution Model Revenue Shifts by Channel")
            viz_data = []
            for ch in attr.channels:
                viz_data.append({"Channel": ch.channel, "Model": "First-Touch", "Revenue": ch.first_touch_revenue})
                viz_data.append({"Channel": ch.channel, "Model": "Last-Touch", "Revenue": ch.last_touch_revenue})
                viz_data.append({"Channel": ch.channel, "Model": "Linear", "Revenue": ch.linear_revenue})
            
            fig_attr = px.bar(
                pd.DataFrame(viz_data),
                x="Channel",
                y="Revenue",
                color="Model",
                barmode="group",
                color_discrete_sequence=["#38BDF8", "#818CF8", "#10B981"]
            )
            fig_attr.update_layout(plot_bgcolor="#FFFFFF", height=340)
            st.plotly_chart(fig_attr, use_container_width=True)

        with col_a2:
            st.subheader("💡 Strategic Attribution Takeaways")
            for ins in attr.insights:
                st.markdown(f"• {ins}")
            
            if attr.overlap_analysis:
                st.markdown("**Top Observed Multi-Channel Customer Journeys:**")
                for ov in attr.overlap_analysis:
                    st.markdown(f"- `{ov['path']}`: **{ov['conversions']:,} customer paths**")

# -----------------------------------------------------------------------------
# MODULE 5: AI BUDGET OPTIMIZER (CORE FEATURE)
# -----------------------------------------------------------------------------
elif nav_selection == "5. AI Budget Optimizer":
    st.title("AI-Powered Marketing Budget Optimizer")
    st.markdown("Mathematically constrained optimization allocating capital based on non-linear diminishing returns response curves and gross margin economics.")

    c_opt1, c_opt2 = st.columns([7, 3])
    with c_opt1:
        opt_objective = st.selectbox(
            "Optimization Target Objective",
            [
                ("maximize_profit", "🎯 Maximize Contribution Profit (Net Cash Margin after COGS)"),
                ("maximize_revenue", "📈 Maximize Attributed Revenue (Top-Line Growth)"),
                ("maximize_conversions", "👥 Maximize Total Conversions within Target CPA"),
                ("prioritize_high_value", "💎 Prioritize High-LTV & Repeat Customer Acquisition")
            ],
            format_func=lambda x: x[1],
            index=0
        )[0]
    with c_opt2:
        new_budget = st.number_input(
            "Total Available Budget ($)",
            min_value=10000.0,
            max_value=1000000.0,
            value=float(target_budget),
            step=5000.0
        )

    # Campaign Protection Controls
    campaigns_in_db = db.query(CampaignRecord.campaign_id, CampaignRecord.campaign_name).filter(
        CampaignRecord.workspace_id == st.session_state.workspace_id
    ).distinct().all()

    camp_dict = {cid: cname for cid, cname in campaigns_in_db}
    
    with st.expander("🛡️ Advanced Constraints: Protect Essential Campaigns & Spending Shift Caps", expanded=False):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            protected_ids = st.multiselect(
                "Protected Campaigns (Guaranteed NO Budget Cuts)",
                options=list(camp_dict.keys()),
                format_func=lambda x: f"{camp_dict.get(x, x)} ({x})",
                default=[cid for cid in camp_dict.keys() if "Brand Intent" in camp_dict.get(cid, "")]
            )
        with col_p2:
            shift_cap = st.slider(
                "Maximum Permitted Allocation Shift per Campaign (%)",
                min_value=10,
                max_value=50,
                value=30,
                help="Limits extreme reallocations to ensure business continuity and stable ad auction bidding."
            )

    # Run Optimization
    opt_res = optimize_marketing_budget(
        db,
        st.session_state.workspace_id,
        target_budget=new_budget,
        objective=opt_objective,
        protected_campaigns=protected_ids,
        max_change_pct=float(shift_cap)
    )

    if not opt_res:
        st.warning("Please load or import campaign data to run the budget optimization engine.")
    else:
        st.markdown("---")
        # 3 Scenario Comparison Cards
        st.subheader("⚖️ Scenario Comparison: Current vs Conservative vs AI-Recommended")
        sc_col1, sc_col2, sc_col3 = st.columns(3)

        sc_cur = opt_res.current_scenario
        sc_con = opt_res.conservative_scenario
        sc_ai = opt_res.ai_recommended_scenario

        with sc_col1:
            st.markdown(f"""
            <div class="kpi-card" style="border-top: 4px solid #94A3B8;">
                <div class="kpi-label">Current Allocation</div>
                <div class="kpi-value">{sym}{sc_cur.expected_profit:,.0f} <span style="font-size:14px;color:#64748B;">Profit</span></div>
                <div style="font-size: 13px; color: #475569; margin-top: 6px;">
                    • <strong>Revenue:</strong> {sym}{sc_cur.expected_revenue:,.0f}<br>
                    • <strong>Expected ROAS:</strong> {sc_cur.expected_roas:.2f}x<br>
                    • <strong>Conversions:</strong> {sc_cur.expected_conversions:,}<br>
                    • <strong>Blended CPA:</strong> {sym}{sc_cur.blended_cpa:.2f}
                </div>
                <span class="kpi-badge-warning" style="margin-top: 10px;">Baseline Status Quo</span>
            </div>
            """, unsafe_allow_html=True)

        with sc_col2:
            profit_lift_con = ((sc_con.expected_profit - sc_cur.expected_profit) / max(sc_cur.expected_profit, 1.0)) * 100
            st.markdown(f"""
            <div class="kpi-card" style="border-top: 4px solid #3B82F6;">
                <div class="kpi-label">Conservative Shift (+/- 15%)</div>
                <div class="kpi-value">{sym}{sc_con.expected_profit:,.0f} <span style="font-size:14px;color:#10B981;">(+{profit_lift_con:.1f}%)</span></div>
                <div style="font-size: 13px; color: #475569; margin-top: 6px;">
                    • <strong>Revenue:</strong> {sym}{sc_con.expected_revenue:,.0f}<br>
                    • <strong>Expected ROAS:</strong> {sc_con.expected_roas:.2f}x<br>
                    • <strong>Conversions:</strong> {sc_con.expected_conversions:,}<br>
                    • <strong>Blended CPA:</strong> {sym}{sc_con.blended_cpa:.2f}
                </div>
                <span class="kpi-badge-positive" style="margin-top: 10px;">Low Risk / Guarded Shift</span>
            </div>
            """, unsafe_allow_html=True)

        with sc_col3:
            profit_lift_ai = ((sc_ai.expected_profit - sc_cur.expected_profit) / max(sc_cur.expected_profit, 1.0)) * 100
            st.markdown(f"""
            <div class="kpi-card" style="border-top: 4px solid #10B981; background: #F0FDF4;">
                <div class="kpi-label" style="color: #047857;">AI-Recommended Optimal</div>
                <div class="kpi-value" style="color: #065F46;">{sym}{sc_ai.expected_profit:,.0f} <span style="font-size:14px;color:#059669;">(+{profit_lift_ai:.1f}%)</span></div>
                <div style="font-size: 13px; color: #064E3B; margin-top: 6px;">
                    • <strong>Revenue:</strong> {sym}{sc_ai.expected_revenue:,.0f}<br>
                    • <strong>Expected ROAS:</strong> {sc_ai.expected_roas:.2f}x<br>
                    • <strong>Conversions:</strong> {sc_ai.expected_conversions:,}<br>
                    • <strong>Blended CPA:</strong> {sym}{sc_ai.blended_cpa:.2f}
                </div>
                <span class="kpi-badge-positive" style="background:#A7F3D0;color:#064E3B;margin-top: 10px;">Max Efficiency Target</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # Before & After Budget Reallocation Waterfall / Grouped Chart
        st.subheader("📊 Before & After Campaign Budget Reallocations")
        alloc_plot_data = []
        for a in sc_ai.allocations:
            alloc_plot_data.append({"Campaign": a.campaign_name, "Type": "Current Budget", "Spend": a.current_spend})
            alloc_plot_data.append({"Campaign": a.campaign_name, "Type": "Proposed Budget", "Spend": a.proposed_spend})
        
        fig_alloc = px.bar(
            pd.DataFrame(alloc_plot_data),
            x="Spend",
            y="Campaign",
            color="Type",
            barmode="group",
            orientation="h",
            color_discrete_map={"Current Budget": "#94A3B8", "Proposed Budget": "#10B981"}
        )
        fig_alloc.update_layout(plot_bgcolor="#FFFFFF", height=420)
        st.plotly_chart(fig_alloc, use_container_width=True)

        # Detailed Allocation Table with Explainability Rationales
        st.markdown("---")
        st.subheader("📝 Campaign Reallocation Proposals & AI Rationales")
        st.caption("Every proposed dollar shift includes an explicit mathematical explanation grounded in unit economics.")

        alloc_rows = []
        for a in sc_ai.allocations:
            alloc_rows.append({
                "Campaign Name": a.campaign_name,
                "Channel": a.channel,
                "Current Spend": f"${a.current_spend:,.2f}",
                "Proposed Spend": f"${a.proposed_spend:,.2f}",
                "Delta ($)": f"{a.spend_diff:+,.2f}",
                "Delta (%)": f"{a.spend_diff_percent:+.1f}%",
                "Exp. ROAS": f"{a.expected_roas:.2f}x",
                "Exp. Profit": f"${a.expected_profit:,.2f}",
                "Confidence": a.confidence,
                "AI Rationale": a.rationale
            })
        st.dataframe(pd.DataFrame(alloc_rows), use_container_width=True)

        with st.expander("ℹ️ Scientific Optimization Methodology & Assumptions", expanded=False):
            st.markdown(f"**Methodology:** {opt_res.methodology}")
            for ass in opt_res.assumptions_and_limitations:
                st.markdown(f"• {ass}")

# -----------------------------------------------------------------------------
# MODULE 6: PREDICTIVE INSIGHTS & MACHINE LEARNING
# -----------------------------------------------------------------------------
elif nav_selection == "6. Predictive Insights":
    st.title("Predictive Analytics & Machine Learning Models")
    st.markdown("Trained statistical models utilizing historical marketing data, conversion rates, and retention signals.")

    with st.spinner("Training predictive models on active workspace data..."):
        ml_results = train_and_evaluate_models(db, st.session_state.workspace_id)

    if ml_results.get("status") == "insufficient_data":
        st.warning(f"⚠️ {ml_results.get('message')}")
    else:
        col_m1, col_m2 = st.columns(2)
        
        # Model 1: Conversion Classifier
        with col_m1:
            m_c = ml_results["conversion_classifier"]
            st.subheader(f"🌲 {m_c['name']}")
            st.markdown(f"**Algorithm:** `{m_c['type']}` | **Target:** `{m_c['target']}`")
            
            c_met1, c_met2 = st.columns(2)
            for m in m_c["metrics"]:
                c_met1.metric(m["name"], m["score"], delta=f"Target: {m['benchmark']}")

            st.markdown("**Top Predictive Feature Importances:**")
            fi_df = pd.DataFrame(m_c["feature_importances"])
            fig_fi = px.bar(fi_df, x="importance", y="feature", orientation="h", color="importance", color_continuous_scale="Viridis")
            fig_fi.update_layout(plot_bgcolor="#FFFFFF", height=200, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_fi, use_container_width=True)

        # Model 2: Retention & Churn Classifier
        with col_m2:
            if "churn_model" in ml_results and ml_results["churn_model"]:
                m_ch = ml_results["churn_model"]
                st.subheader(f"🛡️ {m_ch['name']}")
                st.markdown(f"**Algorithm:** `{m_ch['type']}` | **Target:** `{m_ch['target']}`")
                
                ch_cols = st.columns(len(m_ch["metrics"]))
                for idx, met in enumerate(m_ch["metrics"]):
                    ch_cols[idx].metric(met["name"], met["score"])

                st.markdown("**Top Churn Risk Coefficients:**")
                cw_df = pd.DataFrame(m_ch["feature_weights"])
                st.dataframe(cw_df, use_container_width=True, height=160)
            else:
                st.info("Upload individual customer cohort records to activate Churn Risk Classification.")

        st.markdown("---")
        # 30-Day Forward Trend Forecasting
        st.subheader("📈 30-Day Forward Trend Forecast (Spend & Revenue)")
        st.caption("Auto-regressive trend with confidence boundaries distinguishing historical results from predicted values.")

        ts_points = ml_results.get("forecast_curve", [])
        if ts_points:
            ts_df = pd.DataFrame(ts_points)
            fig_fc = go.Figure()

            # Historical Spend & Revenue
            fig_fc.add_trace(go.Scatter(
                x=ts_df["date"],
                y=ts_df["historical_spend"],
                name="Historical Spend ($)",
                line=dict(color="#64748B", width=2)
            ))
            fig_fc.add_trace(go.Scatter(
                x=ts_df["date"],
                y=ts_df["historical_revenue"],
                name="Historical Revenue ($)",
                line=dict(color="#3B82F6", width=2.5)
            ))

            # Forecasted Spend & Revenue
            fig_fc.add_trace(go.Scatter(
                x=ts_df["date"],
                y=ts_df["predicted_spend"],
                name="Projected Spend (Forecast)",
                line=dict(color="#F59E0B", width=2, dash="dash")
            ))
            fig_fc.add_trace(go.Scatter(
                x=ts_df["date"],
                y=ts_df["predicted_revenue"],
                name="Projected Revenue (Forecast)",
                line=dict(color="#10B981", width=2.5, dash="dash")
            ))

            fig_fc.update_layout(
                plot_bgcolor="#FFFFFF",
                height=350,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_fc, use_container_width=True)

# -----------------------------------------------------------------------------
# MODULE 7: AI MARKETING ASSISTANT
# -----------------------------------------------------------------------------
elif nav_selection == "7. AI Marketing Assistant":
    st.title("AI Marketing Intelligence Assistant")
    st.markdown("Grounded, deterministic analytical advisor answering executive marketing questions using exact calculated metrics.")

    # Sample Quick Questions
    st.markdown("**Suggested Executive Questions:**")
    q_col1, q_col2, q_col3 = st.columns(3)
    preset_q = None
    if q_col1.button("💸 Which campaigns are wasting money?", use_container_width=True):
        preset_q = "Which campaigns are wasting money?"
    if q_col2.button("🏆 Which channel has the strongest ROAS?", use_container_width=True):
        preset_q = "Which channel has the strongest ROAS?"
    if q_col3.button("📉 Why is customer acquisition cost increasing?", use_container_width=True):
        preset_q = "Why is customer acquisition cost increasing?"

    q_col4, q_col5, q_col6 = st.columns(3)
    if q_col4.button("🚀 Which campaigns should receive additional budget?", use_container_width=True):
        preset_q = "Which campaigns should receive additional budget?"
    if q_col5.button("💡 Revenue growth vs. profitable growth?", use_container_width=True):
        preset_q = "What is the difference between revenue growth and profitable growth?"
    if q_col6.button("✂️ What if we reduced budget by 10%?", use_container_width=True):
        preset_q = "What would happen if we reduced the budget by 10%?"

    # Query Input Box
    user_query = st.text_input("Ask a question about your marketing data:", value=preset_q or "")

    if user_query:
        with st.spinner("Analyzing workspace calculations..."):
            ai_ans = answer_marketing_query(db, st.session_state.workspace_id, user_query)

        st.markdown(f"""
        <div style="background:#F8FAFC;border:1px solid #CBD5E1;border-radius:10px;padding:22px;margin-top:16px;">
            <div style="font-size:12px;font-weight:700;color:#2563EB;text-transform:uppercase;margin-bottom:8px;">
                MARKETIQ AI Response • Category: {ai_ans.get('category', 'Analytical')}
            </div>
            <div style="font-size:15px;line-height:1.6;color:#1E293B;">
                {ai_ans.get('answer', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if ai_ans.get("supporting_facts"):
            with st.expander("🔍 Verified Grounding Facts & Referenced Data", expanded=False):
                for fact in ai_ans["supporting_facts"]:
                    st.markdown(f"• {fact}")

# -----------------------------------------------------------------------------
# MODULE 8: REPORTS & EXPORTS
# -----------------------------------------------------------------------------
elif nav_selection == "8. Reports & Exports":
    st.title("Executive Reports & Data Exports")
    st.markdown("Generate and export professional marketing audit packages in CSV, Excel (.xlsx), and printable executive brief formats.")

    col_rep1, col_rep2, col_rep3 = st.columns(3)

    # 1. Excel Export
    with col_rep1:
        st.subheader("📑 Full Executive Workbook")
        st.markdown("Includes Executive Overview, Campaign Intelligence, Channel Breakdown, Budget Proposals, and Customer Segments across formatted worksheets.")
        excel_bytes = generate_excel_full_report(db, st.session_state.workspace_id)
        st.download_button(
            label="📥 Download Excel Workbook (.xlsx)",
            data=excel_bytes,
            file_name=f"marketiq_report_{datetime.utcnow().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )

    # 2. CSV Export
    with col_rep2:
        st.subheader("📊 Campaign Performance CSV")
        st.markdown("Raw and calculated campaign metrics including CTR, CPC, CPA, ROAS, Contribution Profit, and automated diagnostic flags.")
        csv_data = generate_csv_campaign_report(db, st.session_state.workspace_id)
        st.download_button(
            label="📥 Download Campaign CSV",
            data=csv_data,
            file_name=f"marketiq_campaigns_{datetime.utcnow().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # 3. Text Brief
    with col_rep3:
        st.subheader("📄 C-Suite Text Brief")
        st.markdown("Clean, structured ASCII brief formatted for board packets, executive email summaries, and MBA presentations.")
        text_brief = generate_executive_text_brief(db, st.session_state.workspace_id)
        st.download_button(
            label="📥 Download Executive Brief (.txt)",
            data=text_brief,
            file_name=f"marketiq_executive_brief_{datetime.utcnow().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("👁️ Live Preview of Executive Intelligence Brief")
    st.code(text_brief, language="markdown")

# -----------------------------------------------------------------------------
# MODULE 9: DATA MANAGEMENT & SETTINGS
# -----------------------------------------------------------------------------
elif nav_selection == "9. Data Management & Settings":
    st.title("Data Management, Upload & Workspace Settings")
    st.markdown("Upload marketing datasets, map custom columns, inspect data quality scores, and configure workspace profiles.")

    tab_upload, tab_sample, tab_settings = st.tabs(["📤 File Upload & Data Mapping", "📥 Sample Templates & Dictionary", "⚙️ Workspace Profile"])

    with tab_upload:
        st.subheader("Upload Marketing Performance Data (CSV or Excel)")
        uploaded_file = st.file_uploader("Select a CSV or Excel file", type=["csv", "xlsx", "xls"])

        if uploaded_file:
            file_bytes = uploaded_file.read()
            val_res = validate_and_parse_dataset(file_bytes, uploaded_file.name)

            if not val_res["success"]:
                st.error(val_res["error"])
            else:
                st.success(f"File **{uploaded_file.name}** parsed successfully: {val_res['total_rows']:,} rows detected.")
                
                # Quality Score card
                q_col1, q_col2, q_col3 = st.columns(3)
                q_col1.metric("Data Quality Score", f"{val_res['quality_score']}%", delta="High Quality" if val_res['quality_score'] >= 80 else "Needs Review")
                q_col2.metric("Total Records", f"{val_res['total_rows']:,}")
                q_col3.metric("Duplicate Rows", f"{val_res['duplicates']:,}")

                # Issues list
                if val_res["issues"]:
                    st.markdown("**Validation Notices:**")
                    for iss in val_res["issues"]:
                        if iss["severity"] == "CRITICAL":
                            st.error(iss["message"])
                        elif iss["severity"] == "WARNING":
                            st.warning(iss["message"])
                        else:
                            st.info(iss["message"])

                # Column Mapping Interface
                st.markdown("---")
                st.subheader("🗺️ Column Mapping Interface")
                st.caption("Verify or adjust matching between your file's headers and MARKETIQ analytical fields.")

                cols = val_res["detected_columns"]
                mapping_cols = st.columns(3)
                user_mapping = {}

                fields_to_map = [
                    ("campaign_name", "Campaign Name *", True),
                    ("channel", "Marketing Channel *", True),
                    ("spend", "Advertising Spend *", True),
                    ("conversions", "Conversions / Orders *", True),
                    ("attributed_revenue", "Attributed Revenue *", True),
                    ("date", "Activity Date", False),
                    ("campaign_id", "Campaign ID", False),
                    ("impressions", "Impressions", False),
                    ("clicks", "Clicks", False),
                    ("gross_margin_rate", "Gross Margin Rate", False)
                ]

                for idx, (f_key, f_label, is_req) in enumerate(fields_to_map):
                    c = mapping_cols[idx % 3]
                    curr_match = val_res["mapped_columns"].get(f_key)
                    sel_idx = cols.index(curr_match) if curr_match in cols else 0
                    user_mapping[f_key] = c.selectbox(
                        f_label,
                        options=["-- None / Skip --"] + cols,
                        index=sel_idx + 1 if curr_match in cols else 0
                    )
                    if user_mapping[f_key] == "-- None / Skip --":
                        user_mapping[f_key] = None

                st.markdown("---")
                st.subheader("👁️ First 10 Rows Preview")
                st.dataframe(pd.DataFrame(val_res["preview"]), use_container_width=True)

                if st.button("🚀 Complete Import into Workspace", type="primary", use_container_width=True):
                    with st.spinner("Validating and importing records into SQLite..."):
                        imp_res = import_mapped_dataset(
                            db,
                            st.session_state.workspace_id,
                            file_bytes,
                            uploaded_file.name,
                            user_mapping
                        )
                        st.success(imp_res["message"])
                        st.rerun()

    with tab_sample:
        st.subheader("Download Ready-to-Use Sample Datasets & Data Dictionary")
        st.markdown("Use these pre-formatted files as templates for preparing your company's marketing performance data.")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("##### 📄 Sample Marketing Campaigns CSV")
            st.caption("Includes Google Search, Meta Ads, LinkedIn, Email, and Affiliate marketing records with margin rates.")
            with open("data/demo/sample_campaigns.csv", "r", encoding="utf-8") as f:
                sample_csv_text = f.read()
            st.download_button(
                label="📥 Download sample_campaigns.csv",
                data=sample_csv_text,
                file_name="sample_campaigns.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col_s2:
            st.markdown("##### 📖 Data Dictionary & Formula Reference")
            st.caption("Exhaustive specifications of field definitions, data types, and transparent calculation methodologies.")
            with open("data/demo/data_dictionary.md", "r", encoding="utf-8") as f:
                dict_text = f.read()
            st.download_button(
                label="📥 Download data_dictionary.md",
                data=dict_text,
                file_name="data_dictionary.md",
                mime="text/markdown",
                use_container_width=True
            )

    with tab_settings:
        st.subheader("🏢 Workspace Profile & Financial Configuration")
        with st.form("workspace_settings_form"):
            c_w1, c_w2 = st.columns(2)
            with c_w1:
                new_org_name = st.text_input("Company / Organization Name", value=active_ws.name)
                new_industry = st.selectbox(
                    "Industry Sector",
                    ["E-commerce & Retail", "B2B SaaS & Tech", "Financial Services", "Healthcare", "Direct-to-Consumer (DTC)", "Agency / Multi-Client"],
                    index=0
                )
                new_reporting_period = st.text_input("Active Reporting Horizon", value=active_ws.reporting_period)
            with c_w2:
                new_currency = st.selectbox("Operating Currency", ["USD ($)", "EUR (€)", "GBP (£)", "INR (₹)"], index=0)
                new_target_budget = st.number_input("Target Total Marketing Budget ($)", value=float(active_ws.target_budget), step=5000.0)

            if st.form_submit_button("💾 Save Workspace Profile", type="primary", use_container_width=True):
                active_ws.name = new_org_name
                active_ws.industry = new_industry
                active_ws.reporting_period = new_reporting_period
                active_ws.target_budget = new_target_budget
                if "USD" in new_currency:
                    active_ws.currency = "USD"
                    active_ws.currency_symbol = "$"
                elif "EUR" in new_currency:
                    active_ws.currency = "EUR"
                    active_ws.currency_symbol = "€"
                elif "GBP" in new_currency:
                    active_ws.currency = "GBP"
                    active_ws.currency_symbol = "£"
                elif "INR" in new_currency:
                    active_ws.currency = "INR"
                    active_ws.currency_symbol = "₹"
                db.commit()
                st.success("Workspace profile updated successfully.")
                st.rerun()

db.close()
