"""
Feature Store Implementation
Using Feast for feature management
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from feast import FeatureStore, Entity, Feature, FeatureView, ValueType
from feast.data_source import FileSource

logger = logging.getLogger(__name__)


class FeatureStoreManager:
    """Feature store manager using Feast"""
    
    def __init__(self, repo_path: str = "./feature_repo"):
        """
        Initialize feature store manager
        
        Args:
            repo_path: Path to Feast feature repository
        """
        self.repo_path = repo_path
        self.store = None
        self._initialize_store()
    
    def _initialize_store(self):
        """Initialize Feast feature store"""
        try:
            self.store = FeatureStore(repo_path=self.repo_path)
            logger.info(f"Feature store initialized from {self.repo_path}")
        except Exception as e:
            logger.warning(f"Feature store not found at {self.repo_path}. Creating new one.")
            self._create_feature_repo()
    
    def _create_feature_repo(self):
        """Create new feature repository"""
        # This would typically be done via Feast CLI
        # For now, we'll just log the structure
        logger.info("Feature repository structure:")
        logger.info(f"  {self.repo_path}/")
        logger.info(f"    feature_store.yaml")
        logger.info(f"    features/")
        logger.info(f"    data/")
    
    def define_entity(self, name: str, value_type: str = "STRING"):
        """
        Define a feature entity
        
        Args:
            name: Entity name
            value_type: Value type (STRING, INT64, etc.)
        """
        entity = Entity(
            name=name,
            value_type=ValueType[value_type]
        )
        logger.info(f"Defined entity: {name}")
        return entity
    
    def define_feature_view(
        self,
        name: str,
        entities: List[Entity],
        features: List[Feature],
        source: Any,
        ttl: Optional[int] = None
    ):
        """
        Define a feature view
        
        Args:
            name: Feature view name
            entities: List of entities
            features: List of features
            source: Data source
            ttl: Time to live in seconds
        """
        feature_view = FeatureView(
            name=name,
            entities=entities,
            features=features,
            source=source,
            ttl=ttl
        )
        logger.info(f"Defined feature view: {name}")
        return feature_view
    
    def get_online_features(
        self,
        entity_rows: List[Dict[str, Any]],
        features: List[str]
    ) -> pd.DataFrame:
        """
        Get online features
        
        Args:
            entity_rows: List of entity rows
            features: List of feature names
            
        Returns:
            DataFrame with features
        """
        if self.store is None:
            raise ValueError("Feature store not initialized")
        
        feature_vector = self.store.get_online_features(
            features=features,
            entity_rows=entity_rows
        )
        
        return feature_vector.to_df()
    
    def get_historical_features(
        self,
        entity_df: pd.DataFrame,
        features: List[str]
    ) -> pd.DataFrame:
        """
        Get historical features
        
        Args:
            entity_df: Entity DataFrame
            features: List of feature names
            
        Returns:
            DataFrame with historical features
        """
        if self.store is None:
            raise ValueError("Feature store not initialized")
        
        feature_df = self.store.get_historical_features(
            features=features,
            entity_df=entity_df
        )
        
        return feature_df.to_df()
    
    def materialize_features(
        self,
        start_date: datetime,
        end_date: datetime
    ):
        """
        Materialize features to online store
        
        Args:
            start_date: Start date
            end_date: End date
        """
        if self.store is None:
            raise ValueError("Feature store not initialized")
        
        self.store.materialize(start_date, end_date)
        logger.info(f"Materialized features from {start_date} to {end_date}")


class AdvancedFeatureEngineering:
    """Advanced feature engineering utilities"""
    
    @staticmethod
    def create_time_features(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        """
        Create time-based features
        
        Args:
            df: Input DataFrame
            date_column: Date column name
            
        Returns:
            DataFrame with time features
        """
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        df["year"] = df[date_column].dt.year
        df["month"] = df[date_column].dt.month
        df["day"] = df[date_column].dt.day
        df["day_of_week"] = df[date_column].dt.dayofweek
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
        df["hour"] = df[date_column].dt.hour
        df["quarter"] = df[date_column].dt.quarter
        
        return df
    
    @staticmethod
    def create_aggregation_features(
        df: pd.DataFrame,
        group_by: str,
        agg_columns: List[str],
        agg_functions: List[str] = ["mean", "std", "min", "max"]
    ) -> pd.DataFrame:
        """
        Create aggregation features
        
        Args:
            df: Input DataFrame
            group_by: Column to group by
            agg_columns: Columns to aggregate
            agg_functions: Aggregation functions
            
        Returns:
            DataFrame with aggregation features
        """
        agg_dict = {}
        for col in agg_columns:
            for func in agg_functions:
                agg_dict[f"{col}_{func}"] = (col, func)
        
        aggregated = df.groupby(group_by).agg(agg_dict).reset_index()
        
        return aggregated
    
    @staticmethod
    def create_interaction_features(
        df: pd.DataFrame,
        feature_pairs: List[tuple]
    ) -> pd.DataFrame:
        """
        Create interaction features
        
        Args:
            df: Input DataFrame
            feature_pairs: List of (feature1, feature2) tuples
            
        Returns:
            DataFrame with interaction features
        """
        df = df.copy()
        
        for feat1, feat2 in feature_pairs:
            df[f"{feat1}_x_{feat2}"] = df[feat1] * df[feat2]
            df[f"{feat1}_div_{feat2}"] = df[feat1] / (df[feat2] + 1e-8)  # Avoid division by zero
        
        return df


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Feature engineering example
    import numpy as np
    
    df = pd.DataFrame({
        "customer_id": range(100),
        "timestamp": pd.date_range("2024-01-01", periods=100, freq="D"),
        "amount": np.random.rand(100) * 100,
        "quantity": np.random.randint(1, 10, 100)
    })
    
    fe = AdvancedFeatureEngineering()
    
    # Create time features
    df_with_time = fe.create_time_features(df, "timestamp")
    print("Time features created:", [col for col in df_with_time.columns if col not in df.columns])
    
    # Create aggregation features
    df_with_agg = fe.create_aggregation_features(
        df,
        group_by="customer_id",
        agg_columns=["amount", "quantity"]
    )
    print("Aggregation features created:", df_with_agg.columns.tolist())
    
    print("Feature engineering complete!")

