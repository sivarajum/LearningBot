/*
  bronze_products.sql
  -------------------
  BRONZE LAYER — Raw ingest of products.csv.

  price and cost stored as DOUBLE for financial computations in Gold layer.
*/



SELECT
    product_id::VARCHAR                 AS product_id,
    name::VARCHAR                       AS name,
    category::VARCHAR                   AS category,
    price::DOUBLE                       AS price,
    cost::DOUBLE                        AS cost,
    CURRENT_TIMESTAMP                   AS _ingested_at,
    'products.csv'                      AS _source_file
FROM read_csv_auto('/Users/sivarajumalladi/Documents/GitHub/LearningBot/Sj-Prod/Medallion-Architecture-dbt/data/raw/products.csv')