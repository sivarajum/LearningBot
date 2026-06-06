
  
    
    

    create  table
      "warehouse"."main_silver"."silver_products__dbt_tmp"
  
    as (
      /*
  silver_products.sql
  -------------------
  SILVER LAYER — Clean, validate, enrich bronze_products.

  Transformations applied:
    1. Category normalisation — consistent title-case via UPPER of first char + LOWER rest
    2. Margin calculation     — gross_margin_pct derived from price / cost
    3. Price tier bucketing   — budget/mid-range/premium classification
    4. Validation             — price and cost must be positive
    5. Deduplication          — latest ingest per product_id
*/



SELECT
    product_id,
    
    TRIM(
        REGEXP_REPLACE(
            LOWER(TRIM(name)),
            '\\s+',
            ' '
        )
    )
                                      AS name,
    -- DuckDB title-case: UPPER first char + LOWER rest of trimmed category
    UPPER(LEFT(TRIM(category), 1)) || LOWER(SUBSTR(TRIM(category), 2)) AS category,
    price,
    cost,
    ROUND((price - cost) / NULLIF(price, 0) * 100, 2)              AS gross_margin_pct,
    CASE
        WHEN price <  30  THEN 'budget'
        WHEN price < 100  THEN 'mid-range'
        ELSE 'premium'
    END                                                             AS price_tier,
    _ingested_at,
    _source_file
FROM "warehouse"."main_bronze"."bronze_products"
WHERE price > 0
  AND cost > 0
  AND product_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY product_id
    ORDER BY _ingested_at DESC
) = 1
    );
  
  