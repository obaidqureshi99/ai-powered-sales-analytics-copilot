
import pandas as pd

from src.validation import validate_sales_data


def test_valid_dataset():

    df = pd.DataFrame({
        "order_date": pd.to_datetime(["2024-01-01"]),
        "sales": [100],
        "profit": [20],
        "quantity": [2],
        "customer_id": ["C001"],
        "product_id": ["P001"]
    })

    result = validate_sales_data(df)

    assert result == []


def test_missing_required_column():

    df = pd.DataFrame({
        "sales": [100],
        "profit": [20]
    })

    result = validate_sales_data(df)

    assert any("Missing columns" in error for error in result)


def test_invalid_quantity():

    df = pd.DataFrame({
        "order_date": pd.to_datetime(["2024-01-01"]),
        "sales": [100],
        "profit": [20],
        "quantity": [0],
        "customer_id": ["C001"],
        "product_id": ["P001"]
    })

    result = validate_sales_data(df)

    assert any("Invalid quantity" in error for error in result)