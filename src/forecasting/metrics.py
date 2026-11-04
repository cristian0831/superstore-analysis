import numpy as np


def mape(actual, forecast) -> float:
    """Mean Absolute Percentage Error, in %: the average of each month's |error| / actual."""
    actual, forecast = np.asarray(actual, dtype=float), np.asarray(forecast, dtype=float)
    return float(np.mean(np.abs(actual - forecast) / np.abs(actual)) * 100)


def wape(actual, forecast) -> float:
    """Weighted Absolute Percentage Error, in %: total |error| / total actual.

    Unlike MAPE, a low-sales month cannot dominate the score, because each month
    weighs in proportion to its sales.
    """
    actual, forecast = np.asarray(actual, dtype=float), np.asarray(forecast, dtype=float)
    return float(np.sum(np.abs(actual - forecast)) / np.sum(np.abs(actual)) * 100)
