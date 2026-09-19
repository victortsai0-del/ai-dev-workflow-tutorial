"""Tests for data.py."""

import pandas as pd
import pytest

from data import DataLoadError, load_data


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
