/*
  gold_customer_lifetime_value.sql
  --------------------------------
  GOLD LAYER — Customer Lifetime Value (CLV) aggregation.

  Business question: "What is the total revenue and order behaviour for each customer?"

  Design decisions:
    - Only DELIVERED orders count toward CLV (business rule)
    - LEFT JOIN so customers with no delivered orders still appear (CLV = 0)
    - COALESCE handles customers with zero delivered orders
    - Tenure days = span between first and last delivered order
*/

{{ config(materialized='table') }}

SELECT
    c.customer_id,
    c.name,
    c.tier,
    c.tier_rank,
    c.country,
    c.signup_date,
    c.customer_age_days,
    -- Order metrics (delivered only)
    COALESCE(COUNT(o.order_id), 0)                                  AS total_orders,
    COALESCE(ROUND(SUM(o.amount), 2), 0)                            AS lifetime_value,
    COALESCE(ROUND(AVG(o.amount), 2), 0)                            AS avg_order_value,
    MIN(o.order_date)                                               AS first_order_date,
    MAX(o.order_date)                                               AS last_order_date,
    COALESCE(
        DATEDIFF('day', MIN(o.order_date), MAX(o.order_date)),
        0
    )                                                               AS customer_tenure_days,
    -- Value segment
    CASE
        WHEN COALESCE(SUM(o.amount), 0) >= 1000 THEN 'high_value'
        WHEN COALESCE(SUM(o.amount), 0) >= 300  THEN 'mid_value'
        ELSE 'low_value'
    END                                                             AS clv_segment
FROM {{ ref('silver_customers') }} c
LEFT JOIN {{ ref('silver_orders') }} o
    ON c.customer_id = o.customer_id
    AND o.status = 'DELIVERED'
GROUP BY
    c.customer_id,
    c.name,
    c.tier,
    c.tier_rank,
    c.country,
    c.signup_date,
    c.customer_age_days
