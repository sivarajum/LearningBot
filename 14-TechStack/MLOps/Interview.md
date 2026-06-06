# MLOps Interview Questions and Answers

## Beginner Level Questions

### Q1: What is MLOps and why is it important?

**Answer:**
MLOps (Machine Learning Operations) is the practice of operationalizing machine learning models, bringing DevOps principles to ML workflows. It encompasses the entire ML lifecycle from development through deployment, monitoring, and maintenance.

**Importance:**
- **Reliability**: Ensures models work consistently in production
- **Scalability**: Handles varying loads and data volumes
- **Reproducibility**: Consistent results across environments
- **Monitoring**: Tracks model performance and data quality
- **Automation**: Reduces manual work and errors
- **Governance**: Ensures compliance and security

**Benefits:**
- Faster time to market
- Improved model quality
- Reduced operational costs
- Better collaboration
- Regulatory compliance

### Q2: Explain the ML lifecycle and MLOps stages.

**Answer:**

**ML Lifecycle Stages:**

**1. Data Collection:**
- Gather and ingest data
- Data validation and quality checks
- Data versioning and lineage

**2. Data Preparation:**
- Data cleaning and preprocessing
- Feature engineering
- Data splitting (train/validation/test)

**3. Model Training:**
- Experiment tracking
- Hyperparameter tuning
- Model versioning
- Model evaluation

**4. Model Deployment:**
- Model packaging
- Containerization
- Deployment to production
- A/B testing

**5. Monitoring:**
- Model performance tracking
- Data drift detection
- Model drift detection
- Alerting and logging

**6. Retraining:**
- Trigger retraining
- Model updates
- Rollback mechanisms

### Q3: What is the difference between MLOps and DevOps?

**Answer:**

**DevOps:**
- Focuses on software development and deployment
- Code changes are the primary artifacts
- Testing and validation are straightforward
- Deployment is relatively simple

**MLOps:**
- Focuses on ML model lifecycle
- Models, data, and code are artifacts
- Testing involves data and model validation
- Deployment includes model serving and monitoring
- Requires data pipeline management
- Needs model versioning and experiment tracking

**Key Differences:**
- **Artifacts**: Code vs Models + Data + Code
- **Testing**: Unit/integration tests vs Data/model validation
- **Monitoring**: Application metrics vs Model performance metrics
- **Deployment**: Application deployment vs Model serving

### Q4: Explain model versioning and experiment tracking.

**Answer:**

**Model Versioning:**
- Track different versions of models
- Store model artifacts and metadata
- Enable model rollback
- Compare model performance

**Experiment Tracking:**
- Track experiments and hyperparameters
- Log metrics and artifacts
- Compare experiment results
- Reproduce experiments

**Tools:**
- **MLflow**: Experiment tracking and model registry
- **Weights & Biases**: Experiment tracking and visualization
- **DVC**: Data version control
- **Git LFS**: Large file storage for models

**Example:**
```python
import mlflow

# Start experiment
mlflow.set_experiment("customer_churn")

with mlflow.start_run():
    # Log parameters
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)
    
    # Train model
    model = train_model()
    
    # Log metrics
    mlflow.log_metric("accuracy", 0.95)
    mlflow.log_metric("f1_score", 0.92)
    
    # Log model
    mlflow.sklearn.log_model(model, "model")
```

### Q5: What is model serving and what are the deployment patterns?

**Answer:**

**Model Serving:**
- Making trained models available for predictions
- Handling inference requests
- Managing model versions
- Scaling for load

**Deployment Patterns:**

**1. Batch Prediction:**
- Process predictions in batches
- Scheduled or on-demand
- High throughput
- Higher latency

**2. Real-time Prediction:**
- Process predictions in real-time
- Low latency
- REST API or gRPC
- Lower throughput

**3. Edge Deployment:**
- Deploy models to edge devices
- Low latency
- Offline capability
- Limited resources

**Example:**
```python
from flask import Flask, request, jsonify
import pickle

app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb'))

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    prediction = model.predict(data['features'])
    return jsonify({'prediction': prediction.tolist()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## Intermediate Level Questions

### Q6: Explain data drift and model drift detection.

**Answer:**

**Data Drift:**
- Change in input data distribution over time
- Affects model performance
- Detected by comparing data distributions
- Requires monitoring and alerting

**Model Drift:**
- Degradation in model performance over time
- Caused by data drift or concept drift
- Detected by monitoring metrics
- Requires retraining

**Detection Methods:**
- Statistical tests (KS test, Chi-square test)
- Distribution comparisons
- Performance metric tracking
- Anomaly detection

**Example:**
```python
from scipy import stats
import numpy as np

def detect_data_drift(reference_data, current_data):
    # Kolmogorov-Smirnov test
    statistic, p_value = stats.ks_2samp(reference_data, current_data)
    
    if p_value < 0.05:
        return True  # Drift detected
    return False

# Monitor data drift
reference_distribution = training_data['feature']
current_distribution = production_data['feature']

if detect_data_drift(reference_distribution, current_distribution):
    alert("Data drift detected")
```

### Q7: How do you implement CI/CD for ML pipelines?

**Answer:**

**CI/CD for ML:**
- Continuous Integration: Test code and data
- Continuous Deployment: Deploy models automatically
- Automated testing: Unit, integration, and validation tests
- Automated deployment: Deploy to staging and production

**Pipeline Stages:**

**1. Code Testing:**
- Unit tests for data processing
- Integration tests for pipelines
- Code quality checks

**2. Data Validation:**
- Schema validation
- Data quality checks
- Data drift detection

**3. Model Validation:**
- Model performance tests
- Model comparison
- A/B testing

**4. Deployment:**
- Deploy to staging
- Run smoke tests
- Deploy to production
- Monitor deployment

**Example:**
```yaml
# CI/CD pipeline
stages:
  - test
  - validate_data
  - train_model
  - validate_model
  - deploy_staging
  - deploy_production

test:
  script:
    - pytest tests/

validate_data:
  script:
    - python validate_data.py

train_model:
  script:
    - python train_model.py

validate_model:
  script:
    - python validate_model.py

deploy_staging:
  script:
    - kubectl apply -f k8s/staging/

deploy_production:
  script:
    - kubectl apply -f k8s/production/
```

### Q8: Explain model monitoring and observability.

**Answer:**

**Model Monitoring:**
- Track model performance metrics
- Monitor prediction latency
- Track prediction distributions
- Detect anomalies

**Observability:**
- **Metrics**: Performance metrics, business metrics
- **Logs**: Prediction logs, error logs
- **Traces**: Request tracing, dependency tracing
- **Dashboards**: Visualization of metrics and logs

**Key Metrics:**
- **Performance**: Accuracy, precision, recall, F1-score
- **Latency**: Prediction time, p50, p95, p99
- **Throughput**: Requests per second
- **Errors**: Error rate, error types
- **Data Quality**: Data drift, data quality scores

**Example:**
```python
import logging
from prometheus_client import Counter, Histogram

# Metrics
prediction_counter = Counter('predictions_total', 'Total predictions')
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')
error_counter = Counter('prediction_errors_total', 'Prediction errors')

def predict_with_monitoring(model, data):
    prediction_counter.inc()
    
    with prediction_latency.time():
        try:
            prediction = model.predict(data)
            return prediction
        except Exception as e:
            error_counter.inc()
            logging.error(f"Prediction error: {e}")
            raise
```

## Advanced Level Questions

### Q9: How do you handle model A/B testing and canary deployments?

**Answer:**

**A/B Testing:**
- Compare two model versions
- Split traffic between models
- Measure performance metrics
- Statistical significance testing

**Canary Deployment:**
- Gradually roll out new model
- Start with small percentage of traffic
- Monitor performance and errors
- Increase traffic if successful

**Example:**
```python
import random

def route_prediction(model_a, model_b, data, traffic_split=0.5):
    # Route traffic based on split
    if random.random() < traffic_split:
        model = model_a
        variant = 'A'
    else:
        model = model_b
        variant = 'B'
    
    prediction = model.predict(data)
    
    # Log variant for analysis
    log_prediction(variant, prediction, data)
    
    return prediction
```

### Q10: Explain feature stores and their role in MLOps.

**Answer:**

**Feature Stores:**
- Centralized storage for features
- Consistent feature definitions
- Feature versioning and lineage
- Real-time and batch features

**Benefits:**
- **Consistency**: Same features in training and serving
- **Reusability**: Share features across models
- **Efficiency**: Reduce feature computation
- **Governance**: Track feature usage and lineage

**Components:**
- **Feature Registry**: Feature definitions and metadata
- **Offline Store**: Historical features for training
- **Online Store**: Real-time features for serving
- **Feature Serving**: API for feature access

**Example:**
```python
from feast import FeatureStore

# Initialize feature store
store = FeatureStore(repo_path=".")

# Get features for training
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "user_stats:age",
        "user_stats:total_orders",
        "product_stats:price"
    ]
).to_df()

# Get features for serving
features = store.get_online_features(
    entity_rows=[{"user_id": 123}],
    features=[
        "user_stats:age",
        "user_stats:total_orders"
    ]
)
```

### Q11: How do you implement model rollback and version management?

**Answer:**

**Model Rollback:**
- Revert to previous model version
- Triggered by performance degradation
- Automatic or manual rollback
- Maintain model version history

**Version Management:**
- Store multiple model versions
- Tag versions (production, staging, etc.)
- Track version metadata
- Enable version comparison

**Example:**
```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# List model versions
versions = client.search_model_versions("name='churn_model'")

# Get current production model
production_model = client.get_model_version(
    name="churn_model",
    version="production"
)

# Rollback to previous version
if model_performance_degraded:
    previous_version = client.get_model_version(
        name="churn_model",
        version=production_model.version - 1
    )
    client.transition_model_version_stage(
        name="churn_model",
        version=previous_version.version,
        stage="Production"
    )
```

### Q12: Explain MLOps infrastructure and tooling.

**Answer:**

**MLOps Infrastructure:**

**Experiment Tracking:**
- MLflow, Weights & Biases, TensorBoard
- Track experiments and models
- Compare results
- Reproduce experiments

**Model Registry:**
- MLflow Model Registry, Kubeflow
- Store and version models
- Manage model lifecycle
- Enable model deployment

**Model Serving:**
- TensorFlow Serving, TorchServe, MLflow
- Serve models for inference
- Handle requests
- Scale for load

**Orchestration:**
- Airflow, Kubeflow, Prefect
- Schedule and coordinate workflows
- Manage dependencies
- Handle errors

**Monitoring:**
- Prometheus, Grafana, Evidently
- Track metrics and logs
- Detect anomalies
- Alert on issues

**Example:**
```python
# MLOps pipeline
import mlflow
from airflow import DAG
from airflow.operators.python import PythonOperator

def train_and_register_model():
    with mlflow.start_run():
        # Train model
        model = train_model()
        
        # Log model
        mlflow.sklearn.log_model(model, "model")
        
        # Register model
        mlflow.register_model(
            model_uri=f"runs:/{mlflow.active_run().info.run_id}/model",
            name="churn_model"
        )

dag = DAG('mlops_pipeline')

train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_and_register_model,
    dag=dag
)
```

---

## Key Takeaways

1. **MLOps operationalizes ML models** throughout their lifecycle
2. **Model versioning and experiment tracking** ensure reproducibility
3. **Data drift and model drift** require continuous monitoring
4. **CI/CD pipelines** automate model deployment
5. **Model monitoring** tracks performance and detects issues
6. **Feature stores** provide consistent features for training and serving
7. **A/B testing and canary deployments** enable safe model updates
8. **MLOps infrastructure** includes tracking, serving, orchestration, and monitoring tools

