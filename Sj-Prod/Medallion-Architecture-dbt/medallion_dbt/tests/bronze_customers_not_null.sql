/*
  bronze_customers_not_null.sql
  -----------------------------
  SINGULAR TEST — Data Contract for Bronze Customers.

  Asserts that no row has a NULL customer_id or NULL email.
  A non-empty result set means the test FAILS.

  Why this matters:
    - Bronze is the system of record. If primary keys are null here,
      downstream Silver deduplication cannot work correctly.
    - This test acts as an automated data contract check at ingestion time.
*/

SELECT
    customer_id,
    email,
    _source_file,
    _ingested_at
FROM {{ ref('bronze_customers') }}
WHERE customer_id IS NULL
   OR email IS NULL
