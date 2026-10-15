from pathlib import Path
import sqlite3

import pandas as pd
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = (
    PROJECT_ROOT
    / "data"
    / "database"
    / "banking_pricing.db"
)

if len(sys.argv) < 2:
    raise SystemExit(
        "Usage: python src/analysis/run_query.py <query_file.sql>"
    )

query_file = sys.argv[1]

SQL_PATH = (
    PROJECT_ROOT
    / "sql"
    / "analysis"
    / query_file
)
with open(SQL_PATH, "r", encoding="utf-8") as file:
    query = file.read()


with sqlite3.connect(DB_PATH) as connection:
    result = pd.read_sql_query(
        query,
        connection
    )


print(result.tail(12).to_string(index=False))