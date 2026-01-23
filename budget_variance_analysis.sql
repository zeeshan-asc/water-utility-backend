-- Budget Variance Analysis for Infrastructure Department in 2024
-- This query analyzes budget performance for the Infrastructure department

-- Main Analysis Query
SELECT 
    date,
    department,
    budget,
    actual,
    variance,
    variance_pct,
    CASE 
        WHEN variance_pct > 0.10 THEN 'Over Budget'
        WHEN variance_pct < -0.10 THEN 'Under Budget'
        ELSE 'On Budget'
    END as status
FROM departments
WHERE department = 'Infrastructure'
    AND date LIKE '2024%'
ORDER BY date DESC;

-- Summary Statistics
SELECT 
    department,
    COUNT(*) as total_records,
    SUM(budget) as total_budget,
    SUM(actual) as total_actual,
    SUM(variance) as total_variance,
    AVG(variance_pct) as avg_variance_pct,
    MAX(variance_pct) as max_variance_pct,
    MIN(variance_pct) as min_variance_pct,
    COUNT(CASE WHEN variance_pct > 0.10 THEN 1 END) as over_budget_count,
    COUNT(CASE WHEN variance_pct < -0.10 THEN 1 END) as under_budget_count,
    COUNT(CASE WHEN variance_pct BETWEEN -0.10 AND 0.10 THEN 1 END) as on_budget_count
FROM departments
WHERE department = 'Infrastructure'
    AND date LIKE '2024%'
GROUP BY department;

-- Monthly Trend Analysis
SELECT 
    SUBSTR(date, 1, 7) as month,
    SUM(budget) as monthly_budget,
    SUM(actual) as monthly_actual,
    SUM(variance) as monthly_variance,
    AVG(variance_pct) as avg_variance_pct
FROM departments
WHERE department = 'Infrastructure'
    AND date LIKE '2024%'
GROUP BY SUBSTR(date, 1, 7)
ORDER BY month;

