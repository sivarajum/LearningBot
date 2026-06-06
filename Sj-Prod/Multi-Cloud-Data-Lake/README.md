# POC-04: Multi-Cloud Data Lake Architecture

### Scope & Fidelity → Production path

This is a **concept simulator**, not operational evidence of running a cross-cloud
lake. It runs locally with pandas/pyarrow; no S3/GCS/ADLS, no cross-cloud egress, no
IAM. The production mapping:

| Simulated here | Production technology | Concern it introduces |
|---|---|---|
| `cloud_simulator` synthetic AWS/Azure/GCP data | S3 / ADLS / GCS object stores | Per-cloud IAM, encryption, egress **cost** |
| In-memory zone layout | Bronze/silver/gold prefixes + table format (Iceberg/Delta/Hudi) | ACID on object store, compaction, time-travel |
| pandas transforms | Spark / Trino / DuckDB over the lake | Partition pruning, file sizing, shuffle/skew |
| (none) catalog | Glue / Unity Catalog / BigLake | Cross-engine schema + a single lineage source |
| (none) cross-cloud movement | Egress is the real architecture driver | Data gravity: compute moves to data, not vice-versa |

The honest takeaway this POC supports: *"multi-cloud is usually an egress-cost and
catalog-federation problem, not a code problem."* That framing is the value — not a
claim of having operated three clouds.

## Section 1: What This POC Actually Implements

This POC is a working data lake pipeline that runs entirely locally using Python, pandas, and pyarrow. It simulates the data access and transformation patterns of a multi-cloud lake without connecting to any actual cloud provider.

**What actually runs when you execute `python main.py`:**

1. **Cloud data simulation** (`src/cloud_simulator.py`) — generates synthetic customer and transaction data in memory as if sourced from three cloud providers:
   - AWS: customer IDs prefixed `AW-XXXXX`, regions `us-east-1`, `us-west-2`, `eu-west-1`
   - Azure: customer IDs prefixed `AZ-XXXXX`, regions `eastus`, `westeurope`, `southeastasia`
   - GCP: customer IDs prefixed `GC-XXXXX`, regions `us-central1`, `europe-west1`, `asia-east1`

   Each simulated cloud produces 1,000 customers and 5,000 transactions, persisted as Parquet files in `data/aws/`, `data/azure/`, `data/gcp/`.

2. **Lake builder** (`src/lake_builder.py`) — runs a 5-step pipeline:
   - Ingest: loads all three clouds' Parquet files and unions them into a single DataFrame
   - Transform customers: adds `tenure_days` and `spend_tier` (low/medium/high/premium) columns
   - Transform transactions: adds `month` period and `amount_bucket` (small/medium/large/whale) columns
   - Compute customer metrics: aggregates total transactions, total spent, avg transaction per customer
   - Save: writes `customers.parquet`, `transactions.parquet`, `customer_metrics.parquet` to `data/lake/`

3. **FastAPI REST server** (`src/api.py`) — serves endpoints to query lake tables, get per-cloud stats, and preview data.

4. **Streamlit dashboard** (`src/ui.py`) — visualises cross-cloud customer distribution, spend tier breakdowns, and transaction category analysis.

All data lives on the local filesystem as Parquet files. There is no AWS S3, no Azure ADLS, no GCP Cloud Storage, no Databricks, no Airflow running locally.

---

## Section 2: Architecture This Represents

The code models the ingestion and transformation patterns of a production multi-cloud data lake with these components:

```
Source Layer (one per cloud):
  AWS S3 + Glue         — raw data files in S3, schema catalogued in Glue
  Azure ADLS Gen2 + ADF — raw data in ADLS hierarchical namespace, ADF for orchestrated copy
  GCP Cloud Storage + BQ — raw files in GCS, loaded into BigQuery native tables

Processing Layer:
  Databricks / Spark    — unified processing engine with connectors to all three clouds
                          reads from S3/ADLS/GCS, writes to a unified Delta/Iceberg lake

Orchestration:
  Apache Airflow        — multi-cloud DAGs that coordinate ingestion schedules across clouds
  Cloud-specific:       AWS Glue jobs, Azure Data Factory pipelines, GCP Dataflow

Unified Analytics Layer:
  Google BigQuery       — final destination for cross-cloud aggregated tables
  BI tools (Looker, PowerBI, Tableau) — query unified views

Governance:
  Unity Catalog (Databricks) or Apache Atlas — cross-cloud metadata and lineage
```

The local simulation exercises the schema design, transformation logic, and cross-cloud unification that would run in the processing layer of this stack.

---

## Section 3: Running It Locally

**Prerequisites:**

```bash
pip install -r requirements.txt
```

**Run the full pipeline (generate data + build lake):**

```bash
python main.py
```

This generates ~3,000 customers and ~15,000 transactions across 3 simulated clouds, writes Parquet files, runs transformations, and computes customer metrics. Completes in under 5 seconds.

**Start the REST API:**

```bash
python main.py api
# Server starts on http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

**Start the Streamlit dashboard:**

```bash
python main.py ui
# Opens on http://localhost:8501
```

**Query the lake via API:**

```bash
# Get stats for all clouds
curl http://localhost:8000/stats

# Preview the unified customer metrics table
curl "http://localhost:8000/lake/customer_metrics?limit=5"

# Filter transactions by cloud source
curl "http://localhost:8000/transactions?source_cloud=aws&limit=10"
```

---

## Section 4: Production Path

The delta between local and production is the storage and compute backend. The schema, transformation logic, and aggregation queries in this POC translate directly.

**1. Replace local Parquet reads with cloud object storage:**

```python
# POC (local)
df = pd.read_parquet("data/aws/customers.parquet")

# Production — AWS S3
import boto3
import pandas as pd
df = pd.read_parquet("s3://your-bucket/raw/customers/2026-05-19/customers.parquet")
# Requires: pip install s3fs

# Production — Azure ADLS
df = pd.read_parquet(
    "abfs://your-container@youraccount.dfs.core.windows.net/raw/customers.parquet"
)
# Requires: pip install adlfs

# Production — GCP Cloud Storage
df = pd.read_parquet("gs://your-bucket/raw/customers/customers.parquet")
# Requires: pip install gcsfs
```

**2. Replace local Parquet writes with BigQuery loads:**

```python
# POC (local)
df.to_parquet("data/lake/customer_metrics.parquet", index=False)

# Production — BigQuery
from google.cloud import bigquery
client = bigquery.Client(project="your-project")
job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
client.load_table_from_dataframe(
    df, "your-project.unified_lake.customer_metrics", job_config=job_config
).result()
```

**3. Replace pandas with PySpark for scale (on Databricks or Dataproc):**

```python
# POC (local pandas)
unified = pd.concat([aws_df, azure_df, gcp_df], ignore_index=True)

# Production (PySpark on Databricks)
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("multi-cloud-lake").getOrCreate()

aws_df   = spark.read.parquet("s3://your-bucket/raw/aws/customers/")
azure_df = spark.read.parquet("abfss://container@account.dfs.core.windows.net/raw/azure/customers/")
gcp_df   = spark.read.parquet("gs://your-bucket/raw/gcp/customers/")

unified = aws_df.unionByName(azure_df).unionByName(gcp_df)
```

**4. The transformation logic is portable as-is:**

The derivations in `lake_builder.py` (`tenure_days`, `spend_tier`, `amount_bucket`, customer metrics aggregation) translate to PySpark with near-identical syntax:

```python
# POC (pandas)
df["tenure_days"] = (pd.Timestamp.now(tz="UTC") - df["signup_date"]).dt.days

# PySpark equivalent
from pyspark.sql import functions as F
df = df.withColumn("tenure_days", F.datediff(F.current_date(), F.col("signup_date")))
```

The primary changes needed for production are the I/O adapters (reading from cloud storage, writing to BigQuery). The business logic is unchanged.
