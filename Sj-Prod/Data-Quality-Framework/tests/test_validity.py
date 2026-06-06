"""
test_validity.py — Tests for validity rules (RegexRule, ValueRangeRule, AllowedValuesRule).

Tests validate against real pandas DataFrames. No mocking of rule logic.
"""

import os
import sys

import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.rules.validity import AllowedValuesRule, RegexRule, ValueRangeRule

# ---------------------------------------------------------------------------
# RegexRule
# ---------------------------------------------------------------------------

class TestRegexRule:

    EMAIL_PATTERN = r'^[^@]+@[^@]+[.][^@]+$'

    def test_valid_emails_pass(self):
        """All valid email addresses should produce passed=True."""
        df = pd.DataFrame({"email": ["alice@example.com", "bob@test.org", "carol@company.co.uk"]})
        rule = RegexRule(name="email_format", column="email", pattern=self.EMAIL_PATTERN)
        result = rule.validate(df)

        assert result.passed is True
        assert result.failing_count == 0
        assert result.score == 1.0

    def test_invalid_email_fails(self):
        """An email without '@' should fail."""
        df = pd.DataFrame({"email": ["alice@example.com", "not-an-email", "another-bad"]})
        rule = RegexRule(name="email_format", column="email", pattern=self.EMAIL_PATTERN)
        result = rule.validate(df)

        assert result.passed is False
        assert result.failing_count == 2

    def test_null_values_skipped_by_regex(self):
        """Null values should be skipped — they don't count as regex failures."""
        df = pd.DataFrame({"email": ["alice@example.com", None, None]})
        rule = RegexRule(name="email_format", column="email", pattern=self.EMAIL_PATTERN)
        result = rule.validate(df)

        # 2 nulls are excluded; 1 valid email passes => no regex failures
        assert result.failing_count == 0
        assert result.passed is True

    def test_all_nulls_returns_passed(self):
        """A column that is entirely null should pass (nothing to validate)."""
        df = pd.DataFrame({"email": [None, None, None]})
        rule = RegexRule(name="email_format", column="email", pattern=self.EMAIL_PATTERN)
        result = rule.validate(df)

        assert result.passed is True
        assert result.score == 1.0

    def test_mixed_valid_invalid_partial_score(self):
        """2 valid + 2 invalid => failing_count == 2, score == 0.5."""
        df = pd.DataFrame({"email": ["a@b.com", "bad", "c@d.com", "alsobad"]})
        rule = RegexRule(name="email_format", column="email", pattern=self.EMAIL_PATTERN)
        result = rule.validate(df)

        assert result.failing_count == 2
        assert abs(result.score - 0.5) < 1e-6

    def test_invalid_regex_raises_on_init(self):
        """An invalid regex pattern should raise ValueError at init, not at validate time."""
        with pytest.raises(ValueError, match="Invalid regex"):
            RegexRule(name="bad_regex", column="col", pattern="[invalid(")

    def test_dimension_is_validity(self):
        df = pd.DataFrame({"col": ["abc"]})
        rule = RegexRule(name="r", column="col", pattern=r"^abc$")
        result = rule.validate(df)
        assert result.dimension == "validity"

    def test_missing_column_returns_error(self):
        df = pd.DataFrame({"other": ["x"]})
        rule = RegexRule(name="r", column="email", pattern=self.EMAIL_PATTERN)
        result = rule.validate(df)
        assert result.passed is False
        assert "does not exist" in result.details


# ---------------------------------------------------------------------------
# ValueRangeRule
# ---------------------------------------------------------------------------

class TestValueRangeRule:

    def test_in_range_passes(self):
        """All values in [0, 120] should pass for an age range rule."""
        df = pd.DataFrame({"age": [25, 0, 100, 120, 45]})
        rule = ValueRangeRule(name="age_range", column="age", min_val=0, max_val=120)
        result = rule.validate(df)

        assert result.passed is True
        assert result.failing_count == 0
        assert result.score == 1.0

    def test_out_of_range_fails(self):
        """Values outside [0, 120] should be flagged."""
        df = pd.DataFrame({"age": [25, -1, 121, 45]})
        rule = ValueRangeRule(name="age_range", column="age", min_val=0, max_val=120)
        result = rule.validate(df)

        assert result.passed is False
        assert result.failing_count == 2

    def test_non_numeric_handled_gracefully(self):
        """Non-numeric values that can't be coerced should count as failures, not crash."""
        df = pd.DataFrame({"score": [10, "not_a_number", 50, "???"]})
        rule = ValueRangeRule(name="score_range", column="score", min_val=0, max_val=100)
        result = rule.validate(df)

        # 2 non-numeric values should be flagged as failures
        assert result.failing_count == 2
        assert result.passed is False

    def test_null_values_skipped(self):
        """Null values are excluded from range checks (use NotNullRule for that)."""
        df = pd.DataFrame({"price": [10.0, None, 50.0, None]})
        rule = ValueRangeRule(name="price_range", column="price", min_val=0.0, max_val=1000.0)
        result = rule.validate(df)

        # Both nulls are skipped; remaining values are in range => passes
        assert result.passed is True
        assert result.failing_count == 0

    def test_no_lower_bound(self):
        """min_val=None means no lower bound check."""
        df = pd.DataFrame({"temp": [-9999, -100, 0, 50]})
        rule = ValueRangeRule(name="temp_max", column="temp", min_val=None, max_val=100)
        result = rule.validate(df)

        assert result.passed is True

    def test_no_upper_bound(self):
        """max_val=None means no upper bound check."""
        df = pd.DataFrame({"count": [0, 1000, 999999]})
        rule = ValueRangeRule(name="count_min", column="count", min_val=0, max_val=None)
        result = rule.validate(df)

        assert result.passed is True

    def test_invalid_range_raises_on_init(self):
        """min_val > max_val should raise ValueError at init."""
        with pytest.raises(ValueError):
            ValueRangeRule(name="r", column="col", min_val=100, max_val=10)

    def test_dimension_is_validity(self):
        df = pd.DataFrame({"x": [5]})
        rule = ValueRangeRule(name="r", column="x", min_val=0, max_val=10)
        result = rule.validate(df)
        assert result.dimension == "validity"

    def test_boundary_values_are_inclusive(self):
        """Values exactly at min_val and max_val should pass (inclusive)."""
        df = pd.DataFrame({"val": [0, 100]})
        rule = ValueRangeRule(name="r", column="val", min_val=0, max_val=100)
        result = rule.validate(df)
        assert result.passed is True


# ---------------------------------------------------------------------------
# AllowedValuesRule
# ---------------------------------------------------------------------------

class TestAllowedValuesRule:

    def test_valid_value_passes(self):
        """All values from the allowed set should pass."""
        df = pd.DataFrame({"status": ["active", "inactive", "pending", "active"]})
        rule = AllowedValuesRule(
            name="status_values", column="status",
            allowed_values={"active", "inactive", "pending"}
        )
        result = rule.validate(df)

        assert result.passed is True
        assert result.failing_count == 0
        assert result.score == 1.0

    def test_invalid_value_fails(self):
        """A value not in the allowed set should be flagged."""
        df = pd.DataFrame({"status": ["active", "deleted", "active", "unknown"]})
        rule = AllowedValuesRule(
            name="status_values", column="status",
            allowed_values={"active", "inactive", "pending"}
        )
        result = rule.validate(df)

        assert result.passed is False
        assert result.failing_count == 2

    def test_null_values_skipped(self):
        """Null values are not checked against the allowed set."""
        df = pd.DataFrame({"status": ["active", None, "pending", None]})
        rule = AllowedValuesRule(
            name="status_values", column="status",
            allowed_values={"active", "inactive", "pending"}
        )
        result = rule.validate(df)

        assert result.passed is True
        assert result.failing_count == 0

    def test_partial_invalid_score(self):
        """1 invalid in 4 total rows => score = 0.75."""
        df = pd.DataFrame({"tier": ["GOLD", "SILVER", "BRONZE", "PLATINUM"]})
        rule = AllowedValuesRule(
            name="tier_values", column="tier",
            allowed_values={"GOLD", "SILVER", "BRONZE"}
        )
        result = rule.validate(df)

        assert result.failing_count == 1
        assert abs(result.score - 0.75) < 1e-6

    def test_accepts_list_as_allowed_values(self):
        """AllowedValuesRule accepts a list (not just a set) for allowed_values."""
        df = pd.DataFrame({"col": ["a", "b"]})
        rule = AllowedValuesRule(name="r", column="col", allowed_values=["a", "b", "c"])
        result = rule.validate(df)
        assert result.passed is True

    def test_failing_values_in_result(self):
        """failing_values should contain the actual invalid values for debugging."""
        df = pd.DataFrame({"status": ["active", "BOGUS"]})
        rule = AllowedValuesRule(
            name="status_values", column="status", allowed_values={"active"}
        )
        result = rule.validate(df)

        assert "BOGUS" in result.failing_values

    def test_dimension_is_validity(self):
        df = pd.DataFrame({"x": ["a"]})
        rule = AllowedValuesRule(name="r", column="x", allowed_values={"a", "b"})
        result = rule.validate(df)
        assert result.dimension == "validity"
