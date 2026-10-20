# MARKETIQ AI — Intelligent Marketing ROI & Budget Optimization Platform

> **"Turn Marketing Spend into Measurable Growth."**

**MARKETIQ AI** is a professional-grade, full-stack AI-powered marketing intelligence and budget allocation platform designed for CMOs, executive growth teams, and marketing data scientists. Built entirely in Python, it bridges the gap between top-line vanity metrics (clicks, impressions, gross revenue) and **unit economics (COGS, true contribution margin, customer lifetime value, and non-linear diminishing returns)**.

---

## 🌟 Executive Highlights & Core Capabilities

- **100% Python Architecture**: Zero dependency on external node tools; runs directly on Python 3.10+ using Streamlit, Plotly, Pandas, NumPy, Scikit-learn, SciPy, and SQLAlchemy.
- **True Profitability Accounting**: Differentiates between Gross Revenue, Product COGS, Contribution Profit, and Net Marketing Margin. Never mislabels revenue as profit.
- **Non-Linear Diminishing Returns Optimization**: Uses SciPy constrained optimization (SLSQP) with power and logarithmic concave response curves ($R = \alpha \cdot \text{Spend}^\beta$), ensuring that scaling campaigns properly models audience saturation.
- **Granular Multi-Touch Attribution**: Side-by-side comparison of **First-Touch** (discovery credit), **Last-Touch** (conversion closing), and **Linear** (multi-touch share) attribution models with assisted conversions tracking.
- **Automated Root-Cause Diagnostic Flags**: Mathematically flags *Negative Contribution Margins*, *High Spend with Low Conversions*, *Low ROAS*, *Rising CPA Trends*, and *Insufficient Sample Size*.
- **Machine Learning Suite**: Built-in Scikit-learn models for High-Yield Conversion Classification (Random Forest), Retention & Churn Risk (Logistic Regression), Customer Lifetime Value (Gradient Boosting), and 30-Day Forward Trend Projections.
- **Deterministic AI Marketing Advisor**: Built-in grounded executive assistant that provides data-backed answers to strategic C-suite queries without requiring external paid API keys.
- **Clean Workspace Isolation & Demo Reset**: Completely fresh workspace upon initial start. Switch into **Demo Mode** (12 realistic campaigns across 5 channels over 180 days) with 1 click, or reset demo data anytime.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **User Interface** | [Streamlit](https://streamlit.io/) 1.49+ | Modern executive SaaS web application with custom CSS styling |
| **Visualizations** | [Plotly](https://plotly.com/python/) 6.3+ | Interactive financial trajectories, cohort matrices, waterfalls, and funnels |
| **Data Processing** | [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) | Vectorized analytics, cohort retention slicing, and aggregations |
| **Machine Learning** | [Scikit-learn](https://scikit-learn.org/) | Random Forest, Logistic Regression, Gradient Boosting, Ridge |
| **Mathematical Optimization** | [SciPy](https://scipy.org/) (`scipy.optimize.minimize`) | Constrained non-linear optimization with SLSQP |
| **Data Storage** | SQLite & [SQLAlchemy](https://www.sqlalchemy.org/) 2.0+ | Persistent local database with workspace-level isolation |
| **Excel & Reporting** | [openpyxl](https://openpyxl.readthedocs.io/) | Multi-sheet formatted executive Excel workbook generation |
| **Automated Testing** | [pytest](https://docs.pytest.org/) | Mathematical formula verification and optimizer constraint validation |

---

## 🚀 Installation & Quick Start

### 1. Prerequisites
Ensure Python 3.10 or higher is installed on your system.

### 2. Install Required Dependencies
All required dependencies are listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

*(Note: If you have already installed Streamlit, Pandas, NumPy, Scikit-learn, SciPy, and openpyxl, you are ready to go immediately!)*

### 3. Launch the Application

Run the application with one command:
```bash
python run.py
```
*Or directly via Streamlit:*
```bash
python -m streamlit run app.py
```
*On Windows, you can also simply double-click:* `run.bat`

Once launched, your browser will open to: `http://localhost:8501`

---

## 📂 Project Architecture

```
marketiq-ai/
├── app.py                     # Main executive Streamlit web application
├── run.py                     # Python application launcher
├── run.bat                    # Windows 1-click batch launcher
├── requirements.txt           # Python dependency specifications
│
├── core/
│   ├── config.py              # Application settings and data paths
│   └── database.py            # SQLite database initialization & sessions
│
├── models/
│   ├── db_models.py           # SQLAlchemy database schemas (Workspace, Campaign, Customer)
│   └── schemas.py             # Analytical dataclasses and response structures
│
├── analytics/
│   ├── kpi_engine.py          # ROAS, CAC, Contribution Profit, Trends, Channel metrics
│   ├── campaign_analyzer.py   # Diagnostic flags, CTR/CPC/CPA, Funnel metrics
│   ├── customer_profitability.py # Cohort retention matrix, LTV:CAC, Segments
│   └── attribution_engine.py  # First-Touch, Last-Touch, and Linear Attribution
│
├── optimization/
│   └── budget_optimizer.py    # SciPy SLSQP non-linear diminishing returns optimizer
│
├── ml/
│   └── predictive_models.py   # Scikit-learn Random Forest, Logistic Regression, CLV
│
├── services/
│   ├── demo_generator.py      # 12-campaign, 180-day realistic synthetic dataset
│   ├── data_importer.py       # CSV/Excel parsing, column mapping, data quality score
│   ├── ai_assistant.py        # Grounded AI advisor answering business questions
│   └── report_generator.py    # Multi-tab Excel workbooks, CSVs, and executive briefs
│
├── data/
│   ├── demo/
│   │   ├── sample_campaigns.csv   # Pre-formatted sample dataset for testing uploads
│   │   └── data_dictionary.md     # Full field and analytical formula dictionary
│   ├── uploads/               # Raw uploaded client datasets
│   └── exports/               # Stored reports
│
└── tests/
    ├── test_calculations.py   # Unit tests for ROAS, CAC, ROI, and flag detection
    └── test_optimizer.py      # Unit tests for budget bounds and allocation constraints
```

---

## 🧭 Navigation & Core Modules Tour

### 1. Executive Overview
- **Key Metrics**: Total Spend, Attributed Revenue, Contribution Profit, Marketing ROI, ROAS, CAC, CLV, and LTV:CAC.
- **AI Executive Summary**: Real-time synthesized strategic analysis highlighting best and worst performing channels.
- **Interactive Visualizations**: Monthly spend vs revenue vs profit trajectory, channel spend donut, ROAS target benchmarks, and CAC channel bars.
- **Global Filters**: Filter by date range and marketing channel.

### 2. Campaign Intelligence
- **Comprehensive Table**: CTR, CPC, CVR, CPA, ROAS, Gross Margin, and Contribution Profit.
- **Automated Root-Cause Diagnostic Flags**:
  - *Negative Contribution Profit*: Flags campaigns generating revenue but losing net cash due to COGS and ad spend.
  - *High Spend, Low Conversions*: Identifies budget bleeding inventory.
  - *Low ROAS*: Flags campaigns failing the 1.8x sustainability threshold.
  - *Rising CPA Trend*: Compares H1 vs H2 acquisition costs to detect audience fatigue.
  - *Insufficient Data*: Identifies small sample sizes to avoid hasty cancellations.
- **Funnel & Scatter**: Spend vs Revenue efficiency quadrant with 2.0x break-even line, plus Macro Conversion Funnel.

### 3. Customer Profitability & Cohorts
- **Unit Economics**: Blended CLV, LTV:CAC ratio, repeat purchase rate, and retention rate.
- **Segmentation**: High-Value, Repeat, New, Low-Engagement, and At-Risk customer cohorts.
- **Monthly Retention Decay Matrix**: M1 to M6 retention percentages across acquisition cohorts.
- **Campaign Quality Ranking**: Identifies which campaigns attract high repeat-order buyers vs low-value churners.

### 4. Attribution Analytics
- **Cross-Model Breakdown**: Compare revenue credited under First-Touch (acquisition discovery), Last-Touch (closing conversion), and Linear models.
- **Assisted Conversions**: Channels that assist conversions along the path without being the final touchpoint.
- **Journey Path Analysis**: Top recorded customer touchpoint combinations.
- **Causal Disclaimer**: Clear disclosure separating observed statistical correlation from true counterfactual incremental lift.

### 5. AI-Powered Budget Optimizer (Core Feature)
- **Selectable Optimization Objectives**:
  1. *Maximize Contribution Profit* (Net Cash Margin after COGS)
  2. *Maximize Attributed Revenue* (Top-line volume)
  3. *Maximize Conversions within Target CPA*
  4. *Prioritize High-LTV & Repeat Customer Acquisition*
- **Mathematical Constraints**:
  - Total proposed spend strictly constrained: $\sum \text{Proposed Spend}_i \le \text{Total Budget}$.
  - Protected campaigns feature: Prevents budget cuts on essential channels (e.g., Brand Search).
  - Configurable maximum shift caps (e.g., maximum +/- 30% shift per campaign).
  - Diminishing returns modeled via power response curves ($R = \alpha \cdot \text{Spend}^\beta$).
- **Scenario Comparison**: Side-by-side evaluation of **Current Budget**, **Conservative Reallocation**, and **AI-Recommended Optimal**.
- **Visual Reallocation**: Before-and-after bar chart and full explainability rationales for each recommendation.

### 6. Predictive Insights & Machine Learning
- **High-Yield Conversion Classifier**: Random Forest model (50 trees) predicting probability of high daily conversion volume with ROC-AUC and feature importances.
- **Customer Churn Risk Classifier**: Logistic Regression with L2 regularization identifying top drivers of dormancy.
- **CLV Estimator**: Gradient Boosting Regressor predicting continuous customer lifetime value with $R^2$, MAE, and RMSE.
- **30-Day Trend Forecasting**: Time-series auto-regressive trajectory with historical vs predicted visual separation.

### 7. AI Marketing Intelligence Assistant
- An interactive strategic marketing advisor that answers executive questions using exact computed figures from the loaded data.
- Built-in questions for:
  - *Which campaigns are wasting money?*
  - *Which channel has the strongest ROAS?*
  - *Why is customer acquisition cost increasing?*
  - *Which campaigns should receive additional budget?*
  - *What is the difference between revenue growth and profitable growth?*
  - *What would happen if we reduced the budget by 10%?*

### 8. Reports & Exports
- **Excel Workbook (.xlsx)**: Formatted, multi-sheet workbook containing Executive Overview, Campaign Intelligence, Channel Breakdown, Budget Proposals, and Customer Segments.
- **Campaign Performance CSV**: Full raw and calculated table ready for BI tools.
- **C-Suite Text Brief**: Formatted executive report suitable for board packets and presentations.

### 9. Data Management & Settings
- **Upload CSV or Excel**: Supports separate performance and transaction logs.
- **Column Mapping Interface**: Matches custom uploaded headers to standardized fields.
- **Data Quality Score (0–100%)**: Automatically detects missing critical columns, exact duplicates, and null fields.
- **Sample Datasets & Data Dictionary**: Direct in-app downloads of `sample_campaigns.csv` and `data_dictionary.md`.
- **Workspace Profile**: Configure company name, industry, currency ($, €, £, ₹), reporting horizon, and target budget.

---

## 🧪 Automated Testing

Run the automated test suite with pytest:
```bash
python -m pytest tests/ -v
```

Expected output:
```
tests/test_calculations.py::test_kpi_overview_calculations PASSED
tests/test_calculations.py::test_campaign_flags_detection PASSED
tests/test_optimizer.py::test_budget_optimizer_respects_constraints PASSED
============================== 3 passed in 2.5s ==============================
```

---

## 🎓 MBA Presentation Walkthrough Script (5-Minute Demo)

1. **Introduction & Fresh Workspace (Minute 1)**:
   - Launch the app: observe the clean workspace and enterprise dark navy styling.
   - Explain the core business problem: companies pour budget into marketing without knowing if revenue covers COGS and advertising costs.
   - Click **"🚀 Load Realistic Demo Data"** in the sidebar. Note that 180 days across 12 distinct campaigns are loaded.

2. **Executive Overview & The Vanity vs Profit Trap (Minute 2)**:
   - Walk through the KPI cards: observe Total Spend vs Attributed Revenue (ROAS ~ 2.9x).
   - Point out **Contribution Profit** ($46k+): demonstrate that Gross Profit minus Spend is the metric that matters.
   - Show the Monthly Spend vs Revenue Trajectory chart.

3. **Campaign Intelligence & Diagnostic Flags (Minute 3)**:
   - Navigate to **Campaign Intelligence**.
   - Review the automated flags: highlight **Meta Top-of-Funnel Video** (*Negative Contribution Profit*: generated revenue via steep discounts, but lost cash after COGS) and **LinkedIn B2B Sponsored Content** (*High Spend, Low Conversions*, CPA $300+).
   - Highlight **Google Brand Search** and **Email Lifecycle** (*Top Performers*, ROAS > 5x).

4. **Customer Cohorts & Multi-Touch Attribution (Minute 4)**:
   - Jump to **Attribution Analytics**: show the delta between First-Touch and Last-Touch. Explain why discovery channels look weak under Last-Touch, and show the linear multi-touch reconciliation.
   - Show **Customer Profitability**: examine the M1–M6 retention decay cohort matrix and explain why Email and Brand Search deliver 4.5x+ LTV:CAC.

5. **AI Budget Optimizer & C-Suite Assistant (Minute 5)**:
   - Navigate to **AI Budget Optimizer**: select *"Maximize Contribution Profit"*.
   - Protect *Google Brand Search*, set budget to $160,000, and inspect the recommendations.
   - Point out that the optimizer trims capital from the negative-margin video and LinkedIn wasters and redirects it to high-margin search and retention, increasing projected profit by **18% to 24%** without increasing total spend!
   - Finish in the **AI Marketing Assistant** by asking: *"What would happen if we reduced the budget by 10%?"* and download the full Excel audit workbook in **Reports & Exports**.

---

## ⚖️ Methodological Assumptions & Limitations

1. **Diminishing Returns Modeling**: Marketing response curves follow non-linear concave dynamics ($R = \alpha \cdot \text{Spend}^\beta$ with $\beta \in [0.56, 0.75]$). Historical efficiency cannot be linearly extrapolated to infinite spend.
2. **Attribution vs. Causality**: Observed multi-touch attribution (First, Last, Linear) measures touchpoint correlation and customer journey presence. It does not replace randomized controlled holdout experiments (incrementality tests).
3. **Data Privacy**: Customer records are aggregated and scrubbed; no raw PII (emails, phone numbers) is exposed.
4. **Offline Conversion Lags**: For enterprise sales cycles exceeding 90 days, recent monthly cohorts may appear lower before full deal closure reconciles.

---

### License & Attribution
Developed for Enterprise Marketing Analytics, ROI Optimization, and Applied Machine Learning.
© MARKETIQ AI — *Turn Marketing Spend into Measurable Growth.*
