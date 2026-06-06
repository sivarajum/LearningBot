"""Integration tests for MigrationRunner against a real BigQuery dataset.

Each test creates a fresh dataset via the bq_test_dataset fixture and applies
real DDL changes through the BQ API. Tests verify that:
- ADD_NULLABLE_COLUMN physically adds the column to the BQ table schema.
- RENAME_VIA_VIEW creates a queryable view in BQ.
- DEPRECATE_COLUMN updates the field description in the BQ table metadata.
- _migrations audit table is created automatically on first run.
- apply_all() is idempotent: running the same migration set twice produces
  the same final schema state without errors.

These tests require:
    gcloud auth application-default login
    pytest tests/integration/ -v --bq-project ai-trading-prod -m integration
"""

import time

import pytest
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

def _wait_for_schema(
    client: bigquery.Client,
    table_id: str,
    expected_col: str,
    retries: int = 5,
    delay: float = 2.0,
) -> bool:
    """Poll until the expected column appears in the BQ table schema.

    BQ schema updates are synchronous via update_table(), but there can be
    brief metadata propagation delays in the test environment.

    Returns True if the column was found within the retry window.
    """
    for _ in range(retries):
        table = client.get_table(table_id)
        if any(f.name == expected_col for f in table.schema):
            return True
        time.sleep(delay)
    return False


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_add_nullable_column_appears_in_bq_schema(
    bq_test_dataset, bq_client, trades_table
):
    """Proves that ADD_NULLABLE_COLUMN physically modifies the BQ table schema.

    After calling apply() with a risk_score FLOAT64 migration, retrieving the
    table metadata from BQ must show the new column in the schema list.
    """
    project = bq_test_dataset["project"]
    dataset = bq_test_dataset["dataset"]

    migration = Migration(
        version="v1",
        description="Add nullable risk_score column for downstream risk models.",
        migration_type=MigrationType.ADD_NULLABLE_COLUMN,
        column_name="risk_score",
        column_type="FLOAT64",
        compatibility=CompatibilityMode.FULL,
    )

    runner = MigrationRunner(bq_client, project, dataset, "trades")
    result = runner.apply(migration)

    assert result.success is True, f"Migration failed: {result.error}"
    assert result.already_applied is False

    # Verify the column actually exists in BQ.
    table_id = f"{project}.{dataset}.trades"
    found = _wait_for_schema(bq_client, table_id, "risk_score")
    assert found, "risk_score column not found in BQ schema after migration"

    table = bq_client.get_table(table_id)
    risk_field = next(f for f in table.schema if f.name == "risk_score")
    assert risk_field.field_type == "FLOAT64"
    assert risk_field.mode == "NULLABLE"


@pytest.mark.integration
def test_migrations_audit_table_created_automatically(
    bq_test_dataset, bq_client, trades_table
):
    """Proves that _migrations audit table is auto-created on first runner call.

    The runner must create poc10_test_xxxx._migrations before applying any
    migration. After apply(), we must be able to SELECT from that table and
    find exactly one row.
    """
    project = bq_test_dataset["project"]
    dataset = bq_test_dataset["dataset"]

    migration = Migration(
        version="v1",
        description="Audit table creation test.",
        migration_type=MigrationType.ADD_NULLABLE_COLUMN,
        column_name="audit_test_col",
        column_type="STRING",
        compatibility=CompatibilityMode.BACKWARD,
    )

    runner = MigrationRunner(bq_client, project, dataset, "trades")
    result = runner.apply(migration)

    assert result.success is True

    # Poll for the _migrations row (streaming buffer may have a small lag).
    migrations_table_id = f"{project}.{dataset}._migrations"
    query = f"SELECT version, checksum FROM `{migrations_table_id}`"

    rows = []
    for _ in range(6):
        rows = list(bq_client.query(query).result())
        if rows:
            break
        time.sleep(2.0)

    assert len(rows) == 1, f"Expected 1 audit row, got {len(rows)}"
    assert rows[0]["version"] == "v1"
    assert rows[0]["checksum"] == migration.checksum


@pytest.mark.integration
def test_rename_via_view_creates_queryable_view(
    bq_test_dataset, bq_client, trades_table
):
    """Proves that RENAME_VIA_VIEW creates a real, queryable BQ view.

    After applying the rename migration, the view {table}_v2 must exist in BQ
    and expose the column under its new name (currency_code instead of ccy).
    """
    project = bq_test_dataset["project"]
    dataset = bq_test_dataset["dataset"]

    migration = Migration(
        version="v2",
        description="Renamed ccy to currency_code for clarity.",
        migration_type=MigrationType.RENAME_VIA_VIEW,
        column_name="ccy:currency_code",
        compatibility=CompatibilityMode.BACKWARD,
    )

    runner = MigrationRunner(bq_client, project, dataset, "trades")
    result = runner.apply(migration)

    assert result.success is True, f"Migration failed: {result.error}"

    # Verify the view exists and has the new column name.
    view_id = f"{project}.{dataset}.trades_v2"
    view_table = bq_client.get_table(view_id)
    assert view_table is not None
    assert view_table.view_query is not None
    assert "currency_code" in view_table.view_query


@pytest.mark.integration
def test_deprecate_column_updates_field_description(
    bq_test_dataset, bq_client, trades_table
):
    """Proves that DEPRECATE_COLUMN sets the BQ column description to 'DEPRECATED: ...'

    After applying the deprecation migration, retrieving the table schema from
    BQ must show the updated description on the legacy_currency_code column.
    We first add the column, then deprecate it.
    """
    project = bq_test_dataset["project"]
    dataset = bq_test_dataset["dataset"]

    # Step 1: add the column we will deprecate.
    add_migration = Migration(
        version="v1",
        description="Add legacy_currency_code column (will be deprecated).",
        migration_type=MigrationType.ADD_NULLABLE_COLUMN,
        column_name="legacy_currency_code",
        column_type="STRING",
        compatibility=CompatibilityMode.BACKWARD,
    )

    deprecate_migration = Migration(
        version="v3",
        description=(
            "Deprecated legacy_currency_code; use currency_code (v2) instead."
        ),
        migration_type=MigrationType.DEPRECATE_COLUMN,
        column_name="legacy_currency_code",
        compatibility=CompatibilityMode.BACKWARD,
    )

    runner = MigrationRunner(bq_client, project, dataset, "trades")
    add_result = runner.apply(add_migration)
    assert add_result.success is True, f"Add migration failed: {add_result.error}"

    dep_result = runner.apply(deprecate_migration)
    assert dep_result.success is True, f"Deprecate migration failed: {dep_result.error}"

    # Verify description in BQ.
    table_id = f"{project}.{dataset}.trades"
    table = bq_client.get_table(table_id)
    legacy_field = next(
        (f for f in table.schema if f.name == "legacy_currency_code"), None
    )
    assert legacy_field is not None
    assert legacy_field.description.startswith("DEPRECATED:")
    assert "currency_code" in legacy_field.description


@pytest.mark.integration
def test_apply_all_is_idempotent(bq_test_dataset, bq_client, trades_table):
    """Proves that running apply_all() twice produces identical results.

    The second invocation must return already_applied=True for every migration
    and must not raise any errors. The BQ table schema must not have duplicate
    columns.
    """
    project = bq_test_dataset["project"]
    dataset = bq_test_dataset["dataset"]

    migrations = [
        Migration(
            version="v1",
            description="Add risk_score FLOAT64.",
            migration_type=MigrationType.ADD_NULLABLE_COLUMN,
            column_name="risk_score",
            column_type="FLOAT64",
            compatibility=CompatibilityMode.FULL,
        ),
    ]

    runner = MigrationRunner(bq_client, project, dataset, "trades")

    # First run.
    first_results = runner.apply_all(migrations)
    assert all(r.success for r in first_results)
    assert all(not r.already_applied for r in first_results)

    # BQ streaming buffer may delay availability; wait briefly.
    time.sleep(3.0)

    # Second run — all must be skipped.
    second_results = runner.apply_all(migrations)
    assert all(r.success for r in second_results)
    assert all(r.already_applied for r in second_results)

    # Schema must not have duplicate risk_score columns.
    table_id = f"{project}.{dataset}.trades"
    table = bq_client.get_table(table_id)
    risk_cols = [f for f in table.schema if f.name == "risk_score"]
    assert len(risk_cols) == 1, f"Expected 1 risk_score column, found {len(risk_cols)}"
