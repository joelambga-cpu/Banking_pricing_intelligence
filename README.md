# Banking Pricing Intelligence

A Python, SQL and Power BI portfolio project comparing broad and targeted deposit repricing using official ECB interest-rate series and a synthetic retail customer portfolio.

**Scope:** decision-support prototype. Customer records and retention responses are simulated; results are not evidence of realised customer retention or bank profitability.

## Business problem

How can a retail bank compare the cost and potential benefits of increasing deposit rates for all customers versus a selected group?

The project connects market-rate context, customer selection rules, repricing costs and retention scenarios in four Power BI report pages.

## Main findings

Results below refer to the project dataset covering **January 2023–August 2026** and **5,000 synthetic customers**. They are a reproducible snapshot, not live market quotes.

| Metric | Blanket +25 bps | Targeted +25 bps |
|---|---:|---:|
| Customers treated | 5,000 | 348 |
| Deposits covered | €229,423,572.50 | €48,638,727.34 |
| Estimated incremental annual cost | €573,558.93 | €121,596.82 |
| Simulated deposits retained — BASE | €2,453,706.23 | €1,297,184.73 |
| Annual cost per simulated euro retained — BASE | €0.2338 | €0.0937 |

Targeted repricing reduces estimated annual cost by **€451,962.11 (78.8%)**. Under the BASE assumptions, it retains less deposit volume in absolute terms but has approximately **59.9% lower cost per simulated euro retained**.

**Decision supported:** targeted repricing is a candidate for further testing when the objective is cost-efficient intervention. This comparison does not establish an optimal policy or demonstrate that a rate increase causes customers to retain deposits.

## Answers to the five business questions

The existing January 2023–August 2026 snapshot supports these conclusions. The [full business answers](docs/RISPOSTE_BUSINESS.md) document definitions, denominators, query references and limitations; [reproducible evidence](docs/evidence/business_answers.json) records source hashes and independent checks.

| Question | Answer supported by the project snapshot |
|---|---|
| How competitive are deposit rates? | The balance-weighted portfolio rate is 1.937%, approximately 52.3 bps below the 2.46% deposit benchmark. Product/maturity comparability is limited. |
| Which segments are most exposed to outflows? | Private has the highest relative exposure: 66.26% of customers have declining balances and its outflow proxy equals 4.88% of segment deposits. Affluent has the largest absolute proxy (€4.409 million). These are synthetic descriptive indicators. |
| What would a rate increase cost? | A +25 bps increase costs €573,558.93 annually across all customers versus €121,596.82 for the 348 eligible customers, assuming constant balances for one year. |
| Which segments should receive an adjustment? | Under a volume-oriented objective, examine eligible Affluent customers first (€27.013 million), with Private also a priority given its higher relative exposure (€19.390 million eligible). Apply eligibility individually; this is not an empirically optimal allocation. |
| What is the profitability impact? | The indicative mortgage/portfolio-deposit spread moves from 1.613 pp to 1.363 pp under blanket repricing or 1.560 pp under targeted repricing. This is not net interest margin or bank profit. |

Query 08 now includes five additional fields for segment exposure. Its original nine fields retain their snapshot values. The Power BI model has matching fields and ratio measures; native refresh and presentation of the new indicators remain to be checked.

## Power BI pages

| Page | Analytical purpose |
|---|---|
| Executive Overview | Compare repricing costs, portfolio indicators and market context |
| Segment Analysis | Locate target customers and deposits across Mass, Affluent and Private segments |
| Retention Scenarios | Compare potential retained volume and unit costs under three assumptions |
| Market & Regimes | Inspect rate history, monthly pricing regimes and regime transitions |

The report uses native Power BI visuals. Pages 3 and 4 preserve full comparisons rather than cross-filtering their visuals; page 2 supports segment selection.

## Data and methodology

### Official market-rate inputs

The extractor requests these ECB Data Portal series and saves dated raw responses plus processed files:

- [Deposits — MIR.M.IT.B.L22.F.R.A.2250.EUR.N](https://data.ecb.europa.eu/data/datasets/MIR/MIR.M.IT.B.L22.F.R.A.2250.EUR.N): monthly Italian household deposits with agreed maturity up to one year, new business.
- [Housing loans — MIR.M.IT.B.A2C.A.R.A.2250.EUR.N](https://data.ecb.europa.eu/data/datasets/MIR/MIR.M.IT.B.A2C.A.R.A.2250.EUR.N): monthly Italian household lending for house purchase.
- [ECB deposit facility rate — FM.D.U2.EUR.4F.KR.DFR.LEV](https://data.ecb.europa.eu/data/datasets/FM/FM.D.U2.EUR.4F.KR.DFR.LEV): DFR observations recorded by date.

The transformation selects the **last available DFR observation in each month**, not a monthly average. Deposits and housing-loan series are joined on common months. The project checkpoint records a user-run daily coverage check for January 2023–August 2026 with no missing days, duplicate dates, missing month ends or monthly mismatches. This confirmation applies to that snapshot; it has not been rerun during the business-answer analysis and does not guarantee future refresh coverage.

Derived indicators, in percentage points:

- Deposit gap = ECB DFR − deposit benchmark rate.
- Mortgage–deposit spread = housing-loan rate − deposit benchmark rate.

The deposit series is a specific product benchmark, not an average rate across all deposit products. Synthetic customers do not have matching product-maturity attributes; benchmark comparisons are illustrative.

### Synthetic customer portfolio

`src/generate/generate_customer_portfolio.py` generates 5,000 records using NumPy's `default_rng` with seed **42**.

| Segment | Assignment probability | Balance median parameter | Rate mean parameter | 90-day change mean parameter |
|---|---:|---:|---:|---:|
| Mass | 70% | €12,000 | 1.65% | −1% |
| Affluent | 25% | €65,000 | 1.95% | −2% |
| Private | 5% | €250,000 | 2.15% | −3% |

Balances follow segment-specific lognormal distributions. Rates and deposit changes are sampled separately from normal distributions, then rounded and clipped. The resulting segment counts are 3,528 Mass, 1,229 Affluent and 243 Private customers.

These assumptions influence the analytical results. Within segments, the generator does not encode a causal link between remuneration and outflows. Reproduction requires unchanged code, random-call order and a compatible dependency environment, not merely the seed.

### Target selection and repricing

A customer is selected only when all three conditions hold:

1. Deposit balance ≥ €50,000.
2. Deposit change over 90 days ≤ −5%.
3. Latest market deposit benchmark − customer rate ≥ 0.25 percentage points.

Both strategies apply **+25 basis points**. Estimated incremental annual cost is:

```text
Deposits covered × 0.0025
```

This assumes constant balances and a full year of repricing. Selection thresholds are illustrative business rules, not empirically optimised cutoffs.

### Retention scenarios

For customers with declining deposits:

```text
Outflow proxy = deposit balance × abs(90-day percentage change) / 100
Simulated deposits retained = outflow proxy × scenario coefficient
Cost per euro retained = annual repricing cost / simulated deposits retained
```

| Scenario | Assumed share of outflow proxy avoided |
|---|---:|
| CONSERVATIVE | 10% |
| BASE | 25% |
| OPTIMISTIC | 40% |

The proxy is not a measured historical cash outflow: balance and percentage change are generated separately. Scenario coefficients apply to deposit amounts, not customer counts, and are not estimated retention probabilities.

The same coefficient applies to both strategies. Consequently, the relative unit-cost advantage is constant across these scenarios by construction, apart from rounding. Scenarios are alternatives and must not be summed.

### Pricing regimes

| | Mortgage–deposit spread < 1 pp | Mortgage–deposit spread ≥ 1 pp |
|---|---|---|
| ECB–deposit gap < 0 | CRITICAL PRESSURE | FUNDING PRESSURE |
| ECB–deposit gap ≥ 0 | MARGIN PRESSURE | COMFORTABLE |

These are project-defined labels, not regulatory categories or bank-risk diagnoses. Missing inputs produce `UNKNOWN`. A comparison involving `UNKNOWN` produces `DATA GAP`, rather than a regime change.

The validated snapshot contains 44 monthly observations and 14 regime changes: 17 months of MARGIN PRESSURE, 13 FUNDING PRESSURE, 11 CRITICAL PRESSURE and 3 COMFORTABLE.

## Architecture and stack

**Python · pandas · NumPy · requests · SQL · SQLite · Power BI**

ECB API responses are transformed into monthly market inputs. A separate generator creates the synthetic customer portfolio. Both sources are loaded into SQLite, validated, analysed with SQL and exported as CSVs consumed by Power BI.

Key project locations:

- `src/extract`, `src/transform`, `src/generate`, `src/load`: input preparation and loading.
- `src/quality/validate_data.py`: source-data checks and database reconciliation.
- `sql/analysis`: customer, cost, segment, retention and regime queries.
- `src/export/export_analytics.py`: seven analytical CSV exports.
- `data/raw`, `data/processed`, `data/simulated`, `data/database`, `data/analytics`: data stages.
- `dashboard/`: report assets.
- `run_pipeline.py`: pipeline orchestration.

## Running the project

From the project root, create and activate an environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

To validate existing data and regenerate analytical exports without downloading rates or regenerating customers:

```powershell
python src/quality/validate_data.py
```

Only after validation succeeds:

```powershell
python src/export/export_analytics.py
```

For a complete refresh:

```powershell
python run_pipeline.py
```

The configured order is extraction → transformation → customer generation → database load → validation → analytical exports. Subprocess failures stop subsequent steps. Pipeline metadata records running, failed or successful execution.

A full run fetches the latest available source data and can change the snapshot and results. Running validation/export separately does not update the full-pipeline status file.

Open the Power BI project with its report and semantic-model folders kept together. Point its CSV sources to the local project location, preserve the explicit `en-US` numeric parsing in Power Query, and refresh.

## Validation status

The strengthened validator and all seven exports were successfully executed on the local project. The earlier report refresh was confirmed by the user. Native refresh and visual acceptance of the newly extended Segment Analysis table remain pending.

Implemented checks cover required fields, non-empty datasets, valid monthly dates, unique and consecutive months, finite numeric values, gap/spread identities, customer identifiers and domains, and reconciliation of all required source columns against SQLite. The validator was also exercised against deliberately invalid fixtures.

The revised orchestrator passed a six-stage isolated replay using archived ECB HTTP response bodies. The recreated monthly dataset, synthetic customers and seven exports matched the existing snapshot; a failure test verified that subsequent steps stop. This verifies archived-input reproducibility, not live ECB connectivity. Export files are overwritten sequentially; a failed export run can leave files from different runs. Existing files are not automatically removed when validation fails. See [release-check evidence](docs/evidence/release_checks.json).

## Interpretation limits and remaining work

- Customer behaviour and retention responses are synthetic; no causal retention effect is established.
- Annual costs are compared with retained amounts derived from a 90-day change proxy. Their ratio is not ROI or net profit, and retained-balance persistence is not modelled.
- The mortgage–deposit rate difference is a gross benchmark spread, not a bank's net interest margin.
- Refreshes may revise market history. Pin dependency versions and retain source snapshots for exact reproducibility.
- Raw-to-processed reconciliation and snapshot-specific daily DFR coverage passed locally. Live network extraction was not rerun during release checks.
- Final screenshots and a walkthrough should reflect the latest manually edited Power BI report.

### Business-answer verification

Run `python src/quality/verify_business_answers.py` to reproduce queries 07/08/10 against the existing database and independently recompute results from the customer CSV using decimal arithmetic. After all checks pass, this writes `docs/evidence/business_answers.json` and updates only the segment export. It does not refresh ECB data, regenerate customers or validate native Power BI rendering.

The authoritative report location confirmed by the user is `C:\Users\joela\Downloads\BankingPricingIntelligence_QuattroPagine`. Its seven CSV source paths have been aligned with the current project directory. Original model definitions are retained in the local backup `docs/evidence/model_before_business_answers.zip`; exclude this machine-specific backup from the publication package.

### Presentation and release

The [English case study and two-minute walkthrough](docs/CASE_STUDY_EN.md) explain the decision, method, findings and limitations. The [release notes](docs/RELEASE_NOTES_EN.md) distinguish completed checks from native Power BI acceptance and publication still pending.
