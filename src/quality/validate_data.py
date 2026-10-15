"""Validate source CSVs and reconcile their contents with SQLite.

Install as src/quality/validate_data.py. Read-only: no data is modified.
Checks technical consistency, not economic realism or data provenance.
"""
from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RATES_PATH = PROJECT_ROOT / 'data/processed/banking_interest_rates_monthly.csv'
CUSTOMERS_PATH = PROJECT_ROOT / 'data/simulated/customer_portfolio.csv'
DB_PATH = PROJECT_ROOT / 'data/database/banking_pricing.db'

RATE_COLUMNS = [
    'period', 'deposit_rate_pct', 'mortgage_rate_pct', 'ecb_dfr_pct',
    'deposit_gap_pp', 'mortgage_deposit_spread_pp'
]
CUSTOMER_COLUMNS = [
    'customer_id', 'segment', 'deposit_balance_eur',
    'current_deposit_rate_pct', 'deposit_change_90d_pct',
    'product_count', 'tenure_months', 'has_mortgage'
]
# Only tolerate floating-point representation noise, not cent-level differences.
ABS_TOLERANCE = 1e-8


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_structure(frame, columns, source):
    missing = set(columns) - set(frame.columns)
    require(not missing, f'{source}: missing columns: {sorted(missing)}')
    require(not frame.empty, f'{source}: dataset is empty.')
    null_columns = frame[columns].columns[frame[columns].isna().any()].tolist()
    require(not null_columns, f'{source}: null values in {null_columns}')


def convert_numbers(frame, columns, source):
    for column in columns:
        try:
            frame[column] = pd.to_numeric(frame[column], errors='raise')
        except (ValueError, TypeError) as error:
            raise ValueError(f'{source}: non-numeric values in {column}') from error
        require(
            np.isfinite(frame[column].to_numpy(dtype=float)).all(),
            f'{source}: non-finite values in {column}'
        )


def check_rates(frame, source):
    check_structure(frame, RATE_COLUMNS, source)
    frame = frame[RATE_COLUMNS].copy()
    try:
        # Parse separately to support both CSV dates and SQLite timestamps.
        frame['period'] = frame['period'].map(
            lambda value: pd.to_datetime(value, errors='raise')
        )
        periods = frame['period'].dt.to_period('M')
    except (ValueError, TypeError, AttributeError, OverflowError) as error:
        raise ValueError(f'{source}: invalid monthly dates.') from error

    require(frame['period'].notna().all(), f'{source}: missing dates.')
    require(
        frame['period'].dt.tz is None,
        f'{source}: monthly dates must not contain timezones.'
    )
    require(not periods.duplicated().any(), f'{source}: duplicate months.')
    expected_months = pd.period_range(periods.min(), periods.max(), freq='M')
    missing_months = expected_months.difference(pd.PeriodIndex(periods))
    require(
        len(missing_months) == 0,
        f'{source}: missing months: {list(missing_months.astype(str))}'
    )

    convert_numbers(frame, RATE_COLUMNS[1:], source)
    for column in ['deposit_rate_pct', 'mortgage_rate_pct', 'ecb_dfr_pct']:
        require(
            frame[column].between(-5, 20).all(),
            f'{source}: {column} outside project bounds [-5, 20].'
        )

    expected = {
        'deposit_gap_pp': frame['ecb_dfr_pct'] - frame['deposit_rate_pct'],
        'mortgage_deposit_spread_pp': (
            frame['mortgage_rate_pct'] - frame['deposit_rate_pct']
        )
    }
    for column, calculated in expected.items():
        require(
            np.isclose(frame[column], calculated, rtol=0,
                       atol=ABS_TOLERANCE).all(),
            f'{source}: {column} is inconsistent with the underlying rates.'
        )
    return frame


def check_customers(frame, source):
    check_structure(frame, CUSTOMER_COLUMNS, source)
    frame = frame[CUSTOMER_COLUMNS].copy()
    for column in ['customer_id', 'segment']:
        require(
            frame[column].map(lambda value: isinstance(value, str)).all(),
            f'{source}: {column} must contain text.'
        )
        require(
            frame[column].str.strip().ne('').all(),
            f'{source}: blank values in {column}.'
        )
    require(
        not frame['customer_id'].duplicated().any(),
        f'{source}: duplicate customer IDs.'
    )
    require(
        frame['segment'].isin(['Mass', 'Affluent', 'Private']).all(),
        f'{source}: unexpected customer segments.'
    )
    convert_numbers(frame, CUSTOMER_COLUMNS[2:], source)
    require(
        frame['deposit_balance_eur'].ge(0).all(),
        f'{source}: negative deposit balances.'
    )
    require(
        frame['current_deposit_rate_pct'].between(-5, 20).all(),
        f'{source}: customer rates outside project bounds [-5, 20].'
    )
    require(
        frame['deposit_change_90d_pct'].ge(-100).all(),
        f'{source}: deposit changes below -100%.'
    )
    for column, minimum in [('product_count', 1), ('tenure_months', 0)]:
        require(
            (frame[column].ge(minimum) & frame[column].mod(1).eq(0)).all(),
            f'{source}: {column} must contain integers >= {minimum}.'
        )
    require(
        frame['has_mortgage'].isin([0, 1]).all(),
        f'{source}: has_mortgage must be 0 or 1.'
    )
    return frame


def validate_interest_rates():
    rates = check_rates(pd.read_csv(RATES_PATH), 'Interest rates CSV')
    print(f'[OK] Interest rates validated: {len(rates)} rows; '
          'continuous months and consistent gap/spread.')
    return rates


def validate_customers():
    customers = check_customers(pd.read_csv(CUSTOMERS_PATH), 'Customers CSV')
    print(f'[OK] Customer portfolio validated: {len(customers)} rows')
    return customers


def compare_contents(expected, actual, key, source):
    require(len(expected) == len(actual), f'{source}: row count differs from CSV.')
    left = expected.sort_values(key).reset_index(drop=True)
    right = actual.sort_values(key).reset_index(drop=True)
    for column in left.columns:
        if pd.api.types.is_numeric_dtype(left[column]):
            matching = np.isclose(
                left[column].to_numpy(dtype=float),
                right[column].to_numpy(dtype=float),
                rtol=0, atol=ABS_TOLERANCE
            )
        else:
            matching = left[column].eq(right[column]).to_numpy()
        require(
            matching.all(),
            f'{source}: column {column} differs from CSV '
            f'in {int((~matching).sum())} sorted row(s).'
        )
    print(f'[OK] {source}: all required columns match CSV ({len(left)} rows)')


def validate_database(expected_rates, expected_customers):
    if not DB_PATH.is_file():
        raise FileNotFoundError(f'SQLite database not found: {DB_PATH}')

    # Read-only mode prevents accidental database creation or writes.
    with sqlite3.connect(DB_PATH.resolve().as_uri() + '?mode=ro', uri=True) as conn:
        rates = pd.read_sql_query('SELECT * FROM interest_rates', conn)
        customers = pd.read_sql_query('SELECT * FROM customers', conn)

    rates = check_rates(rates, 'Database interest_rates')
    customers = check_customers(customers, 'Database customers')
    compare_contents(expected_rates, rates, 'period', 'Database interest_rates')
    compare_contents(expected_customers, customers, 'customer_id', 'Database customers')


def main():
    rates = validate_interest_rates()
    customers = validate_customers()
    validate_database(rates, customers)
    print('\nAll data quality checks passed.')


if __name__ == '__main__':
    main()
