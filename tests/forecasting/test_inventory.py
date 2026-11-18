import numpy as np
import pandas as pd
import pytest

from src.forecasting.inventory import bottom_up_total, safety_stock, stock_target

MONTHS = pd.date_range("2018-01-01", periods=2, freq="MS")


def test_stock_target_at_50_percent_is_the_forecast():
    assert stock_target(100.0, 20.0, 0.5) == pytest.approx(100.0)


def test_stock_target_adds_safety_stock():
    # 90% one-sided normal quantile is 1.2816 standard errors above the mean
    assert stock_target(100.0, 20.0, 0.9) == pytest.approx(100.0 + 1.2816 * 20.0, abs=0.01)
    assert safety_stock(20.0, 0.9) == pytest.approx(stock_target(100.0, 20.0, 0.9) - 100.0)


def test_higher_service_level_needs_more_stock():
    assert stock_target(100.0, 20.0, 0.95) > stock_target(100.0, 20.0, 0.9)


@pytest.fixture
def two_categories():
    means = pd.DataFrame({"A": [10.0, 20.0], "B": [5.0, 5.0]}, index=MONTHS)
    ses = pd.DataFrame({"A": [3.0, 3.0], "B": [4.0, 4.0]}, index=MONTHS)
    return means, ses


def test_bottom_up_total_independent_errors_add_in_quadrature(two_categories):
    means, ses = two_categories
    mean, se = bottom_up_total(means, ses, pd.DataFrame(np.eye(2), index=["A", "B"], columns=["A", "B"]))
    assert mean.tolist() == [15.0, 25.0]
    assert se.tolist() == pytest.approx([5.0, 5.0])  # sqrt(3² + 4²)


def test_bottom_up_total_perfectly_correlated_errors_add_up(two_categories):
    means, ses = two_categories
    _, se = bottom_up_total(means, ses, pd.DataFrame(np.ones((2, 2)), index=["A", "B"], columns=["A", "B"]))
    assert se.tolist() == pytest.approx([7.0, 7.0])
