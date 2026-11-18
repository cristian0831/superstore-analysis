"""SARIMA order selection, following the rules of auto.arima (Hyndman & Khandakar, 2008).

AICc can only compare models fitted to the same differenced data, so the
differencing is fixed first by rules, and AICc then chooses the remaining orders:

1. D (seasonal differencing): 1 when STL seasonal strength is above 0.64.
2. d (first differencing): 1 when KPSS rejects stationarity of the series
   (after the seasonal difference, if D = 1).
3. p, q, P, Q in {0, 1} and the trend term: the lowest AICc.
"""
import itertools
import warnings

import numpy as np
import pandas as pd
from statsmodels.tools.sm_exceptions import InterpolationWarning
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.stattools import kpss

SEASON = 12
SEASONAL_STRENGTH_THRESHOLD = 0.64
KPSS_ALPHA = 0.05


def seasonal_strength(series: pd.Series, season: int = SEASON) -> float:
    """STL seasonal strength from 0 (none) to 1, with a fixed seasonal pattern.

    Same decomposition as the exploration notebook: a seasonal window longer
    than the data, so every year shares one set of seasonal values.
    """
    result = STL(series, period=season, seasonal=101, seasonal_deg=0, robust=True).fit()
    return max(0.0, 1 - result.resid.var() / (result.seasonal + result.resid).var())


def choose_seasonal_differencing(series: pd.Series, season: int = SEASON) -> int:
    return int(seasonal_strength(series, season) > SEASONAL_STRENGTH_THRESHOLD)


def kpss_pvalue(series: pd.Series) -> float:
    with warnings.catch_warnings():
        # KPSS reports p-values outside its lookup table as 0.01 or 0.10
        warnings.simplefilter("ignore", InterpolationWarning)
        return kpss(series, regression="c", nlags="auto", result_object=True).pvalue


def choose_differencing(series: pd.Series, D: int, season: int = SEASON) -> int:
    differenced = series.diff(season).dropna() if D else series
    return int(kpss_pvalue(differenced) < KPSS_ALPHA)


def trend_options(d: int, D: int) -> list:
    """Deterministic terms that remain identifiable after differencing.

    "c" is a constant mean (no differencing); "t" is a linear trend, which
    after one difference becomes a constant drift, i.e. steady growth.
    """
    total = d + D
    if total == 0:
        return ["n", "c"]
    if total == 1:
        return ["n", "t"]
    return ["n"]


def candidate_specs(d: int, D: int, max_order: int = 1, season: int = SEASON):
    orders = range(max_order + 1)
    for p, q, P, Q in itertools.product(orders, orders, orders, orders):
        for trend in trend_options(d, D):
            yield (p, d, q), (P, D, Q, season), trend


def fit_sarima(series: pd.Series, order, seasonal_order, trend):
    with warnings.catch_warnings():
        # Small samples often trigger convergence and start-value warnings;
        # the fit is still usable and is judged by its AICc.
        warnings.simplefilter("ignore")
        return ARIMA(series, order=order, seasonal_order=seasonal_order, trend=trend).fit()


def select_sarima(series: pd.Series, max_order: int = 1, season: int = SEASON):
    """Choose d and D by rule, then the lowest-AICc model among the candidates.

    Returns (best fitted result, table of every candidate sorted by AICc).
    """
    D = choose_seasonal_differencing(series, season)
    d = choose_differencing(series, D, season)

    rows, fits = [], {}
    for order, seasonal_order, trend in candidate_specs(d, D, max_order, season):
        key = (order, seasonal_order, trend)
        try:
            fits[key] = fit_sarima(series, order, seasonal_order, trend)
        except (ValueError, IndexError, np.linalg.LinAlgError):
            continue
        rows.append({"order": order, "seasonal_order": seasonal_order, "trend": trend,
                     "aicc": fits[key].aicc})

    table = pd.DataFrame(rows).sort_values("aicc", ignore_index=True)
    best = table.iloc[0]
    return fits[(best["order"], best["seasonal_order"], best["trend"])], table


def refit(result, series: pd.Series):
    """Re-estimate an already chosen specification (orders, differencing, trend) on new data."""
    model = result.model
    return fit_sarima(series, model.order, model.seasonal_order, model.trend)
