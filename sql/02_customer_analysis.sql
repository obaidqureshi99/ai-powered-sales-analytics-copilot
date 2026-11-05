
-- 1. Customer sales and profit summary
SELECT
    customer_id,
    customer_name,
    COUNT(*) AS transaction_lines,
    ROUND(SUM(sales)::numeric, 2) AS total_sales,
    ROUND(SUM(profit)::numeric, 2) AS total_profit,
    ROUND(AVG(discount)::numeric, 3) AS average_discount
FROM superstore
GROUP BY customer_id, customer_name
ORDER BY total_sales DESC;


-- 2. Customers with high sales but negative profit
SELECT
    customer_id,
    customer_name,
    ROUND(SUM(sales)::numeric, 2) AS total_sales,
    ROUND(SUM(profit)::numeric, 2) AS total_profit,
    ROUND(AVG(discount)::numeric, 3) AS average_discount
FROM superstore
GROUP BY customer_id, customer_name
HAVING SUM(sales) > 1000
   AND SUM(profit) < 0
ORDER BY total_sales DESC;


-- 3. Sales and profit by customer segment
SELECT
    segment,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(sales)::numeric, 2) AS total_sales,
    ROUND(SUM(profit)::numeric, 2) AS total_profit
FROM superstore
GROUP BY segment
ORDER BY total_sales DESC;
