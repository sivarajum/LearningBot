# Running the Enterprise Data Quality Framework

Complete guide for installing, running, testing, and deploying the Data Quality Framework.

---

## Prerequisites

- **Python 3.11+** (tested on 3.11, 3.12, 3.13)
- **pip** (bundled with Python)
- **Docker** and **Docker Compose** (optional, for containerised deployment)

---

## Installation

```bash
cd Sj-Prod/Data-Quality-Framework

# Install runtime dependencies
pip install -r requirements.txt

# Install test dependencies (adds pytest, pytest-cov, httpx)
pip install -r requirements-test.txt
```

---

## Running the System

The `main.py` entry point supports four modes:

### Validate mode (default)

Runs the full DQ pipeline on all three datasets (customers, transactions, products),
prints scorecards and saves JSON reports to `reports/`.

```bash
python main.py                # default
python main.py validate       # explicit
```

### API mode

Starts a FastAPI REST server on port 8000 with interactive docs.

```bash
python main.py api
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

### UI mode

Starts a Streamlit dashboard on port 8501.

```bash
python main.py ui
```

Open http://localhost:8501 in your browser.

### All mode

Runs validation first, then starts the API server.

```bash
python main.py all
```

### Environment Variables

| Variable         | Default     | Description                    |
|------------------|-------------|--------------------------------|
| `DQ_DATA_DIR`    | `./data`    | Directory for CSV datasets     |
| `DQ_REPORTS_DIR` | `./reports` | Directory for JSON reports     |
| `API_PORT`       | `8000`      | FastAPI server port            |

---

## Running Tests

```bash
# Run all tests
pytest

# Run all tests with verbose output
pytest -v

# Run a specific test file
pytest tests/test_api.py
pytest tests/test_completeness.py

# Run a specific test class or method
pytest tests/test_api.py::TestHealthEndpoint
pytest tests/test_api.py::TestHealthEndpoint::test_health_returns_200

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run with coverage and fail if below threshold
pytest --cov=src --cov-fail-under=80
```

### Test files

| File                    | Coverage                                         |
|-------------------------|--------------------------------------------------|
| `tests/test_api.py`        | All 8 API endpoints, success and error cases |
| `tests/test_completeness.py` | NotNullRule, CompletenessRatioRule          |
| `tests/test_validity.py`   | RegexRule, ValueRangeRule, AllowedValuesRule  |
| `tests/test_uniqueness.py` | UniqueRule, UniquenessRatioRule               |
| `tests/test_scorer.py`     | Grade thresholds, weighted scoring           |
| `tests/test_validator.py`  | Validator orchestration, exception isolation |

---

## Running with Docker

### Build and start both API and UI services

```bash
docker compose up --build
```

This starts two containers:

- **dq-api** on port 8000 (FastAPI)
- **dq-ui** on port 8501 (Streamlit)

### Start only the API

```bash
docker compose up --build dq-api
```

### Run validation inside Docker

```bash
docker compose run --rm dq-api python main.py validate
```

### Stop all services

```bash
docker compose down
```

---

## API Endpoint Reference

All endpoints return JSON.

| Method | Path                          | Description                                      |
|--------|-------------------------------|--------------------------------------------------|
| GET    | `/health`                     | Health check. Returns status, version, loaded datasets. |
| GET    | `/datasets`                   | List all datasets with row/column counts.        |
| GET    | `/datasets/{name}/profile`    | Full statistical profile of a dataset.           |
| POST   | `/datasets/{name}/validate`   | Run all DQ rules and return a full report.       |
| GET    | `/datasets/{name}/score`      | Run validation and return only the DQ scorecard. |
| GET    | `/datasets/{name}/rules`      | List configured rules for a dataset.             |
| GET    | `/summary`                    | Cross-dataset DQ summary with scores and grades. |
| GET    | `/concepts`                   | Educational content about DQ dimensions.         |

### Valid dataset names

`customers`, `transactions`, `products`

### Example requests

```bash
# Health check
curl http://localhost:8000/health

# List datasets
curl http://localhost:8000/datasets

# Profile a dataset
curl http://localhost:8000/datasets/customers/profile

# Validate a dataset (POST)
curl -X POST http://localhost:8000/datasets/customers/validate

# Get DQ scorecard
curl http://localhost:8000/datasets/customers/score

# List rules
curl http://localhost:8000/datasets/customers/rules

# Cross-dataset summary
curl http://localhost:8000/summary

# DQ concepts
curl http://localhost:8000/concepts
```

### Error responses

- **404** -- Dataset not found (invalid name in path)
- **400** -- No rules configured for the requested dataset
- **405** -- Wrong HTTP method (e.g., GET on a POST-only endpoint)

---

## Configuration

### Rule configuration: `config/dq_rules.json`

All DQ rules are defined in `config/dq_rules.json`. Each dataset has an array of rule objects.

Example rule:

```json
{
  "rule": "ValueRangeRule",
  "name": "age_valid_range",
  "column": "age",
  "min_val": 0,
  "max_val": 120,
  "severity": "error"
}
```

### Available rule types

| Rule Type               | Dimension    | Key Parameters                          |
|-------------------------|--------------|-----------------------------------------|
| `NotNullRule`           | completeness | `column`                                |
| `CompletenessRatioRule` | completeness | `column`, `threshold` (0.0-1.0)        |
| `RegexRule`             | validity     | `column`, `pattern`                     |
| `ValueRangeRule`        | validity     | `column`, `min_val`, `max_val`          |
| `AllowedValuesRule`     | validity     | `column`, `allowed_values` (list)       |
| `TypeRule`              | validity     | `column`, `expected_type`               |
| `UniqueRule`            | uniqueness   | `column`                                |
| `UniquenessRatioRule`   | uniqueness   | `column`, `threshold` (0.0-1.0)        |
| `ReferentialIntegrityRule` | consistency | `column`, `reference_dataset`, `reference_column` |
| `CrossColumnRule`       | consistency  | `column`, `column_b`, `operator`        |
| `DataFreshnessRule`     | freshness    | `column`, `max_age_hours`               |

### Severity levels

- **error** -- Critical issue. Fails the overall DQ check.
- **warning** -- Notable issue. Does not fail the overall check.
- **info** -- Informational. Logged but does not affect pass/fail.

---

## Production Deployment Notes

### Scaling

- The API is stateless. Run multiple instances behind a load balancer.
- Each instance loads datasets into memory on startup. For large datasets, consider a shared data layer (database or object storage).

### Monitoring

- Use the `/health` endpoint for load balancer health checks (already configured in `docker-compose.yml`).
- The `/summary` endpoint provides a machine-readable DQ overview suitable for dashboard integration.

### Security

- The default configuration allows all CORS origins (`allow_origins=["*"]`). Restrict this in production.
- Add authentication middleware (e.g., API key, OAuth2) before exposing to external consumers.

### Data persistence

- By default, datasets are CSV files in `data/` and reports are JSON files in `reports/`.
- Both directories are mounted as Docker volumes for persistence across container restarts.
- Override paths via `DQ_DATA_DIR` and `DQ_REPORTS_DIR` environment variables.

### Logging

- The framework prints structured log messages to stdout. Redirect to a log aggregator in production.
- Validation reports are saved as timestamped JSON files in the reports directory.

### Linting

```bash
# From the Sj-Prod root (uses shared ruff.toml)
ruff check Data-Quality-Framework/
ruff format Data-Quality-Framework/
```
