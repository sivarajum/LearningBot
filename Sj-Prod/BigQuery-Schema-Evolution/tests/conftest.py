"""Shared pytest fixtures for the unit test suite.

Integration test fixtures live in tests/integration/conftest.py.
These fixtures use only stdlib and do not make any network calls.
"""

from unittest.mock import MagicMock

import pytest
from google.cloud import bigquery


@pytest.fixture()
def mock_bq_client() -> MagicMock:
    """Return a MagicMock that satisfies the google.cloud.bigquery.Client interface.

    Pre-configured behaviours:
    - get_table() returns a Table with an empty schema list.
    - query().result() returns an empty iterator by default.
    - insert_rows_json() returns [] (no errors).
    - create_table() succeeds without raising.
    - update_table() returns the table argument unchanged.
    """
    client = MagicMock(spec=bigquery.Client)

    # Default table returned by get_table — empty schema.
    default_table = MagicMock(spec=bigquery.Table)
    default_table.schema = []
    default_table.view_query = None
    client.get_table.return_value = default_table

    # Default query result — empty.
    mock_query_job = MagicMock()
    mock_query_job.result.return_value = iter([])
    mock_query_job.job_id = "bqjob_r_mock_unit_test"
    mock_query_job.num_dml_affected_rows = 0
    client.query.return_value = mock_query_job

    # insert_rows_json returns no errors by default.
    client.insert_rows_json.return_value = []

    # update_table returns the passed table by default.
    client.update_table.side_effect = lambda table, fields: table

    return client


@pytest.fixture()
def sample_migration_v1():
    """Return a pre-built ADD_NULLABLE_COLUMN migration for tests."""
    from src.migration.models import CompatibilityMode, Migration, MigrationType

    return Migration(
        version="v1",
        description="Add nullable risk_score column for downstream risk models.",
        migration_type=MigrationType.ADD_NULLABLE_COLUMN,
        column_name="risk_score",
        column_type="FLOAT64",
        compatibility=CompatibilityMode.FULL,
    )


@pytest.fixture()
def sample_migration_v2():
    """Return a pre-built RENAME_VIA_VIEW migration for tests."""
    from src.migration.models import CompatibilityMode, Migration, MigrationType

    return Migration(
        version="v2",
        description="Renamed ccy to currency_code for clarity.",
        migration_type=MigrationType.RENAME_VIA_VIEW,
        column_name="ccy:currency_code",
        compatibility=CompatibilityMode.BACKWARD,
    )


@pytest.fixture()
def sample_migration_v3():
    """Return a pre-built DEPRECATE_COLUMN migration for tests."""
    from src.migration.models import CompatibilityMode, Migration, MigrationType

    return Migration(
        version="v3",
        description="Deprecated legacy_currency_code; use currency_code instead.",
        migration_type=MigrationType.DEPRECATE_COLUMN,
        column_name="legacy_currency_code",
        compatibility=CompatibilityMode.BACKWARD,
    )
