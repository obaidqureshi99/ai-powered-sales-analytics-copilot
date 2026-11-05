
import re
import pandas as pd


def standardize_columns(df):
    """Standardize column names into lowercase snake_case."""

    df = df.copy()

    df.columns = [
        re.sub(
            r"_+",
            "_",
            re.sub(r"[^a-z0-9]+", "_", col.strip().lower())
        ).strip("_")
        for col in df.columns
    ]

    return df


def clean_sales_data(df):
    """Clean Superstore sales data."""

    df = standardize_columns(df)

    # Remove exact duplicate records.
    df = df.drop_duplicates().copy()

    # Convert date columns.
    for column in ["order_date", "ship_date"]:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    # Convert numeric columns.
    numeric_columns = [
        "sales",
        "profit",
        "quantity",
        "discount",
        "shipping_cost"
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # Remove rows with missing sales.
    if "sales" in df.columns:
        df = df.dropna(subset=["sales"])

    return df
