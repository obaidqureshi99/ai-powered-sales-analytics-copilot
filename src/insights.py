
from sqlalchemy import text
from src.database import get_engine


QUERIES = {
    "overall": """
        SELECT
            COALESCE(SUM(sales), 0) AS total_sales,
            COALESCE(SUM(profit), 0) AS total_profit,
            COALESCE(SUM(quantity), 0) AS total_quantity,
            COUNT(DISTINCT order_id) AS total_orders,
            COUNT(DISTINCT customer_id) AS total_customers
        FROM superstore;
    """,

    "category": """
        SELECT
            category,
            SUM(sales) AS total_sales,
            SUM(profit) AS total_profit
        FROM superstore
        GROUP BY category
        ORDER BY total_sales DESC;
    """,

    "region": """
        SELECT
            region,
            SUM(sales) AS total_sales,
            SUM(profit) AS total_profit
        FROM superstore
        GROUP BY region
        ORDER BY total_sales DESC;
    """,

    "monthly": """
        SELECT
            TO_CHAR(DATE_TRUNC('month', order_date), 'YYYY-MM') AS month,
            SUM(sales) AS total_sales,
            SUM(profit) AS total_profit
        FROM superstore
        GROUP BY DATE_TRUNC('month', order_date)
        ORDER BY DATE_TRUNC('month', order_date) DESC
        LIMIT 12;
    """,

    "top_products": """
        SELECT
            product_name,
            SUM(sales) AS total_sales,
            SUM(profit) AS total_profit
        FROM superstore
        GROUP BY product_name
        ORDER BY total_sales DESC
        LIMIT 10;
    """,

    "loss_products": """
        SELECT
            product_name,
            SUM(sales) AS total_sales,
            SUM(profit) AS total_profit
        FROM superstore
        GROUP BY product_name
        HAVING SUM(profit) < 0
        ORDER BY total_profit ASC
        LIMIT 10;
    """
}


def get_business_metrics():

    engine = get_engine()
    results = {}

    with engine.connect() as connection:

        for name, query in QUERIES.items():

            rows = connection.execute(
                text(query)
            ).mappings().all()

            results[name] = [
                dict(row) for row in rows
            ]

    return results
