# Weights & Biases Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```bash
pip install wandb

# Login
wandb login
```

### 2. **Basic Tracking**
```python
import wandb

wandb.init(project="my-project")

# Log parameters
wandb.config.learning_rate = 0.01
wandb.config.epochs = 10

# Log metrics
wandb.log({"accuracy": 0.95, "loss": 0.05})

# Log model
wandb.log_model("model", "model.pkl")
```

### 3. **Hyperparameter Sweeps**
```python
sweep_config = {
    "method": "random",
    "parameters": {
        "learning_rate": {"min": 0.001, "max": 0.1},
        "epochs": {"values": [10, 20, 30]}
    }
}

sweep_id = wandb.sweep(sweep_config, project="my-project")
wandb.agent(sweep_id, train_function)
```

## Level 2 – Production Patterns

### Advanced Tracking
```python
# Log images
wandb.log({"examples": [wandb.Image(img) for img in images]})

# Log tables
wandb.log({"predictions": wandb.Table(data=df)})

# Log audio
wandb.log({"audio": wandb.Audio(audio_data, sample_rate=16000)})
```

### Model Registry
```python
# Register model
run = wandb.init(project="my-project")
artifact = wandb.Artifact("model", type="model")
artifact.add_file("model.pkl")
run.log_artifact(artifact)

# Use model
artifact = run.use_artifact("model:latest")
artifact.download()
```

### Integration with MLflow
```python
import wandb
import mlflow

with wandb.init() as run:
    # W&B tracking
    wandb.log({"metric": value})
    
    # MLflow tracking
    with mlflow.start_run():
        mlflow.log_metric("metric", value)
```

## Level 3 – Architect Playbook

### Team Collaboration
```python
# Set team
wandb.init(project="team-project", entity="my-team")

# Share runs
wandb.init(project="shared-project", tags=["experiment"])
```

### Production Monitoring
```python
# Monitor model in production
wandb.init(project="production-monitoring")

# Log predictions
wandb.log({
    "prediction": prediction,
    "ground_truth": true_value,
    "timestamp": datetime.now()
})
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Login | `wandb login` | Authenticate |
| Init | `wandb.init()` | Start run |
| Log | `wandb.log()` | Log metrics |
| Finish | `wandb.finish()` | End run |
| Sweep | `wandb.sweep()` | Create sweep |

## Checklist Before Production

- [ ] Set up team workspace
- [ ] Configure proper project organization
- [ ] Set up model registry
- [ ] Implement proper logging
- [ ] Set up monitoring
- [ ] Configure alerts
- [ ] Set up cost tracking
- [ ] Implement proper access controls
