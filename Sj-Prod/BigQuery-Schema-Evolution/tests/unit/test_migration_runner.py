"""Unit tests for MigrationRunner.

All tests use a MagicMock BQ client — no network calls are made.
Run with: pytest tests/unit/test_migration_runner.py -v

Coverage targets:
- apply() with ADD_NULLABLE_COLUMN calls client.update_table() with new schema
- apply() with RENAME_VIA_VIEW calls client.create_table() with a view
- apply() with DEPRECATE_COLUMN updates column description
- apply() with already-applied checksum returns MigrationResult(already_applied=True)
- apply_all() skips migrations whose version is in get_applied_migrations()
- apply_all() applies migrations whose version is not yet applied
- _ensure_migrations_table() calls client.create_table() when table does not exist
- _ensure_migrations_table() silently ignores Conflict (table already exists)
- Checksum is deterministic and stable across Python sessions
- MigrationResult.success=False is returned when BQ raises an exception
- apply_all() continues after a failed migration
- RENAME_VIA_VIEW raises ValueError for missing colon separator in column_name
- ADD_NULLABLE_COLUMN raises ValueError when column_type is None
- DEPRECATE_COLUMN raises ValueError when column not found in schema
- get_applied_migrations() returns empty list when _migrations table is missing
"""

from unittest.mock import MagicMock, patch

from google.api_core.exceptions import Conflict, NotFound
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

def _make_runner(mock_client: MagicMock) -> MigrationRunner:
    return MigrationRunner(
        client=mock_client,
        project="test-project",
        dataset="test_dataset",
        table="trades",
    )


def _mock_row(data: dict) -> MagicMock:
    """Create a MagicMock row that supports dict-style key access."""
    row = MagicMock()
    row.__getitem__.side_effect = data.__getitem__
    return row


def _configure_checksum_not_applied(mock_client: MagicMock) -> None:
    """Make _is_already_applied return False (count=0)."""
    count_row = _mock_row({"cnt": 0})
    mock_query_job = MagicMock()
    mock_query_job.result.return_value = iter([count_row])
    mock_query_job.job_id = "bqjob_r_unit"
    mock_query_job.num_dml_affected_rows = 1
    mock_client.query.return_value = mock_query_job


def _configure_checksum_already_applied(mock_client: MagicMock) -> None:
    """Make _is_already_applied return True (count=1)."""
    count_row = _mock_row({"cnt": 1})
    mock_query_job = MagicMock()
    mock_query_job.result.return_value = iter([count_row])
    mock_query_job.job_id = "bqjob_r_unit_exists"
    mock_client.query.return_value = mock_query_job


# ---------------------------------------------------------------------------
# Tests: _ensure_migrations_table
# ---------------------------------------------------------------------------

class TestEnsureMigrationsTable:
    def test_creates_table_when_not_exists(self, mock_bq_client):
        """_ensure_migrations_table calls create_table when no table exists."""
        runner = _make_runner(mock_bq_client)
        runner._ensure_migrations_table()
        mock_bq_client.create_table.assert_called_once()
        created_table_arg = mock_bq_client.create_table.call_args[0][0]
        # Assert it is a Table object targeting the _migrations table.
        assert "_migrations" in (created_table_arg.full_table_id or "") or \
               "_migrations" in str(mock_bq_client.create_table.call_args)

    def test_ignores_conflict_when_table_exists(self, mock_bq_client):
        """_ensure_migrations_table silently ignores Conflict (table already exists)."""
        mock_bq_client.create_table.side_effect = Conflict("already exists")
        runner = _make_runner(mock_bq_client)
        # Should not raise.
        runner._ensure_migrations_table()
        mock_bq_client.create_table.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: apply() — ADD_NULLABLE_COLUMN
# ---------------------------------------------------------------------------

class TestApplyAddNullableColumn:
    def test_calls_update_table_with_new_column(self, mock_bq_client, sample_migration_v1):
        """ADD_NULLABLE_COLUMN calls client.update_table() with expanded schema."""
        existing_field = bigquery.SchemaField("trade_id", "STRING", mode="REQUIRED")
        existing_table = MagicMock(spec=bigquery.Table)
        existing_table.schema = [existing_field]
        mock_bq_client.get_table.return_value = existing_table

        _configure_checksum_not_applied(mock_bq_client)

        runner = _make_runner(mock_bq_client)
        runner.apply(sample_migration_v1)

        # update_table must be called.
        assert mock_bq_client.update_table.called, "update_table was not called"
        # The table schema passed to update_table should have 2 fields.
        updated_table = mock_bq_client.update_table.call_args[0][0]
        assert len(updated_table.schema) == 2
        new_field_names = [f.name for f in updated_table.schema]
        assert "risk_score" in new_field_names

    def test_new_column_is_nullable(self, mock_bq_client, sample_migration_v1):
        """ADD_NULLABLE_COLUMN creates the new field with NULLABLE mode."""
        existing_table = MagicMock(spec=bigquery.Table)
        existing_table.schema = []
        mock_bq_client.get_table.return_value = existing_table
        _configure_checksum_not_applied(mock_bq_client)

        runner = _make_runner(mock_bq_client)
        runner.apply(sample_migration_v1)

        updated_table = mock_bq_client.update_table.call_args[0][0]
        risk_field = next(f for f in updated_table.schema if f.name == "risk_score")
        assert risk_field.mode == "NULLABLE"
        assert risk_field.field_type == "FLOAT64"

    def test_returns_success_result(self, mock_bq_client, sample_migration_v1):
        """apply() returns MigrationResult(success=True) on ADD_NULLABLE_COLUMN."""
        existing_table = MagicMock(spec=bigquery.Table)
        existing_table.schema = []
        mock_bq_client.get_table.return_value = existing_table
        _configure_checksum_not_applied(mock_bq_client)

        runner = _make_runner(mock_bq_client)
        result = runner.apply(sample_migration_v1)

        assert result.success is True
        assert result.already_applied is False
        assert result.version == "v1"
        assert result.error is None
        assert result.duration_seconds >= 0.0

    def test_raises_value_error_when_column_type_missing(self, mock_bq_client):
        """ADD_NULLABLE_COLUMN raises ValueError if column_type is None."""

        bad_migration = Migration(
            version="v99",
            description="Missing type",
            migration_type=MigrationType.ADD_NULLABLE_COLUMN,
            column_name="some_col",
            column_type=None,
        )
        existing_table = MagicMock(spec=bigquery.Table)
        existing_table.schema = []
        mock_bq_client.get_table.return_value = existing_table
        _configure_checksum_not_applied(mock_bq_client)

        runner = _make_runner(mock_bq_client)
        result = runner.apply(bad_migration)

        # ValueError is caught internally and returned as a failed result.
        assert result.success is False
        assert "column_type" in result.error or "required" in result.error.lower()


# ---------------------------------------------------------------------------
# Tests: apply() — RENAME_VIA_VIEW
# ---------------------------------------------------------------------------

class TestApplyRenameViaView:
    def _setup(self, mock_bq_client):
        existing_field = bigquery.SchemaField("ccy", "STRING", mode="REQUIRED")
        amount_field = bigquery.SchemaField("amount", "FLOAT64", mode="REQUIRED")
        existing_table = MagicMock(spec=bigquery.Table)
        existing_table.schema = [existing_field, amount_field]
        mock_bq_client.get_table.return_value = existing_table
        _configure_checksum_not_applied(mock_bq_client)

    def test_calls_create_table_with_view(self, mock_bq_client, sample_migration_v2):
        """RENAME_VIA_VIEW calls client.create_table() with a view object."""
        self._setup(mock_bq_client)
        runner = _make_runner(mock_bq_client)
        result = runner.apply(sample_migration_v2)

        assert mock_bq_client.create_table.called
        assert result.success is True

    def test_view_contains_alias(self, mock_bq_client, sample_migration_v2):
        """The view query must contain 'ccy AS currency_code'."""
        self._setup(mock_bq_client)
        runner = _make_runner(mock_bq_client)
        runner.apply(sample_migration_v2)

        created_view = mock_bq_client.create_table.call_args[0][0]
        assert "currency_code" in created_view.view_query
        assert "ccy" in created_view.view_query

    def test_raises_value_error_without_colon(self, mock_bq_client):
        """RENAME_VIA_VIEW raises ValueError if column_name lacks colon separator."""

        bad_migration = Migration(
            version="v2",
            description="Bad rename",
            migration_type=MigrationType.RENAME_VIA_VIEW,
            column_name="ccy_no_colon",
        )
        existing_table = MagicMock(spec=bigquery.Table)
        existing_table.schema = [bigquery.SchemaField("ccy_no_colon", "STRING")]
        mock_bq_client.get_table.return_value = existing_table
        _configure_checksum_not_applied(mock_bq_client)

        runner = _make_runner(mock_bq_client)
        result = runner.apply(bad_migration)

        assert result.success is False
        assert "RENAME_VIA_VIEW" in result.error or "old:new" in result.error

    def test_updates_existing_view_on_conflict(self, mock_bq_client, sample_migration_v2):
        """If create_table raises Conflict, the view is updated in place."""
        self._setup(mock_bq_client)
        mock_bq_client.create_table.side_effect = Conflict("view exists")
        existing_view = MagicMock(spec=bigquery.Table)
        existing_view.view_query = ""
        mock_bq_client.get_table.side_effect = [
            mock_bq_client.get_table.return_value,  # first call for schema
            existing_view,  # second call inside except block
        ]
        # Reset side_effect for get_table after setUp
        original_table = MagicMock(spec=bigquery.Table)
        original_table.schema = [
            bigquery.SchemaField("ccy", "STRING", mode="REQUIRED"),
        ]
        mock_bq_client.get_table.side_effect = None
        mock_bq_client.get_table.return_value = original_table
        mock_bq_client.create_table.side_effect = Conflict("view exists")

        runner = _make_runner(mock_bq_client)
        result = runner.apply(sample_migration_v2)

        # update_table must be called since create_table conflicted.
        assert mock_bq_client.update_table.called
        assert result.success is True


# ---------------------------------------------------------------------------
# Tests: apply() — DEPRECATE_COLUMN
# ---------------------------------------------------------------------------

class TestApplyDeprecateColumn:
    def _setup(self, mock_bq_client):
        legacy_field = bigquery.SchemaField(
            "legacy_currency_code", "STRING", mode="NULLABLE", description=""
        )
        existing_table = MagicMock(spec=bigquery.Table)
        existing_table.schema = [legacy_field]
        mock_bq_client.get_table.return_value = existing_table
        _configure_checksum_not_applied(mock_bq_client)

    def test_calls_update_table(self, mock_bq_client, sample_migration_v3):
        """DEPRECATE_COLUMN calls client.update_table()."""
        self._setup(mock_bq_client)
        runner = _make_runner(mock_bq_client)
        result = runner.apply(sample_migration_v3)

        assert mock_bq_client.update_table.called
        assert result.success is True

    def test_deprecated_description_set(self, mock_bq_client, sample_migration_v3):
        """DEPRECATE_COLUMN sets field description to 'DEPRECATED: use ...'."""
        self._setup(mock_bq_client)
        # Capture what was passed to update_table.
        captured = {}
        def capture_update(table, fields):
            captured["table"] = table
            return table
        mock_bq_client.update_table.side_effect = capture_update

        runner = _make_runner(mock_bq_client)
        runner.apply(sample_migration_v3)

        updated_schema = captured["table"].schema
        deprecated_field = next(
            (f for f in updated_schema if f.name == "legacy_currency_code"), None
        )
        assert deprecated_field is not None
        assert deprecated_field.description.startswith("DEPRECATED:")

    def test_raises_value_error_for_missing_column(self, mock_bq_client):
        """DEPRECATE_COLUMN raises ValueError if column is not in schema."""

        bad_migration = Migration(
            version="v3",
            description="Deprecate nonexistent; use other",
            migration_type=MigrationType.DEPRECATE_COLUMN,
            column_name="nonexistent_col",
        )
        existing_table = MagicMock(spec=bigquery.Table)
        existing_table.schema = [bigquery.SchemaField("trade_id", "STRING")]
        mock_bq_client.get_table.return_value = existing_table
        _configure_checksum_not_applied(mock_bq_client)

        runner = _make_runner(mock_bq_client)
        result = runner.apply(bad_migration)

        assert result.success is False
        assert "nonexistent_col" in result.error


# ---------------------------------------------------------------------------
# Tests: idempotency (already-applied checksum)
# ---------------------------------------------------------------------------

class TestIdempotency:
    def test_already_applied_returns_skipped_result(self, mock_bq_client, sample_migration_v1):
        """apply() returns already_applied=True when checksum exists in _migrations."""
        _configure_checksum_already_applied(mock_bq_client)
        runner = _make_runner(mock_bq_client)
        result = runner.apply(sample_migration_v1)

        assert result.already_applied is True
        assert result.success is True
        assert result.version == "v1"
        # update_table must NOT be called.
        mock_bq_client.update_table.assert_not_called()

    def test_checksum_is_deterministic(self, sample_migration_v1):
        """Same migration definition always produces the same checksum."""

        migration_copy = Migration(
            version="v1",
            description="Different description should not change checksum",
            migration_type=MigrationType.ADD_NULLABLE_COLUMN,
            column_name="risk_score",
            column_type="FLOAT64",
            compatibility=CompatibilityMode.FULL,
        )
        assert migration_copy.checksum == sample_migration_v1.checksum


# ---------------------------------------------------------------------------
# Tests: apply_all()
# ---------------------------------------------------------------------------

class TestApplyAll:
    def test_skips_already_applied_versions(self, mock_bq_client, sample_migration_v1):
        """apply_all() skips migrations whose version is in get_applied_migrations()."""
        version_row = _mock_row({"version": "v1"})
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = iter([version_row])
        mock_bq_client.query.return_value = mock_query_job

        runner = _make_runner(mock_bq_client)
        results = runner.apply_all([sample_migration_v1])

        assert len(results) == 1
        assert results[0].already_applied is True
        # update_table must never be called for a skipped migration.
        mock_bq_client.update_table.assert_not_called()

    def test_applies_new_migrations(self, mock_bq_client, sample_migration_v1):
        """apply_all() applies migrations not in get_applied_migrations()."""
        # First query (get_applied_migrations): returns empty set.
        empty_job = MagicMock()
        empty_job.result.return_value = iter([])
        # Second query (idempotency checksum check): returns count=0.
        count_row = _mock_row({"cnt": 0})
        count_job = MagicMock()
        count_job.result.return_value = iter([count_row])
        count_job.job_id = "bqjob_r_unit"
        count_job.num_dml_affected_rows = 0

        mock_bq_client.query.side_effect = [empty_job, count_job]

        existing_table = MagicMock(spec=bigquery.Table)
        existing_table.schema = []
        mock_bq_client.get_table.return_value = existing_table

        runner = _make_runner(mock_bq_client)
        results = runner.apply_all([sample_migration_v1])

        assert len(results) == 1
        assert results[0].success is True
        assert results[0].already_applied is False

    def test_continues_after_failed_migration(self, mock_bq_client):
        """apply_all() continues applying remaining migrations after one fails."""

        failing_migration = Migration(
            version="v1",
            description="Will fail",
            migration_type=MigrationType.ADD_NULLABLE_COLUMN,
            column_name="bad_col",
            column_type=None,  # Will cause ValueError
        )
        passing_migration = Migration(
            version="v2",
            description="Will succeed",
            migration_type=MigrationType.ADD_NULLABLE_COLUMN,
            column_name="good_col",
            column_type="STRING",
        )

        # Both queries (checksum checks) return count=0.
        def make_count_job(count):
            row = _mock_row({"cnt": count})
            job = MagicMock()
            job.result.return_value = iter([row])
            job.job_id = "bqjob_r_unit"
            job.num_dml_affected_rows = 0
            return job

        mock_bq_client.query.side_effect = [
            make_count_job(0),  # get_applied_migrations -> empty (but we use side_effect)
            make_count_job(0),  # checksum check for v1
            make_count_job(0),  # checksum check for v2
        ]

        existing_table = MagicMock(spec=bigquery.Table)
        existing_table.schema = []
        mock_bq_client.get_table.return_value = existing_table

        # Override apply_all with manual mock for get_applied_migrations
        runner = _make_runner(mock_bq_client)

        # Patch get_applied_migrations to return empty list.
        with patch.object(runner, "get_applied_migrations", return_value=[]):
            results = runner.apply_all([failing_migration, passing_migration])

        assert len(results) == 2
        assert results[0].success is False   # failing_migration failed
        assert results[1].success is True    # passing_migration succeeded


# ---------------------------------------------------------------------------
# Tests: get_applied_migrations()
# ---------------------------------------------------------------------------

class TestGetAppliedMigrations:
    def test_returns_empty_list_on_not_found(self, mock_bq_client):
        """get_applied_migrations() returns [] when _migrations table doesn't exist."""
        # Conflict on create_table is normal; query raises NotFound.
        mock_bq_client.create_table.side_effect = Conflict("exists")
        mock_query_job = MagicMock()
        mock_query_job.result.side_effect = NotFound("_migrations")
        mock_bq_client.query.return_value = mock_query_job

        runner = _make_runner(mock_bq_client)
        versions = runner.get_applied_migrations()

        assert versions == []

    def test_returns_version_list(self, mock_bq_client):
        """get_applied_migrations() returns sorted list of applied versions."""
        rows = [_mock_row({"version": "v1"}), _mock_row({"version": "v2"})]
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = iter(rows)
        mock_bq_client.query.return_value = mock_query_job

        runner = _make_runner(mock_bq_client)
        # Suppress create_table call (Conflict = already exists).
        mock_bq_client.create_table.side_effect = Conflict("exists")
        versions = runner.get_applied_migrations()

        assert versions == ["v1", "v2"]


# ---------------------------------------------------------------------------
# Tests: BQ exception propagation
# ---------------------------------------------------------------------------

class TestExceptionHandling:
    def test_bq_api_error_returns_failed_result(self, mock_bq_client, sample_migration_v1):
        """apply() returns MigrationResult(success=False) when BQ raises an error."""
        from google.api_core.exceptions import BadRequest

        _configure_checksum_not_applied(mock_bq_client)
        existing_table = MagicMock(spec=bigquery.Table)
        existing_table.schema = []
        mock_bq_client.get_table.return_value = existing_table
        mock_bq_client.update_table.side_effect = BadRequest("invalid schema")

        runner = _make_runner(mock_bq_client)
        result = runner.apply(sample_migration_v1)

        assert result.success is False
        assert "invalid schema" in result.error
        assert result.version == "v1"
