import pandas as pd

from src.cleaning import standardize_columns, clean_sales_data


def test_standardize_columns():

    df = pd.DataFrame({
        "Order Date": ["2024-01-01"],
        "Customer Name": ["John"]
    })

    result = standardize_columns(df)

    assert "order_date" in result.columns
    assert "customer_name" in result.columns


def test_remove_duplicates():

    df = pd.DataFrame({
        "Sales": [100, 200, 100],
        "Profit": [20, 40, 20]
    })

    result = clean_sales_data(df)

    assert len(result) == 2


def test_sales_are_numeric():

    df = pd.DataFrame({
        "Sales": ["100", "200"],
        "Profit": ["20", "40"]
    })

    result = clean_sales_data(df)

    assert pd.api.types.is_numeric_dtype(result["sales"])