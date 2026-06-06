"""
uniqueness.py — Rules that check for duplicate or low-cardinality values.

DQ Dimension: Uniqueness
    Uniqueness answers: "Are records distinct where they should be?"
    Low uniqueness = duplicate keys, repeated records, low-cardinality identifiers.

    Real-world context:
        - PayPal: duplicate transaction_id = double-posting / accounting errors
        - FedEx: duplicate tracking_number = package mis-routing
        - Customer tables: duplicate email = split profiles, incorrect marketing

Rules:
    UniqueRule            — column must have NO duplicate values (strict, for PK/IDs)
    UniquenessRatioRule   — distinct / total >= threshold (for fields that should be "mostly" unique)
"""

import logging

import pandas as pd

from .base_rule import BaseRule, RuleResult

logger = logging.getLogger(__name__)


class UniqueRule(BaseRule):
    """
    Asserts that a column contains no duplicate values.

    Null values are excluded from uniqueness checks (handled by NotNullRule).
    Score = (distinct non-null count) / (non-null count)

    Use for: primary keys, transaction IDs, order numbers.

    Example:
        UniqueRule(name="customer_id_unique", column="customer_id", severity="error")
    """

    dimension = "uniqueness"

    def __init__(self, name: str, column: str, severity: str = "error"):
        super().__init__(name=name, column=column, severity=severity)

    def validate(self, df: pd.DataFrame) -> RuleResult:
        missing = self._check_column_exists(df)
        if missing:
            return missing

        total = len(df)
        non_null = df[self.column].dropna()
        non_null_count = len(non_null)

        if non_null_count == 0:
            return RuleResult(
                rule_name=self.name, column=self.column, dimension=self.dimension,
                severity=self.severity, passed=True, score=1.0,
                failing_count=0, total_count=total, pass_rate=1.0,
                details=f"Column '{self.column}' has no non-null values to check uniqueness.",
            )

        # Total rows that are duplicates (all occurrences beyond the first)
        dup_mask = non_null.duplicated(keep="first")
        failing_count = int(dup_mask.sum())

        pass_rate = (total - failing_count) / total if total > 0 else 1.0
        score = pass_rate
        passed = failing_count == 0

        dup_sample = non_null[dup_mask].head(10).astype(str).tolist()
        unique_count = non_null.nunique()
        uniqueness_rate = unique_count / non_null_count if non_null_count > 0 else 1.0

        details = (
            f"Column '{self.column}' uniqueness: {unique_count} distinct values in "
            f"{non_null_count} non-null rows (uniqueness rate: {uniqueness_rate * 100:.1f}%). "
            f"{failing_count} duplicate rows found."
        )

        return RuleResult(
            rule_name=self.name, column=self.column, dimension=self.dimension,
            severity=self.severity, passed=passed, score=score,
            failing_count=failing_count, total_count=total, pass_rate=pass_rate,
            details=details, failing_values=dup_sample,
        )


class UniquenessRatioRule(BaseRule):
    """
    Asserts that the ratio (distinct count / non-null count) >= threshold.

    More lenient than UniqueRule — accepts near-unique fields.
    Score: 1.0 if ratio >= threshold, penalised proportionally below threshold.

    Args:
        threshold: Minimum acceptable uniqueness ratio (0.0–1.0). Default 0.95.

    Example:
        UniquenessRatioRule(
            name="email_mostly_unique", column="email",
            threshold=0.95, severity="warning"
        )
        # Passes if >= 95% of emails are unique
    """

    dimension = "uniqueness"

    def __init__(self, name: str, column: str, threshold: float = 0.95, severity: str = "warning"):
        super().__init__(name=name, column=column, severity=severity)
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"threshold must be between 0.0 and 1.0, got {threshold}")
        self.threshold = threshold

    def validate(self, df: pd.DataFrame) -> RuleResult:
        missing = self._check_column_exists(df)
        if missing:
            return missing

        total = len(df)
        non_null = df[self.column].dropna()
        non_null_count = len(non_null)

        if non_null_count == 0:
            return RuleResult(
                rule_name=self.name, column=self.column, dimension=self.dimension,
                severity=self.severity, passed=True, score=1.0,
                failing_count=0, total_count=total, pass_rate=1.0,
                details=f"Column '{self.column}' has no non-null values to check uniqueness ratio.",
            )

        unique_count = non_null.nunique()
        uniqueness_ratio = unique_count / non_null_count
        passed = uniqueness_ratio >= self.threshold

        # Score: proportional within [0, threshold]
        score = min(1.0, uniqueness_ratio / self.threshold) if self.threshold > 0 else 1.0

        # "Failing" rows = approximate duplicates (all dup rows beyond first occurrence)
        dup_mask = non_null.duplicated(keep="first")
        failing_count = int(dup_mask.sum())
        pass_rate = (total - failing_count) / total if total > 0 else 1.0

        details = (
            f"Column '{self.column}' uniqueness ratio: {uniqueness_ratio * 100:.1f}% "
            f"(threshold: {self.threshold * 100:.1f}%). "
            f"{unique_count} distinct / {non_null_count} non-null. "
            f"{'PASSED' if passed else 'FAILED'}."
        )

        return RuleResult(
            rule_name=self.name, column=self.column, dimension=self.dimension,
            severity=self.severity, passed=passed, score=score,
            failing_count=failing_count, total_count=total, pass_rate=pass_rate,
            details=details, failing_values=[],
        )
