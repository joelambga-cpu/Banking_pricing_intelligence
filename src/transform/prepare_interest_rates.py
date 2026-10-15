from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def load_series(filename):
    df = pd.read_csv(
        PROCESSED_DIR / filename,
        parse_dates=["period"]
    )

    return df


# 1. LOAD DATA
deposit = load_series(
    "italy_household_deposit_rate.csv"
)

mortgage = load_series(
    "italy_household_mortgage_rate.csv"
)

dfr = load_series(
    "ecb_deposit_facility_rate.csv"
)


# 2. KEEP ONLY REQUIRED COLUMNS
deposit = deposit[
    ["period", "value_pct"]
].rename(
    columns={
        "value_pct": "deposit_rate_pct"
    }
)

mortgage = mortgage[
    ["period", "value_pct"]
].rename(
    columns={
        "value_pct": "mortgage_rate_pct"
    }
)

dfr = dfr[
    ["period", "value_pct"]
].rename(
    columns={
        "value_pct": "ecb_dfr_pct"
    }
)


# 3. CONVERT DAILY ECB RATE TO MONTHLY
dfr = dfr.sort_values("period")

dfr["month"] = (
    dfr["period"]
    .dt.to_period("M")
)

dfr_monthly = (
    dfr
    .groupby("month", as_index=False)
    .last()
)

dfr_monthly["period"] = (
    dfr_monthly["month"]
    .dt.to_timestamp()
)

dfr_monthly = dfr_monthly[
    ["period", "ecb_dfr_pct"]
]


# 4. MERGE MONTHLY SERIES
rates = deposit.merge(
    mortgage,
    on="period",
    how="inner"
)

rates = rates.merge(
    dfr_monthly,
    on="period",
    how="left"
)


# 5. BUSINESS METRICS
rates["deposit_gap_pp"] = (
    rates["ecb_dfr_pct"]
    - rates["deposit_rate_pct"]
)

rates["mortgage_deposit_spread_pp"] = (
    rates["mortgage_rate_pct"]
    - rates["deposit_rate_pct"]
)


# 6. SORT AND SAVE
rates = rates.sort_values("period")

output_path = (
    PROCESSED_DIR /
    "banking_interest_rates_monthly.csv"
)

rates.to_csv(
    output_path,
    index=False
)

print(
    "Analytical dataset saved:",
    output_path
)

print("\nLatest observations:")
print(rates.tail())