"""
Drift Detection Module
Detects data drift and model performance degradation
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset
from evidently.metrics import (
    DatasetDriftMetric,
    DataQualityMetrics,
    RegressionQualityMetrics,
    ClassificationQualityMetrics
)

logger = logging.getLogger(__name__)


class DriftDetector:
    """Detects data and model drift"""
    
    def __init__(
        self,
        reference_data: pd.DataFrame,
        target_column: str = "is_churn",
        task_type: str = "classification"
    ):
        """
        Initialize drift detector
        
        Args:
            reference_data: Reference dataset (training data)
            target_column: Target column name
            task_type: Task type ("classification" or "regression")
        """
        self.reference_data = reference_data
        self.target_column = target_column
        self.task_type = task_type
        
        # Define column mapping
        feature_columns = [col for col in reference_data.columns if col != target_column]
        self.column_mapping = ColumnMapping(
            target=target_column,
            prediction="prediction",
            numerical_features=feature_columns,
            categorical_features=[]
        )
    
    def detect_data_drift(
        self,
        current_data: pd.DataFrame,
        threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Detect data drift between reference and current data
        
        Args:
            current_data: Current dataset
            threshold: Drift threshold
            
        Returns:
            Drift detection results
        """
        logger.info("Detecting data drift...")
        
        # Create drift report
        data_drift_report = Report(metrics=[DataDriftPreset()])
        data_drift_report.run(
            reference_data=self.reference_data,
            current_data=current_data,
            column_mapping=self.column_mapping
        )
        
        # Get drift metrics
        drift_metrics = data_drift_report.as_dict()
        
        # Check for drift
        dataset_drift = drift_metrics.get("metrics", [{}])[0].get("result", {}).get("dataset_drift", False)
        drift_score = drift_metrics.get("metrics", [{}])[0].get("result", {}).get("drift_score", 0.0)
        
        drift_detected = dataset_drift or drift_score > threshold
        
        result = {
            "drift_detected": drift_detected,
            "drift_score": drift_score,
            "threshold": threshold,
            "timestamp": datetime.now().isoformat(),
            "details": drift_metrics
        }
        
        if drift_detected:
            logger.warning(f"Data drift detected! Score: {drift_score:.4f}")
        else:
            logger.info(f"No data drift detected. Score: {drift_score:.4f}")
        
        return result
    
    def detect_target_drift(
        self,
        current_data: pd.DataFrame,
        threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Detect target drift
        
        Args:
            current_data: Current dataset with target
            threshold: Drift threshold
            
        Returns:
            Target drift results
        """
        logger.info("Detecting target drift...")
        
        target_drift_report = Report(metrics=[TargetDriftPreset()])
        target_drift_report.run(
            reference_data=self.reference_data,
            current_data=current_data,
            column_mapping=self.column_mapping
        )
        
        drift_metrics = target_drift_report.as_dict()
        drift_score = drift_metrics.get("metrics", [{}])[0].get("result", {}).get("drift_score", 0.0)
        drift_detected = drift_score > threshold
        
        result = {
            "drift_detected": drift_detected,
            "drift_score": drift_score,
            "threshold": threshold,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def detect_model_performance_drift(
        self,
        current_data: pd.DataFrame,
        predictions: np.ndarray,
        threshold: float = 0.1
    ) -> Dict[str, Any]:
        """
        Detect model performance degradation
        
        Args:
            current_data: Current dataset
            predictions: Model predictions
            threshold: Performance degradation threshold
            
        Returns:
            Performance drift results
        """
        logger.info("Detecting model performance drift...")
        
        # Add predictions to current data
        current_with_preds = current_data.copy()
        current_with_preds["prediction"] = predictions
        
        # Create quality report
        if self.task_type == "classification":
            quality_report = Report(metrics=[ClassificationQualityMetrics()])
        else:
            quality_report = Report(metrics=[RegressionQualityMetrics()])
        
        quality_report.run(
            reference_data=self.reference_data,
            current_data=current_with_preds,
            column_mapping=self.column_mapping
        )
        
        quality_metrics = quality_report.as_dict()
        
        # Extract key metrics
        metrics = quality_metrics.get("metrics", [{}])[0].get("result", {})
        
        # Calculate performance degradation
        if self.task_type == "classification":
            ref_accuracy = metrics.get("reference", {}).get("accuracy", 0.0)
            curr_accuracy = metrics.get("current", {}).get("accuracy", 0.0)
            degradation = ref_accuracy - curr_accuracy
        else:
            ref_rmse = metrics.get("reference", {}).get("rmse", 0.0)
            curr_rmse = metrics.get("current", {}).get("rmse", 0.0)
            degradation = curr_rmse - ref_rmse
        
        performance_drift = abs(degradation) > threshold
        
        result = {
            "performance_drift": performance_drift,
            "degradation": degradation,
            "threshold": threshold,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        if performance_drift:
            logger.warning(f"Performance drift detected! Degradation: {degradation:.4f}")
        
        return result


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create sample data
    np.random.seed(42)
    reference_data = pd.DataFrame({
        "feature1": np.random.normal(0, 1, 1000),
        "feature2": np.random.normal(0, 1, 1000),
        "is_churn": np.random.choice([0, 1], 1000)
    })
    
    # Simulate drift in current data
    current_data = pd.DataFrame({
        "feature1": np.random.normal(0.5, 1, 100),  # Shifted mean
        "feature2": np.random.normal(0, 1, 100),
        "is_churn": np.random.choice([0, 1], 100)
    })
    
    # Initialize detector
    detector = DriftDetector(reference_data, target_column="is_churn")
    
    # Detect drift
    drift_result = detector.detect_data_drift(current_data)
    print(f"Drift detected: {drift_result['drift_detected']}")
    print(f"Drift score: {drift_result['drift_score']:.4f}")

