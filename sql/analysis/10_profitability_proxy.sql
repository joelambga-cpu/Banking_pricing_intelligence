WITH latest_market AS (

    SELECT
        deposit_rate_pct AS market_deposit_rate_pct,
        mortgage_rate_pct

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
        c.current_deposit_rate_pct,

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

portfolio AS (

    SELECT
        SUM(deposit_balance_eur) AS total_deposits,

        SUM(
            deposit_balance_eur
            * current_deposit_rate_pct
        )
        / SUM(deposit_balance_eur)
            AS baseline_weighted_rate,

        SUM(
            deposit_balance_eur
            * (current_deposit_rate_pct + 0.25)
        )
        / SUM(deposit_balance_eur)
            AS blanket_weighted_rate,

        SUM(
            deposit_balance_eur
            *
            (
                current_deposit_rate_pct
                +
                CASE
                    WHEN is_target = 1
                    THEN 0.25
                    ELSE 0
                END
            )
        )
        / SUM(deposit_balance_eur)
            AS targeted_weighted_rate

    FROM customer_analysis
)

SELECT
    ROUND(baseline_weighted_rate, 3)
        AS baseline_deposit_rate_pct,

    ROUND(blanket_weighted_rate, 3)
        AS blanket_deposit_rate_pct,

    ROUND(targeted_weighted_rate, 3)
        AS targeted_deposit_rate_pct,

    ROUND(
        m.mortgage_rate_pct
        - baseline_weighted_rate,
        3
    ) AS baseline_spread_proxy_pp,

    ROUND(
        m.mortgage_rate_pct
        - blanket_weighted_rate,
        3
    ) AS blanket_spread_proxy_pp,

    ROUND(
        m.mortgage_rate_pct
        - targeted_weighted_rate,
        3
    ) AS targeted_spread_proxy_pp

FROM portfolio

CROSS JOIN latest_market m;