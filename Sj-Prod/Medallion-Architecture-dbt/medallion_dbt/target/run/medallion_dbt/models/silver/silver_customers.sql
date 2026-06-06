
  
    
    

    create  table
      "warehouse"."main_silver"."silver_customers__dbt_tmp"
  
    as (
      /*
  silver_customers.sql
  --------------------
  SILVER LAYER — Clean, validate, enrich bronze_customers.

  Transformations applied:
    1. Email validation  — only rows with '@' in email pass through (data contract)
    2. NOT NULL check    — customer_id must not be null
    3. Deduplication     — QUALIFY keeps the most recent ingest per customer_id
    4. Normalisation     — name and email lowercased + trimmed
    5. Enrichment        — customer_age_days derived from signup_date
    6. Macro usage       — clean_string macro used on name field
*/



SELECT
    customer_id,
    
    TRIM(
        REGEXP_REPLACE(
            LOWER(TRIM(name)),
            '\\s+',
            ' '
        )
    )
                                      AS name,
    TRIM(LOWER(email))                                              AS email,
    country,
    signup_date,
    UPPER(tier)                                                     AS tier,
    DATEDIFF('day', signup_date, CURRENT_DATE)                      AS customer_age_days,
    CASE
        WHEN UPPER(tier) = 'GOLD'   THEN 3
        WHEN UPPER(tier) = 'SILVER' THEN 2
        ELSE 1
    END                                                             AS tier_rank,
    _ingested_at,
    _source_file
FROM "warehouse"."main_bronze"."bronze_customers"
WHERE email LIKE '%@%'          -- basic email contract
  AND customer_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY _ingested_at DESC
) = 1
    );
  
  