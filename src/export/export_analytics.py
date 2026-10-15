from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = (
    PROJECT_ROOT
    / "data"
    / "database"
    / "banking_pricing.db"
)

SQL_DIR = PROJECT_ROOT / "sql" / "analysis"

OUTPUT_DIR = PROJECT_ROOT / "data" / "analytics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


EXPORTS = {
    "pricing_regimes.csv":
        "04_pricing_regimes.sql",

    "regime_transitions.csv":
        "05_regime_transitions.sql",

    "customer_pricing_opportunities.csv":
        "06_customer_pricing_opportunities.sql",

    "strategy_cost_comparison.csv":
        "07_strategy_cost_comparison.sql",

    "segment_pricing_analysis.csv":
        "08_segment_pricing_analysis.sql",

    "retention_scenarios.csv":
        "09_retention_scenarios.sql",

    "profitability_proxy.csv":
        "10_profitability_proxy.sql"
}


with sqlite3.connect(DB_PATH) as connection:

    for output_file, sql_file in EXPORTS.items():

        sql_path = SQL_DIR / sql_file

        with open(
            sql_path,
            "r",
            encoding="utf-8"
        ) as file:
            query = file.read()

        df = pd.read_sql_query(
            query,
            connection
        )

        output_path = OUTPUT_DIR / output_file

        df.to_csv(
            output_path,
            index=False
        )

        print(
            f"[OK] {sql_file} "
            f"-> {output_file} "
            f"({len(df)} rows)"
        )


print(
    "\nAnalytical exports completed."
)