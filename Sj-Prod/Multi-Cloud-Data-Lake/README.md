# Multi-Cloud Data Lake

Unified data lake pipeline from AWS/Azure/GCP sources — synthetic cloud data, Parquet storage, customer metrics aggregation. FastAPI API + Streamlit dashboard.

## What It Does

- **Cloud Simulation**: Generates customer + transaction data for 3 clouds (AWS, Azure, GCP) with cloud-specific ID prefixes and regions
- **Lake Builder**: 5-step pipeline — ingest from 3 clouds, transform customers (tenure/spend tiers), transform transactions (buckets), compute metrics, save as Parquet
- **Unified Analytics**: Cross-cloud customer metrics (total transactions, total spent, avg transaction)
- **REST API**: FastAPI endpoints for lake table queries, per-cloud stats, data preview
- **Dashboard**: Streamlit UI for cross-cloud distribution, spend tiers, transaction analysis

## Architecture

```
src/cloud_simulator.py    # Synthetic data gen for AWS/Azure/GCP (1000 customers + 5000 txns each)
src/lake_builder.py       # 5-step unification pipeline
src/api.py                # FastAPI REST API
src/ui.py                 # Streamlit dashboard
data/aws/                 # Simulated AWS Parquet files
data/azure/               # Simulated Azure Parquet files
data/gcp/                 # Simulated GCP Parquet files
data/lake/                # Unified lake output (customers, transactions, metrics)
```

## Quick Start

```bash
pip install -r requirements.txt
python main.py pipeline    # Generate data + build lake
python main.py api         # API on :8006
python main.py ui          # Dashboard on :8501
python main.py all         # Both API + UI
```

## Testing

```bash
pytest                     # 91 tests
```

## Docker

```bash
docker compose up --build
```

See [RUNNING.md](RUNNING.md) for full build, test, and deployment instructions.
