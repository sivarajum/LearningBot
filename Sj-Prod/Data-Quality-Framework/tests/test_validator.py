"""
test_validator.py — Tests for DQValidator orchestrator.

Key coverage:
- Exception inside a rule is CAUGHT (not a crash) and reported as error
- overall_passed logic: True only when all error-severity rules pass
- ValidationResult summary fields are correct
"""

import os
import sys

import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.rules.base_rule import BaseRule, RuleResult
from src.rules.completeness import CompletenessRatioRule, NotNullRule
from src.rules.uniqueness import UniqueRule
from src.rules.validity import AllowedValuesRule
from src.validator import DQValidator, ValidationResult

# ---------------------------------------------------------------------------
# Helper: BrokenRule — always raises an exception during validate()
# ---------------------------------------------------------------------------

class BrokenRule(BaseRule):
    """A rule that intentionally raises an exception when validate() is called."""

    dimension = "validity"

    def validate(self, df: pd.DataFrame) -> RuleResult:
        raise RuntimeError("Intentional failure for testing exception isolation")


# ---------------------------------------------------------------------------
# DQValidator basic operation
# ---------------------------------------------------------------------------

class TestDQValidatorBasic:

    def _make_clean_df(self) -> pd.DataFrame:
        return pd.DataFrame({
            "customer_id": ["C001", "C002", "C003"],
            "email":       ["a@b.com", "c@d.com", "e@f.com"],
            "status":      ["active", "active", "inactive"],
        })

    def test_all_passing_rules_overall_passed_true(self):
        """When all error-severity rules pass, overall_passed should be True."""
        df = self._make_clean_df()
        rules = [
            NotNullRule(name="id_nn", column="customer_id"),
            UniqueRule(name="id_unique", column="customer_id"),
        ]
        validator = DQValidator(rules)
        result = validator.validate(df, dataset_name="test_customers")

        assert result.overall_passed is True
        assert result.passed_rules == 2
        assert result.failed_rules == 0
        assert result.total_rules == 2

    def test_one_failing_error_rule_sets_overall_failed(self):
        """One failing error-severity rule should set overall_passed=False."""
        df = pd.DataFrame({"customer_id": ["C001", "C001", "C002"]})  # duplicate
        rules = [
            UniqueRule(name="id_unique", column="customer_id", severity="error"),
        ]
        validator = DQValidator(rules)
        result = validator.validate(df, dataset_name="dup_customers")

        assert result.overall_passed is False
        assert result.failed_rules == 1

    def test_warning_severity_failure_does_not_affect_overall_passed(self):
        """A failing warning-severity rule should not cause overall_passed=False."""
        df = pd.DataFrame({
            "customer_id": ["C001", "C002"],
            "phone": [None, None],   # both null — fails warning rule
        })
        rules = [
            NotNullRule(name="id_nn", column="customer_id", severity="error"),
            CompletenessRatioRule(name="phone_cr", column="phone", threshold=0.05, severity="warning"),
        ]
        validator = DQValidator(rules)
        result = validator.validate(df)

        # id_nn passes (error-sev), phone_cr fails (warning-sev)
        assert result.overall_passed is True

    def test_result_row_count_correct(self):
        df = self._make_clean_df()
        rules = [NotNullRule(name="id_nn", column="customer_id")]
        validator = DQValidator(rules)
        result = validator.validate(df)

        assert result.row_count == 3

    def test_dataset_name_propagated(self):
        df = self._make_clean_df()
        rules = [NotNullRule(name="id_nn", column="customer_id")]
        validator = DQValidator(rules)
        result = validator.validate(df, dataset_name="my_dataset")

        assert result.dataset_name == "my_dataset"

    def test_requires_at_least_one_rule(self):
        """DQValidator should raise ValueError if constructed with empty rules list."""
        with pytest.raises(ValueError):
            DQValidator(rules=[])

    def test_results_list_length_equals_rule_count(self):
        df = self._make_clean_df()
        rules = [
            NotNullRule(name="r1", column="customer_id"),
            UniqueRule(name="r2", column="customer_id"),
            AllowedValuesRule(name="r3", column="status", allowed_values={"active", "inactive"}),
        ]
        validator = DQValidator(rules)
        result = validator.validate(df)

        assert len(result.results) == 3

    def test_validated_at_is_iso_format(self):
        df = self._make_clean_df()
        rules = [NotNullRule(name="r1", column="customer_id")]
        validator = DQValidator(rules)
        result = validator.validate(df)

        # Should end with 'Z' (UTC) and contain 'T'
        assert "T" in result.validated_at
        assert result.validated_at.endswith("Z")


# ---------------------------------------------------------------------------
# Exception isolation — the critical correctness requirement
# ---------------------------------------------------------------------------

class TestValidatorExceptionIsolation:

    def test_exception_in_one_rule_does_not_crash_validator(self):
        """An exception inside a rule must be caught. Validator must not raise."""
        df = pd.DataFrame({"customer_id": ["C001", "C002"]})
        rules = [
            NotNullRule(name="id_nn", column="customer_id"),
            BrokenRule(name="broken", column="customer_id"),
            UniqueRule(name="id_unique", column="customer_id"),
        ]
        validator = DQValidator(rules)

        # This must NOT raise — exception is caught internally
        result = validator.validate(df, dataset_name="isolation_test")

        assert isinstance(result, ValidationResult)

    def test_exception_rule_counted_in_error_rules(self):
        """The error_rules counter must be incremented when a rule throws."""
        df = pd.DataFrame({"x": [1, 2]})
        rules = [
            BrokenRule(name="broken1", column="x"),
            BrokenRule(name="broken2", column="x"),
        ]
        validator = DQValidator(rules)
        result = validator.validate(df)

        assert result.error_rules == 2

    def test_exception_result_has_passed_false(self):
        """A rule that threw an exception should appear in results as passed=False."""
        df = pd.DataFrame({"x": [1, 2]})
        rules = [BrokenRule(name="broken", column="x")]
        validator = DQValidator(rules)
        result = validator.validate(df)

        assert len(result.results) == 1
        assert result.results[0].passed is False

    def test_exception_result_details_contains_error_message(self):
        """The RuleResult.details for an exception should contain the error info."""
        df = pd.DataFrame({"x": [1, 2]})
        rules = [BrokenRule(name="broken", column="x")]
        validator = DQValidator(rules)
        result = validator.validate(df)

        assert "error" in result.results[0].details.lower() or "exception" in result.results[0].details.lower() or "Intentional" in result.results[0].details

    def test_good_rules_still_run_after_broken_rule(self):
        """Rules after a broken rule should still execute and produce results."""
        df = pd.DataFrame({"customer_id": ["C001", "C002"], "email": ["a@b.com", "c@d.com"]})
        rules = [
            BrokenRule(name="broken", column="customer_id"),
            NotNullRule(name="id_nn", column="customer_id"),   # this should still run
        ]
        validator = DQValidator(rules)
        result = validator.validate(df)

        # 2 results total: 1 error + 1 normal pass
        assert len(result.results) == 2
        good_results = [r for r in result.results if r.rule_name == "id_nn"]
        assert len(good_results) == 1
        assert good_results[0].passed is True


# ---------------------------------------------------------------------------
# ValidationResult helper methods
# ---------------------------------------------------------------------------

class TestValidationResultHelpers:

    def _run_mixed_validation(self) -> ValidationResult:
        df = pd.DataFrame({
            "id":     ["A", "A", "B"],    # duplicate — fails UniqueRule
            "status": ["active", "BOGUS", "active"],
        })
        rules = [
            UniqueRule(name="id_unique", column="id", severity="error"),
            AllowedValuesRule(
                name="status_values", column="status",
                allowed_values={"active", "inactive"}, severity="warning"
            ),
        ]
        validator = DQValidator(rules)
        return validator.validate(df)

    def test_failed_results_returns_only_failures(self):
        result = self._run_mixed_validation()
        failed = result.failed_results()
        assert all(not r.passed for r in failed)
        assert len(failed) >= 1

    def test_critical_failures_returns_only_error_severity_failures(self):
        result = self._run_mixed_validation()
        critical = result.critical_failures()
        assert all(r.severity == "error" for r in critical)
        assert all(not r.passed for r in critical)

    def test_to_dict_has_expected_keys(self):
        result = self._run_mixed_validation()
        d = result.to_dict()
        for key in ("dataset_name", "validated_at", "row_count", "total_rules",
                    "passed_rules", "failed_rules", "overall_passed", "rule_results"):
            assert key in d, f"Missing key: {key}"

    def test_summary_by_dim_contains_all_dimensions(self):
        df = pd.DataFrame({"id": ["A", "B"]})
        rules = [UniqueRule(name="id_unique", column="id")]
        validator = DQValidator(rules)
        result = validator.validate(df)

        for dim in ("completeness", "validity", "uniqueness", "consistency", "freshness"):
            assert dim in result.summary_by_dim
