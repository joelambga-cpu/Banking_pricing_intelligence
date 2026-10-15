SELECT
    period,
    deposit_rate_pct,
    mortgage_rate_pct,
    ecb_dfr_pct,
    deposit_gap_pp,
    mortgage_deposit_spread_pp,

    deposit_rate_pct
        - LAG(deposit_rate_pct) OVER (
            ORDER BY period
        ) AS deposit_rate_change_pp,

    mortgage_deposit_spread_pp
        - LAG(mortgage_deposit_spread_pp) OVER (
            ORDER BY period
        ) AS spread_change_pp

FROM interest_rates

ORDER BY period;