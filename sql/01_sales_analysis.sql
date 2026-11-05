
-- 1. Overall business KPIs
SELECT
    COUNT(*) AS transaction_lines,
    ROUND(SUM(sales)::numeric, 2) AS total_sales,
    ROUND(SUM(profit)::numeric, 2) AS total_profit,
    SUM(quantity) AS total_quantity,
    ROUND(
        100.0 * SUM(profit) / NULLIF(SUM(sales), 0),
        2
    ) AS profit_margin_pct
FROM superstore;


-- 2. Category performance
SELECT
    category,
    ROUND(SUM(sales)::numeric, 2) AS total_sales,
    ROUND(SUM(profit)::numeric, 2) AS total_profit,
    SUM(quantity) AS total_quantity,
    ROUND(
        100.0 * SUM(profit) / NULLIF(SUM(sales), 0),
        2
    ) AS profit_margin_pct
FROM superstore
GROUP BY category
ORDER BY total_sales DESC;


-- 3. Regional performance
SELECT
    region,
    ROUND(SUM(sales)::numeric, 2) AS total_sales,
    ROUND(SUM(profit)::numeric, 2) AS total_profit
FROM superstore
GROUP BY region
ORDER BY total_sales DESC;


-- 4. Monthly sales and profit trends
SELECT
    DATE_TRUNC('month', order_date)::date AS sales_month,
    ROUND(SUM(sales)::numeric, 2) AS total_sales,
    ROUND(SUM(profit)::numeric, 2) AS total_profit
FROM superstore
WHERE order_date IS NOT NULL
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY sales_month;


-- 5. Top 10 customers by sales
SELECT
    customer_id,
    customer_name,
    ROUND(SUM(sales)::numeric, 2) AS total_sales,
    ROUND(SUM(profit)::numeric, 2) AS total_profit
FROM superstore
GROUP BY customer_id, customer_name
ORDER BY total_sales DESC
LIMIT 10;


-- 6. Subcategories with negative profit
SELECT
    sub_category,
    ROUND(SUM(sales)::numeric, 2) AS total_sales,
    ROUND(SUM(profit)::numeric, 2) AS total_profit
FROM superstore
GROUP BY sub_category
HAVING SUM(profit) < 0
ORDER BY total_profit ASC;
