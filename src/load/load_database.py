from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RATES_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "banking_interest_rates_monthly.csv"
)

CUSTOMERS_PATH = (
    PROJECT_ROOT
    / "data"
    / "simulated"
    / "customer_portfolio.csv"
)

DB_DIR = PROJECT_ROOT / "data" / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "banking_pricing.db"


rates = pd.read_csv(
    RATES_PATH,
    parse_dates=["period"]
)

rates["period"] = (
    rates["period"]
    .dt.strftime("%Y-%m-%d")
)

customers = pd.read_csv(
    CUSTOMERS_PATH
)


with sqlite3.connect(DB_PATH) as connection:

    rates.to_sql(
        "interest_rates",
        connection,
        if_exists="replace",
        index=False
    )

    customers.to_sql(
        "customers",
        connection,
        if_exists="replace",
        index=False
    )


print("Database created:", DB_PATH)
print("Interest rate rows loaded:", len(rates))
print("Customer rows loaded:", len(customers))