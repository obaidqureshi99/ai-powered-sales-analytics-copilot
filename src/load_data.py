
import re
from pathlib import Path
import pandas as pd
from sqlalchemy import text
from database import get_engine
PROJECT_ROOT = Path(__file__).resolve().parents[1]

CSV_PATH = PROJECT_ROOT / "data" / "raw" / "Superstore.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

TABLE_NAME = "superstore"


def standardize_columns(columns):
    """Convert column names to lowercase snake_case."""

    standardized = []

    for column in columns:
        column = column.strip().lower()
        column = re.sub(r"[^a-z0-9]+", "_", column)
        column = column.strip("_")
        standardized.append(column)

    return standardized


def load_superstore():
    """Load and validate the CSV before writing it to PostgreSQL."""

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {CSV_PATH}"
        )
    df = pd.read_csv(CSV_PATH, encoding="cp1252")
    df.columns = standardize_columns(df.columns)

    # Convert date fields when present.
    for column in ["order_date", "ship_date"]:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column], errors="coerce"
            )

    # Convert numeric fields when present.
    numeric_columns = [
        "sales",
        "profit",
        "quantity",
        "discount",
        "shipping_cost",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column], errors="coerce"
            )

    if df.empty:
        raise ValueError("The dataset contains no rows.")

    if df.columns.duplicated().any():
        raise ValueError("Duplicate column names after standardization.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    engine = get_engine()

    try:
        # Replace the table during this development project only.
        df.to_sql(
            TABLE_NAME,
            engine,
            if_exists="replace",
            index=False,
            chunksize=1000,
            method="multi",
        )

        with engine.connect() as connection:
            database_count = connection.execute(
                text("SELECT COUNT(*) FROM superstore")
            ).scalar_one()

        # Save a local copy of the transformed data.
        processed_path = (
            OUTPUT_DIR / "superstore_processed.csv"
        )
        df.to_csv(processed_path, index=False)

        print(f"CSV rows loaded: {len(df):,}")
        print(f"PostgreSQL rows: {database_count:,}")
        print(f"Columns: {len(df.columns)}")
        print(f"Processed file: {processed_path}")

        if len(df) != database_count:
            raise RuntimeError("CSV and database row counts differ.")

        print("Data load and row-count validation successful.")

    finally:
        engine.dispose()


if __name__ == "__main__":
    load_superstore()
