# MLOps Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **MLflow Tracking**
```python
import mlflow

mlflow.set_experiment("my-experiment")

with mlflow.start_run():
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_metric("accuracy", 0.95)
    mlflow.sklearn.log_model(model, "model")
```

### 2. **Model Registry**
```python
model_uri = f"runs:/{run_id}/model"
model_version = mlflow.register_model(model_uri, "churn_model")
```

### 3. **Model Serving**
```bash
mlflow models serve -m "models:/churn_model/Production" -p 5001
```

## Level 2 – Production Patterns

### CI/CD
```yaml
# .github/workflows/ml.yml
name: ML Pipeline
on: [push]
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Train model
        run: python train.py
      - name: Register model
        run: mlflow.register_model(...)
```

### Feature Store
```python
from feast import FeatureStore

store = FeatureStore(repo_path=".")

features = store.get_online_features(
    entity_rows=[{"user_id": 1}],
    features=["user_features:age", "user_features:score"]
)
```

## Level 3 – Architect Playbook

### Monitoring
```python
import evidently

from evidently.metrics import DataDriftMetric

drift_metric = DataDriftMetric()
drift_metric.calculate(reference_data, current_data)
```

## Ops Cheat Sheet

| Task | Tool | Notes |
| --- | --- | --- |
| Track | MLflow | Experiment tracking |
| Serve | MLflow, TorchServe | Model serving |
| Monitor | Evidently, W&B | Model monitoring |

## Checklist Before Production

- [ ] Set up experiment tracking
- [ ] Implement model registry
- [ ] Set up CI/CD
- [ ] Configure model serving
- [ ] Set up monitoring
- [ ] Implement alerting
- [ ] Set up feature store
- [ ] Document pipeline
