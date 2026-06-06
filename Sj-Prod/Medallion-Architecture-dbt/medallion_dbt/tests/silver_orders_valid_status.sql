/*
  silver_orders_valid_status.sql
  ------------------------------
  SINGULAR TEST — Data Contract for Silver Orders status values.

  Asserts that every order in the Silver layer has a status from the
  canonical allowed set: PENDING, SHIPPED, DELIVERED, CANCELLED.

  A non-empty result set means the test FAILS.

  Why this matters:
    - Gold CLV model filters on status = 'DELIVERED'. An unexpected status
      value would silently corrupt business metrics.
    - Enforcing this at Silver ensures Gold can rely on a clean contract.
*/

SELECT
    order_id,
    status,
    _source_file,
    _ingested_at
FROM {{ ref('silver_orders') }}
WHERE status NOT IN ('PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED')
