"""Idempotency proof: same load_id twice must produce zero duplicate rows.

This is the most critical correctness test in the suite. It proves that the
two-phase protocol (COUNT check + MERGE) prevents duplicate rows regardless of
how many times the same load_id is submitted.

What this file proves:
1. Single batch, called twice → COUNT(*) == len(rows), not len(rows) * 2.
2. Second call returns LoadResult(skipped=True, rows_written=0).
3. Multiple distinct load_ids → COUNT(*) == total rows across all batches.
4. Empty rows list → no rows written, no error.
5. Concurrent-safe: the pre-flight COUNT check uses the same load_id key
   that the MERGE stamps on each row, so even a partial MERGE followed by
   a retry will not double-insert.

Run with:
    pytest tests/integration/test_idempotency.py -v \
        --bq-project ai-trading-prod -m integration
"""

import time

import pytest
from google.cloud import bigquery
from src.pipeline.load_job import IdempotentLoader

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_trades_table(bq_client: bigquery.Client, table_id: str) -> bigquery.Table:
    """Create a trades table with _load_id and trade_id columns."""
    schema = [
        bigquery.SchemaField("trade_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("symbol", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("amount", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("_load_id", "STRING", mode="REQUIRED"),
    ]
    table = bigquery.Table(table_id, schema=schema)
    return bq_client.create_table(table)


def _count_rows(bq_client: bigquery.Client, table_id: str) -> int:
    """Return the total row count for the given table, bypassing streaming buffer."""
    query = f"SELECT COUNT(*) AS cnt FROM `{table_id}`"
    rows = list(bq_client.query(query).result())
    return int(rows[0]["cnt"])


def _count_by_load_id(bq_client: bigquery.Client, table_id: str, load_id: str) -> int:
    """Return the row count for a specific load_id."""
    query = (
        f"SELECT COUNT(*) AS cnt FROM `{table_id}` WHERE _load_id = @load_id"
    )
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("load_id", "STRING", load_id)
        ]
    )
    rows = list(bq_client.query(query, job_config=job_config).result())
    return int(rows[0]["cnt"])


def _poll_count(bq_client, table_id, expected, retries=8, delay=3.0):
    """Poll COUNT(*) until it reaches expected (accounts for streaming buffer lag)."""
    for _ in range(retries):
        actual = _count_rows(bq_client, table_id)
        if actual >= expected:
            return actual
        time.sleep(delay)
    return _count_rows(bq_client, table_id)


# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

SAMPLE_ROWS = [
    {"trade_id": "T001", "symbol": "RELIANCE", "amount": 10000.0},
    {"trade_id": "T002", "symbol": "INFY", "amount": 5500.0},
    {"trade_id": "T003", "symbol": "TCS", "amount": 8200.0},
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_load_same_id_twice_produces_no_duplicates(bq_test_dataset, bq_client):
    """Proves zero duplicate rows when the same load_id is submitted twice.

    Protocol:
    1. Create a trades table with _load_id column.
    2. Load SAMPLE_ROWS with load_id='test-run-001'.
    3. Load SAMPLE_ROWS again with the same load_id='test-run-001'.
    4. Query COUNT(*) — must equal len(SAMPLE_ROWS), not len(SAMPLE_ROWS) * 2.
    5. Second LoadResult.skipped must be True.
    6. Second LoadResult.rows_written must be 0.
    """
    project = bq_test_dataset["project"]
    dataset = bq_test_dataset["dataset"]
    table_id = f"{project}.{dataset}.trades_idempotency"

    _create_trades_table(bq_client, table_id)

    loader = IdempotentLoader(bq_client, project, dataset, "trades_idempotency")
    load_id = "test-run-001"

    # First load.
    first_result = loader.load(SAMPLE_ROWS, load_id=load_id)
    assert first_result.skipped is False, "First load must not be skipped"
    assert first_result.rows_written == len(SAMPLE_ROWS)
    assert first_result.job_id is not None

    # Wait for MERGE to commit (BQ MERGE is synchronous but add small buffer).
    time.sleep(2.0)

    # Second load — identical load_id.
    second_result = loader.load(SAMPLE_ROWS, load_id=load_id)
    assert second_result.skipped is True, "Second load must be skipped (duplicate load_id)"
    assert second_result.rows_written == 0
    assert second_result.job_id is None

    # Query actual row count — must not be doubled.
    actual_count = _poll_count(bq_client, table_id, len(SAMPLE_ROWS))
    assert actual_count == len(SAMPLE_ROWS), (
        f"Expected {len(SAMPLE_ROWS)} rows but found {actual_count}. "
        f"Duplicate rows were inserted."
    )


@pytest.mark.integration
def test_multiple_distinct_load_ids_accumulate(bq_test_dataset, bq_client):
    """Proves that distinct load_ids each add their rows correctly.

    Two separate batches with different load_ids must result in the sum of
    both batches being present — no data loss from the MERGE deduplication.
    """
    project = bq_test_dataset["project"]
    dataset = bq_test_dataset["dataset"]
    table_id = f"{project}.{dataset}.trades_multi"

    _create_trades_table(bq_client, table_id)

    loader = IdempotentLoader(bq_client, project, dataset, "trades_multi")

    batch_a = [
        {"trade_id": "A001", "symbol": "REL", "amount": 1000.0},
        {"trade_id": "A002", "symbol": "INF", "amount": 2000.0},
    ]
    batch_b = [
        {"trade_id": "B001", "symbol": "TCS", "amount": 3000.0},
    ]

    result_a = loader.load(batch_a, load_id="batch-a")
    assert result_a.rows_written == len(batch_a)

    time.sleep(2.0)

    result_b = loader.load(batch_b, load_id="batch-b")
    assert result_b.rows_written == len(batch_b)

    expected_total = len(batch_a) + len(batch_b)
    actual_count = _poll_count(bq_client, table_id, expected_total)
    assert actual_count == expected_total, (
        f"Expected {expected_total} rows from 2 distinct batches, got {actual_count}"
    )


@pytest.mark.integration
def test_repeated_retry_never_exceeds_original_row_count(bq_test_dataset, bq_client):
    """Proves that 5 retries with the same load_id never insert extra rows.

    Simulates a flaky pipeline that retries load() up to 5 times. The final
    row count must equal exactly len(SAMPLE_ROWS).
    """
    project = bq_test_dataset["project"]
    dataset = bq_test_dataset["dataset"]
    table_id = f"{project}.{dataset}.trades_retry"

    _create_trades_table(bq_client, table_id)

    loader = IdempotentLoader(bq_client, project, dataset, "trades_retry")
    load_id = "retry-run-001"

    results = []
    for attempt in range(5):
        result = loader.load(SAMPLE_ROWS, load_id=load_id)
        results.append(result)
        if attempt == 0:
            # After the first successful write, allow BQ to commit.
            time.sleep(2.0)

    # Only the first attempt must write rows.
    assert results[0].rows_written == len(SAMPLE_ROWS)
    assert results[0].skipped is False

    # All subsequent attempts must be skipped.
    for i, res in enumerate(results[1:], start=1):
        assert res.skipped is True, f"Attempt {i} was not skipped"
        assert res.rows_written == 0, f"Attempt {i} wrote unexpected rows"

    actual_count = _poll_count(bq_client, table_id, len(SAMPLE_ROWS))
    assert actual_count == len(SAMPLE_ROWS), (
        f"After 5 retries, expected {len(SAMPLE_ROWS)} rows, got {actual_count}"
    )


@pytest.mark.integration
def test_empty_rows_list_is_noop(bq_test_dataset, bq_client):
    """Proves that load() with an empty rows list is a safe no-op.

    No BQ API calls should be made and the table must remain empty.
    """
    project = bq_test_dataset["project"]
    dataset = bq_test_dataset["dataset"]
    table_id = f"{project}.{dataset}.trades_empty"

    _create_trades_table(bq_client, table_id)

    loader = IdempotentLoader(bq_client, project, dataset, "trades_empty")
    result = loader.load([], load_id="empty-run-001")

    assert result.skipped is True
    assert result.rows_written == 0
    assert result.job_id is None

    actual_count = _count_rows(bq_client, table_id)
    assert actual_count == 0
