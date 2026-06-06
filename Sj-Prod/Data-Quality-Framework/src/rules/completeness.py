"""
completeness.py — Rules that measure whether data is present (not null / not empty).

DQ Dimension: Completeness
    Completeness answers the question: "Is all required data present?"
    Low completeness = missing values, nulls, empty strings.

    Real-world context:
        - At PayPal: transaction records with null merchant_id caused settlement failures
        - At FedEx: null delivery_zip_code made routing impossible

Rules:
    NotNullRule            — zero nulls allowed (strict)
    CompletenessRatioRule  — null rate must be <= threshold (lenient, percentage-based)
"""

import logging

import pandas as pd

from .base_rule import BaseRule, RuleResult

logger = logging.getLogger(__name__)


class NotNullRule(BaseRule):
    """
    Asserts that a column contains NO null values.

    Use for mandatory fields: primary keys, foreign keys, required identifiers.
    Score = (non-null count) / (total count)

    Example:
        NotNullRule(name="customer_id_not_null", column="customer_id", severity="error")
    """

    dimension = "completeness"

    def __init__(self, name: str, column: str, severity: str = "error"):
        super().__init__(name=name, column=column, severity=severity)

    def validate(self, df: pd.DataFrame) -> RuleResult:
        missing = self._check_column_exists(df)
        if missing:
            return missing

        series = df[self.column]
        # Treat empty strings as nulls too
        null_mask = series.isna() | (series.astype(str).str.strip() == "")
        null_count = int(null_mask.sum())
        total = len(df)
        pass_rate = (total - null_count) / total if total > 0 else 1.0

        details = (
            f"Column '{self.column}' has {null_count} null/empty values out of {total} rows "
            f"({pass_rate * 100:.1f}% complete)."
        )

        return RuleResult(
            rule_name=self.name,
            column=self.column,
            dimension=self.dimension,
            severity=self.severity,
            passed=(null_count == 0),
            score=pass_rate,
            failing_count=null_count,
            total_count=total,
            pass_rate=pass_rate,
            details=details,
            failing_values=[],
        )


class CompletenessRatioRule(BaseRule):
    """
    Asserts that null rate is at or below a configurable threshold.

    More lenient than NotNullRule — allows a defined acceptable null %.
    Score = 1.0 if null_rate <= threshold, else proportional.

    Args:
        threshold: Maximum acceptable null rate (0.0–1.0). Default 0.05 (5%).

    Example:
        CompletenessRatioRule(
            name="phone_completeness", column="phone_number",
            threshold=0.10, severity="warning"
        )
        # Passes if <= 10% of phone numbers are null
    """

    dimension = "completeness"

    def __init__(self, name: str, column: str, threshold: float = 0.05, severity: str = "warning"):
        super().__init__(name=name, column=column, severity=severity)
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"threshold must be between 0.0 and 1.0, got {threshold}")
        self.threshold = threshold

    def validate(self, df: pd.DataFrame) -> RuleResult:
        missing = self._check_column_exists(df)
        if missing:
            return missing

        series = df[self.column]
        null_mask = series.isna() | (series.astype(str).str.strip() == "")
        null_count = int(null_mask.sum())
        total = len(df)
        null_rate = null_count / total if total > 0 else 0.0
        pass_rate = 1.0 - null_rate
        passed = null_rate <= self.threshold

        # Score: 1.0 if within threshold, else penalise proportionally
        if passed:
            score = 1.0
        else:
            # How much over threshold? Penalise proportionally
            over_by = null_rate - self.threshold
            score = max(0.0, 1.0 - (over_by / (1.0 - self.threshold + 1e-9)))

        details = (
            f"Column '{self.column}' null rate is {null_rate * 100:.2f}% "
            f"(threshold: {self.threshold * 100:.1f}%). "
            f"{'PASSED' if passed else 'FAILED'} — {null_count} nulls in {total} rows."
        )

        return RuleResult(
            rule_name=self.name,
            column=self.column,
            dimension=self.dimension,
            severity=self.severity,
            passed=passed,
            score=score,
            failing_count=null_count,
            total_count=total,
            pass_rate=pass_rate,
            details=details,
            failing_values=[],
        )
