# MLflow Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```bash
pip install mlflow

# Start tracking server
mlflow ui --port 5000
```

### 2. **Basic Tracking**
```python
import mlflow
import mlflow.sklearn

mlflow.set_experiment("my-experiment")

with mlflow.start_run():
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_metric("accuracy", 0.95)
    mlflow.sklearn.log_model(model, "model")
```

### 3. **View Results**
```python
# Access UI at http://localhost:5000
# Or programmatically
runs = mlflow.search_runs(experiment_names=["my-experiment"])
```

## Level 2 – Production Patterns

### Model Registry
```python
model_uri = f"runs:/{run_id}/model"
model_version = mlflow.register_model(model_uri, "churn_model")

# Transition to staging
client = mlflow.tracking.MlflowClient()
client.transition_model_version_stage(
    name="churn_model",
    version=model_version.version,
    stage="Staging"
)
```

### Projects
```python
# MLproject file
# name: my-project
# conda_env: conda.yaml
# entry_points:
#   main:
#     command: "python train.py"

mlflow.run("path/to/project")
```

## Level 3 – Architect Playbook

### Remote Tracking
```python
mlflow.set_tracking_uri("http://mlflow-server:5000")
```

### Custom Flavors
```python
from mlflow.pyfunc import PythonModel

class CustomModel(PythonModel):
    def predict(self, context, model_input):
        return predictions

mlflow.pyfunc.log_model("custom_model", python_model=CustomModel())
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Start UI | `mlflow ui` | Local server |
| Register | `mlflow.register_model()` | Register model |
| Serve | `mlflow models serve` | Serve model |

## Checklist Before Production

- [ ] Set up remote tracking server
- [ ] Configure model registry
- [ ] Set up model serving
- [ ] Configure authentication
- [ ] Set up monitoring
- [ ] Implement model validation
- [ ] Set up CI/CD
- [ ] Configure artifact storage
