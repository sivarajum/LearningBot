"""Tests for src.feature_engineering — derived features, encoding, scaling."""

import numpy as np
import pandas as pd
import pytest
from sklearn.preprocessing import LabelEncoder, StandardScaler

from src.feature_engineering import (
    create_derived_features,
    encode_categoricals,
    build_features,
)


DERIVED_COLUMNS = [
    "avg_monthly_spend",
    "tenure_bucket",
    "support_ticket_rate",
    "charge_tenure_ratio",
]

EXPECTED_FEATURE_NAMES = [
    "tenure", "monthly_charges", "total_charges",
    "contract_type", "payment_method", "internet_service",
    "num_support_tickets", "avg_monthly_spend",
    "tenure_bucket", "support_ticket_rate", "charge_tenure_ratio",
]


class TestCreateDerivedFeatures:
    """Tests for create_derived_features()."""

    def test_adds_derived_columns(self, raw_dataframe):
        """Derived feature columns should appear after transformation."""
        result = create_derived_features(raw_dataframe)
        for col in DERIVED_COLUMNS:
            assert col in result.columns, f"Missing derived column: {col}"

    def test_does_not_modify_original(self, raw_dataframe):
        """Original DataFrame should not be mutated."""
        original_cols = list(raw_dataframe.columns)
        create_derived_features(raw_dataframe)
        assert list(raw_dataframe.columns) == original_cols

    def test_avg_monthly_spend_positive(self, raw_dataframe):
        """Average monthly spend should be non-negative."""
        result = create_derived_features(raw_dataframe)
        assert (result["avg_monthly_spend"] >= 0).all()

    def test_tenure_bucket_values(self, raw_dataframe):
        """Tenure bucket should be one of {0, 1, 2, 3}."""
        result = create_derived_features(raw_dataframe)
        assert set(result["tenure_bucket"].unique()) <= {0, 1, 2, 3}

    def test_support_ticket_rate_non_negative(self, raw_dataframe):
        """Support ticket rate should be non-negative."""
        result = create_derived_features(raw_dataframe)
        assert (result["support_ticket_rate"] >= 0).all()

    def test_charge_tenure_ratio_positive(self, raw_dataframe):
        """Charge-tenure ratio should be positive (both factors are positive)."""
        result = create_derived_features(raw_dataframe)
        assert (result["charge_tenure_ratio"] > 0).all()

    def test_preserves_original_columns(self, raw_dataframe):
        """All original columns should still be present."""
        result = create_derived_features(raw_dataframe)
        for col in raw_dataframe.columns:
            assert col in result.columns


class TestEncodeCategoricals:
    """Tests for encode_categoricals()."""

    def test_returns_dataframe_and_encoders(self, raw_dataframe):
        """Should return a (DataFrame, dict) tuple."""
        result_df, encoders = encode_categoricals(raw_dataframe, fit=True)
        assert isinstance(result_df, pd.DataFrame)
        assert isinstance(encoders, dict)

    def test_encodes_three_columns(self, raw_dataframe):
        """Should produce encoders for contract_type, payment_method, internet_service."""
        _, encoders = encode_categoricals(raw_dataframe, fit=True)
        assert set(encoders.keys()) == {"contract_type", "payment_method", "internet_service"}

    def test_encoded_values_are_numeric(self, raw_dataframe):
        """After encoding, categorical columns should be integers."""
        result_df, _ = encode_categoricals(raw_dataframe, fit=True)
        for col in ["contract_type", "payment_method", "internet_service"]:
            assert np.issubdtype(result_df[col].dtype, np.integer)

    def test_does_not_modify_original(self, raw_dataframe):
        """Original DataFrame should not be mutated."""
        orig_types = raw_dataframe.dtypes.copy()
        encode_categoricals(raw_dataframe, fit=True)
        pd.testing.assert_series_equal(raw_dataframe.dtypes, orig_types)

    def test_reuse_encoders(self, raw_dataframe):
        """Passing fitted encoders with fit=False should produce consistent encoding."""
        _, encoders = encode_categoricals(raw_dataframe, fit=True)
        # Build a small test row
        single_row = raw_dataframe.iloc[:1].copy()
        result_df, _ = encode_categoricals(single_row, encoders=encoders, fit=False)
        for col in ["contract_type", "payment_method", "internet_service"]:
            assert np.issubdtype(result_df[col].dtype, np.integer)


class TestBuildFeatures:
    """Tests for build_features()."""

    def test_returns_correct_tuple_structure(self, raw_dataframe):
        """Should return (X, y, feature_names, artifacts)."""
        result = build_features(raw_dataframe, fit=True)
        assert len(result) == 4
        X, y, feature_names, artifacts = result
        assert isinstance(X, np.ndarray)
        assert isinstance(y, np.ndarray)
        assert isinstance(feature_names, list)
        assert isinstance(artifacts, dict)

    def test_feature_names_correct(self, raw_dataframe):
        """Feature names should match the expected list."""
        _, _, feature_names, _ = build_features(raw_dataframe, fit=True)
        assert feature_names == EXPECTED_FEATURE_NAMES

    def test_x_shape_matches_features(self, raw_dataframe):
        """X should have columns matching len(feature_names) and rows matching input."""
        X, _, feature_names, _ = build_features(raw_dataframe, fit=True)
        assert X.shape == (len(raw_dataframe), len(feature_names))

    def test_y_shape_matches_rows(self, raw_dataframe):
        """y should have the same number of elements as rows in input."""
        _, y, _, _ = build_features(raw_dataframe, fit=True)
        assert y.shape == (len(raw_dataframe),)

    def test_y_is_binary(self, raw_dataframe):
        """y (churn) should still be binary after feature engineering."""
        _, y, _, _ = build_features(raw_dataframe, fit=True)
        assert set(np.unique(y)) <= {0, 1}

    def test_artifacts_contain_scaler(self, raw_dataframe):
        """Artifacts should include a fitted StandardScaler."""
        _, _, _, artifacts = build_features(raw_dataframe, fit=True)
        assert "scaler" in artifacts
        assert isinstance(artifacts["scaler"], StandardScaler)

    def test_artifacts_contain_encoders(self, raw_dataframe):
        """Artifacts should include label encoders."""
        _, _, _, artifacts = build_features(raw_dataframe, fit=True)
        assert "encoders" in artifacts
        assert isinstance(artifacts["encoders"], dict)
        for key in ["contract_type", "payment_method", "internet_service"]:
            assert key in artifacts["encoders"]
            assert isinstance(artifacts["encoders"][key], LabelEncoder)

    def test_artifacts_contain_feature_names(self, raw_dataframe):
        """Artifacts should include feature_names list."""
        _, _, _, artifacts = build_features(raw_dataframe, fit=True)
        assert "feature_names" in artifacts
        assert artifacts["feature_names"] == EXPECTED_FEATURE_NAMES

    def test_scaled_features_near_zero_mean(self, raw_dataframe):
        """Scaled features should have approximately zero mean."""
        X, _, _, _ = build_features(raw_dataframe, fit=True)
        means = np.abs(X.mean(axis=0))
        # After StandardScaler, column means should be very close to 0
        assert np.all(means < 0.1), f"Some feature means too far from 0: {means}"

    def test_inference_mode(self, raw_dataframe):
        """Using fit=False with pre-fitted artifacts should work on single rows."""
        _, _, _, artifacts = build_features(raw_dataframe, fit=True)
        single = raw_dataframe.iloc[:1].copy()
        X, y_inf, fnames, _ = build_features(
            single,
            scaler=artifacts["scaler"],
            encoders=artifacts["encoders"],
            fit=False,
        )
        assert X.shape == (1, len(EXPECTED_FEATURE_NAMES))

    def test_no_nan_in_features(self, raw_dataframe):
        """Feature matrix should contain no NaN values."""
        X, _, _, _ = build_features(raw_dataframe, fit=True)
        assert not np.any(np.isnan(X))
