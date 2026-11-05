import pandas as pd


REQUIRED_COLUMNS = [
    "order_date",
    "sales",
    "profit",
    "quantity",
    "customer_id",
    "product_id"
]


def validate_sales_data(df):
    """Validate the cleaned sales dataset."""

    errors = []

    # Check required columns
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        errors.append(f"Missing columns: {missing_columns}")
        return errors

    # Check empty dataset
    if df.empty:
        errors.append("Dataset is empty.")
        return errors

    # Check missing values
    for column in ["sales", "profit", "order_date"]:
        if df[column].isna().any():
            errors.append(f"Missing values found in {column}.")

    # Check invalid quantity
    if (df["quantity"] <= 0).any():
        errors.append("Invalid quantity values found.")

    # Check duplicate rows
    if df.duplicated().any():
        errors.append("Duplicate records found.")

    return errors