# Multi-Cloud Data Lake -- Comprehensive Guide

A step-by-step walkthrough of the Multi-Cloud Data Lake simulator. This project
generates synthetic data "as if" it lives in three separate cloud providers (AWS,
Azure, GCP), then ingests, transforms, and unifies it into a single data lake
with a REST API and visual dashboard on top.

---

## Table of Contents

1.  [What You Will Learn](#1-what-you-will-learn)
2.  [Prerequisites](#2-prerequisites)
3.  [Project Structure](#3-project-structure)
4.  [Key Concepts](#4-key-concepts)
5.  [Architecture Overview](#5-architecture-overview)
6.  [Step-by-Step Code Walkthrough](#6-step-by-step-code-walkthrough)
7.  [Running the Project](#7-running-the-project)
8.  [Testing the API](#8-testing-the-api)
9.  [Understanding the Data Flow](#9-understanding-the-data-flow)
10. [Exploring the Dashboard](#10-exploring-the-dashboard)
11. [Common Modifications](#11-common-modifications)
12. [Troubleshooting](#12-troubleshooting)
13. [Glossary](#13-glossary)

---

## 1. What You Will Learn

By working through this project you will understand:

- How organizations store data across multiple cloud providers.
- How a data lake unifies disparate data sources into one queryable layer.
- How Parquet files provide efficient columnar storage.
- How an ETL pipeline ingests, transforms, and loads data.
- How a REST API exposes lake data for downstream consumers.
- How a dashboard provides visual cross-cloud analytics.

---

## 2. Prerequisites

**Software you need installed:**

| Tool           | Minimum Version | What It Does                     |
|--------------- |---------------- |--------------------------------- |
| Python         | 3.10+           | Runs all application code        |
| pip            | 22+             | Installs Python packages         |
| Docker         | 20+ (optional)  | Containerized deployment         |
| docker-compose | 2.0+ (optional) | Multi-container orchestration    |
| curl           | any (optional)  | Manual API testing from terminal |

**Python libraries (installed via requirements.txt):**

| Library    | Purpose                                 |
|----------- |---------------------------------------- |
| fastapi    | REST API framework                      |
| uvicorn    | ASGI server for FastAPI                 |
| streamlit  | Interactive dashboard framework         |
| plotly     | Chart rendering (pie, bar, etc.)        |
| pandas     | DataFrame manipulation and analysis     |
| numpy      | Random number generation, numerical ops |
| pyarrow    | Parquet file read/write engine          |
| requests   | HTTP client (UI calls API)              |

**Knowledge assumptions:**

- Basic Python (functions, dictionaries, f-strings).
- Familiarity with DataFrames is helpful but not required -- we explain as we go.
- No cloud accounts are needed. Everything is simulated locally.

---

## 3. Project Structure

```
POC-04-Multi-Cloud-Data-Lake/
|
|-- main.py                  # Entry point: choose pipeline, api, ui, or all
|-- requirements.txt         # Python dependencies
|-- Dockerfile               # Container image definition
|-- docker-compose.yml       # Multi-service orchestration
|
|-- data/                    # ALL data lives here (auto-generated)
|   |-- aws/                 # Simulated AWS S3 bucket
|   |   |-- customers.parquet
|   |   +-- transactions.parquet
|   |-- azure/               # Simulated Azure Data Lake Storage
|   |   |-- customers.parquet
|   |   +-- transactions.parquet
|   |-- gcp/                 # Simulated Google Cloud Storage
|   |   |-- customers.parquet
|   |   +-- transactions.parquet
|   +-- lake/                # Unified data lake (curated zone)
|       |-- customers.parquet
|       |-- transactions.parquet
|       +-- customer_metrics.parquet
|
+-- src/
    |-- __init__.py          # Makes src/ a Python package
    |-- cloud_simulator.py   # Generates per-cloud raw data
    |-- lake_builder.py      # ETL: ingest -> transform -> load
    |-- api.py               # FastAPI endpoints
    +-- ui.py                # Streamlit dashboard
```

**Why this layout matters:**

- `data/aws/`, `data/azure/`, `data/gcp/` represent the "raw zone" -- data
  exactly as each cloud provider stores it.
- `data/lake/` represents the "curated zone" -- cleaned, enriched, and unified.
- `src/` contains all application logic, cleanly separated by concern.

---

## 4. Key Concepts

### 4.1 What Is a Data Lake?

A data lake is a centralized storage system that holds data from many sources
in its raw or processed form. Unlike a traditional database that requires data
to fit a rigid schema before storage, a data lake accepts data first and applies
structure when you read it.

```
Traditional Database (schema-on-write):
  Define columns -> Then insert data -> Rigid, but consistent

Data Lake (schema-on-read):
  Store data as-is -> Apply structure when querying -> Flexible, handles variety
```

In this project, the "lake" is the `data/lake/` directory containing Parquet
files that unify data from three separate cloud providers.

### 4.2 Why Multi-Cloud?

Organizations use multiple cloud providers for several reasons:

1. **Avoid vendor lock-in.** If one provider raises prices or has an outage,
   workloads can shift.
2. **Best-of-breed services.** AWS might offer the best object storage, GCP the
   best ML tools, Azure the best enterprise integration.
3. **Regulatory compliance.** Some data must reside in specific geographic
   regions that only certain providers serve.
4. **Mergers and acquisitions.** Company A uses AWS; Company B uses Azure.
   After merger, both clouds remain.

The challenge: data is now scattered. A data lake solves this by pulling
everything into one unified view.

### 4.3 Parquet -- Columnar Storage

This project stores all data as Apache Parquet files. Parquet is a columnar
format -- data is organized by column rather than by row.

```
ROW-ORIENTED (CSV):                COLUMN-ORIENTED (Parquet):
+------+--------+-------+         Column "name":  [Alice, Bob, Carol]
| name | amount | cloud |         Column "amount": [100, 200, 150]
+------+--------+-------+         Column "cloud":  [aws, gcp, azure]
| Alice|    100 |  aws  |
| Bob  |    200 |  gcp  |
| Carol|    150 | azure |
+------+--------+-------+
```

**Why columnar matters:** Columns of similar types compress much better (10x
smaller than CSV). Queries that need only one column skip the rest entirely.
Type safety is embedded in file metadata. And Spark, Pandas, DuckDB, Athena,
and BigQuery all read Parquet natively.

### 4.4 ETL Pipelines

ETL stands for Extract, Transform, Load:

```
EXTRACT            TRANSFORM                     LOAD
+----------+       +-----------------------+     +-----------+
| Read raw |  -->  | Clean, enrich, join,  | --> | Write to  |
| data     |       | compute metrics       |     | data lake |
+----------+       +-----------------------+     +-----------+
```

| ETL Phase | What Happens                                              | Code Location                                     |
|---------- |---------------------------------------------------------- |-------------------------------------------------- |
| Extract   | Read Parquet files from data/aws/, data/azure/, data/gcp/ | `ingest_all_customers()`, `ingest_all_transactions()` |
| Transform | Add tenure_days, spend_tier, month, amount_bucket; compute metrics | `transform_customers()`, `transform_transactions()`, `compute_customer_metrics()` |
| Load      | Write unified Parquet files to data/lake/                 | `build_lake()` final section                      |

### 4.5 Data Zones: Raw vs Curated

```
+-------------------+     +--------------------+     +-------------------+
|    RAW ZONE       |     |   CURATED ZONE     |     |  SERVING ZONE     |
|                   |     |                    |     |                   |
| data/aws/         | --> | data/lake/         | --> | FastAPI + Streamlit|
| data/azure/       |     |   customers.parquet|     | (analytics,       |
| data/gcp/         |     |   transactions...  |     |  dashboards)      |
|                   |     |   customer_metrics |     |                   |
| Exact copies of   |     | Cleaned, enriched, |     | Queries, charts,  |
| source data.      |     | unified across all |     | filters, summaries|
+-------------------+     +--------------------+     +-------------------+
```

### 4.6 Schema-on-Read vs Schema-on-Write

**Schema-on-write** (traditional databases): Define the table schema before
inserting data. Non-conforming data is rejected.

**Schema-on-read** (data lakes): Store data as files. Structure is interpreted
at query time. This project uses Parquet (which embeds column types) but does
not enforce relational constraints. The meaningful schema is applied when
`lake_builder.py` loads and transforms the data.

### 4.7 Cross-Cloud Analytics

Once data from all three clouds is unified, you can answer questions no single
cloud could answer alone: total revenue across ALL clouds, which cloud's
customers spend the most, how active rates compare between providers, which
product category generates the most revenue globally.

### 4.8 Data Partitioning and Filtering

In this project, filtering happens at the API level:

```
GET /lake/customers?cloud=aws&limit=50
```

This loads the full table, filters where `source_cloud == "aws"`, and returns
50 rows. In production, Parquet files would be physically partitioned (e.g.,
`customers/source_cloud=aws/part-0.parquet`) so filters eliminate files before
reading.

---

## 5. Architecture Overview

```
+------------------------------------------------------------------+
|                        main.py (Entry Point)                     |
|   Modes: pipeline | api | ui | all                               |
+-------+----------------+-----------------+-----------------------+
        |                |                 |
        v                v                 v
 [pipeline mode]   [api mode]        [ui mode]
        |                |                 |
        v                v                 v
+---------------+  +------------+   +--------------+
| cloud_sim.py  |  | api.py     |   | ui.py        |
| Generate raw  |  | FastAPI    |   | Streamlit    |
| data per cloud|  | REST API   |   | Dashboard    |
+-------+-------+  +-----+------+   +------+-------+
        |                |                  |
        v                v                  |
+---------------+  +------------+           |
| lake_builder  |  | /health    |   HTTP    |
| Ingest +      |  | /clouds    |<----------+
| Transform +   |  | /lake/...  |
| Load          |  | /analytics |
+-------+-------+  | /generate  |
        |           +-----+------+
        v                 |
+---------------------------+
|       data/ directory     |
|  aws/  azure/  gcp/  lake/|
|  (Parquet files)          |
+---------------------------+
```

**Data flow in three sentences:**

1. `cloud_simulator.py` generates synthetic customer and transaction data for
   each cloud, saving Parquet files to `data/aws/`, `data/azure/`, `data/gcp/`.
2. `lake_builder.py` reads those raw files, concatenates them, applies
   transformations, and writes the unified result to `data/lake/`.
3. `api.py` serves the lake data over HTTP, and `ui.py` renders interactive
   charts by calling the API.

---

## 6. Step-by-Step Code Walkthrough

### 6.1 cloud_simulator.py -- Generating Raw Data

**File:** `src/cloud_simulator.py`

This module pretends to be three different cloud providers using NumPy random
number generators to produce synthetic DataFrames.

#### Configuration

Each cloud has three regions matching real naming conventions:

```python
REGIONS_BY_CLOUD = {
    "aws":   ["us-east-1", "us-west-2", "eu-west-1"],
    "azure": ["eastus", "westeurope", "southeastasia"],
    "gcp":   ["us-central1", "europe-west1", "asia-east1"],
}
```

#### Generating Customers

`_generate_customers(cloud, n, seed)` creates `n` customer records:

- **customer_id**: Prefixed by cloud (AW-00001, AZ-00001, GC-00001) for
  global uniqueness after merging.
- **region**: Random from the cloud's region list.
- **signup_date**: Random date in 2022-2023 (730-day range).
- **plan**: 40% free, 30% basic, 20% premium, 10% enterprise.
- **monthly_spend**: Uniform $0-$500.
- **is_active**: 75% active, 25% inactive.
- **seed**: Fixed per cloud (aws=42, azure=123, gcp=456) for reproducibility.

#### Generating Transactions

`_generate_transactions(cloud, customers, n, seed)` creates `n` transactions:

- **transaction_id**: Prefixed by cloud (TX-AW-000001, TX-AZ-000001).
- **customer_id**: Random from the cloud's customer list.
- **amount**: Uniform $5-$1,000.
- **category**: Equal chance among electronics, clothing, groceries, books, home.
- **transaction_date**: Random datetime in 2023.
- **payment_method**: credit_card 40%, debit_card 25%, bank_transfer 20%,
  digital_wallet 15%.

#### Volumes

Defaults: 1,000 customers + 5,000 transactions per cloud = 3,000 customers
and 15,000 transactions total across all three providers.

`save_cloud_data()` writes each cloud's DataFrames as Parquet files into
`data/{cloud}/customers.parquet` and `data/{cloud}/transactions.parquet`.

### 6.2 lake_builder.py -- The ETL Pipeline

**File:** `src/lake_builder.py`

This is the heart of the project -- a 5-step ETL pipeline.

#### Step 1 -- Ingest Customers

```python
def ingest_all_customers() -> pd.DataFrame:
    frames = []
    for cloud in ["aws", "azure", "gcp"]:
        df = load_cloud_data(cloud, "customers")
        frames.append(df)
    unified = pd.concat(frames, ignore_index=True)
    return unified
```

Baby-step breakdown: loop over each cloud, load its Parquet file into a
DataFrame, collect all three, concatenate into one 3,000-row DataFrame.
`ignore_index=True` resets the row index to avoid duplicates. If a cloud's
file is missing, it is silently skipped.

#### Step 2 -- Ingest Transactions

Same logic as Step 1, producing a unified 15,000-row DataFrame.

#### Step 3 -- Transform Customers

Two new columns are added:

| New Column  | Computation                                    |
|------------ |----------------------------------------------- |
| tenure_days | Current UTC date minus signup_date, in days    |
| spend_tier  | Bucket monthly_spend into low/medium/high/premium |

Spend tier buckets: $0-50 = low, $50-150 = medium, $150-300 = high, $300+ = premium.

`pd.cut()` bins continuous values into discrete categories. `df.copy()` is
used first to avoid modifying the original DataFrame.

#### Step 4 -- Transform Transactions

Two new columns:

| New Column    | Computation                                      |
|-------------- |------------------------------------------------- |
| month         | Year-month string from transaction_date ("2023-07") |
| amount_bucket | Bucket amount into small/medium/large/whale      |

Amount buckets: $0-25 = small, $25-100 = medium, $100-500 = large, $500+ = whale.

#### Step 5 -- Compute Customer Metrics

```python
tx_agg = transactions.groupby("customer_id").agg(
    total_transactions=("transaction_id", "count"),
    total_spent=("amount", "sum"),
    avg_transaction=("amount", "mean"),
    max_transaction=("amount", "max"),
    unique_categories=("category", "nunique"),
).round(2)

merged = customers.merge(tx_agg, on="customer_id", how="left")
```

This groups all 15,000 transactions by customer_id, computes five aggregates
per customer, then LEFT JOINs them onto the customer table. Customers with
zero transactions get NaN filled with 0.

#### Output

Three Parquet files are written to `data/lake/`:

| File                    | Rows   | Description                               |
|------------------------ |------- |------------------------------------------ |
| customers.parquet       | 3,000  | All customers + tenure_days + spend_tier  |
| transactions.parquet    | 15,000 | All transactions + month + amount_bucket  |
| customer_metrics.parquet| 3,000  | Customers enriched with transaction aggregates |

### 6.3 api.py -- REST API Layer

**File:** `src/api.py`

#### Auto-Initialization

On startup, the lifespan handler checks whether `data/lake/customers.parquet`
exists. If not, it runs the full pipeline automatically. You can start the API
without running the pipeline first.

#### Endpoint Reference

| Method | Path               | Description                                    |
|------- |------------------- |----------------------------------------------- |
| GET    | /health            | Returns `{"status": "healthy"}`                |
| GET    | /clouds            | Lists Parquet files per cloud directory         |
| GET    | /lake/tables       | Lists table names in the lake                  |
| GET    | /lake/{table_name} | Query a table (?limit=100, ?cloud=aws)         |
| GET    | /analytics/summary | Cross-cloud analytics (totals, breakdowns)     |
| POST   | /generate          | Regenerate all data from scratch               |

The `/analytics/summary` endpoint returns customers and transactions by cloud,
revenue by cloud and category, plan distribution, active rates, and average
spend -- powering every chart on the dashboard.

### 6.4 ui.py -- Streamlit Dashboard

**File:** `src/ui.py`

The dashboard communicates entirely through the API -- it never reads Parquet
files directly. This is a clean separation of concerns.

**Sidebar:** Regenerate button, cloud sources list, lake tables list.

**Main area:** Three metric cards (total customers, transactions, revenue),
then five charts: customers by cloud (pie), revenue by cloud (bar), revenue
by category (bar), customer plans (pie), active rate by cloud (bar). Each
cloud gets its brand color (AWS=#FF9900, Azure=#0089D6, GCP=#4285F4).

**Data Explorer:** Select a table, filter by cloud, view 50 rows in an
interactive dataframe.

### 6.5 main.py -- Entry Point

```
python main.py pipeline    # Generate data + build lake, then exit
python main.py api         # Start FastAPI on port 8000 (default)
python main.py ui          # Start Streamlit on port 8501
python main.py all         # Start both API and UI concurrently
```

The `all` mode starts the API as a background subprocess, then Streamlit in
the foreground. Ctrl+C terminates both via a `finally` block.

---

## 7. Running the Project

### 7.1 Local Setup (Python)

```bash
# Step 1: Create virtual environment
cd POC-04-Multi-Cloud-Data-Lake
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Run the data pipeline
python main.py pipeline

# Step 4: Start the API (in one terminal)
python main.py api
# API is now at http://localhost:8000

# Step 5: Start the dashboard (in a second terminal)
source venv/bin/activate
python main.py ui
# Dashboard is now at http://localhost:8501

# Alternative: start both at once
python main.py all
```

If you skip Step 3 and go straight to Step 4, the API auto-generates data
on first startup.

### 7.2 Docker Setup

```bash
# Build and start both services
docker-compose up --build

# Services:
#   api -> http://localhost:8000
#   ui  -> http://localhost:8501

# Stop everything
docker-compose down
```

The Dockerfile runs `python main.py pipeline` during the build, so data is
pre-generated inside the image. The `ui` service waits for the `api` health
check before starting.

---

## 8. Testing the API

### Health Check

```bash
curl http://localhost:8000/health
# {"status":"healthy","service":"data-lake"}
```

### List Cloud Sources

```bash
curl http://localhost:8000/clouds
# {"clouds":{"aws":["customers.parquet","transactions.parquet"],...}}
```

### List Lake Tables

```bash
curl http://localhost:8000/lake/tables
# {"tables":["customers","transactions","customer_metrics"]}
```

### Query a Lake Table

```bash
# First 5 customers
curl "http://localhost:8000/lake/customers?limit=5"

# AWS customers only
curl "http://localhost:8000/lake/customers?cloud=aws&limit=5"

# GCP transactions
curl "http://localhost:8000/lake/transactions?cloud=gcp&limit=10"

# Customer metrics
curl "http://localhost:8000/lake/customer_metrics?limit=3"
```

### Cross-Cloud Analytics

```bash
curl http://localhost:8000/analytics/summary
```

### Regenerate All Data

```bash
curl -X POST http://localhost:8000/generate
```

### Interactive API Docs

FastAPI auto-generates interactive documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 9. Understanding the Data Flow

```
PHASE 1: DATA GENERATION
=========================

  cloud_simulator.py
  |
  +----> AWS (seed=42)
  |      |-> 1000 customers (AW-00000 to AW-00999)
  |      +-> 5000 transactions (TX-AW-000000 to TX-AW-004999)
  |
  +----> Azure (seed=123)
  |      |-> 1000 customers (AZ-00000 to AZ-00999)
  |      +-> 5000 transactions (TX-AZ-000000 to TX-AZ-004999)
  |
  +----> GCP (seed=456)
         |-> 1000 customers (GC-00000 to GC-00999)
         +-> 5000 transactions (TX-GC-000000 to TX-GC-004999)

  Saved to:
  +----> data/aws/customers.parquet      (1000 rows, 8 cols)
  +----> data/aws/transactions.parquet   (5000 rows, 7 cols)
  +----> data/azure/customers.parquet    (1000 rows, 8 cols)
  +----> data/azure/transactions.parquet (5000 rows, 7 cols)
  +----> data/gcp/customers.parquet      (1000 rows, 8 cols)
  +----> data/gcp/transactions.parquet   (5000 rows, 7 cols)


PHASE 2: ETL PIPELINE
======================

  lake_builder.py  build_lake()

  [1/5]  Ingest customers:   3 files -> concat -> 3000 rows
  [2/5]  Ingest transactions: 3 files -> concat -> 15000 rows
  [3/5]  Transform customers: +tenure_days, +spend_tier
  [4/5]  Transform transactions: +month, +amount_bucket
  [5/5]  Compute metrics: group + aggregate + LEFT JOIN

  Saved to:
  +----> data/lake/customers.parquet        (3000 rows, 10 cols)
  +----> data/lake/transactions.parquet     (15000 rows, 9 cols)
  +----> data/lake/customer_metrics.parquet (3000 rows, 15 cols)


PHASE 3: SERVING
=================

  api.py (FastAPI, port 8000)
  |
  |  /health, /clouds, /lake/tables, /lake/{table}, /analytics/summary
  |
  +----> ui.py (Streamlit, port 8501)
         |  Calls API via HTTP
         |  Renders: metrics, 5 charts, data explorer
```

---

## 10. Exploring the Dashboard

Open http://localhost:8501 to see:

**Sidebar (left):** Regenerate button, cloud file listing, lake table listing.

**Top row:** Three metric cards -- Total Customers (3,000), Total Transactions
(15,000), Total Revenue (sum of all transaction amounts).

**Charts (2x2 grid):**

- Top-left: Customers by Cloud (pie) -- roughly equal thirds.
- Top-right: Revenue by Cloud (bar) -- roughly similar per cloud.
- Bottom-left: Revenue by Category (bar) -- roughly equal since categories are
  uniformly distributed.
- Bottom-right: Customer Plans (pie) -- ~40% free, ~30% basic, ~20% premium,
  ~10% enterprise.

**Below the grid:** Active Customer Rate by Cloud (bar) -- ~75% for each cloud.

**Data Explorer (bottom):** Select table, filter by cloud, view 50 rows in a
sortable, scrollable table. Use this to inspect individual records and verify
that transformation columns (tenure_days, spend_tier, month, amount_bucket)
are present.

---

## 11. Common Modifications

### Change Data Volume

Pass different values to `generate_cloud_data()`:

```python
data = generate_cloud_data(customers_per_cloud=5000, transactions_per_cloud=25000)
```

### Add a New Cloud Provider

1. Add regions to `REGIONS_BY_CLOUD` in `cloud_simulator.py`.
2. Add a seed in `generate_cloud_data()`.
3. Add the cloud name to `CLOUDS` in `lake_builder.py`.
4. Update the API `/clouds` loop and the UI color map.

### Add a New Transformation

Add a column in the appropriate transform function in `lake_builder.py`:

```python
def transform_customers(df):
    df = df.copy()
    ...
    df["high_value"] = df["monthly_spend"] > 300
    return df
```

### Add a New API Endpoint

Add a route in `src/api.py`:

```python
@app.get("/analytics/top-customers")
def top_customers(n: int = Query(default=10, le=100)):
    metrics = load_lake_table("customer_metrics")
    top = metrics.nlargest(n, "total_spent")
    for col in top.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        top[col] = top[col].astype(str)
    return {"top_customers": top.to_dict(orient="records")}
```

---

## 12. Troubleshooting

### "No customer data found. Run data generation first."

**Cause:** The `data/` directory is empty.
**Fix:** Run `python main.py pipeline`, or just start the API (it auto-generates).

---

### "Cannot reach the API. Is the server running?"

**Cause:** Streamlit UI cannot connect to FastAPI.
**Fix:** Ensure the API is running (`python main.py api`). Verify with
`curl http://localhost:8000/health`. If using Docker, check `docker-compose ps`.
If the API is on a non-default host, set `export API_URL=http://host:port`.

---

### "ModuleNotFoundError: No module named 'src'"

**Cause:** Running from inside `src/` instead of the project root.
**Fix:** Always run from `POC-04-Multi-Cloud-Data-Lake/`:

```bash
cd POC-04-Multi-Cloud-Data-Lake
python main.py api       # correct
# NOT: cd src && python api.py
```

---

### "ModuleNotFoundError: No module named 'pyarrow'"

**Cause:** Dependencies not installed.
**Fix:** `pip install -r requirements.txt`

---

### Port 8000 or 8501 already in use

**Fix:** Find and kill the process:

```bash
lsof -i :8000
kill <PID>
```

Or change ports in `main.py` (uvicorn port) or the Streamlit `--server.port`.

---

### Data looks identical after regeneration

**Cause:** Seeds are fixed (42, 123, 456) for reproducibility.
**Fix:** Change seeds in `cloud_simulator.py` if you want different data:

```python
seeds = {"aws": 100, "azure": 200, "gcp": 300}
```

---

### Docker build fails

**Fix:** Ensure internet access. Try `docker-compose build --no-cache`. Pin
specific package versions in `requirements.txt` if needed.

---

### Streamlit shows stale data

**Fix:** Click "Regenerate All Data" in the sidebar. It calls `st.rerun()`
after regeneration, forcing a full page refresh.

---

## 13. Glossary

| Term               | Definition                                                     |
|------------------- |--------------------------------------------------------------- |
| ADLS               | Azure Data Lake Storage. Microsoft's cloud analytics storage.  |
| ASGI               | Asynchronous Server Gateway Interface. Protocol for FastAPI.   |
| Columnar storage   | Data stored by column, enabling compression and fast queries.  |
| CORS               | Cross-Origin Resource Sharing. Browser policy for cross-domain requests. |
| Curated zone       | Lake section with cleaned, validated, enriched data.           |
| DataFrame          | Pandas two-dimensional tabular data structure.                 |
| Data lake          | Centralized repository for structured/semi-structured data.    |
| ETL                | Extract, Transform, Load. Pattern for data movement.           |
| FastAPI            | Python web framework for REST APIs with auto-generated docs.   |
| GCS                | Google Cloud Storage. Google's object storage service.         |
| LEFT JOIN          | Merge keeping all left-table rows, filling NaN for no match.   |
| Lifespan           | FastAPI feature for startup/shutdown hooks.                    |
| Parquet            | Open-source columnar storage format for analytics.             |
| Partitioning       | Dividing data into subsets to improve query performance.       |
| PyArrow            | Python library for Apache Arrow; reads/writes Parquet.         |
| Raw zone           | Lake section with unmodified source data copies.               |
| S3                 | Amazon Simple Storage Service. AWS object storage.             |
| Schema-on-read     | Applying structure at query time, not storage time.            |
| Schema-on-write    | Requiring predefined structure before storing data.            |
| Streamlit          | Python framework for interactive data dashboards.              |
| Uvicorn            | Fast ASGI server for running FastAPI applications.             |
| Vendor lock-in     | Dependence on a single provider that makes switching costly.   |

---

*End of guide. For questions, refer to the troubleshooting section above or
inspect the source files directly.*

---

## 14. Interview Questions

*Situation-based and technical questions from Data Architect, Senior Data Engineer, and Cloud Data Engineer interviews. Sourced from LinkedIn posts, Glassdoor reports, and engineering community discussions.*

---

### Situational / Behavioral Questions

**Q: "Your company acquired a competitor that runs on Azure. You're on AWS. The CEO wants a single source of truth within 3 months. How do you approach this?"**

A: Three-phase sprint: Phase 1 (Month 1) — Discovery. Profile both data estates using this POC's approach: catalog every table, run DataProfiler to understand schemas and data quality, and map entity overlap (how do `customer_id` formats differ? Is "ACME Corp" in AWS the same as "Acme Corporation" in Azure?). Identify the authoritative source for each business domain. Phase 2 (Month 2) — Unified ingestion. Stand up Fivetran or Airbyte connectors for both cloud sources, landing raw data into a neutral zone (S3 or GCS, as in this POC's `data/aws/` and `data/azure/` structure). Apply a canonical data model: same column names, same types, same customer ID format. Resolve entity conflicts using fuzzy matching (recordlinkage library) or MDM tooling. Phase 3 (Month 3) — Serve unified Gold. Build the curated/Gold layer with `source_cloud` tags (exactly as this POC does). Governance: analysts read from unified Gold tables only. Key risk: entity resolution is the hardest part — two "ACME Corp" records that are actually different companies will create silent data corruption. Allocate 40% of Phase 2 time to this.

**Q: "A data analyst is building a revenue report from the raw zone instead of the curated zone, and the numbers are wrong. How do you enforce data access governance going forward?"**

A: Immediate fix: work with the analyst to rewrite the query against the Gold `customer_metrics.parquet` table. Verify the result matches expectations. Long-term governance: (1) **Storage-level IAM** — analysts get read access to the Gold/curated prefix only. Raw zone requires a Data Engineering role, enforced via S3 bucket policies or GCS IAM bindings. The raw zone should be literally inaccessible to analyst accounts. (2) **Data catalog tags** — tag every table in the catalog (Alation, DataHub, or AWS Glue Data Catalog) with trust level: `raw: do-not-query-directly`, `curated: approved-for-analytics`. Analysts see these tags in their IDE. (3) **Published data contracts** — the DE team publishes the schema and freshness SLA of Gold tables. Analysts sign up to the contract. If the Gold table doesn't have a column an analyst needs, they file a request rather than querying raw. (4) **Query auditing** — enable CloudTrail (AWS) or Data Access logs (GCP) on all storage. Alert when an analyst account queries a raw-zone path. Two incidents trigger a mandatory access review.

**Q: "Data lake costs doubled last quarter. Your manager asks you to investigate and present a remediation plan."**

A: Root cause breakdown across four cost categories: (1) **Storage growth** — run a lifecycle audit. Are raw-zone files retained forever? Apply automated S3 Lifecycle policies: raw zone moves to Intelligent-Tiering after 30 days, transitions to Glacier after 90 days. Estimated saving: 60–70% on historical raw data storage. (2) **Small file problem** — many small Parquet files (< 128MB each) inflate S3 API request costs and slow down query engines. Compact small files with a weekly Spark `coalesce()` job. (3) **Cross-region data transfer** — if analytics workloads run in us-east-2 but data is stored in eu-west-1, egress fees accumulate. Co-locate compute with data. (4) **Runaway queries** — analysts running full table scans on large tables without partition filters. Enforce partitioning by date and require `WHERE ingestion_date >= CURRENT_DATE - 7` in all queries. Set query cost limits in Athena or BigQuery. Present a 30/60/90 day plan with estimated savings per intervention. The small file fix and lifecycle policies typically recover 50% of excess cost within 30 days.

---

### Technical Deep-Dive Questions

**Q: "Why is Parquet the standard format for data lakes? Give specific technical reasons vs. CSV."**

A: Four concrete advantages: (1) **Columnar storage** — Parquet stores data by column, not row. An analytical query selecting 3 of 50 columns reads ~6% of the data. CSV reads every row entirely regardless of which columns are needed. For a 100GB table with a 3-column query, Parquet reads ~6GB; CSV reads all 100GB. (2) **Compression** — columns have homogeneous values (same type, similar cardinality), enabling efficient encoding: run-length encoding for repeated values, dictionary encoding for low-cardinality strings, delta encoding for timestamps. Typical 5–10x compression vs. raw CSV. (3) **Schema embedded** — Parquet files are self-describing. `pyarrow.read_schema()` returns column names and types directly from the file without a separate schema catalog. CSV has no embedded schema; types must be inferred or externally specified. (4) **Predicate pushdown** — Parquet's row group statistics (min/max value per column per row group) allow query engines to skip entire row groups that cannot satisfy a filter. Reading January data from a year-long Parquet file reads only the January row groups. CSV reads everything and filters after.

**Q: "Explain schema-on-read vs schema-on-write with a real-world example from this POC."**

A: **Schema-on-write** (traditional RDBMS): you define `CREATE TABLE customers (id INT, email VARCHAR(255), plan ENUM('free','basic','premium'))` before any data enters. Non-conforming data is rejected at insert time. Guarantee: every row matches the schema. Cost: schema must be agreed upfront; changes require migrations. **Schema-on-read** (this POC): we store raw Parquet files from AWS, Azure, and GCP with different column names and types. No single schema is enforced at storage time. When `lake_builder.py` reads the files, it applies the schema by selecting, renaming, and casting columns: `df["tenure_days"] = (current_date - df["signup_date"]).dt.days`. The structure is interpreted at query time, not storage time. Benefit: ingest heterogeneous multi-cloud sources without a coordination meeting about column naming. Risk: bad data enters the raw zone silently — null customer IDs, negative monthly_spend. The medallion architecture mitigates this by applying explicit validation in the Silver/curated layer. Bronze is permissive; Silver is strict.

**Q: "This POC uses pandas with 15,000 rows. At what scale does pandas break down, and what replaces it?"**

A: Pandas operates entirely in memory on a single machine. Rule of thumb: pandas becomes impractical when the dataset exceeds 30% of available RAM (intermediate operations during groupby, merge, and sort create copies). At 100M rows of customer data (roughly 10–50 GB), pandas fails. Replacement options by scale: **DuckDB** — handles hundreds of GB via out-of-core processing (spills to disk). SQL interface, zero infra overhead. Reads Parquet natively with full predicate pushdown. Same SQL used in dbt models. Best choice for 1M–1B rows on a single machine. **Spark (EMR/Databricks)** — distributes computation across a cluster. Native Parquet support, partition-aware reads, full pushdown optimization. Required at 1TB+ or when you need streaming alongside batch. **Polars** — pandas-compatible API, written in Rust, processes 5–10x faster than pandas in memory. Good bridge for teams that want pandas syntax but need more performance. At 15K rows (this POC), pandas is correct. At 15M rows, DuckDB. At 150M+ rows with daily batch, use Spark.

---

### System Design Questions

**Q: "Design a real-time multi-cloud data ingestion pipeline with < 5 minute end-to-end latency from source to curated layer."**

A: Replace batch with CDC (Change Data Capture): (1) **Source connectors** — Debezium captures INSERT/UPDATE/DELETE from each cloud's relational databases by tailing the transaction log. Events published to cloud-specific Kafka topics in Confluent Cloud (the neutral event bus — all three clouds publish here). No point-to-point connections between clouds. (2) **Stream normalization** — a Flink job reads from all three Kafka topics, applies the canonical transformation (rename `CustID` → `customer_id`, cast `signup_date` string → DATE, add `source_cloud` tag), and writes to the unified Bronze layer in S3 in real-time. Parquet files are compacted hourly. (3) **Incremental Silver** — a micro-batch job (triggered by new Bronze files or on a 5-minute schedule) runs Silver transformations (deduplication, validation, enrichment) only on new Bronze data. Writes to Silver Parquet partitioned by `ingestion_date`. (4) **Streaming Gold** — for real-time dashboards, write aggregated metrics to a DynamoDB or BigTable for sub-second reads. Batch Gold refreshes hourly for BI tools. Total latency: source change → Confluent (10s) → Flink normalization (30s) → Bronze write (60s) → Silver micro-batch (3min) = 4.5 minutes end-to-end.

**Q: "How would you handle schema evolution — when AWS adds a new column to their customer table — without breaking downstream consumers?"**

A: Three-layer defense in depth: (1) **Bronze tolerates additive changes** — Bronze models use `SELECT *` from source (or Parquet schema inference via PyArrow). When AWS adds `loyalty_tier`, it automatically appears in Bronze with no code change. Parquet handles schema evolution natively: reading old files with a new schema returns NULL for the new column in pre-migration rows. (2) **Silver provides stable contracts** — Silver models use explicit `SELECT column1, column2, ...` — they are stable interfaces. New Bronze columns don't flow to Silver automatically. A data engineer reviews the new column, decides if it's relevant to the business domain, and adds it with a code review. This decouples source volatility from consumer stability. (3) **Breaking change detection in CI/CD** — a GitHub Actions workflow compares the current source schema (fetched from the source API or database) against the last committed schema (stored in `schemas/aws_customers.json`). New columns: notify Silver model owners via Slack. Type changes or dropped columns: block the pipeline and require explicit migration code. Column renames (most dangerous): detected as a drop + add, requiring a migration plan that handles both old and new name during a transition window.
