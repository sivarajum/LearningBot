# Weights & Biases (W&B): Experiment Tracking and Model Management

## Core Features and Architecture

### What is Weights & Biases?

Weights & Biases (W&B) is a machine learning platform that provides experiment tracking, model versioning, and collaboration tools for ML teams. It helps data scientists and ML engineers track experiments, visualize results, and manage models throughout the ML lifecycle.

### Core Components

#### Experiment Tracking
Comprehensive logging and visualization of ML experiments:

**Key Features:**
- **Automatic logging**: Capture metrics, hyperparameters, and system resources
- **Interactive dashboards**: Real-time visualization of training progress
- **Experiment comparison**: Side-by-side analysis of multiple runs
- **Hyperparameter optimization**: Integration with sweep agents
- **Artifact versioning**: Track datasets, models, and other experiment outputs

#### Model Management
Version control and lifecycle management for ML models:

**Key Features:**
- **Model registry**: Centralized repository for model versions
- **Model cards**: Documentation and metadata for each model
- **Lineage tracking**: Trace models back to their training data and code
- **Access control**: Permissions and sharing controls
- **Deployment tracking**: Monitor model performance in production

#### Collaboration Tools
Team features for ML development and deployment:

**Key Features:**
- **Team workspaces**: Shared dashboards and experiment views
- **Reports**: Interactive documents combining experiments and insights
- **Comments and reviews**: Collaboration on experiments and models
- **Integrations**: Connect with popular ML frameworks and platforms
- **Automation**: CI/CD integration and automated workflows

### Architecture Overview

#### W&B Platform Architecture
```python
# W&B system components
wandb/
├── sdk/                    # Python SDK
├── server/                # Backend services
├── frontend/              # Web interface
├── database/              # Metadata storage
└── artifact_store/        # File storage
```

#### Integration Points
W&B integrates with major ML frameworks and platforms:

**Framework Integrations:**
- **PyTorch**: `wandb.init()` and automatic logging
- **TensorFlow/Keras**: `WandbCallback` for seamless integration
- **Scikit-learn**: Pipeline logging and model tracking
- **JAX/Flax**: Custom training loop integration
- **Hugging Face**: Transformer model tracking

**Platform Integrations:**
- **Google Colab**: Direct notebook integration
- **Kaggle**: Competition and dataset tracking
- **SageMaker**: AWS ML pipeline integration
- **Vertex AI**: Google Cloud ML integration

## Experiment Tracking

### Basic Experiment Logging

#### Initializing W&B
```python
import wandb

# Initialize W&B run
wandb.init(
    project="my-ml-project",
    name="experiment-1",
    config={
        "learning_rate": 0.01,
        "batch_size": 32,
        "epochs": 100,
        "model_architecture": "resnet50"
    }
)
```

#### Logging Metrics and Parameters
```python
# Log hyperparameters (automatically captured from config)
wandb.config.update({
    "optimizer": "adam",
    "loss_function": "cross_entropy"
})

# Log metrics during training
for epoch in range(num_epochs):
    train_loss = train_epoch()
    val_accuracy = validate_epoch()
    
    # Log scalar metrics
    wandb.log({
        "epoch": epoch,
        "train_loss": train_loss,
        "val_accuracy": val_accuracy,
        "learning_rate": get_current_lr()
    })

# Log final metrics
wandb.log({
    "final_train_accuracy": final_train_acc,
    "final_val_accuracy": final_val_acc,
    "best_epoch": best_epoch
})
```

#### Logging Rich Media
```python
import matplotlib.pyplot as plt
import numpy as np

# Log plots
def log_training_curves(train_losses, val_losses):
    plt.figure(figsize=(10, 6))
    plt.plot(train_losses, label='Training Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Training Curves')
    
    # Log plot to W&B
    wandb.log({"training_curves": plt})
    plt.close()

# Log images
def log_predictions(images, predictions, labels, num_samples=10):
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    axes = axes.flatten()
    
    for i in range(num_samples):
        axes[i].imshow(images[i].permute(1, 2, 0))
        pred_class = predictions[i].argmax().item()
        true_class = labels[i].item()
        color = 'green' if pred_class == true_class else 'red'
        axes[i].set_title(f'Pred: {pred_class}\nTrue: {true_class}', color=color)
        axes[i].axis('off')
    
    wandb.log({"predictions_sample": fig})
    plt.close()

# Log histograms
wandb.log({
    "weights_dist": wandb.Histogram(model.conv1.weight.data.numpy()),
    "gradients_dist": wandb.Histogram(model.conv1.weight.grad.numpy())
})
```

### Advanced Logging Features

#### Custom Metrics and Plots
```python
# Log confusion matrix
from sklearn.metrics import confusion_matrix
import seaborn as sns

def log_confusion_matrix(y_true, y_pred, class_names):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    
    wandb.log({"confusion_matrix": plt})
    plt.close()

# Log PR curves and ROC curves
from sklearn.metrics import precision_recall_curve, roc_curve, auc

def log_classification_metrics(y_true, y_pred_proba):
    # PR Curve
    precision, recall, _ = precision_recall_curve(y_true, y_pred_proba)
    pr_auc = auc(recall, precision)
    
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(recall, precision, label=f'PR AUC = {pr_auc:.3f}')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend()
    
    # ROC Curve
    fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
    roc_auc = auc(fpr, tpr)
    
    plt.subplot(1, 2, 2)
    plt.plot(fpr, tpr, label=f'ROC AUC = {roc_auc:.3f}')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    
    wandb.log({"pr_roc_curves": plt})
    plt.close()
```

#### System Resource Monitoring
```python
# Enable system monitoring
wandb.init(settings=wandb.Settings(start_method="fork"))

# W&B automatically logs:
# - CPU usage
# - Memory usage
# - GPU usage (if available)
# - Network I/O
# - Disk I/O

# Custom system metrics
import psutil
import GPUtil

def log_system_metrics():
    # CPU and memory
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    # GPU metrics (if available)
    gpu_metrics = {}
    try:
        gpus = GPUtil.getGPUs()
        for i, gpu in enumerate(gpus):
            gpu_metrics[f'gpu_{i}_util'] = gpu.load * 100
            gpu_metrics[f'gpu_{i}_memory'] = gpu.memoryUsed
    except:
        pass
    
    wandb.log({
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "memory_used_gb": memory.used / (1024**3),
        **gpu_metrics
    })
```

## Hyperparameter Optimization

### W&B Sweeps
Automated hyperparameter tuning with Bayesian optimization:

#### Sweep Configuration
```yaml
# sweep.yaml
program: train.py
method: bayes
metric:
  name: val_accuracy
  goal: maximize
parameters:
  learning_rate:
    min: 0.0001
    max: 0.1
  batch_size:
    values: [16, 32, 64, 128]
  model_depth:
    values: [18, 34, 50, 101]
  optimizer:
    values: ["adam", "sgd", "rmsprop"]
```

#### Running Sweeps
```python
# Initialize sweep
sweep_id = wandb.sweep(sweep_config, project="my-sweep-project")

# Define training function
def train():
    with wandb.init() as run:
        # Get hyperparameters from sweep
        config = wandb.config
        
        # Set up model with sweep parameters
        model = create_model(
            depth=config.model_depth,
            learning_rate=config.learning_rate
        )
        
        # Training loop
        for epoch in range(config.epochs):
            # Training code
            loss, accuracy = train_epoch(model, config)
            
            wandb.log({
                "epoch": epoch,
                "loss": loss,
                "accuracy": accuracy
            })

# Run sweep agent
wandb.agent(sweep_id, function=train, count=50)
```

#### Advanced Sweep Strategies
```python
# Grid search sweep
grid_sweep = {
    "method": "grid",
    "parameters": {
        "learning_rate": {"values": [0.01, 0.001, 0.0001]},
        "batch_size": {"values": [32, 64]},
        "optimizer": {"values": ["adam", "sgd"]}
    }
}

# Random search sweep
random_sweep = {
    "method": "random",
    "parameters": {
        "learning_rate": {"distribution": "uniform", "min": 0.0001, "max": 0.1},
        "dropout": {"distribution": "uniform", "min": 0.1, "max": 0.5},
        "batch_size": {"values": [16, 32, 64, 128, 256]}
    }
}

# Bayesian optimization with early stopping
bayes_sweep = {
    "method": "bayes",
    "early_terminate": {
        "type": "hyperband",
        "min_iter": 3
    },
    "parameters": {
        "learning_rate": {"min": 0.0001, "max": 0.1},
        "model_size": {"min": 100, "max": 1000}
    }
}
```

## Model Management and Registry

### Model Versioning
```python
# Log model artifact
with wandb.init(project="model-registry") as run:
    # Train model
    model = train_model()
    
    # Create model artifact
    artifact = wandb.Artifact(
        name="my-model",
        type="model",
        description="Trained ResNet model for image classification",
        metadata={
            "architecture": "ResNet50",
            "dataset": "ImageNet",
            "epochs": 100,
            "final_accuracy": 0.95
        }
    )
    
    # Add model file
    model_path = "model.pth"
    torch.save(model.state_dict(), model_path)
    artifact.add_file(model_path)
    
    # Add additional files
    artifact.add_file("config.yaml")
    artifact.add_file("requirements.txt")
    
    # Log artifact
    run.log_artifact(artifact)

# Use model from registry
def load_model_from_registry(model_name, version="latest"):
    with wandb.init() as run:
        # Get artifact
        artifact = run.use_artifact(f"{model_name}:{version}")
        
        # Download model
        artifact_dir = artifact.download()
        model_path = f"{artifact_dir}/model.pth"
        
        # Load model
        model = create_model()
        model.load_state_dict(torch.load(model_path))
        
        return model
```

### Model Cards and Documentation
```python
# Create comprehensive model card
model_card = {
    "model_details": {
        "name": "Customer Churn Predictor",
        "version": "1.0.0",
        "description": "Neural network model for predicting customer churn",
        "authors": ["ML Team"],
        "license": "MIT",
        "model_type": "classification"
    },
    "intended_use": {
        "primary_uses": ["Customer retention analysis"],
        "out_of_scope": ["Real-time prediction without monitoring"]
    },
    "factors": {
        "relevant_factors": ["Customer demographics", "Usage patterns", "Billing history"],
        "evaluation_factors": ["Data quality", "Feature engineering"]
    },
    "metrics": {
        "performance_metrics": {
            "accuracy": 0.92,
            "precision": 0.89,
            "recall": 0.85,
            "f1_score": 0.87
        },
        "decision_threshold": 0.5,
        "uncertainty_measures": ["Prediction confidence intervals"]
    },
    "data": {
        "datasets": ["customer_data_v3"],
        "preprocessing": ["Standardization", "One-hot encoding"],
        "data_splits": {"train": 0.7, "validation": 0.2, "test": 0.1}
    },
    "quantitative_analysis": {
        "unitary_results": "Model performance across different customer segments",
        "intersectional_results": "Performance analysis by demographic groups"
    },
    "ethical_considerations": {
        "data_bias": "Potential bias in historical customer data",
        "mitigations": ["Bias detection algorithms", "Regular model audits"]
    }
}

# Log model card as artifact
card_artifact = wandb.Artifact("model-card", type="model-card")
with card_artifact.new_file("model_card.json") as f:
    json.dump(model_card, f, indent=2)

run.log_artifact(card_artifact)
```

## Collaboration and Team Features

### Team Workspaces
```python
# Set up team project
wandb.init(
    entity="my-team",  # Team name
    project="shared-ml-project",
    group="experiment-group-1"  # Group related runs
)

# Use team templates
from wandb import AlertLevel

# Set up alerts for team monitoring
wandb.alert(
    title="Model Performance Degradation",
    text="Validation accuracy dropped below 90%",
    level=AlertLevel.WARN
)
```

### Reports and Interactive Documents
```python
# Create interactive report
with wandb.init(project="reports") as run:
    # Log experiments table
    experiments_table = wandb.Table(
        columns=["experiment_name", "accuracy", "loss", "run_time"],
        data=[
            ["exp_1", 0.92, 0.15, "2h 30m"],
            ["exp_2", 0.89, 0.18, "3h 15m"],
            ["exp_3", 0.95, 0.12, "4h 45m"]
        ]
    )
    
    run.log({"experiments_comparison": experiments_table})
    
    # Create markdown panels
    run.log({
        "conclusions": wandb.Html("""
        <h2>Experiment Conclusions</h2>
        <ul>
            <li>Experiment 3 achieved the best performance</li>
            <li>Training time increased with model complexity</li>
            <li>Data augmentation improved generalization</li>
        </ul>
        """)
    })
```

### Access Control and Sharing
```python
# Private team projects
wandb.init(
    entity="my-team",
    project="confidential-project",
    # Project is private to team members
)

# Share specific runs
run = wandb.init(project="public-demo")
# Run is publicly viewable
run.link_to_publication("https://arxiv.org/abs/1234.5678")

# Create shareable reports
report = wandb.Api().create_report(
    project="my-project",
    title="Model Performance Analysis",
    description="Comprehensive analysis of recent experiments"
)

# Share report link
print(f"Share this report: {report.url}")
```

## Integrations and Automation

### Framework-Specific Integrations

#### PyTorch Lightning Integration
```python
import pytorch_lightning as pl
from pytorch_lightning.loggers import WandbLogger

class LitModel(pl.LightningModule):
    def __init__(self):
        super().__init__()
        self.layer = torch.nn.Linear(28 * 28, 10)
    
    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self.layer(x.view(x.size(0), -1))
        loss = F.cross_entropy(y_hat, y)
        
        # Log metrics (automatically handled by WandbLogger)
        self.log("train_loss", loss)
        return loss

# Set up W&B logger
wandb_logger = WandbLogger(
    project="pytorch-lightning",
    name="my-experiment",
    log_model=True  # Log model checkpoints
)

# Train with automatic logging
trainer = pl.Trainer(logger=wandb_logger)
trainer.fit(model, train_loader, val_loader)
```

#### Hugging Face Transformers Integration
```python
from transformers import Trainer, TrainingArguments
import wandb

# Initialize W&B
wandb.init(project="huggingface-transformers")

# Set up training arguments with W&B integration
training_args = TrainingArguments(
    output_dir="./results",
    logging_steps=100,
    evaluation_strategy="steps",
    save_steps=500,
    report_to="wandb",  # Enable W&B logging
    run_name="bert-finetuning"
)

# Create trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

# Train (automatically logs to W&B)
trainer.train()

# Log model to W&B
trainer.save_model()
wandb.save("pytorch_model.bin")
```

### CI/CD Integration

#### GitHub Actions Workflow
```yaml
# .github/workflows/ml-training.yml
name: ML Training Pipeline
on: [push, pull_request]

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Login to W&B
      run: wandb login ${{ secrets.WANDB_API_KEY }}
    
    - name: Run training
      run: python train.py
    
    - name: Upload model artifacts
      if: github.ref == 'refs/heads/main'
      run: |
        python -c "
        import wandb
        run = wandb.init(project='production-models')
        artifact = wandb.Artifact('model', type='model')
        artifact.add_file('model.pkl')
        run.log_artifact(artifact)
        "
```

#### Automated Model Validation
```python
def validate_and_promote_model(model_artifact_name, validation_threshold=0.9):
    """Automated model validation and promotion"""
    
    with wandb.init(project="model-validation") as run:
        # Load latest model
        artifact = run.use_artifact(f"{model_artifact_name}:latest")
        model_path = artifact.download()
        
        # Load model
        model = load_model(model_path)
        
        # Run validation
        val_metrics = validate_model(model)
        run.log(val_metrics)
        
        # Check against threshold
        if val_metrics['accuracy'] >= validation_threshold:
            # Promote to production
            prod_artifact = wandb.Artifact(
                "production-model",
                type="model",
                description=f"Promoted model with accuracy {val_metrics['accuracy']:.3f}"
            )
            prod_artifact.add_file(f"{model_path}/model.pkl")
            run.log_artifact(prod_artifact)
            
            # Send notification
            wandb.alert(
                title="Model Promoted to Production",
                text=f"Model {model_artifact_name} passed validation with accuracy {val_metrics['accuracy']:.3f}",
                level=wandb.AlertLevel.INFO
            )
            
            return True
        else:
            # Mark as rejected
            wandb.alert(
                title="Model Validation Failed",
                text=f"Model {model_artifact_name} failed validation with accuracy {val_metrics['accuracy']:.3f}",
                level=wandb.AlertLevel.WARN
            )
            
            return False
```

## Advanced Features and Best Practices

### Custom Callbacks and Hooks
```python
class WandbCallback:
    def __init__(self):
        self.run = None
    
    def on_train_begin(self, logs=None):
        self.run = wandb.init(project="custom-training")
    
    def on_epoch_end(self, epoch, logs=None):
        wandb.log({
            "epoch": epoch,
            **logs
        })
    
    def on_train_end(self, logs=None):
        # Log final model
        artifact = wandb.Artifact("final-model", type="model")
        artifact.add_file("model.h5")
        self.run.log_artifact(artifact)
        
        wandb.finish()

# Usage with custom training loop
callback = WandbCallback()
callback.on_train_begin()

for epoch in range(num_epochs):
    # Training logic
    logs = train_epoch()
    callback.on_epoch_end(epoch, logs)

callback.on_train_end()
```

### Distributed Training Logging
```python
# Multi-GPU training logging
import torch.distributed as dist

def setup_distributed_logging(rank, world_size):
    """Set up logging for distributed training"""
    
    # Initialize W&B only on rank 0
    if rank == 0:
        wandb.init(
            project="distributed-training",
            config={
                "world_size": world_size,
                "batch_size": 32 * world_size  # Effective batch size
            }
        )
    
    # Log from all ranks (W&B handles aggregation)
    def log_metrics(metrics, step):
        if rank == 0:
            # Aggregate metrics across ranks if needed
            aggregated_metrics = aggregate_metrics_across_ranks(metrics)
            wandb.log(aggregated_metrics, step=step)
    
    return log_metrics

# Usage
rank = dist.get_rank()
world_size = dist.get_world_size()
log_fn = setup_distributed_logging(rank, world_size)

for step in range(num_steps):
    # Training step
    loss = train_step()
    
    # Log every 100 steps
    if step % 100 == 0:
        log_fn({"loss": loss, "step": step}, step)
```

### Performance Optimization
```python
# Optimize W&B logging for performance
wandb.init(
    project="optimized-training",
    settings=wandb.Settings(
        # Reduce network overhead
        _sync=False,  # Async logging
        _save_requirements=False,  # Don't save requirements
    )
)

# Batch logging for better performance
log_buffer = []
log_batch_size = 10

def buffered_log(metrics):
    log_buffer.append(metrics)
    
    if len(log_buffer) >= log_batch_size:
        # Log all buffered metrics at once
        for i, buffered_metrics in enumerate(log_buffer):
            wandb.log(buffered_metrics, step=current_step - len(log_buffer) + i + 1)
        log_buffer.clear()

# Selective logging for long training runs
def selective_logging(epoch, logs):
    # Always log loss
    wandb.log({"loss": logs["loss"]})
    
    # Log detailed metrics every 10 epochs
    if epoch % 10 == 0:
        wandb.log({
            "accuracy": logs["accuracy"],
            "validation_loss": logs["val_loss"],
            "learning_rate": logs["lr"]
        })
    
    # Log histograms every 50 epochs
    if epoch % 50 == 0:
        wandb.log({
            "weights_histogram": wandb.Histogram(model.weights),
            "gradients_histogram": wandb.Histogram(model.gradients)
        })
```

### Security and Compliance
```python
# Secure W&B configuration
import os

# Use environment variables for sensitive data
os.environ["WANDB_API_KEY"] = "your-secure-api-key"
os.environ["WANDB_BASE_URL"] = "https://wandb.company.com"  # Private instance

# Configure for on-premise deployment
wandb.init(
    project="secure-project",
    settings=wandb.Settings(
        # Use secure storage
        _offline=False,  # Online mode with encryption
        # Configure artifact storage
        artifact_store="s3://secure-bucket/artifacts",
    )
)

# Data privacy and compliance
def log_privacy_safe_metrics(model, test_data):
    """Log metrics without exposing sensitive data"""
    
    # Compute metrics locally
    predictions = model.predict(test_data.drop('sensitive_columns', axis=1))
    accuracy = accuracy_score(test_data['target'], predictions)
    
    # Log only aggregated metrics
    wandb.log({
        "accuracy": accuracy,
        "num_predictions": len(predictions),
        # Don't log individual predictions or sensitive features
    })
    
    # Log model metadata without sensitive information
    wandb.log({
        "model_type": "privacy_preserving_model",
        "training_data_size": len(train_data),
        "feature_count": len(feature_columns)
    })
```

Weights & Biases provides a comprehensive platform for experiment tracking, model management, and team collaboration in machine learning projects. Its extensive integrations, powerful visualization capabilities, and automation features make it an essential tool for modern ML workflows, enabling teams to build, track, and deploy models more effectively.