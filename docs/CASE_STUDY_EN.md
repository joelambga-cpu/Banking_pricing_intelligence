# Banking Pricing Intelligence
## Comparing broad and targeted deposit repricing

### Purpose

Help a retail bank compare the cost of increasing deposit rates for all customers with a targeted increase for selected customers, while making the trade-off between intervention cost and simulated deposit retention explicit.

The project combines archived ECB interest-rate data, a synthetic customer portfolio and transparent business rules. It is a decision-support prototype, not a predictive retention model or a measure of bank profitability.

### Business questions

1. How competitive is the portfolio's deposit remuneration against a market benchmark?
2. Which customer segments show the greatest exposure to declining deposits?
3. What would a 25-basis-point increase cost?
4. Which segments warrant attention first under the proposed eligibility rules?
5. How would repricing affect funding costs and an indicative lending/deposit spread?

### Data and approach

The market snapshot covers January 2023–August 2026. The portfolio contains 5,000 synthetic customers across Mass, Affluent and Private segments, with €229.424 million in deposits. Python prepares inputs and validates data; SQLite and SQL produce analytical outputs; Power BI presents four report pages.

Target eligibility requires all three conditions: a deposit balance of at least €50,000, a 90-day deposit change of −5% or below, and a gap of at least 0.25 percentage points between the market deposit benchmark and the customer's rate.

Both strategies apply a 25-basis-point increase. Annual incremental cost equals affected deposits multiplied by 0.0025, assuming constant balances for a full year.

For customers with declining balances, the outflow proxy equals balance multiplied by the absolute negative 90-day percentage change. This is an illustrative proxy, not a measured cash flow. Retention scenarios assume that 10%, 25% or 40% of that proxy is avoided.

### Findings

The portfolio's balance-weighted deposit rate is **1.937%**, approximately **52.3 basis points below** the August 2026 deposit benchmark of 2.46%. The comparison is illustrative because the benchmark's product maturity is not represented in the synthetic portfolio.

**Private has the greatest relative exposure:** 66.26% of its customers have declining balances, and its outflow proxy represents 4.88% of segment deposits. **Affluent has the largest absolute proxy**, at €4.409 million, compared with €3.464 million for Private and €1.942 million for Mass.

| Strategy | Customers affected | Deposits affected | Annual incremental cost | Simulated deposits retained — BASE |
|---|---:|---:|---:|---:|
| Blanket +25 bps | 5,000 | €229,423,572.50 | €573,558.93 | €2,453,706.23 |
| Targeted +25 bps | 348 | €48,638,727.34 | €121,596.82 | €1,297,184.73 |

Targeted repricing reduces annual incremental cost by **€451,962.11, or 78.8%**, while retaining less simulated deposit volume in absolute terms under the BASE scenario. Its annual cost per simulated euro retained is approximately €0.0937, compared with €0.2338 for blanket repricing. This ratio is not ROI: it compares an annual cost with a retained amount derived from a 90-day change proxy.

Under a volume-oriented intervention objective, **Affluent is the first segment to examine**, with €27.013 million of eligible deposits. Private contributes €19.390 million and warrants attention given its greater relative exposure. Mass contributes €2.235 million. Eligibility remains customer-specific; this prioritisation is conditional on the project assumptions.

With the mortgage benchmark fixed at 3.55%, the indicative spread over the weighted portfolio deposit rate falls from **1.613 percentage points** to **1.363** under blanket repricing or **1.560** under targeted repricing. The project does not model full net interest margin or net profit.

### Decision supported

Targeted repricing is a candidate for further testing when cost efficiency is the main objective. The prototype makes its lower cost and lower simulated retained volume visible together. It does not establish an optimal allocation or demonstrate that a rate increase causes customers to keep their deposits.

### Verification

The three archived market-source files reconcile with their processed series. Daily DFR coverage is complete over the 44-month analytical snapshot. All six pipeline stages were executed in an isolated replay using archived HTTP response bodies; the monthly dataset, synthetic portfolio and seven analytical exports matched the project snapshot. Failure handling also stopped subsequent stages as intended.

This replay tests source parsing and downstream execution, not live ECB connectivity. Business-answer calculations were independently checked against the customer CSV using decimal arithmetic. Native Power BI refresh and final visual review remain separate release checks.

### Limitations

- Customers and retention responses are simulated; segment differences partly reflect generator assumptions.
- Market and customer product characteristics are not fully comparable.
- Retention scenario coefficients are assumptions, not estimated response probabilities. Using the same coefficient for both strategies makes their relative unit-cost advantage constant across scenarios by construction.
- Balance persistence, operating expenses, credit losses, fees and the full funding and loan mix are outside scope.
- The report is a dated snapshot. A refresh may revise history and change eligibility and results.

### Evidence

- [Detailed answers and definitions](RISPOSTE_BUSINESS.md)
- [Business-answer evidence](evidence/business_answers.json)
- [Release-check evidence](evidence/release_checks.json)
- [SQL analysis](../sql/analysis/)
- [Project methodology and reproduction instructions](../README.md)

## Two-minute walkthrough

“This project explores a practical banking question: should a bank raise deposit rates for everyone, or focus on a selected group of customers?

I combined ECB market-rate data with a synthetic portfolio of 5,000 customers. I used Python for preparation and validation, SQL for the business logic, and Power BI to present the results.

The report first shows the overall cost comparison, then examines customer segments, tests retention assumptions and places the decision in its market-rate context.

Under the project rules, 348 customers qualify for a targeted increase. Raising their rates by 25 basis points costs about €122,000 per year, compared with €574,000 for the whole portfolio. The targeted strategy costs less, but also retains less simulated deposit volume in the BASE scenario.

The segment analysis adds an important distinction: Private shows the highest relative exposure, while Affluent has the largest eligible deposit volume. That means priority depends on the decision objective, not just the number of customers.

The main value of the project is a transparent comparison. It shows what each option costs, what the scenarios assume, and where the evidence stops. Because customer behaviour is simulated, the result is a basis for testing a policy, not proof of a retention effect or higher bank profit.”
