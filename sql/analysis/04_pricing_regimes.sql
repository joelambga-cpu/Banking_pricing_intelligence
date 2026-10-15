WITH pricing_regimes AS (

    SELECT
        period,
        deposit_rate_pct,
        mortgage_rate_pct,
        ecb_dfr_pct,
        deposit_gap_pp,
        mortgage_deposit_spread_pp,

        CASE
            WHEN deposit_gap_pp IS NULL
                 OR mortgage_deposit_spread_pp IS NULL
                THEN 'UNKNOWN'

            WHEN deposit_gap_pp < 0
                 AND mortgage_deposit_spread_pp < 1.00
                THEN 'CRITICAL PRESSURE'

            WHEN deposit_gap_pp < 0
                 AND mortgage_deposit_spread_pp >= 1.00
                THEN 'FUNDING PRESSURE'

            WHEN deposit_gap_pp >= 0
                 AND mortgage_deposit_spread_pp < 1.00
                THEN 'MARGIN PRESSURE'

            ELSE 'COMFORTABLE'
        END AS pricing_regime

    FROM interest_rates
)

SELECT
    pricing_regime,
    COUNT(*) AS months,
    ROUND(AVG(deposit_rate_pct), 2) AS avg_deposit_rate_pct,
    ROUND(AVG(mortgage_rate_pct), 2) AS avg_mortgage_rate_pct,
    ROUND(AVG(mortgage_deposit_spread_pp), 2) AS avg_spread_pp,
    ROUND(AVG(deposit_gap_pp), 2) AS avg_deposit_gap_pp

FROM pricing_regimes

GROUP BY pricing_regime

ORDER BY months DESC;