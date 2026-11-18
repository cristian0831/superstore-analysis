from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "superstore.csv"
DB_PATH = PROJECT_ROOT / "db" / "superstore.db"

SQL_DIR = PROJECT_ROOT / "sql"
STAR_SCHEMA_SQL = SQL_DIR / "etl" / "star_schema.sql"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Analysis tracks: each has its queries in sql/<track>/ and its results in outputs/<track>/.
TRACKS = ("diagnostics", "forecasting", "regression")

MONTHLY_SALES_CSV = OUTPUTS_DIR / "forecasting" / "tables" / "01_monthly_sales.csv"
MONTHLY_SALES_BY_CATEGORY_CSV = OUTPUTS_DIR / "forecasting" / "tables" / "02_monthly_sales_by_category.csv"

# Last months set aside to validate the forecasts; never used to fit or tune a model.
HOLDOUT_MONTHS = 12

# Final forecast and inventory plan
FORECAST_HORIZON = 6
# Share of months in which stock should cover demand (90% = run short in about 1 month in 10)
SERVICE_LEVEL = 0.90
