
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from database import get_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = PROJECT_ROOT / "data" / "raw" / "Superstore.csv"

df = pd.read_csv(CSV_PATH, encoding="cp1252")
df.columns = (
    df.columns.str.strip()
    .str.lower()
    .str.replace(r"[^a-z0-9]+", "_", regex=True)
    .str.strip("_")
)

df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
df["profit"] = pd.to_numeric(df["profit"], errors="coerce")

pandas_sales = df["sales"].sum()
pandas_profit = df["profit"].sum()

engine = get_engine()

try:
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    SUM(sales) AS total_sales,
                    SUM(profit) AS total_profit
                FROM superstore
            """)
        ).mappings().one()

    sql_sales = float(result["total_sales"] or 0)
    sql_profit = float(result["total_profit"] or 0)

    print(f"Pandas total sales:  {pandas_sales:.2f}")
    print(f"SQL total sales:     {sql_sales:.2f}")
    print(f"Pandas total profit: {pandas_profit:.2f}")
    print(f"SQL total profit:    {sql_profit:.2f}")

    assert abs(pandas_sales - sql_sales) < 0.01, (
        "Sales totals do not match."
    )
    assert abs(pandas_profit - sql_profit) < 0.01, (
        "Profit totals do not match."
    )

    print("Validation passed: SQL matches Pandas.")

finally:
    engine.dispose()
