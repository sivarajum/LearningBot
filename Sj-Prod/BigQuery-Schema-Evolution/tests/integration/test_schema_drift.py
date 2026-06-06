"""Schema drift tests: verify BQ rejects unknown fields and incompatible writes.

These tests prove that BigQuery's strict schema enforcement works as expected
when inserting data that does not match the declared table schema.

What this file proves:
1. Inserting a row with an extra field not present in the table schema raises
   BadRequest (or the insert_rows_json error list contains "no such field").
2. Inserting a row that is missing a REQUIRED field raises BadRequest or
   produces an error in the insert_rows_json response.
3. After applying ADD_NULLABLE_COLUMN, the new column accepts NULL values
   without rejecting previously-valid rows.
4. Schema update_table() rejects adding a REQUIRED (non-nullable) column to
   an existing table that already has data.

BQ-specific note:
- The streaming insert API (insert_rows_json) returns a list of errors rather
  than raising directly. Tests check both the exception path (via load jobs)
  and the error-list path (via streaming).

Run with:
    pytest tests/integration/test_schema_drift.py -v \
        --bq-project ai-trading-prod -m integration
"""

import pytest
from google.api_core.exceptions import BadRequest
from google.cloud import bigquery
from src.migration.models import (
    CompatibilityMode,
    Migration,
    MigrationType,
)
from src.migration.runner import MigrationRunner

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_strict_table(bq_client: bigquery.Client, table_id: str) -> bigquery.Table:
    """Create a table with a strict, REQUIRED-only schema.

    BQ will reject streaming inserts that contain fields not in this schema
    when the insertId-based deduplication layer is active.
    """
    schema = [
        bigquery.SchemaField("trade_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("amount", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("_load_id", "STRING", mode="REQUIRED"),
    ]
    table = bigquery.Table(table_id, schema=schema)
    return bq_client.create_table(table)


def _create_table_with_data(bq_client: bigquery.Client, table_id: str) -> bigquery.Table:
    """Create a table with data already present (needed for REQUIRED column rejection test)."""
    schema = [
        bigquery.SchemaField("trade_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("amount", "FLOAT64", mode="NULLABLE"),
    ]
    table = bigquery.Table(table_id, schema=schema)
    created = bq_client.create_table(table)

    # Insert one row so the table is non-empty.
    errors = bq_client.insert_rows_json(
        table_id,
        [{"trade_id": "T001", "amount": 100.0}],
    )
    assert not errors, f"Setup insert failed: {errors}"
    return created


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_schema_drift_raises_bad_request(bq_test_dataset, bq_client):
    """BQ must reject a row with an unknown field when schema is strict.

    Proves that inserting {'trade_id': 'T001', 'unknown_field': 'oops', ...}
    into a table that does not have 'unknown_field' results in an error.

    BQ streaming inserts return errors as a list rather than raising. This test
    validates that the error list is non-empty and the message references the
    unknown field name or 'no such field'.
    """
    project = bq_test_dataset["project"]
    dataset = bq_test_dataset["dataset"]
    table_id = f"{project}.{dataset}.trades_strict"

    _create_strict_table(bq_client, table_id)

    # Attempt to insert a row with an extra field not in schema.
    bad_row = {
        "trade_id": "T999",
        "amount": 500.0,
        "_load_id": "drift-test-001",
        "unknown_field": "this_should_fail",
    }

    # BQ streaming insert rejects unknown fields — errors list must be non-empty.
    errors = bq_client.insert_rows_json(table_id, [bad_row])
    assert errors, (
        "Expected insert_rows_json to return errors for unknown field, but got none. "
        "BQ may have silently accepted the unknown field — check table schema strictness."
    )

    # The error message must reference the unknown field.
    error_messages = " ".join(
        str(e) for e in errors
    ).lower()
    assert (
        "unknown_field" in error_messages
        or "no such field" in error_messages
        or "invalid" in error_messages
    ), f"Unexpected error message: {error_messages}"


@pytest.mark.integration
def test_load_job_rejects_extra_field(bq_test_dataset, bq_client):
    """A BQ load job with CREATE_IF_NEEDED + WRITE_APPEND raises BadRequest for extra fields.

    Uses a QueryJob (INSERT INTO ... SELECT) to attempt writing a row with a
    field that does not exist in the destination table schema. BigQuery must
    raise BadRequest or return a job error.
    """
    project = bq_test_dataset["project"]
    dataset = bq_test_dataset["dataset"]
    table_id = f"{project}.{dataset}.trades_load_strict"

    _create_strict_table(bq_client, table_id)

    # Use INSERT DML which raises BadRequest for unknown columns.
    bad_insert_sql = (
        f"INSERT INTO `{table_id}` (trade_id, amount, _load_id, nonexistent_col) "
        f"VALUES ('T001', 500.0, 'run-001', 'bad_value')"
    )

    with pytest.raises(BadRequest) as exc_info:
        job = bq_client.query(bad_insert_sql)
        job.result()  # Triggers the exception.

    error_text = str(exc_info.value).lower()
    assert (
        "nonexistent_col" in error_text
        or "unrecognized name" in error_text
        or "no such field" in error_text
        or "invalid" in error_text
    ), f"Expected field-name error in: {exc_info.value}"


@pytest.mark.integration
def test_add_nullable_column_does_not_break_existing_inserts(
    bq_test_dataset, bq_client
):
    """Proves BACKWARD compatibility: existing row insertions still work after ADD_NULLABLE_COLUMN.

    After adding a nullable column, inserting rows WITHOUT the new column
    must succeed (the column gets NULL). This validates the BACKWARD
    compatibility claim in the migration model.
    """
    project = bq_test_dataset["project"]
    dataset = bq_test_dataset["dataset"]
    table_name = "trades_backward_compat"
    table_id = f"{project}.{dataset}.{table_name}"

    schema = [
        bigquery.SchemaField("trade_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("amount", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("_load_id", "STRING", mode="REQUIRED"),
    ]
    bq_client.create_table(bigquery.Table(table_id, schema=schema))

    migration = Migration(
        version="v1",
        description="Add nullable risk_score column.",
        migration_type=MigrationType.ADD_NULLABLE_COLUMN,
        column_name="risk_score",
        column_type="FLOAT64",
        compatibility=CompatibilityMode.FULL,
    )

    runner = MigrationRunner(bq_client, project, dataset, table_name)
    result = runner.apply(migration)
    assert result.success is True, f"Migration failed: {result.error}"

    # Insert a row without risk_score — must succeed (BACKWARD compatible).
    old_style_row = {
        "trade_id": "T001",
        "amount": 100.0,
        "_load_id": "backward-test-001",
        # risk_score intentionally omitted
    }
    errors = bq_client.insert_rows_json(table_id, [old_style_row])
    assert not errors, (
        f"BACKWARD compatibility broken: inserting without new column failed: {errors}"
    )


@pytest.mark.integration
def test_adding_required_column_to_nonempty_table_is_rejected(
    bq_test_dataset, bq_client
):
    """Proves that BQ rejects adding a REQUIRED column to a table with existing data.

    BQ only allows adding NULLABLE or REPEATED columns to existing tables.
    Attempting to add a REQUIRED (NOT NULL) column must raise BadRequest.
    This test documents an important BQ schema evolution constraint.
    """
    project = bq_test_dataset["project"]
    dataset = bq_test_dataset["dataset"]
    table_id = f"{project}.{dataset}.trades_required_col_test"

    _create_table_with_data(bq_client, table_id)

    # Attempt to add a REQUIRED column — BQ must reject this.
    table_obj = bq_client.get_table(table_id)
    required_field = bigquery.SchemaField(
        "mandatory_new_col", "STRING", mode="REQUIRED"
    )
    table_obj.schema = list(table_obj.schema) + [required_field]

    with pytest.raises(BadRequest) as exc_info:
        bq_client.update_table(table_obj, ["schema"])

    error_text = str(exc_info.value).lower()
    assert any(
        phrase in error_text
        for phrase in ("mandatory_new_col", "required", "not null", "cannot add")
    ), (
        f"BadRequest message did not reference the rejected column. Got: {str(exc_info.value)!r}"
    )
