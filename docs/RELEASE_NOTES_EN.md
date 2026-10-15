# Version 1 — release candidate

Prepared: 8 October 2026. Status: local candidate for review; not published.

## Contents

- Python preparation and validation, SQL analyses and a reproducible snapshot.
- Four-page Power BI project under `dashboard/` in the distribution package.
- English case study and two-minute walkthrough.
- Five detailed business answers, supporting evidence and file hashes.

## Checks completed

- Three archived source files reconciled with processed series.
- Daily DFR coverage confirmed for 1 January 2023–31 August 2026 (1,339 days).
- All six pipeline stages replayed in an isolated copy using archived HTTP responses.
- Recreated market dataset, customer portfolio and seven analytical exports matched the reference snapshot.
- Failure handling stopped subsequent stages and recorded a failed status.
- Business calculations independently reconciled with decimal arithmetic.
- Segment Analysis table extended to show all-customer exposure alongside eligibility and cost. JSON readability, field references and total configured column width checked.

The replay does not test live ECB network access. Structural report checks do not verify native Power BI rendering or DAX evaluation.

## Local setup

Create a Python environment and install `requirements.txt`. Use the supplied snapshot for initial review; a full refresh can change the results. The database is included in this local review package and can also be rebuilt by the pipeline.

The packaged Power BI queries use `C:\banking-pricing-intelligence` as an example project root. Before refreshing, replace that prefix in the seven source queries with the actual root of the extracted project. Keep each CSV suffix unchanged. Preserve `en-US` numeric parsing and the 14-column import for SegmentAnalysis.

Open `dashboard/bankingpricingintelligence.pbip` with its adjacent report and semantic-model directories. Refresh the model before inspecting visuals; local cache files are excluded from the package.

## Native acceptance still required

1. Open and refresh without model or source errors.
2. Confirm the eight-column Segment Analysis table is readable, with no clipped headings or unexpected scrolling. Check Private 66.26% declining and 4.88% proxy/deposits; Affluent proxy €4.409 million.
3. Confirm cost cards match €573,558.93 blanket and €121,596.82 targeted, and scenario totals are not summed across assumptions.
4. Check all four pages, navigation and intended filter behaviour; retain four screenshots from the final report.

Power BI launched during preparation, but the computer-control tool could not obtain a usable screenshot or accessibility tree. Native acceptance and screenshots are therefore explicitly pending.

## Publication

Choose destination and visibility before publication. A source repository can contain code, documentation, report definitions and the reviewed snapshot; local environments, caches, test workspaces, machine-specific backups and personal absolute paths are excluded from this package.

The report retains its existing mixed-language page content; the case study and walkthrough are in English. A fully English report requires an editorial pass before presentation to an English-only audience.

Do not label the candidate as a fully validated release until native acceptance is complete. External publication has not been performed.
