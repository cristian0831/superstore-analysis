"""ETL: raw CSV -> cleaned, enriched, validated data -> SQLite star schema.

Run `python -m src.etl` to rebuild db/superstore.db from data/raw/superstore.csv.
notebooks/01_etl_superstore.ipynb walks through the same steps one at a time.
"""
import sqlite3
from io import StringIO

import chardet
import numpy as np
import pandas as pd

from src import config

ALLOWED_VALUES = {
    "segment": {"Consumer", "Corporate", "Home Office"},
    "region": {"West", "East", "Central", "South"},
    "ship_mode": {"Standard Class", "Second Class", "First Class", "Same Day"},
    "category": {"Furniture", "Office Supplies", "Technology"},
}
STAR_SCHEMA_TABLES = ["customers", "products", "geography", "order_items"]


# ── Extract ──────────────────────────────────────────────────────────────────
def detect_encoding(path=None, sample_bytes: int = 50_000) -> dict:
    """Sniff the file's encoding from its first bytes (chardet)."""
    with open(path or config.RAW_PATH, "rb") as f:
        return chardet.detect(f.read(sample_bytes))


def read_raw(path=None) -> pd.DataFrame:
    """Load the raw CSV exactly as-is, after stripping null bytes."""
    with open(path or config.RAW_PATH, "rb") as f:
        raw_bytes = f.read()
    # Strip null bytes and decode safely
    decoded_text = raw_bytes.replace(b"\x00", b"").decode("utf-8", errors="ignore")
    return pd.read_csv(StringIO(decoded_text))


# ── Transform ────────────────────────────────────────────────────────────────
def clean(df_raw: pd.DataFrame) -> pd.DataFrame:
    """snake_case column names, parsed dates, postal_code as a 5-character string."""
    df = df_raw.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )
    df["order_date"] = pd.to_datetime(df["order_date"], dayfirst=False)
    df["ship_date"] = pd.to_datetime(df["ship_date"], dayfirst=False)
    # Postal code is a label, not a number: leading zeros must be preserved
    df["postal_code"] = df["postal_code"].astype(str).str.zfill(5)
    return df


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Add profit_margin, ship_lag_days and order date parts."""
    df = df.copy()
    # Profit margin — guard against division by zero
    df["profit_margin"] = (df["profit"] / df["sales"].replace(0, np.nan)).round(4)
    df["ship_lag_days"] = (df["ship_date"] - df["order_date"]).dt.days
    df["order_year"] = df["order_date"].dt.year
    df["order_month"] = df["order_date"].dt.month
    df["order_quarter"] = df["order_date"].dt.quarter
    return df


def validate(df: pd.DataFrame) -> list:
    """Check the business rules; return one message per broken rule (empty = valid)."""
    errors = []

    # Rule 1 — No nulls
    null_counts = df.isnull().sum()
    if null_counts.sum() > 0:
        errors.append(f"Nulls found:\n{null_counts[null_counts > 0]}")

    # Rule 2 — Discount in [0, 1]
    if not df["discount"].between(0, 1).all():
        errors.append("discount values outside [0, 1]")

    # Rule 3 — Quantity > 0
    if (df["quantity"] <= 0).any():
        errors.append("quantity has non-positive values")

    # Rule 4 — Sales >= 0
    if (df["sales"] < 0).any():
        errors.append("sales has negative values")

    # Rule 5 — Ship date >= Order date
    if (df["ship_lag_days"] < 0).any():
        n = (df["ship_lag_days"] < 0).sum()
        errors.append(f"{n} rows where ship_date < order_date")

    # Rule 6 — product_id maps to one category
    prod_cat = df.groupby("product_id")["category"].nunique()
    if (prod_cat > 1).any():
        errors.append(f"{(prod_cat > 1).sum()} product_ids map to multiple categories")

    # Rule 7 — Allowed categorical values
    for col, allowed in ALLOWED_VALUES.items():
        bad = set(df[col].unique()) - allowed
        if bad:
            errors.append(f"Unexpected values in '{col}': {bad}")

    return errors


def product_name_conflicts(df: pd.DataFrame) -> pd.Series:
    """product_ids with more than one product_name (known data quality issue).

    The star schema keeps MIN(product_name) per product_id.
    """
    return df.groupby("product_id")["product_name"].nunique().pipe(lambda s: s[s > 1])


# ── Load ─────────────────────────────────────────────────────────────────────
def create_database(db_path=None) -> sqlite3.Connection:
    """Open a brand-new database, deleting any previous one so every run is reproducible."""
    db_path = db_path or config.DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    return sqlite3.connect(db_path)


def stage_raw(df_raw: pd.DataFrame, conn: sqlite3.Connection) -> None:
    """orders_raw: immutable copy of the source, kept as an audit trail."""
    df_raw.to_sql("orders_raw", conn, if_exists="replace", index=False)


def stage_clean(df: pd.DataFrame, conn: sqlite3.Connection) -> None:
    """orders_clean: the cleaned and enriched rows the star schema is built from."""
    df.to_sql("orders_clean", conn, if_exists="replace", index=False)


def load_star_schema(conn: sqlite3.Connection) -> None:
    """Create and fill the star schema tables from orders_clean (sql/etl/star_schema.sql)."""
    conn.executescript(config.STAR_SCHEMA_SQL.read_text())
    conn.commit()


def table_row_counts(conn: sqlite3.Connection) -> dict:
    return {
        table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in STAR_SCHEMA_TABLES
    }


def build_database(raw_path=None, db_path=None) -> dict:
    """Run the full pipeline. Returns the row count of each star schema table."""
    df_raw = read_raw(raw_path)
    df = enrich(clean(df_raw))

    errors = validate(df)
    if errors:
        raise ValueError("Validation failed — fix errors before loading:\n" + "\n".join(errors))

    conn = create_database(db_path)
    try:
        stage_raw(df_raw, conn)
        stage_clean(df, conn)
        load_star_schema(conn)
        return table_row_counts(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    counts = build_database()
    print(f"Built {config.DB_PATH.relative_to(config.PROJECT_ROOT)}")
    for table, n in counts.items():
        print(f"  {table:<12} {n:>6,} rows")
