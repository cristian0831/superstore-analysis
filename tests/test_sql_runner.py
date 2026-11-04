import pandas as pd

from src.sql_runner import run_queries, title_from_stem


def test_title_from_stem_drops_number_prefix():
    assert title_from_stem("01_growth_trends") == "Growth Trends"


def test_run_queries_runs_files_in_order_and_saves_csvs(patch_db_path, tmp_path):
    queries_dir = tmp_path / "queries"
    queries_dir.mkdir()
    (queries_dir / "02_second.sql").write_text("SELECT name FROM widgets WHERE id = 2")
    (queries_dir / "01_first.sql").write_text("SELECT COUNT(*) AS n FROM widgets")
    output_dir = tmp_path / "out" / "tables"

    results = run_queries(queries_dir, output_dir, verbose=False)

    assert list(results) == ["01_first", "02_second"]
    assert pd.read_csv(output_dir / "01_first.csv").loc[0, "n"] == 3
    assert pd.read_csv(output_dir / "02_second.csv").loc[0, "name"] == "beta"
