# SQL for Data Engineering

## Overview

SQL (Structured Query Language) is the standard language for managing and manipulating relational databases. In data engineering, SQL serves as the foundation for data extraction, transformation, and loading operations across various database systems.

## Core Concepts

### 1. Relational Database Fundamentals

**Tables and Relations:**
- **Primary Key**: Unique identifier for each record
- **Foreign Key**: References primary key in another table
- **Relationships**: One-to-one, one-to-many, many-to-many

**Normalization:**
- **1NF**: Eliminate repeating groups
- **2NF**: Remove partial dependencies
- **3NF**: Remove transitive dependencies
- **BCNF**: Boyce-Codd normal form

### 2. Data Types

**Numeric Types:**
- `INTEGER/INT`: Whole numbers (-2^31 to 2^31-1)
- `BIGINT`: Large integers (-2^63 to 2^63-1)
- `DECIMAL/NUMERIC`: Fixed precision decimals
- `FLOAT/REAL`: Floating-point numbers

**String Types:**
- `CHAR(n)`: Fixed-length strings
- `VARCHAR(n)`: Variable-length strings
- `TEXT`: Large text blocks

**Date/Time Types:**
- `DATE`: Date only (YYYY-MM-DD)
- `TIME`: Time only (HH:MM:SS)
- `TIMESTAMP`: Date and time with timezone
- `INTERVAL`: Time intervals

**Boolean and Others:**
- `BOOLEAN`: True/False values
- `JSON/JSONB`: JSON data storage
- `ARRAY`: Array types (PostgreSQL)
- `UUID`: Universally unique identifiers

## Data Definition Language (DDL)

### Creating Tables

```sql
-- Basic table creation
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table with constraints
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount > 0),
    status VARCHAR(20) DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')),

    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Partitioned table (PostgreSQL)
CREATE TABLE sales (
    sale_id SERIAL,
    sale_date DATE NOT NULL,
    product_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL
) PARTITION BY RANGE (sale_date);

CREATE TABLE sales_2023 PARTITION OF sales
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
```

### Indexes and Performance

```sql
-- Single column index
CREATE INDEX idx_customers_email ON customers(email);

-- Composite index
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);

-- Partial index
CREATE INDEX idx_active_orders ON orders(order_id)
WHERE status NOT IN ('cancelled', 'delivered');

-- Unique index
CREATE UNIQUE INDEX idx_unique_customer_email ON customers(email);

-- Full-text search index (PostgreSQL)
CREATE INDEX idx_products_description_fts
ON products USING gin(to_tsvector('english', description));

-- Index for JSON data
CREATE INDEX idx_user_preferences_gin
ON users USING gin(preferences);
```

### Table Alterations

```sql
-- Add columns
ALTER TABLE customers ADD COLUMN date_of_birth DATE;
ALTER TABLE customers ADD COLUMN loyalty_points INTEGER DEFAULT 0;

-- Modify columns
ALTER TABLE customers ALTER COLUMN phone TYPE VARCHAR(25);
ALTER TABLE customers ALTER COLUMN email SET NOT NULL;

-- Drop columns
ALTER TABLE customers DROP COLUMN IF EXISTS middle_name;

-- Add constraints
ALTER TABLE customers ADD CONSTRAINT chk_age
CHECK (date_of_birth <= CURRENT_DATE - INTERVAL '13 years');

-- Rename objects
ALTER TABLE customers RENAME TO client_base;
ALTER TABLE client_base RENAME COLUMN first_name TO given_name;
```

## Data Manipulation Language (DML)

### Basic CRUD Operations

```sql
-- INSERT operations
INSERT INTO customers (first_name, last_name, email)
VALUES ('John', 'Doe', 'john.doe@email.com');

INSERT INTO customers (first_name, last_name, email)
VALUES
    ('Jane', 'Smith', 'jane.smith@email.com'),
    ('Bob', 'Johnson', 'bob.johnson@email.com');

-- INSERT with SELECT
INSERT INTO customer_backup
SELECT * FROM customers WHERE created_at < '2023-01-01';

-- UPDATE operations
UPDATE customers
SET loyalty_points = loyalty_points + 100
WHERE customer_id = 123;

UPDATE customers
SET updated_at = CURRENT_TIMESTAMP
WHERE customer_id IN (
    SELECT customer_id FROM orders
    WHERE order_date >= '2023-01-01'
);

-- DELETE operations
DELETE FROM customers
WHERE customer_id = 123;

DELETE FROM order_items
WHERE order_id IN (
    SELECT order_id FROM orders
    WHERE status = 'cancelled'
    AND order_date < CURRENT_DATE - INTERVAL '1 year'
);

-- UPSERT (INSERT or UPDATE)
INSERT INTO customer_stats (customer_id, total_orders, total_spent)
VALUES (123, 5, 1250.00)
ON CONFLICT (customer_id)
DO UPDATE SET
    total_orders = customer_stats.total_orders + EXCLUDED.total_orders,
    total_spent = customer_stats.total_spent + EXCLUDED.total_spent;
```

### Advanced Data Retrieval

```sql
-- Basic SELECT with filtering
SELECT customer_id, first_name, last_name, email
FROM customers
WHERE created_at >= '2023-01-01'
  AND email LIKE '%@gmail.com'
ORDER BY created_at DESC;

-- JOIN operations
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(o.order_id) as order_count,
    SUM(o.total_amount) as total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= '2023-01-01'
GROUP BY c.customer_id, c.first_name, c.last_name
HAVING COUNT(o.order_id) > 0
ORDER BY total_spent DESC;

-- Subqueries
SELECT *
FROM customers
WHERE customer_id IN (
    SELECT customer_id
    FROM orders
    GROUP BY customer_id
    HAVING SUM(total_amount) > 1000
);

-- CTE (Common Table Expression)
WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', order_date) as month,
        SUM(total_amount) as monthly_total,
        COUNT(*) as order_count
    FROM orders
    WHERE order_date >= '2023-01-01'
    GROUP BY DATE_TRUNC('month', order_date)
),
customer_metrics AS (
    SELECT
        customer_id,
        COUNT(*) as order_count,
        SUM(total_amount) as total_spent,
        AVG(total_amount) as avg_order_value
    FROM orders
    GROUP BY customer_id
)
SELECT
    ms.month,
    ms.monthly_total,
    ms.order_count,
    ROUND(ms.monthly_total::numeric / NULLIF(ms.order_count, 0), 2) as avg_order_value
FROM monthly_sales ms
ORDER BY ms.month;
```

## Advanced SQL Techniques

### Window Functions

```sql
-- Ranking functions
SELECT
    customer_id,
    first_name,
    total_spent,
    RANK() OVER (ORDER BY total_spent DESC) as spending_rank,
    DENSE_RANK() OVER (ORDER BY total_spent DESC) as dense_rank,
    ROW_NUMBER() OVER (ORDER BY total_spent DESC) as row_num
FROM (
    SELECT
        customer_id,
        first_name,
        SUM(total_amount) as total_spent
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY customer_id, first_name
) customer_totals;

-- Running totals and moving averages
SELECT
    order_date,
    total_amount,
    SUM(total_amount) OVER (ORDER BY order_date) as running_total,
    AVG(total_amount) OVER (ORDER BY order_date ROWS 6 PRECEDING) as moving_avg_7d,
    LAG(total_amount) OVER (ORDER BY order_date) as prev_day_amount,
    LEAD(total_amount) OVER (ORDER BY order_date) as next_day_amount
FROM daily_sales
ORDER BY order_date;

-- Percentiles and distribution
SELECT
    product_category,
    product_name,
    sales_amount,
    PERCENT_RANK() OVER (PARTITION BY product_category ORDER BY sales_amount) as percent_rank,
    NTILE(4) OVER (PARTITION BY product_category ORDER BY sales_amount) as quartile
FROM product_sales;

-- FIRST_VALUE and LAST_VALUE
SELECT
    department,
    employee_name,
    salary,
    FIRST_VALUE(employee_name) OVER (PARTITION BY department ORDER BY salary DESC) as highest_paid,
    LAST_VALUE(employee_name) OVER (PARTITION BY department ORDER BY salary DESC
                                   ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as lowest_paid
FROM employees;
```

### Pivoting and Unpivoting

```sql
-- Pivot (static)
SELECT
    product_category,
    SUM(CASE WHEN EXTRACT(month FROM order_date) = 1 THEN total_amount ELSE 0 END) as jan_sales,
    SUM(CASE WHEN EXTRACT(month FROM order_date) = 2 THEN total_amount ELSE 0 END) as feb_sales,
    SUM(CASE WHEN EXTRACT(month FROM order_date) = 3 THEN total_amount ELSE 0 END) as mar_sales
FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE EXTRACT(year FROM order_date) = 2023
GROUP BY product_category;

-- Dynamic pivot (PostgreSQL)
CREATE OR REPLACE FUNCTION pivot_sales()
RETURNS TABLE(category TEXT, jan_sales NUMERIC, feb_sales NUMERIC, mar_sales NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT
        product_category,
        SUM(CASE WHEN EXTRACT(month FROM order_date) = 1 THEN total_amount ELSE 0 END),
        SUM(CASE WHEN EXTRACT(month FROM order_date) = 2 THEN total_amount ELSE 0 END),
        SUM(CASE WHEN EXTRACT(month FROM order_date) = 3 THEN total_amount ELSE 0 END)
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    WHERE EXTRACT(year FROM order_date) = 2023
    GROUP BY product_category;
END;
$$ LANGUAGE plpgsql;

-- Unpivot
SELECT
    product_category,
    CASE month_num
        WHEN 1 THEN 'January'
        WHEN 2 THEN 'February'
        WHEN 3 THEN 'March'
    END as month_name,
    monthly_sales
FROM (
    SELECT
        product_category,
        1 as month_num, jan_sales as monthly_sales FROM sales_pivot
    UNION ALL
    SELECT product_category, 2, feb_sales FROM sales_pivot
    UNION ALL
    SELECT product_category, 3, mar_sales FROM sales_pivot
) unpivoted
WHERE monthly_sales > 0
ORDER BY product_category, month_num;
```

### Recursive Queries

```sql
-- Employee hierarchy
WITH RECURSIVE employee_hierarchy AS (
    -- Base case: top-level managers
    SELECT
        employee_id,
        manager_id,
        first_name,
        last_name,
        0 as level,
        ARRAY[employee_id] as path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: subordinates
    SELECT
        e.employee_id,
        e.manager_id,
        e.first_name,
        e.last_name,
        eh.level + 1,
        eh.path || e.employee_id
    FROM employees e
    JOIN employee_hierarchy eh ON e.manager_id = eh.employee_id
)
SELECT * FROM employee_hierarchy
ORDER BY path;

-- Bill of materials (BOM)
WITH RECURSIVE bom AS (
    -- Base case: final products
    SELECT
        product_id,
        component_id,
        quantity,
        1 as level,
        ARRAY[product_id] as path
    FROM product_components
    WHERE product_id NOT IN (
        SELECT DISTINCT component_id FROM product_components
    )

    UNION ALL

    -- Recursive case: sub-components
    SELECT
        pc.product_id,
        pc.component_id,
        pc.quantity * bom.quantity,
        bom.level + 1,
        bom.path || pc.product_id
    FROM product_components pc
    JOIN bom ON pc.product_id = bom.component_id
    WHERE pc.product_id != ALL(bom.path)  -- Prevent cycles
)
SELECT
    product_id,
    component_id,
    SUM(quantity) as total_quantity,
    level
FROM bom
GROUP BY product_id, component_id, level
ORDER BY product_id, level, component_id;
```

## Performance Optimization

### Query Optimization

```sql
-- EXPLAIN plan analysis
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    c.customer_id,
    c.first_name,
    COUNT(o.order_id) as order_count,
    SUM(o.total_amount) as total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= '2023-01-01'
GROUP BY c.customer_id, c.first_name
HAVING COUNT(o.order_id) > 5;

-- Query with proper indexing strategy
CREATE INDEX CONCURRENTLY idx_orders_customer_date_amount
ON orders(customer_id, order_date, total_amount);

CREATE INDEX CONCURRENTLY idx_orders_date_status
ON orders(order_date, status)
WHERE status IN ('pending', 'processing');

-- Partitioning for large tables
CREATE TABLE orders_y2023 PARTITION OF orders
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE orders_y2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- Materialized views for complex aggregations
CREATE MATERIALIZED VIEW monthly_customer_stats AS
SELECT
    DATE_TRUNC('month', o.order_date) as month,
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(o.order_id) as order_count,
    SUM(o.total_amount) as total_spent,
    AVG(o.total_amount) as avg_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= '2023-01-01'
GROUP BY DATE_TRUNC('month', o.order_date), c.customer_id, c.first_name, c.last_name;

CREATE UNIQUE INDEX idx_monthly_customer_stats
ON monthly_customer_stats(month, customer_id);

-- Refresh materialized view
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_customer_stats;
```

### Database Maintenance

```sql
-- Analyze table statistics
ANALYZE customers;
ANALYZE orders;

-- Vacuum for space reclamation
VACUUM (VERBOSE, ANALYZE) customers;
VACUUM FULL orders;  -- Locks table, use carefully

-- Reindex for performance
REINDEX INDEX CONCURRENTLY idx_orders_customer_date;

-- Monitor slow queries
SELECT
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Connection pooling configuration
-- postgresql.conf
max_connections = 100
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.max = 10000
pg_stat_statements.track = all
```

## Data Warehousing Concepts

### Star Schema Design

```sql
-- Dimension tables
CREATE TABLE dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50),
    effective_date DATE NOT NULL,
    expiry_date DATE DEFAULT '9999-12-31',
    is_current BOOLEAN DEFAULT TRUE
);

CREATE TABLE dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(100),
    category VARCHAR(50),
    subcategory VARCHAR(50),
    price DECIMAL(10,2),
    effective_date DATE NOT NULL,
    expiry_date DATE DEFAULT '9999-12-31',
    is_current BOOLEAN DEFAULT TRUE
);

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    date_actual DATE NOT NULL,
    day_of_week INTEGER,
    day_name VARCHAR(10),
    month_actual INTEGER,
    month_name VARCHAR(10),
    quarter_actual INTEGER,
    year_actual INTEGER,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);

-- Fact table
CREATE TABLE fact_sales (
    sales_key SERIAL PRIMARY KEY,
    customer_key INTEGER NOT NULL REFERENCES dim_customer(customer_key),
    product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    order_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,

    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

-- Populate date dimension
INSERT INTO dim_date (date_key, date_actual, day_of_week, day_name,
                     month_actual, month_name, quarter_actual, year_actual,
                     is_weekend, is_holiday)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INTEGER,
    d,
    EXTRACT(DOW FROM d),
    TO_CHAR(d, 'Day'),
    EXTRACT(MONTH FROM d),
    TO_CHAR(d, 'Month'),
    EXTRACT(QUARTER FROM d),
    EXTRACT(YEAR FROM d),
    CASE WHEN EXTRACT(DOW FROM d) IN (0, 6) THEN TRUE ELSE FALSE END,
    FALSE  -- Simplified holiday logic
FROM generate_series('2020-01-01'::date, '2030-12-31'::date, '1 day'::interval) d;
```

### Slowly Changing Dimensions (SCD)

```sql
-- SCD Type 2 implementation
CREATE OR REPLACE FUNCTION update_customer_scd()
RETURNS TRIGGER AS $$
BEGIN
    -- Expire old record
    UPDATE dim_customer
    SET expiry_date = CURRENT_DATE - INTERVAL '1 day',
        is_current = FALSE
    WHERE customer_id = NEW.customer_id
      AND is_current = TRUE;

    -- Insert new record
    INSERT INTO dim_customer (
        customer_id, first_name, last_name, email,
        city, state, effective_date, is_current
    ) VALUES (
        NEW.customer_id, NEW.first_name, NEW.last_name, NEW.email,
        NEW.city, NEW.state, CURRENT_DATE, TRUE
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER customer_scd_trigger
    AFTER UPDATE ON customers
    FOR EACH ROW
    WHEN (OLD.* IS DISTINCT FROM NEW.*)
    EXECUTE FUNCTION update_customer_scd();
```

## ETL Patterns with SQL

### Incremental Loading

```sql
-- Using timestamps
INSERT INTO target_table
SELECT * FROM source_table
WHERE updated_at > (SELECT COALESCE(MAX(updated_at), '1900-01-01') FROM target_table);

-- Using change tracking (SQL Server)
INSERT INTO target_table
SELECT * FROM source_table
WHERE change_tracking_id > (SELECT MAX(change_tracking_id) FROM target_table);

-- Using hash comparison
WITH source_hashes AS (
    SELECT
        id,
        MD5(ROW(data_col1, data_col2, data_col3)::TEXT) as row_hash
    FROM source_table
),
target_hashes AS (
    SELECT id, row_hash FROM target_table
)
INSERT INTO target_table
SELECT s.* FROM source_table s
JOIN source_hashes sh ON s.id = sh.id
LEFT JOIN target_hashes th ON sh.id = th.id AND sh.row_hash = th.row_hash
WHERE th.id IS NULL;
```

### Data Quality Checks

```sql
-- Completeness check
SELECT
    'Missing customer_id' as check_name,
    COUNT(*) as failed_count
FROM orders
WHERE customer_id IS NULL

UNION ALL

SELECT
    'Missing order_date' as check_name,
    COUNT(*) as failed_count
FROM orders
WHERE order_date IS NULL

UNION ALL

SELECT
    'Invalid email format' as check_name,
    COUNT(*) as failed_count
FROM customers
WHERE email NOT LIKE '%@%.%';

-- Uniqueness check
SELECT
    customer_id,
    COUNT(*) as duplicate_count
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- Referential integrity check
SELECT
    'Orphaned orders' as check_name,
    COUNT(*) as failed_count
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- Range and format validation
SELECT
    'Negative amounts' as check_name,
    COUNT(*) as failed_count
FROM orders
WHERE total_amount < 0

UNION ALL

SELECT
    'Future dates' as check_name,
    COUNT(*) as failed_count
FROM orders
WHERE order_date > CURRENT_DATE;
```

### Error Handling and Logging

```sql
-- Create error logging table
CREATE TABLE etl_error_log (
    error_id SERIAL PRIMARY KEY,
    pipeline_name VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    error_message TEXT NOT NULL,
    error_data JSONB,
    error_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ETL procedure with error handling
CREATE OR REPLACE PROCEDURE load_customer_data()
LANGUAGE plpgsql AS $$
DECLARE
    batch_size INTEGER := 1000;
    processed_count INTEGER := 0;
    error_count INTEGER := 0;
BEGIN
    -- Log start
    INSERT INTO etl_log (pipeline_name, status, message)
    VALUES ('customer_load', 'STARTED', 'Beginning customer data load');

    BEGIN
        -- Truncate staging if needed
        TRUNCATE TABLE customer_staging;

        -- Load data with error handling
        INSERT INTO customer_staging (customer_id, first_name, last_name, email)
        SELECT customer_id, first_name, last_name, email
        FROM raw_customer_data;

        -- Validate data
        INSERT INTO etl_error_log (pipeline_name, table_name, error_message, error_data)
        SELECT
            'customer_load',
            'customer_staging',
            'Invalid email format',
            jsonb_build_object('customer_id', customer_id, 'email', email)
        FROM customer_staging
        WHERE email NOT LIKE '%@%.%';

        -- Load valid data
        INSERT INTO customers (customer_id, first_name, last_name, email)
        SELECT customer_id, first_name, last_name, email
        FROM customer_staging
        WHERE email LIKE '%@%.%'
        ON CONFLICT (customer_id) DO UPDATE SET
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            email = EXCLUDED.email;

        GET DIAGNOSTICS processed_count = ROW_COUNT;

        -- Log success
        INSERT INTO etl_log (pipeline_name, status, message)
        VALUES ('customer_load', 'COMPLETED',
                format('Successfully loaded %s customer records', processed_count));

    EXCEPTION WHEN OTHERS THEN
        -- Log error
        INSERT INTO etl_error_log (pipeline_name, error_message, error_data)
        VALUES ('customer_load', SQLERRM, jsonb_build_object('sqlstate', SQLSTATE));

        -- Re-raise exception
        RAISE;
    END;
END;
$$;
```

## Advanced Analytics with SQL

### Time Series Analysis

```sql
-- Time series aggregation
SELECT
    DATE_TRUNC('hour', event_time) as hour_bucket,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(event_value) as avg_value,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY event_value) as p95_value
FROM user_events
WHERE event_time >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', event_time)
ORDER BY hour_bucket;

-- Trend analysis
WITH daily_metrics AS (
    SELECT
        DATE_TRUNC('day', order_date) as order_day,
        COUNT(*) as daily_orders,
        SUM(total_amount) as daily_revenue
    FROM orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY DATE_TRUNC('day', order_date)
),
trends AS (
    SELECT
        order_day,
        daily_orders,
        daily_revenue,
        LAG(daily_orders) OVER (ORDER BY order_day) as prev_day_orders,
        LAG(daily_revenue) OVER (ORDER BY order_day) as prev_day_revenue
    FROM daily_metrics
)
SELECT
    order_day,
    daily_orders,
    daily_revenue,
    ROUND(
        (daily_orders - prev_day_orders)::numeric / NULLIF(prev_day_orders, 0) * 100, 2
    ) as order_growth_pct,
    ROUND(
        (daily_revenue - prev_day_revenue)::numeric / NULLIF(prev_day_revenue, 0) * 100, 2
    ) as revenue_growth_pct
FROM trends
ORDER BY order_day;
```

### Cohort Analysis

```sql
-- Customer cohort analysis
WITH customer_cohorts AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(order_date)) as cohort_month,
        DATE_TRUNC('month', order_date) as order_month
    FROM orders
    GROUP BY customer_id, DATE_TRUNC('month', order_date)
),
cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) as cohort_size
    FROM customer_cohorts
    GROUP BY cohort_month
),
cohort_activity AS (
    SELECT
        cc.cohort_month,
        cc.order_month,
        COUNT(DISTINCT cc.customer_id) as active_customers,
        cs.cohort_size,
        EXTRACT(month FROM AGE(cc.order_month, cc.cohort_month)) as month_number
    FROM customer_cohorts cc
    JOIN cohort_sizes cs ON cc.cohort_month = cs.cohort_month
    GROUP BY cc.cohort_month, cc.order_month, cs.cohort_size
)
SELECT
    cohort_month,
    month_number,
    active_customers,
    cohort_size,
    ROUND(active_customers::numeric / cohort_size * 100, 2) as retention_rate
FROM cohort_activity
ORDER BY cohort_month, month_number;
```

### A/B Testing Analysis

```sql
-- A/B test results analysis
WITH test_metrics AS (
    SELECT
        test_group,
        COUNT(*) as total_users,
        COUNT(CASE WHEN converted = true THEN 1 END) as conversions,
        AVG(order_value) as avg_order_value,
        SUM(order_value) as total_revenue
    FROM ab_test_results
    WHERE test_id = 'homepage_redesign_q1_2024'
    GROUP BY test_group
),
statistical_test AS (
    SELECT
        a.test_group as group_a,
        b.test_group as group_b,
        a.conversions::float / a.total_users as conversion_rate_a,
        b.conversions::float / b.total_users as conversion_rate_b,
        -- Simplified statistical significance (in practice, use proper statistical tests)
        CASE
            WHEN ABS(a.conversions::float / a.total_users - b.conversions::float / b.total_users) > 0.02
            THEN 'Significant'
            ELSE 'Not Significant'
        END as significance
    FROM test_metrics a
    CROSS JOIN test_metrics b
    WHERE a.test_group < b.test_group
)
SELECT
    tm.test_group,
    tm.total_users,
    tm.conversions,
    ROUND(tm.conversions::numeric / tm.total_users * 100, 2) as conversion_rate,
    ROUND(tm.avg_order_value, 2) as avg_order_value,
    tm.total_revenue,
    st.significance
FROM test_metrics tm
LEFT JOIN statistical_test st ON tm.test_group IN (st.group_a, st.group_b);
```

## Summary

SQL is the cornerstone of data engineering, providing powerful capabilities for:

- **Data Definition**: Creating and managing database structures
- **Data Manipulation**: CRUD operations and complex transformations
- **Query Optimization**: Performance tuning and indexing strategies
- **Analytics**: Advanced analytics and business intelligence
- **ETL Processes**: Data pipeline development and maintenance

Key principles for effective SQL usage:
- **Normalization**: Proper database design
- **Indexing**: Strategic index creation for performance
- **Query Optimization**: Understanding execution plans
- **Data Quality**: Validation and error handling
- **Scalability**: Partitioning and distributed processing
- **Maintainability**: Clear, documented code with proper error handling

Mastering SQL enables building robust, scalable data engineering solutions that form the foundation of modern data platforms.
