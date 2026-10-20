import pandas as pd
import pytest

from src import config
from src.series import CATEGORIES, SERIES, load_monthly_sales, split_holdout

MONTHS = pd.date_range("2020-01-01", periods=4, freq="MS")
CATEGORY_SALES = {"Furniture": 10.0, "Office Supplies": 20.0, "Technology": 30.0}


@pytest.fixture
def prepared_csvs(monkeypatch, tmp_path):
    total = pd.DataFrame({"month_start": MONTHS, "total_sales": 60.0})
    by_category = pd.DataFrame(
        [
            {"month_start": month, "category": category, "total_sales": value}
            for month in MONTHS
            for category, value in CATEGORY_SALES.items()
        ]
    )
    total_path = tmp_path / "total.csv"
    by_category_path = tmp_path / "by_category.csv"
    total.to_csv(total_path, index=False)
    by_category.to_csv(by_category_path, index=False)
    monkeypatch.setattr(config, "MONTHLY_SALES_CSV", total_path)
    monkeypatch.setattr(config, "MONTHLY_SALES_BY_CATEGORY_CSV", by_category_path)


def test_load_monthly_sales_is_wide_with_monthly_index(prepared_csvs):
    sales = load_monthly_sales()
    assert list(sales.columns) == SERIES
    assert list(sales.index) == list(MONTHS)
    assert sales.index.freqstr == "MS"
    assert sales.loc[MONTHS[0]].to_dict() == {"Total": 60.0, **CATEGORY_SALES}


def test_split_holdout_takes_the_last_months(prepared_csvs):
    sales = load_monthly_sales()
    train, holdout = split_holdout(sales, holdout_months=1)
    assert list(train.index) == list(MONTHS[:3])
    assert list(holdout.index) == list(MONTHS[3:])


@pytest.mark.integration
def test_real_series_total_equals_sum_of_categories():
    sales = load_monthly_sales()
    assert not sales.isna().any().any()
    assert sales[CATEGORIES].sum(axis=1).values == pytest.approx(sales["Total"].values)


@pytest.mark.integration
def test_real_series_default_holdout_is_last_12_months():
    train, holdout = split_holdout(load_monthly_sales())
    assert len(holdout) == 12
    assert len(train) == 36
    assert train.index.max() < holdout.index.min()
