"""
test_uniqueness.py — Tests for uniqueness rules (UniqueRule, UniquenessRatioRule).

Tests validate against real pandas DataFrames. No mocking of rule logic.
"""

import os
import sys

import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.rules.uniqueness import UniquenessRatioRule, UniqueRule

# ---------------------------------------------------------------------------
# UniqueRule
# ---------------------------------------------------------------------------

class TestUniqueRule:

    def test_distinct_column_passes(self):
        """A column with all distinct values should pass."""
        df = pd.DataFrame({"customer_id": ["C001", "C002", "C003", "C004"]})
        rule = UniqueRule(name="customer_id_unique", column="customer_id")
        result = rule.validate(df)

        assert result.passed is True
        assert result.failing_count == 0
        assert result.score == 1.0

    def test_duplicate_column_fails(self):
        """A column with duplicate values should fail."""
        df = pd.DataFrame({"order_id": ["O001", "O002", "O001", "O003"]})
        rule = UniqueRule(name="order_id_unique", column="order_id")
        result = rule.validate(df)

        assert result.passed is False
        assert result.failing_count == 1   # 1 duplicate row (O001 appears twice, second is the failure)

    def test_all_duplicates_fail(self):
        """All duplicate values should be flagged."""
        df = pd.DataFrame({"id": ["A", "A", "A", "A"]})
        rule = UniqueRule(name="id_unique", column="id")
        result = rule.validate(df)

        assert result.passed is False
        assert result.failing_count == 3   # 3 duplicates (keep first)

    def test_nulls_excluded_from_uniqueness_check(self):
        """Null values should be excluded from uniqueness checks."""
        df = pd.DataFrame({"id": ["A", "B", None, None, "C"]})
        rule = UniqueRule(name="id_unique", column="id")
        result = rule.validate(df)

        # A, B, C are all distinct (nulls ignored) => passes
        assert result.passed is True

    def test_single_value_passes(self):
        """A single-row DataFrame should always pass uniqueness."""
        df = pd.DataFrame({"id": ["X"]})
        rule = UniqueRule(name="id_unique", column="id")
        result = rule.validate(df)

        assert result.passed is True

    def test_failing_values_contain_duplicates(self):
        """The failing_values list should contain the duplicate values."""
        df = pd.DataFrame({"id": ["X", "X", "Y"]})
        rule = UniqueRule(name="id_unique", column="id")
        result = rule.validate(df)

        assert "X" in result.failing_values

    def test_dimension_is_uniqueness(self):
        df = pd.DataFrame({"x": [1, 2, 3]})
        rule = UniqueRule(name="r", column="x")
        result = rule.validate(df)
        assert result.dimension == "uniqueness"

    def test_missing_column_returns_error(self):
        df = pd.DataFrame({"other": [1, 2]})
        rule = UniqueRule(name="r", column="nonexistent")
        result = rule.validate(df)
        assert result.passed is False
        assert "does not exist" in result.details

    def test_all_nulls_passes(self):
        """Column with all nulls has no non-null values to check — should pass."""
        df = pd.DataFrame({"id": [None, None, None]})
        rule = UniqueRule(name="id_unique", column="id")
        result = rule.validate(df)
        assert result.passed is True

    def test_score_reflects_proportion_of_duplicates(self):
        """score = (total - failing_count) / total."""
        # 4 rows, 2 are duplicates (O001 appears 3 times => 2 extra)
        df = pd.DataFrame({"id": ["O001", "O001", "O001", "O002"]})
        rule = UniqueRule(name="id_unique", column="id")
        result = rule.validate(df)

        assert result.failing_count == 2
        expected_score = (4 - 2) / 4
        assert abs(result.score - expected_score) < 1e-6


# ---------------------------------------------------------------------------
# UniquenessRatioRule
# ---------------------------------------------------------------------------

class TestUniquenessRatioRule:

    def test_passes_above_threshold(self):
        """100% unique column should pass a 95% threshold."""
        df = pd.DataFrame({"email": ["a@x.com", "b@x.com", "c@x.com", "d@x.com"]})
        rule = UniquenessRatioRule(name="email_mostly_unique", column="email", threshold=0.95)
        result = rule.validate(df)

        assert result.passed is True

    def test_fails_below_threshold(self):
        """50% uniqueness should fail a 95% threshold."""
        # 5 non-null values, only 2 distinct (A and B)
        df = pd.DataFrame({"tier": ["A", "A", "A", "B", "B"]})
        rule = UniquenessRatioRule(name="tier_ratio", column="tier", threshold=0.95)
        result = rule.validate(df)

        assert result.passed is False

    def test_threshold_validation_raises(self):
        with pytest.raises(ValueError):
            UniquenessRatioRule(name="x", column="x", threshold=1.5)

    def test_dimension_is_uniqueness(self):
        df = pd.DataFrame({"x": ["a", "b", "c"]})
        rule = UniquenessRatioRule(name="r", column="x", threshold=0.9)
        result = rule.validate(df)
        assert result.dimension == "uniqueness"
