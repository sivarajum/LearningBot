# Weights & Biases Interview Questions and Answers

## Core Concepts and Setup

### Q1: What is Weights & Biases (W&B) and how does it differ from other ML experiment tracking tools?

**Answer:**
Weights & Biases (W&B) is a machine learning platform that provides experiment tracking, model versioning, and collaboration tools for ML teams. It offers a comprehensive suite of features for the entire ML lifecycle.

**Key Differences from Other Tools:**

| Feature | W&B | MLflow | TensorBoard | Comet.ml |
|---------|-----|--------|-------------|----------|
| **Experiment Tracking** | ✅ Rich UI, real-time | ✅ Basic tracking | ✅ TensorFlow-focused | ✅ Similar to W&B |
| **Hyperparameter Sweeps** | ✅ Built-in Bayesian optimization | ❌ Manual implementation | ❌ Limited | ✅ Available |
| **Model Registry** | ✅ Full lifecycle management | ✅ Basic versioning | ❌ No | ✅ Available |
| **Team Collaboration** | ✅ Reports, comments, sharing | ❌ Limited | ❌ Limited | ✅ Available |
| **Artifact Management** | ✅ Automatic versioning | ✅ Basic | ❌ Limited | ✅ Available |
| **Integrations** | ✅ Extensive (PyTorch, TF, HF) | ✅ Good | ✅ TensorFlow only | ✅ Good |
| **Pricing Model** | Freemium with team plans | Open-source | Free | Freemium |

**W&B's Unique Strengths:**
- **Real-time collaboration**: Live dashboards, comments, and sharing
- **Integrated sweeps**: Built-in hyperparameter optimization
- **Rich visualizations**: Interactive plots, comparisons, and reports
- **Model lineage**: Complete traceability from data to deployment
- **Team features**: Workspaces, access control, and automation

### Q2: How do you set up and initialize W&B for experiment tracking?

**Answer:**

**Installation and Setup:**
```bash
# Install W&B
pip install wandb

# Login (first time setup)
wandb login
# Or set API key
export WANDB_API_KEY=your_api_key_here
```

**Basic Initialization:**
```python
import wandb

# Simple initialization
wandb.init(project="my-ml-project")

# Advanced initialization
run = wandb.init(
    project="my-ml-project",
    name="experiment-1",
    notes="Testing different learning rates",
    tags=["baseline", "hyperparameter-tuning"],
    config={
        "learning_rate": 0.01,
        "batch_size": 32,
        "epochs": 100,
        "model_architecture": "resnet50",
        "optimizer": "adam"
    },
    group="experiment-group-1",  # Group related runs
    job_type="training"  # Type of job
)
```

**Configuration Management:**
```python
# Method 1: Pass config directly
config = {"lr": 0.01, "batch_size": 32}
wandb.init(project="my-project", config=config)

# Method 2: Use config object
wandb.config.update({"dropout": 0.5, "activation": "relu"})

# Method 3: Load from file
import yaml
with open("config.yaml") as f:
    config = yaml.safe_load(f)
wandb.init(project="my-project", config=config)

# Access config values
learning_rate = wandb.config.learning_rate
batch_size = wandb.config["batch_size"]
```

**Environment-Specific Setup:**
```python
# Development setup
if os.getenv("ENVIRONMENT") == "development":
    wandb.init(
        project="dev-experiments",
        mode="offline"  # Don't sync to cloud
    )

# Production setup
elif os.getenv("ENVIRONMENT") == "production":
    wandb.init(
        project="production-models",
        entity="my-team",  # Team workspace
        settings=wandb.Settings(
            _sync=True,  # Ensure sync
            _save_code=True  # Save code snapshot
        )
    )
```

## Experiment Tracking

### Q3: How do you log metrics, hyperparameters, and artifacts in W&B?

**Answer:**

**Logging Metrics:**
```python
# Basic metric logging
wandb.log({"loss": 0.5, "accuracy": 0.85})

# Log with step (for time series)
for epoch in range(100):
    train_loss = train_epoch()
    val_acc = validate_epoch()

    wandb.log({
        "epoch": epoch,
        "train_loss": train_loss,
        "val_accuracy": val_acc,
        "learning_rate": get_current_lr()
    }, step=epoch)

# Log multiple metrics at once
metrics = {
    "train_acc": 0.92,
    "val_acc": 0.89,
    "test_acc": 0.87,
    "precision": 0.91,
    "recall": 0.88,
    "f1_score": 0.89
}
wandb.log(metrics)
```

**Logging Rich Media:**
```python
# Log plots
import matplotlib.pyplot as plt

def log_training_curves():
    plt.figure(figsize=(12, 4))

    plt.subplot(1, 3, 1)
    plt.plot(losses, label='Training Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.legend()
    plt.title('Loss Curves')

    plt.subplot(1, 3, 2)
    plt.plot(accuracies, label='Training Accuracy')
    plt.plot(val_accuracies, label='Validation Accuracy')
    plt.legend()
    plt.title('Accuracy Curves')

    plt.subplot(1, 3, 3)
    plt.plot(learning_rates)
    plt.title('Learning Rate Schedule')

    wandb.log({"training_curves": plt})
    plt.close()

# Log images
def log_sample_predictions(images, predictions, labels):
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    axes = axes.flatten()

    for i in range(10):
        axes[i].imshow(images[i].permute(1, 2, 0))
        pred_class = predictions[i].argmax()
        true_class = labels[i]
        color = 'green' if pred_class == true_class else 'red'
        axes[i].set_title(f'Pred: {pred_class}\nTrue: {true_class}', color=color)
        axes[i].axis('off')

    wandb.log({"sample_predictions": fig})
    plt.close()
```

**Logging Artifacts:**
```python
# Log model artifact
artifact = wandb.Artifact(
    name="my-model",
    type="model",
    description="Trained ResNet model for image classification",
    metadata={
        "architecture": "ResNet50",
        "dataset": "ImageNet",
        "epochs": 100,
        "final_accuracy": 0.95,
        "training_time": "2h 30m"
    }
)

# Add files to artifact
artifact.add_file("model.pth")
artifact.add_file("config.yaml")
artifact.add_file("requirements.txt")

# Add entire directory
artifact.add_dir("checkpoints/")

# Log artifact
run.log_artifact(artifact)

# Log dataset artifact
dataset_artifact = wandb.Artifact("my-dataset", type="dataset")
dataset_artifact.add_file("data/train.csv")
dataset_artifact.add_file("data/validation.csv")
run.log_artifact(dataset_artifact)
```

**Advanced Logging Features:**
```python
# Log histograms
wandb.log({
    "weights_dist": wandb.Histogram(model.conv1.weight.data.numpy()),
    "gradients_dist": wandb.Histogram(model.conv1.weight.grad.numpy()),
    "activations_dist": wandb.Histogram(activations)
})

# Log 3D point clouds or molecular structures
wandb.log({
    "point_cloud": wandb.Object3D(point_cloud_data),
    "molecule": wandb.Molecule(mol_file_or_data)
})

# Log audio
wandb.log({
    "generated_audio": wandb.Audio(audio_array, sample_rate=44100),
    "spectrogram": wandb.Image(spectrogram_image)
})

# Log text and tables
wandb.log({
    "model_summary": wandb.Html(model.summary()),
    "predictions_table": wandb.Table(
        columns=["input", "prediction", "confidence"],
        data=[["text1", "class_a", 0.95], ["text2", "class_b", 0.87]]
    )
})
```

### Q4: How do you organize and compare multiple experiments in W&B?

**Answer:**

**Experiment Organization:**
```python
# Use descriptive project names
wandb.init(project="customer_churn_prediction_v2")

# Group related runs
wandb.init(
    project="my-project",
    group="architecture_search",  # All runs in this group
    name="resnet50_exp1",
    job_type="training"
)

# Use tags for categorization
wandb.init(
    project="my-project",
    tags=["baseline", "production-candidate", "hyperparameter-tuning"]
)

# Set run names and notes
wandb.init(
    project="my-project",
    name="lr_0.001_bs_64_adam",
    notes="Testing Adam optimizer with smaller learning rate"
)
```

**Comparing Experiments:**
```python
# Using W&B Public API
import wandb

api = wandb.Api()

# Get runs from a project
runs = api.runs("my-username/my-project")

# Filter runs
filtered_runs = [run for run in runs if run.config.get("learning_rate") > 0.001]

# Compare specific metrics
comparison_data = []
for run in filtered_runs:
    comparison_data.append({
        "name": run.name,
        "learning_rate": run.config.get("learning_rate"),
        "final_accuracy": run.summary.get("final_accuracy"),
        "training_time": run.summary.get("training_time")
    })

# Create comparison table
comparison_table = wandb.Table(
    columns=["Run Name", "Learning Rate", "Final Accuracy", "Training Time"],
    data=[[d["name"], d["learning_rate"], d["final_accuracy"], d["training_time"]]
          for d in comparison_data]
)

# Log comparison
with wandb.init(project="experiment-comparison") as run:
    run.log({"model_comparison": comparison_table})
```

**Advanced Comparison Techniques:**
```python
# Statistical comparison
import numpy as np
from scipy import stats

def compare_experiments(runs, metric_name):
    """Perform statistical comparison of runs"""
    metrics = [run.summary.get(metric_name) for run in runs if run.summary.get(metric_name)]

    if len(metrics) < 2:
        return "Need at least 2 runs for comparison"

    # Basic statistics
    stats_summary = {
        "mean": np.mean(metrics),
        "std": np.std(metrics),
        "min": np.min(metrics),
        "max": np.max(metrics),
        "best_run": runs[np.argmax(metrics)].name
    }

    # Pairwise t-test for significance
    if len(metrics) == 2:
        t_stat, p_value = stats.ttest_ind(metrics[0:1], metrics[1:2])
        stats_summary["t_statistic"] = t_stat
        stats_summary["p_value"] = p_value
        stats_summary["significant"] = p_value < 0.05

    return stats_summary

# Correlation analysis
def analyze_parameter_correlations(runs, params, metrics):
    """Analyze how parameters affect metrics"""
    param_values = []
    metric_values = []

    for run in runs:
        param_combo = [run.config.get(p) for p in params]
        metric_combo = [run.summary.get(m) for m in metrics]

        if all(param_combo) and all(metric_combo):
            param_values.append(param_combo)
            metric_values.append(metric_combo)

    # Calculate correlations
    param_array = np.array(param_values)
    metric_array = np.array(metric_values)

    correlations = np.corrcoef(param_array.T, metric_array.T)

    return {
        "param_metric_correlations": correlations,
        "strongest_correlations": np.unravel_index(
            np.argmax(np.abs(correlations)), correlations.shape
        )
    }
```

## Hyperparameter Optimization

### Q5: How do you set up and run hyperparameter sweeps in W&B?

**Answer:**

**Sweep Configuration:**
```yaml
# sweep.yaml
program: train.py
method: bayes  # bayes, grid, or random
metric:
  name: val_accuracy
  goal: maximize
parameters:
  learning_rate:
    min: 0.0001
    max: 0.1
  batch_size:
    values: [16, 32, 64, 128]
  dropout:
    distribution: uniform
    min: 0.1
    max: 0.5
  optimizer:
    values: ["adam", "sgd", "rmsprop"]
  model_depth:
    values: [18, 34, 50, 101, 152]
early_terminate:
  type: hyperband
  min_iter: 3
```

**Running Sweeps:**
```python
# Method 1: CLI
wandb sweep sweep.yaml
# Returns: wandb: Creating sweep with ID: abc123
wandb agent abc123

# Method 2: Python API
sweep_id = wandb.sweep(sweep_config, project="my-sweep-project")

# Run single agent
wandb.agent(sweep_id, function=train_function)

# Run multiple agents (parallel)
import multiprocessing

def run_agent(sweep_id):
    wandb.agent(sweep_id, function=train_function)

processes = []
for _ in range(4):  # Run 4 parallel agents
    p = multiprocessing.Process(target=run_agent, args=(sweep_id,))
    p.start()
    processes.append(p)

for p in processes:
    p.join()
```

**Training Function for Sweeps:**
```python
def train_function():
    # Initialize run (automatically gets sweep parameters)
    with wandb.init() as run:
        # Get hyperparameters from sweep
        config = wandb.config

        # Set up model and training
        model = create_model(
            depth=config.model_depth,
            dropout=config.dropout
        )

        optimizer = create_optimizer(
            model,
            config.optimizer,
            config.learning_rate
        )

        # Training loop
        best_accuracy = 0
        for epoch in range(config.epochs):
            # Training step
            train_loss = train_epoch(model, optimizer, config.batch_size)
            val_accuracy = validate_epoch(model)

            # Log metrics
            wandb.log({
                "epoch": epoch,
                "train_loss": train_loss,
                "val_accuracy": val_accuracy,
                "learning_rate": config.learning_rate
            })

            # Update best accuracy
            if val_accuracy > best_accuracy:
                best_accuracy = val_accuracy

                # Save best model
                torch.save(model.state_dict(), "best_model.pth")
                wandb.save("best_model.pth")

        # Log final results
        wandb.log({
            "best_accuracy": best_accuracy,
            "final_train_loss": train_loss
        })

# Run sweep
if __name__ == "__main__":
    sweep_id = wandb.sweep(sweep_config, project="hyperparameter-tuning")
    wandb.agent(sweep_id, function=train_function, count=50)
```

**Advanced Sweep Strategies:**
```python
# Multi-objective optimization
multi_objective_sweep = {
    "method": "bayes",
    "metrics": [
        {"name": "accuracy", "goal": "maximize"},
        {"name": "latency", "goal": "minimize"}
    ],
    "parameters": {
        "model_size": {"min": 10, "max": 100},
        "precision": {"values": ["fp32", "fp16", "int8"]}
    }
}

# Conditional parameters
conditional_sweep = {
    "method": "random",
    "parameters": {
        "optimizer": {"values": ["adam", "sgd"]},
        "learning_rate": {
            "distribution": "uniform",
            "min": 0.0001,
            "max": 0.1
        },
        "momentum": {
            "distribution": "uniform",
            "min": 0.0,
            "max": 0.9
        }
    },
    "conditions": [
        {"optimizer": "sgd", "momentum": {"min": 0.0, "max": 0.9}},
        {"optimizer": "adam", "momentum": {"values": [None]}}
    ]
}

# Custom stopping criteria
custom_stop_sweep = {
    "method": "bayes",
    "early_terminate": {
        "type": "custom",
        "function": "my_stopping_function.py"
    }
}
```

## Model Management and Registry

### Q6: How do you manage model versions and artifacts in W&B?

**Answer:**

**Model Artifact Management:**
```python
# Create and log model artifact
def log_model_artifact(model, config, metrics, name="my-model"):
    artifact = wandb.Artifact(
        name=name,
        type="model",
        description=f"Model trained with config: {config}",
        metadata={
            **config,
            **metrics,
            "created_at": str(datetime.now()),
            "framework": "pytorch",
            "dataset": "my_dataset_v1"
        }
    )

    # Save model
    model_path = f"{name}.pth"
    torch.save(model.state_dict(), model_path)

    # Add files
    artifact.add_file(model_path)
    artifact.add_file("config.yaml")
    artifact.add_file("requirements.txt")

    # Add training artifacts
    artifact.add_file("best_checkpoint.pth", name="checkpoints/best.pth")

    # Log artifact
    wandb.log_artifact(artifact)

    return artifact

# Usage
with wandb.init(project="model-registry") as run:
    model = train_model()
    metrics = evaluate_model(model)

    artifact = log_model_artifact(
        model=model,
        config=wandb.config,
        metrics=metrics,
        name="production-model-v1"
    )
```

**Using Model Artifacts:**
```python
# Load model from artifact
def load_model_from_artifact(artifact_name, version="latest"):
    with wandb.init(project="model-deployment") as run:
        # Get artifact
        artifact = run.use_artifact(f"{artifact_name}:{version}")

        # Download artifact
        artifact_dir = artifact.download()

        # Load model
        model_path = f"{artifact_dir}/{artifact_name}.pth"
        model = MyModel()
        model.load_state_dict(torch.load(model_path))

        # Load config
        config_path = f"{artifact_dir}/config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)

        return model, config

# Usage
model, config = load_model_from_artifact("production-model-v1", "v5")
```

**Model Registry and Lifecycle:**
```python
# Create model registry entry
def register_model(model_artifact, evaluation_results):
    """Register a model in the registry with evaluation results"""

    with wandb.init(project="model-registry") as run:
        # Create model card
        model_card = {
            "model_details": {
                "name": model_artifact.name,
                "version": model_artifact.version,
                "description": "Production-ready model for task",
                "authors": ["ML Team"],
                "license": "company-license"
            },
            "intended_use": {
                "primary_uses": ["inference", "batch_prediction"],
                "out_of_scope": ["training", "fine_tuning"]
            },
            "metrics": evaluation_results,
            "ethical_considerations": {
                "bias_analysis": "Performed bias audit",
                "fairness_metrics": "Included in evaluation"
            }
        }

        # Log model card as artifact
        card_artifact = wandb.Artifact("model-card", type="model-card")
        with card_artifact.new_file("model_card.json") as f:
            json.dump(model_card, f, indent=2)

        run.log_artifact(card_artifact)

        # Link model and card
        run.link_artifact(model_artifact, "model")
        run.link_artifact(card_artifact, "card")

# Promote model through stages
def promote_model(model_name, current_version, target_stage):
    """Promote model to different stages (development -> staging -> production)"""

    client = wandb.Api()

    # Get model versions
    model_versions = client.artifact_versions("model", f"{model_name}")

    # Find target version
    target_version = None
    for version in model_versions:
        if version.version == current_version:
            target_version = version
            break

    if not target_version:
        raise ValueError(f"Version {current_version} not found")

    # Update stage (using aliases)
    if target_stage == "staging":
        target_version.aliases.append("staging")
    elif target_stage == "production":
        target_version.aliases.append("production")
        # Remove from previous stages
        target_version.aliases = [a for a in target_version.aliases if a != "staging"]

    target_version.save()

    # Log promotion event
    with wandb.init(project="model-lifecycle") as run:
        wandb.log({
            "event": "model_promotion",
            "model_name": model_name,
            "version": current_version,
            "target_stage": target_stage,
            "timestamp": str(datetime.now())
        })
```

## Team Collaboration and Reports

### Q7: How do you create and share reports in W&B?

**Answer:**

**Creating Interactive Reports:**
```python
# Create report programmatically
import wandb

# Initialize report run
with wandb.init(project="reports", name="weekly-model-comparison") as run:

    # Add markdown content
    run.log({
        "executive_summary": wandb.Html("""
        <h1>Weekly Model Performance Report</h1>
        <p>This report compares the performance of our latest model candidates.</p>
        """)
    })

    # Add experiment comparison table
    api = wandb.Api()
    runs = api.runs("my-team/my-project",
                   filters={"created_at": {"$gte": "last_week"}})

    comparison_data = []
    for run in runs:
        comparison_data.append([
            run.name,
            run.config.get("learning_rate", "N/A"),
            run.summary.get("final_accuracy", "N/A"),
            run.summary.get("training_time", "N/A")
        ])

    comparison_table = wandb.Table(
        columns=["Run Name", "Learning Rate", "Final Accuracy", "Training Time"],
        data=comparison_data
    )

    run.log({"model_comparison": comparison_table})

    # Add visualizations
    run.log({
        "accuracy_trend": wandb.plot.line_series(
            xs=[list(range(len(runs)))],
            ys=[[run.summary.get("final_accuracy", 0) for run in runs]],
            keys=["accuracy"],
            title="Model Accuracy Trends",
            xname="Run Index"
        )
    })
```

**Sharing and Collaboration:**
```python
# Share report with team
def share_report(report_run, team_members, message):
    """Share report with team members"""

    # Create shareable link
    report_url = f"https://wandb.ai/{report_run.entity}/{report_run.project}/runs/{report_run.id}"

    # Log sharing event
    with wandb.init(project="report-sharing") as share_run:
        wandb.log({
            "shared_report": report_run.name,
            "shared_with": team_members,
            "share_message": message,
            "report_url": report_url,
            "shared_at": str(datetime.now())
        })

    # Send notifications (integrate with Slack/email)
    send_notification(team_members, message, report_url)

# Create template reports
def create_template_report(template_name, project_name):
    """Create report from template"""

    templates = {
        "model_comparison": {
            "title": "Model Comparison Report",
            "sections": ["executive_summary", "performance_metrics", "recommendations"]
        },
        "experiment_analysis": {
            "title": "Experiment Analysis Report",
            "sections": ["hypothesis", "methodology", "results", "conclusions"]
        }
    }

    template = templates.get(template_name)
    if not template:
        raise ValueError(f"Template {template_name} not found")

    with wandb.init(project="report-templates", name=f"{template_name}_report") as run:
        # Create sections
        for section in template["sections"]:
            run.log({
                section: wandb.Html(f"<h2>{section.replace('_', ' ').title()}</h2><p>Content here...</p>")
            })

        run.log({"template_name": template_name, "project": project_name})

    return run
```

## Production Deployment and Monitoring

### Q8: How do you deploy and monitor models in production using W&B?

**Answer:**

**Model Deployment Integration:**
```python
# Deploy model with W&B tracking
def deploy_model_to_production(model_artifact_name, deployment_config):
    """Deploy model to production with monitoring"""

    with wandb.init(project="model-deployment", name="production-deployment") as run:
        # Load model from registry
        artifact = run.use_artifact(f"{model_artifact_name}:production")
        model_path = artifact.download()

        # Load model
        model = load_model(model_path)

        # Deploy to serving infrastructure
        deployment_id = deploy_to_serving_infrastructure(
            model=model,
            config=deployment_config
        )

        # Log deployment details
        wandb.log({
            "deployment_id": deployment_id,
            "model_version": artifact.version,
            "deployment_config": deployment_config,
            "deployment_timestamp": str(datetime.now())
        })

        # Set up monitoring
        setup_model_monitoring(deployment_id, model_artifact_name)

        return deployment_id

# Monitor model performance
def setup_model_monitoring(deployment_id, model_name):
    """Set up monitoring for deployed model"""

    with wandb.init(project="model-monitoring", name=f"monitor_{deployment_id}") as run:

        # Define monitoring metrics
        monitoring_config = {
            "metrics": ["accuracy", "latency", "throughput"],
            "alerts": {
                "accuracy_drop": {"threshold": 0.05, "operator": "lt"},
                "latency_increase": {"threshold": 1.5, "operator": "gt"}
            },
            "reference_dataset": "production_reference_data:v1"
        }

        # Log monitoring setup
        wandb.log({
            "deployment_id": deployment_id,
            "model_name": model_name,
            "monitoring_config": monitoring_config,
            "monitoring_start_time": str(datetime.now())
        })
```

**Production Monitoring:**
```python
# Log production predictions
class ProductionLogger:
    def __init__(self, deployment_id, model_name):
        self.deployment_id = deployment_id
        self.model_name = model_name
        self.run = wandb.init(
            project="production-monitoring",
            name=f"prod_{deployment_id}",
            tags=["production", "monitoring"]
        )

    def log_prediction(self, input_data, prediction, latency, metadata=None):
        """Log individual prediction"""

        log_data = {
            "deployment_id": self.deployment_id,
            "model_name": self.model_name,
            "prediction": prediction,
            "latency_ms": latency,
            "timestamp": str(datetime.now())
        }

        if metadata:
            log_data.update(metadata)

        # Batch logging for performance
        if not hasattr(self, 'batch_data'):
            self.batch_data = []

        self.batch_data.append(log_data)

        # Log batch every 100 predictions
        if len(self.batch_data) >= 100:
            self._log_batch()

    def _log_batch(self):
        """Log batch of predictions"""
        if self.batch_data:
            # Calculate batch statistics
            latencies = [d["latency_ms"] for d in self.batch_data]
            batch_stats = {
                "batch_size": len(self.batch_data),
                "avg_latency": sum(latencies) / len(latencies),
                "max_latency": max(latencies),
                "min_latency": min(latencies),
                "predictions_count": len(self.batch_data)
            }

            wandb.log(batch_stats)

            # Log sample predictions
            if len(self.batch_data) > 10:
                sample_predictions = self.batch_data[:10]
                wandb.log({
                    "sample_predictions": wandb.Table(
                        columns=list(sample_predictions[0].keys()),
                        data=[list(d.values()) for d in sample_predictions]
                    )
                })

            self.batch_data = []

    def log_performance_metrics(self, accuracy, drift_score):
        """Log periodic performance metrics"""
        wandb.log({
            "accuracy": accuracy,
            "drift_score": drift_score,
            "performance_check_timestamp": str(datetime.now())
        })

        # Alert on performance degradation
        if accuracy < 0.8:  # Threshold
            wandb.alert(
                title="Model Performance Degradation",
                text=f"Accuracy dropped to {accuracy:.3f} for deployment {self.deployment_id}",
                level=wandb.AlertLevel.WARN
            )

# Usage in serving code
logger = ProductionLogger("deployment_123", "my_model")

@app.route('/predict', methods=['POST'])
def predict():
    start_time = time.time()

    # Get prediction
    data = request.get_json()
    prediction = model.predict(data)

    latency = (time.time() - start_time) * 1000  # ms

    # Log prediction
    logger.log_prediction(data, prediction, latency)

    return jsonify({"prediction": prediction})
```

## Best Practices and Troubleshooting

### Q9: What are the best practices for using W&B in team environments?

**Answer:**

**Project Organization:**
```python
# Use consistent naming conventions
project_naming = {
    "development": "dev-{team}-{project}",
    "staging": "staging-{team}-{project}",
    "production": "prod-{team}-{project}"
}

# Example: dev-ml-team-customer-churn

# Use hierarchical grouping
with wandb.init(
    project="ml-pipelines",
    group="data-preprocessing",  # High-level grouping
    job_type="feature-engineering",  # Specific job type
    name="categorical-encoding-v2"  # Descriptive name
) as run:
    pass
```

**Access Control and Security:**
```python
# Set up team workspaces
wandb.init(
    entity="my-company-ml-team",  # Team entity
    project="confidential-project",
    settings=wandb.Settings(
        # Private project
        _private=True
    )
)

# Use service accounts for CI/CD
# Set WANDB_API_KEY in CI environment
# Never commit API keys to code

# Configure data privacy
wandb.init(
    settings=wandb.Settings(
        # Don't save code snapshots
        _save_code=False,
        # Disable system monitoring
        _disable_stats=True
    )
)
```

**Performance Optimization:**
```python
# Optimize logging for large experiments
wandb.init(
    settings=wandb.Settings(
        # Async logging
        _sync=False,
        # Batch uploads
        _sync_period=60,  # Sync every minute
        # Compress artifacts
        _artifact_compress=True
    )
)

# Selective logging
def smart_logging(epoch, logs, log_frequency=10):
    """Log selectively to reduce overhead"""

    # Always log loss
    wandb.log({"loss": logs["loss"]})

    # Log detailed metrics periodically
    if epoch % log_frequency == 0:
        wandb.log({
            "accuracy": logs["accuracy"],
            "validation_loss": logs["val_loss"],
            "learning_rate": logs["lr"]
        })

        # Log histograms less frequently
        if epoch % (log_frequency * 5) == 0:
            wandb.log({
                "weights_histogram": wandb.Histogram(model.weights),
                "gradients_histogram": wandb.Histogram(model.gradients)
            })
```

**CI/CD Integration Best Practices:**
```yaml
# .github/workflows/ml-pipeline.yml
name: ML Pipeline
on: [push, pull_request]

env:
  WANDB_PROJECT: ${{ github.event.repository.name }}
  WANDB_ENTITY: ${{ secrets.WANDB_ENTITY }}

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'

    - name: Login to W&B
      run: pip install wandb && wandb login ${{ secrets.WANDB_API_KEY }}

    - name: Install dependencies
      run: pip install -r requirements.txt

    - name: Run training
      run: python train.py

    - name: Run evaluation
      run: python evaluate.py

    - name: Register model
      if: github.ref == 'refs/heads/main'
      run: python register_model.py
```

### Q10: How do you troubleshoot common W&B issues?

**Answer:**

**Connection and Authentication Issues:**
```python
# Check API key
import wandb
print("API Key set:", wandb.api.api_key is not None)

# Test connection
try:
    wandb.init(project="test-connection", mode="offline")
    print("Connection successful")
except Exception as e:
    print(f"Connection failed: {e}")

# Check proxy settings
import os
print("HTTP_PROXY:", os.getenv("HTTP_PROXY"))
print("HTTPS_PROXY:", os.getenv("HTTPS_PROXY"))

# Test with verbose logging
wandb.init(settings=wandb.Settings(_debug=True))
```

**Artifact Upload Issues:**
```python
# Check artifact size limits
import os
artifact_size = sum(os.path.getsize(f) for f in artifact_files if os.path.isfile(f))
print(f"Artifact size: {artifact_size / (1024**3):.2f} GB")

# Use chunked upload for large files
wandb.init(settings=wandb.Settings(
    _artifact_upload_chunk_size=100*1024*1024  # 100MB chunks
))

# Check storage quota
api = wandb.Api()
user = api.user
print(f"Storage used: {user.storage_used_bytes / (1024**3):.2f} GB")
print(f"Storage limit: {user.storage_limit_bytes / (1024**3):.2f} GB")
```

**Performance Issues:**
```python
# Profile logging performance
import time
import cProfile

def profile_logging():
    start_time = time.time()

    with wandb.init(project="performance-test") as run:
        for i in range(1000):
            wandb.log({"metric": i})

    end_time = time.time()
    print(f"Logging time: {end_time - start_time:.2f} seconds")

# cProfile.run('profile_logging()', 'profile_output.prof')

# Optimize with batch logging
def batch_log_metrics(metrics_list, batch_size=100):
    """Log metrics in batches to improve performance"""
    for i in range(0, len(metrics_list), batch_size):
        batch = metrics_list[i:i + batch_size]
        wandb.log({f"batch_{i//batch_size}": batch})
```

**Run Recovery and Debugging:**
```python
# Resume interrupted runs
def resume_run(run_id):
    """Resume a run that was interrupted"""

    # Get existing run
    api = wandb.Api()
    run = api.run(f"my-entity/my-project/{run_id}")

    # Initialize with same config
    wandb.init(
        project="my-project",
        id=run_id,  # Resume existing run
        resume="must"  # Fail if run doesn't exist
    )

    # Continue from last logged step
    last_step = run.lastHistoryStep or 0
    for step in range(last_step + 1, total_steps):
        # Continue training/logging
        pass

# Debug run state
def debug_run(run_id):
    """Debug run state and logs"""

    api = wandb.Api()
    run = api.run(run_id)

    print(f"Run status: {run.state}")
    print(f"Run config: {run.config}")
    print(f"Run summary: {run.summary}")

    # Check for errors in logs
    try:
        logs = run.logs()
        for line in logs:
            if "error" in line.lower() or "exception" in line.lower():
                print(f"Error found: {line}")
    except Exception as e:
        print(f"Could not retrieve logs: {e}")

    # Check system metrics
    system_metrics = run.systemMetrics
    if system_metrics:
        print("System metrics available")
    else:
        print("No system metrics found")
```

These interview questions cover the comprehensive capabilities of Weights & Biases, from basic experiment tracking to advanced team collaboration and production deployment. Understanding these concepts demonstrates expertise in modern MLOps practices and the ability to implement robust ML workflows at scale.
