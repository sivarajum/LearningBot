# Google Cloud Dataform: Comprehensive Guide

## What is Dataform?

**Google Cloud Dataform** is a fully managed service for developing, testing, versioning, and scheduling SQL workflows in BigQuery. It enables data teams to transform raw data into structured, analytics-ready datasets using SQL with software engineering best practices like version control, testing, and documentation.

### Core Problem It Solves

Traditional SQL-based data transformation faces several challenges:
- **Lack of Version Control**: SQL scripts scattered across files without proper versioning
- **No Dependency Management**: Manual tracking of table dependencies
- **Limited Testing**: Difficult to test data transformations before production
- **Poor Documentation**: SQL code often lacks context and documentation
- **Complex Orchestration**: Challenging to schedule and manage execution order
- **No Code Reusability**: Duplicated logic across multiple queries

**Dataform solves these problems** by providing:
- Git-based version control for all SQL code
- Automatic dependency resolution and execution ordering
- Built-in data quality testing and assertions
- Inline documentation and metadata management
- Integrated scheduling and orchestration
- Modular, reusable SQL components

## Core Concepts and Principles

### 1. **SQLX Files**

SQLX is Dataform's extension of SQL that adds powerful features while maintaining SQL compatibility.

```sql
-- Example: Creating a table with SQLX
config {
  type: "table",
  schema: "analytics",
  description: "Daily user activity metrics",
  tags: ["daily", "users"],
  assertions: {
    uniqueKey: ["user_id", "activity_date"]
  }
}

SELECT
  user_id,
  DATE(event_timestamp) as activity_date,
  COUNT(*) as event_count,
  SUM(revenue) as total_revenue
FROM ${ref("raw_events")}
WHERE DATE(event_timestamp) = CURRENT_DATE()
GROUP BY 1, 2
```

**Key SQLX Features:**
- **Config Block**: Define table properties, schema, and metadata
- **Ref Function**: Reference other tables with automatic dependency tracking
- **Assertions**: Built-in data quality checks
- **Documentation**: Inline descriptions and tags

### 2. **Declarations**

Declarations allow you to reference external tables not managed by Dataform.

```sql
-- declarations.sqlx
config {
  type: "declaration",
  database: "my-project",
  schema: "raw_data",
  name: "external_events"
}
```

### 3. **Operations**

Operations are custom SQL statements that don't create tables (e.g., GRANT statements, stored procedures).

```sql
-- operations/grant_permissions.sqlx
config {
  type: "operation",
  hasOutput: false
}

GRANT SELECT ON TABLE ${ref("user_analytics")} TO GROUP data_analysts
```

### 4. **Includes**

Includes are reusable JavaScript functions for common transformations.

```javascript
// includes/utils.js
function cleanEmail(emailColumn) {
  return `LOWER(TRIM(${emailColumn}))`;
}

function calculateAge(birthDateColumn) {
  return `DATE_DIFF(CURRENT_DATE(), ${birthDateColumn}, YEAR)`;
}

module.exports = { cleanEmail, calculateAge };
```

Usage in SQLX:
```sql
SELECT
  user_id,
  ${cleanEmail("email")} as email,
  ${calculateAge("birth_date")} as age
FROM ${ref("raw_users")}
```

## Key Features and Capabilities

### 1. **Dependency Management**

Dataform automatically determines execution order based on table references.

```sql
-- Step 1: Base table
config { type: "table" }
SELECT * FROM ${ref("raw_data")}

-- Step 2: Depends on Step 1
config { type: "table" }
SELECT * FROM ${ref("base_table")}
WHERE condition = true

-- Step 3: Depends on Step 2
config { type: "table" }
SELECT * FROM ${ref("filtered_table")}
GROUP BY dimension
```

### 2. **Incremental Tables**

Process only new data to optimize performance and costs.

```sql
config {
  type: "incremental",
  uniqueKey: ["transaction_id"],
  bigquery: {
    partitionBy: "DATE(transaction_date)",
    clusterBy: ["user_id", "product_id"]
  }
}

SELECT
  transaction_id,
  user_id,
  product_id,
  transaction_date,
  amount
FROM ${ref("raw_transactions")}

${ when(incremental(), `WHERE transaction_date > (SELECT MAX(transaction_date) FROM ${self()})`) }
```

**Incremental Strategies:**
- **Append-only**: Add new rows without updates
- **Merge**: Update existing rows and add new ones
- **Insert-overwrite**: Replace partitions with new data

### 3. **Data Quality Assertions**

Built-in testing framework for data validation.

```sql
config {
  type: "table",
  assertions: {
    uniqueKey: ["user_id"],
    nonNull: ["user_id", "email", "created_at"],
    rowConditions: [
      "age >= 0 AND age <= 120",
      "email LIKE '%@%.%'"
    ]
  }
}

SELECT
  user_id,
  email,
  age,
  created_at
FROM ${ref("raw_users")}
```

**Custom Assertions:**
```sql
-- assertions/revenue_check.sqlx
config {
  type: "assertion",
  description: "Ensure daily revenue is within expected range"
}

SELECT
  DATE(transaction_date) as date,
  SUM(amount) as daily_revenue
FROM ${ref("transactions")}
GROUP BY 1
HAVING daily_revenue < 0 OR daily_revenue > 10000000
```

### 4. **Workflow Settings**

Configure compilation and execution behavior.

```yaml
# workflow_settings.yaml
defaultProject: my-gcp-project
defaultDataset: analytics
defaultLocation: US
defaultAssertionDataset: dataform_assertions

vars:
  environment: production
  lookback_days: 30
  min_transaction_amount: 10
```

Access variables in SQLX:
```sql
SELECT *
FROM ${ref("transactions")}
WHERE amount >= ${dataform.projectConfig.vars.min_transaction_amount}
  AND DATE(created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL ${dataform.projectConfig.vars.lookback_days} DAY)
```

## Installation and Setup

### 1. **Create a Dataform Repository**

```bash
# Using gcloud CLI
gcloud dataform repositories create my-dataform-repo \
  --region=us-central1 \
  --project=my-project-id

# Connect to Git repository
gcloud dataform repositories update my-dataform-repo \
  --region=us-central1 \
  --git-remote-settings-url=https://github.com/myorg/dataform-repo.git \
  --git-remote-settings-default-branch=main \
  --git-remote-settings-authentication-token-secret-version=projects/my-project/secrets/github-token/versions/latest
```

### 2. **Initialize Dataform Project Locally**

```bash
# Install Dataform CLI
npm install -g @dataform/cli

# Initialize new project
dataform init my-dataform-project --warehouse bigquery

# Navigate to project
cd my-dataform-project

# Install dependencies
npm install
```

### 3. **Project Structure**

```
my-dataform-project/
├── definitions/           # SQLX files
│   ├── staging/
│   │   ├── stg_users.sqlx
│   │   └── stg_orders.sqlx
│   ├── intermediate/
│   │   └── int_user_orders.sqlx
│   ├── marts/
│   │   └── fct_daily_sales.sqlx
│   └── assertions/
│       └── data_quality_checks.sqlx
├── includes/             # Reusable JavaScript
│   └── utils.js
├── workflow_settings.yaml
└── package.json
```

### 4. **Configure BigQuery Connection**

```yaml
# workflow_settings.yaml
defaultProject: my-gcp-project
defaultDataset: analytics
defaultLocation: US

vars:
  environment: dev
```

## Basic Beginner Examples

### Example 1: Simple Table Creation

```sql
-- definitions/staging/stg_customers.sqlx
config {
  type: "table",
  schema: "staging",
  description: "Cleaned customer data from raw source",
  tags: ["staging", "customers"]
}

SELECT
  customer_id,
  LOWER(TRIM(email)) as email,
  INITCAP(first_name) as first_name,
  INITCAP(last_name) as last_name,
  phone,
  created_at,
  updated_at
FROM ${ref("raw_customers")}
WHERE customer_id IS NOT NULL
```

### Example 2: View Creation

```sql
-- definitions/marts/vw_active_customers.sqlx
config {
  type: "view",
  schema: "marts",
  description: "View of customers with activity in last 90 days"
}

SELECT
  c.customer_id,
  c.email,
  c.first_name,
  c.last_name,
  COUNT(o.order_id) as order_count,
  SUM(o.total_amount) as total_spent,
  MAX(o.order_date) as last_order_date
FROM ${ref("stg_customers")} c
INNER JOIN ${ref("stg_orders")} o
  ON c.customer_id = o.customer_id
WHERE o.order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY 1, 2, 3, 4
```

### Example 3: Incremental Table

```sql
-- definitions/marts/fct_orders.sqlx
config {
  type: "incremental",
  schema: "marts",
  uniqueKey: ["order_id"],
  description: "Fact table for all orders",
  bigquery: {
    partitionBy: "DATE(order_date)",
    clusterBy: ["customer_id", "product_category"]
  }
}

SELECT
  o.order_id,
  o.customer_id,
  o.order_date,
  o.total_amount,
  p.product_category,
  p.product_name,
  CURRENT_TIMESTAMP() as processed_at
FROM ${ref("stg_orders")} o
LEFT JOIN ${ref("stg_products")} p
  ON o.product_id = p.product_id

${when(incremental(), `
  WHERE o.order_date > (
    SELECT MAX(order_date)
    FROM ${self()}
  )
`)}
```

## Intermediate Patterns and Use Cases

### 1. **Slowly Changing Dimensions (SCD Type 2)**

```sql
-- definitions/dimensions/dim_customers_scd2.sqlx
config {
  type: "incremental",
  uniqueKey: ["customer_id", "valid_from"],
  description: "Customer dimension with historical tracking"
}

WITH source_data AS (
  SELECT
    customer_id,
    email,
    first_name,
    last_name,
    address,
    city,
    state,
    updated_at
  FROM ${ref("stg_customers")}
  ${when(incremental(), `WHERE updated_at > (SELECT MAX(valid_to) FROM ${self()})` )}
),

existing_records AS (
  SELECT *
  FROM ${self()}
  WHERE is_current = TRUE
),

changed_records AS (
  SELECT
    s.customer_id,
    s.email,
    s.first_name,
    s.last_name,
    s.address,
    s.city,
    s.state,
    s.updated_at
  FROM source_data s
  INNER JOIN existing_records e
    ON s.customer_id = e.customer_id
  WHERE s.email != e.email
     OR s.address != e.address
     OR s.city != e.city
     OR s.state != e.state
),

new_records AS (
  SELECT
    s.customer_id,
    s.email,
    s.first_name,
    s.last_name,
    s.address,
    s.city,
    s.state,
    s.updated_at
  FROM source_data s
  LEFT JOIN existing_records e
    ON s.customer_id = e.customer_id
  WHERE e.customer_id IS NULL
)

-- Close out changed records
SELECT
  customer_id,
  email,
  first_name,
  last_name,
  address,
  city,
  state,
  valid_from,
  CURRENT_TIMESTAMP() as valid_to,
  FALSE as is_current
FROM existing_records
WHERE customer_id IN (SELECT customer_id FROM changed_records)

UNION ALL

-- Insert new versions of changed records
SELECT
  customer_id,
  email,
  first_name,
  last_name,
  address,
  city,
  state,
  updated_at as valid_from,
  TIMESTAMP('9999-12-31 23:59:59') as valid_to,
  TRUE as is_current
FROM changed_records

UNION ALL

-- Insert completely new records
SELECT
  customer_id,
  email,
  first_name,
  last_name,
  address,
  city,
  state,
  updated_at as valid_from,
  TIMESTAMP('9999-12-31 23:59:59') as valid_to,
  TRUE as is_current
FROM new_records
```

### 2. **Data Quality Framework**

```sql
-- definitions/assertions/data_quality_suite.sqlx
config {
  type: "assertion",
  description: "Comprehensive data quality checks"
}

-- Check for duplicate records
SELECT 'Duplicate Orders' as test_name, COUNT(*) as failures
FROM (
  SELECT order_id, COUNT(*) as cnt
  FROM ${ref("fct_orders")}
  GROUP BY order_id
  HAVING cnt > 1
)

UNION ALL

-- Check for orphaned records
SELECT 'Orphaned Orders' as test_name, COUNT(*) as failures
FROM ${ref("fct_orders")} o
LEFT JOIN ${ref("dim_customers")} c
  ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL

UNION ALL

-- Check for negative amounts
SELECT 'Negative Amounts' as test_name, COUNT(*) as failures
FROM ${ref("fct_orders")}
WHERE total_amount < 0

UNION ALL

-- Check for future dates
SELECT 'Future Dates' as test_name, COUNT(*) as failures
FROM ${ref("fct_orders")}
WHERE order_date > CURRENT_DATE()

HAVING SUM(failures) > 0
```

### 3. **Parameterized Transformations**

```javascript
// includes/date_spine.js
function generateDateSpine(startDate, endDate) {
  return `
    WITH RECURSIVE date_spine AS (
      SELECT DATE('${startDate}') as date
      UNION ALL
      SELECT DATE_ADD(date, INTERVAL 1 DAY)
      FROM date_spine
      WHERE date < DATE('${endDate}')
    )
    SELECT * FROM date_spine
  `;
}

module.exports = { generateDateSpine };
```

```sql
-- definitions/utilities/dim_date.sqlx
config {
  type: "table",
  schema: "utilities",
  description: "Date dimension table"
}

WITH date_spine AS (
  ${generateDateSpine('2020-01-01', '2030-12-31')}
)

SELECT
  date,
  EXTRACT(YEAR FROM date) as year,
  EXTRACT(QUARTER FROM date) as quarter,
  EXTRACT(MONTH FROM date) as month,
  EXTRACT(DAY FROM date) as day,
  EXTRACT(DAYOFWEEK FROM date) as day_of_week,
  FORMAT_DATE('%A', date) as day_name,
  FORMAT_DATE('%B', date) as month_name,
  EXTRACT(WEEK FROM date) as week_of_year,
  CASE WHEN EXTRACT(DAYOFWEEK FROM date) IN (1, 7) THEN TRUE ELSE FALSE END as is_weekend
FROM date_spine
```

## Advanced Architectures and Patterns

### 1. **Medallion Architecture (Bronze-Silver-Gold)**

```sql
-- BRONZE LAYER: Raw data ingestion
-- definitions/bronze/bronze_events.sqlx
config {
  type: "incremental",
  schema: "bronze",
  description: "Raw events from source systems",
  bigquery: {
    partitionBy: "DATE(event_timestamp)",
    clusterBy: ["event_type", "user_id"]
  }
}

SELECT
  event_id,
  event_type,
  user_id,
  event_timestamp,
  event_data,
  _ingestion_timestamp
FROM ${ref("raw_events_stream")}
${when(incremental(), `WHERE _ingestion_timestamp > (SELECT MAX(_ingestion_timestamp) FROM ${self()})`)}

-- SILVER LAYER: Cleaned and validated
-- definitions/silver/silver_events.sqlx
config {
  type: "incremental",
  schema: "silver",
  description: "Cleaned and validated events",
  assertions: {
    nonNull: ["event_id", "event_type", "user_id", "event_timestamp"]
  }
}

SELECT
  event_id,
  UPPER(event_type) as event_type,
  user_id,
  event_timestamp,
  JSON_EXTRACT_SCALAR(event_data, '$.page_url') as page_url,
  JSON_EXTRACT_SCALAR(event_data, '$.referrer') as referrer,
  SAFE_CAST(JSON_EXTRACT_SCALAR(event_data, '$.session_duration') AS INT64) as session_duration,
  _ingestion_timestamp
FROM ${ref("bronze_events")}
WHERE event_id IS NOT NULL
  AND event_type IS NOT NULL
  AND user_id IS NOT NULL
${when(incremental(), `AND _ingestion_timestamp > (SELECT MAX(_ingestion_timestamp) FROM ${self()})`)}

-- GOLD LAYER: Business-ready aggregates
-- definitions/gold/gold_user_engagement.sqlx
config {
  type: "table",
  schema: "gold",
  description: "Daily user engagement metrics for analytics"
}

SELECT
  user_id,
  DATE(event_timestamp) as activity_date,
  COUNT(DISTINCT CASE WHEN event_type = 'PAGE_VIEW' THEN event_id END) as page_views,
  COUNT(DISTINCT CASE WHEN event_type = 'CLICK' THEN event_id END) as clicks,
  COUNT(DISTINCT CASE WHEN event_type = 'PURCHASE' THEN event_id END) as purchases,
  AVG(session_duration) as avg_session_duration,
  COUNT(DISTINCT DATE(event_timestamp)) as days_active
FROM ${ref("silver_events")}
GROUP BY 1, 2
```

### 2. **Event-Driven Incremental Processing**

```sql
-- definitions/marts/fct_user_sessions.sqlx
config {
  type: "incremental",
  schema: "marts",
  uniqueKey: ["session_id"],
  description: "User session facts with event aggregations",
  bigquery: {
    partitionBy: "DATE(session_start)",
    clusterBy: ["user_id"],
    updatePartitionFilter: "DATE(session_start) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)"
  }
}

WITH session_events AS (
  SELECT
    session_id,
    user_id,
    MIN(event_timestamp) as session_start,
    MAX(event_timestamp) as session_end,
    COUNT(*) as event_count,
    COUNT(DISTINCT event_type) as unique_event_types,
    SUM(CASE WHEN event_type = 'PURCHASE' THEN 1 ELSE 0 END) as purchase_count,
    SUM(CASE WHEN event_type = 'PURCHASE' THEN revenue ELSE 0 END) as total_revenue
  FROM ${ref("silver_events")}
  ${when(incremental(), `
    WHERE DATE(event_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
  `)}
  GROUP BY 1, 2
)

SELECT
  s.session_id,
  s.user_id,
  s.session_start,
  s.session_end,
  TIMESTAMP_DIFF(s.session_end, s.session_start, SECOND) as session_duration_seconds,
  s.event_count,
  s.unique_event_types,
  s.purchase_count,
  s.total_revenue,
  CASE
    WHEN s.purchase_count > 0 THEN 'Converted'
    WHEN s.event_count > 10 THEN 'Engaged'
    ELSE 'Browsing'
  END as session_type,
  u.user_segment,
  u.acquisition_channel
FROM session_events s
LEFT JOIN ${ref("dim_users")} u
  ON s.user_id = u.user_id
```

### 3. **Advanced Testing Framework**

```javascript
// includes/test_helpers.js
function generateTestCase(tableName, testName, condition) {
  return `
    SELECT
      '${tableName}' as table_name,
      '${testName}' as test_name,
      COUNT(*) as failure_count,
      CURRENT_TIMESTAMP() as test_timestamp
    FROM ${dataform.ref(tableName)}
    WHERE ${condition}
  `;
}

function compareTableCounts(table1, table2, tolerance = 0) {
  return `
    WITH counts AS (
      SELECT
        (SELECT COUNT(*) FROM ${dataform.ref(table1)}) as count1,
        (SELECT COUNT(*) FROM ${dataform.ref(table2)}) as count2
    )
    SELECT
      '${table1} vs ${table2}' as comparison,
      count1,
      count2,
      ABS(count1 - count2) as difference,
      ${tolerance} as tolerance
    FROM counts
    WHERE ABS(count1 - count2) > ${tolerance}
  `;
}

module.exports = { generateTestCase, compareTableCounts };
```

```sql
-- definitions/tests/comprehensive_tests.sqlx
config {
  type: "assertion",
  schema: "tests",
  description: "Comprehensive test suite for data quality"
}

${generateTestCase('fct_orders', 'Null Order IDs', 'order_id IS NULL')}

UNION ALL

${generateTestCase('fct_orders', 'Invalid Amounts', 'total_amount < 0 OR total_amount > 1000000')}

UNION ALL

${generateTestCase('dim_customers', 'Invalid Emails', "email NOT LIKE '%@%.%'")}

UNION ALL

${compareTableCounts('stg_orders', 'fct_orders', 100)}
```

## Best Practices and Optimization

### 1. **Naming Conventions**

```
Prefix conventions:
- raw_*     : Raw source data
- stg_*     : Staging layer (cleaned)
- int_*     : Intermediate transformations
- fct_*     : Fact tables
- dim_*     : Dimension tables
- rpt_*     : Report/mart tables
- vw_*      : Views
- tmp_*     : Temporary tables
```

### 2. **Performance Optimization**

```sql
config {
  type: "incremental",
  bigquery: {
    -- Partition by date for time-series data
    partitionBy: "DATE(created_at)",
    
    -- Cluster by frequently filtered columns
    clusterBy: ["user_id", "product_category", "region"],
    
    -- Set partition expiration for cost savings
    partitionExpirationDays: 730,
    
    -- Require partition filter for large tables
    requirePartitionFilter: true
  }
}
```

### 3. **Modular Code Organization**

```
definitions/
├── sources/              # Source declarations
│   └── declarations.sqlx
├── staging/             # Cleaned source data
│   ├── stg_customers.sqlx
│   └── stg_orders.sqlx
├── intermediate/        # Business logic
│   ├── int_customer_orders.sqlx
│   └── int_product_metrics.sqlx
├── marts/              # Final analytics tables
│   ├── fct_sales.sqlx
│   ├── dim_customers.sqlx
│   └── dim_products.sqlx
├── reports/            # Specific report tables
│   └── rpt_daily_dashboard.sqlx
└── tests/              # Data quality tests
    └── assertions.sqlx
```

### 4. **Documentation Best Practices**

```sql
config {
  type: "table",
  schema: "marts",
  description: "Daily sales fact table aggregating all transactions",
  columns: {
    sale_date: "Date of the sale transaction",
    customer_id: "Unique identifier for customer (FK to dim_customers)",
    product_id: "Unique identifier for product (FK to dim_products)",
    quantity: "Number of units sold",
    unit_price: "Price per unit at time of sale",
    total_amount: "Total sale amount (quantity * unit_price)",
    discount_amount: "Total discount applied to the sale",
    net_amount: "Net sale amount after discounts"
  },
  tags: ["daily", "sales", "critical"]
}
```

## Common Pitfalls and Solutions

### Pitfall 1: Circular Dependencies

**Problem:**
```sql
-- table_a.sqlx references table_b
SELECT * FROM ${ref("table_b")}

-- table_b.sqlx references table_a
SELECT * FROM ${ref("table_a")}
```

**Solution:**
Break the circular dependency by introducing an intermediate table or restructuring logic.

### Pitfall 2: Incremental Table Issues

**Problem:**
Incremental tables not updating correctly.

**Solution:**
```sql
config {
  type: "incremental",
  uniqueKey: ["id"],  -- Always specify unique key
  bigquery: {
    updatePartitionFilter: "DATE(created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)"
  }
}

-- Use proper incremental logic
${when(incremental(), `
  WHERE created_at > (SELECT MAX(created_at) FROM ${self()})
`)}
```

### Pitfall 3: Missing Dependencies

**Problem:**
Referencing tables without using `ref()` function.

**Solution:**
```sql
-- ❌ Wrong
SELECT * FROM `project.dataset.table`

-- ✅ Correct
SELECT * FROM ${ref("table")}
```

## Comparison with Similar Tools

| Feature | Dataform | dbt | Apache Airflow | Dataflow |
|---------|----------|-----|----------------|----------|
| **Primary Use** | SQL transformation | SQL transformation | Workflow orchestration | Stream/batch processing |
| **Language** | SQL + JavaScript | SQL + Jinja + Python | Python | Java/Python/Go |
| **Version Control** | Git-native | Git-native | External | External |
| **Testing** | Built-in assertions | Built-in tests | Custom | Custom |
| **BigQuery Integration** | Native | Via adapter | Via operators | Via I/O connectors |
| **Incremental Models** | ✅ Yes | ✅ Yes | Manual | ✅ Yes |
| **Dependency Management** | Automatic | Automatic | Manual DAGs | Manual |
| **Learning Curve** | Low (SQL-focused) | Medium | High | High |
| **Managed Service** | ✅ GCP-managed | Cloud or self-hosted | Self-hosted/managed | ✅ GCP-managed |

## Real-World Use Cases

### Use Case 1: E-commerce Analytics Pipeline

```sql
-- Daily sales reporting with customer segmentation
config {
  type: "table",
  schema: "reports",
  description: "Daily sales report with customer segments and product performance"
}

SELECT
  DATE(o.order_date) as report_date,
  c.customer_segment,
  p.product_category,
  COUNT(DISTINCT o.order_id) as order_count,
  COUNT(DISTINCT o.customer_id) as unique_customers,
  SUM(o.total_amount) as gross_revenue,
  SUM(o.discount_amount) as total_discounts,
  SUM(o.total_amount - o.discount_amount) as net_revenue,
  AVG(o.total_amount) as avg_order_value
FROM ${ref("fct_orders")} o
LEFT JOIN ${ref("dim_customers")} c ON o.customer_id = c.customer_id
LEFT JOIN ${ref("dim_products")} p ON o.product_id = p.product_id
WHERE DATE(o.order_date) = CURRENT_DATE() - 1
GROUP BY 1, 2, 3
```

### Use Case 2: Marketing Attribution

```sql
-- Multi-touch attribution model
config {
  type: "table",
  schema: "marketing",
  description: "Marketing attribution using linear model"
}

WITH customer_touchpoints AS (
  SELECT
    customer_id,
    conversion_date,
    touchpoint_date,
    channel,
    campaign,
    ROW_NUMBER() OVER (
      PARTITION BY customer_id, conversion_date
      ORDER BY touchpoint_date
    ) as touchpoint_sequence,
    COUNT(*) OVER (
      PARTITION BY customer_id, conversion_date
    ) as total_touchpoints
  FROM ${ref("customer_journey")}
  WHERE touchpoint_date <= conversion_date
)

SELECT
  customer_id,
  conversion_date,
  channel,
  campaign,
  touchpoint_sequence,
  1.0 / total_touchpoints as attribution_weight,
  conversion_value * (1.0 / total_touchpoints) as attributed_revenue
FROM customer_touchpoints
LEFT JOIN ${ref("conversions")} USING (customer_id, conversion_date)
```

### Use Case 3: IoT Sensor Data Processing

```sql
-- Aggregate sensor readings with anomaly detection
config {
  type: "incremental",
  schema: "iot",
  uniqueKey: ["sensor_id", "reading_hour"],
  bigquery: {
    partitionBy: "reading_hour",
    clusterBy: ["sensor_id", "location"]
  }
}

WITH hourly_readings AS (
  SELECT
    sensor_id,
    location,
    TIMESTAMP_TRUNC(reading_timestamp, HOUR) as reading_hour,
    AVG(temperature) as avg_temperature,
    AVG(humidity) as avg_humidity,
    AVG(pressure) as avg_pressure,
    STDDEV(temperature) as stddev_temperature,
    MIN(temperature) as min_temperature,
    MAX(temperature) as max_temperature,
    COUNT(*) as reading_count
  FROM ${ref("sensor_readings")}
  ${when(incremental(), `
    WHERE reading_timestamp > (SELECT MAX(reading_hour) FROM ${self()})
  `)}
  GROUP BY 1, 2, 3
),

anomalies AS (
  SELECT
    *,
    CASE
      WHEN ABS(avg_temperature - LAG(avg_temperature) OVER (PARTITION BY sensor_id ORDER BY reading_hour)) > 10
        THEN TRUE
      WHEN stddev_temperature > 5
        THEN TRUE
      ELSE FALSE
    END as is_anomaly
  FROM hourly_readings
)

SELECT * FROM anomalies
```

## Performance Considerations

### 1. **Query Optimization**

```sql
-- ❌ Inefficient: Multiple scans
SELECT
  (SELECT COUNT(*) FROM ${ref("orders")} WHERE status = 'completed') as completed,
  (SELECT COUNT(*) FROM ${ref("orders")} WHERE status = 'pending') as pending,
  (SELECT COUNT(*) FROM ${ref("orders")} WHERE status = 'cancelled') as cancelled

-- ✅ Efficient: Single scan with aggregation
SELECT
  COUNTIF(status = 'completed') as completed,
  COUNTIF(status = 'pending') as pending,
  COUNTIF(status = 'cancelled') as cancelled
FROM ${ref("orders")}
```

### 2. **Partitioning Strategy**

```sql
config {
  type: "table",
  bigquery: {
    -- For time-series data
    partitionBy: "DATE(event_timestamp)",
    
    -- For large dimension tables
    clusterBy: ["country", "state", "city"],
    
    -- Optimize partition pruning
    requirePartitionFilter: true
  }
}
```

### 3. **Materialization Strategy**

- **Tables**: Use for frequently accessed data
- **Views**: Use for infrequently accessed or always-fresh data
- **Incremental**: Use for large, append-heavy datasets

## Latest Features (2024)

### 1. **Gemini AI Integration**

Dataform now includes AI-powered code generation using Gemini:

```sql
-- Use natural language comments to generate SQL
-- @gemini: Create a table that calculates customer lifetime value
-- including total orders, total revenue, and average order value
-- for each customer
```

### 2. **Dataplex Integration**

Automatic metadata management and data discovery:

```yaml
# workflow_settings.yaml
dataplexIntegration:
  enabled: true
  lake: my-data-lake
  zone: analytics-zone
```

### 3. **BigLake Tables for Apache Iceberg**

```sql
config {
  type: "table",
  bigquery: {
    tableFormat: "ICEBERG",
    storageUri: "gs://my-bucket/iceberg-tables/customers"
  }
}
```

### 4. **Enhanced Workflow Settings (3.0.0)**

```yaml
# workflow_settings.yaml (new format)
defaultProject: my-project
defaultDataset: analytics
defaultLocation: US

vars:
  environment: production
  
schedules:
  daily_refresh:
    cron: "0 2 * * *"
    tags: ["daily"]
    
  hourly_incremental:
    cron: "0 * * * *"
    tags: ["hourly", "incremental"]
```

## Conclusion

Google Cloud Dataform transforms SQL development into a modern, collaborative, and reliable process. By combining the simplicity of SQL with software engineering best practices, it enables data teams to build robust, scalable, and maintainable data transformation pipelines.

**Key Takeaways:**
- ✅ Version-controlled SQL workflows
- ✅ Automatic dependency management
- ✅ Built-in testing and data quality
- ✅ Incremental processing for efficiency
- ✅ Native BigQuery integration
- ✅ Collaborative development with Git
- ✅ Production-ready orchestration

Whether you're a junior analyst writing your first SQL transformation or an architect designing enterprise data platforms, Dataform provides the tools and structure to succeed.
