"""Reproduce business-answer evidence from the existing snapshot, without refresh.

Run from any directory: python src/quality/verify_business_answers.py
Reads SQLite in read-only mode. Independently checks segment SQL against the
customer CSV using Decimal, preserves the original nine export columns, and
writes reviewed evidence plus the extended segment export only after checks pass.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import csv
import hashlib
import json
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
D = Decimal


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def rounded(value, digits=2):
    return float(value.quantize(D(10) ** -digits, rounding=ROUND_HALF_UP))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    customer_path = ROOT / "data/simulated/customer_portfolio.csv"
    rate_path = ROOT / "data/processed/banking_interest_rates_monthly.csv"
    db_path = ROOT / "data/database/banking_pricing.db"
    export_path = ROOT / "data/analytics/segment_pricing_analysis.csv"
    customers = read_csv(customer_path)
    rates = read_csv(rate_path)
    latest = max(rates, key=lambda row: row["period"])
    market = D(latest["deposit_rate_pct"])
    require(len({r["customer_id"] for r in customers}) == len(customers), "Duplicate customer IDs")
    require({r["segment"] for r in customers} == {"Mass", "Affluent", "Private"}, "Unexpected segments")
    queries = {}
    with sqlite3.connect(db_path.as_uri() + "?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        for name in ["07_strategy_cost_comparison", "08_segment_pricing_analysis", "10_profitability_proxy"]:
            sql = (ROOT / f"sql/analysis/{name}.sql").read_text(encoding="utf-8-sig")
            queries[name] = [dict(row) for row in connection.execute(sql)]
        require(connection.execute("select count(*) from customers").fetchone()[0] == len(customers), "Population mismatch")
        require(connection.execute("select max(period) from interest_rates").fetchone()[0] == latest["period"], "Market period mismatch")

    checked = []
    old = {r["segment"]: r for r in read_csv(export_path)}
    original_columns = ["segment", "total_customers", "target_customers", "target_customer_pct", "total_deposits_eur", "target_deposits_eur", "target_deposit_pct", "target_avg_outflow_90d_pct", "targeted_25bps_cost_eur"]
    all_balances = D(0)
    weighted_sum = D(0)
    target_balances = D(0)
    total_proxy = D(0)
    target_proxy = D(0)
    target_count = 0
    for result in queries["08_segment_pricing_analysis"]:
        rows = [r for r in customers if r["segment"] == result["segment"]]
        balance = lambda r: D(r["deposit_balance_eur"])
        change = lambda r: D(r["deposit_change_90d_pct"])
        targets = [r for r in rows if balance(r) >= 50000 and change(r) <= -5 and market - D(r["current_deposit_rate_pct"]) >= D("0.25")]
        declining = [r for r in rows if change(r) < 0]
        deposits = sum((balance(r) for r in rows), D(0))
        eligible = sum((balance(r) for r in targets), D(0))
        proxy = sum((balance(r) * -change(r) / 100 for r in declining), D(0))
        eligible_proxy = sum((balance(r) * -change(r) / 100 for r in targets), D(0))
        expected = {
            "total_customers": len(rows), "target_customers": len(targets),
            "target_customer_pct": rounded(D(100) * len(targets) / len(rows)),
            "total_deposits_eur": rounded(deposits), "target_deposits_eur": rounded(eligible),
            "target_deposit_pct": rounded(D(100) * eligible / deposits),
            "target_avg_outflow_90d_pct": rounded(sum((change(r) for r in targets), D(0)) / len(targets)) if targets else None,
            "targeted_25bps_cost_eur": rounded(eligible * D("0.0025")),
            "declining_customers": len(declining),
            "declining_customer_pct": rounded(D(100) * len(declining) / len(rows)),
            "outflow_proxy_eur": rounded(proxy),
            "outflow_proxy_pct_of_deposits": rounded(D(100) * proxy / deposits),
            "target_outflow_proxy_eur": rounded(eligible_proxy),
        }
        for key, value in expected.items():
            require(result[key] == value, f"CSV/SQL mismatch: {result['segment']} {key}")
        for key in original_columns[1:]:
            require(D(str(result[key])) == D(old[result["segment"]][key]), f"Original export changed: {key}")
        checked.append(result["segment"])
        all_balances += deposits
        target_balances += eligible
        total_proxy += proxy
        target_proxy += eligible_proxy
        target_count += len(targets)
        weighted_sum += sum((balance(r) * D(r["current_deposit_rate_pct"]) for r in rows), D(0))

    baseline = weighted_sum / all_balances
    blanket = baseline + D("0.25")
    targeted = baseline + D("0.25") * target_balances / all_balances
    mortgage = D(latest["mortgage_rate_pct"])
    expected_profit = dict(zip(
        ["baseline_deposit_rate_pct", "blanket_deposit_rate_pct", "targeted_deposit_rate_pct", "baseline_spread_proxy_pp", "blanket_spread_proxy_pp", "targeted_spread_proxy_pp"],
        [rounded(x, 3) for x in [baseline, blanket, targeted, mortgage-baseline, mortgage-blanket, mortgage-targeted]]))
    require(queries["10_profitability_proxy"] == [expected_profit], "Profitability query mismatch")
    for result, deposits, count in zip(queries["07_strategy_cost_comparison"], [all_balances, target_balances], [len(customers), target_count]):
        require(result["customers_affected"] == count and result["deposits_covered_eur"] == rounded(deposits) and result["estimated_annual_cost_eur"] == rounded(deposits * D("0.0025")), "Strategy reconciliation failed")

    sources = [customer_path, rate_path, db_path] + [ROOT / f"sql/analysis/{name}.sql" for name in queries]
    evidence = {
        "scope": "Existing local snapshot; no external refresh or native Power BI validation",
        "market_period": [min(r["period"] for r in rates), latest["period"]],
        "months": len(rates), "customers": len(customers), "latest_market": latest,
        "queries": queries,
        "additional_results": {
            "portfolio_weighted_rate_pct": float(baseline),
            "benchmark_minus_portfolio_pp": float(market-baseline),
            "outflow_proxy_eur": rounded(total_proxy),
            "target_outflow_proxy_eur": rounded(target_proxy),
            "blanket_retained_base_eur": rounded(total_proxy * D("0.25")),
            "targeted_retained_base_eur": rounded(target_proxy * D("0.25")),
        },
        "validation": {"independent_decimal_recomputation": "PASS", "original_nine_segment_columns": "UNCHANGED", "segments_checked": checked},
        "sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
    }
    output = ROOT / "docs/evidence"
    output.mkdir(parents=True, exist_ok=True)
    (output / "business_answers.json").write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    with export_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(queries["08_segment_pricing_analysis"][0]))
        writer.writeheader()
        writer.writerows(queries["08_segment_pricing_analysis"])
    print(json.dumps(evidence, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
