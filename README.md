# Global Bank Branch Performance & Loan Portfolio Health Dashboard

**Institution:** Solenne International Bank (fictional multinational bank)  
**Domain:** BFSI (Banking, Financial Services & Insurance)  
**Tools:** Python, PostgreSQL, Power BI, Excel, Pandas, NumPy, Seaborn

---

## Project Overview

A complete end-to-end analyst workflow simulating the kind of work a data analyst 
does at a retail bank — from raw data triage to an executive Power BI dashboard. 
The business problem: a regional manager has no unified view of which branches are 
underperforming, which loan segments are at risk, and where deposit growth is 
declining. All data lived in separate exports with no single source of truth.

This project builds that source of truth — a 4-page interactive dashboard backed 
by a PostgreSQL analytical layer, covering 18 global branches across 6 regions.

---

## Dataset

Synthetic data generated using Python (Faker + NumPy) to simulate a realistic 
multinational retail bank. No real customer or financial data used.

| Table | Rows | Description |
|---|---|---|
| branches | 18 | 18 branches across 6 global regions |
| customers | 50,000 | Retail, SME, and Corporate segments |
| loans | 130,000 | 7 loan types, 2.5 years of disbursements |
| transactions | 1,500,000 | Deposits and withdrawals, Jan 2022 – Jun 2024 |

**Regions covered:** North America · Europe · APAC · Middle East · 
Latin America · Africa  
**Currency:** USD  
**Time period:** January 2022 – June 2024

---

## Workflow

### Step 1 — Excel Triage
Manual data quality audit across all 4 CSVs before any code was written.
- Pivot tables on loans (NPL rate by branch) and customers (segment distribution)
- Documented finding: transactions.csv exceeds Excel's 1,048,576-row limit —
  flagged for Python-based inspection
- Deliverable: `docs/data_quality_notes.md`

### Step 2 — Python EDA
Systematic exploration using Pandas and Seaborn. Every chart answers a specific 
business question.
- Missing value check across all 4 tables (zero missing values confirmed)
- NPL rate by branch bar chart — confirmed performance tier logic working correctly
- Loan amount distribution on log scale — revealed bimodal pattern 
  (retail/SME cluster + corporate cluster)
- Outlier detection on overdue_days — identified zero-inflation bias in full 
population IQR; corrected by isolating 25,515 genuinely overdue loans. 
  Corrected bounds: Q1=35 days, Q3=173 days, upper bound=380 days, 
  1,120 loans (4.39%) flagged as statistical outliers
- Monthly deposit trend — confirmed seasonal peaks in Nov/Dec and April
- Deliverable: `notebooks/eda_notebook.ipynb`

### Step 3 — SQL Transformation Layer (PostgreSQL)
6 analytical views built in PostgreSQL — the single source of truth that 
Power BI connects to.

| View | Business Question | Key SQL Feature |
|---|---|---|
| `vw_branch_npl_rate` | Which branches have the worst loan quality? | Conditional aggregation, NULLIF |
| `vw_mom_deposit_growth` | Is deposit growth accelerating per branch? | CTE + LAG() window function |
| `vw_customer_risk_tiers` | Which customers carry the most risk? | MAX() + CASE WHEN bucketing |
| `vw_officer_performance` | Which loan officers originate risky loans? | Same NPL logic at officer level |
| `vw_loan_disbursement_trend` | Is loan growth accelerating by region? | DATE_TRUNC + GROUP BY region |
| `vw_overdue_aging_buckets` | How severe is the bad debt? | SUM() OVER() window in aggregate |

Deliverable: `data/sql/analysis.sql`

### Step 4 — Power BI Dashboard (4 pages)

**Page 1 — Executive Overview**
- KPI cards: 130K total loans · 9.71% NPL rate · $328.88bn total exposure
- Bar chart: NPL rate by branch (sorted highest to lowest, average reference line)
- Line chart: Monthly disbursement trend by region (6 regional lines)

**Page 2 — Loan Portfolio Health**
- Donut: Customer risk distribution (65.3% Low · 23.6% Medium · 11.2% High)
- Bar chart: Loan exposure by aging bucket ($266bn current vs $32bn 90+ days NPL)
- Table: Branch NPL league table (18 branches, sortable by NPL rate)

**Page 3 — Branch Deep-Dive**
- Region slicer: Interactive filter — click a region, all visuals update
- Line chart: Monthly deposits by branch (30-month trend, 18 lines)
- Scatter plot: Officer performance (loans issued vs NPL rate, 9.71% reference line)
- KPI card: Average loan size (updates dynamically with slicer selection)

**Page 4 — Customer Risk**
- Table: High-risk customers filtered by risk tier, sorted by total exposure
- Bar chart: Loan exposure by customer segment and risk tier
- Donut: Loan count by segment (70.1% Retail · 21.8% SME · 8.0% Corporate)

---

## Key Findings

1. **NPL rate ranges from 5.95% (Manhattan) to 18.52% (Madrid)** — a 3x spread 
   driven entirely by branch performance tier assignment
2. **$32bn sits in the 90+ days NPL bucket** vs $266bn current — 
   majority of the portfolio is performing but the tail risk is significant
3. **11.15% of customers (5,170) are High Risk** — concentrated in Corporate 
   segment which carries disproportionate exposure relative to loan count
4. **Seasonal deposit peaks confirmed** in Nov/Dec and April across all branches
5. **Outlier detection corrected for zero-inflation** — standard IQR on full 
   population was invalid; isolated overdue population gave meaningful 4.39% 
   outlier rate

---

## Repository Structure
```

bank-dashboard/

├── data/

│   ├── raw/               # Generated CSVs (not pushed — see .gitignore)

│   └── sql/

│       └── analysis.sql   # All 6 PostgreSQL views

├── docs/

│   ├── data_quality_notes.md

│   └── dashboard_export.pdf

├── notebooks/

│   └── eda_notebook.ipynb

├── powerbi/

│   └── bank_dashboard.pbix

├── scripts/

│   ├── generate_data.py

│   └── load_to_postgres.py

├── .gitignore

├── README.md

└── requirements.txt

```
---

## How to Run This Project

**1. Generate the data**
```bash
python scripts/generate_data.py
```

**2. Load into PostgreSQL**
- Create a database called `bank_dashboard` in PostgreSQL
- Run `data/sql/analysis.sql` to create the schema and views
- Update credentials in `load_to_postgres.py` and run:
```bash
python scripts/load_to_postgres.py
```

**3. Open the dashboard**
- Open `powerbi/bank_dashboard.pbix` in Power BI Desktop
- Refresh the data connection (Home → Refresh)

---
*Fictional dataset. No real bank data used.*
