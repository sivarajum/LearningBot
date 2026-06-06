
  
    
    

    create  table
      "warehouse"."main_bronze"."bronze_customers__dbt_tmp"
  
    as (
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



SELECT
    customer_id::VARCHAR                AS customer_id,
    name::VARCHAR                       AS name,
    email::VARCHAR                      AS email,
    country::VARCHAR                    AS country,
    signup_date::DATE                   AS signup_date,
    tier::VARCHAR                       AS tier,
    CURRENT_TIMESTAMP                   AS _ingested_at,
    'customers.csv'                     AS _source_file
FROM read_csv_auto('/Users/sivarajumalladi/Documents/GitHub/LearningBot/Sj-Prod/Medallion-Architecture-dbt/data/raw/customers.csv')
    );
  
  