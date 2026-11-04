"""Run every .sql file of an analysis track and save each result as a CSV.

    python -m src.sql_runner                 # every track that has queries
    python -m src.sql_runner forecasting     # one track

Queries are read from sql/<track>/ and results written to outputs/<track>/tables/.
"""
import argparse
import re
from pathlib import Path

from src import config
from src.db_utils import run_query


def title_from_stem(stem: str) -> str:
    """"01_growth_trends" -> "Growth Trends" """
    name = re.sub(r"^\d+_", "", stem)
    return name.replace("_", " ").title()


def run_queries(queries_dir: Path, output_dir: Path, verbose: bool = True) -> dict:
    """Run each .sql file in queries_dir (in name order) and save its result to output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    results = {}

    for sql_file in sorted(queries_dir.glob("*.sql")):
        result = run_query(sql_file)
        csv_path = output_dir / f"{sql_file.stem}.csv"
        result.to_csv(csv_path, index=False)
        results[sql_file.stem] = result

        if verbose:
            print(f"=== {title_from_stem(sql_file.stem)} ===")
            print(result.to_string(index=False, max_rows=12))
            print(f"Saved {len(result)} rows to {csv_path}\n")

    return results


def run_track(track: str, verbose: bool = True) -> dict:
    return run_queries(
        config.SQL_DIR / track, config.OUTPUTS_DIR / track / "tables", verbose=verbose
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("tracks", nargs="*", metavar="track",
                        help=f"one or more of {', '.join(config.TRACKS)} (default: all)")
    args = parser.parse_args()
    unknown = set(args.tracks) - set(config.TRACKS)
    if unknown:
        parser.error(f"unknown track(s): {', '.join(sorted(unknown))}")

    for track in args.tracks or config.TRACKS:
        if any((config.SQL_DIR / track).glob("*.sql")):
            run_track(track)


if __name__ == "__main__":
    main()
