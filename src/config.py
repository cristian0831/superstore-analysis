from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "superstore.csv"
DB_PATH = PROJECT_ROOT / "db" / "superstore.db"

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
PREPARED_TABLES_DIR = OUTPUTS_DIR / "phase2_data_preparation" / "tables"
MONTHLY_SALES_CSV = PREPARED_TABLES_DIR / "01_monthly_sales.csv"
MONTHLY_SALES_BY_CATEGORY_CSV = PREPARED_TABLES_DIR / "02_monthly_sales_by_category.csv"

# Last months set aside to validate the forecasts; never used to fit or tune a model.
HOLDOUT_MONTHS = 12
