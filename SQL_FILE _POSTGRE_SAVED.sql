SELECT *
FROM superstore
LIMIT 10;

SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE sales IS NULL) AS missing_sales,
    COUNT(*) FILTER (WHERE profit IS NULL) AS missing_profit
FROM superstore;
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'superstore'
ORDER BY ordinal_position;