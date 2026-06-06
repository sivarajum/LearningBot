/*
  gold_product_performance.sql
  ----------------------------
  GOLD LAYER — Revenue and profitability metrics per product.

  Business question: "Which products generate the most revenue and margin?"

  Design decisions:
    - Only DELIVERED orders count as realised revenue
    - Profit = (price - cost) × quantity sold; uses product cost from silver_products
    - Revenue rank helps BI tools quickly identify top performers
*/

{{ config(materialized='table') }}

SELECT
    p.product_id,
    p.name                                                          AS product_name,
    p.category,
    p.price_tier,
    p.price,
    p.cost,
    p.gross_margin_pct,
    -- Sales metrics
    COALESCE(COUNT(o.order_id), 0)                                  AS total_orders,
    COALESCE(ROUND(SUM(o.amount), 2), 0)                            AS total_revenue,
    COALESCE(ROUND(AVG(o.amount), 2), 0)                            AS avg_sale_price,
    -- Estimated profit (orders × margin per unit)
    COALESCE(
        ROUND(COUNT(o.order_id) * (p.price - p.cost), 2),
        0
    )                                                               AS estimated_profit,
    MIN(o.order_date)                                               AS first_sale_date,
    MAX(o.order_date)                                               AS last_sale_date,
    -- Revenue rank within category
    RANK() OVER (
        PARTITION BY p.category
        ORDER BY COALESCE(SUM(o.amount), 0) DESC
    )                                                               AS revenue_rank_in_category,
    -- Overall revenue percentile
    ROUND(
        PERCENT_RANK() OVER (
            ORDER BY COALESCE(SUM(o.amount), 0)
        ) * 100,
        1
    )                                                               AS revenue_percentile
FROM {{ ref('silver_products') }} p
LEFT JOIN {{ ref('silver_orders') }} o
    ON p.product_id = o.product_id
    AND o.status = 'DELIVERED'
GROUP BY
    p.product_id,
    p.name,
    p.category,
    p.price_tier,
    p.price,
    p.cost,
    p.gross_margin_pct
