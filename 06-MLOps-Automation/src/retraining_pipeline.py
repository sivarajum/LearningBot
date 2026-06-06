"""
Automated Retraining Pipeline
Triggers model retraining based on drift detection
"""
import os
import logging
import schedule
import time
from typing import Dict, Any, Optional
from datetime import datetime
import mlflow
from drift_detection import DriftDetector
import pandas as pd

logger = logging.getLogger(__name__)


class AutomatedRetrainingPipeline:
    """Automated model retraining pipeline"""
    
    def __init__(
        self,
        drift_detector: DriftDetector,
        training_function,
        mlflow_tracking_uri: str = "http://localhost:5000",
        drift_threshold: float = 0.5,
        performance_threshold: float = 0.1,
        retrain_interval_hours: int = 24
    ):
        """
        Initialize automated retraining pipeline
        
        Args:
            drift_detector: Drift detector instance
            training_function: Function to train model
            mlflow_tracking_uri: MLflow tracking URI
            drift_threshold: Data drift threshold
            performance_threshold: Performance degradation threshold
            retrain_interval_hours: Hours between retraining checks
        """
        self.drift_detector = drift_detector
        self.training_function = training_function
        self.drift_threshold = drift_threshold
        self.performance_threshold = performance_threshold
        self.retrain_interval_hours = retrain_interval_hours
        
        # Initialize MLflow
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        mlflow.set_experiment("automated_retraining")
        
        self.last_retrain_time = None
        self.retrain_count = 0
    
    def check_and_retrain(
        self,
        current_data: pd.DataFrame,
        current_predictions: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """
        Check for drift and retrain if necessary
        
        Args:
            current_data: Current production data
            current_predictions: Current model predictions (optional)
            
        Returns:
            Retraining result
        """
        logger.info("Checking for drift and retraining triggers...")
        
        # Check data drift
        drift_result = self.drift_detector.detect_data_drift(
            current_data,
            threshold=self.drift_threshold
        )
        
        # Check performance drift if predictions available
        performance_result = None
        if current_predictions is not None:
            performance_result = self.drift_detector.detect_model_performance_drift(
                current_data,
                current_predictions.values,
                threshold=self.performance_threshold
            )
        
        # Determine if retraining is needed
        retrain_needed = (
            drift_result["drift_detected"] or
            (performance_result and performance_result["performance_drift"])
        )
        
        result = {
            "retrain_needed": retrain_needed,
            "drift_detected": drift_result["drift_detected"],
            "performance_drift": performance_result["performance_drift"] if performance_result else False,
            "timestamp": datetime.now().isoformat()
        }
        
        if retrain_needed:
            logger.warning("Retraining triggered!")
            retrain_result = self.retrain_model()
            result["retraining"] = retrain_result
        else:
            logger.info("No retraining needed")
        
        return result
    
    def retrain_model(self) -> Dict[str, Any]:
        """
        Retrain the model
        
        Returns:
            Retraining result
        """
        logger.info("Starting model retraining...")
        
        try:
            with mlflow.start_run(run_name=f"automated_retrain_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
                # Call training function
                model, metrics = self.training_function()
                
                # Log metrics
                for metric, value in metrics.items():
                    mlflow.log_metric(metric, value)
                
                # Log model
                mlflow.sklearn.log_model(model, "model")
                
                # Update tracking
                self.last_retrain_time = datetime.now()
                self.retrain_count += 1
                
                logger.info(f"Model retrained successfully. Run #{self.retrain_count}")
                
                return {
                    "success": True,
                    "retrain_count": self.retrain_count,
                    "timestamp": self.last_retrain_time.isoformat(),
                    "metrics": metrics
                }
        except Exception as e:
            logger.error(f"Retraining failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def start_scheduled_retraining(
        self,
        get_current_data_function,
        get_predictions_function=None
    ):
        """
        Start scheduled retraining checks
        
        Args:
            get_current_data_function: Function to get current production data
            get_predictions_function: Function to get current predictions (optional)
        """
        logger.info(f"Starting scheduled retraining checks (every {self.retrain_interval_hours} hours)")
        
        def check_and_retrain_job():
            """Job function for scheduled retraining"""
            try:
                current_data = get_current_data_function()
                current_predictions = None
                if get_predictions_function:
                    current_predictions = get_predictions_function()
                
                self.check_and_retrain(current_data, current_predictions)
            except Exception as e:
                logger.error(f"Scheduled retraining check failed: {e}")
        
        # Schedule job
        schedule.every(self.retrain_interval_hours).hours.do(check_and_retrain_job)
        
        # Run scheduler
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # This would be integrated with actual training function
    def dummy_training_function():
        """Dummy training function for example"""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score
        import numpy as np
        
        # Dummy data
        X = np.random.rand(100, 5)
        y = np.random.choice([0, 1], 100)
        
        model = RandomForestClassifier()
        model.fit(X, y)
        predictions = model.predict(X)
        accuracy = accuracy_score(y, predictions)
        
        return model, {"accuracy": accuracy}
    
    # Create drift detector
    reference_data = pd.DataFrame({
        "feature1": [1, 2, 3, 4, 5],
        "feature2": [2, 3, 4, 5, 6],
        "is_churn": [0, 1, 0, 1, 0]
    })
    
    detector = DriftDetector(reference_data)
    
    # Create retraining pipeline
    pipeline = AutomatedRetrainingPipeline(
        drift_detector=detector,
        training_function=dummy_training_function,
        retrain_interval_hours=24
    )
    
    # Manual retrain check
    current_data = pd.DataFrame({
        "feature1": [1.5, 2.5, 3.5],
        "feature2": [2.5, 3.5, 4.5],
        "is_churn": [0, 1, 0]
    })
    
    result = pipeline.check_and_retrain(current_data)
    print(f"Retrain needed: {result['retrain_needed']}")

