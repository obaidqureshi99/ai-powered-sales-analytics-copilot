

from pathlib import Path

import pandas as pd

from database import get_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "reports" / "sql"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

QUERIES = {
    "category_performance": """
        SELECT
            category,
            ROUND(SUM(sales)::numeric, 2) AS total_sales,
            ROUND(SUM(profit)::numeric, 2) AS total_profit
        FROM superstore
        GROUP BY category
        ORDER BY total_sales DESC
    """,
    "regional_performance": """
        SELECT
            region,
            ROUND(SUM(sales)::numeric, 2) AS total_sales,
            ROUND(SUM(profit)::numeric, 2) AS total_profit
        FROM superstore
        GROUP BY region
        ORDER BY total_sales DESC
    """,
    "monthly_performance": """
        SELECT
            DATE_TRUNC('month', order_date)::date AS sales_month,
            ROUND(SUM(sales)::numeric, 2) AS total_sales,
            ROUND(SUM(profit)::numeric, 2) AS total_profit
        FROM superstore
        WHERE order_date IS NOT NULL
        GROUP BY DATE_TRUNC('month', order_date)
        ORDER BY sales_month
    """,
}

engine = get_engine()

try:
    for report_name, query in QUERIES.items():
        result = pd.read_sql_query(query, engine)
        output_path = OUTPUT_DIR / f"{report_name}.csv"
        result.to_csv(output_path, index=False)

        print(f"Saved {output_path}")
        print(result.head(), "\n")
finally:
    engine.dispose()
