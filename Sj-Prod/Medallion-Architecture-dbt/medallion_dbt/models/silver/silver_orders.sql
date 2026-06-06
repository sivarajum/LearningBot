/*
  silver_orders.sql
  -----------------
  SILVER LAYER — Clean, validate, enrich bronze_orders.

  Transformations applied:
    1. Status normalisation  — status cast to UPPER for uniform values
    2. Status validation     — only accepted statuses pass through
    3. Amount validation     — negative amounts excluded
    4. Deduplication         — QUALIFY keeps latest ingest per order_id
    5. Enrichment            — order_year, order_month, order_quarter derived
    6. Revenue category      — small/medium/large order bucketing
*/

{{ config(materialized='table') }}

SELECT
    order_id,
    customer_id,
    product_id,
    order_date,
    amount,
    UPPER(status)                                                   AS status,
    EXTRACT('year'  FROM order_date)::INTEGER                       AS order_year,
    EXTRACT('month' FROM order_date)::INTEGER                       AS order_month,
    EXTRACT('quarter' FROM order_date)::INTEGER                     AS order_quarter,
    CASE
        WHEN amount <  50  THEN 'small'
        WHEN amount < 150  THEN 'medium'
        ELSE 'large'
    END                                                             AS order_size,
    _ingested_at,
    _source_file
FROM {{ ref('bronze_orders') }}
WHERE UPPER(status) IN ('PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED')
  AND amount > 0
  AND order_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY order_id
    ORDER BY _ingested_at DESC
) = 1
