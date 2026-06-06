"""
Feature Engineering Module
Creates features from raw customer data for churn prediction
"""
import logging
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from google.cloud import bigquery

logger = logging.getLogger(__name__)


class FeatureEngineeringPipeline:
    """Pipeline for feature engineering from customer data"""
    
    def __init__(self, project_id: str, dataset_id: str):
        """
        Initialize feature engineering pipeline
        
        Args:
            project_id: GCP project ID
            dataset_id: BigQuery dataset ID
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.bq_client = bigquery.Client(project=project_id)
    
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features from raw customer data
        
        Args:
            df: Raw customer data DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        logger.info("Starting feature engineering...")
        
        # Create feature DataFrame
        features_df = pd.DataFrame()
        
        # Customer ID
        features_df["customer_id"] = df["customer_id"]
        
        # Time-based features
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            features_df["hour_of_day"] = df["timestamp"].dt.hour
            features_df["day_of_week"] = df["timestamp"].dt.dayofweek
            features_df["is_weekend"] = (features_df["day_of_week"] >= 5).astype(int)
        
        # Aggregated features per customer
        customer_features = df.groupby("customer_id").agg({
            "total_spent": ["sum", "mean", "std"],
            "num_orders": ["sum", "mean"],
            "days_since_last_order": ["min", "mean"],
            "avg_order_value": ["mean", "std"],
            "event_type": "count"
        }).reset_index()
        
        # Flatten column names
        customer_features.columns = [
            "customer_id",
            "total_spent_sum",
            "total_spent_mean",
            "total_spent_std",
            "num_orders_sum",
            "num_orders_mean",
            "days_since_last_order_min",
            "days_since_last_order_mean",
            "avg_order_value_mean",
            "avg_order_value_std",
            "event_count"
        ]
        
        # Merge aggregated features
        features_df = features_df.merge(customer_features, on="customer_id", how="left")
        
        # Fill NaN values
        features_df = features_df.fillna(0)
        
        # Derived features
        features_df["spending_per_order"] = (
            features_df["total_spent_sum"] / (features_df["num_orders_sum"] + 1)
        )
        features_df["order_frequency"] = (
            features_df["num_orders_sum"] / (features_df["days_since_last_order_mean"] + 1)
        )
        features_df["spending_consistency"] = (
            1 / (features_df["total_spent_std"] + 1)
        )
        
        # Churn label (if available)
        if "is_churn" in df.columns:
            churn_labels = df.groupby("customer_id")["is_churn"].max().reset_index()
            features_df = features_df.merge(churn_labels, on="customer_id", how="left")
            features_df["is_churn"] = features_df["is_churn"].fillna(False).astype(int)
        
        logger.info(f"Engineered {len(features_df.columns)} features for {len(features_df)} customers")
        
        return features_df
    
    def get_feature_list(self) -> List[str]:
        """
        Get list of feature column names
        
        Returns:
            List of feature names
        """
        return [
            "hour_of_day",
            "day_of_week",
            "is_weekend",
            "total_spent_sum",
            "total_spent_mean",
            "total_spent_std",
            "num_orders_sum",
            "num_orders_mean",
            "days_since_last_order_min",
            "days_since_last_order_mean",
            "avg_order_value_mean",
            "avg_order_value_std",
            "event_count",
            "spending_per_order",
            "order_frequency",
            "spending_consistency"
        ]
    
    def save_features_to_bigquery(
        self,
        features_df: pd.DataFrame,
        table_id: str = "customer_features"
    ):
        """
        Save engineered features to BigQuery
        
        Args:
            features_df: DataFrame with features
            table_id: Target table ID
        """
        table_ref = self.bq_client.dataset(self.dataset_id).table(table_id)
        
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            source_format=bigquery.SourceFormat.PARQUET,
        )
        
        job = self.bq_client.load_table_from_dataframe(
            features_df, table_ref, job_config=job_config
        )
        job.result()
        
        logger.info(f"Saved features to {table_id}")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    from data_ingestion import DataIngestionPipeline
    import os
    
    project_id = os.getenv("GCP_PROJECT_ID", "your-project-id")
    
    # Ingest data
    ingestion = DataIngestionPipeline(
        project_id=project_id,
        dataset_id="customer_data",
        table_id="events"
    )
    df = ingestion.generate_synthetic_data(num_records=1000)
    
    # Engineer features
    feature_eng = FeatureEngineeringPipeline(
        project_id=project_id,
        dataset_id="customer_data"
    )
    features_df = feature_eng.extract_features(df)
    
    # Save features
    feature_eng.save_features_to_bigquery(features_df)
    
    logger.info("Feature engineering complete!")

