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
        c.current_deposit_rate_pct,
        c.deposit_change_90d_pct,

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
            THEN 1
            ELSE 0
        END AS is_target

    FROM customers c

    CROSS JOIN latest_market m
)

SELECT
    segment,

    COUNT(*) AS total_customers,

    SUM(is_target) AS target_customers,

    ROUND(
        100.0 * SUM(is_target) / COUNT(*),
        2
    ) AS target_customer_pct,

    ROUND(
        SUM(deposit_balance_eur),
        2
    ) AS total_deposits_eur,

    ROUND(
        SUM(
            CASE
                WHEN is_target = 1
                THEN deposit_balance_eur
                ELSE 0
            END
        ),
        2
    ) AS target_deposits_eur,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN is_target = 1
                THEN deposit_balance_eur
                ELSE 0
            END
        )
        / NULLIF(SUM(deposit_balance_eur), 0),
        2
    ) AS target_deposit_pct,

    ROUND(
        AVG(
            CASE
                WHEN is_target = 1
                THEN deposit_change_90d_pct
            END
        ),
        2
    ) AS target_avg_outflow_90d_pct,

    ROUND(
        SUM(
            CASE
                WHEN is_target = 1
                THEN deposit_balance_eur
                ELSE 0
            END
        ) * 0.0025,
        2
    ) AS targeted_25bps_cost_eur,

    -- Exposure across ALL customers in the segment, not only eligible targets.
    SUM(CASE WHEN deposit_change_90d_pct < 0 THEN 1 ELSE 0 END)
        AS declining_customers,

    ROUND(
        100.0 * SUM(CASE WHEN deposit_change_90d_pct < 0 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0), 2
    ) AS declining_customer_pct,

    -- Illustrative balance-change proxy; not an observed cash flow.
    ROUND(SUM(
        CASE WHEN deposit_change_90d_pct < 0
            THEN deposit_balance_eur * (-deposit_change_90d_pct) / 100.0
            ELSE 0 END
    ), 2) AS outflow_proxy_eur,

    ROUND(
        100.0 * SUM(
            CASE WHEN deposit_change_90d_pct < 0
                THEN deposit_balance_eur * (-deposit_change_90d_pct) / 100.0
                ELSE 0 END
        ) / NULLIF(SUM(deposit_balance_eur), 0), 2
    ) AS outflow_proxy_pct_of_deposits,

    ROUND(SUM(
        CASE WHEN is_target = 1
            THEN deposit_balance_eur * (-deposit_change_90d_pct) / 100.0
            ELSE 0 END
    ), 2) AS target_outflow_proxy_eur

FROM customer_analysis

GROUP BY segment

ORDER BY target_deposits_eur DESC;
