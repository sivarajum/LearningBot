"""
base_rule.py — Abstract base class for all DQ rules.

Design philosophy:
    Every rule in this framework follows the same contract:
        - Takes a DataFrame as input
        - Returns a RuleResult dataclass describing pass/fail, score, and counts
        - Is self-describing: carries name, column, severity, and dimension

    This mirrors enterprise DQ frameworks (Deequ, Great Expectations) but is
    implemented from scratch to demonstrate deep understanding of DQ mechanics.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

VALID_SEVERITIES = {"error", "warning", "info"}
VALID_DIMENSIONS = {"completeness", "validity", "uniqueness", "consistency", "freshness"}


@dataclass
class RuleResult:
    """
    Immutable result object produced by each rule's validate() call.

    Attributes:
        rule_name     : Human-readable rule identifier (e.g. "NotNullRule")
        column        : Column(s) the rule was applied to
        dimension     : DQ dimension (completeness / validity / uniqueness / consistency / freshness)
        severity      : error | warning | info
        passed        : True if rule passed overall (score == 1.0 or above threshold)
        score         : Continuous score 0.0–1.0 (e.g. 0.95 = 95% records pass)
        failing_count : Number of records that violated the rule
        total_count   : Total records evaluated
        pass_rate     : (total_count - failing_count) / total_count
        details       : Human-readable explanation of the result
        failing_values: Sample of values that failed (for debugging)
    """
    rule_name: str
    column: str
    dimension: str
    severity: str
    passed: bool
    score: float           # 0.0 to 1.0
    failing_count: int
    total_count: int
    pass_rate: float
    details: str
    failing_values: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rule_name": self.rule_name,
            "column": self.column,
            "dimension": self.dimension,
            "severity": self.severity,
            "passed": self.passed,
            "score": round(self.score, 4),
            "failing_count": self.failing_count,
            "total_count": self.total_count,
            "pass_rate": round(self.pass_rate, 4),
            "details": self.details,
            "failing_values": self.failing_values[:10],  # cap at 10 for display
        }


class BaseRule(ABC):
    """
    Abstract base for all DQ rules.

    Subclasses must implement validate(df) and return a RuleResult.
    The dimension property must be set by each rule category subclass.

    Usage:
        class MyRule(BaseRule):
            dimension = "validity"
            def validate(self, df): ...
    """

    dimension: str = "validity"  # override in each subclass

    def __init__(self, name: str, column: str, severity: str = "error"):
        if severity not in VALID_SEVERITIES:
            raise ValueError(f"severity must be one of {VALID_SEVERITIES}, got '{severity}'")
        self.name = name
        self.column = column
        self.severity = severity

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> RuleResult:
        """
        Run this rule against the given DataFrame.
        Must return a fully populated RuleResult.
        """
        pass

    def _check_column_exists(self, df: pd.DataFrame) -> Optional[RuleResult]:
        """Helper: return an error RuleResult if the column is missing from the DataFrame."""
        if self.column not in df.columns:
            return RuleResult(
                rule_name=self.name,
                column=self.column,
                dimension=self.dimension,
                severity=self.severity,
                passed=False,
                score=0.0,
                failing_count=len(df),
                total_count=len(df),
                pass_rate=0.0,
                details=f"Column '{self.column}' does not exist in the dataset.",
                failing_values=[],
            )
        return None

    def _build_result(
        self,
        df: pd.DataFrame,
        failing_mask: "pd.Series[bool]",
        details: str,
    ) -> RuleResult:
        """
        Convenience builder: given a boolean mask of failing rows, produce a RuleResult.
        failing_mask is True where a row FAILS the rule.
        """
        total = len(df)
        failing_count = int(failing_mask.sum())
        pass_rate = (total - failing_count) / total if total > 0 else 1.0
        score = pass_rate
        passed = failing_count == 0

        # Collect sample failing values for debugging
        failing_values = []
        if failing_count > 0 and self.column in df.columns:
            sample = df.loc[failing_mask, self.column].dropna().head(10).tolist()
            failing_values = [str(v) for v in sample]

        return RuleResult(
            rule_name=self.name,
            column=self.column,
            dimension=self.dimension,
            severity=self.severity,
            passed=passed,
            score=score,
            failing_count=failing_count,
            total_count=total,
            pass_rate=pass_rate,
            details=details,
            failing_values=failing_values,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, column={self.column!r}, severity={self.severity!r})"
