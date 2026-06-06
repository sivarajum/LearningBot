# Google Cloud Dataform: The Complete Guide (Zero to Architect)

This guide serves as a comprehensive manual for Google Cloud Dataform, covering every aspect from initial setup to enterprise-grade architecture and optimization.

---

## 🏗️ Phase 1: Foundations & Setup

### 1. **Core Concepts Review**
- **SQLX**: Dataform's SQL dialect. Combines SQL with a `config` block (YAML-like) and JavaScript.
- **Dependency Management**: Use `${ref("table_name")}` to let Dataform build the DAG (Directed Acyclic Graph).
- **Compilation**: Dataform compiles SQLX + JS into standard BigQuery SQL.
- **Execution**: Orchestrates the order of execution based on dependencies.

### 2. **Project Initialization**
```bash
# 1. Install Dataform CLI globally
npm install -g @dataform/cli

# 2. Init project (creates standard folder structure)
dataform init my_analytics_project --warehouse bigquery

# 3. Install core dependencies
cd my_analytics_project
npm install
```

### 3. **The Dataform Config (`workflow_settings.yaml`)**
The brain of your project. Defines global settings and variables.
```yaml
defaultProject: my-gcp-prod-project
defaultLocation: US
defaultDataset: analytics_prod
defaultAssertionDataset: analytics_assertions

# Project-wide variables accessed via ${dataform.projectConfig.vars.variable_name}
vars:
  env: production
  start_date: "2024-01-01"
  cost_center_id: "CC-123"
```

---

## 🧱 Phase 2: Data Modeling (Basic to Intermediate)

### 1. **Tables & Views**
The building blocks.
```sql
-- definitions/marts/daily_sales.sqlx
config {
  type: "table", -- or "view"
  schema: "sales_mart",
  description: "Aggregated daily sales by region",
  tags: ["daily", "critical"]
}

SELECT
  region,
  DATE(order_date) as sales_date,
  SUM(amount) as total_revenue
FROM ${ref("stg_orders")}
GROUP BY 1, 2
```

### 2. **Declarations (External Sources)**
Tell Dataform about tables it *doesn't* manage (raw data).
```sql
-- definitions/sources/raw_stripe.sqlx
config {
  type: "declaration",
  database: "raw_data_project",
  schema: "stripe_export",
  name: "charges"
}
```

### 3. **Incremental Tables (Cost Optimization)**
Crucial for big data. Only process new rows.
```sql
-- definitions/events/page_views.sqlx
config {
  type: "incremental",
  uniqueKey: ["event_id"], -- Required for MERGE strategy (updates existing rows)
  bigquery: {
    partitionBy: "DATE(timestamp)",
    clusterBy: ["user_id"]
  }
}

SELECT
  event_id,
  user_id,
  timestamp,
  url
FROM ${ref("raw_logs")}

-- Incremental Logic
${when(incremental(), `
  WHERE timestamp > (SELECT MAX(timestamp) FROM ${self()})
`)}
```

---

## 🧪 Phase 3: Data Quality & Testing (Advanced)

### 1. **Inline Assertions**
Built-in checks defined in the config block.
```sql
config {
  type: "table",
  assertions: {
    uniqueKey: ["customer_id"],
    nonNull: ["email", "created_at"],
    rowConditions: [
      "age >= 0",
      "status IN ('active', 'inactive')"
    ]
  }
}
SELECT ...
```

### 2. **Custom Assertion Files**
Complex logic tests (e.g., cross-table validation).
```sql
-- definitions/tests/assert_revenue_match.sqlx
config { type: "assertion" }

WITH stripe_total AS (
  SELECT SUM(amount) as total FROM ${ref("stg_stripe")}
),
db_total AS (
  SELECT SUM(val) as total FROM ${ref("stg_database")}
)
SELECT *
FROM stripe_total s
JOIN db_total d ON 1=1
WHERE ABS(s.total - d.total) > 100 -- Fail if difference > $100
```

### 3. **Unit Testing**
Test logic *without* touching real triggers.
```sql
-- definitions/tests/test_user_logic.sqlx
config { type: "test", dataset: "stg_users" }

input "raw_users" {
  SELECT 1 as id, " JOHN " as name
}

expect {
  SELECT 1 as id, "John" as name
}
```

---

## ⚡ Phase 4: Advanced Architectures & JavaScript

### 1. **JavaScript Includes (DRY Principle)**
Encapsulate repetitive logic in `.js` files.
```javascript
// includes/masking.js
function mask_pii(column) {
  return `REGEXP_REPLACE(${column}, r'\d', 'X')`;
}
module.exports = { mask_pii };
```

Usage:
```sql
SELECT ${masking.mask_pii("phone_number")} as masked_phone ...
```

### 2. **Dynamic Table Generation**
Use JS loops to generate multiple tables programmatically.
```javascript
// definitions/dynamic_tables.js
const countries = ["US", "UK", "CA"];

countries.forEach(country => {
  publish("sales_" + country)
    .type("table")
    .query(ctx => `
      SELECT * FROM ${ctx.ref("all_sales")}
      WHERE country_code = '${country}'
    `);
});
```

### 3. **SCD Type 2 (History Tracking)**
Handling slowly changing dimensions manually (since Dataform doesn't have a native SCD macro like dbt).
```sql
-- 1. Identify new/changed records
WITH source AS (
  SELECT *,
         FARM_FINGERPRINT(TO_JSON_STRING(t)) as hash 
  FROM ${ref("raw_customers")} t
),
target AS (
  SELECT *, hash as current_hash
  FROM ${self()}
  WHERE is_active = true
)

-- 2. Logic to close old records and insert new ones
-- (This typically requires a merge operation or custom SQL operation script)
```

---

## 🚀 Phase 5: Production & Operations (Architect Level)

### 1. **Environments & Variables**
Control execution flow for Dev vs. Prod.
```sql
-- Inside a SQLX file
${when(dataform.projectConfig.vars.env === "production", 
  `SELECT * FROM prod_table`, 
  `SELECT * FROM dev_sample_table`
)}
```

### 2. **Orchestration (Cloud Composer / Airflow)**
Trigger Dataform via Airflow API.
```python
# Airflow DAG snippet
from airflow.providers.google.cloud.operators.dataform import (
    DataformCreateWorkflowInvocationOperator
)

create_workflow = DataformCreateWorkflowInvocationOperator(
    task_id="run_dataform",
    project_id="my-gcp-project",
    region="us-central1",
    repository_id="my-repo",
    compilation_result_id="{{ task_instance.xcom_pull('compile') }}",
)
```

### 3. **CICD with GitHub Actions**
```yaml
name: Dataform CI
on: [push]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install -g @dataform/cli
      - run: dataform install
      - run: dataform compile # Fails if circular dependency or syntax error
      - run: dataform test    # Runs unit tests
```

---

## 🛠️ Phase 6: Optimization & Performance

### 1. **Partitioning & Clustering Strategy**
*   **Partitioning**: Always partition by DATE/TIMESTAMP for tables > 10GB.
*   **Clustering**: Cluster by high-cardinality filter columns (e.g., `user_id`, `customer_id`).

```sql
bigquery: {
  partitionBy: "DATE(event_timestamp)",
  clusterBy: ["user_id", "session_id"],
  requirePartitionFilter: true -- Safety mechanism
}
```

### 2. **Code Optimization**
*   **Avoid SELECT \***: Explicitly select columns to reduce slot usage.
*   **Filter Early**: Apply `WHERE` clauses *before* joins.
*   **Materialized Views**: For real-time dashboards on massive aggregates, use `type: "view"` logic backed by BigQuery Materialized Views (managed via Operations).

---

## 🛡️ Phase 7: Governance & Security

### 1. **Column-Level Security**
Apply policy tags via Dataform config.
```sql
config {
  type: "table",
  columns: {
    email: {
      description: "User Email",
      bigqueryPolicyTags: ["projects/my-proj/locations/us/taxonomies/pii/policyTags/email"]
    }
  }
}
```

### 2. **Documentation & Lineage**
*   **Descriptions**: Mandatory for every table and column.
*   **Lineage**: Dataform auto-generates this. Export metadata to **Dataplex** for enterprise discovery.

---

## 📋 Comprehensive Checklist for Architects

### **Design**
- [ ] Is the layer structure defined? (Bronze -> Silver -> Gold)
- [ ] Are naming conventions enforced? (`stg_`, `dim_`, `fct_`)
- [ ] Are reusable functions extracted to `includes/`?

### **Performance**
- [ ] Are all large tables partitioned & clustered?
- [ ] Is `incremental()` used for immutable event streams?
- [ ] Are partition filters required on huge tables?

### **Reliability**
- [ ] `uniqueKey` assertions on all entities?
- [ ] `nonNull` assertions on PK/FKs?
- [ ] Custom assertions for critical business logic (e.g., revenue !< 0)?

### **Ops**
- [ ] Is CI/CD enforcing `dataform compile`?
- [ ] Are production schedules isolated from dev runs?
- [ ] Is alerting configured for workflow failures?

---

## 📚 Appendix: Key Commands
| Command | Action |
| :--- | :--- |
| `dataform init` | Create new project |
| `dataform compile` | Validate code & build dependency graph |
| `dataform run` | Execute SQL against BigQuery |
| `dataform run --dry-run` | Print SQL execution plan without running |
| `dataform run --tags "daily"` | Run only specific pipeline segment |
| `dataform test` | Execute unit tests defined in `test` type |
| `dataform format` | Auto-format SQLX code |

This guide provides the complete blueprint for mastering Dataform. Start with the basics, but aim for the Phase 6 & 7 practices for a robust, enterprise-grade data platform.
