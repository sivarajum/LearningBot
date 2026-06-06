"""Tests for the cloud_simulator module."""

import pandas as pd
import pytest

from src.cloud_simulator import (
    PRODUCT_CATEGORIES,
    REGIONS_BY_CLOUD,
    _generate_customers,
    _generate_transactions,
    generate_cloud_data,
    load_cloud_data,
    save_cloud_data,
)

CLOUDS = ["aws", "azure", "gcp"]

EXPECTED_CUSTOMER_COLUMNS = [
    "customer_id",
    "source_cloud",
    "name",
    "region",
    "signup_date",
    "plan",
    "monthly_spend",
    "is_active",
]

EXPECTED_TRANSACTION_COLUMNS = [
    "transaction_id",
    "customer_id",
    "source_cloud",
    "amount",
    "category",
    "transaction_date",
    "payment_method",
]


# ---------------------------------------------------------------------------
# Customer data generation
# ---------------------------------------------------------------------------

class TestGenerateCustomers:
    """Tests for _generate_customers."""

    @pytest.mark.parametrize("cloud", CLOUDS)
    def test_returns_dataframe(self, cloud):
        df = _generate_customers(cloud, n=10, seed=42)
        assert isinstance(df, pd.DataFrame)

    @pytest.mark.parametrize("cloud", CLOUDS)
    def test_correct_row_count(self, cloud):
        n = 25
        df = _generate_customers(cloud, n=n, seed=42)
        assert len(df) == n

    @pytest.mark.parametrize("cloud", CLOUDS)
    def test_expected_columns(self, cloud):
        df = _generate_customers(cloud, n=5, seed=42)
        for col in EXPECTED_CUSTOMER_COLUMNS:
            assert col in df.columns, f"Missing column: {col}"

    @pytest.mark.parametrize("cloud", CLOUDS)
    def test_source_cloud_value(self, cloud):
        df = _generate_customers(cloud, n=5, seed=42)
        assert (df["source_cloud"] == cloud).all()

    @pytest.mark.parametrize("cloud", CLOUDS)
    def test_customer_id_prefix(self, cloud):
        df = _generate_customers(cloud, n=5, seed=42)
        prefix = f"{cloud[:2].upper()}-"
        assert df["customer_id"].str.startswith(prefix).all()

    @pytest.mark.parametrize("cloud", CLOUDS)
    def test_regions_are_valid(self, cloud):
        df = _generate_customers(cloud, n=50, seed=42)
        valid_regions = set(REGIONS_BY_CLOUD[cloud])
        assert set(df["region"].unique()).issubset(valid_regions)

    def test_plans_are_valid(self):
        df = _generate_customers("aws", n=100, seed=42)
        valid_plans = {"free", "basic", "premium", "enterprise"}
        assert set(df["plan"].unique()).issubset(valid_plans)

    def test_monthly_spend_range(self):
        df = _generate_customers("aws", n=100, seed=42)
        assert df["monthly_spend"].min() >= 0
        assert df["monthly_spend"].max() <= 500

    def test_is_active_boolean(self):
        df = _generate_customers("aws", n=10, seed=42)
        assert df["is_active"].dtype == bool

    def test_deterministic_with_same_seed(self):
        df1 = _generate_customers("aws", n=10, seed=99)
        df2 = _generate_customers("aws", n=10, seed=99)
        pd.testing.assert_frame_equal(df1, df2)

    def test_different_seed_different_data(self):
        df1 = _generate_customers("aws", n=10, seed=1)
        df2 = _generate_customers("aws", n=10, seed=2)
        assert not df1["monthly_spend"].equals(df2["monthly_spend"])


# ---------------------------------------------------------------------------
# Transaction data generation
# ---------------------------------------------------------------------------

class TestGenerateTransactions:
    """Tests for _generate_transactions."""

    def test_returns_dataframe(self, aws_customers):
        df = _generate_transactions("aws", aws_customers, n=50, seed=43)
        assert isinstance(df, pd.DataFrame)

    def test_correct_row_count(self, aws_customers):
        n = 75
        df = _generate_transactions("aws", aws_customers, n=n, seed=43)
        assert len(df) == n

    def test_expected_columns(self, aws_customers):
        df = _generate_transactions("aws", aws_customers, n=50, seed=43)
        for col in EXPECTED_TRANSACTION_COLUMNS:
            assert col in df.columns, f"Missing column: {col}"

    def test_source_cloud_value(self, aws_customers):
        df = _generate_transactions("aws", aws_customers, n=50, seed=43)
        assert (df["source_cloud"] == "aws").all()

    def test_transaction_id_prefix(self, aws_customers):
        df = _generate_transactions("aws", aws_customers, n=50, seed=43)
        assert df["transaction_id"].str.startswith("TX-AW-").all()

    def test_customer_ids_valid(self, aws_customers):
        df = _generate_transactions("aws", aws_customers, n=50, seed=43)
        valid_ids = set(aws_customers["customer_id"])
        assert set(df["customer_id"].unique()).issubset(valid_ids)

    def test_categories_valid(self, aws_customers):
        df = _generate_transactions("aws", aws_customers, n=200, seed=43)
        assert set(df["category"].unique()).issubset(set(PRODUCT_CATEGORIES))

    def test_amount_range(self, aws_customers):
        df = _generate_transactions("aws", aws_customers, n=200, seed=43)
        assert df["amount"].min() >= 5
        assert df["amount"].max() <= 1000

    def test_payment_methods_valid(self, aws_customers):
        valid_methods = {"credit_card", "debit_card", "bank_transfer", "digital_wallet"}
        df = _generate_transactions("aws", aws_customers, n=200, seed=43)
        assert set(df["payment_method"].unique()).issubset(valid_methods)


# ---------------------------------------------------------------------------
# Full data generation
# ---------------------------------------------------------------------------

class TestGenerateCloudData:
    """Tests for generate_cloud_data."""

    def test_returns_all_clouds(self, small_cloud_data):
        assert set(small_cloud_data.keys()) == {"aws", "azure", "gcp"}

    def test_each_cloud_has_tables(self, small_cloud_data):
        for cloud in CLOUDS:
            assert "customers" in small_cloud_data[cloud]
            assert "transactions" in small_cloud_data[cloud]

    def test_customer_counts(self):
        data = generate_cloud_data(customers_per_cloud=15, transactions_per_cloud=30)
        for cloud in CLOUDS:
            assert len(data[cloud]["customers"]) == 15

    def test_transaction_counts(self):
        data = generate_cloud_data(customers_per_cloud=15, transactions_per_cloud=30)
        for cloud in CLOUDS:
            assert len(data[cloud]["transactions"]) == 30


# ---------------------------------------------------------------------------
# Save and load
# ---------------------------------------------------------------------------

class TestSaveAndLoad:
    """Tests for save_cloud_data and load_cloud_data."""

    def test_save_creates_parquet_files(self, tmp_data_dir, small_cloud_data):
        save_cloud_data(small_cloud_data)
        for cloud in CLOUDS:
            assert (tmp_data_dir / cloud / "customers.parquet").exists()
            assert (tmp_data_dir / cloud / "transactions.parquet").exists()

    def test_save_returns_paths(self, tmp_data_dir, small_cloud_data):
        saved = save_cloud_data(small_cloud_data)
        assert set(saved.keys()) == {"aws", "azure", "gcp"}
        for cloud, paths in saved.items():
            assert len(paths) == 2

    def test_load_roundtrip(self, tmp_data_dir, small_cloud_data):
        save_cloud_data(small_cloud_data)
        for cloud in CLOUDS:
            loaded = load_cloud_data(cloud, "customers")
            original = small_cloud_data[cloud]["customers"]
            assert len(loaded) == len(original)
            assert list(loaded.columns) == list(original.columns)

    def test_load_nonexistent_raises(self, tmp_data_dir):
        with pytest.raises(FileNotFoundError):
            load_cloud_data("aws", "nonexistent_table")
