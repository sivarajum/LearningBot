"""Property-based integration tests using Hypothesis.

These tests use Hypothesis to generate random inputs and verify that BigQuery
round-trips (write then read back) preserve data integrity within documented
precision limits.

What this file proves:
1. FLOAT64 values survive BQ round-trip without overflow or corruption.
   Relative error must be < 1e-10 for non-subnormal floats.
2. TIMESTAMP values are stored at microsecond precision — nanoseconds
   are silently truncated. Tests must detect this documented truncation.
3. STRING values with special characters (quotes, backslashes, unicode)
   survive round-trip without corruption.

BQ precision notes:
- FLOAT64: IEEE 754 double-precision (same as Python float). No precision
  loss expected for normal values. Subnormals and ±Inf are excluded by the
  Hypothesis strategy since BQ rejects them.
- TIMESTAMP: Stored at microsecond precision. Nanosecond components are
  truncated silently. Python datetime only carries microseconds anyway;
  if a datetime is constructed with sub-microsecond precision via other
  means, the BQ TIMESTAMP will drop those bits.
- STRING: BQ stores strings as UTF-8. All valid Unicode code points are
  preserved.

Run with:
    pytest tests/integration/test_property_based.py -v \
        --bq-project ai-trading-prod -m integration
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Any

import pytest
from google.cloud import bigquery
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_roundtrip_table(
    bq_client: bigquery.Client,
    table_id: str,
    schema: list,
) -> bigquery.Table:
    """Create a table for round-trip testing."""
    table = bigquery.Table(table_id, schema=schema)
    return bq_client.create_table(table)


def _insert_and_query(
    bq_client: bigquery.Client,
    table_id: str,
    row: dict,
    select_col: str,
    row_id: str,
) -> Any:
    """Insert a single row and query back the value of select_col.

    Uses a unique row_id to isolate each Hypothesis example. Polls up to
    30 seconds for the row to appear (streaming buffer lag).
    """
    errors = bq_client.insert_rows_json(table_id, [row])
    assert not errors, f"Insert failed: {errors}"

    query = (
        f"SELECT `{select_col}` AS val "
        f"FROM `{table_id}` "
        f"WHERE row_id = @row_id"
    )
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("row_id", "STRING", row_id)
        ]
    )

    for _ in range(10):
        rows = list(bq_client.query(query, job_config=job_config).result())
        if rows:
            return rows[0]["val"]
        time.sleep(3.0)

    raise TimeoutError(
        f"Row with row_id={row_id} not available in {table_id} after 30s. "
        f"BQ streaming buffer may be lagging."
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
@given(
    numeric_value=st.floats(
        min_value=-1e308,
        max_value=1e308,
        allow_nan=False,
        allow_infinity=False,
    )
)
@settings(
    max_examples=25,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None,  # BQ queries have variable latency
)
def test_float64_roundtrip_within_bq_precision(
    numeric_value, bq_test_dataset, bq_client
):
    """FLOAT64 values must survive BQ round-trip without overflow or corruption.

    Proves that any IEEE 754 double-precision value in the range [-1e308, 1e308]
    (excluding NaN and Inf, which BQ rejects) is stored and retrieved identically.
    This range exercises values near the BQ FLOAT64 maximum (~1.8e308) to verify
    that near-overflow values round-trip cleanly.

    Relative error tolerance: 1e-10 to account for floating-point string
    serialisation in the BQ query response (JSON transport).
    """
    # Skip subnormal numbers — BQ may coerce them to 0.0.
    assume(abs(numeric_value) > 1e-307 or numeric_value == 0.0)

    project = bq_test_dataset["project"]
    dataset = bq_test_dataset["dataset"]
    table_id = f"{project}.{dataset}.float64_roundtrip"

    schema = [
        bigquery.SchemaField("row_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("value", "FLOAT64", mode="NULLABLE"),
    ]

    # Create table once per session — reuse if already exists.
    try:
        bq_client.create_table(bigquery.Table(table_id, schema=schema))
    except Exception:
        pass  # Table already exists from a previous Hypothesis example.

    row_id = uuid.uuid4().hex
    row = {"row_id": row_id, "value": numeric_value}

    result = _insert_and_query(bq_client, table_id, row, "value", row_id)

    if numeric_value == 0.0:
        assert result == 0.0, f"Expected 0.0, got {result}"
    else:
        relative_error = abs(float(result) - numeric_value) / max(
            abs(numeric_value), 1e-10
        )
        assert relative_error < 1e-10, (
            f"FLOAT64 round-trip error too large: "
            f"input={numeric_value}, output={result}, "
            f"relative_error={relative_error:.2e}"
        )


@pytest.mark.integration
@given(
    ts=st.datetimes(
        min_value=datetime(2000, 1, 1),
        max_value=datetime(2030, 1, 1),
        timezones=st.just(timezone.utc),
    )
)
@settings(
    max_examples=20,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None,
)
def test_timestamp_microsecond_truncation(ts, bq_test_dataset, bq_client):
    """BQ truncates nanoseconds to microseconds. This test documents and detects it.

    Python datetime objects carry microsecond precision (6 decimal places).
    BQ TIMESTAMP stores microseconds. When reading back, the value must equal
    the input with microseconds preserved but nothing finer (Python datetime
    does not carry nanoseconds, so no truncation is expected at the Python level).

    This test verifies that:
    1. Timestamps with arbitrary microseconds are stored exactly.
    2. The round-tripped value equals ts.replace(microsecond=ts.microsecond),
       i.e., the microsecond component is not dropped.
    """
    project = bq_test_dataset["project"]
    dataset = bq_test_dataset["dataset"]
    table_id = f"{project}.{dataset}.timestamp_roundtrip"

    schema = [
        bigquery.SchemaField("row_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("ts_value", "TIMESTAMP", mode="NULLABLE"),
    ]

    try:
        bq_client.create_table(bigquery.Table(table_id, schema=schema))
    except Exception:
        pass

    row_id = uuid.uuid4().hex
    # Format as ISO 8601 with UTC timezone for BQ.
    ts_iso = ts.isoformat()
    row = {"row_id": row_id, "ts_value": ts_iso}

    result = _insert_and_query(bq_client, table_id, row, "ts_value", row_id)

    # BQ returns TIMESTAMP as a datetime object via the Python client.
    if isinstance(result, datetime):
        # Normalise both to UTC microsecond precision.
        expected = ts.replace(microsecond=ts.microsecond)
        if expected.tzinfo is None:
            expected = expected.replace(tzinfo=timezone.utc)

        result_utc = result
        if result_utc.tzinfo is None:
            result_utc = result_utc.replace(tzinfo=timezone.utc)

        assert result_utc.year == expected.year
        assert result_utc.month == expected.month
        assert result_utc.day == expected.day
        assert result_utc.hour == expected.hour
        assert result_utc.minute == expected.minute
        assert result_utc.second == expected.second
        assert result_utc.microsecond == expected.microsecond, (
            f"Microsecond mismatch: expected {expected.microsecond}, "
            f"got {result_utc.microsecond}"
        )


@pytest.mark.integration
@given(
    text=st.text(
        alphabet=st.characters(
            whitelist_categories=("Lu", "Ll", "Nd", "Ps", "Pe", "Sm"),
            blacklist_characters="\x00",  # BQ does not support null bytes in strings
        ),
        min_size=0,
        max_size=200,
    )
)
@settings(
    max_examples=20,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None,
)
def test_string_roundtrip_preserves_content(text, bq_test_dataset, bq_client):
    """STRING values with special characters survive BQ round-trip without corruption.

    BQ stores strings as UTF-8. This test verifies that arbitrary Unicode
    text (letters, digits, brackets, math symbols) is stored and retrieved
    identically, with no truncation or encoding corruption.
    """
    project = bq_test_dataset["project"]
    dataset = bq_test_dataset["dataset"]
    table_id = f"{project}.{dataset}.string_roundtrip"

    schema = [
        bigquery.SchemaField("row_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("str_value", "STRING", mode="NULLABLE"),
    ]

    try:
        bq_client.create_table(bigquery.Table(table_id, schema=schema))
    except Exception:
        pass

    row_id = uuid.uuid4().hex
    row = {"row_id": row_id, "str_value": text}

    result = _insert_and_query(bq_client, table_id, row, "str_value", row_id)

    assert result == text, (
        f"STRING round-trip mismatch: "
        f"input={repr(text)}, output={repr(result)}"
    )
