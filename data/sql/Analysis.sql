-- Business Question: Which branches have the highest proportion of bad loans?
-- Logic: Conditional aggregation (CASE inside SUM) counts NPA loans without
-- needing a separate filtered query — one pass over the data.

SELECT 
    b.branch_name,
    b.region,
    b.performance_tier,
    COUNT(l.loan_id) AS total_loans,
    SUM(CASE WHEN l.status = 'NPA' THEN 1 ELSE 0 END) AS npa_count,
    ROUND(
        SUM(CASE WHEN l.status = 'NPA' THEN 1 ELSE 0 END) * 100.0 
        / COUNT(l.loan_id), 2
    ) AS npa_rate_pct
FROM branches b
JOIN loans l ON b.branch_id = l.branch_id
GROUP BY b.branch_name, b.region, b.performance_tier
ORDER BY npa_rate_pct DESC;