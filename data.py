"""Data loading and calculations for the ShopSmart sales dashboard."""

import pandas as pd

REQUIRED_COLUMNS = [
    "date",
    "order_id",
    "product",
    "category",
    "region",
    "quantity",
    "unit_price",
    "total_amount",
]


class DataLoadError(Exception):
    """Raised when the sales data file can't be loaded or is malformed."""


def load_data(path):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise DataLoadError(f"Data file not found at {path}") from None

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise DataLoadError(f"Missing required column(s): {', '.join(missing)}")

    df["date"] = pd.to_datetime(df["date"])
    return df
