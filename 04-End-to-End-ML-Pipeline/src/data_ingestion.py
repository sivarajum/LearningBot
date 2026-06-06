"""
Data Ingestion Module for ML Pipeline
Handles data ingestion from Pub/Sub to BigQuery
"""
import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
import pandas as pd
from google.cloud import bigquery, pubsub_v1
from google.cloud.exceptions import NotFound

logger = logging.getLogger(__name__)


class DataIngestionPipeline:
    """Pipeline for ingesting data from Pub/Sub to BigQuery"""
    
    def __init__(
        self,
        project_id: str,
        dataset_id: str,
        table_id: str,
        subscription_id: str = None
    ):
        """
        Initialize data ingestion pipeline
        
        Args:
            project_id: GCP project ID
            dataset_id: BigQuery dataset ID
            table_id: BigQuery table ID
            subscription_id: Pub/Sub subscription ID (optional)
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.subscription_id = subscription_id
        
        # Initialize clients
        self.bq_client = bigquery.Client(project=project_id)
        self.pubsub_subscriber = pubsub_v1.SubscriberClient()
        
        # Ensure dataset exists
        self._ensure_dataset()
        self._ensure_table()
    
    def _ensure_dataset(self):
        """Ensure BigQuery dataset exists"""
        dataset_ref = self.bq_client.dataset(self.dataset_id)
        try:
            self.bq_client.get_dataset(dataset_ref)
            logger.info(f"Dataset {self.dataset_id} already exists")
        except NotFound:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            dataset = self.bq_client.create_dataset(dataset, exists_ok=True)
            logger.info(f"Created dataset {self.dataset_id}")
    
    def _ensure_table(self):
        """Ensure BigQuery table exists with schema"""
        table_ref = self.bq_client.dataset(self.dataset_id).table(self.table_id)
        
        schema = [
            bigquery.SchemaField("customer_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("total_spent", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("num_orders", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("days_since_last_order", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("avg_order_value", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("is_churn", "BOOLEAN", mode="NULLABLE"),
            bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
        ]
        
        try:
            self.bq_client.get_table(table_ref)
            logger.info(f"Table {self.table_id} already exists")
        except NotFound:
            table = bigquery.Table(table_ref, schema=schema)
            table = self.bq_client.create_table(table)
            logger.info(f"Created table {self.table_id}")
    
    def generate_synthetic_data(self, num_records: int = 1000) -> pd.DataFrame:
        """
        Generate synthetic customer churn data for testing
        
        Args:
            num_records: Number of records to generate
            
        Returns:
            DataFrame with synthetic data
        """
        import numpy as np
        
        np.random.seed(42)
        
        data = {
            "customer_id": [f"CUST_{i:05d}" for i in range(num_records)],
            "timestamp": pd.date_range(
                start="2024-01-01",
                periods=num_records,
                freq="1H"
            ),
            "event_type": np.random.choice(
                ["purchase", "view", "cart_add", "login"],
                num_records
            ),
            "total_spent": np.random.gamma(2, 50, num_records),
            "num_orders": np.random.poisson(5, num_records),
            "days_since_last_order": np.random.exponential(7, num_records),
            "avg_order_value": np.random.normal(100, 30, num_records),
        }
        
        df = pd.DataFrame(data)
        
        # Generate churn label based on features
        churn_prob = (
            0.3 * (df["days_since_last_order"] > 30).astype(int) +
            0.2 * (df["num_orders"] < 2).astype(int) +
            0.2 * (df["total_spent"] < 50).astype(int) +
            0.3 * np.random.random(num_records)
        )
        df["is_churn"] = (churn_prob > 0.5).astype(bool)
        
        return df
    
    def load_to_bigquery(self, df: pd.DataFrame):
        """
        Load DataFrame to BigQuery
        
        Args:
            df: DataFrame to load
        """
        table_ref = self.bq_client.dataset(self.dataset_id).table(self.table_id)
        
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            source_format=bigquery.SourceFormat.PARQUET,
        )
        
        job = self.bq_client.load_table_from_dataframe(
            df, table_ref, job_config=job_config
        )
        job.result()
        
        logger.info(f"Loaded {len(df)} rows to {self.table_id}")
    
    def ingest_from_pubsub(self, max_messages: int = 10):
        """
        Ingest messages from Pub/Sub subscription
        
        Args:
            max_messages: Maximum number of messages to pull
        """
        if not self.subscription_id:
            logger.warning("No subscription ID provided, skipping Pub/Sub ingestion")
            return
        
        subscription_path = self.pubsub_subscriber.subscription_path(
            self.project_id, self.subscription_id
        )
        
        messages = []
        response = self.pubsub_subscriber.pull(
            request={"subscription": subscription_path, "max_messages": max_messages}
        )
        
        for received_message in response.received_messages:
            try:
                data = json.loads(received_message.message.data.decode("utf-8"))
                messages.append(data)
                
                # Acknowledge message
                self.pubsub_subscriber.acknowledge(
                    request={
                        "subscription": subscription_path,
                        "ack_ids": [received_message.ack_id],
                    }
                )
            except Exception as e:
                logger.error(f"Error processing message: {e}")
        
        if messages:
            df = pd.DataFrame(messages)
            self.load_to_bigquery(df)
            logger.info(f"Ingested {len(messages)} messages from Pub/Sub")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    pipeline = DataIngestionPipeline(
        project_id=os.getenv("GCP_PROJECT_ID", "your-project-id"),
        dataset_id="customer_data",
        table_id="events"
    )
    
    # Generate and load synthetic data
    df = pipeline.generate_synthetic_data(num_records=1000)
    pipeline.load_to_bigquery(df)
    
    logger.info("Data ingestion complete!")

