"""
Vertex AI Training Module
Trains churn prediction model using Vertex AI AutoML
"""
import os
import logging
import pandas as pd
from typing import Dict, Any
from google.cloud import aiplatform
from google.cloud import bigquery
from google.cloud.aiplatform import schema

logger = logging.getLogger(__name__)


class VertexAITrainingPipeline:
    """Pipeline for training models on Vertex AI"""
    
    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        dataset_id: str = "customer_data",
        table_id: str = "customer_features"
    ):
        """
        Initialize Vertex AI training pipeline
        
        Args:
            project_id: GCP project ID
            location: GCP region
            dataset_id: BigQuery dataset ID
            table_id: BigQuery table ID with training data
        """
        self.project_id = project_id
        self.location = location
        self.dataset_id = dataset_id
        self.table_id = table_id
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)
        
        self.bq_client = bigquery.Client(project=project_id)
    
    def prepare_training_data(self) -> str:
        """
        Prepare training data in BigQuery
        
        Returns:
            BigQuery URI for training data
        """
        # Ensure table exists and has data
        table_ref = self.bq_client.dataset(self.dataset_id).table(self.table_id)
        
        try:
            table = self.bq_client.get_table(table_ref)
            num_rows = table.num_rows
            logger.info(f"Training data table has {num_rows} rows")
        except Exception as e:
            logger.error(f"Error accessing training data: {e}")
            raise
        
        # Return BigQuery URI
        bq_uri = f"bq://{self.project_id}.{self.dataset_id}.{self.table_id}"
        return bq_uri
    
    def train_automl_model(
        self,
        display_name: str = "churn-prediction-automl",
        target_column: str = "is_churn",
        budget_milli_node_hours: int = 1000,
        optimization_objective: str = "MAXIMIZE_AU_ROC"
    ) -> Dict[str, Any]:
        """
        Train AutoML tabular model
        
        Args:
            display_name: Display name for the model
            target_column: Target column name
            budget_milli_node_hours: Training budget
            optimization_objective: Optimization objective
            
        Returns:
            Training job information
        """
        logger.info("Starting Vertex AI AutoML training...")
        
        # Prepare training data
        bq_uri = self.prepare_training_data()
        
        # Create dataset
        dataset = aiplatform.TabularDataset.create(
            display_name=f"{display_name}-dataset",
            bq_source=bq_uri
        )
        
        logger.info(f"Created dataset: {dataset.resource_name}")
        
        # Train AutoML model
        job = aiplatform.AutoMLTabularTrainingJob(
            display_name=display_name,
            optimization_objective=optimization_objective,
            column_specs={
                target_column: "target"
            }
        )
        
        model = job.run(
            dataset=dataset,
            target_column=target_column,
            budget_milli_node_hours=budget_milli_node_hours,
            model_display_name=display_name,
            disable_early_stopping=False
        )
        
        logger.info(f"Training job completed: {model.resource_name}")
        
        return {
            "model_name": model.resource_name,
            "model_display_name": model.display_name,
            "dataset_name": dataset.resource_name
        }
    
    def deploy_model(
        self,
        model_name: str,
        endpoint_display_name: str = "churn-prediction-endpoint",
        machine_type: str = "n1-standard-2",
        min_replica_count: int = 1,
        max_replica_count: int = 1
    ) -> Dict[str, Any]:
        """
        Deploy model to Vertex AI endpoint
        
        Args:
            model_name: Model resource name
            endpoint_display_name: Endpoint display name
            machine_type: Machine type for deployment
            min_replica_count: Minimum number of replicas
            max_replica_count: Maximum number of replicas
            
        Returns:
            Endpoint information
        """
        logger.info("Deploying model to endpoint...")
        
        # Get model
        model = aiplatform.Model(model_name=model_name)
        
        # Create endpoint
        endpoint = model.deploy(
            endpoint=aiplatform.Endpoint.create(display_name=endpoint_display_name),
            deployed_model_display_name=endpoint_display_name,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count
        )
        
        logger.info(f"Model deployed to endpoint: {endpoint.resource_name}")
        
        return {
            "endpoint_name": endpoint.resource_name,
            "endpoint_display_name": endpoint.display_name,
            "model_name": model_name
        }
    
    def predict(
        self,
        endpoint_name: str,
        instances: list
    ) -> list:
        """
        Make predictions using deployed endpoint
        
        Args:
            endpoint_name: Endpoint resource name
            instances: List of instances to predict
            
        Returns:
            List of predictions
        """
        endpoint = aiplatform.Endpoint(endpoint_name=endpoint_name)
        predictions = endpoint.predict(instances=instances)
        return predictions.predictions


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    project_id = os.getenv("GCP_PROJECT_ID", "your-project-id")
    
    # Initialize pipeline
    pipeline = VertexAITrainingPipeline(
        project_id=project_id,
        dataset_id="customer_data",
        table_id="customer_features"
    )
    
    # Train model
    training_result = pipeline.train_automl_model(
        display_name="churn-prediction-automl",
        budget_milli_node_hours=1000
    )
    
    logger.info(f"Training result: {training_result}")
    
    # Deploy model (uncomment after training completes)
    # deployment_result = pipeline.deploy_model(
    #     model_name=training_result["model_name"],
    #     endpoint_display_name="churn-prediction-endpoint"
    # )
    # logger.info(f"Deployment result: {deployment_result}")

