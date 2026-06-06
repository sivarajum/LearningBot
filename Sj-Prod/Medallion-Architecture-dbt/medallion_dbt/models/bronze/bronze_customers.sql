/*
  bronze_customers.sql
  --------------------
  BRONZE LAYER — Raw ingest of customers.csv.

  Design principles:
    - No business logic. Type casts only.
    - Preserve every source row (no filtering).
    - Add metadata columns: _ingested_at, _source_file.
    - Acts as the immutable "system of record" for customers.
*/

{{ config(materialized='table') }}

SELECT
    customer_id::VARCHAR                AS customer_id,
    name::VARCHAR                       AS name,
    email::VARCHAR                      AS email,
    country::VARCHAR                    AS country,
    signup_date::DATE                   AS signup_date,
    tier::VARCHAR                       AS tier,
    CURRENT_TIMESTAMP                   AS _ingested_at,
    'customers.csv'                     AS _source_file
FROM read_csv_auto('{{ env_var("RAW_DATA_PATH") }}/customers.csv')
