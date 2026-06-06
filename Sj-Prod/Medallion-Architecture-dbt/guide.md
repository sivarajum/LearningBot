# POC-08: Medallion Architecture with dbt + DuckDB
## Complete Guide for Data Architect / Principal DE Interviews

**Target audience**: Lead Data Engineers (10+ years) preparing for Data Architect or Principal DE interviews at enterprise companies (MetLife, Goldman Sachs, Databricks, Snowflake, etc.)

**Stack**: dbt-core + dbt-duckdb + DuckDB + FastAPI + Streamlit + Python 3.11

---

## Table of Contents

1. What is Medallion Architecture and Why It Matters
2. Bronze / Silver / Gold Layers Explained
3. What is dbt and Why Every Data Team Uses It
4. dbt Models: Table vs View vs Incremental
5. dbt Tests: Generic + Singular
6. dbt Macros
7. DuckDB as a Local Warehouse
8. Step-by-Step Code Walkthrough Per Layer
9. Data Lineage and How to Trace Data
10. Running Locally (Step by Step)
11. Docker Deployment
12. API Endpoints with curl Examples
13. How to Extend: Snowflake, More Sources, Incremental Models
14. How This Maps to Real Enterprise Work
15. Troubleshooting
16. Glossary
17. Interview Questions and Model Answers

---

## 1. What is Medallion Architecture and Why It Matters

### The Problem It Solves

Before medallion architecture, data lakes were often "data swamps": raw files dumped without structure, impossible to trust, and requiring full re-reads every time a consumer needed data. Teams would create ad-hoc ETL scripts that:
- Mixed business logic with ingestion logic
- Had no concept of data quality gates
- Were impossible to audit or trace
- Required full refreshes to fix errors

Medallion architecture — popularised by Databricks — solves this with a **tiered, progressive refinement model**.

### The Core Idea

Data flows through three named zones:

```
SOURCE FILES
    |
    v
[BRONZE]  - "What did we receive?" (raw, immutable)
    |
    v
[SILVER]  - "What is clean and valid?" (filtered, validated)
    |
    v
[GOLD]    - "What does the business need?" (aggregated, curated)
```

Each layer has a specific contract:
- **Bronze**: Preserve everything. Never mutate. Add metadata only.
- **Silver**: Apply business rules. Clean data. Validate contracts.
- **Gold**: Aggregate for consumers. One answer per business question.

### Why Architects Care About This

At the Data Architect level, you are responsible for:

1. **Data trust** — downstream consumers (BI tools, ML models, finance reports) need to know where data came from and whether it was validated.
2. **Blast radius reduction** — when a source sends bad data, only Bronze is contaminated. Silver remains clean because it rejects bad records.
3. **Incremental improvement** — you can rebuild Gold without touching Bronze. You can fix Silver logic without re-ingesting Bronze.
4. **Auditability** — every row in Gold can be traced back to the exact source row in Bronze via `_ingested_at` and `_source_file` metadata.
5. **Team contracts** — data engineers own Bronze→Silver. Analytics engineers own Silver→Gold. Clear ownership boundaries.

### Industry Adoption

| Company | Their Name for It |
|---------|------------------|
| Databricks | Medallion (coined the term) |
| Airbnb | Bronze/Silver/Gold |
| Netflix | Stream Processing Layers |
| Uber | Hudi Bronze/Silver |
| MetLife | Raw/Conformed/Curated/Consumption (4-layer variant) |

---

## 2. Bronze / Silver / Gold Layers Explained

### Bronze: The System of Record

Bronze is your **immutable audit log**. It answers the question: "What exactly did we receive from the source?"

**Rules for Bronze:**
- Load all rows, including bad ones
- Cast types (VARCHAR, DATE, DOUBLE) but apply no filters
- Add `_ingested_at TIMESTAMP` and `_source_file VARCHAR` metadata columns
- Never delete rows (append-only in incremental scenarios)

**Bronze example — bronze_customers.sql:**
```sql
SELECT
    customer_id::VARCHAR    AS customer_id,
    email::VARCHAR          AS email,
    signup_date::DATE       AS signup_date,
    CURRENT_TIMESTAMP       AS _ingested_at,
    'customers.csv'         AS _source_file
FROM read_csv_auto('/data/raw/customers.csv')
```

**Key insight for interviews**: If a consumer asks "why did this bad record appear in production?", Bronze is where you start the investigation. It's the crime scene, not processed evidence.

### Silver: The Conformed Layer

Silver answers: "What data can we trust?"

**Rules for Silver:**
- Apply all validation rules (email must contain '@', amounts must be positive)
- Deduplicate by business key using QUALIFY / ROW_NUMBER()
- Normalise values (lowercase emails, uppercase status codes)
- Add derived columns that are universally useful (customer_age_days, order_quarter)
- Never add aggregations — that's Gold's job

**Silver example — silver_orders.sql:**
```sql
SELECT
    order_id,
    UPPER(status) AS status,
    order_date,
    EXTRACT('year' FROM order_date) AS order_year
FROM bronze_orders
WHERE UPPER(status) IN ('PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED')
  AND amount > 0
QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY _ingested_at DESC) = 1
```

**Key insight for interviews**: The QUALIFY + ROW_NUMBER() deduplication pattern is industry standard. It handles late-arriving data, reprocessing, and CDC events. Know this cold.

### Gold: Business-Ready Metrics

Gold answers: "What does the business need to make decisions?"

**Rules for Gold:**
- One model per business question or report
- Aggregations (SUM, COUNT, AVG) live here
- Use COALESCE to handle customers with no orders (LEFT JOIN pattern)
- Derived business segments (CLV tier: high/mid/low value)
- Named for the consumer, not the data (gold_customer_lifetime_value, not gold_order_agg)

**Gold example — gold_customer_lifetime_value.sql:**
```sql
SELECT
    c.customer_id,
    c.tier,
    COUNT(o.order_id)   AS total_orders,
    SUM(o.amount)       AS lifetime_value
FROM silver_customers c
LEFT JOIN silver_orders o
    ON c.customer_id = o.customer_id
    AND o.status = 'DELIVERED'
GROUP BY 1, 2
```

**Key insight for interviews**: Gold models should be named from the business perspective, not the technical one. `gold_customer_lifetime_value` communicates business intent. `gold_cust_ord_agg` does not.

---

## 3. What is dbt and Why Every Data Team Uses It

### The Problem Before dbt

In 2015-era data engineering:
- Transformations were Python scripts or stored procedures
- No dependency management — scripts ran in arbitrary order
- No testing — bad data silently propagated
- No documentation — only the author knew what a table meant
- Deployments required DBAs and JIRA tickets

### What dbt Changes

dbt (data build tool) is a **SQL-first transformation framework** that brings software engineering practices to analytics:

| Software Engineering | dbt Equivalent |
|---------------------|----------------|
| Git version control | dbt project in Git |
| Unit tests | dbt tests (not_null, unique, etc.) |
| Dependency management | dbt DAG (ref() function) |
| Documentation | dbt docs |
| CI/CD | dbt in GitHub Actions |
| Linting | dbt's schema.yml validation |

### How dbt Works

You write SELECT statements. dbt wraps them in CREATE TABLE AS or CREATE VIEW AS — you never write DDL:

```sql
-- You write:
SELECT customer_id, name FROM {{ ref('bronze_customers') }}

-- dbt generates:
CREATE TABLE silver.silver_customers AS
SELECT customer_id, name FROM bronze.bronze_customers
```

The `ref()` function is critical: it:
1. Tells dbt to run the referenced model first (dependency resolution)
2. Builds the full DAG (Directed Acyclic Graph)
3. Enables column-level lineage in dbt docs

### dbt in the Modern Data Stack

```
Ingestion      Storage       Transform     Serving
(Fivetran)  →  (Snowflake) → (dbt)      → (Looker/Tableau)
(Airbyte)      (BigQuery)    (dbt)         (Metabase)
(Kafka)        (DuckDB)      (dbt)         (FastAPI)
```

dbt is **warehouse-agnostic** via adapters:
- dbt-snowflake, dbt-bigquery, dbt-databricks, dbt-redshift, dbt-duckdb

---

## 4. dbt Models: Table vs View vs Incremental

### Materialisation Types

| Type | What dbt Creates | When to Use |
|------|-----------------|-------------|
| `view` | A SQL view | Small models, frequently changing logic, upstream of tables |
| `table` | A full table (truncate + reload) | Medium models, used by many consumers |
| `incremental` | Append/upsert new rows only | Large models, time-series, partitioned data |
| `ephemeral` | CTE (never stored) | Intermediate logic only |

### Table Materialisation (Used in This POC)

```yaml
# dbt_project.yml
models:
  medallion_dbt:
    bronze:
      +materialized: table
```

On every `dbt run`:
1. DROP TABLE IF EXISTS bronze.bronze_customers
2. CREATE TABLE bronze.bronze_customers AS (SELECT ...)

**When to use table**: Bronze and Silver layers where you want physical storage for query performance and downstream independence.

### Incremental Materialisation

Incremental models are the most important concept for a Principal DE interview. They process only new/changed rows:

```sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge'
) }}

SELECT order_id, customer_id, status, _ingested_at
FROM bronze_orders
{% if is_incremental() %}
  WHERE _ingested_at > (SELECT MAX(_ingested_at) FROM {{ this }})
{% endif %}
```

On first run: full table load.
On subsequent runs: only rows where `_ingested_at > last run timestamp`.

**The `{{ this }}` variable** refers to the existing table — dbt uses it to find the high-water mark.

**Incremental strategies**:
- `append`: Add new rows only (time-series, immutable events)
- `merge` (UPSERT): Match on unique_key, update changed rows
- `delete+insert`: Delete matching rows, re-insert (clean but expensive)

**Interview question**: "When would you NOT use incremental?"
Answer: When source data can be late-arriving or backdated (e.g., corrections to historical orders). Incremental misses these unless you use a lookback window.

---

## 5. dbt Tests: Generic + Singular

### Tests as Data Contracts

dbt tests are automated assertions that must pass before data is considered production-ready. They implement **data contracts**:

> "I, as a data producer, guarantee that customer_id is never null and is always unique in this model."

### Generic Tests (schema.yml)

Declared in schema.yml, no SQL required:

```yaml
models:
  - name: silver_customers
    columns:
      - name: customer_id
        tests:
          - not_null
          - unique
      - name: tier
        tests:
          - accepted_values:
              values: ['BRONZE', 'SILVER', 'GOLD']
```

Built-in generic tests:
- `not_null` — no nulls in this column
- `unique` — all values are distinct
- `accepted_values` — only these values allowed
- `relationships` — foreign key integrity

### Singular Tests (tests/ directory)

Custom SQL files that return failing rows:

```sql
-- tests/silver_orders_valid_status.sql
-- Returns rows where status is NOT in the accepted set
SELECT order_id, status
FROM {{ ref('silver_orders') }}
WHERE status NOT IN ('PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED')
```

**Test convention**: The test PASSES if the query returns 0 rows. Any returned rows indicate a failure.

### Running Tests

```bash
dbt test                           # all tests
dbt test --select silver_orders    # tests for one model
dbt test --select tag:silver       # tests for all silver models
```

### Test Severity Levels

```yaml
columns:
  - name: amount
    tests:
      - not_null:
          severity: error    # fails the pipeline
      - dbt_utils.expression_is_true:
          expression: ">= 0"
          severity: warn     # logs warning, continues
```

---

## 6. dbt Macros

### What Are Macros

Macros are reusable Jinja2 functions that generate SQL. They prevent code duplication across models.

### This POC's clean_string Macro

```sql
-- macros/clean_string.sql
{% macro clean_string(column_name) %}
    TRIM(
        REGEXP_REPLACE(
            LOWER(TRIM({{ column_name }})),
            '\\s+',
            ' '
        )
    )
{% endmacro %}
```

Used in silver models:
```sql
{{ clean_string('name') }} AS name  -- applies TRIM + LOWER + collapse spaces
```

### Advanced Macro Patterns

**Audit macro** — used in Gold models to add standard audit columns:
```sql
{% macro add_audit_columns() %}
    CURRENT_TIMESTAMP AS _created_at,
    '{{ run_started_at }}' AS _dbt_run_started_at,
    '{{ invocation_id }}' AS _dbt_invocation_id
{% endmacro %}
```

**Dynamic incremental filter** — parameterise the lookback window:
```sql
{% macro incremental_filter(column, days_back=3) %}
    {% if is_incremental() %}
    WHERE {{ column }} >= CURRENT_DATE - INTERVAL '{{ days_back }} days'
    {% endif %}
{% endmacro %}
```

---

## 7. DuckDB as a Local Warehouse

### Why DuckDB for This POC

DuckDB is an **in-process OLAP database** — it runs inside your Python process, writes to a single file, and requires zero infrastructure:

```python
import duckdb
conn = duckdb.connect("warehouse.duckdb")
result = conn.execute("SELECT COUNT(*) FROM bronze.bronze_customers").fetchone()
```

### DuckDB vs Traditional Warehouses

| Feature | DuckDB | Snowflake | BigQuery |
|---------|--------|-----------|---------|
| Setup time | 0 minutes | 15+ minutes | 10+ minutes |
| Cost | Free | $2-4/TB scanned | $5/TB |
| Max data | ~100GB practical | Unlimited | Unlimited |
| Columnar storage | Yes | Yes | Yes |
| SQL dialect | PostgreSQL-compatible | Snowflake SQL | GoogleSQL |
| dbt adapter | dbt-duckdb | dbt-snowflake | dbt-bigquery |

### DuckDB Features Used in This POC

**read_csv_auto**: Read CSVs directly in SQL without loading:
```sql
SELECT * FROM read_csv_auto('/data/raw/customers.csv')
```

**QUALIFY clause**: Window function filtering (Silver deduplication):
```sql
SELECT * FROM bronze_orders
QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY _ingested_at DESC) = 1
```

**Window functions**: Revenue rolling averages in Gold:
```sql
AVG(daily_revenue) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
```

**EXTRACT**: Date parts for time-series analysis:
```sql
EXTRACT('year' FROM order_date)::INTEGER AS order_year
```

### DuckDB for Prototyping → Production Pattern

```
Local Dev:   DuckDB (file-based, instant)
    |
    v
CI Tests:    DuckDB (same models, no change needed)
    |
    v
Production:  Swap profiles.yml to Snowflake adapter
             All SQL continues to work (standard SQL)
```

This is why DuckDB is invaluable: you can develop, test, and validate the full dbt model suite locally, then deploy to Snowflake/BigQuery with only a `profiles.yml` change.

---

## 8. Step-by-Step Code Walkthrough Per Layer

### Bronze Layer Walkthrough

**bronze_customers.sql** — The simplest, most important model:

```sql
{{ config(materialized='table') }}

SELECT
    customer_id::VARCHAR    AS customer_id,    -- explicit cast
    email::VARCHAR          AS email,
    signup_date::DATE       AS signup_date,    -- string → date
    CURRENT_TIMESTAMP       AS _ingested_at,   -- lineage metadata
    'customers.csv'         AS _source_file    -- source tracing
FROM read_csv_auto('{{ env_var("RAW_DATA_PATH") }}/customers.csv')
```

Notice:
- `env_var("RAW_DATA_PATH")` — path comes from environment, works in any environment (local/Docker/CI)
- No WHERE clause — Bronze preserves all rows including bad ones
- Explicit casts document the expected types

### Silver Layer Walkthrough

**silver_customers.sql** — Demonstrates all Silver patterns:

```sql
{{ config(materialized='table') }}

SELECT
    customer_id,
    {{ clean_string('name') }}      AS name,         -- macro for DRY code
    TRIM(LOWER(email))              AS email,         -- normalisation
    UPPER(tier)                     AS tier,          -- normalisation
    DATEDIFF('day', signup_date, CURRENT_DATE) AS customer_age_days,  -- enrichment
    CASE WHEN UPPER(tier) = 'GOLD' THEN 3 ... END AS tier_rank        -- derived metric
FROM {{ ref('bronze_customers') }}    -- dbt dependency via ref()
WHERE email LIKE '%@%'                -- validation gate
  AND customer_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (           -- deduplication
    PARTITION BY customer_id
    ORDER BY _ingested_at DESC
) = 1                                  -- keep most recent ingestion
```

The `QUALIFY` pattern deserves emphasis: it's DuckDB/Snowflake syntax that allows window function filtering in a single pass. The equivalent in older SQL would require a subquery or CTE.

### Gold Layer Walkthrough

**gold_customer_lifetime_value.sql** — Demonstrates Gold aggregation patterns:

```sql
{{ config(materialized='table') }}

SELECT
    c.customer_id,
    c.tier,
    -- COALESCE handles customers with zero delivered orders
    COALESCE(COUNT(o.order_id), 0)      AS total_orders,
    COALESCE(SUM(o.amount), 0)          AS lifetime_value,
    -- Business segmentation
    CASE
        WHEN COALESCE(SUM(o.amount), 0) >= 1000 THEN 'high_value'
        WHEN COALESCE(SUM(o.amount), 0) >= 300  THEN 'mid_value'
        ELSE 'low_value'
    END                                  AS clv_segment
FROM {{ ref('silver_customers') }} c
LEFT JOIN {{ ref('silver_orders') }} o   -- LEFT JOIN preserves all customers
    ON c.customer_id = o.customer_id
    AND o.status = 'DELIVERED'           -- filter on JOIN condition, not WHERE
GROUP BY 1, 2, 3, 4
```

Critical design note: The status filter `o.status = 'DELIVERED'` is on the JOIN condition, not in a WHERE clause. If it were in a WHERE clause, it would silently drop customers with no delivered orders (because NULL != 'DELIVERED'). On the JOIN condition, it correctly returns NULL amounts for unmatched customers, which COALESCE then converts to 0.

**gold_daily_revenue.sql** — Demonstrates advanced window functions:

```sql
-- 7-day rolling average
AVG(daily_revenue) OVER (
    ORDER BY order_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
) AS revenue_7d_avg,

-- Month-to-date revenue
SUM(daily_revenue) OVER (
    PARTITION BY order_year, order_month
    ORDER BY order_date
    ROWS UNBOUNDED PRECEDING
) AS mtd_revenue,

-- Day-over-day change
daily_revenue - LAG(daily_revenue) OVER (ORDER BY order_date) AS revenue_vs_prev_day
```

These three patterns together answer virtually every time-series business question.

---

## 9. Data Lineage and How to Trace Data

### The Problem

A BI analyst asks: "This customer's lifetime value changed overnight. What happened?"

Without lineage: you manually search through pipelines, Slack history, Git commits.

With lineage: you follow the directed acyclic graph backward.

### DAG in This POC

```
customers.csv ──> bronze_customers ──> silver_customers ──┐
                                                           ├──> gold_customer_lifetime_value
orders.csv ────> bronze_orders ────> silver_orders ────────┤
                                                           ├──> gold_daily_revenue
                                                 ──────────┤
products.csv ──> bronze_products ──> silver_products ──────┴──> gold_product_performance
```

### dbt Lineage Commands

```bash
# View the DAG in terminal
dbt ls --select gold_customer_lifetime_value+   # upstream (+) models

# Generate HTML lineage docs
dbt docs generate
dbt docs serve   # opens browser at localhost:8080
```

### Column-Level Lineage

dbt 1.6+ supports column-level lineage via `--emit-facts`. This tells you not just "which model", but "which column in which model" contributed to a downstream value.

### API Lineage Endpoint

This POC exposes `/lineage` via the FastAPI:
```json
{
  "nodes": [{"id": "customers.csv", "layer": "source"}, ...],
  "edges": [{"from": "customers.csv", "to": "bronze_customers"}, ...]
}
```

The Streamlit UI renders this as an interactive Plotly graph.

---

## 10. Running Locally (Step by Step)

### Prerequisites

- Python 3.10+ (`python --version`)
- pip
- ~500MB disk space

### Step 1: Clone and Navigate

```bash
git clone <your-repo>
cd POC-08-Medallion-Architecture-dbt
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\activate       # Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs dbt-duckdb (which includes dbt-core + DuckDB adapter), FastAPI, Streamlit, Plotly, and Faker. Approximately 400MB total.

### Step 4: Verify dbt Installation

```bash
dbt --version
# Should print: Core: 1.7.x, Plugins: duckdb: 1.7.x
```

### Step 5: Run the Full Pipeline

```bash
python main.py pipeline
```

This will:
1. Generate 500 customers, 2000 orders, 50 products → `data/raw/`
2. Run `dbt run --select bronze` → creates `bronze.*` tables in DuckDB
3. Run `dbt run --select silver` → creates `silver.*` tables
4. Run `dbt run --select gold` → creates `gold.*` tables
5. Run `dbt test` → validates all data contracts

Expected output:
```
Pipeline SUCCEEDED
  Duration : 12.3s

  BRONZE layer:
    bronze_customers                              500 rows
    bronze_orders                               2,000 rows
    bronze_products                                50 rows

  SILVER layer:
    silver_customers                              490 rows  (10 bad emails filtered)
    silver_orders                               1,950 rows  (50 bad records filtered)
    silver_products                                50 rows

  GOLD layer:
    gold_customer_lifetime_value                  490 rows
    gold_product_performance                       50 rows
    gold_daily_revenue                          2,200 rows  (daily buckets ~6yr range)
```

### Step 6: Start the API

In a new terminal:
```bash
source .venv/bin/activate
python main.py api
# API docs: http://localhost:8000/docs
```

### Step 7: Start the Streamlit UI

In another terminal:
```bash
source .venv/bin/activate
python main.py ui
# Dashboard: http://localhost:8501
```

### Step 8: Run Everything at Once

```bash
python main.py all
```

This runs the pipeline, then starts the API (background thread), then launches Streamlit (foreground).

### Step 9: Verify Stats

```bash
python main.py stats
```

---

## 11. Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t medallion-poc08 .

# Run all services
docker-compose up medallion

# Access:
#   API:       http://localhost:8000/docs
#   Streamlit: http://localhost:8501
```

### Run Only the Pipeline

```bash
docker-compose run --rm pipeline
```

### Persist Data Between Runs

The `docker-compose.yml` mounts `./data:/app/data`, so DuckDB warehouse and CSV files persist on your host machine even after the container restarts.

### Environment Variable Override

```bash
# Run with custom DuckDB path
docker run \
  -e DUCKDB_PATH=/app/data/custom.duckdb \
  -e RAW_DATA_PATH=/app/data/raw \
  -p 8000:8000 -p 8501:8501 \
  medallion-poc08 python main.py all
```

---

## 12. API Endpoints with curl Examples

### Health Check

```bash
curl http://localhost:8000/health

# Response:
{
  "status": "ok",
  "dbt_installed": true,
  "warehouse_exists": true,
  "version": "1.0.0"
}
```

### List All Layers

```bash
curl http://localhost:8000/layers | python -m json.tool

# Response:
{
  "bronze": {"total_rows": 2550, "models": ["bronze_customers", ...]},
  "silver": {"total_rows": 2490, "models": [...]},
  "gold":   {"total_rows": 2740, "models": [...]}
}
```

### Single Layer Stats

```bash
curl http://localhost:8000/layers/gold
```

### Preview a Model (first 20 rows)

```bash
curl "http://localhost:8000/layers/gold/gold_customer_lifetime_value?limit=5" | python -m json.tool
```

### Trigger Pipeline

```bash
curl -X POST http://localhost:8000/pipeline/run

# Response:
{"status": "started", "message": "Pipeline started in background. Poll GET /pipeline/status."}
```

### Check Pipeline Status

```bash
# Poll until running: false
curl http://localhost:8000/pipeline/status | python -m json.tool
```

### Fetch Lineage Graph

```bash
curl http://localhost:8000/lineage | python -m json.tool
```

### Get Concepts Glossary

```bash
curl http://localhost:8000/concepts | python -m json.tool
```

---

## 13. How to Extend

### Add Snowflake as Production Target

1. Install the Snowflake adapter:
```bash
pip install dbt-snowflake
```

2. Add a Snowflake output to `profiles.yml`:
```yaml
medallion_dbt:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: "{{ env_var('DUCKDB_PATH', '../data/warehouse.duckdb') }}"
      threads: 4
    prod:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
      role: TRANSFORMER
      warehouse: COMPUTE_WH
      database: MEDALLION
      schema: PUBLIC
      threads: 16
```

3. Run against production:
```bash
dbt run --target prod
```

No SQL changes needed. dbt handles the adapter translation.

### Add a New Source (e.g., Returns Data)

1. Add `data/raw/returns.csv` (or Fivetran/Airbyte connector)
2. Create `models/bronze/bronze_returns.sql` (read_csv_auto or source())
3. Create `models/silver/silver_returns.sql` (validate, deduplicate)
4. Update `gold_customer_lifetime_value.sql` to join silver_returns and subtract refunds

```sql
-- Update Gold CLV to subtract returns
SELECT
    c.customer_id,
    SUM(o.amount) - COALESCE(SUM(r.refund_amount), 0) AS net_lifetime_value
FROM silver_customers c
LEFT JOIN silver_orders o ON c.customer_id = o.customer_id AND o.status = 'DELIVERED'
LEFT JOIN silver_returns r ON o.order_id = r.order_id
GROUP BY 1
```

### Convert Bronze → Silver to Incremental

```sql
-- silver_orders.sql (incremental version)
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge'
) }}

SELECT
    order_id,
    customer_id,
    UPPER(status) AS status,
    amount,
    _ingested_at
FROM {{ ref('bronze_orders') }}
WHERE UPPER(status) IN ('PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED')
  AND amount > 0
{% if is_incremental() %}
  AND _ingested_at > (SELECT MAX(_ingested_at) FROM {{ this }})
{% endif %}
```

### Add dbt Packages

Add `packages.yml` to the project:
```yaml
# medallion_dbt/packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.1.0"]
  - package: calogica/dbt_expectations
    version: [">=0.10.0"]
```

Install:
```bash
dbt deps
```

Then use in schema.yml:
```yaml
tests:
  - dbt_utils.expression_is_true:
      expression: "amount >= 0"
  - dbt_expectations.expect_column_to_exist
```

### Add Great Expectations for Data Quality

For enterprise-grade data quality beyond dbt tests:
```python
import great_expectations as ge

context = ge.get_context()
batch = context.get_batch(silver_orders_df)
result = batch.expect_column_values_to_be_in_set(
    "status", ["PENDING", "SHIPPED", "DELIVERED", "CANCELLED"]
)
```

---

## 14. How This Maps to Real Enterprise Work

### MetLife 4-Layer Model

MetLife uses a variant with four layers instead of three:

| MetLife Layer | Medallion Equivalent | Purpose |
|--------------|---------------------|---------|
| RAW | Bronze | Exact copy of source |
| CONFORMED | Silver | Standard types, deduplication |
| CURATED | Silver+ / pre-Gold | Business-domain validated |
| CONSUMPTION | Gold | BI-ready, aggregated |

The extra CURATED layer separates:
- Generic cleansing (CONFORMED) — email validation, deduplication
- Domain logic (CURATED) — business rules like "a customer is churned if no order in 90 days"

### Goldman Sachs / JPMorgan Pattern

Financial firms typically add:
1. **Data lineage certification** — every model must have a certified lineage path from raw to consumption
2. **PII layer** — a separate schema with masked/tokenized columns for analysts without PII access
3. **Regulatory snapshots** — daily snapshots of Silver layer for regulatory auditing (Basel III, GDPR article 20)

### Databricks Lakehouse Pattern

On Databricks:
- Bronze uses Delta Lake tables (`USING DELTA`) with auto-compaction
- Silver uses Delta Lake MERGE for CDC (Change Data Capture)
- Gold is typically a Databricks SQL Warehouse or Unity Catalog table share

The SQL in dbt models is identical — only the `profiles.yml` and `dbt_project.yml` materialisation strategies change.

### Team Ownership Model

```
Data Engineering Team:
  - Owns Bronze layer (ingestion reliability)
  - Owns Bronze → Silver transformations (data quality)

Analytics Engineering Team:
  - Owns Silver → Gold transformations (business logic)
  - Writes and maintains schema.yml tests

Data Consumers:
  - Reads only from Gold layer (never raw tables)
  - Raises data quality issues as dbt test failures, not Slack messages
```

This separation of concerns is what allows data teams to scale from 5 to 50 people without becoming a bottleneck for each other.

---

## 15. Troubleshooting

### dbt not found after pip install

```bash
# Check which Python dbt was installed into
which dbt
pip show dbt-duckdb

# If using venv, ensure it's activated:
source .venv/bin/activate
which dbt   # should point to .venv/bin/dbt
```

### "Database 'bronze' not found"

DuckDB schemas are created automatically by dbt-duckdb when models run. This error usually means the model failed before creating the schema. Run:
```bash
dbt run --select bronze --full-refresh
```

### "Cannot read CSV: file not found"

Ensure the env var is set:
```bash
export RAW_DATA_PATH=/absolute/path/to/data/raw
python main.py pipeline
```

Or run data generation first:
```bash
python main.py generate
```

### QUALIFY not supported

Older DuckDB versions (pre-0.8) do not support QUALIFY. Ensure:
```bash
python -c "import duckdb; print(duckdb.__version__)"
# Should be 0.10+
pip install 'duckdb>=0.10.0'
```

### Streamlit shows "API offline"

Start the API server first in a separate terminal:
```bash
python main.py api
# Then in another terminal:
python main.py ui
```

Or use `python main.py all` which handles the sequencing automatically.

### dbt test failures

Run tests with debug output:
```bash
dbt test --store-failures
# Failed test data stored in: target/compiled/medallion_dbt/tests/
```

### DuckDB file locked

DuckDB does not support multiple writers. If the pipeline is running, the API cannot write simultaneously. The pipeline should complete (< 30s) before the API starts modifying data. Reads can happen concurrently without issues.

---

## 16. Glossary

**Bronze Layer**: The raw ingestion zone. Stores data exactly as received from source systems. Acts as the immutable system of record.

**Silver Layer**: The cleansed and validated layer. Applies business rules, deduplication, and enrichment. Provides a trusted, conformed view of data.

**Gold Layer**: The business-ready layer. Contains aggregated metrics, KPIs, and wide tables optimised for BI tools and analytical queries.

**dbt (data build tool)**: A SQL-based transformation framework that manages model dependencies, testing, documentation, and deployment to analytics warehouses.

**dbt Model**: A SQL SELECT statement in a .sql file that dbt compiles and executes against the warehouse.

**dbt ref()**: A Jinja function `{{ ref('model_name') }}` that creates a dependency between models and resolves the correct schema/table name at runtime.

**dbt Test**: An assertion about model data. Generic tests (not_null, unique) are declared in schema.yml. Singular tests are custom SQL files that return failing rows.

**dbt Macro**: A Jinja2 function in the macros/ directory that generates reusable SQL fragments.

**Incremental Model**: A dbt materialisation that processes only new/changed rows on runs after the initial full load.

**QUALIFY clause**: A DuckDB/Snowflake SQL extension that filters rows based on window function results in a single pass, avoiding subqueries.

**Data Contract**: A formal agreement between data producers and consumers specifying schema, quality SLAs, and semantics. Implemented as dbt tests in this POC.

**DuckDB**: An in-process analytical database that runs inside a Python process, stores data in a single file, and supports full SQL analytics without a server.

**CLV (Customer Lifetime Value)**: Total net revenue attributed to a single customer across all their historical transactions. A key Gold-layer business metric.

**DAG (Directed Acyclic Graph)**: A graph where nodes are dbt models and edges are ref() dependencies. dbt uses the DAG to determine execution order and parallelism.

**Medallion Architecture**: A data design pattern using Bronze/Silver/Gold layers to progressively refine raw data into trusted, business-ready assets.

**Data Lineage**: The provenance trail showing where data came from and what transformations were applied. Enables root-cause analysis and impact assessment.

**Materialisation**: How dbt persists a model's results — as a table (full refresh), view (query at read time), incremental table (append/upsert), or ephemeral CTE.

**schema.yml**: A dbt configuration file declaring model descriptions, column documentation, and generic tests.

**profiles.yml**: A dbt configuration file specifying warehouse connection details. Kept outside version control or parameterised with env_vars.

---

## 17. Interview Questions and Model Answers

### "Walk me through the medallion architecture layers."

"Medallion has three layers: Bronze is the raw ingest layer — we preserve every source row with only type casts and metadata added. Silver is the cleansed layer where we apply business rules: email validation, deduplication via QUALIFY + ROW_NUMBER(), normalisation. Gold is business-ready metrics: aggregations, KPIs, one model per business question. The key benefit is blast-radius isolation — bad source data contaminates only Bronze. Silver and Gold remain clean."

### "How does dbt handle dependencies between models?"

"dbt's ref() function. When I write `{{ ref('silver_customers') }}` in a Gold model, dbt resolves it to the actual schema.table name and adds an edge in the DAG. Before running any model, dbt topologically sorts the DAG to ensure upstream models run first. No manual orchestration needed."

### "What's the difference between a generic test and a singular test?"

"Generic tests are reusable assertions declared in schema.yml — not_null, unique, accepted_values, relationships. They're quick to add and require no SQL. Singular tests are custom SQL files in the tests/ directory that return failing rows. You write them when you need domain-specific logic that can't be expressed as a generic test — for example, 'no order should have an amount greater than the customer's credit limit'."

### "When would you use incremental models?"

"For large append-only tables like event streams, order histories, or audit logs where full refresh is prohibitively expensive. The key pattern is: if is_incremental(), filter WHERE _ingested_at > max(_ingested_at) from the existing table. The risk is late-arriving data — corrections or backdated records get missed. In that case, I'd use a rolling window: filter WHERE event_date >= CURRENT_DATE - 3 instead of using the max timestamp."

### "How would you add a new source to this architecture?"

"Three steps: First, add a Bronze model that reads the new source — read_csv_auto or a source() function pointing to a raw table. Second, add a Silver model that inherits the cleansing patterns — ref() the Bronze model, apply dedup, validate. Third, either create a new Gold model if it's a standalone business question, or update an existing Gold model with a LEFT JOIN to incorporate the new data. The whole pipeline stays intact; you just extend the DAG."

### "What's your strategy for handling schema changes from upstream sources?"

"At Bronze, we're resilient to additive changes — new columns appear automatically with read_csv_auto. For breaking changes (renamed columns, type changes), Bronze is the firewall: Silver and Gold are insulated. I'd add a test in Bronze that alerts when an expected column is missing. For truly breaking upstream changes, I'd version the Bronze table (bronze_customers_v2) and transition Silver gradually."

### "How does this translate to production at scale (e.g., Snowflake with 100M rows)?"

"The SQL is warehouse-agnostic — switching from DuckDB to Snowflake is a profiles.yml change. For scale: Bronze becomes an incremental table with COPY INTO from S3/Azure Blob. Silver uses MERGE with a 3-day lookback window to handle late-arriving data. Gold becomes clustered tables (CLUSTER BY date columns) for partition pruning. dbt models stay identical — only materialisation config changes."

### Situation: Your nightly dbt run takes 4 hours and blocks the morning BI refresh. How do you fix it?

"My first step is profiling with `dbt run --profiles-dir . 2>&1 | grep 'Completed in'` to identify the slowest models. Common causes and fixes: (1) **Full-refresh on large tables** — convert the worst offenders to incremental models with `unique_key` + `merge` strategy. A Silver orders table processing 100M rows as a full refresh could become a 5-minute incremental run processing only yesterday's data. (2) **Sequential models that could be parallel** — dbt parallelises automatically via the DAG, but a long chain of single-dependency models forces sequential execution. Restructure so intermediate transforms don't chain unnecessarily. (3) **Warehouse size** — scale up the Snowflake warehouse for the run window, then scale down. Use `dbt run --threads 16` to maximise parallelism within the session. (4) **Missing clustering keys** — Gold aggregation models scanning 100M-row Silver tables without partition pruning. Add `CLUSTER BY (date_key, region_id)` on the Silver tables. In this POC with DuckDB the same principle applies: add appropriate indexes or pre-filter in upstream Silver models. Target: break the 4-hour run into a Bronze stage (30 min), Silver stage (60 min), and Gold stage (30 min) with Airflow orchestrating the stages so BI can read from Gold while Silver is still processing."

### Situation: Two teams report different customer counts from two different Gold models. How do you investigate?

"This is a data lineage investigation. My process: (1) Run `dbt docs generate && dbt docs serve` to open the lineage graph — identify which Bronze and Silver models feed each Gold model. (2) Check if they're reading from the same Silver table or diverged at different points. (3) Check deduplication logic — `gold_customer_lifetime_value` might join on `customer_id` while `gold_churn_risk` joins on `email`, producing different counts if customers have multiple emails. (4) Check filter conditions — one model might filter `status = 'ACTIVE'` while the other counts all customers. (5) Check `is_incremental()` windows — if one model uses a 7-day lookback and the other uses 30 days, they'll diverge when customers stop ordering. The fix: define a single `dim_customers` Silver model that is the authoritative source for customer counts, and have all Gold models `ref()` it. Add a singular dbt test that cross-checks: `SELECT COUNT(*) FROM gold_customer_lifetime_value clv FULL OUTER JOIN gold_churn_risk cr ON clv.customer_id = cr.customer_id WHERE clv.customer_id IS NULL OR cr.customer_id IS NULL` — any rows here indicate a discrepancy."

### Situation: You're leading a team of 15 engineers across 5 squads. Each squad owns their dbt models but there's no consistency in naming, testing, or documentation. How do you establish governance?

"At scale, governance must be structural not cultural — you can't rely on people remembering conventions. My approach: (1) **dbt project structure by squad**: each squad gets their own subdirectory in `models/` (e.g., `models/payments/`, `models/risk/`), which makes ownership explicit and allows squad-specific materialisation configs. (2) **Required tests via dbt meta-testing**: add a custom macro `check_required_tests` that runs as part of CI and fails the build if any model in Silver or Gold is missing `not_null` + `unique` tests on its primary key. (3) **Naming conventions enforced in CI**: write a Python script that validates all model names match the pattern `bronze_*`, `silver_*`, `gold_*` — run it as a pre-commit hook and in CI. (4) **Schema.yml coverage gates**: add a CI step that checks schema.yml coverage using `dbt ls --select state:modified+` — any modified model must have a corresponding schema.yml update or the PR is rejected. (5) **Data contracts as the interface**: when Squad A's Gold model is consumed by Squad B's downstream system, that interface is formalised as a dbt source with specific tests. Changing it requires a PR that Squad B reviews. This prevents silent breakage. Roll this out in phases: start with the Bronze/Silver boundary (highest value, lowest political resistance), then extend to Silver/Gold, then inter-squad interfaces."

---

*This guide is part of the Lead DE → Data Architect interview preparation series.*
*POC-08: Medallion Architecture with dbt + DuckDB | 2025*
