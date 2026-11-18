"""Turn forecasts with uncertainty into stock targets.

The forecast for a month is treated as normally distributed with the model's
mean and standard error. A stock target at service level s is the s-quantile:
enough to cover demand in a share s of months.
"""
import numpy as np
import pandas as pd
from scipy.stats import norm


def stock_target(mean, se, service_level: float):
    """Demand level covered with probability `service_level`."""
    return mean + norm.ppf(service_level) * se


def safety_stock(se, service_level: float):
    """Buffer above the forecast needed to reach `service_level`."""
    return norm.ppf(service_level) * se


def bottom_up_total(means: pd.DataFrame, ses: pd.DataFrame, corr: pd.DataFrame):
    """Mean and standard error of the sum of the columns, for each row (month).

    Category errors are correlated, so the standard error of the sum is not the
    plain sum of standard errors: var(sum) = s' C s, with s the standard errors
    and C their correlation matrix.
    """
    corr = corr.loc[ses.columns, ses.columns].to_numpy()
    s = ses.to_numpy()
    variance = np.einsum("ti,ij,tj->t", s, corr, s)
    return means.sum(axis=1), pd.Series(np.sqrt(variance), index=ses.index)
