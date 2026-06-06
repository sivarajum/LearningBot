"""
validator.py — Orchestrates rule execution against a dataset.

The DQValidator is the "engine" of the framework:
    1. Receives a list of BaseRule objects
    2. Runs each rule against the DataFrame
    3. Collects all RuleResult objects
    4. Returns a ValidationResult summary

Design choices:
    - Rules run sequentially (simple, debuggable)
    - Each rule is independent — one failing rule doesn't stop others
    - Errors within a single rule are caught and reported without crashing
    - ValidationResult is a rich object with full audit trail

Real-world parallel:
    - Great Expectations: Checkpoint.run()
    - Deequ: VerificationSuite.onData().run()
    - This custom version: DQValidator.validate()
"""

import logging
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List

import pandas as pd

from .rules.base_rule import BaseRule, RuleResult

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """
    Complete result of running all rules against a single dataset.

    Attributes:
        dataset_name    : Name of the dataset that was validated
        validated_at    : ISO 8601 timestamp
        row_count       : Number of rows in the DataFrame
        total_rules     : Total rules run
        passed_rules    : Rules that fully passed
        failed_rules    : Rules that had at least one violation
        error_rules     : Rules that threw exceptions during execution
        results         : All individual RuleResult objects
        summary_by_dim  : Per-dimension pass/fail counts
        overall_passed  : True if all error-severity rules passed
    """
    dataset_name: str
    validated_at: str
    row_count: int
    total_rules: int
    passed_rules: int
    failed_rules: int
    error_rules: int
    results: List[RuleResult]
    summary_by_dim: Dict[str, Dict]
    overall_passed: bool

    def to_dict(self) -> dict:
        return {
            "dataset_name": self.dataset_name,
            "validated_at": self.validated_at,
            "row_count": self.row_count,
            "total_rules": self.total_rules,
            "passed_rules": self.passed_rules,
            "failed_rules": self.failed_rules,
            "error_rules": self.error_rules,
            "overall_passed": self.overall_passed,
            "summary_by_dimension": self.summary_by_dim,
            "rule_results": [r.to_dict() for r in self.results],
        }

    def failed_results(self) -> List[RuleResult]:
        """Return only the rules that failed."""
        return [r for r in self.results if not r.passed]

    def results_by_severity(self, severity: str) -> List[RuleResult]:
        """Filter results by severity level."""
        return [r for r in self.results if r.severity == severity]

    def critical_failures(self) -> List[RuleResult]:
        """Error-severity rules that failed — the ones that block pipeline."""
        return [r for r in self.results if r.severity == "error" and not r.passed]

    def print_summary(self) -> None:
        """Log a formatted validation summary."""
        status = "PASSED" if self.overall_passed else "FAILED"
        lines = [
            f"\n{'='*70}",
            f"  DQ Validation: {self.dataset_name}  --  {status}",
            f"{'='*70}",
            f"  Validated at : {self.validated_at}",
            f"  Rows         : {self.row_count:,}",
            f"  Rules run    : {self.total_rules}",
            f"  Passed       : {self.passed_rules}",
            f"  Failed       : {self.failed_rules}",
            f"  Errors       : {self.error_rules}",
            f"{'='*70}",
        ]

        if self.failed_rules > 0:
            lines.append("\n  FAILURES:")
            for r in self.failed_results():
                icon = {"error": "[ERR]", "warning": "[WRN]", "info": "[INF]"}.get(r.severity, "[???]")
                lines.append(
                    f"    {icon} [{r.dimension.upper():<13}] {r.rule_name:<40} "
                    f"score={r.score:.3f}  failing={r.failing_count}/{r.total_count}"
                )
                lines.append(f"         {r.details}")
        logger.info("\n".join(lines))


class DQValidator:
    """
    Runs a collection of DQ rules against a DataFrame and returns a ValidationResult.

    Usage:
        rules = [
            NotNullRule("id_not_null", "customer_id"),
            UniqueRule("id_unique", "customer_id"),
            RegexRule("email_fmt", "email", r'^[^@]+@[^@]+\\.[^@]+$'),
        ]
        validator = DQValidator(rules)
        result = validator.validate(df, dataset_name="customers")
        result.print_summary()

    Args:
        rules: List of BaseRule instances to run.
    """

    def __init__(self, rules: List[BaseRule]):
        if not rules:
            raise ValueError("DQValidator requires at least one rule.")
        self.rules = rules

    def validate(self, df: pd.DataFrame, dataset_name: str = "dataset") -> ValidationResult:
        """
        Execute all rules against the DataFrame.

        Args:
            df:           DataFrame to validate.
            dataset_name: Logical name of the dataset (used in reporting).

        Returns:
            ValidationResult with all rule results and summary statistics.
        """
        validated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        row_count = len(df)

        results: List[RuleResult] = []
        passed_count = 0
        failed_count = 0
        error_count = 0

        for rule in self.rules:
            try:
                result = rule.validate(df)
                results.append(result)
                if result.passed:
                    passed_count += 1
                else:
                    failed_count += 1
            except (ValueError, TypeError, KeyError, RuntimeError, AttributeError) as exc:
                # Rule threw an exception — record it as a failed rule
                logger.error("Rule '%s' raised %s: %s", rule.name, type(exc).__name__, exc)
                error_count += 1
                error_result = RuleResult(
                    rule_name=rule.name,
                    column=rule.column,
                    dimension=getattr(rule, "dimension", "unknown"),
                    severity=rule.severity,
                    passed=False,
                    score=0.0,
                    failing_count=row_count,
                    total_count=row_count,
                    pass_rate=0.0,
                    details=f"Rule execution error: {exc}\n{traceback.format_exc()}",
                    failing_values=[],
                )
                results.append(error_result)
                failed_count += 1

        # Summarise by dimension
        summary_by_dim = self._summarise_by_dimension(results)

        # overall_passed = True only if no error-severity rules failed
        critical_failures = [r for r in results if r.severity == "error" and not r.passed]
        overall_passed = len(critical_failures) == 0

        return ValidationResult(
            dataset_name=dataset_name,
            validated_at=validated_at,
            row_count=row_count,
            total_rules=len(self.rules),
            passed_rules=passed_count,
            failed_rules=failed_count,
            error_rules=error_count,
            results=results,
            summary_by_dim=summary_by_dim,
            overall_passed=overall_passed,
        )

    @staticmethod
    def _summarise_by_dimension(results: List[RuleResult]) -> Dict[str, Dict]:
        """Aggregate pass/fail counts and average score per DQ dimension."""
        dimensions = ["completeness", "validity", "uniqueness", "consistency", "freshness"]
        summary = {}

        for dim in dimensions:
            dim_results = [r for r in results if r.dimension == dim]
            if not dim_results:
                summary[dim] = {
                    "total_rules": 0,
                    "passed": 0,
                    "failed": 0,
                    "avg_score": None,
                }
                continue

            passed = sum(1 for r in dim_results if r.passed)
            failed = len(dim_results) - passed
            avg_score = sum(r.score for r in dim_results) / len(dim_results)

            summary[dim] = {
                "total_rules": len(dim_results),
                "passed": passed,
                "failed": failed,
                "avg_score": round(avg_score, 4),
            }

        return summary
