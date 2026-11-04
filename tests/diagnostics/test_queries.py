import pandas as pd
import pytest

from src.config import SQL_DIR
from src.db_utils import run_query

# Runs against the real db/superstore.db (built by `python -m src.etl`) -- same convention as
# test_db_utils_real_db.py. These check internal consistency (does the SQL
# reconcile against order_items, is every value from a known set), not exact
# business numbers -- that would break on any legitimate data refresh even
# when the query logic is still correct.
pytestmark = pytest.mark.integration

QUERIES_DIR = SQL_DIR / "diagnostics"
TOLERANCE = 0.01

ALLOWED_CATEGORIES = {"Furniture", "Office Supplies", "Technology"}
ALLOWED_SEGMENTS = {"Consumer", "Corporate", "Home Office"}
ALLOWED_REGIONS = {"West", "East", "Central", "South"}
ALLOWED_DISCOUNT_BANDS = {"0%", "1-10%", "11-20%", "21-30%", "31-40%", "41-49%", "50%+"}


def _load(filename):
    """Run the actual file src.sql_runner executes, not a re-typed copy of it."""
    return run_query(QUERIES_DIR / filename)


def _order_items_total(column):
    return run_query(f"SELECT SUM({column}) AS total FROM order_items").loc[0, "total"]


def test_01_growth_trends_reconciles_and_is_ordered():
    df = _load("01_growth_trends.sql")

    expected_years = run_query(
        "SELECT COUNT(DISTINCT order_year) AS n FROM order_items"
    ).loc[0, "n"]
    assert len(df) == expected_years
    assert df["order_year"].is_monotonic_increasing

    assert df["total_sales"].sum() == pytest.approx(_order_items_total("sales"), abs=TOLERANCE)
    assert df["total_profit"].sum() == pytest.approx(_order_items_total("profit"), abs=TOLERANCE)

    # The first year has no prior year to diff against.
    assert pd.isna(df.loc[0, "sales_growth_pct"])
    assert df.loc[1:, "sales_growth_pct"].notna().all()


def test_02_growth_by_category_reconciles():
    df = _load("02_growth_by_category.sql")

    assert set(df["category"]) == ALLOWED_CATEGORIES
    assert not df.duplicated(subset=["order_year", "category"]).any()

    assert df["total_sales"].sum() == pytest.approx(_order_items_total("sales"), abs=TOLERANCE)
    assert df["total_profit"].sum() == pytest.approx(_order_items_total("profit"), abs=TOLERANCE)


def test_03_customer_segment_profitability_reconciles_and_margin_is_correct():
    df = _load("03_customer_segment_profitability.sql")

    assert set(df["segment"]) == ALLOWED_SEGMENTS
    assert len(df) == len(ALLOWED_SEGMENTS)

    assert df["total_sales"].sum() == pytest.approx(_order_items_total("sales"), abs=TOLERANCE)
    assert df["total_profit"].sum() == pytest.approx(_order_items_total("profit"), abs=TOLERANCE)

    recomputed = df["total_profit"] / df["total_sales"]
    assert (recomputed - df["segment_margin"]).abs().max() <= TOLERANCE


def test_04_discount_impact_reconciles():
    df = _load("04_discount_impact.sql")

    assert set(df["category"]) <= ALLOWED_CATEGORIES
    assert set(df["discount_band"]) <= ALLOWED_DISCOUNT_BANDS

    # Bands are meant to be mutually exclusive and exhaustive across the full
    # category x band grid -- nothing should be double-counted or dropped.
    assert df["total_sales"].sum() == pytest.approx(_order_items_total("sales"), abs=TOLERANCE)
    assert df["total_profit"].sum() == pytest.approx(_order_items_total("profit"), abs=TOLERANCE)


def test_05_regional_profitability_reconciles_and_margin_is_correct():
    df = _load("05_regional_profitability.sql")

    assert set(df["region"]) <= ALLOWED_REGIONS

    assert df["total_sales"].sum() == pytest.approx(_order_items_total("sales"), abs=TOLERANCE)
    assert df["total_profit"].sum() == pytest.approx(_order_items_total("profit"), abs=TOLERANCE)

    # Regression test for the arbitrary-profit_margin bug this query once had:
    # margin must be the blended SUM(profit)/SUM(sales) for every row.
    recomputed = df["total_profit"] / df["total_sales"]
    assert (recomputed - df["margin"]).abs().max() <= TOLERANCE
