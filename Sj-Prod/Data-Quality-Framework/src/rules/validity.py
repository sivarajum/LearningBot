"""
validity.py — Rules that check whether data conforms to expected formats, ranges, and types.

DQ Dimension: Validity
    Validity answers: "Does the data conform to defined business rules?"
    Invalid data = wrong format, out-of-range, wrong type, bad categorical value.

    Real-world context:
        - PayPal: transaction amounts must be > 0 and <= 1,000,000
        - FedEx: tracking numbers must match a specific regex pattern
        - Customer emails failing regex = bounce rates, undeliverable marketing

Rules:
    RegexRule          — value must match a regular expression
    ValueRangeRule     — numeric value must be within [min_val, max_val]
    AllowedValuesRule  — value must be in a predefined set of allowed values
    TypeRule           — value must be castable to the expected Python type
"""

import logging
import re
from typing import Any, Optional, Set

import pandas as pd

from .base_rule import BaseRule, RuleResult

logger = logging.getLogger(__name__)


class RegexRule(BaseRule):
    """
    Asserts that non-null values in a column match a regular expression.

    Null values are skipped (use NotNullRule separately to catch nulls).
    Score = matching_count / non_null_count

    Args:
        pattern: Python regex string. Will be compiled once at init time.

    Example:
        RegexRule(
            name="email_format", column="email",
            pattern=r'^[^@]+@[^@]+[.][^@]+$', severity="warning"
        )
    """

    dimension = "validity"

    def __init__(self, name: str, column: str, pattern: str, severity: str = "error"):
        super().__init__(name=name, column=column, severity=severity)
        self.pattern = pattern
        try:
            self._compiled = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{pattern}': {e}")

    def validate(self, df: pd.DataFrame) -> RuleResult:
        missing = self._check_column_exists(df)
        if missing:
            return missing

        series = df[self.column].dropna().astype(str)
        total = len(df)

        if len(series) == 0:
            return RuleResult(
                rule_name=self.name, column=self.column, dimension=self.dimension,
                severity=self.severity, passed=True, score=1.0,
                failing_count=0, total_count=total, pass_rate=1.0,
                details=f"Column '{self.column}' is entirely null — regex not evaluated.",
            )

        non_null_mask = df[self.column].notna()
        str_series = df.loc[non_null_mask, self.column].astype(str)
        match_mask = str_series.str.match(self._compiled)
        failing_mask_among_nonnull = ~match_mask

        # Failing rows in the full df context
        failing_in_full = pd.Series(False, index=df.index)
        failing_in_full[str_series[failing_mask_among_nonnull].index] = True

        failing_count = int(failing_in_full.sum())
        pass_rate = (total - failing_count) / total if total > 0 else 1.0
        score = pass_rate
        passed = failing_count == 0

        failing_sample = str_series[failing_mask_among_nonnull].head(10).tolist()

        details = (
            f"Column '{self.column}' regex '{self.pattern}': "
            f"{failing_count} of {total} rows fail ({pass_rate * 100:.1f}% pass)."
        )

        return RuleResult(
            rule_name=self.name, column=self.column, dimension=self.dimension,
            severity=self.severity, passed=passed, score=score,
            failing_count=failing_count, total_count=total, pass_rate=pass_rate,
            details=details, failing_values=failing_sample,
        )


class ValueRangeRule(BaseRule):
    """
    Asserts that numeric values fall within [min_val, max_val] (inclusive).

    Null values are skipped. Use with NotNullRule if nulls should be caught too.
    Score = (rows within range) / (total rows)

    Args:
        min_val: Minimum acceptable value (inclusive). None = no lower bound.
        max_val: Maximum acceptable value (inclusive). None = no upper bound.

    Example:
        ValueRangeRule(
            name="age_range", column="age",
            min_val=0, max_val=120, severity="error"
        )
    """

    dimension = "validity"

    def __init__(
        self,
        name: str,
        column: str,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        severity: str = "error",
    ):
        super().__init__(name=name, column=column, severity=severity)
        if min_val is not None and max_val is not None and min_val > max_val:
            raise ValueError(f"min_val ({min_val}) must be <= max_val ({max_val})")
        self.min_val = min_val
        self.max_val = max_val

    def validate(self, df: pd.DataFrame) -> RuleResult:
        missing = self._check_column_exists(df)
        if missing:
            return missing

        total = len(df)
        non_null_mask = df[self.column].notna()
        numeric_series = pd.to_numeric(df.loc[non_null_mask, self.column], errors="coerce")

        # Rows that failed type coercion (non-numeric)
        coerce_fail = numeric_series.isna()
        valid_numeric = numeric_series.dropna()

        # Build range violation mask
        range_fail = pd.Series(False, index=valid_numeric.index)
        if self.min_val is not None:
            range_fail |= (valid_numeric < self.min_val)
        if self.max_val is not None:
            range_fail |= (valid_numeric > self.max_val)

        # Total failing = non-numeric + out of range
        failing_count = int(coerce_fail.sum()) + int(range_fail.sum())
        pass_rate = (total - failing_count) / total if total > 0 else 1.0
        score = pass_rate
        passed = failing_count == 0

        range_str = f"[{self.min_val if self.min_val is not None else '-inf'}, {self.max_val if self.max_val is not None else '+inf'}]"
        failing_values = [str(v) for v in df.loc[range_fail[range_fail].index, self.column].head(10).tolist()]

        details = (
            f"Column '{self.column}' range {range_str}: "
            f"{failing_count} of {total} rows fail ({pass_rate * 100:.1f}% pass)."
        )

        return RuleResult(
            rule_name=self.name, column=self.column, dimension=self.dimension,
            severity=self.severity, passed=passed, score=score,
            failing_count=failing_count, total_count=total, pass_rate=pass_rate,
            details=details, failing_values=failing_values,
        )


class AllowedValuesRule(BaseRule):
    """
    Asserts that all non-null values belong to a predefined set of allowed values.

    Use for status fields, category codes, flag columns.
    Score = (allowed values count) / (total count)

    Args:
        allowed_values: Set (or list) of acceptable values.

    Example:
        AllowedValuesRule(
            name="status_values", column="status",
            allowed_values={"active", "inactive", "pending"}, severity="error"
        )
    """

    dimension = "validity"

    def __init__(self, name: str, column: str, allowed_values: Set[Any], severity: str = "error"):
        super().__init__(name=name, column=column, severity=severity)
        self.allowed_values = set(allowed_values)

    def validate(self, df: pd.DataFrame) -> RuleResult:
        missing = self._check_column_exists(df)
        if missing:
            return missing

        total = len(df)
        non_null = df[self.column].dropna()

        # Convert allowed values to strings for comparison consistency
        allowed_str = {str(v) for v in self.allowed_values}
        value_strs = non_null.astype(str)

        failing_mask_nonnull = ~value_strs.isin(allowed_str)
        failing_count = int(failing_mask_nonnull.sum())
        pass_rate = (total - failing_count) / total if total > 0 else 1.0
        score = pass_rate
        passed = failing_count == 0

        failing_sample = non_null[failing_mask_nonnull].head(10).astype(str).tolist()
        allowed_preview = sorted([str(v) for v in self.allowed_values])[:10]

        details = (
            f"Column '{self.column}' allowed values {allowed_preview}: "
            f"{failing_count} of {total} rows fail ({pass_rate * 100:.1f}% pass)."
        )

        return RuleResult(
            rule_name=self.name, column=self.column, dimension=self.dimension,
            severity=self.severity, passed=passed, score=score,
            failing_count=failing_count, total_count=total, pass_rate=pass_rate,
            details=details, failing_values=failing_sample,
        )


class TypeRule(BaseRule):
    """
    Asserts that all non-null values in a column can be cast to the expected Python type.

    Supports: int, float, str, bool, and "date" (ISO 8601 format).
    Score = (castable count) / (total count)

    Args:
        expected_type: One of "int", "float", "str", "bool", "date".

    Example:
        TypeRule(
            name="age_is_int", column="age",
            expected_type="int", severity="error"
        )
    """

    dimension = "validity"
    SUPPORTED_TYPES = {"int", "float", "str", "bool", "date"}

    def __init__(self, name: str, column: str, expected_type: str, severity: str = "error"):
        super().__init__(name=name, column=column, severity=severity)
        if expected_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"expected_type must be one of {self.SUPPORTED_TYPES}, got '{expected_type}'")
        self.expected_type = expected_type

    def _can_cast(self, value: Any) -> bool:
        try:
            if self.expected_type == "int":
                int(float(str(value)))
            elif self.expected_type == "float":
                float(str(value))
            elif self.expected_type == "str":
                str(value)
            elif self.expected_type == "bool":
                if str(value).lower() not in {"true", "false", "1", "0", "yes", "no"}:
                    return False
            elif self.expected_type == "date":
                pd.to_datetime(str(value))
            return True
        except (ValueError, TypeError):
            return False

    def validate(self, df: pd.DataFrame) -> RuleResult:
        missing = self._check_column_exists(df)
        if missing:
            return missing

        total = len(df)
        non_null_mask = df[self.column].notna()
        non_null_series = df.loc[non_null_mask, self.column]

        cast_results = non_null_series.apply(self._can_cast)
        failing_mask_nonnull = ~cast_results

        failing_count = int(failing_mask_nonnull.sum())
        pass_rate = (total - failing_count) / total if total > 0 else 1.0
        score = pass_rate
        passed = failing_count == 0

        failing_sample = non_null_series[failing_mask_nonnull].head(10).astype(str).tolist()

        details = (
            f"Column '{self.column}' type check (expected: {self.expected_type}): "
            f"{failing_count} of {total} rows cannot be cast ({pass_rate * 100:.1f}% pass)."
        )

        return RuleResult(
            rule_name=self.name, column=self.column, dimension=self.dimension,
            severity=self.severity, passed=passed, score=score,
            failing_count=failing_count, total_count=total, pass_rate=pass_rate,
            details=details, failing_values=failing_sample,
        )
