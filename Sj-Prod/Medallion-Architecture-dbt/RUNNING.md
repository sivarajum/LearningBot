# Medallion Architecture dbt + DuckDB -- Running Guide

## Prerequisites

- Python 3.11 or later
- pip (Python package manager)
- dbt-duckdb 1.7+ (installed via requirements.txt)
- Docker and Docker Compose (optional, for containerised runs)

## Installation

### 1. Create and activate a virtual environment

```bash
cd Sj-Prod/Medallion-Architecture-dbt
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

This installs all runtime and test dependencies: FastAPI, Streamlit, dbt-duckdb, DuckDB, Faker, pytest, pytest-cov, and httpx.

### 3. Verify dbt is available

```bash
dbt --version
```

You should see dbt-core and the dbt-duckdb adapter listed.

## Generating Synthetic Data

Generate CSV files (customers, orders, products) into `data/raw/`:

```bash
python main.py generate
```

This creates:
- `data/raw/customers.csv` (500 rows)
- `data/raw/orders.csv` (2000 rows)
- `data/raw/products.csv` (50 rows)

## Running the dbt Pipeline

### Full pipeline (data generation + dbt run + dbt test)

```bash
python main.py pipeline
```

This executes:
1. Synthetic data generation
2. `dbt deps` (install dbt packages if any)
3. `dbt run --select bronze` (raw ingest layer)
4. `dbt run --select silver` (cleansed/validated layer)
5. `dbt run --select gold` (business metrics layer)
6. `dbt test` (41 data quality tests)

The DuckDB warehouse is written to `data/warehouse.duckdb`.

### Running dbt commands directly

```bash
# Ensure environment variables are set
export RAW_DATA_PATH=$(pwd)/data/raw
export DUCKDB_PATH=$(pwd)/data/warehouse.duckdb

# Run all models
dbt run --project-dir medallion_dbt --profiles-dir medallion_dbt

# Run a single layer
dbt run --project-dir medallion_dbt --profiles-dir medallion_dbt --select bronze

# Run dbt tests
dbt test --project-dir medallion_dbt --profiles-dir medallion_dbt
```

### Checking layer statistics

After running the pipeline:

```bash
python main.py stats
```

## Running the API Server

Start the FastAPI server on port 8000:

```bash
python main.py api
```

API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Key endpoints:
- `GET /health` -- liveness check
- `GET /layers` -- stats for all layers
- `GET /layers/{layer}` -- stats for a single layer (bronze, silver, gold)
- `GET /layers/{layer}/{model}` -- row preview for a model
- `POST /pipeline/run` -- trigger a full pipeline run (async)
- `GET /pipeline/status` -- poll pipeline run status
- `GET /lineage` -- data lineage graph
- `GET /concepts` -- architecture concepts glossary

## Running the Streamlit Dashboard

Start the Streamlit UI on port 8501 (requires the API server to be running):

```bash
python main.py ui
```

Open http://localhost:8501 in your browser.

## Running API + UI Together

Run the full pipeline, then start both servers:

```bash
python main.py all
```

This runs the pipeline first, then starts the API (background) and Streamlit (foreground).

## Running Python Tests

### Run all tests

```bash
pytest
```

### Run tests with verbose output

```bash
pytest -v
```

### Run a specific test file

```bash
pytest tests/test_data_generator.py
pytest tests/test_pipeline.py
pytest tests/test_api.py
```

### Run a specific test class or function

```bash
pytest tests/test_data_generator.py::TestGenerateProducts
pytest tests/test_data_generator.py::TestGenerateProducts::test_default_count
```

### Run with coverage report

```bash
pytest --cov=src --cov-report=term-missing
```

Coverage is enabled by default via `pytest.ini`. The report shows line-by-line coverage for all `src/` modules.

### Skip integration tests (tests that need dbt installed)

```bash
pytest -m "not integration"
```

## Running dbt Tests

dbt tests validate data quality in the warehouse (41 tests covering schema constraints, referential integrity, and business rules):

```bash
export RAW_DATA_PATH=$(pwd)/data/raw
export DUCKDB_PATH=$(pwd)/data/warehouse.duckdb
dbt test --project-dir medallion_dbt --profiles-dir medallion_dbt
```

## Running with Docker

### Full stack (pipeline + API + UI)

```bash
docker compose up --build
```

This builds the image, runs the full pipeline, then starts both the API (port 8000) and Streamlit (port 8501).

### Pipeline only (one-shot)

```bash
docker compose run --rm pipeline
```

### API only (requires pipeline to have been run first)

```bash
docker compose up api
```

### Stopping containers

```bash
docker compose down
```

Data persists across container restarts via the `./data` volume mount.

## Linting

Lint with ruff (shared config at `Sj-Prod/ruff.toml`):

```bash
ruff check .
ruff format .
```

## Production Deployment Notes

- **Database**: DuckDB is an embedded OLAP database suitable for local development and testing. For production workloads, replace with Snowflake, BigQuery, or Databricks by changing the dbt profile in `medallion_dbt/profiles.yml` and installing the corresponding dbt adapter.
- **Scheduling**: The pipeline can be triggered via `POST /pipeline/run` or scheduled externally with cron, Airflow, or any orchestrator calling `python main.py pipeline`.
- **Environment variables**:
  - `RAW_DATA_PATH` -- directory containing source CSV files (default: `data/raw`)
  - `DUCKDB_PATH` -- path to the DuckDB warehouse file (default: `data/warehouse.duckdb`)
- **Scaling**: The FastAPI server can be run behind a reverse proxy (nginx, Caddy) with multiple uvicorn workers: `uvicorn src.api:app --workers 4`.
- **Monitoring**: The `/health` endpoint returns dbt and warehouse availability and can be used for health checks in container orchestrators (Kubernetes, ECS).
- **Data persistence**: In Docker deployments, the `./data` directory is mounted as a volume so that generated CSVs and the DuckDB warehouse survive container restarts.
