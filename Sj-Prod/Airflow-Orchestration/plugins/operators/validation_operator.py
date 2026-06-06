"""
Custom Operator: DataValidationOperator
=======================================
Demonstrates how to write a reusable custom Airflow operator.

Why custom operators?
  When a DQ check pattern repeats across many DAGs, packaging it as a
  custom operator:
  - Eliminates duplication
  - Centralises behaviour and testing
  - Allows non-engineers to use it declaratively in DAG files

Usage in a DAG:
    from plugins.operators.validation_operator import DataValidationOperator

    t_validate = DataValidationOperator(
        task_id="validate_transactions",
        table="fact_transactions",
        connection_id="postgres_dw",
        checks=[
            {"type": "not_null", "column": "txn_id", "threshold": 0.0},
            {"type": "row_count_min", "threshold": 100},
            {"type": "value_range", "column": "amount", "min": 0, "max": 1_000_000},
            {"type": "freshness", "column": "created_at", "max_age_hours": 2},
        ],
        fail_on_error=True,
    )

Architecture notes:
- Inherits from BaseOperator
- Overrides execute(context) — the single method Airflow calls
- Uses XCom.set() internally (accessed via context["ti"])
- Separates check logic into _run_check() for testability
- Returns a dict that Airflow automatically stores as an XCom return value
"""

import logging
import random
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Airflow imports — graceful fallback so operator is importable without Airflow
# ---------------------------------------------------------------------------
try:
    from airflow.models.baseoperator import BaseOperator
    from airflow.utils.decorators import apply_defaults
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False

    def apply_defaults(func):
        """No-op decorator when Airflow is not installed."""
        return func

    class BaseOperator:
        """Minimal stub that mimics the interface the operator needs."""

        ui_color = "#e8f5e9"
        ui_fgcolor = "#1b5e20"

        def __init__(self, task_id: str = "", *args, **kwargs):
            self.task_id = task_id
            # Absorb standard Airflow kwargs silently
            for key in ("dag", "owner", "retries", "retry_delay", "sla",
                        "email", "email_on_failure", "email_on_retry",
                        "depends_on_past", "execution_timeout"):
                kwargs.pop(key, None)

        def execute(self, context: dict) -> Any:
            raise NotImplementedError

        def __rshift__(self, other):
            return other

        def __lshift__(self, other):
            return other


# ---------------------------------------------------------------------------
# Supported check type constants
# ---------------------------------------------------------------------------
CHECK_NOT_NULL = "not_null"
CHECK_ROW_COUNT_MIN = "row_count_min"
CHECK_ROW_COUNT_MAX = "row_count_max"
CHECK_VALUE_RANGE = "value_range"
CHECK_FRESHNESS = "freshness"
CHECK_UNIQUE = "unique"
CHECK_REGEX = "regex"
CHECK_REFERENTIAL = "referential_integrity"


class DataValidationOperator(BaseOperator):
    """
    Custom operator that runs a configurable suite of data quality checks
    against a table and pushes a detailed report to XCom.

    Parameters
    ----------
    table : str
        Target table to validate (schema.table or just table).
    connection_id : str
        Airflow connection ID for the database.  Not used in simulator mode.
    checks : list[dict]
        List of check definitions.  Each dict must have a "type" key.
        See CHECK_* constants above for supported types.
    fail_on_error : bool
        If True (default), raise an AirflowException on any check failure.
        If False, only log warnings — useful for non-blocking quality monitoring.
    xcom_key : str
        XCom key to use when pushing the validation report.

    Template fields:
        table — can be a Jinja template, e.g. "{{ params.table }}"
    """

    # Jinja-templateable fields
    template_fields = ("table",)

    # UI colour in Airflow Graph View
    ui_color = "#fff9c4"
    ui_fgcolor = "#f57f17"

    @apply_defaults
    def __init__(
        self,
        table: str,
        connection_id: str = "postgres_default",
        checks: Optional[List[Dict]] = None,
        fail_on_error: bool = True,
        xcom_key: str = "validation_report",
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.table = table
        self.connection_id = connection_id
        self.checks = checks or []
        self.fail_on_error = fail_on_error
        self.xcom_key = xcom_key

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def execute(self, context: dict) -> Dict:
        """
        Run all configured checks against self.table.

        Returns a validation report dict and pushes it to XCom.
        Raises ValueError if any check fails and fail_on_error=True.
        """
        logger.info(
            "DataValidationOperator: starting %d checks on table '%s' (conn=%s)",
            len(self.checks), self.table, self.connection_id,
        )

        report = {
            "table": self.table,
            "connection_id": self.connection_id,
            "check_count": len(self.checks),
            "results": [],
            "passed": 0,
            "failed": 0,
            "errors": [],
            "validated_at": datetime.now(UTC).isoformat(),
        }

        for check_def in self.checks:
            result = self._run_check(check_def)
            report["results"].append(result)
            if result["passed"]:
                report["passed"] += 1
            else:
                report["failed"] += 1
                report["errors"].append(
                    f"[{check_def.get('type')}] {result.get('message', 'failed')}"
                )

        report["overall_passed"] = report["failed"] == 0
        report["pass_rate"] = (
            round(report["passed"] / report["check_count"] * 100, 1)
            if report["check_count"] else 0.0
        )

        # Push to XCom
        ti = context.get("ti")
        if ti:
            ti.xcom_push(key=self.xcom_key, value=report)

        log_fn = logger.info if report["overall_passed"] else logger.error
        log_fn(
            "Validation complete: %d/%d checks passed (%.1f%%) on '%s'",
            report["passed"], report["check_count"], report["pass_rate"], self.table,
        )

        if not report["overall_passed"] and self.fail_on_error:
            raise ValueError(
                f"DataValidationOperator: {report['failed']} check(s) failed on "
                f"'{self.table}': {report['errors']}"
            )

        return report

    # ------------------------------------------------------------------
    # Individual check runners
    # ------------------------------------------------------------------

    def _run_check(self, check_def: Dict) -> Dict:
        """
        Dispatch to the appropriate check method based on check_def["type"].

        Returns a result dict with: type, passed, value, threshold, message.
        """
        check_type = check_def.get("type")
        dispatch = {
            CHECK_NOT_NULL: self._check_not_null,
            CHECK_ROW_COUNT_MIN: self._check_row_count_min,
            CHECK_ROW_COUNT_MAX: self._check_row_count_max,
            CHECK_VALUE_RANGE: self._check_value_range,
            CHECK_FRESHNESS: self._check_freshness,
            CHECK_UNIQUE: self._check_unique,
            CHECK_REGEX: self._check_regex,
            CHECK_REFERENTIAL: self._check_referential,
        }

        handler = dispatch.get(check_type)
        if handler is None:
            return {
                "type": check_type,
                "passed": False,
                "message": f"Unknown check type: '{check_type}'",
            }

        try:
            return handler(check_def)
        except (ValueError, TypeError, KeyError, ArithmeticError, AttributeError) as exc:
            logger.exception("Check '%s' raised an exception: %s", check_type, exc)
            return {
                "type": check_type,
                "passed": False,
                "message": f"Exception during check: {exc}",
            }

    def _check_not_null(self, check_def: Dict) -> Dict:
        """Verify null rate for a column is below threshold."""
        column = check_def.get("column", "unknown")
        threshold = check_def.get("threshold", 0.01)    # default 1 %

        # Simulate: query COUNT(*) WHERE column IS NULL / COUNT(*)
        null_rate = round(random.uniform(0, 0.008), 4)
        passed = null_rate <= threshold

        return {
            "type": CHECK_NOT_NULL,
            "column": column,
            "passed": passed,
            "null_rate": null_rate,
            "threshold": threshold,
            "message": f"column='{column}' null_rate={null_rate:.4f} threshold={threshold}",
        }

    def _check_row_count_min(self, check_def: Dict) -> Dict:
        """Verify table has at least `threshold` rows."""
        threshold = check_def.get("threshold", 1)

        # Simulate: SELECT COUNT(*) FROM table
        row_count = 1000 + random.randint(0, 9000)
        passed = row_count >= threshold

        return {
            "type": CHECK_ROW_COUNT_MIN,
            "passed": passed,
            "row_count": row_count,
            "threshold": threshold,
            "message": f"row_count={row_count} >= min={threshold}: {'OK' if passed else 'FAIL'}",
        }

    def _check_row_count_max(self, check_def: Dict) -> Dict:
        """Verify table does not exceed `threshold` rows (anomaly detection)."""
        threshold = check_def.get("threshold", 10_000_000)

        row_count = 1000 + random.randint(0, 9000)
        passed = row_count <= threshold

        return {
            "type": CHECK_ROW_COUNT_MAX,
            "passed": passed,
            "row_count": row_count,
            "threshold": threshold,
            "message": f"row_count={row_count} <= max={threshold}: {'OK' if passed else 'FAIL'}",
        }

    def _check_value_range(self, check_def: Dict) -> Dict:
        """Verify all values in `column` fall within [min, max]."""
        column = check_def.get("column", "unknown")
        min_val = check_def.get("min")
        max_val = check_def.get("max")

        # Simulate: SELECT COUNT(*) WHERE column < min OR column > max
        out_of_range = random.randint(0, 5)
        total_rows = 10000
        pass_rate = round((total_rows - out_of_range) / total_rows, 4)
        passed = out_of_range == 0

        return {
            "type": CHECK_VALUE_RANGE,
            "column": column,
            "passed": passed,
            "out_of_range_count": out_of_range,
            "pass_rate": pass_rate,
            "min": min_val,
            "max": max_val,
            "message": (
                f"column='{column}' range=[{min_val},{max_val}] "
                f"out_of_range={out_of_range}: {'OK' if passed else 'FAIL'}"
            ),
        }

    def _check_freshness(self, check_def: Dict) -> Dict:
        """Verify max timestamp in `column` is within `max_age_hours`."""
        column = check_def.get("column", "created_at")
        max_age_hours = check_def.get("max_age_hours", 24)

        # Simulate: SELECT MAX(column) FROM table
        age_hours = round(random.uniform(0.1, 3.0), 2)
        passed = age_hours <= max_age_hours

        return {
            "type": CHECK_FRESHNESS,
            "column": column,
            "passed": passed,
            "actual_age_hours": age_hours,
            "max_age_hours": max_age_hours,
            "message": (
                f"column='{column}' age={age_hours:.2f}h threshold={max_age_hours}h: "
                f"{'OK' if passed else 'FAIL'}"
            ),
        }

    def _check_unique(self, check_def: Dict) -> Dict:
        """Verify a column (or column combination) has no duplicates."""
        columns = check_def.get("columns", check_def.get("column", "id"))
        if isinstance(columns, str):
            columns = [columns]

        # Simulate: SELECT COUNT(*) - COUNT(DISTINCT col) FROM table
        duplicate_count = random.randint(0, 3)
        passed = duplicate_count == 0

        return {
            "type": CHECK_UNIQUE,
            "columns": columns,
            "passed": passed,
            "duplicate_count": duplicate_count,
            "message": (
                f"columns={columns} duplicates={duplicate_count}: "
                f"{'OK' if passed else 'FAIL'}"
            ),
        }

    def _check_regex(self, check_def: Dict) -> Dict:
        """Verify column values match a regex pattern."""
        column = check_def.get("column", "unknown")
        pattern = check_def.get("pattern", ".*")

        # Simulate regex match
        non_matching = random.randint(0, 2)
        passed = non_matching == 0

        return {
            "type": CHECK_REGEX,
            "column": column,
            "pattern": pattern,
            "passed": passed,
            "non_matching_count": non_matching,
            "message": (
                f"column='{column}' pattern='{pattern}' non_matching={non_matching}: "
                f"{'OK' if passed else 'FAIL'}"
            ),
        }

    def _check_referential(self, check_def: Dict) -> Dict:
        """Verify FK integrity: all values in `column` exist in `reference_table.reference_column`."""
        column = check_def.get("column", "unknown")
        ref_table = check_def.get("reference_table", "unknown")
        ref_column = check_def.get("reference_column", "id")
        max_violations = check_def.get("max_violations", 0)

        # Simulate: SELECT COUNT(*) FROM t LEFT JOIN ref ON t.col = ref.col WHERE ref.col IS NULL
        violations = random.randint(0, 10)
        passed = violations <= max_violations

        return {
            "type": CHECK_REFERENTIAL,
            "column": column,
            "reference": f"{ref_table}.{ref_column}",
            "passed": passed,
            "violations": violations,
            "max_violations": max_violations,
            "message": (
                f"FK {column} → {ref_table}.{ref_column}: "
                f"violations={violations} max={max_violations}: "
                f"{'OK' if passed else 'FAIL'}"
            ),
        }


# ---------------------------------------------------------------------------
# Convenience factory function
# ---------------------------------------------------------------------------

def create_standard_dq_operator(
    task_id: str,
    table: str,
    connection_id: str = "postgres_default",
    critical_columns: Optional[List[str]] = None,
    fail_on_error: bool = True,
    **kwargs,
) -> DataValidationOperator:
    """
    Factory that creates a DataValidationOperator with a sensible
    default check suite for any table.

    Parameters
    ----------
    task_id : str
    table : str
    connection_id : str
    critical_columns : list[str], optional
        Columns to run not-null and unique checks on.
    fail_on_error : bool
    """
    critical_columns = critical_columns or ["id", "created_at"]

    checks = [
        {"type": CHECK_ROW_COUNT_MIN, "threshold": 1},
        {"type": CHECK_FRESHNESS, "column": "created_at", "max_age_hours": 24},
    ]

    for col in critical_columns:
        checks.append({"type": CHECK_NOT_NULL, "column": col, "threshold": 0.01})
        checks.append({"type": CHECK_UNIQUE, "column": col})

    return DataValidationOperator(
        task_id=task_id,
        table=table,
        connection_id=connection_id,
        checks=checks,
        fail_on_error=fail_on_error,
        **kwargs,
    )


__all__ = [
    "DataValidationOperator",
    "create_standard_dq_operator",
    "CHECK_NOT_NULL",
    "CHECK_ROW_COUNT_MIN",
    "CHECK_ROW_COUNT_MAX",
    "CHECK_VALUE_RANGE",
    "CHECK_FRESHNESS",
    "CHECK_UNIQUE",
    "CHECK_REGEX",
    "CHECK_REFERENTIAL",
]
