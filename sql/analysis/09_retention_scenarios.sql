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
        c.segment,
        c.deposit_balance_eur,
        c.deposit_change_90d_pct,

        CASE
            WHEN c.deposit_change_90d_pct < 0
            THEN
                c.deposit_balance_eur
                * ABS(c.deposit_change_90d_pct)
                / 100.0
            ELSE 0
        END AS outflow_proxy_eur,

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
),

strategies AS (

    SELECT
        'BLANKET' AS strategy,
        customer_id,
        deposit_balance_eur,
        outflow_proxy_eur
    FROM customer_analysis

    UNION ALL

    SELECT
        'TARGETED' AS strategy,
        customer_id,
        deposit_balance_eur,
        outflow_proxy_eur
    FROM customer_analysis
    WHERE is_target = 1
),

scenarios AS (

    SELECT 'CONSERVATIVE' AS scenario, 0.10 AS retention_rate
    UNION ALL
    SELECT 'BASE', 0.25
    UNION ALL
    SELECT 'OPTIMISTIC', 0.40
)

SELECT
    s.strategy,
    sc.scenario,

    COUNT(*) AS customers_treated,

    ROUND(
        SUM(s.deposit_balance_eur) * 0.0025,
        2
    ) AS annual_repricing_cost_eur,

    ROUND(
        SUM(s.outflow_proxy_eur),
        2
    ) AS outflow_proxy_eur,

    ROUND(
        SUM(s.outflow_proxy_eur)
        * sc.retention_rate,
        2
    ) AS estimated_deposits_retained_eur,

    ROUND(
        (
            SUM(s.deposit_balance_eur) * 0.0025
        )
        /
        NULLIF(
            SUM(s.outflow_proxy_eur)
            * sc.retention_rate,
            0
        ),
        4
    ) AS cost_per_eur_retained

FROM strategies s

CROSS JOIN scenarios sc

GROUP BY
    s.strategy,
    sc.scenario,
    sc.retention_rate

ORDER BY
    sc.retention_rate,
    s.strategy;