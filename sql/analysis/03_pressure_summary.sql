WITH classified_months AS (

    SELECT
        period,
        deposit_rate_pct,
        mortgage_rate_pct,
        ecb_dfr_pct,
        deposit_gap_pp,
        mortgage_deposit_spread_pp,

        CASE
            WHEN deposit_gap_pp < 0
                 AND mortgage_deposit_spread_pp < 1.00
                THEN 'HIGH PRESSURE'

            WHEN deposit_gap_pp < 0
                THEN 'MEDIUM PRESSURE'

            ELSE 'LOW PRESSURE'
        END AS pricing_pressure

    FROM interest_rates
)

SELECT
    pricing_pressure,
    COUNT(*) AS months,
    ROUND(AVG(deposit_rate_pct), 2) AS avg_deposit_rate_pct,
    ROUND(AVG(mortgage_deposit_spread_pp), 2) AS avg_spread_pp,
    ROUND(AVG(deposit_gap_pp), 2) AS avg_deposit_gap_pp

FROM classified_months

GROUP BY pricing_pressure

ORDER BY
    CASE pricing_pressure
        WHEN 'HIGH PRESSURE' THEN 1
        WHEN 'MEDIUM PRESSURE' THEN 2
        WHEN 'LOW PRESSURE' THEN 3
    END;