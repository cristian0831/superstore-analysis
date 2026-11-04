import pandas as pd

from src import config

TOTAL = "Total"
CATEGORIES = ["Furniture", "Office Supplies", "Technology"]
SERIES = [TOTAL, *CATEGORIES]


def load_monthly_sales() -> pd.DataFrame:
    """Monthly sales indexed by month start, one column per series (Total + each category).

    Reads the CSVs written by `python -m src.sql_runner forecasting`.
    """
    total = pd.read_csv(config.MONTHLY_SALES_CSV, parse_dates=["month_start"])
    by_category = pd.read_csv(
        config.MONTHLY_SALES_BY_CATEGORY_CSV, parse_dates=["month_start"]
    )

    sales = by_category.pivot(
        index="month_start", columns="category", values="total_sales"
    )[CATEGORIES]
    sales.insert(0, TOTAL, total.set_index("month_start")["total_sales"])
    sales.columns.name = None
    sales.index.name = "month"
    # asfreq gives the index a monthly frequency (statsmodels needs it) and
    # would surface a missing month as a NaN row instead of hiding it.
    return sales.asfreq("MS")


def split_holdout(sales, holdout_months: int = config.HOLDOUT_MONTHS):
    """Split into (train, holdout), where holdout is the last `holdout_months` rows."""
    return sales.iloc[:-holdout_months], sales.iloc[-holdout_months:]
