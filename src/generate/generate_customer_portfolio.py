from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "data" / "simulated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "customer_portfolio.csv"

N_CUSTOMERS = 5000
RANDOM_SEED = 42

rng = np.random.default_rng(RANDOM_SEED)


# --------------------------------------------------
# 1. CUSTOMER SEGMENTS
# --------------------------------------------------

segments = rng.choice(
    ["Mass", "Affluent", "Private"],
    size=N_CUSTOMERS,
    p=[0.70, 0.25, 0.05]
)


# --------------------------------------------------
# 2. SEGMENT ASSUMPTIONS
# Synthetic values for portfolio demonstration only
# --------------------------------------------------

config = {
    "Mass": {
        "median_balance": 12000,
        "balance_sigma": 0.75,
        "rate_mean": 1.65,
        "rate_sd": 0.25,
        "change_mean": -1.0,
        "change_sd": 7.0,
        "products_lambda": 1.3
    },

    "Affluent": {
        "median_balance": 65000,
        "balance_sigma": 0.65,
        "rate_mean": 1.95,
        "rate_sd": 0.22,
        "change_mean": -2.0,
        "change_sd": 8.0,
        "products_lambda": 2.0
    },

    "Private": {
        "median_balance": 250000,
        "balance_sigma": 0.55,
        "rate_mean": 2.15,
        "rate_sd": 0.18,
        "change_mean": -3.0,
        "change_sd": 9.0,
        "products_lambda": 2.8
    }
}


deposit_balance = np.zeros(N_CUSTOMERS)
current_rate = np.zeros(N_CUSTOMERS)
deposit_change_90d = np.zeros(N_CUSTOMERS)
product_count = np.zeros(N_CUSTOMERS, dtype=int)


for segment, settings in config.items():

    mask = segments == segment
    n = mask.sum()

    deposit_balance[mask] = rng.lognormal(
        mean=np.log(settings["median_balance"]),
        sigma=settings["balance_sigma"],
        size=n
    )

    current_rate[mask] = rng.normal(
        loc=settings["rate_mean"],
        scale=settings["rate_sd"],
        size=n
    )

    deposit_change_90d[mask] = rng.normal(
        loc=settings["change_mean"],
        scale=settings["change_sd"],
        size=n
    )

    product_count[mask] = (
        rng.poisson(
            lam=settings["products_lambda"],
            size=n
        ) + 1
    )


# --------------------------------------------------
# 3. OTHER RELATIONSHIP VARIABLES
# --------------------------------------------------

tenure_months = rng.integers(
    6,
    181,
    size=N_CUSTOMERS
)

has_mortgage = rng.choice(
    [0, 1],
    size=N_CUSTOMERS,
    p=[0.68, 0.32]
)


# --------------------------------------------------
# 4. BUILD DATASET
# --------------------------------------------------

customers = pd.DataFrame({
    "customer_id": [
        f"CUST_{i:05d}"
        for i in range(1, N_CUSTOMERS + 1)
    ],
    "segment": segments,
    "deposit_balance_eur": deposit_balance.round(2),
    "current_deposit_rate_pct": current_rate.round(2),
    "deposit_change_90d_pct": deposit_change_90d.round(2),
    "product_count": product_count,
    "tenure_months": tenure_months,
    "has_mortgage": has_mortgage
})


# Basic guardrails
customers["current_deposit_rate_pct"] = (
    customers["current_deposit_rate_pct"]
    .clip(lower=0.25, upper=3.00)
)

customers["deposit_change_90d_pct"] = (
    customers["deposit_change_90d_pct"]
    .clip(lower=-50, upper=30)
)


# --------------------------------------------------
# 5. SAVE
# --------------------------------------------------

customers.to_csv(
    OUTPUT_PATH,
    index=False
)


print("Synthetic portfolio saved:", OUTPUT_PATH)
print("Customers generated:", len(customers))

print("\nCustomers by segment:")
print(
    customers["segment"]
    .value_counts()
)

print("\nDeposit balance by segment:")
print(
    customers
    .groupby("segment")["deposit_balance_eur"]
    .agg(["count", "mean", "median", "sum"])
    .round(2)
)