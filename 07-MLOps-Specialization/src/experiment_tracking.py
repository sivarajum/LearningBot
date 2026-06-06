"""
Advanced Experiment Tracking
Using MLflow and Weights & Biases
"""
import logging
import mlflow
import wandb
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ExperimentTracker:
    """Advanced experiment tracking with MLflow and W&B"""
    
    def __init__(
        self,
        experiment_name: str,
        mlflow_tracking_uri: str = "http://localhost:5000",
        use_wandb: bool = True,
        wandb_project: str = "mlops-specialization"
    ):
        """
        Initialize experiment tracker
        
        Args:
            experiment_name: Experiment name
            mlflow_tracking_uri: MLflow tracking URI
            use_wandb: Whether to use Weights & Biases
            wandb_project: W&B project name
        """
        self.experiment_name = experiment_name
        self.use_wandb = use_wandb
        
        # Initialize MLflow
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        mlflow.set_experiment(experiment_name)
        
        # Initialize W&B
        if use_wandb:
            wandb.init(project=wandb_project, name=experiment_name)
        
        self.current_run = None
    
    def start_run(self, run_name: Optional[str] = None):
        """Start a new experiment run"""
        if run_name is None:
            run_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_run = mlflow.start_run(run_name=run_name)
        logger.info(f"Started run: {run_name}")
    
    def log_params(self, params: Dict[str, Any]):
        """Log hyperparameters"""
        mlflow.log_params(params)
        if self.use_wandb:
            wandb.config.update(params)
        logger.info(f"Logged parameters: {params}")
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Log metrics"""
        mlflow.log_metrics(metrics, step=step)
        if self.use_wandb:
            wandb.log(metrics, step=step)
        logger.info(f"Logged metrics: {metrics}")
    
    def log_model(self, model, artifact_path: str = "model"):
        """Log model artifact"""
        mlflow.sklearn.log_model(model, artifact_path)
        logger.info(f"Logged model to {artifact_path}")
    
    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        """Log file artifact"""
        mlflow.log_artifact(local_path, artifact_path)
        if self.use_wandb:
            wandb.log_artifact(local_path, artifact_path)
        logger.info(f"Logged artifact: {local_path}")
    
    def end_run(self):
        """End current run"""
        if self.current_run:
            mlflow.end_run()
            if self.use_wandb:
                wandb.finish()
            logger.info("Ended run")
    
    def search_runs(self, filter_string: str = "", max_results: int = 100):
        """Search previous runs"""
        experiment = mlflow.get_experiment_by_name(self.experiment_name)
        if experiment:
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string=filter_string,
                max_results=max_results
            )
            return runs
        return None
    
    def get_best_run(self, metric: str = "accuracy", ascending: bool = False):
        """Get best run based on metric"""
        runs = self.search_runs()
        if runs is not None and len(runs) > 0:
            best_run = runs.sort_values(
                f"metrics.{metric}",
                ascending=ascending
            ).iloc[0]
            return best_run
        return None


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    tracker = ExperimentTracker(
        experiment_name="test_experiment",
        use_wandb=False  # Set to True if W&B is configured
    )
    
    tracker.start_run("test_run_1")
    tracker.log_params({"learning_rate": 0.01, "epochs": 10})
    tracker.log_metrics({"accuracy": 0.95, "loss": 0.05})
    tracker.end_run()
    
    print("Experiment tracking complete!")

