WITH monthly_regimes AS (

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
),

regime_changes AS (

    SELECT
        *,
        LAG(pricing_regime) OVER (
            ORDER BY period
        ) AS previous_regime

    FROM monthly_regimes
)

SELECT
    period,
    previous_regime,
    pricing_regime,
    deposit_rate_pct,
    mortgage_deposit_spread_pp,

    CASE
        WHEN pricing_regime = 'UNKNOWN'
             OR previous_regime = 'UNKNOWN'
            THEN 'DATA GAP'

        WHEN previous_regime IS NULL
            THEN 'START'

        WHEN previous_regime <> pricing_regime
            THEN 'REGIME CHANGE'

        ELSE 'UNCHANGED'
    END AS regime_status

FROM regime_changes

ORDER BY period;