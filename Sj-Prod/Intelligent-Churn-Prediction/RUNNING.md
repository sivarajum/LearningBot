# Intelligent Churn Prediction -- Running Guide

## Prerequisites

- Python 3.11+
- pip
- Docker and Docker Compose (optional, for containerised deployment)

## Install

```bash
cd Sj-Prod/Intelligent-Churn-Prediction
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run Tests

```bash
# All tests with coverage
pytest

# Specific test file
pytest tests/test_model.py

# Specific test
pytest tests/test_model.py::TestTrainModel::test_trains_successfully

# Skip slow pipeline tests
pytest -m "not slow"

# Without coverage report
pytest --no-cov -v
```

Coverage is configured in `pytest.ini` with `--cov=src --cov-report=term-missing`.

## Train the Model (Pipeline Mode)

```bash
python main.py pipeline
```

This runs the full pipeline:
1. Generates 10,000 synthetic customers to `data/customers.csv`
2. Engineers 11 features (derived + encoded + scaled)
3. Trains an XGBoost classifier with 5-fold cross-validation
4. Saves the model bundle to `data/model_bundle.joblib`

The pipeline prints accuracy, precision, recall, F1, and CV mean upon completion.

## Run the API

```bash
python main.py api
```

Starts a FastAPI server on `http://localhost:8000`. If no trained model exists, the pipeline runs automatically on first startup.

Interactive API docs are available at `http://localhost:8000/docs`.

## Run the Streamlit Dashboard

```bash
python main.py ui
```

Starts the Streamlit dashboard on `http://localhost:8501`. The dashboard connects to the API, so the API must be running first.

## Run Both API and Dashboard

```bash
python main.py all
```

Starts the API server in the background, then launches the Streamlit dashboard. Ctrl+C stops both.

## Run with Docker

```bash
# Build and start both services
docker compose up --build

# Or run individual services
docker compose up api
docker compose up ui
```

The Docker build pre-trains the model during the image build phase so containers start instantly.

- API: `http://localhost:8000`
- Dashboard: `http://localhost:8501`

## API Endpoint Reference

### GET /health

Health check. Returns model load status.

```json
{"status": "healthy", "model_loaded": true}
```

### GET /model-info

Returns training metrics and feature importance.

```json
{
  "training_date": "2026-06-06T...",
  "metrics": {"accuracy": 0.80, "precision": 0.72, "recall": 0.68, "f1": 0.70},
  "feature_importance": {"contract_type": 0.25, "tenure": 0.18, ...}
}
```

### POST /predict

Predict churn for a single customer.

**Request body:**
```json
{
  "tenure": 12,
  "monthly_charges": 65.0,
  "total_charges": 780.0,
  "contract_type": "month-to-month",
  "payment_method": "electronic_check",
  "internet_service": "Fiber",
  "num_support_tickets": 3
}
```

- `total_charges` is optional (auto-calculated from tenure * monthly_charges)
- `contract_type` default: `"month-to-month"`
- `payment_method` default: `"electronic_check"`
- `internet_service` default: `"Fiber"`
- `num_support_tickets` default: `2`

**Response:**
```json
{
  "churn_probability": 0.73,
  "prediction": "churn",
  "top_contributing_features": [
    ["contract_type", 0.25],
    ["tenure", 0.18],
    ["monthly_charges", 0.15]
  ]
}
```

### POST /batch-predict

Upload a CSV file for batch predictions. The CSV should have the same columns as the predict endpoint fields.

```bash
curl -X POST http://localhost:8000/batch-predict \
  -F "file=@data/customers.csv"
```

**Response:**
```json
{
  "predictions": [
    {"churn_probability": 0.73, "prediction": "churn", "customer_id": "CUST-00001", ...},
    ...
  ],
  "total": 10000
}
```

## Production Deployment Notes

- **Model retraining**: Run `python main.py pipeline` periodically to retrain on new data. The model bundle at `data/model_bundle.joblib` is loaded at API startup.
- **Environment variables**: Set `API_URL` for the Streamlit dashboard when the API is on a different host (default: `http://localhost:8000`).
- **Scaling**: The API is a single-process uvicorn server. For production, use `gunicorn` with uvicorn workers: `gunicorn src.api:app -w 4 -k uvicorn.workers.UvicornWorker`.
- **Health checks**: The Docker Compose configuration includes a health check on the `/health` endpoint. The UI service waits for the API to be healthy before starting.
- **Model artifacts**: The `data/` directory contains `customers.csv` and `model_bundle.joblib`. Both are gitignored by the project (`.joblib` and `.csv` patterns). Ensure these are persisted or regenerated in your deployment environment.
