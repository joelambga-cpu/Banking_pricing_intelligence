from pathlib import Path
from datetime import date
from io import StringIO

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def create_session():
    retry_strategy = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    session = requests.Session()

    adapter = HTTPAdapter(
        max_retries=retry_strategy
    )

    session.mount(
        "https://",
        adapter
    )

    return session


def fetch_ecb_series(
    dataset,
    series_key,
    series_name,
    start_period
):
    base_url = (
        f"https://data-api.ecb.europa.eu/"
        f"service/data/{dataset}"
    )

    url = f"{base_url}/{series_key}"

    params = {
        "startPeriod": start_period,
        "format": "csvdata"
    }

    session = create_session()

    try:
        response = session.get(
            url,
            params=params,
            timeout=(10, 90)
        )

        response.raise_for_status()

    except requests.RequestException as error:
        raise SystemExit(
            f"ECB API request failed for "
            f"{series_name}: {error}"
        )

    print(
        f"\n{series_name}"
    )

    print(
        "Status:",
        response.status_code
    )

    today = date.today().isoformat()

    raw_path = (
        RAW_DIR /
        f"{series_name}_{today}.csv"
    )

    raw_path.write_bytes(
        response.content
    )

    print(
        "Raw file saved:",
        raw_path
    )

    df = pd.read_csv(
        StringIO(response.text)
    )

    print(
        "Rows received:",
        len(df)
    )

    clean_df = df[
        [
            "TIME_PERIOD",
            "OBS_VALUE"
        ]
    ].copy()

    clean_df = clean_df.rename(
        columns={
            "TIME_PERIOD": "period",
            "OBS_VALUE": "value_pct"
        }
    )

    clean_df["period"] = pd.to_datetime(
        clean_df["period"]
    )

    clean_df["value_pct"] = pd.to_numeric(
        clean_df["value_pct"],
        errors="coerce"
    )

    clean_df["series_name"] = series_name
    clean_df["series_key"] = series_key

    clean_df = clean_df.sort_values(
        "period"
    )

    processed_path = (
        PROCESSED_DIR /
        f"{series_name}.csv"
    )

    clean_df.to_csv(
        processed_path,
        index=False
    )

    print(
        "Processed file saved:",
        processed_path
    )

    print(
        "\nLatest observations:"
    )

    print(
        clean_df.tail()
    )

    return clean_df

if __name__ == "__main__":

    deposit_rates = fetch_ecb_series(
        dataset="MIR",
        series_key="M.IT.B.L22.F.R.A.2250.EUR.N",
        series_name="italy_household_deposit_rate",
        start_period="2023-01"
    )

    ecb_deposit_facility_rate = fetch_ecb_series(
        dataset="FM",
        series_key="D.U2.EUR.4F.KR.DFR.LEV",
        series_name="ecb_deposit_facility_rate",
        start_period="2023-01-01"
    )

    mortgage_rates = fetch_ecb_series(
        dataset="MIR",
        series_key="M.IT.B.A2C.A.R.A.2250.EUR.N",
        series_name="italy_household_mortgage_rate",
        start_period="2023-01"
    )