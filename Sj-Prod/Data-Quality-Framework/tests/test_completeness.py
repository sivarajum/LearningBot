"""
test_completeness.py — Tests for completeness rules (NotNullRule, CompletenessRatioRule).

Tests validate against real pandas DataFrames. No mocking of rule logic.
"""

import os
import sys

import numpy as np
import pandas as pd
import pytest

# Ensure project root is on sys.path so `from src.xxx` imports work
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.rules.completeness import CompletenessRatioRule, NotNullRule

# ---------------------------------------------------------------------------
# NotNullRule
# ---------------------------------------------------------------------------

class TestNotNullRule:

    def test_passes_on_clean_column(self):
        """A column with no nulls or empty strings should pass."""
        df = pd.DataFrame({"customer_id": ["C001", "C002", "C003", "C004"]})
        rule = NotNullRule(name="customer_id_not_null", column="customer_id")
        result = rule.validate(df)

        assert result.passed is True
        assert result.failing_count == 0
        assert result.score == 1.0
        assert result.total_count == 4

    def test_fails_on_nan_column(self):
        """A column with NaN values should fail."""
        df = pd.DataFrame({"customer_id": ["C001", None, "C003", np.nan]})
        rule = NotNullRule(name="customer_id_not_null", column="customer_id")
        result = rule.validate(df)

        assert result.passed is False
        assert result.failing_count == 2
        assert result.score < 1.0

    def test_fails_on_empty_strings(self):
        """NotNullRule treats empty strings as null — they should fail."""
        df = pd.DataFrame({"email": ["a@b.com", "", "c@d.com", "  "]})
        rule = NotNullRule(name="email_not_null", column="email")
        result = rule.validate(df)

        assert result.passed is False
        assert result.failing_count == 2

    def test_fails_on_all_null_column(self):
        """All-null column should have score 0 and pass_rate 0."""
        df = pd.DataFrame({"col": [None, None, None]})
        rule = NotNullRule(name="col_not_null", column="col")
        result = rule.validate(df)

        assert result.passed is False
        assert result.score == 0.0
        assert result.failing_count == 3

    def test_partial_nulls_score_is_proportional(self):
        """1 null out of 4 rows => pass_rate = 0.75."""
        df = pd.DataFrame({"val": ["a", "b", None, "d"]})
        rule = NotNullRule(name="val_not_null", column="val")
        result = rule.validate(df)

        assert result.passed is False
        assert abs(result.score - 0.75) < 1e-6
        assert result.failing_count == 1

    def test_missing_column_returns_error_result(self):
        """Accessing a non-existent column should return a failed RuleResult, not raise."""
        df = pd.DataFrame({"other_col": [1, 2, 3]})
        rule = NotNullRule(name="bad_col", column="nonexistent")
        result = rule.validate(df)

        assert result.passed is False
        assert "does not exist" in result.details

    def test_dimension_is_completeness(self):
        df = pd.DataFrame({"x": [1, 2]})
        rule = NotNullRule(name="x_nn", column="x")
        result = rule.validate(df)
        assert result.dimension == "completeness"

    def test_severity_propagated(self):
        df = pd.DataFrame({"x": ["a", None]})
        rule = NotNullRule(name="x_nn", column="x", severity="warning")
        result = rule.validate(df)
        assert result.severity == "warning"


# ---------------------------------------------------------------------------
# CompletenessRatioRule
# ---------------------------------------------------------------------------

class TestCompletenessRatioRule:

    def test_passes_exactly_at_threshold(self):
        """5% null rate on a 5% threshold should pass."""
        # 1 null in 20 rows = 5% null rate, threshold = 0.05
        data = ["val"] * 19 + [None]
        df = pd.DataFrame({"phone": data})
        rule = CompletenessRatioRule(
            name="phone_completeness", column="phone", threshold=0.05
        )
        result = rule.validate(df)

        assert result.passed is True
        assert result.score == 1.0

    def test_fails_above_threshold(self):
        """20% null rate on a 10% threshold should fail."""
        data = [None] * 2 + ["val"] * 8   # 20% null
        df = pd.DataFrame({"phone": data})
        rule = CompletenessRatioRule(
            name="phone_completeness", column="phone", threshold=0.10
        )
        result = rule.validate(df)

        assert result.passed is False
        assert result.score < 1.0

    def test_passes_well_below_threshold(self):
        """0% null rate should always pass regardless of threshold."""
        df = pd.DataFrame({"col": ["a", "b", "c", "d"]})
        rule = CompletenessRatioRule(
            name="col_completeness", column="col", threshold=0.05
        )
        result = rule.validate(df)

        assert result.passed is True
        assert result.score == 1.0

    def test_threshold_validation_raises_on_invalid(self):
        """threshold > 1.0 should raise ValueError at init time."""
        with pytest.raises(ValueError):
            CompletenessRatioRule(name="x", column="x", threshold=1.5)

    def test_threshold_validation_raises_on_negative(self):
        with pytest.raises(ValueError):
            CompletenessRatioRule(name="x", column="x", threshold=-0.1)

    def test_empty_strings_counted_as_null(self):
        """Empty strings count as nulls in CompletenessRatioRule."""
        df = pd.DataFrame({"col": ["a", "", "c", "   "]})
        # 2 empty = 50% null rate, threshold = 0.10 → should fail
        rule = CompletenessRatioRule(name="col_cr", column="col", threshold=0.10)
        result = rule.validate(df)

        assert result.passed is False
        assert result.failing_count == 2

    def test_result_details_contains_threshold(self):
        """Details string should mention the configured threshold."""
        df = pd.DataFrame({"col": ["a", None, "b"]})
        rule = CompletenessRatioRule(name="col_cr", column="col", threshold=0.20)
        result = rule.validate(df)

        assert "20.0%" in result.details or "0.20" in result.details or "threshold" in result.details.lower()
