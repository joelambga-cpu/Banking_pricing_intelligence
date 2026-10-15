WITH latest_market AS (

    SELECT
        period,
        deposit_rate_pct AS market_deposit_rate_pct,
        mortgage_deposit_spread_pp,
        deposit_gap_pp

    FROM interest_rates

    WHERE period = (
        SELECT MAX(period)
        FROM interest_rates
    )
),

customer_analysis AS (

    SELECT
        c.customer_id,
        c.segment,
        c.deposit_balance_eur,
        c.current_deposit_rate_pct,
        c.deposit_change_90d_pct,
        c.product_count,
        c.tenure_months,
        c.has_mortgage,

        m.market_deposit_rate_pct,

        m.market_deposit_rate_pct
            - c.current_deposit_rate_pct
            AS rate_gap_pp,

        CASE
            WHEN
                c.deposit_balance_eur >= 50000
                AND c.deposit_change_90d_pct <= -5
                AND (
                    m.market_deposit_rate_pct
                    - c.current_deposit_rate_pct
                ) >= 0.25

                THEN 'TARGET'

            ELSE 'NO TARGET'
        END AS pricing_action

    FROM customers c

    CROSS JOIN latest_market m
)

SELECT
    pricing_action,

    COUNT(*) AS customers,

    ROUND(
        SUM(deposit_balance_eur),
        2
    ) AS deposits_eur,

    ROUND(
        AVG(rate_gap_pp),
        2
    ) AS avg_rate_gap_pp,

    ROUND(
        AVG(deposit_change_90d_pct),
        2
    ) AS avg_deposit_change_90d_pct

FROM customer_analysis

GROUP BY pricing_action

ORDER BY deposits_eur DESC;