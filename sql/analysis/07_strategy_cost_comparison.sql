WITH latest_market AS (

    SELECT
        deposit_rate_pct AS market_deposit_rate_pct

    FROM interest_rates

    WHERE period = (
        SELECT MAX(period)
        FROM interest_rates
    )
),

customer_analysis AS (

    SELECT
        c.customer_id,
        c.deposit_balance_eur,

        CASE
            WHEN
                c.deposit_balance_eur >= 50000
                AND c.deposit_change_90d_pct <= -5
                AND (
                    m.market_deposit_rate_pct
                    - c.current_deposit_rate_pct
                ) >= 0.25
            THEN 1
            ELSE 0
        END AS is_target

    FROM customers c

    CROSS JOIN latest_market m
)

SELECT
    'BLANKET +25 BPS' AS strategy,
    COUNT(*) AS customers_affected,
    ROUND(SUM(deposit_balance_eur), 2) AS deposits_covered_eur,
    ROUND(SUM(deposit_balance_eur) * 0.0025, 2)
        AS estimated_annual_cost_eur

FROM customer_analysis

UNION ALL

SELECT
    'TARGETED +25 BPS' AS strategy,
    COUNT(*) AS customers_affected,
    ROUND(SUM(deposit_balance_eur), 2) AS deposits_covered_eur,
    ROUND(SUM(deposit_balance_eur) * 0.0025, 2)
        AS estimated_annual_cost_eur

FROM customer_analysis

WHERE is_target = 1;