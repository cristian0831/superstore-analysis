import numpy as np
import pandas as pd
import pytest

from src.forecasting.sarima import (
    candidate_specs,
    choose_differencing,
    choose_seasonal_differencing,
    select_sarima,
    trend_options,
)

MONTHS = pd.date_range("2014-01-01", periods=48, freq="MS")
SEASONAL_SHAPE = np.array([2, 1, 5, 4, 4, 4, 4, 4, 9, 5, 10, 11], dtype=float)


def make_series(values):
    return pd.Series(values, index=MONTHS)


@pytest.fixture
def seasonal_series():
    rng = np.random.default_rng(0)
    return make_series(100 + 10 * np.tile(SEASONAL_SHAPE, 4) + rng.normal(0, 3, 48))


@pytest.fixture
def white_noise():
    return make_series(100 + np.random.default_rng(1).normal(0, 10, 48))


@pytest.fixture
def trending_series():
    # A steady climb: its mean clearly changes over time.
    return make_series(100 + 5 * np.arange(48) + np.random.default_rng(2).normal(0, 10, 48))


@pytest.mark.parametrize(
    "d, D, expected",
    [(0, 0, ["n", "c"]), (1, 0, ["n", "t"]), (0, 1, ["n", "t"]), (1, 1, ["n"])],
)
def test_trend_options_depend_on_total_differencing(d, D, expected):
    assert trend_options(d, D) == expected


def test_candidate_specs_cover_every_order_and_trend():
    specs = list(candidate_specs(d=0, D=1))
    assert len(specs) == 16 * 2
    assert ((0, 0, 0), (0, 1, 0, 12), "n") in specs
    assert all(order[1] == 0 and seasonal[1] == 1 for order, seasonal, _ in specs)


def test_seasonal_differencing_only_for_strong_seasonality(seasonal_series, white_noise):
    assert choose_seasonal_differencing(seasonal_series) == 1
    assert choose_seasonal_differencing(white_noise) == 0


def test_first_differencing_only_for_a_drifting_series(white_noise, trending_series):
    assert choose_differencing(white_noise, D=0) == 0
    assert choose_differencing(trending_series, D=0) == 1


def test_select_sarima_returns_lowest_aicc_model(seasonal_series):
    best, table = select_sarima(seasonal_series, max_order=0)
    assert table["aicc"].is_monotonic_increasing
    assert best.aicc == pytest.approx(table.loc[0, "aicc"])
    assert best.model.seasonal_order[1] == 1
    assert len(best.forecast(6)) == 6
