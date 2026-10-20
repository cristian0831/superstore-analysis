import pandas as pd
import pytest

from scripts.phase2_data_preparation.run_phase import QUERIES_DIR
from src.db_utils import run_query

EXPECTED_TABLES = {
    "customers",
    "order_items",
    "products",
    "orders_raw",
    "orders_clean",
    "geography",
}
EXPECTED_CATEGORIES = {"Furniture", "Office Supplies", "Technology"}
EXPECTED_MONTHS = 48


@pytest.mark.integration
def test_real_db_expected_tables_exist():
    df = run_query("SELECT name FROM sqlite_master WHERE type='table'")
    assert EXPECTED_TABLES <= set(df["name"])


@pytest.mark.integration
def test_real_db_customers_has_rows():
    df = run_query("SELECT COUNT(*) AS n FROM customers")
    assert df.loc[0, "n"] > 0


def _assert_48_consecutive_months(month_start):
    months = pd.to_datetime(month_start)
    expected = pd.date_range(start=months.iloc[0], periods=EXPECTED_MONTHS, freq="MS")
    assert list(months) == list(expected)


@pytest.mark.integration
def test_real_db_monthly_sales_is_48_months_with_no_gaps():
    df = run_query(QUERIES_DIR / "01_monthly_sales.sql")
    _assert_48_consecutive_months(df["month_start"])


@pytest.mark.integration
def test_real_db_monthly_sales_by_category_is_48_months_with_no_gaps():
    df = run_query(QUERIES_DIR / "02_monthly_sales_by_category.sql")
    assert set(df["category"]) == EXPECTED_CATEGORIES
    # A month where one category sold nothing would be a missing row, not a zero.
    for _, series in df.groupby("category"):
        _assert_48_consecutive_months(series["month_start"])
