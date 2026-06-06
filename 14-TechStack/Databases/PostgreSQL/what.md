# PostgreSQL Database Guide

## PostgreSQL Fundamentals

### What is PostgreSQL?

PostgreSQL is an advanced open-source relational database management system (RDBMS) known for its robustness, extensibility, and compliance with SQL standards. It supports both SQL and JSON querying, making it suitable for a wide range of applications.

### Key Characteristics

- **ACID Compliance**: Full ACID transactions with multi-version concurrency control (MVCC)
- **Extensible**: Support for custom data types, operators, and functions
- **Standards Compliant**: Full SQL:2016 standard compliance
- **Advanced Features**: JSON support, full-text search, geospatial data
- **Performance**: Advanced indexing, query optimization, and parallel processing
- **Security**: Role-based access control, SSL connections, data encryption
- **Scalability**: Support for large databases and high concurrency

### Data Types

```sql
-- Numeric types
CREATE TABLE numeric_types (
    small_int SMALLINT,           -- -32,768 to 32,767
    integer INTEGER,              -- -2,147,483,648 to 2,147,483,647
    big_int BIGINT,               -- -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807
    decimal_num DECIMAL(10,2),    -- Exact precision
    numeric_num NUMERIC(10,2),    -- Exact precision
    real_num REAL,                -- 6 decimal digits precision
    double_precision DOUBLE PRECISION -- 15 decimal digits precision
);

-- Character types
CREATE TABLE character_types (
    char_field CHAR(10),          -- Fixed length
    varchar_field VARCHAR(50),    -- Variable length
    text_field TEXT               -- Unlimited length
);

-- Date/Time types
CREATE TABLE temporal_types (
    date_field DATE,              -- Date only
    time_field TIME,              -- Time only
    timestamp_field TIMESTAMP,    -- Date and time
    timestamptz_field TIMESTAMPTZ,-- Date and time with timezone
    interval_field INTERVAL       -- Time interval
);

-- Boolean and UUID
CREATE TABLE other_types (
    bool_field BOOLEAN,           -- TRUE/FALSE
    uuid_field UUID               -- Universally unique identifier
);

-- Arrays
CREATE TABLE array_types (
    int_array INTEGER[],          -- Array of integers
    text_array TEXT[],            -- Array of text
    nested_array INTEGER[][]      -- Multidimensional array
);

-- JSON types
CREATE TABLE json_types (
    json_field JSON,              -- JSON data
    jsonb_field JSONB             -- Binary JSON with indexing
);

-- Geometric types
CREATE TABLE geometric_types (
    point_field POINT,            -- (x,y)
    line_field LINE,              -- Line segment
    circle_field CIRCLE,          -- Center point and radius
    polygon_field POLYGON         -- Closed path
);
```

## Database Operations

### Connecting to PostgreSQL

```javascript
const { Pool, Client } = require('pg');

// Using connection pool (recommended)
const pool = new Pool({
  user: 'postgres',
  host: 'localhost',
  database: 'myapp',
  password: 'password',
  port: 5432,
  max: 20, // Maximum number of clients in the pool
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Using single client
const client = new Client({
  user: 'postgres',
  host: 'localhost',
  database: 'myapp',
  password: 'password',
  port: 5432,
});

async function connectWithPool() {
  try {
    const client = await pool.connect();
    console.log('Connected to PostgreSQL');

    // Use the client
    const result = await client.query('SELECT NOW()');
    console.log('Current time:', result.rows[0]);

    client.release(); // Release the client back to the pool
  } catch (error) {
    console.error('Connection failed:', error);
  }
}

async function connectWithClient() {
  try {
    await client.connect();
    console.log('Connected to PostgreSQL');

    const result = await client.query('SELECT NOW()');
    console.log('Current time:', result.rows[0]);

    await client.end();
  } catch (error) {
    console.error('Connection failed:', error);
  }
}
```

### CRUD Operations

#### Create Operations

```sql
-- Create database
CREATE DATABASE myapp
    WITH OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Create table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    age INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert single row
INSERT INTO users (name, email, age)
VALUES ('John Doe', 'john@example.com', 30);

-- Insert multiple rows
INSERT INTO users (name, email, age) VALUES
    ('Jane Smith', 'jane@example.com', 25),
    ('Bob Johnson', 'bob@example.com', 35),
    ('Alice Brown', 'alice@example.com', 28);

-- Insert with returning
INSERT INTO users (name, email, age)
VALUES ('Charlie Wilson', 'charlie@example.com', 32)
RETURNING id, name, email;
```

#### Read Operations

```sql
-- Select all columns
SELECT * FROM users;

-- Select specific columns
SELECT name, email FROM users;

-- Select with WHERE clause
SELECT * FROM users WHERE age >= 25;

-- Select with multiple conditions
SELECT * FROM users
WHERE age BETWEEN 25 AND 35
  AND name LIKE 'J%';

-- Select with ordering
SELECT * FROM users
ORDER BY created_at DESC;

-- Select with limiting
SELECT * FROM users
ORDER BY created_at DESC
LIMIT 10 OFFSET 20;

-- Select with aggregation
SELECT
    COUNT(*) as total_users,
    AVG(age) as average_age,
    MIN(age) as min_age,
    MAX(age) as max_age
FROM users;

-- Select with grouping
SELECT
    EXTRACT(YEAR FROM created_at) as year,
    COUNT(*) as users_created
FROM users
GROUP BY EXTRACT(YEAR FROM created_at)
ORDER BY year;

-- Select with joins
SELECT
    u.name,
    u.email,
    o.order_id,
    o.total_amount,
    o.order_date
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.order_date >= '2023-01-01'
ORDER BY o.order_date DESC;
```

#### Update Operations

```sql
-- Update single row
UPDATE users
SET age = 31, updated_at = CURRENT_TIMESTAMP
WHERE id = 1;

-- Update multiple rows
UPDATE users
SET updated_at = CURRENT_TIMESTAMP
WHERE age < 25;

-- Update with returning
UPDATE users
SET name = 'John Smith', updated_at = CURRENT_TIMESTAMP
WHERE id = 1
RETURNING id, name, email, age;

-- Update with subquery
UPDATE users
SET age = (
    SELECT AVG(age) FROM users WHERE age > 20
)
WHERE id = 2;

-- Update with CASE statement
UPDATE users
SET age = CASE
    WHEN age < 25 THEN age + 1
    WHEN age >= 25 AND age < 35 THEN age + 2
    ELSE age + 3
END,
updated_at = CURRENT_TIMESTAMP;
```

#### Delete Operations

```sql
-- Delete single row
DELETE FROM users WHERE id = 1;

-- Delete multiple rows
DELETE FROM users WHERE age < 20;

-- Delete with returning
DELETE FROM users WHERE email = 'old@example.com'
RETURNING id, name, email;

-- Delete with subquery
DELETE FROM users
WHERE id IN (
    SELECT user_id FROM inactive_users
);

-- Truncate table (faster than DELETE for all rows)
TRUNCATE TABLE users RESTART IDENTITY;
```

## Advanced Queries

### Common Table Expressions (CTEs)

```sql
-- Recursive CTE for hierarchical data
WITH RECURSIVE employee_hierarchy AS (
    -- Base case: top-level employees
    SELECT
        id,
        name,
        manager_id,
        0 as level,
        ARRAY[name] as path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: subordinates
    SELECT
        e.id,
        e.name,
        e.manager_id,
        eh.level + 1,
        eh.path || e.name
    FROM employees e
    JOIN employee_hierarchy eh ON e.manager_id = eh.id
)
SELECT * FROM employee_hierarchy
ORDER BY level, name;

-- CTE for complex aggregations
WITH monthly_stats AS (
    SELECT
        DATE_TRUNC('month', order_date) as month,
        COUNT(*) as order_count,
        SUM(total_amount) as total_revenue,
        AVG(total_amount) as avg_order_value
    FROM orders
    WHERE order_date >= '2023-01-01'
    GROUP BY DATE_TRUNC('month', order_date)
),
user_stats AS (
    SELECT
        DATE_TRUNC('month', created_at) as month,
        COUNT(*) as new_users
    FROM users
    WHERE created_at >= '2023-01-01'
    GROUP BY DATE_TRUNC('month', created_at)
)
SELECT
    ms.month,
    ms.order_count,
    ms.total_revenue,
    ms.avg_order_value,
    COALESCE(us.new_users, 0) as new_users
FROM monthly_stats ms
LEFT JOIN user_stats us ON ms.month = us.month
ORDER BY ms.month;
```

### Window Functions

```sql
-- ROW_NUMBER, RANK, DENSE_RANK
SELECT
    name,
    department,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) as row_num,
    RANK() OVER (ORDER BY salary DESC) as rank,
    DENSE_RANK() OVER (ORDER BY salary DESC) as dense_rank
FROM employees;

-- PARTITION BY for group-wise calculations
SELECT
    department,
    name,
    salary,
    AVG(salary) OVER (PARTITION BY department) as dept_avg_salary,
    MAX(salary) OVER (PARTITION BY department) as dept_max_salary,
    salary - AVG(salary) OVER (PARTITION BY department) as salary_diff_from_avg
FROM employees;

-- Running totals and moving averages
SELECT
    order_date,
    total_amount,
    SUM(total_amount) OVER (ORDER BY order_date) as running_total,
    AVG(total_amount) OVER (ORDER BY order_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as moving_avg_3
FROM orders
ORDER BY order_date;

-- LAG and LEAD functions
SELECT
    order_date,
    total_amount,
    LAG(total_amount) OVER (ORDER BY order_date) as prev_order_amount,
    LEAD(total_amount) OVER (ORDER BY order_date) as next_order_amount,
    total_amount - LAG(total_amount) OVER (ORDER BY order_date) as amount_change
FROM orders
ORDER BY order_date;

-- FIRST_VALUE and LAST_VALUE
SELECT
    department,
    name,
    salary,
    hire_date,
    FIRST_VALUE(name) OVER (PARTITION BY department ORDER BY hire_date) as first_hired,
    LAST_VALUE(name) OVER (PARTITION BY department ORDER BY hire_date
                          ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_hired
FROM employees;
```

### Full-Text Search

```sql
-- Create table with text search vector
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    search_vector TSVECTOR
);

-- Create index on search vector
CREATE INDEX articles_search_idx ON articles USING GIN (search_vector);

-- Function to update search vector
CREATE OR REPLACE FUNCTION articles_search_vector_update() RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
CREATE TRIGGER articles_search_vector_trigger
    BEFORE INSERT OR UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION articles_search_vector_update();

-- Insert sample data
INSERT INTO articles (title, content) VALUES
    ('PostgreSQL Tutorial', 'Learn how to use PostgreSQL database'),
    ('Advanced SQL', 'Deep dive into SQL queries and optimization'),
    ('Database Design', 'Best practices for database schema design');

-- Basic text search
SELECT title, content
FROM articles
WHERE search_vector @@ to_tsquery('english', 'postgresql & tutorial');

-- Ranked search results
SELECT
    title,
    content,
    ts_rank(search_vector, to_tsquery('english', 'database')) as rank
FROM articles
WHERE search_vector @@ to_tsquery('english', 'database')
ORDER BY rank DESC;

-- Search with highlighting
SELECT
    title,
    ts_headline('english', content, to_tsquery('english', 'database')) as highlighted_content
FROM articles
WHERE search_vector @@ to_tsquery('english', 'database');

-- Fuzzy search with trigram similarity
CREATE EXTENSION IF NOT EXISTS pg_trgm;

SELECT
    title,
    similarity(title, 'PostgreSQL') as similarity_score
FROM articles
WHERE title % 'PostgreSQL'  -- Similarity threshold
ORDER BY similarity_score DESC;
```

### JSON Operations

```sql
-- Create table with JSON columns
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    profile_data JSONB,
    settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert JSON data
INSERT INTO user_profiles (user_id, profile_data, settings) VALUES
    (1, '{"name": "John Doe", "preferences": {"theme": "dark", "notifications": true}}',
        '{"language": "en", "timezone": "UTC"}'),
    (2, '{"name": "Jane Smith", "preferences": {"theme": "light", "notifications": false}}',
        '{"language": "fr", "timezone": "CET"}');

-- Query JSON data
SELECT
    user_id,
    profile_data->>'name' as name,
    profile_data->'preferences'->>'theme' as theme,
    settings->>'language' as language
FROM user_profiles;

-- JSON path queries
SELECT * FROM user_profiles
WHERE profile_data @> '{"preferences": {"notifications": true}}';

-- Update JSON fields
UPDATE user_profiles
SET profile_data = profile_data || '{"last_login": "2023-12-01"}'
WHERE user_id = 1;

-- JSON array operations
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    tags JSONB
);

INSERT INTO products (name, tags) VALUES
    ('Laptop', '["electronics", "computer", "portable"]'),
    ('Book', '["education", "fiction"]');

-- Query array elements
SELECT * FROM products
WHERE tags ? 'electronics';  -- Contains element

SELECT * FROM products
WHERE tags @> '["electronics"]';  -- Contains array

-- JSONB indexing for performance
CREATE INDEX idx_user_profiles_data ON user_profiles USING GIN (profile_data);
CREATE INDEX idx_products_tags ON products USING GIN (tags);
```

## Indexing

### Index Types

```sql
-- B-tree index (default, good for equality and range queries)
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_age ON users (age);
CREATE INDEX idx_orders_date_amount ON orders (order_date, total_amount);

-- Unique index
CREATE UNIQUE INDEX idx_users_unique_email ON users (email);

-- Partial index (index only certain rows)
CREATE INDEX idx_active_users ON users (email) WHERE active = true;

-- Expression index
CREATE INDEX idx_users_lower_email ON users (LOWER(email));
CREATE INDEX idx_orders_year ON orders (EXTRACT(YEAR FROM order_date));

-- Hash index (good for equality only, smaller size)
CREATE INDEX idx_users_hash_email ON users USING HASH (email);

-- GIN index (for arrays, full-text search, JSONB)
CREATE INDEX idx_posts_tags ON posts USING GIN (tags);
CREATE INDEX idx_articles_search ON articles USING GIN (search_vector);

-- GiST index (for geometric data, full-text search)
CREATE INDEX idx_places_location ON places USING GiST (location);

-- SP-GiST index (for space-partitioned trees)
CREATE INDEX idx_routes_path ON routes USING SPGIST (path);

-- BRIN index (for large tables with correlated data)
CREATE INDEX idx_logs_timestamp ON logs USING BRIN (timestamp);

-- Covering index (includes all columns needed by query)
CREATE INDEX idx_users_covering ON users (department) INCLUDE (name, salary);
```

### Index Management

```sql
-- List all indexes
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Get index usage statistics
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Analyze index effectiveness
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM users WHERE email = 'john@example.com';

-- Reindex (rebuild index)
REINDEX INDEX idx_users_email;

-- Reindex all indexes in a table
REINDEX TABLE users;

-- Drop index
DROP INDEX IF EXISTS idx_users_email;

-- Index size information
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```

## Transactions and Concurrency

### Transaction Control

```sql
-- Basic transaction
BEGIN;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- Transaction with error handling
DO $$
DECLARE
    sender_balance INTEGER;
BEGIN
    -- Check sender balance
    SELECT balance INTO sender_balance FROM accounts WHERE id = 1;

    IF sender_balance < 100 THEN
        RAISE EXCEPTION 'Insufficient funds';
    END IF;

    -- Perform transfer
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;

    RAISE NOTICE 'Transfer completed successfully';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Transfer failed: %', SQLERRM;
        ROLLBACK;
END;
$$;

-- Savepoints for partial rollback
BEGIN;
    SAVEPOINT before_transfer;

    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;

    -- Some other operations that might fail
    UPDATE accounts SET balance = balance + 50 WHERE id = 3;

    RELEASE SAVEPOINT before_transfer;
COMMIT;
```

### Isolation Levels

```sql
-- Set transaction isolation level
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
    -- Your queries here
COMMIT;

-- Different isolation levels:
-- READ UNCOMMITTED - Allows reading uncommitted changes
-- READ COMMITTED - Default, only committed changes visible
-- REPEATABLE READ - Same snapshot throughout transaction
-- SERIALIZABLE - Highest isolation, prevents serialization anomalies

-- Check current isolation level
SHOW transaction_isolation;

-- Demonstrate isolation levels
-- Session 1
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT balance FROM accounts WHERE id = 1;  -- Returns 1000

-- Session 2
UPDATE accounts SET balance = 900 WHERE id = 1;
COMMIT;

-- Session 1
SELECT balance FROM accounts WHERE id = 1;  -- Still returns 1000
COMMIT;
```

### Locking

```sql
-- Explicit row locking
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;

-- Different lock modes:
-- FOR UPDATE - Exclusive lock, blocks other updates
-- FOR NO KEY UPDATE - Allows updates to non-key columns
-- FOR SHARE - Shared lock, allows other shared locks
-- FOR KEY SHARE - Allows updates to non-key columns

-- Advisory locks (application-level locking)
SELECT pg_advisory_lock(12345);    -- Acquire lock
-- Do some work
SELECT pg_advisory_unlock(12345);  -- Release lock

-- Table-level locks
LOCK TABLE accounts IN ACCESS EXCLUSIVE MODE;

-- Lock monitoring
SELECT
    locktype,
    relation::regclass,
    mode,
    granted,
    pid
FROM pg_locks
WHERE relation::regclass::text LIKE 'accounts';
```

## Views and Functions

### Views

```sql
-- Simple view
CREATE VIEW active_users AS
SELECT id, name, email, created_at
FROM users
WHERE active = true;

-- Materialized view (cached results)
CREATE MATERIALIZED VIEW monthly_revenue AS
SELECT
    DATE_TRUNC('month', order_date) as month,
    SUM(total_amount) as revenue,
    COUNT(*) as order_count
FROM orders
GROUP BY DATE_TRUNC('month', order_date);

-- Refresh materialized view
REFRESH MATERIALIZED VIEW monthly_revenue;

-- View with check option (prevents invalid inserts)
CREATE VIEW premium_users AS
SELECT * FROM users
WHERE subscription_level = 'premium'
WITH CHECK OPTION;

-- Recursive view
CREATE RECURSIVE VIEW employee_tree AS
SELECT id, name, manager_id, 0 as level
FROM employees
WHERE manager_id IS NULL

UNION ALL

SELECT e.id, e.name, e.manager_id, et.level + 1
FROM employees e
JOIN employee_tree et ON e.manager_id = et.id;
```

### Functions

```sql
-- Simple function
CREATE OR REPLACE FUNCTION get_user_balance(user_id INTEGER)
RETURNS DECIMAL AS $$
DECLARE
    balance DECIMAL;
BEGIN
    SELECT COALESCE(SUM(amount), 0) INTO balance
    FROM transactions
    WHERE account_id = user_id;

    RETURN balance;
END;
$$ LANGUAGE plpgsql;

-- Function with parameters
CREATE OR REPLACE FUNCTION transfer_funds(
    from_account INTEGER,
    to_account INTEGER,
    transfer_amount DECIMAL
) RETURNS BOOLEAN AS $$
DECLARE
    sender_balance DECIMAL;
BEGIN
    -- Check balance
    SELECT get_user_balance(from_account) INTO sender_balance;

    IF sender_balance < transfer_amount THEN
        RETURN FALSE;
    END IF;

    -- Perform transfer
    INSERT INTO transactions (account_id, amount, type) VALUES
        (from_account, -transfer_amount, 'transfer_out'),
        (to_account, transfer_amount, 'transfer_in');

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Table-returning function
CREATE OR REPLACE FUNCTION get_recent_transactions(days_back INTEGER DEFAULT 30)
RETURNS TABLE (
    transaction_id INTEGER,
    account_id INTEGER,
    amount DECIMAL,
    transaction_date TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT t.id, t.account_id, t.amount, t.created_at
    FROM transactions t
    WHERE t.created_at >= CURRENT_DATE - INTERVAL '1 day' * days_back
    ORDER BY t.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Aggregate function
CREATE OR REPLACE FUNCTION array_agg_distinct(anyarray)
RETURNS anyarray AS $$
    SELECT array_agg(DISTINCT x) FROM unnest($1) x;
$$ LANGUAGE sql;

-- Window function
CREATE OR REPLACE FUNCTION running_average(state numeric[], value numeric)
RETURNS numeric[] AS $$
BEGIN
    IF state IS NULL THEN
        RETURN ARRAY[value, 1, value];  -- sum, count, average
    ELSE
        state[1] := state[1] + value;    -- add to sum
        state[2] := state[2] + 1;        -- increment count
        state[3] := state[1] / state[2]; -- calculate average
        RETURN state;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

## Triggers

```sql
-- Basic trigger for audit logging
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT,
    operation TEXT,
    old_data JSONB,
    new_data JSONB,
    changed_by TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, operation, old_data, new_data, changed_by)
    VALUES (
        TG_TABLE_NAME,
        TG_OP,
        CASE WHEN TG_OP != 'INSERT' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP != 'DELETE' THEN row_to_json(NEW) ELSE NULL END,
        current_user
    );

    RETURN CASE
        WHEN TG_OP = 'DELETE' THEN OLD
        ELSE NEW
    END;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger
CREATE TRIGGER users_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- Trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Conditional trigger
CREATE OR REPLACE FUNCTION prevent_negative_balance()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.balance < 0 THEN
        RAISE EXCEPTION 'Balance cannot be negative';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_balance_trigger
    BEFORE UPDATE ON accounts
    FOR EACH ROW
    WHEN (OLD.balance IS DISTINCT FROM NEW.balance)
    EXECUTE FUNCTION prevent_negative_balance();
```

## Performance Optimization

### Query Optimization

```sql
-- Use EXPLAIN to analyze query plans
EXPLAIN SELECT * FROM users WHERE age > 25;
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM users WHERE age > 25;

-- Common optimization techniques:

-- 1. Use appropriate indexes
CREATE INDEX CONCURRENTLY idx_users_age ON users (age);

-- 2. Avoid SELECT *
SELECT id, name, email FROM users WHERE age > 25;

-- 3. Use LIMIT for large result sets
SELECT * FROM users ORDER BY created_at DESC LIMIT 100;

-- 4. Use UNION ALL instead of UNION when possible
SELECT name FROM customers
UNION ALL
SELECT name FROM employees;

-- 5. Use EXISTS instead of IN for large datasets
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.user_id = u.id AND o.total_amount > 100
);

-- 6. Use CTEs for complex queries
WITH recent_orders AS (
    SELECT user_id, SUM(total_amount) as total
    FROM orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT u.name, ro.total
FROM users u
LEFT JOIN recent_orders ro ON u.id = ro.user_id;

-- 7. Partition large tables
CREATE TABLE orders_y2023 PARTITION OF orders
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

-- 8. Use appropriate data types
-- Use INTEGER instead of BIGINT when possible
-- Use VARCHAR(n) instead of TEXT when length is known
-- Use TIMESTAMP instead of VARCHAR for dates
```

### Configuration Tuning

```sql
-- View current settings
SHOW ALL;

-- Key performance parameters:

-- Memory settings
SET work_mem = '64MB';                    -- Memory for sorts and hashes
SET maintenance_work_mem = '256MB';       -- Memory for maintenance operations
SET shared_buffers = '256MB';             -- Shared buffer cache

-- Connection settings
SET max_connections = 100;                -- Maximum concurrent connections
SET effective_cache_size = '1GB';         -- Estimate of OS cache

-- Query planning
SET random_page_cost = 1.1;               -- Cost of random page access
SET seq_page_cost = 1.0;                  -- Cost of sequential page access

-- Logging
SET log_statement = 'ddl';                -- Log DDL statements
SET log_duration = on;                    -- Log query duration
SET log_min_duration_statement = 1000;   -- Log slow queries (>1s)

-- Autovacuum settings
SET autovacuum = on;                      -- Enable autovacuum
SET autovacuum_max_workers = 3;           -- Number of autovacuum workers
SET autovacuum_naptime = '20s';           -- Time between autovacuum runs

-- Replication settings (for master)
SET wal_level = replica;                  -- WAL level for replication
SET max_wal_senders = 3;                  -- Maximum WAL senders
SET wal_keep_segments = 32;               -- WAL segments to keep
```

### Monitoring and Maintenance

```sql
-- Database size information
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) -
                   pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Table statistics
SELECT
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;

-- Index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as scans,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Active queries
SELECT
    pid,
    usename,
    client_addr,
    query_start,
    state,
    left(query, 50) as query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_start;

-- Vacuum and analyze
VACUUM ANALYZE users;           -- Update statistics and clean dead tuples
VACUUM FULL users;              -- Aggressive vacuum (locks table)
REINDEX TABLE users;            -- Rebuild all indexes

-- Backup and restore
pg_dump myapp > backup.sql;     -- Logical backup
psql myapp < backup.sql;        -- Restore from backup

-- Physical backup (using pg_basebackup)
pg_basebackup -D /path/to/backup -Ft -z -P
```

This comprehensive guide covers PostgreSQL from basic operations to advanced features including indexing, transactions, views, functions, triggers, and performance optimization.
