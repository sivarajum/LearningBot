
  
    
    

    create  table
      "warehouse"."main_bronze"."bronze_orders__dbt_tmp"
  
    as (
      /*
  bronze_orders.sql
  -----------------
  BRONZE LAYER — Raw ingest of orders.csv.

  Design principles:
    - No business logic. Cast types, add metadata.
    - amount stored as DOUBLE for downstream aggregation.
    - order_date cast to DATE; time component not relevant for this dataset.
*/



SELECT
    order_id::VARCHAR                   AS order_id,
    customer_id::VARCHAR                AS customer_id,
    product_id::VARCHAR                 AS product_id,
    order_date::DATE                    AS order_date,
    amount::DOUBLE                      AS amount,
    status::VARCHAR                     AS status,
    CURRENT_TIMESTAMP                   AS _ingested_at,
    'orders.csv'                        AS _source_file
FROM read_csv_auto('/Users/sivarajumalladi/Documents/GitHub/LearningBot/Sj-Prod/Medallion-Architecture-dbt/data/raw/orders.csv')
    );
  
  