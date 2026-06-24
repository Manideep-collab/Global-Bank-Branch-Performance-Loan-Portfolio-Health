# Data Quality Notes — Solenne International Bank Project

Manual Excel triage performed on all 4 raw data tables before EDA/SQL work began.

## branches.csv
- **Row count:** 18
- **Findings:** 6 global regions represented (North America, Europe, APAC, Middle East, 
  Latin America, Africa). Branch size tiers (flagship/large/standard/small) correctly 
  scale `total_staff` — flagship branches average 150-300 staff, small branches 15-40.
- **Issues:** None

## customers.csv
- **Row count:** 50,000
- **Findings:** Segment split confirmed at ~70% Retail / 22% SME / 8% Corporate, matching 
  expected distribution. Customer volume per branch scales directly with branch_size tier:
  - Flagship branches: ~4,550-4,800 customers each
  - Large branches: ~2,700-2,900 customers each
  - Standard branches: ~1,850-1,930 customers each
  - Small branches: ~940-980 customers each
  This confirms the 5:3:2:1 weighting ratio applied during data generation.
- **Issues:** None

## loans.csv
- **Row count:** 130,000
- **Findings:** 
  - NPL Rate = 9.71% (industry-realistic for the "medium/low" tier mix modeled)
  - Loan volume by branch precisely mirrors the branch-size weighting seen in customers.csv:
    Flagship 47.1% | Large 28.3% | Standard 18.9% | Small 5.7%
  - All 5 loan statuses present with non-zero counts and exposure: Active (70.5%), 
    Closed (9.9%), NPL (9.7%), Overdue_30 (4.5%), Overdue_60 (5.4%)
- **Issues:** None

## transactions.csv
- **Row count:** 1,500,000
- **Findings:** Could not be fully loaded/pivoted in Excel.
- **Issues:** Exceeds Excel's 1,048,576-row worksheet limit (Excel attempted to load only 
  ~1.4M rows and warned of data loss on save — file was closed without saving to prevent 
  corruption of the source CSV). This file requires Python/Pandas for proper inspection 
  and EDA, which is the next phase of this workflow.

## Summary
All 4 tables pass triage. Synthetic data generation logic (branch tiering, customer 
weighting, NPL probability by performance tier) verified correct via manual pivot table 
cross-checks. No data cleaning required before EDA. transactions.csv flagged for 
Python-based analysis due to Excel's row-count ceiling.