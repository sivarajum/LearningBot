"""Tests for src.data_generator — synthetic data creation."""

import numpy as np
import pandas as pd
import pytest

from src.data_generator import (
    generate_customers,
    save_data,
    CONTRACT_TYPES,
    PAYMENT_METHODS,
    INTERNET_SERVICES,
    NUM_CUSTOMERS,
)

EXPECTED_COLUMNS = [
    "customer_id",
    "tenure",
    "monthly_charges",
    "total_charges",
    "contract_type",
    "payment_method",
    "internet_service",
    "num_support_tickets",
    "churn",
]


class TestGenerateCustomers:
    """Tests for generate_customers()."""

    def test_default_shape(self, full_dataframe):
        """Default generation should produce NUM_CUSTOMERS rows."""
        assert full_dataframe.shape[0] == NUM_CUSTOMERS

    def test_custom_size(self):
        """Passing a custom n should produce exactly that many rows."""
        df = generate_customers(n=200, seed=1)
        assert len(df) == 200

    def test_expected_columns(self, full_dataframe):
        """All expected columns must be present."""
        for col in EXPECTED_COLUMNS:
            assert col in full_dataframe.columns, f"Missing column: {col}"

    def test_no_extra_columns(self, full_dataframe):
        """No unexpected columns should appear."""
        assert set(full_dataframe.columns) == set(EXPECTED_COLUMNS)

    def test_churn_is_binary(self, full_dataframe):
        """Churn column must only contain 0 and 1."""
        unique_vals = set(full_dataframe["churn"].unique())
        assert unique_vals <= {0, 1}

    def test_no_nan_in_key_fields(self, full_dataframe):
        """Key fields should have no NaN values."""
        key_cols = [
            "customer_id", "tenure", "monthly_charges", "total_charges",
            "contract_type", "payment_method", "internet_service",
            "num_support_tickets", "churn",
        ]
        for col in key_cols:
            assert full_dataframe[col].isna().sum() == 0, f"NaN found in {col}"

    def test_tenure_range(self, full_dataframe):
        """Tenure should be between 1 and 72 inclusive."""
        assert full_dataframe["tenure"].min() >= 1
        assert full_dataframe["tenure"].max() <= 72

    def test_monthly_charges_range(self, full_dataframe):
        """Monthly charges should be between 20 and 120."""
        assert full_dataframe["monthly_charges"].min() >= 20.0
        assert full_dataframe["monthly_charges"].max() <= 120.0

    def test_contract_type_values(self, full_dataframe):
        """Contract types should only be from the defined set."""
        assert set(full_dataframe["contract_type"].unique()) <= set(CONTRACT_TYPES)

    def test_payment_method_values(self, full_dataframe):
        """Payment methods should only be from the defined set."""
        assert set(full_dataframe["payment_method"].unique()) <= set(PAYMENT_METHODS)

    def test_internet_service_values(self, full_dataframe):
        """Internet services should only be from the defined set."""
        assert set(full_dataframe["internet_service"].unique()) <= set(INTERNET_SERVICES)

    def test_support_tickets_range(self, full_dataframe):
        """Support tickets should be clipped between 0 and 10."""
        assert full_dataframe["num_support_tickets"].min() >= 0
        assert full_dataframe["num_support_tickets"].max() <= 10

    def test_customer_ids_unique(self, full_dataframe):
        """Customer IDs should be unique."""
        assert full_dataframe["customer_id"].is_unique

    def test_reproducibility(self):
        """Same seed should produce identical output."""
        df1 = generate_customers(n=100, seed=42)
        df2 = generate_customers(n=100, seed=42)
        pd.testing.assert_frame_equal(df1, df2)

    def test_different_seeds_differ(self):
        """Different seeds should produce different data."""
        df1 = generate_customers(n=100, seed=1)
        df2 = generate_customers(n=100, seed=2)
        assert not df1["monthly_charges"].equals(df2["monthly_charges"])

    def test_churn_rate_reasonable(self, full_dataframe):
        """Churn rate should be approximately 26% (within 20-32%)."""
        churn_rate = full_dataframe["churn"].mean()
        assert 0.20 <= churn_rate <= 0.32, f"Churn rate {churn_rate:.2%} out of expected range"


class TestSaveData:
    """Tests for save_data()."""

    def test_save_creates_file(self, tmp_path, raw_dataframe):
        """save_data should create a CSV file at the given path."""
        out = tmp_path / "test_customers.csv"
        result = save_data(raw_dataframe, path=out)
        assert result == out
        assert out.exists()

    def test_saved_file_readable(self, tmp_path, raw_dataframe):
        """Saved CSV should be readable and match the original DataFrame shape."""
        out = tmp_path / "test_customers.csv"
        save_data(raw_dataframe, path=out)
        loaded = pd.read_csv(out)
        assert loaded.shape == raw_dataframe.shape

    def test_save_creates_parent_dirs(self, tmp_path, raw_dataframe):
        """save_data should create parent directories if they don't exist."""
        out = tmp_path / "nested" / "dir" / "customers.csv"
        save_data(raw_dataframe, path=out)
        assert out.exists()
