import sqlite3

import pandas as pd
import pytest

from src import etl

RAW_COLUMNS = [
    "Row ID", "Order ID", "Order Date", "Ship Date", "Ship Mode", "Customer ID",
    "Customer Name", "Segment", "Country", "City", "State", "Postal Code", "Region",
    "Product ID", "Category", "Sub-Category", "Product Name", "Sales", "Quantity",
    "Discount", "Profit",
]
RAW_ROWS = [
    [1, "CA-1", "1/3/2014", "1/5/2014", "Second Class", "C-1", "Ann", "Consumer",
     "United States", "Boston", "Massachusetts", 2108, "East", "FUR-1", "Furniture",
     "Chairs", "Chair", 100.0, 2, 0.0, 20.0],
    [2, "CA-1", "1/3/2014", "1/5/2014", "Second Class", "C-1", "Ann", "Consumer",
     "United States", "Boston", "Massachusetts", 2108, "East", "OFF-1", "Office Supplies",
     "Paper", "Paper", 10.0, 5, 0.2, -1.0],
    [3, "CA-2", "2/10/2014", "2/10/2014", "Same Day", "C-2", "Bo", "Corporate",
     "United States", "Seattle", "Washington", 98103, "West", "TEC-1", "Technology",
     "Phones", "Phone", 300.0, 1, 0.0, 90.0],
]


@pytest.fixture
def raw_df():
    return pd.DataFrame(RAW_ROWS, columns=RAW_COLUMNS)


@pytest.fixture
def raw_csv(tmp_path, raw_df):
    path = tmp_path / "raw.csv"
    raw_df.to_csv(path, index=False)
    return path


def test_read_raw_strips_null_bytes(tmp_path, raw_df):
    path = tmp_path / "with_nulls.csv"
    path.write_bytes(raw_df.to_csv(index=False).encode().replace(b"Chair", b"Ch\x00air"))
    df = etl.read_raw(path)
    assert df.shape == raw_df.shape
    assert df.loc[0, "Product Name"] == "Chair"


def test_clean_renames_parses_dates_and_pads_postal_code(raw_df):
    df = etl.clean(raw_df)
    assert "sub_category" in df.columns and "order_id" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["order_date"])
    assert df.loc[0, "postal_code"] == "02108"


def test_enrich_adds_derived_columns(raw_df):
    df = etl.enrich(etl.clean(raw_df))
    assert df.loc[0, "profit_margin"] == pytest.approx(0.2)
    assert df.loc[0, "ship_lag_days"] == 2
    assert (df.loc[2, "order_year"], df.loc[2, "order_month"], df.loc[2, "order_quarter"]) == (2014, 2, 1)


def test_validate_passes_on_clean_data(raw_df):
    assert etl.validate(etl.enrich(etl.clean(raw_df))) == []


@pytest.mark.parametrize(
    "column, bad_value, expected_message",
    [
        pytest.param("Discount", 1.5, "discount", id="discount_above_1"),
        pytest.param("Quantity", 0, "quantity", id="zero_quantity"),
        pytest.param("Sales", -5.0, "sales", id="negative_sales"),
        pytest.param("Region", "North", "region", id="unknown_region"),
    ],
)
def test_validate_reports_broken_rules(raw_df, column, bad_value, expected_message):
    raw_df.loc[0, column] = bad_value
    errors = etl.validate(etl.enrich(etl.clean(raw_df)))
    assert len(errors) == 1
    assert expected_message in errors[0]


def test_build_database_creates_star_schema(raw_csv, tmp_path):
    db_path = tmp_path / "db" / "test.db"
    counts = etl.build_database(raw_path=raw_csv, db_path=db_path)
    assert counts == {"customers": 2, "products": 3, "geography": 2, "order_items": 3}

    conn = sqlite3.connect(db_path)
    margin = conn.execute("SELECT profit_margin FROM order_items WHERE row_id = 1").fetchone()[0]
    conn.close()
    assert margin == pytest.approx(0.2)


def test_build_database_refuses_invalid_data(raw_csv, tmp_path, raw_df):
    raw_df.loc[0, "Discount"] = 2.0
    raw_df.to_csv(raw_csv, index=False)
    db_path = tmp_path / "test.db"
    with pytest.raises(ValueError, match="Validation failed"):
        etl.build_database(raw_path=raw_csv, db_path=db_path)
    assert not db_path.exists()
