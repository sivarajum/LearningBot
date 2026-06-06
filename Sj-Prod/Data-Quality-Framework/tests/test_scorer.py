"""
test_scorer.py — Tests for DQScorer (grade thresholds, weighted score arithmetic).

All tests use real RuleResult and ValidationResult objects — no mocking of scoring logic.
"""

import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.rules.completeness import NotNullRule
from src.rules.uniqueness import UniqueRule
from src.rules.validity import AllowedValuesRule, ValueRangeRule
from src.scorer import DIMENSION_WEIGHTS, DQScoreCard, DQScorer, _compute_grade
from src.validator import DQValidator, ValidationResult

# ---------------------------------------------------------------------------
# Grade threshold tests
# ---------------------------------------------------------------------------

class TestGradeThresholds:

    def test_grade_a_at_90(self):
        grade, _ = _compute_grade(90.0)
        assert grade == "A"

    def test_grade_a_above_90(self):
        grade, _ = _compute_grade(95.5)
        assert grade == "A"

    def test_grade_a_at_exactly_100(self):
        grade, _ = _compute_grade(100.0)
        assert grade == "A"

    def test_grade_b_at_75(self):
        grade, _ = _compute_grade(75.0)
        assert grade == "B"

    def test_grade_b_between_75_and_90(self):
        grade, _ = _compute_grade(82.0)
        assert grade == "B"

    def test_grade_c_at_60(self):
        grade, _ = _compute_grade(60.0)
        assert grade == "C"

    def test_grade_c_between_60_and_75(self):
        grade, _ = _compute_grade(67.0)
        assert grade == "C"

    def test_grade_d_at_45(self):
        grade, _ = _compute_grade(45.0)
        assert grade == "D"

    def test_grade_d_between_45_and_60(self):
        grade, _ = _compute_grade(52.0)
        assert grade == "D"

    def test_grade_f_below_45(self):
        grade, _ = _compute_grade(44.9)
        assert grade == "F"

    def test_grade_f_at_zero(self):
        grade, _ = _compute_grade(0.0)
        assert grade == "F"

    def test_grade_boundary_89_is_b(self):
        """89.99 should be B (not A)."""
        grade, _ = _compute_grade(89.99)
        assert grade == "B"

    def test_grade_boundary_74_is_c(self):
        grade, _ = _compute_grade(74.99)
        assert grade == "C"


# ---------------------------------------------------------------------------
# Weighted score arithmetic
# ---------------------------------------------------------------------------

class TestWeightedScoreArithmetic:

    def _validate_clean_df(self) -> ValidationResult:
        """Return a ValidationResult from a perfectly clean dataset."""
        df = pd.DataFrame({
            "customer_id": ["C001", "C002", "C003"],
            "status":      ["active", "inactive", "active"],
            "score":       [50, 75, 90],
        })
        rules = [
            NotNullRule(name="id_nn", column="customer_id"),
            UniqueRule(name="id_unique", column="customer_id"),
            AllowedValuesRule(name="status_vals", column="status",
                              allowed_values={"active", "inactive", "pending"}),
            ValueRangeRule(name="score_range", column="score", min_val=0, max_val=100),
        ]
        validator = DQValidator(rules)
        return validator.validate(df, dataset_name="clean")

    def test_perfect_data_gets_near_100_score(self):
        """A clean dataset with all rules passing should score close to 100."""
        validation_result = self._validate_clean_df()
        scorer = DQScorer()
        scorecard = scorer.compute_scores(validation_result)

        assert scorecard.overall_score >= 95.0

    def test_perfect_data_gets_grade_a(self):
        validation_result = self._validate_clean_df()
        scorer = DQScorer()
        scorecard = scorer.compute_scores(validation_result)

        assert scorecard.overall_grade == "A"

    def test_dimension_weights_sum_to_1(self):
        """All dimension weights must sum to exactly 1.0."""
        total = sum(DIMENSION_WEIGHTS.values())
        assert abs(total - 1.0) < 1e-9

    def test_dimension_weights_are_positive(self):
        for dim, weight in DIMENSION_WEIGHTS.items():
            assert weight > 0, f"Weight for '{dim}' should be positive"

    def test_scorer_returns_scorecard(self):
        validation_result = self._validate_clean_df()
        scorer = DQScorer()
        scorecard = scorer.compute_scores(validation_result)

        assert isinstance(scorecard, DQScoreCard)

    def test_scorecard_has_all_dimensions(self):
        """Scorecard must have a DimensionScore entry for all 5 dimensions."""
        validation_result = self._validate_clean_df()
        scorer = DQScorer()
        scorecard = scorer.compute_scores(validation_result)

        for dim in ("completeness", "validity", "uniqueness", "consistency", "freshness"):
            assert dim in scorecard.dimension_scores, f"Missing dimension: {dim}"

    def test_scorecard_dataset_name_matches(self):
        validation_result = self._validate_clean_df()
        scorer = DQScorer()
        scorecard = scorer.compute_scores(validation_result)

        assert scorecard.dataset_name == "clean"

    def test_failed_completeness_lowers_score(self):
        """A column with NaN values should lower the completeness dimension score."""
        df = pd.DataFrame({
            "customer_id": [None, None, None, None, None],  # all null — badly failing
        })
        rules = [NotNullRule(name="id_nn", column="customer_id", severity="error")]
        validator = DQValidator(rules)
        validation_result = validator.validate(df)

        scorer = DQScorer()
        scorecard = scorer.compute_scores(validation_result)

        completeness_ds = scorecard.dimension_scores["completeness"]
        assert completeness_ds.score_0_to_100 < 50.0
        assert scorecard.overall_score < 90.0

    def test_weighted_contribution_calculation(self):
        """
        Manual check: for a single completeness rule with score=1.0,
        the completeness dimension's weighted_contribution should be
        weight * 1.0 = 0.30.
        """
        df = pd.DataFrame({"id": ["A", "B", "C"]})
        rules = [NotNullRule(name="id_nn", column="id")]
        validator = DQValidator(rules)
        validation_result = validator.validate(df)

        scorer = DQScorer()
        scorecard = scorer.compute_scores(validation_result)

        completeness_ds = scorecard.dimension_scores["completeness"]
        expected_contribution = DIMENSION_WEIGHTS["completeness"] * completeness_ds.score_0_to_1
        assert abs(completeness_ds.weighted_contribution - expected_contribution) < 1e-9

    def test_no_rules_for_dimension_defaults_to_100(self):
        """
        When no rules are configured for a dimension (e.g. freshness),
        that dimension should contribute as if score=1.0 (neutral — don't penalise).
        """
        df = pd.DataFrame({"id": ["A", "B"]})
        rules = [NotNullRule(name="id_nn", column="id")]  # completeness only
        validator = DQValidator(rules)
        validation_result = validator.validate(df)

        scorer = DQScorer()
        scorecard = scorer.compute_scores(validation_result)

        freshness_ds = scorecard.dimension_scores["freshness"]
        assert freshness_ds.score_0_to_100 == 100.0
        assert freshness_ds.rule_count == 0

    def test_to_dict_has_expected_keys(self):
        validation_result = self._validate_clean_df()
        scorer = DQScorer()
        scorecard = scorer.compute_scores(validation_result)
        d = scorecard.to_dict()

        for key in ("dataset_name", "overall_score", "overall_grade",
                    "total_rules", "passed_rules", "failed_rules", "dimensions"):
            assert key in d, f"Missing key in scorecard dict: {key}"

    def test_critical_issues_populated_on_error_failures(self):
        """critical_issues list should be non-empty when error-severity rules fail."""
        df = pd.DataFrame({"id": [None, None]})
        rules = [NotNullRule(name="id_nn", column="id", severity="error")]
        validator = DQValidator(rules)
        validation_result = validator.validate(df)

        scorer = DQScorer()
        scorecard = scorer.compute_scores(validation_result)

        assert len(scorecard.critical_issues) >= 1

    def test_to_json_is_valid_string(self):
        """to_json() should return a non-empty string."""
        import json
        validation_result = self._validate_clean_df()
        scorer = DQScorer()
        scorecard = scorer.compute_scores(validation_result)

        json_str = scorecard.to_json()
        assert isinstance(json_str, str)
        # Must be valid JSON
        parsed = json.loads(json_str)
        assert "overall_score" in parsed
