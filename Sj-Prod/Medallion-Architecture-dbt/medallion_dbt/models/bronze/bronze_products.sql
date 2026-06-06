/*
  bronze_products.sql
  -------------------
  BRONZE LAYER — Raw ingest of products.csv.

  price and cost stored as DOUBLE for financial computations in Gold layer.
*/

{{ config(materialized='table') }}

SELECT
    product_id::VARCHAR                 AS product_id,
    name::VARCHAR                       AS name,
    category::VARCHAR                   AS category,
    price::DOUBLE                       AS price,
    cost::DOUBLE                        AS cost,
    CURRENT_TIMESTAMP                   AS _ingested_at,
    'products.csv'                      AS _source_file
FROM read_csv_auto('{{ env_var("RAW_DATA_PATH") }}/products.csv')
