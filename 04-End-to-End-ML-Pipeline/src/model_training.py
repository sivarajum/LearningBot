"""
Model Training Module
Trains churn prediction model using Vertex AI
"""
import os
import logging
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)
import mlflow
import mlflow.sklearn
from google.cloud import aiplatform
from google.cloud import bigquery

logger = logging.getLogger(__name__)


class ModelTrainingPipeline:
    """Pipeline for training churn prediction model"""
    
    def __init__(
        self,
        project_id: str,
        dataset_id: str,
        table_id: str = "customer_features",
        mlflow_tracking_uri: str = "http://localhost:5000"
    ):
        """
        Initialize model training pipeline
        
        Args:
            project_id: GCP project ID
            dataset_id: BigQuery dataset ID
            table_id: Features table ID
            mlflow_tracking_uri: MLflow tracking URI
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.bq_client = bigquery.Client(project=project_id)
        
        # Initialize MLflow
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        mlflow.set_experiment("churn_prediction")
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location="us-central1")
    
    def load_data_from_bigquery(self) -> pd.DataFrame:
        """
        Load training data from BigQuery
        
        Returns:
            DataFrame with features and labels
        """
        query = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
        """
        
        df = self.bq_client.query(query).to_dataframe()
        logger.info(f"Loaded {len(df)} records from BigQuery")
        
        return df
    
    def prepare_data(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Prepare data for training
        
        Args:
            df: Input DataFrame
            test_size: Test set size
            random_state: Random seed
            
        Returns:
            X_train, X_test, y_train, y_test
        """
        # Separate features and target
        feature_cols = [
            col for col in df.columns
            if col not in ["customer_id", "is_churn"]
        ]
        
        X = df[feature_cols].fillna(0)
        y = df["is_churn"]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        logger.info(f"Training set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        logger.info(f"Churn rate - Train: {y_train.mean():.2%}, Test: {y_test.mean():.2%}")
        
        return X_train, X_test, y_train, y_test
    
    def train_model(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        n_estimators: int = 100,
        max_depth: int = 10,
        random_state: int = 42
    ) -> RandomForestClassifier:
        """
        Train Random Forest model
        
        Args:
            X_train: Training features
            y_train: Training labels
            n_estimators: Number of trees
            max_depth: Max tree depth
            random_state: Random seed
            
        Returns:
            Trained model
        """
        logger.info("Training Random Forest model...")
        
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        logger.info("Model training complete!")
        
        return model
    
    def evaluate_model(
        self,
        model: RandomForestClassifier,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ) -> Dict[str, float]:
        """
        Evaluate model performance
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Dictionary of metrics
        """
        # Predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1_score": f1_score(y_test, y_pred, zero_division=0),
            "roc_auc": roc_auc_score(y_test, y_pred_proba)
        }
        
        # Log metrics
        logger.info("Model Performance:")
        for metric, value in metrics.items():
            logger.info(f"  {metric}: {value:.4f}")
        
        # Classification report
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, y_pred))
        
        return metrics
    
    def train_and_evaluate(
        self,
        n_estimators: int = 100,
        max_depth: int = 10
    ) -> Tuple[RandomForestClassifier, Dict[str, float]]:
        """
        Complete training and evaluation pipeline
        
        Args:
            n_estimators: Number of trees
            max_depth: Max tree depth
            
        Returns:
            Trained model and metrics
        """
        # Load data
        df = self.load_data_from_bigquery()
        
        # Prepare data
        X_train, X_test, y_train, y_test = self.prepare_data(df)
        
        # Train model with MLflow tracking
        with mlflow.start_run():
            # Log parameters
            mlflow.log_param("n_estimators", n_estimators)
            mlflow.log_param("max_depth", max_depth)
            mlflow.log_param("train_size", len(X_train))
            mlflow.log_param("test_size", len(X_test))
            
            # Train model
            model = self.train_model(X_train, y_train, n_estimators, max_depth)
            
            # Evaluate model
            metrics = self.evaluate_model(model, X_test, y_test)
            
            # Log metrics
            for metric, value in metrics.items():
                mlflow.log_metric(metric, value)
            
            # Log model
            mlflow.sklearn.log_model(model, "model")
            
            # Log feature importance
            feature_importance = pd.DataFrame({
                "feature": X_train.columns,
                "importance": model.feature_importances_
            }).sort_values("importance", ascending=False)
            
            mlflow.log_text(
                feature_importance.to_string(),
                "feature_importance.txt"
            )
        
        return model, metrics
    
    def save_model(self, model: RandomForestClassifier, model_path: str):
        """
        Save model to disk
        
        Args:
            model: Trained model
            model_path: Path to save model
        """
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(model, model_path)
        logger.info(f"Model saved to {model_path}")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    import os
    
    project_id = os.getenv("GCP_PROJECT_ID", "your-project-id")
    
    # Initialize pipeline
    training = ModelTrainingPipeline(
        project_id=project_id,
        dataset_id="customer_data",
        mlflow_tracking_uri="http://localhost:5000"
    )
    
    # Train and evaluate
    model, metrics = training.train_and_evaluate(
        n_estimators=100,
        max_depth=10
    )
    
    # Save model
    training.save_model(model, "models/churn_model.pkl")
    
    logger.info("Training pipeline complete!")

