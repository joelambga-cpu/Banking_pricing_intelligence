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

ORDER BY period;