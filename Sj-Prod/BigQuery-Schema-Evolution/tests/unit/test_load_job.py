"""Unit tests for IdempotentLoader.

All tests use a MagicMock BQ client — no network calls are made.
Run with: pytest tests/unit/test_load_job.py -v

Coverage targets:
- load() returns LoadResult(skipped=True) when _count_by_load_id > 0
- load() calls _merge_rows when count == 0
- load() with empty rows list returns skipped=True immediately
- LoadResult.rows_written == 0 on duplicate load
- LoadResult.rows_written == len(rows) on first load
- LoadResult.job_id is populated from the BQ job_id on a real write
- LoadResult.job_id is None on skipped load
- _sql_literal handles None, bool, int, float, str, datetime correctly
- _count_by_load_id passes parameterised query to avoid SQL injection
- MERGE SQL contains the primary_key condition
- MERGE SQL contains _load_id condition
- load() handles BQ exceptions and re-raises
- load_id with single quotes is escaped in the MERGE SQL
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from google.api_core.exceptions import BadRequest
from google.cloud import bigquery
from src.pipeline.load_job import IdempotentLoader

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_loader(
    mock_client: MagicMock,
    primary_key: str = "trade_id",
) -> IdempotentLoader:
    return IdempotentLoader(
        client=mock_client,
        project="test-project",
        dataset="test_dataset",
        table="trades",
        primary_key=primary_key,
    )


def _mock_row(data: dict) -> MagicMock:
    row = MagicMock()
    row.__getitem__.side_effect = data.__getitem__
    return row


def _make_query_job(count: int = 0, job_id: str = "bqjob_r_unit") -> MagicMock:
    count_row = _mock_row({"cnt": count})
    job = MagicMock()
    job.result.return_value = iter([count_row])
    job.job_id = job_id
    job.num_dml_affected_rows = count
    return job


# ---------------------------------------------------------------------------
# Tests: empty rows list
# ---------------------------------------------------------------------------

class TestEmptyRows:
    def test_empty_rows_returns_skipped(self, mock_bq_client):
        """load() with empty rows list returns skipped=True without BQ call."""
        loader = _make_loader(mock_bq_client)
        result = loader.load([], load_id="run-001")

        assert result.skipped is True
        assert result.rows_written == 0
        assert result.load_id == "run-001"
        mock_bq_client.query.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: duplicate load_id (pre-flight check)
# ---------------------------------------------------------------------------

class TestDuplicateLoadId:
    def test_skips_when_load_id_exists(self, mock_bq_client):
        """load() skips the MERGE when _count_by_load_id returns > 0."""
        mock_bq_client.query.return_value = _make_query_job(count=3)
        loader = _make_loader(mock_bq_client)

        rows = [{"trade_id": "T001", "symbol": "REL", "amount": 100.0}]
        result = loader.load(rows, load_id="run-001")

        assert result.skipped is True
        assert result.rows_written == 0
        assert result.load_id == "run-001"
        assert result.job_id is None

    def test_skipped_result_count_is_zero(self, mock_bq_client):
        """rows_written must be exactly 0 on skipped (duplicate) load."""
        mock_bq_client.query.return_value = _make_query_job(count=5)
        loader = _make_loader(mock_bq_client)

        rows = [{"trade_id": f"T{i}", "amount": float(i)} for i in range(10)]
        result = loader.load(rows, load_id="dup-run")

        assert result.rows_written == 0


# ---------------------------------------------------------------------------
# Tests: first load (count == 0 → MERGE executed)
# ---------------------------------------------------------------------------

class TestFirstLoad:
    def _setup_for_merge(self, mock_bq_client, rows_affected: int = 2):
        """Configure mock to return count=0 (pre-flight) then succeed on MERGE."""
        count_job = _make_query_job(count=0, job_id="bqjob_r_count")
        merge_job = MagicMock()
        merge_job.result.return_value = iter([])
        merge_job.job_id = "bqjob_r_merge_001"
        merge_job.num_dml_affected_rows = rows_affected
        mock_bq_client.query.side_effect = [count_job, merge_job]

    def test_executes_merge_on_first_load(self, mock_bq_client):
        """load() calls client.query() twice: once for count, once for MERGE."""
        self._setup_for_merge(mock_bq_client)
        loader = _make_loader(mock_bq_client)

        rows = [
            {"trade_id": "T001", "symbol": "REL", "amount": 100.0},
            {"trade_id": "T002", "symbol": "INF", "amount": 200.0},
        ]
        result = loader.load(rows, load_id="run-001")

        assert mock_bq_client.query.call_count == 2
        assert result.skipped is False
        assert result.rows_written == 2

    def test_job_id_populated_from_bq(self, mock_bq_client):
        """LoadResult.job_id must be set from the MERGE BQ job's job_id."""
        self._setup_for_merge(mock_bq_client)
        loader = _make_loader(mock_bq_client)

        rows = [{"trade_id": "T001", "amount": 100.0}]
        result = loader.load(rows, load_id="run-001")

        assert result.job_id == "bqjob_r_merge_001"

    def test_merge_sql_contains_load_id_condition(self, mock_bq_client):
        """The MERGE SQL must reference _load_id in the ON clause."""
        self._setup_for_merge(mock_bq_client)
        loader = _make_loader(mock_bq_client)

        rows = [{"trade_id": "T001", "amount": 1.0}]
        loader.load(rows, load_id="run-abc")

        # The second query call is the MERGE.
        merge_call_args = mock_bq_client.query.call_args_list[1]
        merge_sql = merge_call_args[0][0]
        assert "_load_id" in merge_sql

    def test_merge_sql_contains_primary_key_condition(self, mock_bq_client):
        """The MERGE SQL must reference the primary_key in the ON clause."""
        self._setup_for_merge(mock_bq_client)
        loader = _make_loader(mock_bq_client, primary_key="trade_id")

        rows = [{"trade_id": "T001", "amount": 1.0}]
        loader.load(rows, load_id="run-pk-test")

        merge_sql = mock_bq_client.query.call_args_list[1][0][0]
        assert "trade_id" in merge_sql

    def test_load_result_skipped_is_false_on_first_load(self, mock_bq_client):
        """LoadResult.skipped must be False on a successful first load."""
        self._setup_for_merge(mock_bq_client)
        loader = _make_loader(mock_bq_client)

        rows = [{"trade_id": "T001", "amount": 99.5}]
        result = loader.load(rows, load_id="first-run")

        assert result.skipped is False

    def test_count_query_uses_parameterised_load_id(self, mock_bq_client):
        """_count_by_load_id must use QueryJobConfig with ScalarQueryParameter."""
        mock_bq_client.query.return_value = _make_query_job(count=0)
        loader = _make_loader(mock_bq_client)

        rows = [{"trade_id": "T001"}]
        # Will fail on MERGE step (no second job configured), but we only care
        # about the first call.
        try:
            loader.load(rows, load_id="test-id")
        except Exception:
            pass

        first_call = mock_bq_client.query.call_args_list[0]
        # Check QueryJobConfig was passed as keyword or positional arg.
        job_config = first_call[1].get("job_config") or (
            first_call[0][1] if len(first_call[0]) > 1 else None
        )
        assert job_config is not None, "QueryJobConfig not passed to count query"
        assert isinstance(job_config, bigquery.QueryJobConfig)


# ---------------------------------------------------------------------------
# Tests: _sql_literal
# ---------------------------------------------------------------------------

class TestSqlLiteral:
    def test_none_returns_null(self, mock_bq_client):
        """_sql_literal(None) must return 'NULL'."""
        loader = _make_loader(mock_bq_client)
        assert loader._sql_literal(None) == "NULL"

    def test_true_returns_true(self, mock_bq_client):
        """_sql_literal(True) must return 'TRUE'."""
        loader = _make_loader(mock_bq_client)
        assert loader._sql_literal(True) == "TRUE"

    def test_false_returns_false(self, mock_bq_client):
        """_sql_literal(False) must return 'FALSE'."""
        loader = _make_loader(mock_bq_client)
        assert loader._sql_literal(False) == "FALSE"

    def test_integer_returned_as_repr(self, mock_bq_client):
        """_sql_literal(42) must return '42'."""
        loader = _make_loader(mock_bq_client)
        assert loader._sql_literal(42) == "42"

    def test_float_returned_as_repr(self, mock_bq_client):
        """_sql_literal(3.14) must return a valid float literal."""
        loader = _make_loader(mock_bq_client)
        result = loader._sql_literal(3.14)
        assert float(result) == pytest.approx(3.14)

    def test_string_quoted_with_apostrophes_escaped(self, mock_bq_client):
        """_sql_literal for strings must escape single quotes."""
        loader = _make_loader(mock_bq_client)
        result = loader._sql_literal("it's a test")
        assert result == r"'it\'s a test'"

    def test_datetime_rendered_as_timestamp_literal(self, mock_bq_client):
        """_sql_literal for datetime must produce TIMESTAMP '...' format."""
        loader = _make_loader(mock_bq_client)
        dt = datetime(2026, 5, 19, 10, 0, 0, tzinfo=timezone.utc)
        result = loader._sql_literal(dt)
        assert result.startswith("TIMESTAMP '")
        assert "2026-05-19" in result


# ---------------------------------------------------------------------------
# Tests: exception propagation
# ---------------------------------------------------------------------------

class TestExceptionPropagation:
    def test_bq_bad_request_is_raised_from_merge(self, mock_bq_client):
        """BadRequest from the MERGE job is propagated to the caller."""
        count_job = _make_query_job(count=0)
        bad_merge_job = MagicMock()
        bad_merge_job.result.side_effect = BadRequest("no such field: unknown_col")
        mock_bq_client.query.side_effect = [count_job, bad_merge_job]

        loader = _make_loader(mock_bq_client)
        rows = [{"trade_id": "T001", "unknown_col": "oops"}]

        with pytest.raises(BadRequest):
            loader.load(rows, load_id="bad-run")
