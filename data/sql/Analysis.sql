-- ============================================================
-- VIEW: vw_branch_npl_rate
-- Business Question: Which branches have the worst loan quality,
-- and where should the risk team focus collection efforts first?
-- ============================================================

CREATE OR REPLACE VIEW vw_branch_npl_rate AS
SELECT
    b.branch_id,
    b.branch_name,
    b.region,
    b.performance_tier,
    b.branch_size,
    COUNT(l.loan_id)                                               AS total_loans,
    SUM(CASE WHEN l.status = 'NPL' THEN 1 ELSE 0 END)             AS npl_count,
    ROUND(
        SUM(CASE WHEN l.status = 'NPL' THEN 1 ELSE 0 END) * 100.0
        / NULLIF(COUNT(l.loan_id), 0),
    2)                                                             AS npl_rate_pct,
    SUM(l.loan_amount)                                             AS total_exposure_usd,
    ROUND(AVG(l.loan_amount), 0)                                   AS avg_loan_amount_usd
FROM branches b
JOIN loans l ON b.branch_id = l.branch_id
GROUP BY
    b.branch_id,
    b.branch_name,
    b.region,
    b.performance_tier,
    b.branch_size
ORDER BY npl_rate_pct DESC;

-- ============================================================
-- VIEW: vw_mom_deposit_growth
-- Business Question: Is each branch's deposit base growing or
-- shrinking month to month? Which branches are losing depositors?
-- ============================================================

CREATE OR REPLACE VIEW vw_mom_deposit_growth AS
WITH monthly_deposits AS (
    SELECT
        t.branch_id,
        DATE_TRUNC('month', t.txn_date)  AS month,
        SUM(t.amount)                     AS total_deposits
    FROM transactions t
    WHERE t.txn_type = 'deposit'
    GROUP BY t.branch_id, DATE_TRUNC('month', t.txn_date)
)
SELECT
    md.branch_id,
    b.branch_name,
    b.region,
    md.month,
    md.total_deposits,
    LAG(md.total_deposits) OVER (
        PARTITION BY md.branch_id
        ORDER BY md.month
    )                                                              AS prev_month_deposits,
    ROUND(
        (md.total_deposits - LAG(md.total_deposits) OVER (
            PARTITION BY md.branch_id ORDER BY md.month
        )) * 100.0
        / NULLIF(LAG(md.total_deposits) OVER (
            PARTITION BY md.branch_id ORDER BY md.month
        ), 0),
    2)                                                             AS mom_growth_pct
FROM monthly_deposits md
JOIN branches b ON md.branch_id = b.branch_id
ORDER BY md.branch_id, md.month;

-- ============================================================
-- VIEW: vw_customer_risk_tiers
-- Business Question: Which customers carry the most financial
-- risk? How should the collections team prioritize outreach?
-- ============================================================

CREATE OR REPLACE VIEW vw_customer_risk_tiers AS
SELECT
    c.customer_id,
    c.customer_name,
    c.segment,
    c.branch_id,
    b.branch_name,
    b.region,
    COUNT(l.loan_id)                AS loan_count,
    SUM(l.loan_amount)              AS total_exposure_usd,
    MAX(l.overdue_days)             AS max_overdue_days,
    CASE
        WHEN MAX(l.overdue_days) > 90            THEN 'High Risk'
        WHEN MAX(l.overdue_days) BETWEEN 31 AND 90 THEN 'Medium Risk'
        ELSE                                          'Low Risk'
    END                             AS risk_tier
FROM customers c
JOIN loans l ON c.customer_id = l.customer_id
JOIN branches b ON c.branch_id = b.branch_id
GROUP BY
    c.customer_id,
    c.customer_name,
    c.segment,
    c.branch_id,
    b.branch_name,
    b.region
ORDER BY total_exposure_usd DESC;

-- ============================================================
-- VIEW: vw_officer_performance
-- Business Question: Which loan officers are originating
-- high-risk loans? Is poor loan quality a branch problem
-- or an individual underwriting problem?
-- ============================================================

CREATE OR REPLACE VIEW vw_officer_performance AS
SELECT
    l.officer_id,
    b.branch_name,
    b.region,
    b.performance_tier,
    COUNT(l.loan_id)                                               AS loans_issued,
    SUM(l.loan_amount)                                             AS total_disbursed_usd,
    ROUND(AVG(l.loan_amount), 0)                                   AS avg_loan_size_usd,
    SUM(CASE WHEN l.status = 'NPL' THEN 1 ELSE 0 END)              AS npl_count,
    ROUND(
        SUM(CASE WHEN l.status = 'NPL' THEN 1 ELSE 0 END) * 100.0
        / NULLIF(COUNT(l.loan_id), 0),
    2)                                                             AS officer_npl_rate_pct
FROM loans l
JOIN branches b ON l.branch_id = b.branch_id
GROUP BY
    l.officer_id,
    b.branch_name,
    b.region,
    b.performance_tier
ORDER BY officer_npl_rate_pct DESC;

-- ============================================================
-- VIEW: vw_loan_disbursement_trend
-- Business Question: Is total loan growth accelerating or
-- decelerating? Which regions are driving disbursement growth?
-- ============================================================

CREATE OR REPLACE VIEW vw_loan_disbursement_trend AS
SELECT
    DATE_TRUNC('month', l.disburse_date)   AS month,
    b.region,
    COUNT(l.loan_id)                        AS loans_disbursed,
    SUM(l.loan_amount)                      AS total_disbursed_usd,
    ROUND(AVG(l.loan_amount), 0)            AS avg_loan_size_usd
FROM loans l
JOIN branches b ON l.branch_id = b.branch_id
GROUP BY
    DATE_TRUNC('month', l.disburse_date),
    b.region
ORDER BY month, region;

-- ============================================================
-- VIEW: vw_overdue_aging_buckets
-- Business Question: Of all the bad debt on the books,
-- how severe is it — mild lateness or near write-off?
-- ============================================================

CREATE OR REPLACE VIEW vw_overdue_aging_buckets AS
SELECT
    CASE
        WHEN l.overdue_days = 0                THEN '1 - Current'
        WHEN l.overdue_days BETWEEN 1  AND 30  THEN '2 - 1-30 Days'
        WHEN l.overdue_days BETWEEN 31 AND 60  THEN '3 - 31-60 Days'
        WHEN l.overdue_days BETWEEN 61 AND 90  THEN '4 - 61-90 Days'
        ELSE                                        '5 - 90+ Days (NPL)'
    END                          AS aging_bucket,
    COUNT(l.loan_id)             AS loan_count,
    SUM(l.loan_amount)           AS total_exposure_usd,
    ROUND(
        SUM(l.loan_amount) * 100.0
        / NULLIF(SUM(SUM(l.loan_amount)) OVER (), 0),
    2)                           AS pct_of_total_exposure
FROM loans l
GROUP BY
    CASE
        WHEN l.overdue_days = 0                THEN '1 - Current'
        WHEN l.overdue_days BETWEEN 1  AND 30  THEN '2 - 1-30 Days'
        WHEN l.overdue_days BETWEEN 31 AND 60  THEN '3 - 31-60 Days'
        WHEN l.overdue_days BETWEEN 61 AND 90  THEN '4 - 61-90 Days'
        ELSE                                        '5 - 90+ Days (NPL)'
    END
ORDER BY aging_bucket;


--- Sanity Check
SELECT * FROM vw_branch_npl_rate LIMIT 5;
SELECT * FROM vw_mom_deposit_growth LIMIT 5;
SELECT * FROM vw_customer_risk_tiers LIMIT 5;
SELECT * FROM vw_officer_performance LIMIT 5;
SELECT * FROM vw_loan_disbursement_trend LIMIT 5;
SELECT * FROM vw_overdue_aging_buckets;

