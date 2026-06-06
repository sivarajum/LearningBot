# Google Cloud Dataform Interview Questions and Answers

## Beginner Level Questions

### Q1: What is Google Cloud Dataform and what problem does it solve?

**Answer:**

Google Cloud Dataform is a fully managed service for developing, testing, versioning, and scheduling SQL workflows in BigQuery. It enables data teams to transform raw data into analytics-ready datasets using SQL with software engineering best practices.

**Problems It Solves:**

**1. Version Control:**
- Traditional SQL scripts lack proper versioning
- Difficult to track changes and collaborate
- **Solution**: Git-native version control for all SQL code

**2. Dependency Management:**
- Manual tracking of table dependencies is error-prone
- Difficult to determine execution order
- **Solution**: Automatic dependency resolution using `ref()` function

**3. Data Quality:**
- Limited testing capabilities for SQL transformations
- Data quality issues discovered late in production
- **Solution**: Built-in assertions and data quality tests

**4. Documentation:**
- SQL code often lacks context and metadata
- Difficult for new team members to understand pipelines
- **Solution**: Inline documentation with config blocks

**5. Orchestration:**
- Complex scheduling and execution management
- Manual coordination of dependent jobs
- **Solution**: Integrated scheduling with automatic dependency ordering

**Example:**
```sql
-- Dataform automatically manages dependencies
config {
  type: "table",
  description: "Customer orders with enriched data"
}

SELECT
  o.order_id,
  o.customer_id,
  c.customer_name,  -- Automatically waits for dim_customers
  o.total_amount
FROM ${ref("raw_orders")} o
LEFT JOIN ${ref("dim_customers")} c
  ON o.customer_id = c.customer_id
```

---

### Q2: Explain the difference between SQLX and regular SQL.

**Answer:**

SQLX is Dataform's extension of SQL that adds powerful features while maintaining SQL compatibility.

**Key Differences:**

**1. Config Blocks:**
```sql
-- SQLX with config
config {
  type: "table",
  schema: "analytics",
  description: "Daily sales metrics",
  tags: ["daily", "sales"]
}

SELECT * FROM source_table

-- Regular SQL
-- No metadata or configuration
SELECT * FROM source_table
```

**2. Ref Function:**
```sql
-- SQLX: Automatic dependency tracking
SELECT * FROM ${ref("customers")}

-- Regular SQL: Hard-coded references
SELECT * FROM `project.dataset.customers`
```

**3. Assertions:**
```sql
-- SQLX: Built-in data quality
config {
  type: "table",
  assertions: {
    uniqueKey: ["customer_id"],
    nonNull: ["email", "created_at"]
  }
}

-- Regular SQL: Manual validation queries
```

**4. Incremental Logic:**
```sql
-- SQLX: Built-in incremental support
${when(incremental(), `
  WHERE created_at > (SELECT MAX(created_at) FROM ${self()})
`)}

-- Regular SQL: Complex manual logic
```

**5. JavaScript Integration:**
```sql
-- SQLX: Reusable functions
SELECT ${cleanEmail("email")} as email

-- Regular SQL: Repeated logic
SELECT LOWER(TRIM(email)) as email
```

---

### Q3: What are the main components of a Dataform project?

**Answer:**

A Dataform project consists of several key components:

**1. Definitions Directory:**
Contains all SQLX files that define tables, views, and transformations.

```
definitions/
├── staging/          # Cleaned source data
├── intermediate/     # Business logic transformations
├── marts/           # Final analytics tables
└── assertions/      # Data quality tests
```

**2. Includes Directory:**
Reusable JavaScript functions for common transformations.

```javascript
// includes/utils.js
function cleanEmail(column) {
  return `LOWER(TRIM(${column}))`;
}

function calculateAge(birthDateColumn) {
  return `DATE_DIFF(CURRENT_DATE(), ${birthDateColumn}, YEAR)`;
}

module.exports = { cleanEmail, calculateAge };
```

**3. Workflow Settings:**
Configuration file for project-wide settings.

```yaml
# workflow_settings.yaml
defaultProject: my-gcp-project
defaultDataset: analytics
defaultLocation: US

vars:
  environment: production
  lookback_days: 30
```

**4. Package.json:**
Node.js package configuration for dependencies.

```json
{
  "name": "my-dataform-project",
  "dependencies": {
    "@dataform/core": "2.9.0"
  }
}
```

**5. Compilation Output:**
Generated execution graph showing dependencies and execution order (created automatically).

---

### Q4: How does Dataform handle table dependencies?

**Answer:**

Dataform automatically manages dependencies through the `ref()` function and builds an execution graph.

**How It Works:**

**1. Reference Declaration:**
```sql
-- definitions/staging/stg_customers.sqlx
config { type: "table" }
SELECT * FROM ${ref("raw_customers")}

-- definitions/marts/customer_orders.sqlx
config { type: "table" }
SELECT
  c.customer_id,
  c.customer_name,
  COUNT(o.order_id) as order_count
FROM ${ref("stg_customers")} c  -- Depends on stg_customers
LEFT JOIN ${ref("stg_orders")} o  -- Depends on stg_orders
  ON c.customer_id = o.customer_id
GROUP BY 1, 2
```

**2. Automatic Execution Order:**
```
Execution Graph:
1. raw_customers (source)
2. stg_customers (depends on #1)
3. stg_orders (source)
4. customer_orders (depends on #2 and #3)
```

**3. Dependency Visualization:**
Dataform creates a DAG (Directed Acyclic Graph) showing all dependencies.

**4. Error Prevention:**
- Detects circular dependencies
- Ensures tables are created before they're referenced
- Validates all references exist

**Benefits:**
- ✅ No manual orchestration needed
- ✅ Parallel execution where possible
- ✅ Automatic retry on dependency failures
- ✅ Clear visualization of data lineage

---

### Q5: What is the difference between a table, view, and incremental table in Dataform?

**Answer:**

**1. Table:**
Materialized data stored in BigQuery.

```sql
config {
  type: "table",
  schema: "analytics"
}

SELECT
  customer_id,
  SUM(order_amount) as total_spent
FROM ${ref("orders")}
GROUP BY 1
```

**Characteristics:**
- Data is physically stored
- Fast query performance
- Consumes storage
- Rebuilt completely on each run
- **Use when**: Data is frequently accessed and doesn't change often

**2. View:**
Virtual table, query executed on demand.

```sql
config {
  type: "view",
  schema: "analytics"
}

SELECT
  customer_id,
  customer_name,
  email
FROM ${ref("customers")}
WHERE is_active = TRUE
```

**Characteristics:**
- No data storage
- Always shows current data
- Query runs each time view is accessed
- No storage cost, but query cost on each access
- **Use when**: Data must always be fresh or accessed infrequently

**3. Incremental Table:**
Only processes new/changed data.

```sql
config {
  type: "incremental",
  uniqueKey: ["order_id"],
  bigquery: {
    partitionBy: "DATE(order_date)"
  }
}

SELECT
  order_id,
  customer_id,
  order_date,
  amount
FROM ${ref("raw_orders")}

${when(incremental(), `
  WHERE order_date > (SELECT MAX(order_date) FROM ${self()})
`)}
```

**Characteristics:**
- Only processes new data after initial load
- Much faster and cheaper for large datasets
- Requires unique key for updates
- **Use when**: Large datasets with append-heavy patterns

**Comparison Table:**

| Feature | Table | View | Incremental |
|---------|-------|------|-------------|
| Storage | ✅ Yes | ❌ No | ✅ Yes |
| Performance | ⚡ Fast | 🐌 Slow | ⚡ Fast |
| Freshness | Scheduled | Real-time | Scheduled |
| Cost | Storage + Compute | Compute only | Storage + Reduced Compute |
| Best For | Frequent access | Always fresh | Large datasets |

---

### Q6: How do you create and use reusable functions in Dataform?

**Answer:**

Reusable functions are created in the `includes/` directory using JavaScript.

**Step 1: Create Function File**

```javascript
// includes/transformations.js

// Email cleaning function
function cleanEmail(emailColumn) {
  return `LOWER(TRIM(${emailColumn}))`;
}

// Phone number formatting
function formatPhone(phoneColumn) {
  return `REGEXP_REPLACE(${phoneColumn}, r'[^0-9]', '')`;
}

// Calculate age from birthdate
function calculateAge(birthDateColumn) {
  return `DATE_DIFF(CURRENT_DATE(), ${birthDateColumn}, YEAR)`;
}

// Create full name
function fullName(firstNameCol, lastNameCol) {
  return `CONCAT(${firstNameCol}, ' ', ${lastNameCol})`;
}

// Categorize amount
function categorizeAmount(amountColumn) {
  return `
    CASE
      WHEN ${amountColumn} < 100 THEN 'Low'
      WHEN ${amountColumn} < 1000 THEN 'Medium'
      ELSE 'High'
    END
  `;
}

// Export functions
module.exports = {
  cleanEmail,
  formatPhone,
  calculateAge,
  fullName,
  categorizeAmount
};
```

**Step 2: Use Functions in SQLX**

```sql
-- definitions/staging/stg_customers.sqlx
config {
  type: "table",
  schema: "staging",
  description: "Cleaned customer data with standardized fields"
}

SELECT
  customer_id,
  ${cleanEmail("email")} as email,
  ${formatPhone("phone")} as phone,
  ${fullName("first_name", "last_name")} as full_name,
  ${calculateAge("birth_date")} as age,
  birth_date,
  created_at
FROM ${ref("raw_customers")}
WHERE customer_id IS NOT NULL
```

**Step 3: Advanced Reusable Patterns**

```javascript
// includes/date_helpers.js

// Generate date spine
function dateSpine(startDate, endDate) {
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

// Get date range filter
function dateRangeFilter(dateColumn, days) {
  return `${dateColumn} >= DATE_SUB(CURRENT_DATE(), INTERVAL ${days} DAY)`;
}

module.exports = { dateSpine, dateRangeFilter };
```

**Usage:**
```sql
-- definitions/utilities/dim_date.sqlx
config { type: "table" }

WITH dates AS (
  ${dateSpine('2020-01-01', '2030-12-31')}
)

SELECT
  date,
  EXTRACT(YEAR FROM date) as year,
  EXTRACT(MONTH FROM date) as month,
  FORMAT_DATE('%A', date) as day_name
FROM dates
```

**Benefits:**
- ✅ DRY (Don't Repeat Yourself) principle
- ✅ Consistent transformations across project
- ✅ Easy to maintain and update
- ✅ Testable and reusable

---

### Q7: What are assertions in Dataform and how do you use them?

**Answer:**

Assertions are data quality tests that validate your data meets expected criteria.

**Built-in Assertions:**

```sql
config {
  type: "table",
  schema: "staging",
  assertions: {
    // Check for unique values
    uniqueKey: ["customer_id"],
    
    // Check for non-null values
    nonNull: ["customer_id", "email", "created_at"],
    
    // Check row-level conditions
    rowConditions: [
      "age >= 0 AND age <= 120",
      "email LIKE '%@%.%'",
      "total_orders >= 0"
    ]
  }
}

SELECT
  customer_id,
  email,
  age,
  total_orders,
  created_at
FROM ${ref("raw_customers")}
```

**Custom Assertions:**

```sql
-- definitions/assertions/revenue_validation.sqlx
config {
  type: "assertion",
  description: "Validate daily revenue is within expected range"
}

SELECT
  DATE(order_date) as date,
  SUM(amount) as daily_revenue
FROM ${ref("fct_orders")}
GROUP BY 1
HAVING daily_revenue < 0 OR daily_revenue > 10000000
```

**Complex Assertion Example:**

```sql
-- definitions/assertions/data_quality_suite.sqlx
config {
  type: "assertion",
  description: "Comprehensive data quality checks"
}

-- Check for duplicates
SELECT 'Duplicate Customer IDs' as test_name, COUNT(*) as failures
FROM (
  SELECT customer_id, COUNT(*) as cnt
  FROM ${ref("dim_customers")}
  GROUP BY customer_id
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

-- Check for future dates
SELECT 'Future Order Dates' as test_name, COUNT(*) as failures
FROM ${ref("fct_orders")}
WHERE order_date > CURRENT_DATE()

UNION ALL

-- Check for negative amounts
SELECT 'Negative Amounts' as test_name, COUNT(*) as failures
FROM ${ref("fct_orders")}
WHERE total_amount < 0

-- Fail if any test has failures
HAVING SUM(failures) > 0
```

**Assertion Best Practices:**

1. **Test at Each Layer:**
```sql
-- Staging: Basic validation
assertions: { nonNull: ["id", "created_at"] }

-- Intermediate: Business rules
assertions: { rowConditions: ["revenue >= 0"] }

-- Marts: Comprehensive checks
assertions: { uniqueKey: ["customer_id"], nonNull: [...] }
```

2. **Use Descriptive Names:**
```sql
-- ✅ Good
-- assertions/validate_customer_email_format.sqlx

-- ❌ Bad
-- assertions/test1.sqlx
```

3. **Document Expected Behavior:**
```sql
config {
  type: "assertion",
  description: "Ensures all orders have valid customer references and positive amounts"
}
```

---

### Q8: How do you schedule and execute Dataform workflows?

**Answer:**

Dataform workflows can be scheduled and executed in multiple ways:

**1. Manual Execution (Development):**

```bash
# Compile the project
dataform compile

# Run all actions
dataform run

# Run specific tags
dataform run --tags=daily

# Run specific actions
dataform run --actions=staging.stg_customers

# Run with dependencies
dataform run --actions=marts.fct_orders --include-deps
```

**2. Scheduled Execution (Production):**

**Using Google Cloud Console:**
- Navigate to Dataform in GCP Console
- Select your repository
- Create a workflow configuration
- Set schedule using cron expression

**Using Workflow Settings:**
```yaml
# workflow_settings.yaml
defaultProject: my-project
defaultDataset: analytics

schedules:
  daily_full_refresh:
    cron: "0 2 * * *"  # 2 AM daily
    tags: ["daily"]
    timeZone: "America/New_York"
  
  hourly_incremental:
    cron: "0 * * * *"  # Every hour
    tags: ["hourly", "incremental"]
    
  weekly_reports:
    cron: "0 8 * * 1"  # 8 AM every Monday
    tags: ["weekly", "reports"]
```

**3. API-based Execution:**

```python
from google.cloud import dataform_v1beta1

def trigger_dataform_workflow(project_id, region, repository_id):
    client = dataform_v1beta1.DataformClient()
    
    # Create workflow invocation
    parent = f"projects/{project_id}/locations/{region}/repositories/{repository_id}"
    
    workflow_invocation = {
        "compilation_result": f"{parent}/compilationResults/latest",
        "invocation_config": {
            "included_tags": ["daily"],
            "transitive_dependencies_included": True,
            "transitive_dependents_included": False
        }
    }
    
    response = client.create_workflow_invocation(
        parent=parent,
        workflow_invocation=workflow_invocation
    )
    
    return response

# Trigger workflow
result = trigger_dataform_workflow(
    project_id="my-project",
    region="us-central1",
    repository_id="my-dataform-repo"
)
```

**4. Cloud Scheduler Integration:**

```bash
# Create Cloud Scheduler job
gcloud scheduler jobs create http dataform-daily-run \
  --schedule="0 2 * * *" \
  --uri="https://dataform.googleapis.com/v1beta1/projects/my-project/locations/us-central1/repositories/my-repo/workflowInvocations" \
  --http-method=POST \
  --oauth-service-account-email=dataform-scheduler@my-project.iam.gserviceaccount.com \
  --message-body='{"compilationResult":"projects/my-project/locations/us-central1/repositories/my-repo/compilationResults/latest"}'
```

**5. Execution with Tags:**

```sql
-- Tag tables for different schedules
config {
  type: "table",
  tags: ["daily", "critical", "sales"]
}

-- Run only daily tagged tables
-- dataform run --tags=daily
```

**Execution Strategies:**

| Strategy | Use Case | Frequency |
|----------|----------|-----------|
| Full Refresh | Complete rebuild | Daily/Weekly |
| Incremental | Large datasets | Hourly/Daily |
| Tagged Subsets | Specific pipelines | Varies |
| Dependency-based | Single table + deps | On-demand |

---

## Intermediate Level Questions

### Q9: Explain incremental tables and their strategies in detail.

**Answer:**

Incremental tables only process new or changed data, significantly improving performance and reducing costs for large datasets.

**Incremental Strategies:**

**1. Append-Only Strategy:**
Add new rows without updating existing ones.

```sql
config {
  type: "incremental",
  schema: "marts",
  bigquery: {
    partitionBy: "DATE(event_timestamp)",
    clusterBy: ["user_id", "event_type"]
  }
}

SELECT
  event_id,
  user_id,
  event_type,
  event_timestamp,
  event_data
FROM ${ref("raw_events")}

${when(incremental(), `
  WHERE event_timestamp > (
    SELECT MAX(event_timestamp)
    FROM ${self()}
  )
`)}
```

**2. Merge Strategy (Upsert):**
Update existing rows and insert new ones.

```sql
config {
  type: "incremental",
  uniqueKey: ["customer_id"],
  schema: "dimensions",
  bigquery: {
    updatePartitionFilter: "updated_at >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)"
  }
}

SELECT
  customer_id,
  customer_name,
  email,
  address,
  updated_at,
  CURRENT_TIMESTAMP() as processed_at
FROM ${ref("stg_customers")}

${when(incremental(), `
  WHERE updated_at > (
    SELECT MAX(updated_at)
    FROM ${self()}
  )
`)}
```

**3. Insert-Overwrite Strategy:**
Replace specific partitions with new data.

```sql
config {
  type: "incremental",
  schema: "marts",
  bigquery: {
    partitionBy: "DATE(order_date)",
    updatePartitionFilter: "DATE(order_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)"
  }
}

SELECT
  order_id,
  customer_id,
  order_date,
  total_amount
FROM ${ref("stg_orders")}

${when(incremental(), `
  WHERE DATE(order_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)
`)}
```

**4. Slowly Changing Dimension (SCD Type 2):**
Track historical changes with validity periods.

```sql
config {
  type: "incremental",
  uniqueKey: ["customer_id", "valid_from"],
  schema: "dimensions"
}

WITH source AS (
  SELECT
    customer_id,
    customer_name,
    email,
    address,
    updated_at
  FROM ${ref("stg_customers")}
  ${when(incremental(), `
    WHERE updated_at > (SELECT MAX(valid_to) FROM ${self()})
  `)}
),

current_records AS (
  SELECT *
  FROM ${when(incremental(), `${self()}`, `(SELECT NULL as customer_id LIMIT 0)`)}
  WHERE is_current = TRUE
),

changed_records AS (
  SELECT s.*
  FROM source s
  INNER JOIN current_records c
    ON s.customer_id = c.customer_id
  WHERE s.email != c.email
     OR s.address != c.address
),

new_records AS (
  SELECT s.*
  FROM source s
  LEFT JOIN current_records c
    ON s.customer_id = c.customer_id
  WHERE c.customer_id IS NULL
)

-- Close changed records
SELECT
  customer_id,
  customer_name,
  email,
  address,
  valid_from,
  CURRENT_TIMESTAMP() as valid_to,
  FALSE as is_current
FROM current_records
WHERE customer_id IN (SELECT customer_id FROM changed_records)

UNION ALL

-- Insert new versions
SELECT
  customer_id,
  customer_name,
  email,
  address,
  updated_at as valid_from,
  TIMESTAMP('9999-12-31') as valid_to,
  TRUE as is_current
FROM changed_records

UNION ALL

-- Insert new records
SELECT
  customer_id,
  customer_name,
  email,
  address,
  updated_at as valid_from,
  TIMESTAMP('9999-12-31') as valid_to,
  TRUE as is_current
FROM new_records
```

**Performance Optimization:**

```sql
config {
  type: "incremental",
  uniqueKey: ["transaction_id"],
  bigquery: {
    // Partition for efficient filtering
    partitionBy: "DATE(transaction_date)",
    
    // Cluster for query performance
    clusterBy: ["customer_id", "product_id"],
    
    // Only update recent partitions
    updatePartitionFilter: "DATE(transaction_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)",
    
    // Require partition filter for safety
    requirePartitionFilter: true,
    
    // Set partition expiration
    partitionExpirationDays: 730
  }
}
```

**Best Practices:**

1. **Always specify uniqueKey for merge operations**
2. **Use partition filters to limit data scanned**
3. **Test incremental logic with full refresh first**
4. **Monitor for data drift and gaps**
5. **Use appropriate lookback windows**

---

### Q10: How do you implement data quality testing in Dataform?

**Answer:**

Data quality testing in Dataform uses a multi-layered approach with built-in assertions and custom tests.

**Layer 1: Schema-Level Assertions**

```sql
config {
  type: "table",
  schema: "staging",
  assertions: {
    uniqueKey: ["customer_id"],
    nonNull: ["customer_id", "email", "created_at"],
    rowConditions: [
      "email LIKE '%@%.%'",
      "LENGTH(customer_id) = 36",
      "created_at <= CURRENT_TIMESTAMP()"
    ]
  }
}

SELECT * FROM ${ref("raw_customers")}
```

**Layer 2: Custom Assertion Files**

```sql
-- definitions/assertions/customer_quality_checks.sqlx
config {
  type: "assertion",
  description: "Comprehensive customer data quality validations",
  tags: ["data_quality", "customers"]
}

WITH quality_checks AS (
  -- Check 1: Duplicate emails
  SELECT
    'duplicate_emails' as check_name,
    COUNT(*) as failure_count,
    'CRITICAL' as severity
  FROM (
    SELECT email, COUNT(*) as cnt
    FROM ${ref("dim_customers")}
    WHERE email IS NOT NULL
    GROUP BY email
    HAVING cnt > 1
  )
  
  UNION ALL
  
  -- Check 2: Invalid email format
  SELECT
    'invalid_email_format' as check_name,
    COUNT(*) as failure_count,
    'HIGH' as severity
  FROM ${ref("dim_customers")}
  WHERE email IS NOT NULL
    AND NOT REGEXP_CONTAINS(email, r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
  
  UNION ALL
  
  -- Check 3: Missing required fields
  SELECT
    'missing_required_fields' as check_name,
    COUNT(*) as failure_count,
    'CRITICAL' as severity
  FROM ${ref("dim_customers")}
  WHERE customer_name IS NULL
     OR email IS NULL
     OR created_at IS NULL
  
  UNION ALL
  
  -- Check 4: Future created dates
  SELECT
    'future_created_dates' as check_name,
    COUNT(*) as failure_count,
    'MEDIUM' as severity
  FROM ${ref("dim_customers")}
  WHERE created_at > CURRENT_TIMESTAMP()
  
  UNION ALL
  
  -- Check 5: Inactive customers with recent orders
  SELECT
    'inactive_with_orders' as check_name,
    COUNT(DISTINCT c.customer_id) as failure_count,
    'MEDIUM' as severity
  FROM ${ref("dim_customers")} c
  INNER JOIN ${ref("fct_orders")} o
    ON c.customer_id = o.customer_id
  WHERE c.is_active = FALSE
    AND o.order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
)

SELECT
  check_name,
  failure_count,
  severity,
  CURRENT_TIMESTAMP() as check_timestamp
FROM quality_checks
WHERE failure_count > 0
```

**Layer 3: Cross-Table Validation**

```sql
-- definitions/assertions/referential_integrity.sqlx
config {
  type: "assertion",
  description: "Validate referential integrity across tables"
}

-- Orphaned orders (no matching customer)
SELECT
  'orphaned_orders' as test_name,
  COUNT(*) as failure_count
FROM ${ref("fct_orders")} o
LEFT JOIN ${ref("dim_customers")} c
  ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL

UNION ALL

-- Orders with invalid products
SELECT
  'invalid_products' as test_name,
  COUNT(*) as failure_count
FROM ${ref("fct_orders")} o
LEFT JOIN ${ref("dim_products")} p
  ON o.product_id = p.product_id
WHERE p.product_id IS NULL

UNION ALL

-- Mismatched aggregations
SELECT
  'aggregation_mismatch' as test_name,
  ABS(
    (SELECT SUM(total_amount) FROM ${ref("fct_orders")}) -
    (SELECT SUM(order_total) FROM ${ref("customer_summary")})
  ) as failure_count

HAVING SUM(failure_count) > 0
```

**Layer 4: Statistical Anomaly Detection**

```sql
-- definitions/assertions/anomaly_detection.sqlx
config {
  type: "assertion",
  description: "Detect statistical anomalies in daily metrics"
}

WITH daily_metrics AS (
  SELECT
    DATE(order_date) as date,
    COUNT(*) as order_count,
    SUM(total_amount) as revenue
  FROM ${ref("fct_orders")}
  WHERE DATE(order_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  GROUP BY 1
),

statistics AS (
  SELECT
    AVG(order_count) as avg_orders,
    STDDEV(order_count) as stddev_orders,
    AVG(revenue) as avg_revenue,
    STDDEV(revenue) as stddev_revenue
  FROM daily_metrics
  WHERE date < CURRENT_DATE()
),

today_metrics AS (
  SELECT *
  FROM daily_metrics
  WHERE date = CURRENT_DATE() - 1
)

SELECT
  'daily_order_anomaly' as test_name,
  1 as failure_count
FROM today_metrics t
CROSS JOIN statistics s
WHERE t.order_count < (s.avg_orders - 3 * s.stddev_orders)
   OR t.order_count > (s.avg_orders + 3 * s.stddev_orders)

UNION ALL

SELECT
  'daily_revenue_anomaly' as test_name,
  1 as failure_count
FROM today_metrics t
CROSS JOIN statistics s
WHERE t.revenue < (s.avg_revenue - 3 * s.stddev_revenue)
   OR t.revenue > (s.avg_revenue + 3 * s.stddev_revenue)
```

**Layer 5: Business Rule Validation**

```sql
-- definitions/assertions/business_rules.sqlx
config {
  type: "assertion",
  description: "Validate business logic rules"
}

-- Rule 1: Order total matches line items
SELECT
  'order_total_mismatch' as rule_name,
  COUNT(*) as violations
FROM ${ref("fct_orders")} o
LEFT JOIN (
  SELECT
    order_id,
    SUM(quantity * unit_price) as calculated_total
  FROM ${ref("fct_order_lines")}
  GROUP BY order_id
) l ON o.order_id = l.order_id
WHERE ABS(o.total_amount - COALESCE(l.calculated_total, 0)) > 0.01

UNION ALL

-- Rule 2: Discount doesn't exceed total
SELECT
  'discount_exceeds_total' as rule_name,
  COUNT(*) as violations
FROM ${ref("fct_orders")}
WHERE discount_amount > total_amount

UNION ALL

-- Rule 3: Subscription end after start
SELECT
  'invalid_subscription_dates' as rule_name,
  COUNT(*) as violations
FROM ${ref("subscriptions")}
WHERE end_date < start_date

HAVING SUM(violations) > 0
```

**Testing Framework Helper:**

```javascript
// includes/test_helpers.js

function createQualityTest(tableName, testName, condition, severity = 'HIGH') {
  return `
    SELECT
      '${testName}' as test_name,
      '${tableName}' as table_name,
      COUNT(*) as failure_count,
      '${severity}' as severity,
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
      '${table1}_vs_${table2}_count_mismatch' as test_name,
      ABS(count1 - count2) as failure_count,
      'MEDIUM' as severity
    FROM counts
    WHERE ABS(count1 - count2) > ${tolerance}
  `;
}

module.exports = { createQualityTest, compareTableCounts };
```

**Usage:**
```sql
-- definitions/assertions/automated_tests.sqlx
config {
  type: "assertion",
  description: "Automated quality tests"
}

${createQualityTest('dim_customers', 'null_emails', 'email IS NULL', 'CRITICAL')}

UNION ALL

${createQualityTest('fct_orders', 'negative_amounts', 'total_amount < 0', 'CRITICAL')}

UNION ALL

${compareTableCounts('stg_orders', 'fct_orders', 10)}
```

**Best Practices:**

1. **Test at every layer** (staging, intermediate, marts)
2. **Use severity levels** (CRITICAL, HIGH, MEDIUM, LOW)
3. **Document expected behavior** in assertions
4. **Monitor test results** and alert on failures
5. **Balance coverage vs. performance**

---

### Q11: How do you organize a Dataform project following best practices?

**Answer:**

A well-organized Dataform project follows a layered architecture with clear naming conventions and modular structure.

**Recommended Project Structure:**

```
dataform-project/
├── definitions/
│   ├── sources/
│   │   └── declarations.sqlx          # External table declarations
│   │
│   ├── staging/                       # Layer 1: Cleaned source data
│   │   ├── crm/
│   │   │   ├── stg_crm__customers.sqlx
│   │   │   ├── stg_crm__contacts.sqlx
│   │   │   └── stg_crm__accounts.sqlx
│   │   ├── ecommerce/
│   │   │   ├── stg_ecom__orders.sqlx
│   │   │   ├── stg_ecom__products.sqlx
│   │   │   └── stg_ecom__payments.sqlx
│   │   └── marketing/
│   │       ├── stg_mkt__campaigns.sqlx
│   │       └── stg_mkt__events.sqlx
│   │
│   ├── intermediate/                  # Layer 2: Business logic
│   │   ├── customer/
│   │   │   ├── int_customer__orders.sqlx
│   │   │   ├── int_customer__lifetime_value.sqlx
│   │   │   └── int_customer__segments.sqlx
│   │   ├── product/
│   │   │   ├── int_product__performance.sqlx
│   │   │   └── int_product__inventory.sqlx
│   │   └── finance/
│   │       ├── int_finance__revenue.sqlx
│   │       └── int_finance__costs.sqlx
│   │
│   ├── marts/                         # Layer 3: Business-ready tables
│   │   ├── core/
│   │   │   ├── dim_customers.sqlx
│   │   │   ├── dim_products.sqlx
│   │   │   ├── dim_dates.sqlx
│   │   │   ├── fct_orders.sqlx
│   │   │   └── fct_order_lines.sqlx
│   │   ├── marketing/
│   │   │   ├── fct_campaign_performance.sqlx
│   │   │   └── dim_campaigns.sqlx
│   │   └── finance/
│   │       ├── fct_daily_revenue.sqlx
│   │       └── fct_monthly_summary.sqlx
│   │
│   ├── reports/                       # Layer 4: Specific reports
│   │   ├── rpt_executive_dashboard.sqlx
│   │   ├── rpt_sales_performance.sqlx
│   │   └── rpt_customer_cohorts.sqlx
│   │
│   ├── utilities/                     # Utility tables
│   │   ├── dim_date.sqlx
│   │   └── dim_time.sqlx
│   │
│   └── tests/                         # Data quality tests
│       ├── assertions/
│       │   ├── test_referential_integrity.sqlx
│       │   ├── test_data_quality.sqlx
│       │   └── test_business_rules.sqlx
│       └── schema_tests/
│           ├── test_staging_layer.sqlx
│           └── test_marts_layer.sqlx
│
├── includes/                          # Reusable functions
│   ├── transformations.js
│   ├── date_helpers.js
│   ├── string_utils.js
│   └── test_helpers.js
│
├── workflow_settings.yaml             # Project configuration
├── package.json                       # Dependencies
└── README.md                          # Documentation
```

**Naming Conventions:**

```sql
-- Prefix conventions:
-- raw_*     : Raw source data (declarations)
-- stg_*     : Staging layer (cleaned)
-- int_*     : Intermediate layer (business logic)
-- fct_*     : Fact tables
-- dim_*     : Dimension tables
-- rpt_*     : Report tables
-- vw_*      : Views
-- tmp_*     : Temporary tables

-- Source system prefix:
-- stg_crm__*    : CRM system staging
-- stg_ecom__*   : E-commerce system staging
-- stg_mkt__*    : Marketing system staging

-- Examples:
-- stg_crm__customers.sqlx
-- int_customer__lifetime_value.sqlx
-- fct_orders.sqlx
-- dim_customers.sqlx
-- rpt_daily_sales.sqlx
```

**Layer-Specific Configurations:**

```sql
-- STAGING LAYER: Light transformations only
config {
  type: "table",
  schema: "staging",
  description: "Cleaned customer data from CRM",
  tags: ["staging", "crm", "daily"],
  assertions: {
    nonNull: ["customer_id", "created_at"]
  }
}

SELECT
  customer_id,
  LOWER(TRIM(email)) as email,
  INITCAP(first_name) as first_name,
  created_at
FROM ${ref("raw_crm_customers")}
WHERE customer_id IS NOT NULL
```

```sql
-- INTERMEDIATE LAYER: Business logic
config {
  type: "table",
  schema: "intermediate",
  description: "Customer lifetime value calculation",
  tags: ["intermediate", "customer", "daily"]
}

SELECT
  c.customer_id,
  COUNT(DISTINCT o.order_id) as total_orders,
  SUM(o.total_amount) as lifetime_value,
  AVG(o.total_amount) as avg_order_value,
  MAX(o.order_date) as last_order_date
FROM ${ref("stg_crm__customers")} c
LEFT JOIN ${ref("stg_ecom__orders")} o
  ON c.customer_id = o.customer_id
GROUP BY 1
```

```sql
-- MARTS LAYER: Business-ready dimensions/facts
config {
  type: "table",
  schema: "marts",
  description: "Customer dimension with enriched attributes",
  tags: ["marts", "dimension", "daily"],
  bigquery: {
    clusterBy: ["customer_segment", "country"]
  }
}

SELECT
  c.customer_id,
  c.email,
  c.first_name,
  c.last_name,
  ltv.lifetime_value,
  ltv.total_orders,
  seg.customer_segment,
  c.country,
  c.created_at
FROM ${ref("stg_crm__customers")} c
LEFT JOIN ${ref("int_customer__lifetime_value")} ltv
  ON c.customer_id = ltv.customer_id
LEFT JOIN ${ref("int_customer__segments")} seg
  ON c.customer_id = seg.customer_id
```

**Workflow Settings Organization:**

```yaml
# workflow_settings.yaml
defaultProject: my-gcp-project
defaultDataset: analytics
defaultLocation: US
defaultAssertionDataset: data_quality

vars:
  # Environment
  environment: production
  
  # Date ranges
  lookback_days: 30
  partition_retention_days: 730
  
  # Business rules
  min_order_amount: 10
  max_discount_percent: 50
  
  # Data quality
  max_null_percent: 5
  max_duplicate_percent: 1

# Schema mappings
schemas:
  staging: staging
  intermediate: intermediate
  marts: marts
  reports: reports

# Tags for scheduling
tags:
  daily: ["staging", "intermediate", "marts"]
  hourly: ["incremental"]
  weekly: ["reports"]
```

**Documentation Standards:**

```sql
config {
  type: "table",
  schema: "marts",
  description: `
    Fact table for all customer orders.
    
    Grain: One row per order
    
    Updates: Daily full refresh at 2 AM UTC
    
    Dependencies:
    - stg_ecom__orders: Source order data
    - dim_customers: Customer attributes
    - dim_products: Product attributes
    
    Business Rules:
    - Only includes completed orders (status = 'COMPLETED')
    - Excludes test orders (is_test = FALSE)
    - Revenue excludes tax and shipping
    
    SLA: Available by 3 AM UTC daily
  `,
  columns: {
    order_id: "Unique order identifier (PK)",
    customer_id: "Customer identifier (FK to dim_customers)",
    product_id: "Product identifier (FK to dim_products)",
    order_date: "Date order was placed",
    total_amount: "Total order amount excluding tax/shipping",
    status: "Order status (COMPLETED, CANCELLED, PENDING)"
  },
  tags: ["marts", "orders", "daily", "critical"]
}
```

**Best Practices Summary:**

1. ✅ **Use consistent naming conventions**
2. ✅ **Organize by layer and domain**
3. ✅ **Document thoroughly**
4. ✅ **Tag appropriately for scheduling**
5. ✅ **Test at every layer**
6. ✅ **Keep staging layer simple**
7. ✅ **Centralize business logic in intermediate**
8. ✅ **Make marts business-ready**
9. ✅ **Version control everything**
10. ✅ **Use modular, reusable code**

---

## Advanced Level Questions

### Q12: How do you implement a Medallion Architecture (Bronze-Silver-Gold) in Dataform?

**Answer:**

The Medallion Architecture organizes data into three layers: Bronze (raw), Silver (cleaned), and Gold (business-ready).

**Complete Implementation:**

**Bronze Layer: Raw Data Ingestion**

```sql
-- definitions/bronze/bronze_events.sqlx
config {
  type: "incremental",
  schema: "bronze",
  description: "Raw events from source systems - no transformations",
  tags: ["bronze", "raw", "hourly"],
  bigquery: {
    partitionBy: "DATE(_ingestion_timestamp)",
    clusterBy: ["event_type", "source_system"],
    partitionExpirationDays: 90
  }
}

-- Raw data with minimal processing
SELECT
  event_id,
  event_type,
  source_system,
  user_id,
  event_timestamp,
  event_data,  -- JSON payload
  _ingestion_timestamp,
  _source_file,
  _batch_id
FROM ${ref("raw_events_stream")}

${when(incremental(), `
  WHERE _ingestion_timestamp > (
    SELECT MAX(_ingestion_timestamp)
    FROM ${self()}
  )
`)}
```

**Silver Layer: Cleaned and Validated**

```sql
-- definitions/silver/silver_events.sqlx
config {
  type: "incremental",
  schema: "silver",
  description: "Cleaned and validated events with parsed JSON",
  tags: ["silver", "cleaned", "hourly"],
  assertions: {
    nonNull: ["event_id", "event_type", "user_id", "event_timestamp"],
    rowConditions: [
      "event_timestamp <= CURRENT_TIMESTAMP()",
      "LENGTH(event_id) = 36"
    ]
  },
  bigquery: {
    partitionBy: "DATE(event_timestamp)",
    clusterBy: ["event_type", "user_id"],
    partitionExpirationDays: 365
  }
}

WITH parsed_events AS (
  SELECT
    event_id,
    UPPER(TRIM(event_type)) as event_type,
    source_system,
    user_id,
    event_timestamp,
    
    -- Parse JSON fields
    JSON_EXTRACT_SCALAR(event_data, '$.page_url') as page_url,
    JSON_EXTRACT_SCALAR(event_data, '$.referrer') as referrer,
    JSON_EXTRACT_SCALAR(event_data, '$.device_type') as device_type,
    JSON_EXTRACT_SCALAR(event_data, '$.browser') as browser,
    SAFE_CAST(JSON_EXTRACT_SCALAR(event_data, '$.session_duration') AS INT64) as session_duration,
    SAFE_CAST(JSON_EXTRACT_SCALAR(event_data, '$.revenue') AS FLOAT64) as revenue,
    
    -- Metadata
    _ingestion_timestamp,
    CURRENT_TIMESTAMP() as _processed_timestamp
  FROM ${ref("bronze_events")}
  
  ${when(incremental(), `
    WHERE _ingestion_timestamp > (
      SELECT MAX(_ingestion_timestamp)
      FROM ${self()}
    )
  `)}
)

-- Data quality filtering
SELECT *
FROM parsed_events
WHERE event_id IS NOT NULL
  AND event_type IS NOT NULL
  AND user_id IS NOT NULL
  AND event_timestamp IS NOT NULL
  AND event_timestamp <= CURRENT_TIMESTAMP()
  -- Remove duplicates
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY event_id
    ORDER BY _ingestion_timestamp DESC
  ) = 1
```

**Gold Layer: Business-Ready Aggregates**

```sql
-- definitions/gold/gold_user_daily_activity.sqlx
config {
  type: "table",
  schema: "gold",
  description: "Daily user activity metrics for business analytics",
  tags: ["gold", "analytics", "daily"],
  bigquery: {
    partitionBy: "activity_date",
    clusterBy: ["user_segment", "device_type"],
    partitionExpirationDays: 730
  }
}

WITH daily_activity AS (
  SELECT
    user_id,
    DATE(event_timestamp) as activity_date,
    device_type,
    
    -- Engagement metrics
    COUNT(DISTINCT event_id) as total_events,
    COUNT(DISTINCT CASE WHEN event_type = 'PAGE_VIEW' THEN event_id END) as page_views,
    COUNT(DISTINCT CASE WHEN event_type = 'CLICK' THEN event_id END) as clicks,
    COUNT(DISTINCT CASE WHEN event_type = 'PURCHASE' THEN event_id END) as purchases,
    
    -- Session metrics
    COUNT(DISTINCT session_id) as sessions,
    AVG(session_duration) as avg_session_duration,
    
    -- Revenue metrics
    SUM(CASE WHEN event_type = 'PURCHASE' THEN revenue ELSE 0 END) as total_revenue,
    
    -- Engagement score
    COUNT(DISTINCT event_id) * 1.0 +
    COUNT(DISTINCT CASE WHEN event_type = 'PURCHASE' THEN event_id END) * 10.0 as engagement_score
    
  FROM ${ref("silver_events")}
  WHERE DATE(event_timestamp) = CURRENT_DATE() - 1
  GROUP BY 1, 2, 3
)

SELECT
  a.*,
  u.user_segment,
  u.acquisition_channel,
  u.signup_date,
  DATE_DIFF(a.activity_date, u.signup_date, DAY) as days_since_signup,
  
  -- User lifecycle stage
  CASE
    WHEN DATE_DIFF(a.activity_date, u.signup_date, DAY) <= 7 THEN 'New'
    WHEN a.purchases > 0 THEN 'Active Buyer'
    WHEN a.engagement_score > 50 THEN 'Engaged'
    ELSE 'Casual'
  END as lifecycle_stage
  
FROM daily_activity a
LEFT JOIN ${ref("dim_users")} u
  ON a.user_id = u.user_id
```

**Gold Layer: Business Metrics**

```sql
-- definitions/gold/gold_product_performance.sqlx
config {
  type: "table",
  schema: "gold",
  description: "Product performance metrics for business reporting",
  tags: ["gold", "products", "daily"]
}

WITH product_metrics AS (
  SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    DATE(e.event_timestamp) as metric_date,
    
    -- View metrics
    COUNT(DISTINCT CASE WHEN e.event_type = 'PRODUCT_VIEW' THEN e.user_id END) as unique_viewers,
    COUNT(CASE WHEN e.event_type = 'PRODUCT_VIEW' THEN 1 END) as total_views,
    
    -- Cart metrics
    COUNT(DISTINCT CASE WHEN e.event_type = 'ADD_TO_CART' THEN e.user_id END) as users_added_to_cart,
    COUNT(CASE WHEN e.event_type = 'ADD_TO_CART' THEN 1 END) as times_added_to_cart,
    
    -- Purchase metrics
    COUNT(DISTINCT CASE WHEN e.event_type = 'PURCHASE' THEN e.user_id END) as unique_buyers,
    COUNT(CASE WHEN e.event_type = 'PURCHASE' THEN 1 END) as units_sold,
    SUM(CASE WHEN e.event_type = 'PURCHASE' THEN e.revenue ELSE 0 END) as total_revenue,
    
  FROM ${ref("silver_events")} e
  LEFT JOIN ${ref("dim_products")} p
    ON JSON_EXTRACT_SCALAR(e.event_data, '$.product_id') = p.product_id
  WHERE DATE(e.event_timestamp) = CURRENT_DATE() - 1
    AND p.product_id IS NOT NULL
  GROUP BY 1, 2, 3, 4, 5
)

SELECT
  *,
  -- Conversion rates
  SAFE_DIVIDE(users_added_to_cart, unique_viewers) as view_to_cart_rate,
  SAFE_DIVIDE(unique_buyers, users_added_to_cart) as cart_to_purchase_rate,
  SAFE_DIVIDE(unique_buyers, unique_viewers) as overall_conversion_rate,
  
  -- Revenue metrics
  SAFE_DIVIDE(total_revenue, units_sold) as avg_selling_price,
  
  -- Engagement score
  (total_views * 1) + (times_added_to_cart * 5) + (units_sold * 10) as product_engagement_score
  
FROM product_metrics
```

**Data Quality Across Layers:**

```sql
-- definitions/tests/medallion_quality_checks.sqlx
config {
  type: "assertion",
  description: "Quality checks across medallion layers"
}

-- Bronze to Silver: Check for data loss
WITH bronze_count AS (
  SELECT COUNT(*) as cnt
  FROM ${ref("bronze_events")}
  WHERE DATE(_ingestion_timestamp) = CURRENT_DATE() - 1
),
silver_count AS (
  SELECT COUNT(*) as cnt
  FROM ${ref("silver_events")}
  WHERE DATE(_processed_timestamp) = CURRENT_DATE() - 1
)

SELECT
  'bronze_to_silver_data_loss' as test_name,
  ABS(b.cnt - s.cnt) as difference,
  b.cnt as bronze_count,
  s.cnt as silver_count
FROM bronze_count b
CROSS JOIN silver_count s
WHERE ABS(b.cnt - s.cnt) > (b.cnt * 0.05)  -- More than 5% difference

UNION ALL

-- Silver to Gold: Validate aggregations
SELECT
  'silver_gold_revenue_mismatch' as test_name,
  ABS(silver_revenue - gold_revenue) as difference,
  silver_revenue,
  gold_revenue
FROM (
  SELECT
    SUM(revenue) as silver_revenue
  FROM ${ref("silver_events")}
  WHERE DATE(event_timestamp) = CURRENT_DATE() - 1
    AND event_type = 'PURCHASE'
) s
CROSS JOIN (
  SELECT
    SUM(total_revenue) as gold_revenue
  FROM ${ref("gold_user_daily_activity")}
  WHERE activity_date = CURRENT_DATE() - 1
) g
WHERE ABS(silver_revenue - gold_revenue) > 0.01
```

**Benefits of Medallion Architecture:**

1. **Clear Separation of Concerns**
   - Bronze: Raw data preservation
   - Silver: Data quality and standardization
   - Gold: Business logic and aggregations

2. **Incremental Processing**
   - Each layer processes only new data
   - Reduces compute costs
   - Faster execution times

3. **Data Quality Gates**
   - Validate at each layer
   - Early detection of issues
   - Prevent bad data propagation

4. **Flexibility**
   - Easy to rebuild layers independently
   - Multiple gold layers from same silver
   - Support different use cases

---

### Q13: How do you optimize Dataform workflows for performance and cost?

**Answer:**

Performance and cost optimization in Dataform involves multiple strategies across query optimization, partitioning, incremental processing, and resource management.

**1. Partitioning and Clustering**

```sql
config {
  type: "table",
  schema: "marts",
  bigquery: {
    // Partition by date for time-series data
    partitionBy: "DATE(order_date)",
    
    // Cluster by frequently filtered columns (max 4)
    clusterBy: ["customer_id", "product_category", "region"],
    
    // Set partition expiration for cost savings
    partitionExpirationDays: 730,  // 2 years
    
    // Require partition filter to prevent full scans
    requirePartitionFilter: true
  }
}

SELECT
  order_id,
  customer_id,
  product_category,
  region,
  order_date,
  total_amount
FROM ${ref("stg_orders")}
```

**2. Incremental Processing with Partition Filters**

```sql
config {
  type: "incremental",
  uniqueKey: ["transaction_id"],
  bigquery: {
    partitionBy: "DATE(transaction_date)",
    clusterBy: ["user_id", "merchant_id"],
    
    // Only update recent partitions
    updatePartitionFilter: "DATE(transaction_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)"
  }
}

SELECT
  transaction_id,
  user_id,
  merchant_id,
  transaction_date,
  amount,
  CURRENT_TIMESTAMP() as processed_at
FROM ${ref("stg_transactions")}

${when(incremental(), `
  -- Only process last 7 days
  WHERE DATE(transaction_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
`)}
```

**3. Query Optimization Techniques**

```sql
-- ❌ INEFFICIENT: Multiple table scans
config { type: "table" }

SELECT
  customer_id,
  (SELECT COUNT(*) FROM ${ref("orders")} o WHERE o.customer_id = c.customer_id) as order_count,
  (SELECT SUM(amount) FROM ${ref("orders")} o WHERE o.customer_id = c.customer_id) as total_spent,
  (SELECT MAX(order_date) FROM ${ref("orders")} o WHERE o.customer_id = c.customer_id) as last_order
FROM ${ref("customers")} c

-- ✅ EFFICIENT: Single table scan with aggregation
config { type: "table" }

SELECT
  c.customer_id,
  COUNT(o.order_id) as order_count,
  SUM(o.amount) as total_spent,
  MAX(o.order_date) as last_order
FROM ${ref("customers")} c
LEFT JOIN ${ref("orders")} o
  ON c.customer_id = o.customer_id
GROUP BY 1
```

**4. Materialization Strategy**

```sql
-- Use views for infrequently accessed data
config {
  type: "view",  // No storage cost
  schema: "reports"
}

SELECT * FROM ${ref("fct_orders")}
WHERE order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)

-- Use tables for frequently accessed data
config {
  type: "table",  // Fast queries
  schema: "marts"
}

SELECT * FROM ${ref("customer_metrics")}

-- Use incremental for large, append-heavy datasets
config {
  type: "incremental",  // Efficient updates
  uniqueKey: ["event_id"]
}

SELECT * FROM ${ref("events")}
${when(incremental(), `WHERE event_date > (SELECT MAX(event_date) FROM ${self()})`)}
```

**5. Reduce Data Scanned**

```sql
config {
  type: "table",
  bigquery: {
    partitionBy: "DATE(order_date)",
    clusterBy: ["customer_segment"]
  }
}

-- ❌ Scans all data
SELECT *
FROM ${ref("orders")}

-- ✅ Scans only necessary partitions and clusters
SELECT *
FROM ${ref("orders")}
WHERE DATE(order_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND customer_segment = 'Premium'
```

**6. Optimize Joins**

```sql
-- ❌ INEFFICIENT: Large table first
SELECT *
FROM ${ref("large_fact_table")} f  -- 1B rows
LEFT JOIN ${ref("small_dim_table")} d  -- 1K rows
  ON f.dim_id = d.dim_id

-- ✅ EFFICIENT: Small table first (broadcast join)
SELECT *
FROM ${ref("small_dim_table")} d  -- 1K rows
LEFT JOIN ${ref("large_fact_table")} f  -- 1B rows
  ON d.dim_id = f.dim_id
WHERE f.order_date >= CURRENT_DATE() - 30
```

**7. Use Approximate Aggregations**

```sql
-- ❌ Exact count (expensive)
SELECT
  customer_segment,
  COUNT(DISTINCT customer_id) as unique_customers
FROM ${ref("large_table")}
GROUP BY 1

-- ✅ Approximate count (much faster, 98%+ accurate)
SELECT
  customer_segment,
  APPROX_COUNT_DISTINCT(customer_id) as unique_customers
FROM ${ref("large_table")}
GROUP BY 1
```

**8. Batch Processing Strategy**

```yaml
# workflow_settings.yaml

schedules:
  # Heavy transformations during off-peak hours
  daily_full_refresh:
    cron: "0 2 * * *"  # 2 AM
    tags: ["daily", "heavy"]
  
  # Light incremental updates during business hours
  hourly_incremental:
    cron: "0 * * * *"  # Every hour
    tags: ["hourly", "incremental"]
  
  # Reports after data is ready
  morning_reports:
    cron: "0 6 * * *"  # 6 AM
    tags: ["reports"]
```

**9. Selective Column Selection**

```sql
-- ❌ Select all columns
SELECT *
FROM ${ref("wide_table")}  -- 200 columns

-- ✅ Select only needed columns
SELECT
  customer_id,
  order_date,
  total_amount
FROM ${ref("wide_table")}
```

**10. Cost Monitoring**

```sql
-- definitions/monitoring/query_cost_analysis.sqlx
config {
  type: "table",
  schema: "monitoring",
  description: "Track query costs and data scanned"
}

SELECT
  table_name,
  DATE(creation_time) as execution_date,
  SUM(total_bytes_processed) / POW(10, 12) as tb_processed,
  SUM(total_bytes_processed) / POW(10, 12) * 5 as estimated_cost_usd,  -- $5 per TB
  COUNT(*) as query_count,
  AVG(total_slot_ms) / 1000 as avg_slot_seconds
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE'
GROUP BY 1, 2
ORDER BY tb_processed DESC
```

**Performance Optimization Checklist:**

- ✅ Use partitioning for time-series data
- ✅ Cluster by frequently filtered columns
- ✅ Implement incremental processing
- ✅ Use partition filters in queries
- ✅ Optimize join order (small table first)
- ✅ Select only necessary columns
- ✅ Use approximate functions when possible
- ✅ Set partition expiration
- ✅ Require partition filters for large tables
- ✅ Schedule heavy jobs during off-peak hours
- ✅ Monitor query costs regularly
- ✅ Use views for infrequent access
- ✅ Use tables for frequent access
- ✅ Avoid SELECT *

**Cost Optimization Results:**

| Optimization | Typical Savings |
|--------------|----------------|
| Partitioning + Clustering | 60-80% |
| Incremental Processing | 70-90% |
| Column Selection | 30-50% |
| Approximate Aggregations | 50-70% |
| Partition Expiration | 20-40% |

---

## Key Takeaways

1. **Dataform transforms SQL development** with version control, dependency management, and testing
2. **SQLX extends SQL** with config blocks, ref() function, and built-in assertions
3. **Incremental tables** optimize performance and costs for large datasets
4. **Data quality testing** is built-in with assertions and custom tests
5. **Medallion architecture** (Bronze-Silver-Gold) provides clear data organization
6. **Performance optimization** through partitioning, clustering, and incremental processing
7. **Modular organization** with clear naming conventions and layered structure
8. **Latest features** include Gemini AI integration, Dataplex integration, and BigLake support
9. **Cost optimization** through smart materialization and query optimization
10. **Production-ready** with scheduling, monitoring, and orchestration capabilities
