import pandas as pd
import pytest

from src.baselines import naive_forecast, seasonal_naive_forecast
from src.metrics import mape, wape


def test_mape_averages_the_percentage_errors():
    # errors of 10% and 50% -> 30%
    assert mape([100, 10], [110, 15]) == pytest.approx(30.0)


def test_wape_weights_errors_by_actual_sales():
    # total error 10 + 5 = 15 over total actual 110
    assert wape([100, 10], [110, 15]) == pytest.approx(15 / 110 * 100)


def test_perfect_forecast_scores_zero():
    assert mape([5, 7], [5, 7]) == 0
    assert wape([5, 7], [5, 7]) == 0


@pytest.fixture
def two_years():
    index = pd.date_range("2020-01-01", periods=24, freq="MS")
    return pd.Series(range(24), index=index, dtype=float)


def test_naive_repeats_last_month(two_years):
    forecast = naive_forecast(two_years, horizon=3)
    assert forecast.tolist() == [23.0, 23.0, 23.0]
    assert list(forecast.index) == list(pd.date_range("2022-01-01", periods=3, freq="MS"))


def test_seasonal_naive_repeats_last_year(two_years):
    forecast = seasonal_naive_forecast(two_years, horizon=14)
    assert forecast.tolist() == [float(v) for v in [*range(12, 24), 12, 13]]
    assert forecast.index[0] == pd.Timestamp("2022-01-01")
