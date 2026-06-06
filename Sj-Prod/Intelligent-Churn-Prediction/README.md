# POC-01: Intelligent Customer Churn Prediction

## Section 1: What This POC Actually Implements

This POC is a working end-to-end ML pipeline that runs entirely locally using Python, pandas, scikit-learn, and XGBoost.

**What actually runs when you execute `python main.py`:**

1. **Synthetic data generation** (`src/data_generator.py`) — generates ~2,000 customer records in memory using random distributions. No database required.

2. **Feature engineering** (`src/feature_engineering.py`) — derives 11 features from the raw data:
   - `avg_monthly_spend` (total_charges / tenure)
   - `tenure_bucket` (binned: new/mid/loyal/veteran)
   - `support_ticket_rate` (tickets per year of tenure)
   - `charge_tenure_ratio` (spending intensity)
   - Label-encoded categoricals: `contract_type`, `payment_method`, `internet_service`
   - StandardScaler normalization applied to all features

3. **XGBoost classifier** (`src/model.py`) — trains `XGBClassifier(n_estimators=200, max_depth=5, learning_rate=0.1)` with an 80/20 train/test split and 5-fold cross-validation.

4. **Model persistence** — saves a `joblib` bundle (model + scaler + encoders + metrics) to `data/model_bundle.joblib`.

5. **FastAPI REST server** (`src/api.py`) — serves `/predict` and `/model/info` endpoints that load the saved bundle and return churn probability + top contributing features.

6. **Streamlit dashboard** (`src/ui.py`) — interactive UI for entering customer attributes and viewing predictions and feature importance charts.

The pipeline stores all data as in-memory pandas DataFrames. There is no BigQuery, no Vertex AI, no MLflow, no Spark, no Redis, no Airflow running locally.

---

## Section 2: Architecture This Represents

The code in this POC models the core logic of a production ML system that would use these cloud-native components:

```
Data Layer:
  BigQuery            — stores raw customer events and transaction history
  Pub/Sub             — streams real-time events (logins, purchases, cancellations)

Feature Engineering:
  Vertex AI Pipelines — orchestrated, versioned feature computation jobs
  Dataflow / Spark    — distributed feature aggregation at scale

Model Training and Registry:
  Vertex AI Training  — managed training jobs with GPU/TPU support
  MLflow Tracking     — experiment logging (metrics, params, artifacts)
  MLflow Registry     — model versioning and stage promotion (Staging -> Production)

Serving:
  Vertex AI Endpoint  — managed model serving with autoscaling
  FastAPI             — thin API layer forwarding to the endpoint
  Redis               — prediction caching to reduce endpoint latency

Orchestration:
  Airflow             — daily feature refresh, weekly retraining DAGs
  Cloud Monitoring    — drift detection, prediction latency alerts
```

The local implementation exercises every conceptual layer of this stack: data generation, feature engineering, model training, evaluation, persistence, and serving.

---

## Section 3: Running It Locally

**Prerequisites:**

```bash
pip install -r requirements.txt
```

**Run the full pipeline (generate data + train model):**

```bash
python main.py
```

This prints training metrics (accuracy, precision, recall, F1, CV mean) and saves the model bundle to `data/model_bundle.joblib`.

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

**Example API call:**

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "tenure": 12,
    "monthly_charges": 75.5,
    "total_charges": 900.0,
    "contract_type": "Month-to-month",
    "payment_method": "Electronic check",
    "internet_service": "Fiber optic",
    "num_support_tickets": 3
  }'
```

The pipeline completes in under 10 seconds on a laptop.

---

## Section 4: Production Path

The delta between this local POC and a production deployment is primarily in three areas: data access, training infrastructure, and serving infrastructure. The feature engineering and model logic are unchanged.

**1. Replace synthetic data with BigQuery:**

```python
# POC (local)
from src.data_generator import generate_customers
df = generate_customers()

# Production
from google.cloud import bigquery
client = bigquery.Client(project="your-project")
df = client.query("""
    SELECT customer_id, tenure, monthly_charges, total_charges,
           contract_type, payment_method, internet_service,
           num_support_tickets, churn
    FROM `your-project.customers.features`
    WHERE feature_date = CURRENT_DATE()
""").to_dataframe()
```

**2. Replace joblib file save with Vertex AI model registration:**

```python
# POC (local)
from src.model import save_model
save_model(model, artifacts)

# Production
from google.cloud import aiplatform
aiplatform.init(project="your-project", location="us-central1")

model = aiplatform.Model.upload(
    display_name="churn-xgboost-v1",
    artifact_uri="gs://your-bucket/models/churn/v1/",
    serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-3:latest",
)
```

**3. Replace local prediction with Vertex AI Endpoint call:**

```python
# POC (local)
from src.model import load_model, predict_single
bundle = load_model()
result = predict_single(bundle["model"], X, feature_names)

# Production
endpoint = aiplatform.Endpoint("projects/your-project/locations/us-central1/endpoints/YOUR_ENDPOINT_ID")
prediction = endpoint.predict(instances=[X.tolist()])
```

**4. Add MLflow experiment tracking (drop-in addition to training loop):**

```python
import mlflow
mlflow.set_tracking_uri("http://your-mlflow-server:5000")
mlflow.set_experiment("churn-prediction")

with mlflow.start_run():
    mlflow.log_params({"n_estimators": 200, "max_depth": 5})
    # ... train model ...
    mlflow.log_metrics({"accuracy": results["accuracy"], "f1": results["f1"]})
    mlflow.xgboost.log_model(model, "churn_model")
```

The feature engineering code in `src/feature_engineering.py` is production-ready as-is and can be deployed directly to a Dataflow job or Vertex AI Pipeline component with no logic changes.
