# MLOps: Machine Learning Operations

## Overview

MLOps (Machine Learning Operations) is the practice of operationalizing machine learning models, bringing DevOps principles to ML workflows. It encompasses the entire ML lifecycle from development through deployment, monitoring, and maintenance, ensuring reliable, scalable, and maintainable ML systems in production.

## Core Principles

### ML Lifecycle Management
- **Experimentation**: Rapid prototyping and testing
- **Reproducibility**: Consistent results across environments
- **Automation**: CI/CD pipelines for ML workflows
- **Monitoring**: Performance tracking and drift detection
- **Governance**: Compliance, security, and auditability

### Key Challenges Addressed
- Model deployment complexity
- Data drift and concept drift
- Model performance degradation
- Scalability and resource management
- Compliance and regulatory requirements

## Experimentation and Development

### Experiment Tracking

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Start MLflow experiment
mlflow.set_experiment("customer_churn_prediction")

def train_model(n_estimators, max_depth, random_state=42):
    with mlflow.start_run():
        # Log parameters
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("random_state", random_state)

        # Train model
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state
        )

        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)

        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)

        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)

        # Log model
        mlflow.sklearn.log_model(model, "model")

        # Log artifacts
        mlflow.log_artifact("feature_importance.png")
        mlflow.log_artifact("confusion_matrix.png")

        return model, accuracy

# Hyperparameter tuning with tracking
for n_est in [50, 100, 200]:
    for max_d in [5, 10, None]:
        train_model(n_est, max_d)
```

### Data Versioning

```python
import dvc
from dvc.repo import Repo
from dvc.main import main

# Initialize DVC in project
def setup_dvc():
    # Initialize DVC repository
    main(["init"])

    # Add data files to DVC tracking
    main(["add", "data/raw/train.csv"])
    main(["add", "data/raw/test.csv"])
    main(["add", "data/processed/features.pkl"])

    # Create data pipeline
    main(["run", "-n", "preprocess",
          "-d", "data/raw/train.csv",
          "-d", "src/preprocess.py",
          "-o", "data/processed/train_features.pkl",
          "python", "src/preprocess.py", "train"])

    main(["run", "-n", "train",
          "-d", "data/processed/train_features.pkl",
          "-d", "src/train.py",
          "-o", "models/model.pkl",
          "-M", "metrics.json",
          "python", "src/train.py"])

# Version control for data
def version_data():
    repo = Repo()

    # Create new branch for experiment
    main(["checkout", "-b", "experiment/churn-prediction-v2"])

    # Update data
    main(["add", "data/raw/new_train.csv"])
    main(["commit", "-m", "Add new training data"])

    # Push to remote storage
    main(["push"])

# Reproduce experiments
def reproduce_experiment():
    # Checkout specific version
    main(["checkout", "v1.0.0"])

    # Reproduce pipeline
    main(["repro"])
```

### Model Registry

```python
import mlflow
from mlflow.tracking import MlflowClient

def register_model():
    client = MlflowClient()

    # Register model in Model Registry
    model_version = mlflow.register_model(
        model_uri="runs:/123456789/model",
        name="customer_churn_model"
    )

    print(f"Model registered: {model_version.name} v{model_version.version}")

    return model_version

def promote_model(model_name, version, stage):
    client = MlflowClient()

    # Transition model to production
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage=stage  # "Staging", "Production", "Archived"
    )

    print(f"Model {model_name} v{version} promoted to {stage}")

def compare_model_versions():
    client = MlflowClient()

    # Get all versions of a model
    versions = client.get_latest_versions(model_name, stages=["Production", "Staging"])

    for version in versions:
        run = client.get_run(version.run_id)

        print(f"Version {version.version} ({version.current_stage}):")
        print(f"  Accuracy: {run.data.metrics.get('accuracy', 'N/A')}")
        print(f"  Precision: {run.data.metrics.get('precision', 'N/A')}")
        print(f"  Created: {version.creation_timestamp}")
```

## CI/CD for ML

### ML Pipeline Automation

```python
from kfp import dsl
from kfp import compiler
from kfp.client import Client

@dsl.pipeline(
    name="Customer Churn ML Pipeline",
    description="End-to-end ML pipeline for customer churn prediction"
)
def ml_pipeline(
    project_id: str,
    region: str,
    input_data: str,
    output_model: str
):

    # Data ingestion
    @dsl.component
    def ingest_data(input_path: str, output_path: str):
        import pandas as pd
        from google.cloud import storage

        # Download data from GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(input_path.split('/')[2])
        blob = bucket.blob('/'.join(input_path.split('/')[3:]))
        blob.download_to_filename('/tmp/data.csv')

        # Basic preprocessing
        df = pd.read_csv('/tmp/data.csv')
        df.to_parquet(output_path)

    # Data validation
    @dsl.component
    def validate_data(input_path: str, schema_path: str):
        import pandas as pd
        import great_expectations as ge

        df = pd.read_parquet(input_path)
        context = ge.get_context()

        # Validate data quality
        validator = context.get_validator(
            datasource_name="pandas",
            data_connector_name="runtime",
            data_asset_name="data",
            runtime_parameters={"batch_data": df},
            expectation_suite_name="churn_suite"
        )

        # Add expectations
        validator.expect_column_to_exist("customer_id")
        validator.expect_column_values_to_be_between("tenure", 0, 100)

        results = validator.validate()
        assert results.success, "Data validation failed"

    # Feature engineering
    @dsl.component
    def feature_engineering(input_path: str, output_path: str):
        import pandas as pd
        from sklearn.preprocessing import StandardScaler, OneHotEncoder

        df = pd.read_parquet(input_path)

        # Feature engineering logic
        numerical_features = ['tenure', 'monthly_charges', 'total_charges']
        categorical_features = ['contract_type', 'payment_method']

        scaler = StandardScaler()
        encoder = OneHotEncoder(sparse=False)

        # Scale numerical features
        df[numerical_features] = scaler.fit_transform(df[numerical_features])

        # Encode categorical features
        encoded_features = encoder.fit_transform(df[categorical_features])
        encoded_df = pd.DataFrame(
            encoded_features,
            columns=encoder.get_feature_names_out(categorical_features)
        )

        # Combine features
        final_df = pd.concat([df[numerical_features], encoded_df], axis=1)
        final_df.to_parquet(output_path)

    # Model training
    @dsl.component
    def train_model(input_path: str, model_output: str, metrics_output: str):
        import pandas as pd
        import pickle
        import json
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, precision_score, recall_score
        from sklearn.model_selection import train_test_split

        df = pd.read_parquet(input_path)

        # Split features and target
        X = df.drop('churn', axis=1)
        y = df['churn']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Evaluate model
        y_pred = model.predict(X_test)
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred)
        }

        # Save model and metrics
        with open(model_output, 'wb') as f:
            pickle.dump(model, f)

        with open(metrics_output, 'w') as f:
            json.dump(metrics, f)

    # Model validation
    @dsl.component
    def validate_model(metrics_path: str, threshold: float):
        import json

        with open(metrics_path, 'r') as f:
            metrics = json.load(f)

        accuracy = metrics['accuracy']

        if accuracy < threshold:
            raise ValueError(f"Model accuracy {accuracy} below threshold {threshold}")

        print(f"Model validation passed: accuracy = {accuracy}")

    # Pipeline orchestration
    ingest_task = ingest_data(input_data, "gs://bucket/processed/data.parquet")
    validate_task = validate_data(ingest_task.output, "gs://bucket/schemas/churn_schema.json")
    features_task = feature_engineering(validate_task.output, "gs://bucket/features/features.parquet")
    train_task = train_model(features_task.output, "gs://bucket/models/model.pkl", "gs://bucket/metrics/metrics.json")
    validate_task_final = validate_model(train_task.outputs["metrics_output"], 0.8)

# Compile and run pipeline
def run_pipeline():
    compiler.Compiler().compile(ml_pipeline, 'pipeline.yaml')

    client = Client()
    run = client.create_run_from_pipeline_func(
        ml_pipeline,
        arguments={
            'project_id': 'your-project',
            'region': 'us-central1',
            'input_data': 'gs://bucket/raw/data.csv',
            'output_model': 'gs://bucket/models/'
        }
    )

    print(f"Pipeline run created: {run.run_id}")
```

### Automated Testing

```python
import pytest
import pandas as pd
from sklearn.metrics import classification_report
import pickle

class TestMLPipeline:

    @pytest.fixture
    def sample_data(self):
        # Create sample data for testing
        data = {
            'customer_id': range(100),
            'tenure': [12, 24, 6, 48, 3] * 20,
            'monthly_charges': [50.0, 75.0, 25.0, 100.0, 30.0] * 20,
            'contract_type': ['Month-to-month', 'One year', 'Two year'] * 33 + ['Month-to-month'],
            'churn': [0, 1, 0, 0, 1] * 20
        }
        return pd.DataFrame(data)

    def test_data_ingestion(self, sample_data):
        """Test data ingestion functionality"""
        assert len(sample_data) == 100
        assert 'customer_id' in sample_data.columns
        assert 'churn' in sample_data.columns

    def test_feature_engineering(self, sample_data):
        """Test feature engineering pipeline"""
        from sklearn.preprocessing import StandardScaler, OneHotEncoder

        # Test numerical scaling
        numerical_features = ['tenure', 'monthly_charges']
        scaler = StandardScaler()
        scaled = scaler.fit_transform(sample_data[numerical_features])

        assert scaled.shape == (100, 2)
        assert abs(scaled.mean()) < 0.1  # Approximately zero mean

        # Test categorical encoding
        categorical_features = ['contract_type']
        encoder = OneHotEncoder(sparse=False)
        encoded = encoder.fit_transform(sample_data[categorical_features])

        assert encoded.shape[1] == len(sample_data['contract_type'].unique())

    def test_model_training(self, sample_data):
        """Test model training and evaluation"""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split

        # Prepare data
        X = sample_data[['tenure', 'monthly_charges']]
        y = sample_data['churn']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train model
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)

        # Test predictions
        y_pred = model.predict(X_test)
        assert len(y_pred) == len(y_test)

        # Test prediction probabilities
        y_proba = model.predict_proba(X_test)
        assert y_proba.shape == (len(y_test), 2)
        assert all(y_proba.sum(axis=1) == 1.0)  # Probabilities sum to 1

    def test_model_validation(self):
        """Test model validation against thresholds"""
        metrics = {
            'accuracy': 0.85,
            'precision': 0.82,
            'recall': 0.78
        }

        # Test against minimum thresholds
        assert metrics['accuracy'] >= 0.8
        assert metrics['precision'] >= 0.75
        assert metrics['recall'] >= 0.7

    def test_model_serialization(self, tmp_path):
        """Test model save and load"""
        from sklearn.ensemble import RandomForestClassifier

        # Create and train model
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit([[1, 2], [3, 4], [5, 6]], [0, 1, 0])

        # Save model
        model_path = tmp_path / "test_model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)

        # Load model
        with open(model_path, 'rb') as f:
            loaded_model = pickle.load(f)

        # Test loaded model
        prediction = loaded_model.predict([[1, 2]])
        assert len(prediction) == 1

def test_data_drift():
    """Test for data drift detection"""
    import numpy as np
    from scipy.stats import ks_2samp

    # Simulate reference and current distributions
    reference_data = np.random.normal(0, 1, 1000)
    current_data = np.random.normal(0.1, 1.1, 1000)  # Slight drift

    # Kolmogorov-Smirnov test
    statistic, p_value = ks_2samp(reference_data, current_data)

    # If p_value < 0.05, significant drift detected
    drift_detected = p_value < 0.05

    assert drift_detected  # We expect drift in this test
```

## Model Deployment

### Model Serving Patterns

```python
from flask import Flask, request, jsonify
import pickle
import pandas as pd
from prometheus_client import Counter, Histogram, generate_latest

app = Flask(__name__)

# Load model
with open('models/churn_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Prometheus metrics
REQUEST_COUNT = Counter('model_requests_total', 'Total model requests', ['endpoint'])
REQUEST_LATENCY = Histogram('model_request_latency_seconds', 'Request latency', ['endpoint'])

@app.route('/health')
def health():
    return {'status': 'healthy'}

@app.route('/predict', methods=['POST'])
@REQUEST_LATENCY.labels(endpoint='/predict').time()
def predict():
    REQUEST_COUNT.labels(endpoint='/predict').inc()

    try:
        # Get input data
        data = request.get_json()

        # Convert to DataFrame
        df = pd.DataFrame([data])

        # Make prediction
        prediction = model.predict(df)[0]
        probability = model.predict_proba(df)[0].tolist()

        response = {
            'prediction': int(prediction),
            'probability': probability,
            'model_version': '1.0.0'
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Containerized Deployment

```dockerfile
# Dockerfile for ML model serving
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy model and application code
COPY models/ ./models/
COPY src/ ./src/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["python", "src/app.py"]
```

```yaml
# Kubernetes deployment manifest
apiVersion: apps/v1
kind: Deployment
metadata:
  name: churn-prediction-model
  labels:
    app: churn-prediction
spec:
  replicas: 3
  selector:
    matchLabels:
      app: churn-prediction
  template:
    metadata:
      labels:
        app: churn-prediction
    spec:
      containers:
      - name: model-server
        image: gcr.io/your-project/churn-model:v1.0.0
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
        env:
        - name: MODEL_PATH
          value: "/app/models/churn_model.pkl"
---
apiVersion: v1
kind: Service
metadata:
  name: churn-prediction-service
spec:
  selector:
    app: churn-prediction
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: churn-prediction-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.your-domain.com
    secretName: tls-secret
  rules:
  - host: api.your-domain.com
    http:
      paths:
      - path: /predict
        pathType: Prefix
        backend:
          service:
            name: churn-prediction-service
            port:
              number: 80
```

### Serverless Deployment

```python
# Google Cloud Functions deployment
import functions_framework
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic import PredictionServiceClient
import json

# Initialize Vertex AI client
aiplatform.init(project="your-project", location="us-central1")

@functions_framework.http
def predict_churn(request):
    """HTTP Cloud Function for churn prediction."""

    # Parse request
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'instances' in request_json:
        instances = request_json['instances']
    elif request_args and 'instances' in request_args:
        instances = json.loads(request_args.get('instances'))
    else:
        return json.dumps({'error': 'No instances provided'}), 400

    try:
        # Load model from Vertex AI
        model = aiplatform.Model(
            model_name="projects/your-project/locations/us-central1/models/churn_model"
        )

        # Make prediction
        prediction = model.predict(instances=instances)

        # Return response
        response = {
            'predictions': prediction.predictions,
            'model_version': model.version_id,
            'deployed_model_id': model.resource_name
        }

        return json.dumps(response), 200

    except Exception as e:
        return json.dumps({'error': str(e)}), 500
```

## Monitoring and Observability

### Model Performance Monitoring

```python
import prometheus_client as prom
from prometheus_client import Counter, Gauge, Histogram
import time
import logging

# Custom metrics
MODEL_PREDICTIONS = Counter(
    'model_predictions_total',
    'Total number of predictions made',
    ['model_name', 'model_version', 'prediction_class']
)

MODEL_LATENCY = Histogram(
    'model_prediction_latency_seconds',
    'Time spent processing prediction',
    ['model_name', 'model_version']
)

MODEL_ACCURACY = Gauge(
    'model_accuracy_current',
    'Current model accuracy based on recent predictions',
    ['model_name', 'model_version']
)

DATA_DRIFT_SCORE = Gauge(
    'data_drift_score',
    'Data drift detection score',
    ['feature_name', 'model_name']
)

class ModelMonitor:
    def __init__(self, model_name, model_version):
        self.model_name = model_name
        self.model_version = model_version
        self.logger = logging.getLogger(__name__)

        # Ground truth storage for accuracy calculation
        self.predictions = []
        self.actuals = []

    def record_prediction(self, prediction, probability, latency):
        """Record a model prediction"""
        MODEL_PREDICTIONS.labels(
            model_name=self.model_name,
            model_version=self.model_version,
            prediction_class=str(prediction)
        ).inc()

        MODEL_LATENCY.labels(
            model_name=self.model_name,
            model_version=self.model_version
        ).observe(latency)

        # Store for accuracy calculation
        self.predictions.append((prediction, probability))

        self.logger.info(f"Prediction recorded: {prediction} (prob: {max(probability)})")

    def record_actual(self, actual):
        """Record actual outcome for accuracy calculation"""
        self.actuals.append(actual)

        # Calculate rolling accuracy
        if len(self.predictions) >= 100:  # Calculate every 100 predictions
            recent_predictions = [p[0] for p in self.predictions[-100:]]
            recent_actuals = self.actuals[-100:]

            correct = sum(p == a for p, a in zip(recent_predictions, recent_actuals))
            accuracy = correct / len(recent_actuals)

            MODEL_ACCURACY.labels(
                model_name=self.model_name,
                model_version=self.model_version
            ).set(accuracy)

            self.logger.info(f"Rolling accuracy: {accuracy:.3f}")

    def check_data_drift(self, feature_data, reference_stats):
        """Check for data drift using statistical tests"""
        from scipy.stats import ks_2samp

        drift_detected = False

        for feature_name, current_values in feature_data.items():
            reference_values = reference_stats.get(feature_name, [])

            if len(reference_values) > 0:
                # Kolmogorov-Smirnov test
                statistic, p_value = ks_2samp(reference_values, current_values)

                # Update drift metric
                DATA_DRIFT_SCORE.labels(
                    feature_name=feature_name,
                    model_name=self.model_name
                ).set(statistic)

                if p_value < 0.05:  # Significant drift
                    drift_detected = True
                    self.logger.warning(f"Data drift detected in {feature_name} (p={p_value:.4f})")

        return drift_detected

# Usage in model serving
monitor = ModelMonitor("churn_model", "v1.0.0")

def predict_with_monitoring(features):
    start_time = time.time()

    # Make prediction
    prediction = model.predict([features])[0]
    probability = model.predict_proba([features])[0]

    # Record metrics
    latency = time.time() - start_time
    monitor.record_prediction(prediction, probability, latency)

    return prediction, probability
```

### Automated Retraining

```python
import schedule
import time
from datetime import datetime, timedelta
import logging

class ModelRetrainer:
    def __init__(self, model_name, performance_threshold=0.8, drift_threshold=0.05):
        self.model_name = model_name
        self.performance_threshold = performance_threshold
        self.drift_threshold = drift_threshold
        self.logger = logging.getLogger(__name__)

    def check_retraining_needed(self):
        """Check if model retraining is needed"""
        needs_retraining = False
        reasons = []

        # Check performance degradation
        current_accuracy = self.get_current_accuracy()
        if current_accuracy < self.performance_threshold:
            needs_retraining = True
            reasons.append(f"Accuracy dropped to {current_accuracy:.3f}")

        # Check for data drift
        drift_score = self.calculate_drift_score()
        if drift_score > self.drift_threshold:
            needs_retraining = True
            reasons.append(f"Data drift detected (score: {drift_score:.3f})")

        # Check data freshness
        days_since_training = self.get_days_since_training()
        if days_since_training > 30:  # Retrain monthly
            needs_retraining = True
            reasons.append(f"Model is {days_since_training} days old")

        if needs_retraining:
            self.logger.info(f"Retraining needed for {self.model_name}: {', '.join(reasons)}")
            return True, reasons
        else:
            self.logger.info(f"No retraining needed for {self.model_name}")
            return False, []

    def retrain_model(self):
        """Execute model retraining pipeline"""
        try:
            self.logger.info(f"Starting retraining for {self.model_name}")

            # Update training data
            self.update_training_data()

            # Run feature engineering
            self.run_feature_engineering()

            # Train new model
            new_model, metrics = self.train_new_model()

            # Validate new model
            if self.validate_new_model(metrics):
                # Deploy new model
                self.deploy_new_model(new_model, metrics)

                self.logger.info(f"Successfully retrained and deployed {self.model_name}")
                return True
            else:
                self.logger.error(f"New model validation failed for {self.model_name}")
                return False

        except Exception as e:
            self.logger.error(f"Retraining failed for {self.model_name}: {str(e)}")
            return False

    def update_training_data(self):
        """Fetch latest training data"""
        # Implementation depends on data source
        # Could be from database, data lake, etc.
        pass

    def run_feature_engineering(self):
        """Run feature engineering pipeline"""
        # Execute feature engineering steps
        pass

    def train_new_model(self):
        """Train new model version"""
        # Model training logic
        # Return model and metrics
        pass

    def validate_new_model(self, metrics):
        """Validate new model performance"""
        accuracy = metrics.get('accuracy', 0)
        return accuracy >= self.performance_threshold

    def deploy_new_model(self, model, metrics):
        """Deploy new model to production"""
        # Model deployment logic
        # Update model registry, API endpoints, etc.
        pass

    def get_current_accuracy(self):
        """Get current model accuracy from monitoring"""
        # Query monitoring system for current accuracy
        return 0.85  # Placeholder

    def calculate_drift_score(self):
        """Calculate data drift score"""
        # Implement drift detection logic
        return 0.02  # Placeholder

    def get_days_since_training(self):
        """Get days since last training"""
        # Query model registry for last training date
        return 15  # Placeholder

# Automated retraining scheduler
def setup_automated_retraining():
    retrainer = ModelRetrainer("churn_model")

    # Check daily for retraining needs
    schedule.every().day.at("02:00").do(
        lambda: retrainer.check_retraining_needed()
    )

    # Run retraining weekly
    schedule.every().week.do(
        lambda: retrainer.retrain_model()
    )

    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour

if __name__ == "__main__":
    setup_automated_retraining()
```

## Governance and Compliance

### Model Governance

```python
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import json

@dataclass
class ModelMetadata:
    model_name: str
    version: str
    created_at: datetime
    created_by: str
    description: str
    model_type: str
    training_data: Dict[str, str]
    hyperparameters: Dict[str, any]
    metrics: Dict[str, float]
    artifacts: List[str]
    approval_status: str
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    compliance_checks: List[str]

class ModelGovernance:
    def __init__(self, registry_path: str = "model_registry/"):
        self.registry_path = registry_path

    def register_model(self, metadata: ModelMetadata):
        """Register a new model in the governance system"""
        # Save metadata
        metadata_path = f"{self.registry_path}{metadata.model_name}_{metadata.version}.json"

        with open(metadata_path, 'w') as f:
            json.dump(metadata.__dict__, f, default=str, indent=2)

        print(f"Model {metadata.model_name} v{metadata.version} registered")

    def approve_model(self, model_name: str, version: str, approver: str):
        """Approve model for production deployment"""
        metadata = self.get_model_metadata(model_name, version)

        if not metadata:
            raise ValueError(f"Model {model_name} v{version} not found")

        # Update approval status
        metadata.approval_status = "approved"
        metadata.approved_by = approver
        metadata.approved_at = datetime.now()

        # Save updated metadata
        self.register_model(metadata)

        print(f"Model {model_name} v{version} approved by {approver}")

    def audit_model(self, model_name: str, version: str):
        """Perform compliance audit on model"""
        metadata = self.get_model_metadata(model_name, version)

        audit_results = {
            "model_name": model_name,
            "version": version,
            "audit_timestamp": datetime.now(),
            "checks": []
        }

        # Check required fields
        required_fields = ["description", "training_data", "metrics"]
        for field in required_fields:
            if not getattr(metadata, field, None):
                audit_results["checks"].append({
                    "check": f"Required field '{field}'",
                    "status": "FAILED",
                    "details": f"Field '{field}' is missing or empty"
                })
            else:
                audit_results["checks"].append({
                    "check": f"Required field '{field}'",
                    "status": "PASSED"
                })

        # Check performance thresholds
        accuracy = metadata.metrics.get("accuracy", 0)
        if accuracy < 0.8:
            audit_results["checks"].append({
                "check": "Minimum accuracy threshold",
                "status": "FAILED",
                "details": f"Accuracy {accuracy} below 0.8 threshold"
            })
        else:
            audit_results["checks"].append({
                "check": "Minimum accuracy threshold",
                "status": "PASSED"
            })

        # Check data compliance
        training_data = metadata.training_data
        if "pii_fields" in training_data:
            audit_results["checks"].append({
                "check": "PII data handling",
                "status": "WARNING",
                "details": "Model trained on data containing PII fields"
            })

        # Save audit results
        audit_path = f"{self.registry_path}audits/{model_name}_{version}_audit.json"
        with open(audit_path, 'w') as f:
            json.dump(audit_results, f, default=str, indent=2)

        return audit_results

    def get_model_metadata(self, model_name: str, version: str) -> Optional[ModelMetadata]:
        """Retrieve model metadata"""
        metadata_path = f"{self.registry_path}{model_name}_{version}.json"

        try:
            with open(metadata_path, 'r') as f:
                data = json.load(f)

            # Convert string dates back to datetime
            data['created_at'] = datetime.fromisoformat(data['created_at'])
            if data.get('approved_at'):
                data['approved_at'] = datetime.fromisoformat(data['approved_at'])

            return ModelMetadata(**data)
        except FileNotFoundError:
            return None

    def list_models(self, status_filter: Optional[str] = None) -> List[ModelMetadata]:
        """List all registered models"""
        import os

        models = []
        for filename in os.listdir(self.registry_path):
            if filename.endswith('.json') and not filename.startswith('audit'):
                try:
                    model_name, version = filename.rsplit('_', 1)
                    version = version.replace('.json', '')

                    metadata = self.get_model_metadata(model_name, version)
                    if metadata and (not status_filter or metadata.approval_status == status_filter):
                        models.append(metadata)
                except:
                    continue

        return models

# Usage example
def demonstrate_governance():
    governance = ModelGovernance()

    # Register a new model
    metadata = ModelMetadata(
        model_name="customer_churn_model",
        version="1.0.0",
        created_at=datetime.now(),
        created_by="data-scientist@company.com",
        description="Random Forest model for customer churn prediction",
        model_type="RandomForestClassifier",
        training_data={
            "source": "customer_database",
            "date_range": "2023-01-01 to 2023-12-31",
            "size": "100000 records",
            "features": ["tenure", "monthly_charges", "contract_type"]
        },
        hyperparameters={
            "n_estimators": 100,
            "max_depth": 10,
            "random_state": 42
        },
        metrics={
            "accuracy": 0.85,
            "precision": 0.82,
            "recall": 0.78,
            "f1_score": 0.80
        },
        artifacts=["model.pkl", "feature_importance.png", "confusion_matrix.png"],
        approval_status="pending",
        approved_by=None,
        approved_at=None,
        compliance_checks=["gdpr_compliant", "bias_audited"]
    )

    governance.register_model(metadata)

    # Perform audit
    audit_results = governance.audit_model("customer_churn_model", "1.0.0")
    print("Audit Results:", audit_results)

    # Approve model
    governance.approve_model("customer_churn_model", "1.0.0", "ml-engineer@company.com")

    # List approved models
    approved_models = governance.list_models(status_filter="approved")
    print(f"Approved models: {len(approved_models)}")
```

## Best Practices

### Development Best Practices
1. **Version Control**: Use Git for code, DVC for data, MLflow for experiments
2. **Code Quality**: Implement testing, linting, and code reviews
3. **Documentation**: Maintain clear documentation for models and pipelines
4. **Reproducibility**: Ensure experiments can be reproduced consistently

### Deployment Best Practices
1. **Containerization**: Use Docker for consistent environments
2. **Orchestration**: Leverage Kubernetes for scalable deployments
3. **Monitoring**: Implement comprehensive monitoring and alerting
4. **Rollback Strategy**: Have clear procedures for model rollback

### Monitoring Best Practices
1. **Performance Metrics**: Track accuracy, latency, and resource usage
2. **Data Quality**: Monitor for data drift and concept drift
3. **Business Metrics**: Align with business KPIs and outcomes
4. **Alerting**: Set up automated alerts for performance degradation

### Governance Best Practices
1. **Model Registry**: Maintain centralized model catalog
2. **Approval Workflows**: Implement review processes for production deployment
3. **Audit Trails**: Keep comprehensive logs of model changes and decisions
4. **Compliance**: Ensure regulatory compliance and ethical AI practices

MLOps represents the convergence of machine learning and DevOps, enabling organizations to operationalize ML models reliably and efficiently. By implementing comprehensive MLOps practices, teams can reduce time-to-market, improve model reliability, and ensure continuous value delivery from their ML investments.
