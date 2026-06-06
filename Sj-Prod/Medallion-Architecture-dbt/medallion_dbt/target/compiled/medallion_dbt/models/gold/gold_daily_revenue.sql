/*
  gold_daily_revenue.sql
  ----------------------
  GOLD LAYER — Daily revenue trend for time-series analysis.

  Business question: "How is daily revenue trending over time?"

  Design decisions:
    - Only DELIVERED orders represent confirmed revenue
    - 7-day rolling average smooths short-term noise
    - revenue_vs_prev_day enables day-over-day % change calculation in BI tools
    - Cumulative revenue supports "revenue to date" dashboards
*/



WITH daily AS (
    SELECT
        order_date,
        EXTRACT('year'  FROM order_date)::INTEGER   AS order_year,
        EXTRACT('month' FROM order_date)::INTEGER   AS order_month,
        EXTRACT('quarter' FROM order_date)::INTEGER AS order_quarter,
        EXTRACT('dow'   FROM order_date)::INTEGER   AS day_of_week,
        COUNT(order_id)                             AS order_count,
        ROUND(SUM(amount), 2)                       AS daily_revenue,
        ROUND(AVG(amount), 2)                       AS avg_order_value,
        COUNT(DISTINCT customer_id)                 AS unique_customers
    FROM "warehouse"."main_silver"."silver_orders"
    WHERE status = 'DELIVERED'
    GROUP BY 1, 2, 3, 4, 5
)

SELECT
    order_date,
    order_year,
    order_month,
    order_quarter,
    day_of_week,
    order_count,
    daily_revenue,
    avg_order_value,
    unique_customers,
    -- 7-day rolling average (smoothed trend)
    ROUND(
        AVG(daily_revenue) OVER (
            ORDER BY order_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ),
        2
    )                                                               AS revenue_7d_avg,
    -- Day-over-day change
    ROUND(
        daily_revenue - LAG(daily_revenue) OVER (ORDER BY order_date),
        2
    )                                                               AS revenue_vs_prev_day,
    -- Month-to-date revenue
    ROUND(
        SUM(daily_revenue) OVER (
            PARTITION BY order_year, order_month
            ORDER BY order_date
            ROWS UNBOUNDED PRECEDING
        ),
        2
    )                                                               AS mtd_revenue,
    -- Cumulative all-time revenue
    ROUND(
        SUM(daily_revenue) OVER (
            ORDER BY order_date
            ROWS UNBOUNDED PRECEDING
        ),
        2
    )                                                               AS cumulative_revenue
FROM daily
ORDER BY order_date