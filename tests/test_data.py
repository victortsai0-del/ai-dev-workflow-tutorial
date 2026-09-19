"""Tests for data.py."""

import pandas as pd
import pytest

from data import (
    DataLoadError,
    load_data,
    monthly_trend,
    sales_by_category,
    sales_by_region,
    total_orders,
    total_sales,
)


def sample_df():
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-15", "2024-01-20", "2024-02-10", "2024-02-15"]
            ),
            "order_id": ["ORD-1", "ORD-2", "ORD-3", "ORD-4"],
            "product": ["Widget", "Gadget", "Widget", "Gizmo"],
            "category": ["Electronics", "Accessories", "Electronics", "Accessories"],
            "region": ["North", "South", "North", "West"],
            "quantity": [1, 2, 1, 3],
            "unit_price": [100.00, 25.00, 200.00, 10.00],
            "total_amount": [100.00, 50.00, 200.00, 30.00],
        }
    )


def test_load_data_missing_file():
    with pytest.raises(DataLoadError, match="not found"):
        load_data("data/does-not-exist.csv")


def test_load_data_missing_column(tmp_path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text(
        "date,order_id,product,category,region,quantity,unit_price\n"
        "2024-01-01,ORD-1,Widget,Electronics,North,1,9.99\n"
    )

    with pytest.raises(DataLoadError, match="total_amount"):
        load_data(str(csv_path))


def test_load_data_happy_path(tmp_path):
    csv_path = tmp_path / "good.csv"
    csv_path.write_text(
        "date,order_id,product,category,region,quantity,unit_price,total_amount\n"
        "2024-01-01,ORD-1,Widget,Electronics,North,1,9.99,9.99\n"
    )

    df = load_data(str(csv_path))

    assert len(df) == 1
    assert list(df.columns) == [
        "date",
        "order_id",
        "product",
        "category",
        "region",
        "quantity",
        "unit_price",
        "total_amount",
    ]
    assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_total_sales():
    assert total_sales(sample_df()) == pytest.approx(380.00)


def test_total_orders():
    assert total_orders(sample_df()) == 4


def test_monthly_trend():
    result = monthly_trend(sample_df())

    assert list(result.index) == [
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-02-01"),
    ]
    assert result.tolist() == pytest.approx([150.00, 230.00])


def test_sales_by_category():
    result = sales_by_category(sample_df())

    assert list(result.index) == ["Electronics", "Accessories"]
    assert result.tolist() == pytest.approx([300.00, 80.00])


def test_sales_by_region():
    result = sales_by_region(sample_df())

    assert list(result.index) == ["North", "South", "West"]
    assert result.tolist() == pytest.approx([300.00, 50.00, 30.00])
