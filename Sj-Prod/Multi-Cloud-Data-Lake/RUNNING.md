# Multi-Cloud Data Lake -- Running Guide

## Prerequisites

- Python 3.11+
- pip
- Docker and Docker Compose (optional, for containerized deployment)

## Installation

```bash
cd Sj-Prod/Multi-Cloud-Data-Lake
pip install -r requirements.txt
```

## Running Tests

```bash
# Run all tests with coverage
pytest

# Run a specific test file
pytest tests/test_cloud_simulator.py
pytest tests/test_lake_builder.py
pytest tests/test_api.py

# Run a specific test class or method
pytest tests/test_cloud_simulator.py::TestGenerateCustomers
pytest tests/test_api.py::TestHealth::test_health_returns_200

# Run without coverage report
pytest --no-cov

# Run with verbose output
pytest -v
```

## Running the System

The system has four modes, all launched via `main.py`:

### Pipeline Mode -- Generate Data and Build Lake

Generates simulated cloud data (AWS, Azure, GCP) and builds the unified data lake.

```bash
python main.py pipeline
```

This creates Parquet files under `data/aws/`, `data/azure/`, `data/gcp/`, and `data/lake/`.

### API Mode (default) -- FastAPI Server

Starts the REST API on port 8000. If no lake data exists, it auto-generates on startup.

```bash
python main.py api
```

The server runs at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### UI Mode -- Streamlit Dashboard

Starts the Streamlit dashboard on port 8501. Requires the API to be running separately.

```bash
python main.py ui
```

Dashboard runs at `http://localhost:8501`.

### All Mode -- API + UI Together

Starts both the API server and the Streamlit dashboard.

```bash
python main.py all
```

## Running with Docker

Build and run both services (API + UI):

```bash
docker compose up --build
```

- API: `http://localhost:8000`
- UI: `http://localhost:8501`

To run only the API:

```bash
docker compose up --build api
```

## API Endpoint Reference

| Method | Path                 | Description                                      |
|--------|----------------------|--------------------------------------------------|
| GET    | `/health`            | Health check. Returns `{"status": "healthy"}`    |
| POST   | `/generate`          | Regenerate all cloud data and rebuild the lake   |
| GET    | `/clouds`            | List data files available per cloud provider     |
| GET    | `/lake/tables`       | List all tables in the data lake                 |
| GET    | `/lake/{table_name}` | Query a lake table. Params: `limit`, `cloud`     |
| GET    | `/analytics/summary` | Cross-cloud analytics summary (counts, revenue)  |

### Query Parameters for `/lake/{table_name}`

- `limit` (int, default 100, max 10000) -- Number of rows to return
- `cloud` (string, optional) -- Filter by source cloud (`aws`, `azure`, `gcp`)

### Example Requests

```bash
# Health check
curl http://localhost:8000/health

# Regenerate data
curl -X POST http://localhost:8000/generate

# List cloud sources
curl http://localhost:8000/clouds

# List lake tables
curl http://localhost:8000/lake/tables

# Query customers (first 10, AWS only)
curl "http://localhost:8000/lake/customers?limit=10&cloud=aws"

# Analytics summary
curl http://localhost:8000/analytics/summary
```

## Architecture Overview

```
Multi-Cloud-Data-Lake/
|-- main.py                  # CLI entry point (pipeline|api|ui|all)
|-- src/
|   |-- cloud_simulator.py   # Generates simulated data for AWS, Azure, GCP
|   |-- lake_builder.py      # Ingests cloud data, transforms, builds unified lake
|   |-- api.py               # FastAPI REST endpoints
|   |-- ui.py                # Streamlit dashboard
|-- tests/
|   |-- conftest.py          # Shared pytest fixtures (temp dirs, test data)
|   |-- test_cloud_simulator.py
|   |-- test_lake_builder.py
|   |-- test_api.py
|-- data/                    # Generated data (gitignored)
|   |-- aws/                 # Simulated AWS S3 data
|   |-- azure/               # Simulated Azure ADLS data
|   |-- gcp/                 # Simulated GCP GCS data
|   |-- lake/                # Unified data lake tables
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
|-- pytest.ini
```

### Data Flow

1. **cloud_simulator.py** generates customer and transaction data for each cloud provider, saved as Parquet files in `data/{cloud}/`.
2. **lake_builder.py** ingests all cloud data, merges into unified tables, applies feature engineering (tenure_days, spend_tier, amount_bucket), computes per-customer metrics, and saves to `data/lake/`.
3. **api.py** exposes the lake via REST endpoints with filtering and analytics.
4. **ui.py** presents a Streamlit dashboard consuming the API.

## Production Deployment Notes

- **Environment variables**: Set `API_URL` for the UI container to point to the API (default: `http://localhost:8000`).
- **Data persistence**: Mount a volume to `/app/data` in Docker to persist generated data across container restarts.
- **Scaling**: The API is stateless once the lake is built. Multiple API replicas can serve the same data directory.
- **Regeneration**: Use `POST /generate` to refresh all data. This is a blocking operation; for production, consider running the pipeline as a scheduled job.
- **Security**: The default CORS policy allows all origins. Restrict `allow_origins` in `src/api.py` for production.
- **Health checks**: Docker Compose includes a health check on the API. Use `/health` for load balancer probes.
