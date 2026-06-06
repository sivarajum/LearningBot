"""
consistency.py — Rules that check internal consistency and referential integrity.

DQ Dimension: Consistency
    Consistency answers: "Is data logically coherent within and across datasets?"
    Inconsistent data = orphaned foreign keys, logical contradictions (end < start),
    cross-system mismatches.

    Real-world context:
        - PayPal: transaction.customer_id not in customer table = orphaned transactions
        - FedEx: shipment.delivery_date < shipment.pickup_date = impossible timeline
        - Cross-system: same entity has conflicting attributes in two source systems

Rules:
    ReferentialIntegrityRule — all values in a column must exist in a reference set
    CrossColumnRule          — logical comparison between two columns (e.g. end >= start)
"""

import logging
import operator
from typing import Any, Set

import pandas as pd

from .base_rule import BaseRule, RuleResult

logger = logging.getLogger(__name__)

# Supported operators for CrossColumnRule
OPERATORS = {
    ">=": operator.ge,
    "<=": operator.le,
    ">":  operator.gt,
    "<":  operator.lt,
    "==": operator.eq,
    "!=": operator.ne,
}


class ReferentialIntegrityRule(BaseRule):
    """
    Asserts that all non-null values in column_a exist in a reference set.

    Models a foreign-key constraint without requiring an actual database.
    The reference set can be populated from another DataFrame's column at runtime.

    Args:
        reference_values: Set of valid values. Can be IDs from another table.

    Example:
        # Ensure every transaction.customer_id exists in the customers table
        valid_ids = set(customers_df["customer_id"].dropna())
        ReferentialIntegrityRule(
            name="txn_customer_ref", column="customer_id",
            reference_values=valid_ids, severity="error"
        )
    """

    dimension = "consistency"

    def __init__(
        self,
        name: str,
        column: str,
        reference_values: Set[Any],
        severity: str = "error",
    ):
        super().__init__(name=name, column=column, severity=severity)
        # Normalise to strings for safe cross-type comparison
        self.reference_values = {str(v) for v in reference_values}

    def validate(self, df: pd.DataFrame) -> RuleResult:
        missing = self._check_column_exists(df)
        if missing:
            return missing

        total = len(df)
        non_null_mask = df[self.column].notna()
        non_null_series = df.loc[non_null_mask, self.column].astype(str)

        orphan_mask = ~non_null_series.isin(self.reference_values)
        failing_count = int(orphan_mask.sum())
        pass_rate = (total - failing_count) / total if total > 0 else 1.0
        score = pass_rate
        passed = failing_count == 0

        orphan_sample = non_null_series[orphan_mask].head(10).tolist()

        details = (
            f"Column '{self.column}' referential integrity: "
            f"{failing_count} of {total} rows reference values not in the reference set "
            f"({pass_rate * 100:.1f}% valid). "
            f"Reference set size: {len(self.reference_values)}."
        )

        return RuleResult(
            rule_name=self.name, column=self.column, dimension=self.dimension,
            severity=self.severity, passed=passed, score=score,
            failing_count=failing_count, total_count=total, pass_rate=pass_rate,
            details=details, failing_values=orphan_sample,
        )


class CrossColumnRule(BaseRule):
    """
    Asserts a logical comparison between two columns in the same row.

    Evaluates: column_a  <operator>  column_b
    where operator is one of: >=, <=, >, <, ==, !=

    Useful for temporal assertions (end_date >= start_date), financial
    assertions (credit_amount >= debit_amount), etc.

    Args:
        column_b:  The right-hand column for the comparison.
        operator:  One of ">=", "<=", ">", "<", "==", "!=".

    Example:
        CrossColumnRule(
            name="end_after_start",
            column="end_date",
            column_b="start_date",
            operator=">=",
            severity="error"
        )
        # Asserts: every row where end_date >= start_date
    """

    dimension = "consistency"

    def __init__(
        self,
        name: str,
        column: str,
        column_b: str,
        operator: str,
        severity: str = "error",
    ):
        super().__init__(name=name, column=column, severity=severity)
        if operator not in OPERATORS:
            raise ValueError(f"operator must be one of {list(OPERATORS.keys())}, got '{operator}'")
        self.column_b = column_b
        self.operator_str = operator
        self._op_func = OPERATORS[operator]

    def validate(self, df: pd.DataFrame) -> RuleResult:
        # Check both columns exist
        for col in [self.column, self.column_b]:
            if col not in df.columns:
                return RuleResult(
                    rule_name=self.name, column=self.column, dimension=self.dimension,
                    severity=self.severity, passed=False, score=0.0,
                    failing_count=len(df), total_count=len(df), pass_rate=0.0,
                    details=f"Column '{col}' does not exist in the dataset.",
                )

        total = len(df)

        # Only evaluate rows where BOTH columns are non-null
        both_present = df[self.column].notna() & df[df.columns.intersection([self.column_b])].notna().all(axis=1)
        # Simpler: check column_b directly
        both_present = df[self.column].notna() & df[self.column_b].notna()
        subset = df[both_present]
        skipped = total - len(subset)

        if len(subset) == 0:
            return RuleResult(
                rule_name=self.name, column=self.column, dimension=self.dimension,
                severity=self.severity, passed=True, score=1.0,
                failing_count=0, total_count=total, pass_rate=1.0,
                details=f"No rows with both '{self.column}' and '{self.column_b}' non-null.",
            )

        # Try numeric comparison first, then fall back to direct comparison
        try:
            col_a_vals = pd.to_numeric(subset[self.column], errors="raise")
            col_b_vals = pd.to_numeric(subset[self.column_b], errors="raise")
        except (ValueError, TypeError):
            # Try datetime
            try:
                col_a_vals = pd.to_datetime(subset[self.column], errors="raise")
                col_b_vals = pd.to_datetime(subset[self.column_b], errors="raise")
            except (ValueError, TypeError):
                # Fall back to raw values
                col_a_vals = subset[self.column]
                col_b_vals = subset[self.column_b]

        try:
            comparison_result = self._op_func(col_a_vals, col_b_vals)
            failing_in_subset = ~comparison_result
            failing_count = int(failing_in_subset.sum())
        except (ValueError, TypeError, KeyError) as e:
            logger.error(
                "Could not compare '%s' %s '%s': %s", self.column, self.operator_str, self.column_b, e
            )
            return RuleResult(
                rule_name=self.name, column=self.column, dimension=self.dimension,
                severity=self.severity, passed=False, score=0.0,
                failing_count=0, total_count=total, pass_rate=0.0,
                details=f"Could not compare '{self.column}' {self.operator_str} '{self.column_b}': {e}",
            )

        pass_rate = (total - failing_count) / total if total > 0 else 1.0
        score = pass_rate
        passed = failing_count == 0

        failing_idx = subset[failing_in_subset].index
        failing_sample = [
            f"{self.column}={row[self.column]}, {self.column_b}={row[self.column_b]}"
            for _, row in df.loc[failing_idx[:10]].iterrows()
        ]

        details = (
            f"Cross-column check '{self.column}' {self.operator_str} '{self.column_b}': "
            f"{failing_count} violations in {total} rows "
            f"({pass_rate * 100:.1f}% pass). "
            f"{skipped} rows skipped due to nulls."
        )

        return RuleResult(
            rule_name=self.name, column=self.column, dimension=self.dimension,
            severity=self.severity, passed=passed, score=score,
            failing_count=failing_count, total_count=total, pass_rate=pass_rate,
            details=details, failing_values=failing_sample,
        )
