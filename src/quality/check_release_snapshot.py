"""Check archived sources and replay all six pipeline stages in an isolated copy.

The replay substitutes archived HTTP response bodies: it does not test live ECB
connectivity. No source dataset or production pipeline metadata is overwritten.
"""
from pathlib import Path
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/evidence"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    OUT.mkdir(exist_ok=True, parents=True)
    source_names = ["italy_household_deposit_rate", "italy_household_mortgage_rate", "ecb_deposit_facility_rate"]
    raw_files = {}
    reconciliation = {}
    for name in source_names:
        raw = sorted((ROOT / "data/raw").glob(name + "_*.csv"))[-1]
        raw_files[name] = raw
        data = pd.read_csv(raw)
        actual = pd.read_csv(ROOT / f"data/processed/{name}.csv")
        expected = data[["TIME_PERIOD", "OBS_VALUE"]].copy()
        expected.columns = ["period", "value_pct"]
        expected["period"] = pd.to_datetime(expected["period"])
        actual["period"] = pd.to_datetime(actual["period"])
        expected = expected.sort_values("period").reset_index(drop=True)
        actual = actual.sort_values("period").reset_index(drop=True)
        require(not expected["period"].duplicated().any(), name + " duplicates")
        pd.testing.assert_frame_equal(expected, actual[["period", "value_pct"]], check_dtype=False, atol=1e-12, rtol=0)
        reconciliation[name] = {"raw": str(raw.relative_to(ROOT)), "rows": len(data), "sha256": hashlib.sha256(raw.read_bytes()).hexdigest(), "status": "PASS"}

    monthly = pd.read_csv(ROOT / "data/processed/banking_interest_rates_monthly.csv")
    daily = pd.read_csv(ROOT / "data/processed/ecb_deposit_facility_rate.csv", parse_dates=["period"])
    start = pd.Timestamp(monthly.period.min())
    end = pd.Timestamp(monthly.period.max()) + pd.offsets.MonthEnd(0)
    covered = daily[daily.period.between(start, end)]
    expected_days = pd.date_range(start, end, freq="D")
    require(len(expected_days.difference(covered.period)) == 0, "DFR missing days")
    require(not covered.period.duplicated().any() and covered.value_pct.notna().all(), "DFR invalid dates/values")

    work = Path(tempfile.mkdtemp(prefix="release-check-", dir=OUT))
    for folder in ["src", "sql"]:
        shutil.copytree(ROOT / folder, work / folder, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(ROOT / "run_pipeline.py", work / "run_pipeline.py")
    fixture_dir = work / "fixtures"
    fixture_dir.mkdir()
    for name, raw in raw_files.items():
        shutil.copy2(raw, fixture_dir / (name + ".csv"))
    hook = work / "replay_hook"
    hook.mkdir()
    (hook / "sitecustomize.py").write_text('''from pathlib import Path
import requests
def archived_get(self, url, **kwargs):
    mapping = {"M.IT.B.L22.F.R.A.2250.EUR.N": "italy_household_deposit_rate", "M.IT.B.A2C.A.R.A.2250.EUR.N": "italy_household_mortgage_rate", "D.U2.EUR.4F.KR.DFR.LEV": "ecb_deposit_facility_rate"}
    key = url.rsplit("/", 1)[-1]
    if key not in mapping:
        raise RuntimeError("Unexpected network request in offline replay")
    response = requests.Response()
    response.status_code = 200
    response.url = url
    response.encoding = "utf-8"
    response._content = (Path(__file__).resolve().parents[1] / "fixtures" / (mapping[key] + ".csv")).read_bytes()
    return response
requests.Session.get = archived_get
''', encoding="utf-8")
    env = dict(os.environ, PYTHONPATH=str(hook), PYTHONIOENCODING="utf-8")
    run = subprocess.run([sys.executable, str(work / "run_pipeline.py")], cwd=work, env=env, capture_output=True, text=True, encoding="utf-8")
    (OUT / "pipeline_replay.log").write_text(run.stdout + run.stderr, encoding="utf-8")
    require(run.returncode == 0, "Replay failed; see pipeline_replay.log")
    metadata = json.loads((work / "data/metadata/pipeline_status.json").read_text())
    require(metadata["status"] == "success" and metadata["completed_steps"] == 6, "Incomplete replay")
    compared = []
    for relative in ["data/processed/banking_interest_rates_monthly.csv", "data/simulated/customer_portfolio.csv"] + [str(p.relative_to(ROOT)) for p in (ROOT / "data/analytics").glob("*.csv")]:
        pd.testing.assert_frame_equal(pd.read_csv(ROOT / relative), pd.read_csv(work / relative), check_dtype=False, atol=1e-9, rtol=0)
        compared.append(relative)
    failure_test = '''import importlib.util,json,sys
from pathlib import Path
p=Path(sys.argv[1]); spec=importlib.util.spec_from_file_location("pipeline",p/"run_pipeline.py"); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.METADATA_PATH=p/"failure_status.json"
(p/"fail.py").write_text("raise SystemExit(7)")
(p/"sentinel.py").write_text("from pathlib import Path; Path('should_not_exist').touch()")
m.STEPS=[("expected failure",p/"fail.py"),("must not run",p/"sentinel.py")]
result=m.main(); state=json.loads(m.METADATA_PATH.read_text())
assert result==7 and state["status"]=="failed" and state["completed_steps"]==0 and not (p/"should_not_exist").exists()
'''
    test_path = work / "check_failure.py"
    test_path.write_text(failure_test, encoding="utf-8")
    failure = subprocess.run([sys.executable, str(test_path), str(work)], cwd=work, capture_output=True, text=True)
    require(failure.returncode == 0, "Failure-stop check failed: " + failure.stderr)
    result = {"raw_to_processed": reconciliation, "daily_DFR_coverage": {"start": str(start.date()), "end": str(end.date()), "days": len(expected_days), "status": "PASS"}, "six_stage_archived_response_replay": "PASS", "live_network_extraction": "NOT_TESTED", "output_comparison": compared, "failure_stops_subsequent_steps": "PASS", "production_inputs": "UNCHANGED", "workspace": str(work.relative_to(ROOT)), "python": sys.version, "pandas": pd.__version__}
    (OUT / "release_checks.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
