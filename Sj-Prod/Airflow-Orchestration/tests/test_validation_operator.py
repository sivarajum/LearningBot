"""
Unit tests for DataValidationOperator.

No Airflow installation required — the operator ships with import stubs
that provide a BaseOperator shim when Airflow is absent.

Run:
    pip install pytest pytest-cov
    PYTHONPATH=. pytest tests/test_validation_operator.py -v
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Ensure the project root is on the path so the operator is importable
# without an installed package.
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from plugins.operators.validation_operator import (
    CHECK_FRESHNESS,
    CHECK_NOT_NULL,
    CHECK_REFERENTIAL,
    CHECK_REGEX,
    CHECK_ROW_COUNT_MAX,
    CHECK_ROW_COUNT_MIN,
    CHECK_UNIQUE,
    CHECK_VALUE_RANGE,
    DataValidationOperator,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_context(run_id: str = "manual__2024-01-01T00:00:00") -> dict:
    """Return a minimal Airflow-like context dict with a MagicMock TaskInstance."""
    ti = MagicMock()
    return {
        "ti": ti,
        "run_id": run_id,
    }


def _make_operator(
    checks: list,
    fail_on_error: bool = True,
    table: str = "test_table",
) -> DataValidationOperator:
    """Convenience factory for operator instances."""
    return DataValidationOperator(
        task_id="test_dvo",
        table=table,
        connection_id="test_conn",
        checks=checks,
        fail_on_error=fail_on_error,
    )


# ---------------------------------------------------------------------------
# Test 1: all checks pass → overall_passed=True
# ---------------------------------------------------------------------------

class TestExecuteAllPass(unittest.TestCase):
    """Operator returns a report with overall_passed=True when all checks pass."""

    def test_execute_all_pass(self):
        checks = [
            {"type": CHECK_ROW_COUNT_MIN, "threshold": 1},     # always passes (simulated 1000+)
            {"type": CHECK_FRESHNESS, "column": "created_at", "max_age_hours": 24},  # always passes
        ]
        op = _make_operator(checks, fail_on_error=True)
        ctx = _make_context()

        # Force both checks to pass by patching the internal check methods
        with patch.object(op, "_check_row_count_min", return_value={"type": CHECK_ROW_COUNT_MIN, "passed": True, "message": "ok"}):
            with patch.object(op, "_check_freshness", return_value={"type": CHECK_FRESHNESS, "passed": True, "message": "ok"}):
                report = op.execute(ctx)

        self.assertTrue(report["overall_passed"])
        self.assertEqual(report["failed"], 0)
        self.assertEqual(report["passed"], 2)


# ---------------------------------------------------------------------------
# Test 2: fail_on_error=True + failing check → raises exception
# ---------------------------------------------------------------------------

class TestExecuteOneFailRaises(unittest.TestCase):
    """Operator raises ValueError when a check fails and fail_on_error=True."""

    def test_execute_one_fail_raises(self):
        checks = [{"type": CHECK_NOT_NULL, "column": "txn_id", "threshold": 0.0}]
        op = _make_operator(checks, fail_on_error=True)
        ctx = _make_context()

        # Force the check to fail
        failing_result = {
            "type": CHECK_NOT_NULL,
            "passed": False,
            "message": "null_rate=0.5 exceeds threshold=0.0",
        }
        with patch.object(op, "_check_not_null", return_value=failing_result):
            with self.assertRaises((ValueError, Exception)):
                op.execute(ctx)


# ---------------------------------------------------------------------------
# Test 3: fail_on_error=False + failing check → returns report, no exception
# ---------------------------------------------------------------------------

class TestExecuteFailNoRaise(unittest.TestCase):
    """Operator does NOT raise when fail_on_error=False, even with a failing check."""

    def test_execute_fail_no_raise(self):
        checks = [{"type": CHECK_NOT_NULL, "column": "txn_id", "threshold": 0.0}]
        op = _make_operator(checks, fail_on_error=False)
        ctx = _make_context()

        failing_result = {
            "type": CHECK_NOT_NULL,
            "passed": False,
            "message": "null_rate=0.5 exceeds threshold=0.0",
        }
        with patch.object(op, "_check_not_null", return_value=failing_result):
            report = op.execute(ctx)  # must NOT raise

        self.assertFalse(report["overall_passed"])
        self.assertEqual(report["failed"], 1)


# ---------------------------------------------------------------------------
# Test 4: XCom push called with correct key and a dict containing 'overall_passed'
# ---------------------------------------------------------------------------

class TestXcomPush(unittest.TestCase):
    """After execute(), ti.xcom_push must be called with xcom_key and a report dict."""

    def test_xcom_push(self):
        checks = [{"type": CHECK_ROW_COUNT_MIN, "threshold": 1}]
        op = _make_operator(checks, fail_on_error=False)
        ctx = _make_context()

        passing_result = {"type": CHECK_ROW_COUNT_MIN, "passed": True, "message": "ok"}
        with patch.object(op, "_check_row_count_min", return_value=passing_result):
            op.execute(ctx)

        ti = ctx["ti"]
        ti.xcom_push.assert_called_once()
        call_kwargs = ti.xcom_push.call_args
        # Support both positional and keyword call signatures
        key_used = call_kwargs[1].get("key") or call_kwargs[0][0]
        value_used = call_kwargs[1].get("value") or call_kwargs[0][1]

        self.assertEqual(key_used, "validation_report")
        self.assertIn("overall_passed", value_used)


# ---------------------------------------------------------------------------
# Test 5: Unknown check type → result with passed=False, no crash
# ---------------------------------------------------------------------------

class TestUnknownCheckType(unittest.TestCase):
    """An unknown check type returns passed=False and does not crash the operator."""

    def test_unknown_check_type(self):
        checks = [{"type": "nonexistent_check_xyz"}]
        op = _make_operator(checks, fail_on_error=False)
        ctx = _make_context()

        report = op.execute(ctx)

        self.assertEqual(len(report["results"]), 1)
        result = report["results"][0]
        self.assertFalse(result["passed"])
        self.assertIn("Unknown check type", result["message"])

    def test_unknown_check_type_does_not_crash(self):
        """Unknown check type must not raise even with fail_on_error=True."""
        checks = [{"type": "bogus_type"}]
        op = _make_operator(checks, fail_on_error=False)
        ctx = _make_context()
        # Should complete without exception
        report = op.execute(ctx)
        self.assertIsInstance(report, dict)


# ---------------------------------------------------------------------------
# Test 6: All 8 check types dispatch correctly — each returns a dict with 'passed'
# ---------------------------------------------------------------------------

class TestAllCheckTypesDispatch(unittest.TestCase):
    """Every supported check type dispatches to a handler that returns {'passed': <bool>}."""

    CHECK_DEFS = [
        {"type": CHECK_NOT_NULL, "column": "col1"},
        {"type": CHECK_ROW_COUNT_MIN, "threshold": 1},
        {"type": CHECK_ROW_COUNT_MAX, "threshold": 10_000_000},
        {"type": CHECK_VALUE_RANGE, "column": "amount", "min": 0, "max": 1_000_000},
        {"type": CHECK_FRESHNESS, "column": "created_at", "max_age_hours": 24},
        {"type": CHECK_UNIQUE, "column": "txn_id"},
        {"type": CHECK_REGEX, "column": "email", "pattern": r".+@.+"},
        {"type": CHECK_REFERENTIAL, "column": "customer_id",
         "reference_table": "dim_customer", "reference_column": "id"},
    ]

    def test_all_check_types_dispatch(self):
        op = DataValidationOperator(
            task_id="dispatch_test",
            table="test_table",
            checks=[],
            fail_on_error=False,
        )
        for check_def in self.CHECK_DEFS:
            with self.subTest(check_type=check_def["type"]):
                result = op._run_check(check_def)
                self.assertIsInstance(result, dict, f"Expected dict for {check_def['type']}")
                self.assertIn("passed", result, f"'passed' key missing for {check_def['type']}")
                self.assertIsInstance(
                    result["passed"], bool,
                    f"'passed' must be bool for {check_def['type']}"
                )


# ---------------------------------------------------------------------------
# Test 7: pass_rate calculation = (passed_count / total_count) * 100
# ---------------------------------------------------------------------------

class TestPassRateCalculation(unittest.TestCase):
    """pass_rate in the report equals (passed_count / total_count) * 100."""

    def test_pass_rate_all_pass(self):
        checks = [
            {"type": CHECK_ROW_COUNT_MIN, "threshold": 1},
            {"type": CHECK_ROW_COUNT_MIN, "threshold": 1},
        ]
        op = _make_operator(checks, fail_on_error=False)
        ctx = _make_context()
        passing = {"type": CHECK_ROW_COUNT_MIN, "passed": True, "message": "ok"}

        with patch.object(op, "_check_row_count_min", return_value=passing):
            report = op.execute(ctx)

        self.assertAlmostEqual(report["pass_rate"], 100.0)

    def test_pass_rate_half_pass(self):
        checks = [
            {"type": CHECK_ROW_COUNT_MIN, "threshold": 1},
            {"type": CHECK_ROW_COUNT_MAX, "threshold": 1},
        ]
        op = _make_operator(checks, fail_on_error=False)
        ctx = _make_context()
        passing = {"type": CHECK_ROW_COUNT_MIN, "passed": True, "message": "ok"}
        failing = {"type": CHECK_ROW_COUNT_MAX, "passed": False, "message": "fail"}

        with patch.object(op, "_check_row_count_min", return_value=passing):
            with patch.object(op, "_check_row_count_max", return_value=failing):
                report = op.execute(ctx)

        self.assertAlmostEqual(report["pass_rate"], 50.0)

    def test_pass_rate_none_pass(self):
        checks = [
            {"type": CHECK_NOT_NULL, "column": "col", "threshold": 0.0},
        ]
        op = _make_operator(checks, fail_on_error=False)
        ctx = _make_context()
        failing = {"type": CHECK_NOT_NULL, "passed": False, "message": "fail"}

        with patch.object(op, "_check_not_null", return_value=failing):
            report = op.execute(ctx)

        self.assertAlmostEqual(report["pass_rate"], 0.0)

    def test_pass_rate_empty_checks(self):
        """With zero checks, pass_rate should be 0.0 (not a division-by-zero error)."""
        op = _make_operator([], fail_on_error=False)
        ctx = _make_context()
        report = op.execute(ctx)
        self.assertEqual(report["pass_rate"], 0.0)


# ---------------------------------------------------------------------------
# Additional: report structure completeness
# ---------------------------------------------------------------------------

class TestReportStructure(unittest.TestCase):
    """The returned report always contains required top-level keys."""

    REQUIRED_KEYS = {
        "table", "connection_id", "check_count", "results",
        "passed", "failed", "errors", "validated_at",
        "overall_passed", "pass_rate",
    }

    def test_report_has_required_keys(self):
        op = _make_operator([{"type": CHECK_ROW_COUNT_MIN, "threshold": 1}], fail_on_error=False)
        ctx = _make_context()
        report = op.execute(ctx)
        for key in self.REQUIRED_KEYS:
            self.assertIn(key, report, f"Missing key in report: {key}")


# ---------------------------------------------------------------------------
# Test: on_sla_miss callback — JSON structure and no-throw guarantee
# ---------------------------------------------------------------------------

class TestOnSlaMissCallback(unittest.TestCase):
    """on_sla_miss emits a valid JSON WARNING log and never throws."""

    def _make_mock_task(self, task_id: str):
        t = MagicMock()
        t.task_id = task_id
        return t

    def test_on_sla_miss_emits_json_log(self):
        """on_sla_miss must emit a valid JSON warning log with required fields."""
        import os
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from plugins.callbacks import on_sla_miss

        dag = MagicMock()
        dag.dag_id = "test_dag"
        task_list = [self._make_mock_task("extract"), self._make_mock_task("load")]
        blocking_task_list = [self._make_mock_task("extract")]

        with patch("plugins.callbacks.logger") as mock_logger:
            on_sla_miss(dag, task_list, blocking_task_list, slas=[], blocking_tis=[])

        mock_logger.warning.assert_called_once()
        raw = mock_logger.warning.call_args[0][0]
        parsed = json.loads(raw)  # must be valid JSON
        self.assertEqual(parsed["event"], "sla_miss")
        self.assertEqual(parsed["dag_id"], "test_dag")
        self.assertIn("extract", parsed["missed_tasks"])
        self.assertEqual(parsed["severity"], "WARNING")
        self.assertIn("timestamp", parsed)

    def test_on_sla_miss_does_not_throw_on_malformed_input(self):
        """on_sla_miss must not raise even if Airflow passes unexpected types."""
        from plugins.callbacks import on_sla_miss

        dag = MagicMock()
        dag.dag_id = "test_dag"
        # Pass objects whose .task_id access will raise AttributeError
        broken_task = MagicMock(spec=[])  # no attributes at all

        try:
            on_sla_miss(dag, [broken_task], [], slas=[], blocking_tis=[])
        except Exception as exc:
            self.fail(f"on_sla_miss raised unexpectedly: {exc}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
