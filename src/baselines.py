import numpy as np
import pandas as pd


def _future_index(train: pd.Series, horizon: int) -> pd.DatetimeIndex:
    return pd.date_range(train.index[-1], periods=horizon + 1, freq=train.index.freq)[1:]


def naive_forecast(train: pd.Series, horizon: int) -> pd.Series:
    """Repeat the last observed month for every future month."""
    return pd.Series(train.iloc[-1], index=_future_index(train, horizon), name=train.name)


def seasonal_naive_forecast(train: pd.Series, horizon: int, season: int = 12) -> pd.Series:
    """Repeat the value from the same month one season earlier (Jan 2017 = Jan 2016)."""
    last_season = train.iloc[-season:].to_numpy()
    values = np.resize(last_season, horizon)
    return pd.Series(values, index=_future_index(train, horizon), name=train.name)
