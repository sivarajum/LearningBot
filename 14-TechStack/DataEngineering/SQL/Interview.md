# SQL Data Engineering Interview Questions & Answers

## Beginner Level Questions

### 1. What is SQL and why is it important for data engineering?
**Answer:** SQL (Structured Query Language) is a standard programming language for managing and manipulating relational databases. It's crucial for data engineering because:

**Key Importance:**
- **Data Retrieval**: Extract data from databases using SELECT statements
- **Data Manipulation**: Insert, update, and delete data using DML commands
- **Data Definition**: Create and modify database structures using DDL commands
- **Data Control**: Manage permissions and security using DCL commands
- **ETL Operations**: Foundation for extract, transform, load processes
- **Analytics**: Perform complex aggregations and business intelligence queries

**Real-world Usage:**
```sql
-- Data extraction for reporting
SELECT customer_id, SUM(amount) as total_spent
FROM orders
WHERE order_date >= '2023-01-01'
GROUP BY customer_id
ORDER BY total_spent DESC;

-- Data loading in ETL pipeline
INSERT INTO customer_summary
SELECT c.customer_id, c.name, COUNT(o.order_id) as order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name;
```

### 2. Explain the difference between WHERE and HAVING clauses.
**Answer:** WHERE and HAVING both filter data, but they operate at different stages:

**WHERE Clause:**
- Filters rows BEFORE grouping and aggregation
- Used with SELECT, UPDATE, DELETE statements
- Cannot use aggregate functions
- Applied to individual rows

**HAVING Clause:**
- Filters groups AFTER aggregation
- Used only with GROUP BY clause
- Can use aggregate functions
- Applied to grouped results

**Example:**
```sql
-- WHERE filters individual orders
SELECT customer_id, COUNT(*) as order_count
FROM orders
WHERE order_date >= '2023-01-01'  -- Filter before grouping
GROUP BY customer_id;

-- HAVING filters aggregated results
SELECT customer_id, COUNT(*) as order_count
FROM orders
WHERE order_date >= '2023-01-01'
GROUP BY customer_id
HAVING COUNT(*) > 5;  -- Filter after grouping
```

### 3. What are the different types of JOINs in SQL?
**Answer:** SQL supports several types of JOINs for combining data from multiple tables:

**INNER JOIN:**
- Returns only matching rows from both tables
- Most common type of join

**LEFT (OUTER) JOIN:**
- Returns all rows from left table, matching rows from right table
- NULL values for non-matching right table rows

**RIGHT (OUTER) JOIN:**
- Returns all rows from right table, matching rows from left table
- NULL values for non-matching left table rows

**FULL (OUTER) JOIN:**
- Returns all rows from both tables
- NULL values where there are no matches

**CROSS JOIN:**
- Returns Cartesian product of both tables
- Every row from first table paired with every row from second table

**Example:**
```sql
-- INNER JOIN: Only customers with orders
SELECT c.name, o.order_id, o.amount
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id;

-- LEFT JOIN: All customers, even those without orders
SELECT c.name, COUNT(o.order_id) as order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name;

-- FULL OUTER JOIN: All customers and all orders
SELECT c.name, o.order_id
FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id;
```

## Intermediate Level Questions

### 4. How do you optimize a slow SQL query?
**Answer:** Query optimization involves multiple strategies:

**1. Analyze Execution Plan:**
```sql
EXPLAIN ANALYZE
SELECT c.name, COUNT(o.order_id) as order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.created_date >= '2023-01-01'
GROUP BY c.customer_id, c.name;
```

**2. Index Optimization:**
```sql
-- Add appropriate indexes
CREATE INDEX idx_customers_created_date ON customers(created_date);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- Composite index for common query patterns
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
```

**3. Query Rewriting:**
```sql
-- Instead of multiple subqueries
SELECT c.name,
       (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.customer_id) as order_count
FROM customers c;

-- Use JOIN for better performance
SELECT c.name, COUNT(o.order_id) as order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name;
```

**4. Use Appropriate JOIN Types:**
```sql
-- Use EXISTS instead of COUNT for existence checks
SELECT c.name
FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);
```

**5. Limit Result Sets:**
```sql
-- Use LIMIT for large datasets
SELECT * FROM large_table
ORDER BY created_date DESC
LIMIT 1000;

-- Use pagination
SELECT * FROM products
ORDER BY product_id
LIMIT 50 OFFSET 100;  -- Page 3 of 50-item pages
```

### 5. Explain window functions and provide examples.
**Answer:** Window functions perform calculations across a set of rows related to the current row, without collapsing rows like aggregate functions.

**Key Concepts:**
- **Window Frame**: Set of rows for calculation
- **Partition**: Groups rows for separate calculations
- **Order**: Defines sequence within partition

**Common Window Functions:**
```sql
-- Ranking functions
SELECT
    product_name,
    sales_amount,
    RANK() OVER (ORDER BY sales_amount DESC) as sales_rank,
    DENSE_RANK() OVER (ORDER BY sales_amount DESC) as dense_rank,
    ROW_NUMBER() OVER (ORDER BY sales_amount DESC) as row_num
FROM product_sales;

-- Running totals and moving averages
SELECT
    order_date,
    daily_sales,
    SUM(daily_sales) OVER (ORDER BY order_date) as running_total,
    AVG(daily_sales) OVER (ORDER BY order_date ROWS 6 PRECEDING) as moving_avg_7d,
    LAG(daily_sales) OVER (ORDER BY order_date) as prev_day_sales,
    LEAD(daily_sales) OVER (ORDER BY order_date) as next_day_sales
FROM daily_sales_summary;

-- Percentiles and distribution
SELECT
    employee_name,
    salary,
    department,
    PERCENT_RANK() OVER (PARTITION BY department ORDER BY salary) as dept_percentile,
    NTILE(4) OVER (PARTITION BY department ORDER BY salary) as salary_quartile
FROM employees;

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

### 6. How do you handle NULL values in SQL?
**Answer:** NULL represents missing or unknown data. Handling requires special consideration:

**NULL Behavior:**
- Any operation with NULL results in NULL
- NULL comparisons return UNKNOWN (not TRUE/FALSE)
- Use IS NULL or IS NOT NULL for NULL checks

**Handling Strategies:**
```sql
-- Check for NULL values
SELECT * FROM customers
WHERE phone IS NULL;

-- Replace NULL with default values
SELECT
    customer_id,
    COALESCE(phone, 'Not provided') as phone,
    COALESCE(email, 'No email') as email
FROM customers;

-- NULL-safe comparisons
SELECT * FROM products
WHERE price IS NOT NULL
  AND price > 100;

-- Aggregate functions and NULL
SELECT
    COUNT(*) as total_rows,           -- Includes NULL
    COUNT(price) as non_null_prices,  -- Excludes NULL
    AVG(COALESCE(price, 0)) as avg_price_with_default,
    SUM(price) as total_price         -- NULL values ignored
FROM products;

-- NULL in WHERE clauses
SELECT * FROM orders
WHERE ship_date IS NULL;  -- Orders not yet shipped

-- NULL in JOIN conditions
SELECT c.name, o.order_id
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;  -- Customers with no orders
```

### 7. What are database indexes and when should you use them?
**Answer:** Indexes are data structures that improve query performance by providing fast access to rows.

**Index Types:**
```sql
-- Single column index
CREATE INDEX idx_customers_email ON customers(email);

-- Composite index (multiple columns)
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);

-- Unique index
CREATE UNIQUE INDEX idx_customers_unique_email ON customers(email);

-- Partial index (conditional)
CREATE INDEX idx_active_orders ON orders(order_id)
WHERE status = 'active';

-- Full-text search index (PostgreSQL)
CREATE INDEX idx_products_description_fts
ON products USING gin(to_tsvector('english', description));
```

**When to Use Indexes:**
- **High Selectivity**: Columns with many distinct values
- **Frequent Queries**: Columns used in WHERE, JOIN, ORDER BY
- **Foreign Keys**: Always index foreign key columns
- **Composite Indexes**: For multi-column WHERE conditions

**When NOT to Use Indexes:**
- **Low Selectivity**: Columns with few distinct values (e.g., gender)
- **Small Tables**: Full table scan is faster
- **Write-Heavy Tables**: Indexes slow down INSERT/UPDATE/DELETE
- **Computed Columns**: Better to index the source columns

**Index Maintenance:**
```sql
-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Reindex for performance
REINDEX INDEX CONCURRENTLY idx_orders_customer_date;

-- Remove unused indexes
DROP INDEX IF EXISTS idx_unused_index;
```

## Advanced Level Questions

### 8. How do you implement Slowly Changing Dimensions (SCD)?
**Answer:** SCD handles changes in dimension data over time. There are several types:

**SCD Type 1: Overwrite**
- Overwrites old data with new data
- No history preserved
- Simple but loses historical context

```sql
-- SCD Type 1 implementation
UPDATE customers
SET address = 'New Address',
    updated_at = CURRENT_TIMESTAMP
WHERE customer_id = 123;
```

**SCD Type 2: Add New Row**
- Creates new row for changes
- Preserves full history
- Uses effective/expiry dates or version numbers

```sql
-- SCD Type 2 implementation
CREATE TABLE dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    customer_name VARCHAR(100),
    address VARCHAR(200),
    effective_date DATE NOT NULL,
    expiry_date DATE DEFAULT '9999-12-31',
    is_current BOOLEAN DEFAULT TRUE
);

-- Insert new customer
INSERT INTO dim_customer (customer_id, customer_name, address, effective_date)
VALUES (123, 'John Doe', '123 Main St', CURRENT_DATE);

-- Handle updates
CREATE OR REPLACE FUNCTION update_customer_scd2()
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
        customer_id, customer_name, address,
        effective_date, is_current
    ) VALUES (
        NEW.customer_id, NEW.customer_name, NEW.address,
        CURRENT_DATE, TRUE
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER customer_scd2_trigger
    AFTER UPDATE ON customers
    FOR EACH ROW
    WHEN (OLD.* IS DISTINCT FROM NEW.*)
    EXECUTE FUNCTION update_customer_scd2();
```

**SCD Type 3: Add New Column**
- Adds new column for previous value
- Limited history (usually just current and previous)
- Good for frequently changing attributes

```sql
-- SCD Type 3 implementation
ALTER TABLE dim_customer
ADD COLUMN previous_address VARCHAR(200);

UPDATE dim_customer
SET previous_address = address,
    address = 'New Address',
    updated_at = CURRENT_TIMESTAMP
WHERE customer_id = 123;
```

### 9. Explain query execution plans and how to read them.
**Answer:** Execution plans show how the database will execute a query, including join order, access methods, and cost estimates.

**Reading Execution Plans:**
```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT c.customer_name, COUNT(o.order_id) as order_count, SUM(o.amount) as total_amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.region = 'North America'
  AND o.order_date >= '2023-01-01'
GROUP BY c.customer_id, c.customer_name
HAVING COUNT(o.order_id) > 3
ORDER BY total_amount DESC
LIMIT 10;
```

**Key Components:**
- **Node Types**: Seq Scan, Index Scan, Hash Join, etc.
- **Cost Estimates**: startup_cost and total_cost
- **Row Estimates**: Expected number of rows
- **Width**: Average row width in bytes
- **Actual vs Estimated**: How accurate the planner was

**Common Operations:**
- **Seq Scan**: Full table scan (expensive for large tables)
- **Index Scan**: Uses index to find rows
- **Bitmap Index Scan**: Combines multiple index conditions
- **Hash Join**: Builds hash table for one side, probes with other
- **Nested Loop**: For each row in outer, scan inner
- **Merge Join**: Requires sorted inputs
- **Sort**: Sorts data (expensive)
- **Aggregate**: GROUP BY operations
- **Limit**: Stops after N rows

**Optimization Strategies:**
```sql
-- Force index usage (if needed)
SELECT * FROM customers
WHERE customer_id = 123;  -- Will use primary key index

-- Avoid functions on indexed columns
SELECT * FROM orders
WHERE DATE(order_date) = '2023-01-01';  -- Won't use index

-- Use proper data types
SELECT * FROM products
WHERE price > 100.00;  -- Will use index if exists

-- Rewrite for better plans
-- Instead of IN with subquery
SELECT c.* FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.customer_id = c.customer_id
    AND o.amount > 1000
);
```

### 10. How do you implement data partitioning in SQL?
**Answer:** Partitioning divides large tables into smaller, more manageable pieces while maintaining a single logical table.

**Partitioning Types:**

**Range Partitioning:**
```sql
-- Create partitioned table
CREATE TABLE sales (
    sale_id SERIAL,
    sale_date DATE NOT NULL,
    customer_id INTEGER,
    amount DECIMAL(10,2)
) PARTITION BY RANGE (sale_date);

-- Create partitions
CREATE TABLE sales_2023_q1 PARTITION OF sales
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');

CREATE TABLE sales_2023_q2 PARTITION OF sales
    FOR VALUES FROM ('2023-04-01') TO ('2023-07-01');

-- Automatic routing
INSERT INTO sales (sale_date, customer_id, amount)
VALUES ('2023-02-15', 123, 100.00);  -- Goes to sales_2023_q1
```

**List Partitioning:**
```sql
CREATE TABLE orders (
    order_id SERIAL,
    customer_id INTEGER,
    region VARCHAR(50),
    amount DECIMAL(10,2)
) PARTITION BY LIST (region);

CREATE TABLE orders_us PARTITION OF orders
    FOR VALUES IN ('US-East', 'US-West', 'US-Central');

CREATE TABLE orders_eu PARTITION OF orders
    FOR VALUES IN ('EU-West', 'EU-East');

CREATE TABLE orders_other PARTITION OF orders
    FOR VALUES IN ('Asia', 'Other');
```

**Hash Partitioning:**
```sql
CREATE TABLE user_events (
    event_id SERIAL,
    user_id INTEGER,
    event_type VARCHAR(50),
    event_data JSONB,
    created_at TIMESTAMP
) PARTITION BY HASH (user_id);

-- Create 4 hash partitions
CREATE TABLE user_events_0 PARTITION OF user_events
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE user_events_1 PARTITION OF user_events
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE user_events_2 PARTITION OF user_events
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE user_events_3 PARTITION OF user_events
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

**Partitioning Benefits:**
- **Query Performance**: Scan only relevant partitions
- **Maintenance**: Drop old partitions easily
- **Parallel Processing**: Multiple partitions simultaneously
- **Storage Management**: Different storage per partition

**Partition Management:**
```sql
-- Add new partition
CREATE TABLE sales_2024_q1 PARTITION OF sales
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

-- Detach partition (becomes standalone table)
ALTER TABLE sales DETACH PARTITION sales_2022_q1;

-- Attach existing table as partition
ALTER TABLE sales ATTACH PARTITION sales_2024_q1
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

-- Partition pruning verification
EXPLAIN SELECT * FROM sales
WHERE sale_date >= '2023-01-01' AND sale_date < '2023-04-01';
-- Should show: "Partitions selected: sales_2023_q1"
```

### 11. How do you implement recursive queries in SQL?
**Answer:** Recursive queries use CTEs to process hierarchical or tree-structured data.

**Basic Recursive CTE Structure:**
```sql
WITH RECURSIVE cte_name AS (
    -- Anchor member (base case)
    SELECT columns
    FROM table
    WHERE condition

    UNION ALL

    -- Recursive member (calls itself)
    SELECT columns
    FROM table
    JOIN cte_name ON join_condition
)
SELECT * FROM cte_name;
```

**Employee Hierarchy Example:**
```sql
-- Create sample data
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    manager_id INTEGER REFERENCES employees(employee_id)
);

-- Recursive CTE for hierarchy
WITH RECURSIVE employee_hierarchy AS (
    -- Anchor: top-level managers
    SELECT
        employee_id,
        name,
        manager_id,
        0 as level,
        ARRAY[employee_id] as path,
        name as hierarchy_path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive: subordinates
    SELECT
        e.employee_id,
        e.name,
        e.manager_id,
        eh.level + 1,
        eh.path || e.employee_id,
        eh.hierarchy_path || ' > ' || e.name
    FROM employees e
    JOIN employee_hierarchy eh ON e.manager_id = eh.employee_id
)
SELECT * FROM employee_hierarchy
ORDER BY path;
```

**Bill of Materials (BOM) Example:**
```sql
CREATE TABLE product_components (
    product_id INTEGER,
    component_id INTEGER,
    quantity INTEGER,
    PRIMARY KEY (product_id, component_id)
);

WITH RECURSIVE bom AS (
    -- Anchor: final products (not used as components)
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

    -- Recursive: sub-components
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

**Graph Traversal Example:**
```sql
-- Find all paths between nodes
WITH RECURSIVE paths AS (
    SELECT
        start_node,
        end_node,
        ARRAY[start_node, end_node] as path,
        cost
    FROM edges
    WHERE start_node = 'A'  -- Starting point

    UNION ALL

    SELECT
        p.start_node,
        e.end_node,
        p.path || e.end_node,
        p.cost + e.cost
    FROM paths p
    JOIN edges e ON p.end_node = e.start_node
    WHERE e.end_node != ALL(p.path)  -- Avoid cycles
)
SELECT * FROM paths
WHERE end_node = 'Z'  -- Target node
ORDER BY cost;
```

### 12. How do you implement data quality checks in SQL?
**Answer:** Data quality checks ensure data integrity and reliability:

**Completeness Checks:**
```sql
-- Check for NULL values in required fields
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
    'Missing email' as check_name,
    COUNT(*) as failed_count
FROM customers
WHERE email IS NULL OR email = '';
```

**Accuracy and Validity Checks:**
```sql
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
WHERE order_date > CURRENT_DATE

UNION ALL

SELECT
    'Invalid email format' as check_name,
    COUNT(*) as failed_count
FROM customers
WHERE email NOT LIKE '%@%.%'

UNION ALL

SELECT
    'Invalid phone format' as check_name,
    COUNT(*) as failed_count
FROM customers
WHERE phone !~ '^\+?[0-9\s\-\(\)]+$';
```

**Consistency and Integrity Checks:**
```sql
-- Referential integrity
SELECT
    'Orphaned orders' as check_name,
    COUNT(*) as failed_count
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- Cross-field validation
SELECT
    'Ship date before order date' as check_name,
    COUNT(*) as failed_count
FROM orders
WHERE ship_date < order_date;

-- Business rule validation
SELECT
    'High-value order without approval' as check_name,
    COUNT(*) as failed_count
FROM orders
WHERE total_amount > 10000
  AND approval_status IS NULL;
```

**Uniqueness Checks:**
```sql
-- Duplicate detection
SELECT
    customer_id,
    COUNT(*) as duplicate_count
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- Composite uniqueness
SELECT
    order_id,
    product_id,
    COUNT(*) as duplicate_count
FROM order_items
GROUP BY order_id, product_id
HAVING COUNT(*) > 1;
```

**Timeliness Checks:**
```sql
-- Data freshness
SELECT
    'Stale customer data' as check_name,
    COUNT(*) as failed_count
FROM customers
WHERE updated_at < CURRENT_DATE - INTERVAL '90 days';

-- Processing timeliness
SELECT
    'Unprocessed orders' as check_name,
    COUNT(*) as failed_count
FROM orders
WHERE status = 'pending'
  AND created_at < CURRENT_DATE - INTERVAL '7 days';
```

**Statistical Checks:**
```sql
-- Outlier detection using IQR
WITH stats AS (
    SELECT
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY amount) as q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY amount) as q3
    FROM orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT
    'Amount outliers' as check_name,
    COUNT(*) as failed_count
FROM orders o, stats s
WHERE o.order_date >= CURRENT_DATE - INTERVAL '30 days'
  AND o.amount < s.q1 - 1.5 * (s.q3 - s.q1)
   OR o.amount > s.q3 + 1.5 * (s.q3 - s.q1);
```

**Data Quality Dashboard:**
```sql
-- Create quality metrics table
CREATE TABLE data_quality_metrics (
    check_date DATE,
    table_name VARCHAR(100),
    check_name VARCHAR(200),
    failed_count INTEGER,
    total_count INTEGER,
    quality_score DECIMAL(5,2)
);

-- Insert daily quality metrics
INSERT INTO data_quality_metrics
SELECT
    CURRENT_DATE,
    'customers',
    'Completeness Check',
    COUNT(CASE WHEN customer_id IS NULL OR name IS NULL THEN 1 END),
    COUNT(*),
    ROUND(
        (COUNT(*) - COUNT(CASE WHEN customer_id IS NULL OR name IS NULL THEN 1 END))::numeric
        / COUNT(*)::numeric * 100, 2
    )
FROM customers;
```

## Scenario-Based Questions

### 13. How would you design a data warehouse for an e-commerce company?
**Answer:** Designing a comprehensive e-commerce data warehouse:

**1. Identify Business Requirements:**
- Sales analytics and reporting
- Customer behavior analysis
- Inventory management
- Marketing campaign effectiveness
- Product performance metrics

**2. Design Star Schema:**
```sql
-- Date dimension
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

-- Customer dimension (SCD Type 2)
CREATE TABLE dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    registration_date DATE,
    customer_segment VARCHAR(20),
    effective_date DATE NOT NULL,
    expiry_date DATE DEFAULT '9999-12-31',
    is_current BOOLEAN DEFAULT TRUE
);

-- Product dimension (SCD Type 2)
CREATE TABLE dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(100),
    category VARCHAR(50),
    subcategory VARCHAR(50),
    brand VARCHAR(50),
    price DECIMAL(10,2),
    effective_date DATE NOT NULL,
    expiry_date DATE DEFAULT '9999-12-31',
    is_current BOOLEAN DEFAULT TRUE
);

-- Store dimension
CREATE TABLE dim_store (
    store_key SERIAL PRIMARY KEY,
    store_id INTEGER NOT NULL,
    store_name VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50),
    region VARCHAR(50),
    store_type VARCHAR(20)
);

-- Fact tables
CREATE TABLE fact_sales (
    sales_key SERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    customer_key INTEGER NOT NULL REFERENCES dim_customer(customer_key),
    product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
    store_key INTEGER NOT NULL REFERENCES dim_store(store_key),
    order_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    shipping_cost DECIMAL(10,2) DEFAULT 0,

    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (store_key) REFERENCES dim_store(store_key)
);

-- Fact table for inventory
CREATE TABLE fact_inventory (
    inventory_key SERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
    store_key INTEGER NOT NULL REFERENCES dim_store(store_key),
    beginning_inventory INTEGER,
    ending_inventory INTEGER,
    inventory_adjustments INTEGER,
    stockouts INTEGER,
    overstock INTEGER
);
```

**3. Implement ETL Process:**
```sql
-- Stage data from source systems
CREATE TABLE stg_orders (
    order_id INTEGER,
    customer_id INTEGER,
    order_date DATE,
    product_id INTEGER,
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    discount DECIMAL(10,2),
    tax DECIMAL(10,2),
    shipping_cost DECIMAL(10,2),
    store_id INTEGER
);

-- Load dimensions
INSERT INTO dim_customer (
    customer_id, first_name, last_name, email,
    registration_date, customer_segment, effective_date
)
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    c.registration_date,
    CASE
        WHEN c.total_orders > 10 THEN 'High Value'
        WHEN c.total_orders > 5 THEN 'Medium Value'
        ELSE 'Low Value'
    END,
    CURRENT_DATE
FROM source_customers c
WHERE NOT EXISTS (
    SELECT 1 FROM dim_customer dc
    WHERE dc.customer_id = c.customer_id
    AND dc.is_current = TRUE
);

-- Load fact table
INSERT INTO fact_sales (
    date_key, customer_key, product_key, store_key,
    order_id, quantity, unit_price, total_amount,
    discount_amount, tax_amount, shipping_cost
)
SELECT
    dd.date_key,
    dc.customer_key,
    dp.product_key,
    ds.store_key,
    so.order_id,
    so.quantity,
    so.unit_price,
    (so.quantity * so.unit_price) - COALESCE(so.discount, 0) + COALESCE(so.tax, 0),
    COALESCE(so.discount, 0),
    COALESCE(so.tax, 0),
    COALESCE(so.shipping_cost, 0)
FROM stg_orders so
JOIN dim_date dd ON dd.date_actual = so.order_date
JOIN dim_customer dc ON dc.customer_id = so.customer_id AND dc.is_current = TRUE
JOIN dim_product dp ON dp.product_id = so.product_id AND dp.is_current = TRUE
JOIN dim_store ds ON ds.store_id = so.store_id;
```

**4. Create Analytics Views:**
```sql
-- Customer analytics
CREATE VIEW customer_analytics AS
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    c.customer_segment,
    COUNT(DISTINCT fs.order_id) as total_orders,
    SUM(fs.total_amount) as lifetime_value,
    AVG(fs.total_amount) as avg_order_value,
    MAX(fs.date_key) as last_order_date,
    DATEDIFF(day, MAX(dd.date_actual), CURRENT_DATE) as days_since_last_order
FROM dim_customer c
LEFT JOIN fact_sales fs ON c.customer_key = fs.customer_key
LEFT JOIN dim_date dd ON fs.date_key = dd.date_key
WHERE c.is_current = TRUE
GROUP BY c.customer_id, c.first_name, c.last_name, c.customer_segment;

-- Product performance
CREATE VIEW product_performance AS
SELECT
    p.product_name,
    p.category,
    p.brand,
    SUM(fs.quantity) as total_quantity_sold,
    SUM(fs.total_amount) as total_revenue,
    COUNT(DISTINCT fs.customer_key) as unique_customers,
    AVG(fs.unit_price) as avg_selling_price,
    SUM(fs.discount_amount) as total_discounts
FROM dim_product p
LEFT JOIN fact_sales fs ON p.product_key = fs.product_key
WHERE p.is_current = TRUE
GROUP BY p.product_name, p.category, p.brand;
```

### 14. How do you handle database migrations in a production environment?
**Answer:** Database migrations require careful planning and execution:

**Migration Strategy:**
```sql
-- Create migration tracking table
CREATE TABLE schema_migrations (
    version VARCHAR(20) PRIMARY KEY,
    description TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_by VARCHAR(100)
);

-- Example migration script
DO $$
DECLARE
    migration_version VARCHAR(20) := '20240115_001';
BEGIN
    -- Check if migration already applied
    IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = migration_version) THEN
        RAISE NOTICE 'Migration % already applied', migration_version;
        RETURN;
    END IF;

    -- Start transaction
    BEGIN
        -- Add new column
        ALTER TABLE customers ADD COLUMN customer_segment VARCHAR(20);

        -- Update existing data
        UPDATE customers
        SET customer_segment = CASE
            WHEN total_orders > 10 THEN 'High Value'
            WHEN total_orders > 5 THEN 'Medium Value'
            ELSE 'Low Value'
        END;

        -- Add constraint
        ALTER TABLE customers
        ADD CONSTRAINT chk_customer_segment
        CHECK (customer_segment IN ('High Value', 'Medium Value', 'Low Value'));

        -- Create index
        CREATE INDEX idx_customers_segment ON customers(customer_segment);

        -- Record migration
        INSERT INTO schema_migrations (version, description, applied_by)
        VALUES (migration_version, 'Add customer segmentation', CURRENT_USER);

        RAISE NOTICE 'Migration % completed successfully', migration_version;

    EXCEPTION WHEN OTHERS THEN
        -- Rollback on error
        RAISE EXCEPTION 'Migration % failed: %', migration_version, SQLERRM;
    END;
END;
$$ LANGUAGE plpgsql;
```

**Migration Best Practices:**
```sql
-- 1. Backward compatibility
-- Add new columns as nullable first
ALTER TABLE orders ADD COLUMN priority VARCHAR(10) DEFAULT 'normal';

-- 2. Data migration in batches
CREATE OR REPLACE PROCEDURE migrate_customer_data()
LANGUAGE plpgsql AS $$
DECLARE
    batch_size INTEGER := 1000;
    migrated_count INTEGER := 0;
BEGIN
    LOOP
        UPDATE customers
        SET migrated_flag = TRUE,
            updated_at = CURRENT_TIMESTAMP
        WHERE customer_id IN (
            SELECT customer_id
            FROM customers
            WHERE migrated_flag = FALSE
            LIMIT batch_size
        );

        GET DIAGNOSTICS migrated_count = ROW_COUNT;
        EXIT WHEN migrated_count = 0;

        COMMIT;
        PERFORM pg_sleep(0.1);  -- Small delay between batches
    END LOOP;
END;
$$;

-- 3. Rollback scripts
CREATE OR REPLACE PROCEDURE rollback_migration_20240115_001()
LANGUAGE plpgsql AS $$
BEGIN
    -- Remove index
    DROP INDEX IF EXISTS idx_customers_segment;

    -- Remove constraint
    ALTER TABLE customers DROP CONSTRAINT IF EXISTS chk_customer_segment;

    -- Remove column
    ALTER TABLE customers DROP COLUMN IF EXISTS customer_segment;

    -- Remove migration record
    DELETE FROM schema_migrations WHERE version = '20240115_001';
END;
$$;

-- 4. Pre and post migration checks
CREATE OR REPLACE FUNCTION pre_migration_checks() RETURNS BOOLEAN AS $$
BEGIN
    -- Check disk space
    IF (SELECT pg_size_pretty(pg_database_size(current_database()))) LIKE '%GB' THEN
        -- Ensure sufficient space
        RETURN TRUE;
    END IF;

    -- Check for long-running transactions
    IF EXISTS (
        SELECT 1 FROM pg_stat_activity
        WHERE state = 'active'
        AND now() - query_start > interval '1 hour'
    ) THEN
        RAISE EXCEPTION 'Long-running transactions detected';
    END IF;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
```

**Deployment Process:**
```sql
-- 1. Backup database
-- pg_dump production_db > backup_$(date +%Y%m%d_%H%M%S).sql

-- 2. Test migration on staging
-- psql staging_db < migration_script.sql

-- 3. Run pre-migration checks
SELECT pre_migration_checks();

-- 4. Execute migration with timeout
SET statement_timeout = '3600000';  -- 1 hour
\i migration_script.sql

-- 5. Run post-migration validation
SELECT COUNT(*) FROM customers WHERE customer_segment IS NULL;

-- 6. Update application code
-- Deploy new application version

-- 7. Monitor for issues
-- Check application logs and performance metrics
```

## Summary

SQL interview questions for data engineering cover:

- **Basic SQL**: CRUD operations, joins, filtering, aggregation
- **Performance**: Indexing, query optimization, execution plans
- **Advanced Features**: Window functions, CTEs, recursive queries
- **Data Warehousing**: SCD, partitioning, star schema design
- **Data Quality**: Validation, integrity checks, monitoring
- **Production Concerns**: Migrations, backups, scalability

Key areas to master:
- **Query Optimization**: Understanding execution plans and indexing strategies
- **Data Modeling**: Designing efficient schemas and relationships
- **ETL Patterns**: Building robust data pipelines with error handling
- **Performance Tuning**: Monitoring, partitioning, and maintenance
- **Data Quality**: Implementing comprehensive validation frameworks
- **Production Readiness**: Migration strategies and operational concerns

Understanding these concepts enables building scalable, reliable data engineering solutions that form the backbone of modern data platforms.
