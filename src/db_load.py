"""Load processed CSVs into the DuckDB warehouse and apply schema."""
from __future__ import annotations

from pathlib import Path

import duckdb

PROC = Path("data/processed")
TABLES = ["slots", "sku_velocity", "optimal_assignment", "baseline_assignment"]


def main() -> None:
    db_path = PROC / "slotting.duckdb"
    con = duckdb.connect(str(db_path))
    con.execute(Path("sql/schema.sql").read_text())
    for table in TABLES:
        csv = PROC / f"{table}.csv"
        if not csv.exists():
            print(f"skip {table} ({csv} not found yet)")
            continue
        con.execute(f"DELETE FROM {table}")
        con.execute(f"INSERT INTO {table} SELECT * FROM read_csv_auto('{csv}', header=true)")
        n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"loaded {table}: {n:,} rows")
    con.close()


if __name__ == "__main__":
    main()
