"""Tests for the lake_builder module."""

import pandas as pd
import pytest

from src.cloud_simulator import _generate_customers, _generate_transactions
from src.lake_builder import (
    build_lake,
    compute_customer_metrics,
    ingest_all_customers,
    ingest_all_transactions,
    load_lake_table,
    transform_customers,
    transform_transactions,
)


CLOUDS = ["aws", "azure", "gcp"]


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------

class TestIngestion:
    """Tests for ingest_all_customers and ingest_all_transactions."""

    def test_ingest_customers_merges_all_clouds(self, saved_cloud_data):
        customers = ingest_all_customers()
        clouds_present = customers["source_cloud"].unique()
        assert set(clouds_present) == {"aws", "azure", "gcp"}

    def test_ingest_customers_total_count(self, saved_cloud_data):
        # small_cloud_data uses 10 customers per cloud = 30 total
        customers = ingest_all_customers()
        assert len(customers) == 30

    def test_ingest_transactions_merges_all_clouds(self, saved_cloud_data):
        transactions = ingest_all_transactions()
        clouds_present = transactions["source_cloud"].unique()
        assert set(clouds_present) == {"aws", "azure", "gcp"}

    def test_ingest_transactions_total_count(self, saved_cloud_data):
        # small_cloud_data uses 50 transactions per cloud = 150 total
        transactions = ingest_all_transactions()
        assert len(transactions) == 150

    def test_ingest_customers_raises_when_no_data(self, tmp_data_dir):
        with pytest.raises(RuntimeError, match="No customer data found"):
            ingest_all_customers()

    def test_ingest_transactions_raises_when_no_data(self, tmp_data_dir):
        with pytest.raises(RuntimeError, match="No transaction data found"):
            ingest_all_transactions()


# ---------------------------------------------------------------------------
# Unified customer table columns
# ---------------------------------------------------------------------------

class TestUnifiedCustomers:
    """Tests for the unified customer table structure."""

    def test_unified_customer_columns(self, saved_cloud_data):
        customers = ingest_all_customers()
        expected = [
            "customer_id", "source_cloud", "name", "region",
            "signup_date", "plan", "monthly_spend", "is_active",
        ]
        for col in expected:
            assert col in customers.columns, f"Missing column: {col}"

    def test_customer_ids_unique_within_cloud(self, saved_cloud_data):
        customers = ingest_all_customers()
        for cloud in CLOUDS:
            cloud_df = customers[customers["source_cloud"] == cloud]
            assert cloud_df["customer_id"].is_unique


# ---------------------------------------------------------------------------
# Unified transaction table
# ---------------------------------------------------------------------------

class TestUnifiedTransactions:
    """Tests for the unified transaction table structure."""

    def test_unified_transaction_columns(self, saved_cloud_data):
        transactions = ingest_all_transactions()
        expected = [
            "transaction_id", "customer_id", "source_cloud",
            "amount", "category", "transaction_date", "payment_method",
        ]
        for col in expected:
            assert col in transactions.columns, f"Missing column: {col}"

    def test_transaction_ids_unique(self, saved_cloud_data):
        transactions = ingest_all_transactions()
        assert transactions["transaction_id"].is_unique


# ---------------------------------------------------------------------------
# Transform customers (feature engineering)
# ---------------------------------------------------------------------------

class TestTransformCustomers:
    """Tests for transform_customers (tenure_days, spend_tier)."""

    def test_tenure_days_column_added(self, saved_cloud_data):
        customers = ingest_all_customers()
        transformed = transform_customers(customers)
        assert "tenure_days" in transformed.columns

    def test_tenure_days_positive(self, saved_cloud_data):
        customers = ingest_all_customers()
        transformed = transform_customers(customers)
        assert (transformed["tenure_days"] >= 0).all()

    def test_spend_tier_column_added(self, saved_cloud_data):
        customers = ingest_all_customers()
        transformed = transform_customers(customers)
        assert "spend_tier" in transformed.columns

    def test_spend_tier_valid_values(self, saved_cloud_data):
        customers = ingest_all_customers()
        transformed = transform_customers(customers)
        valid_tiers = {"low", "medium", "high", "premium"}
        actual_tiers = set(transformed["spend_tier"].dropna().unique())
        assert actual_tiers.issubset(valid_tiers)

    def test_spend_tier_bins(self):
        """Verify spend_tier bin boundaries."""
        df = pd.DataFrame({
            "customer_id": ["C1", "C2", "C3", "C4"],
            "source_cloud": ["aws"] * 4,
            "name": ["A", "B", "C", "D"],
            "region": ["us-east-1"] * 4,
            "signup_date": [pd.Timestamp("2023-01-01", tz="UTC")] * 4,
            "plan": ["free"] * 4,
            "monthly_spend": [10.0, 100.0, 200.0, 400.0],
            "is_active": [True] * 4,
        })
        transformed = transform_customers(df)
        tiers = transformed["spend_tier"].tolist()
        assert tiers[0] == "low"       # 10 -> [0, 50)
        assert tiers[1] == "medium"    # 100 -> [50, 150)
        assert tiers[2] == "high"      # 200 -> [150, 300)
        assert tiers[3] == "premium"   # 400 -> [300, inf)

    def test_transform_does_not_mutate_input(self, saved_cloud_data):
        customers = ingest_all_customers()
        original_cols = list(customers.columns)
        transform_customers(customers)
        assert list(customers.columns) == original_cols


# ---------------------------------------------------------------------------
# Transform transactions
# ---------------------------------------------------------------------------

class TestTransformTransactions:
    """Tests for transform_transactions."""

    def test_month_column_added(self, saved_cloud_data):
        transactions = ingest_all_transactions()
        transformed = transform_transactions(transactions)
        assert "month" in transformed.columns

    def test_amount_bucket_column_added(self, saved_cloud_data):
        transactions = ingest_all_transactions()
        transformed = transform_transactions(transactions)
        assert "amount_bucket" in transformed.columns

    def test_amount_bucket_valid_values(self, saved_cloud_data):
        transactions = ingest_all_transactions()
        transformed = transform_transactions(transactions)
        valid_buckets = {"small", "medium", "large", "whale"}
        actual_buckets = set(transformed["amount_bucket"].dropna().unique())
        assert actual_buckets.issubset(valid_buckets)

    def test_transform_does_not_mutate_input(self, saved_cloud_data):
        transactions = ingest_all_transactions()
        original_cols = list(transactions.columns)
        transform_transactions(transactions)
        assert list(transactions.columns) == original_cols


# ---------------------------------------------------------------------------
# Customer metrics aggregation
# ---------------------------------------------------------------------------

class TestComputeCustomerMetrics:
    """Tests for compute_customer_metrics."""

    def test_metrics_columns(self, saved_cloud_data):
        customers = transform_customers(ingest_all_customers())
        transactions = transform_transactions(ingest_all_transactions())
        metrics = compute_customer_metrics(customers, transactions)

        expected_extra = [
            "total_transactions", "total_spent",
            "avg_transaction", "max_transaction", "unique_categories",
        ]
        for col in expected_extra:
            assert col in metrics.columns, f"Missing metric column: {col}"

    def test_metrics_preserves_all_customers(self, saved_cloud_data):
        customers = transform_customers(ingest_all_customers())
        transactions = transform_transactions(ingest_all_transactions())
        metrics = compute_customer_metrics(customers, transactions)
        assert len(metrics) == len(customers)

    def test_total_transactions_not_negative(self, saved_cloud_data):
        customers = transform_customers(ingest_all_customers())
        transactions = transform_transactions(ingest_all_transactions())
        metrics = compute_customer_metrics(customers, transactions)
        assert (metrics["total_transactions"] >= 0).all()

    def test_total_spent_not_negative(self, saved_cloud_data):
        customers = transform_customers(ingest_all_customers())
        transactions = transform_transactions(ingest_all_transactions())
        metrics = compute_customer_metrics(customers, transactions)
        assert (metrics["total_spent"] >= 0).all()

    def test_customers_with_no_transactions_have_zero_spend(self):
        """A customer with no transactions should have 0 for all metric columns."""
        customers = pd.DataFrame({
            "customer_id": ["LONE-001"],
            "source_cloud": ["aws"],
            "name": ["Lonely"],
            "region": ["us-east-1"],
            "signup_date": [pd.Timestamp("2023-06-01", tz="UTC")],
            "plan": ["free"],
            "monthly_spend": [0.0],
            "is_active": [True],
            "tenure_days": [365],
            "spend_tier": ["low"],
        })
        transactions = pd.DataFrame({
            "transaction_id": ["TX-NONE"],
            "customer_id": ["OTHER-001"],
            "source_cloud": ["aws"],
            "amount": [100.0],
            "category": ["books"],
            "transaction_date": [pd.Timestamp("2023-07-01", tz="UTC")],
            "payment_method": ["credit_card"],
        })
        metrics = compute_customer_metrics(customers, transactions)
        row = metrics.iloc[0]
        assert row["total_transactions"] == 0
        assert row["total_spent"] == 0
        assert row["avg_transaction"] == 0


# ---------------------------------------------------------------------------
# Full build_lake pipeline
# ---------------------------------------------------------------------------

class TestBuildLake:
    """Tests for the full build_lake pipeline."""

    def test_build_lake_creates_parquet_files(self, saved_cloud_data):
        from src.lake_builder import LAKE_DIR

        build_lake()
        assert (LAKE_DIR / "customers.parquet").exists()
        assert (LAKE_DIR / "transactions.parquet").exists()
        assert (LAKE_DIR / "customer_metrics.parquet").exists()

    def test_build_lake_returns_paths(self, saved_cloud_data):
        paths = build_lake()
        assert "customers" in paths
        assert "transactions" in paths
        assert "customer_metrics" in paths

    def test_load_lake_table_roundtrip(self, built_lake):
        customers = load_lake_table("customers")
        assert isinstance(customers, pd.DataFrame)
        assert len(customers) > 0

    def test_load_lake_table_nonexistent_raises(self, built_lake):
        with pytest.raises(FileNotFoundError):
            load_lake_table("nonexistent_table")
