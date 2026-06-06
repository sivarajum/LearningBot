# Medallion Architecture with dbt

Bronze/Silver/Gold data pipeline using dbt + DuckDB. 9 dbt models, 41 SQL tests, Python data generation, FastAPI API + Streamlit dashboard.

## What It Does

- **Bronze Layer**: Raw data ingestion (customers, orders, products) with ingestion timestamps
- **Silver Layer**: Cleaned, validated, enriched data (deduplication, type casting, derived fields)
- **Gold Layer**: Business aggregates — customer lifetime value, daily revenue, product performance
- **dbt Pipeline**: 9 SQL models with schema tests, custom macros, incremental processing
- **REST API**: FastAPI endpoints for pipeline status, layer stats, data preview
- **Dashboard**: Streamlit UI for exploring bronze/silver/gold layers

## Architecture

```
src/data_generator.py         # Synthetic data generation (CSV)
src/pipeline.py               # Pipeline orchestration (generate + dbt run)
medallion_dbt/
  models/bronze/              # 3 raw ingestion models
  models/silver/              # 3 cleaned/enriched models
  models/gold/                # 3 business aggregate models
  macros/clean_string.sql     # Reusable SQL macros
  tests/                      # Custom SQL tests
src/api.py                    # FastAPI REST API
src/ui.py                     # Streamlit dashboard
```

## Quick Start

```bash
pip install -r requirements.txt
python main.py pipeline    # Generate data + run dbt
python main.py api         # API on :8003
python main.py ui          # Dashboard on :8501
```

## Testing

```bash
pytest                     # 83 Python tests
dbt test --project-dir medallion_dbt --profiles-dir medallion_dbt  # 41 SQL tests
```

## Docker

```bash
docker compose up --build
```

See [RUNNING.md](RUNNING.md) for full build, test, and deployment instructions.
