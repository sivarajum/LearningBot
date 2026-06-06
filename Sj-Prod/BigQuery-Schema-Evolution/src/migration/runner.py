"""BigQuery schema migration runner.

Applies versioned DDL migrations to BigQuery tables in an idempotent fashion.
Each applied migration is recorded in a _migrations audit table within the same
dataset, keyed by checksum so that re-running the same migration set is safe.

Typical usage:

    from google.cloud import bigquery
    from src.migration.runner import MigrationRunner
    from src.migration.models import Migration, MigrationType, CompatibilityMode

    client = bigquery.Client(project="my-project")
    runner = MigrationRunner(client, "my-project", "my_dataset", "trades")

    migrations = [
        Migration(
            version="v1",
            description="Add nullable risk_score column",
            migration_type=MigrationType.ADD_NULLABLE_COLUMN,
            column_name="risk_score",
            column_type="FLOAT64",
            compatibility=CompatibilityMode.FULL,
        ),
    ]
    results = runner.apply_all(migrations)
"""

import logging
import time
from datetime import datetime, timezone
from typing import List, Optional

from google.api_core.exceptions import Conflict, NotFound
from google.cloud import bigquery

from .models import Migration, MigrationResult, MigrationType

logger = logging.getLogger(__name__)

# BQ standard SQL schema for the _migrations audit table.
_MIGRATIONS_TABLE_SCHEMA = [
    bigquery.SchemaField("version", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("checksum", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("applied_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("migration_type", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("compatibility", "STRING", mode="NULLABLE"),
]


class MigrationRunner:
    """Applies schema migrations to a BigQuery table with idempotency guarantees.

    The runner maintains a _migrations audit table in the same dataset as the
    target table. Before applying any migration it checks whether the migration's
    checksum already exists in _migrations; if so, the migration is skipped.

    Args:
        client:  An authenticated google.cloud.bigquery.Client instance.
        project: GCP project ID that owns the dataset.
        dataset: BigQuery dataset ID.
        table:   Target table name within the dataset.
    """

    def __init__(
        self,
        client: bigquery.Client,
        project: str,
        dataset: str,
        table: str,
    ) -> None:
        self._client = client
        self._project = project
        self._dataset = dataset
        self._table = table
        self._migrations_table_id = (
            f"{project}.{dataset}._migrations"
        )
        self._target_table_id = f"{project}.{dataset}.{table}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_applied_migrations(self) -> List[str]:
        """Return the list of version strings that have already been applied.

        Reads from the _migrations audit table. If the table does not exist yet
        it returns an empty list (bootstrapping case).

        Returns:
            List of version strings, e.g. ["v1", "v2"], in the order they were
            inserted into the audit table (ascending applied_at).
        """
        self._ensure_migrations_table()
        query = (
            f"SELECT version FROM `{self._migrations_table_id}` "
            f"ORDER BY applied_at ASC"
        )
        try:
            rows = list(self._client.query(query).result())
            versions = [row["version"] for row in rows]
            logger.debug(
                "Found %d applied migration(s): %s", len(versions), versions
            )
            return versions
        except NotFound:
            logger.warning(
                "_migrations table not found during get_applied_migrations; "
                "returning empty list."
            )
            return []

    def apply(self, migration: Migration) -> MigrationResult:
        """Apply a single migration, recording the result in the audit table.

        The method is idempotent: if the migration's checksum already exists in
        the _migrations table the call returns immediately with
        MigrationResult(already_applied=True, success=True) without touching
        the target table schema.

        Args:
            migration: The Migration instance to apply.

        Returns:
            MigrationResult describing the outcome.
        """
        start = time.monotonic()
        self._ensure_migrations_table()

        # Idempotency check: look up by checksum, not just version.
        if self._is_already_applied(migration.checksum):
            duration = time.monotonic() - start
            logger.info(
                "Migration %s (checksum=%s) already applied — skipping.",
                migration.version,
                migration.checksum,
            )
            return MigrationResult(
                version=migration.version,
                success=True,
                already_applied=True,
                duration_seconds=duration,
            )

        logger.info(
            "Applying migration %s: %s", migration.version, migration.description
        )
        try:
            if migration.migration_type == MigrationType.ADD_NULLABLE_COLUMN:
                self._add_nullable_column(migration)
            elif migration.migration_type == MigrationType.RENAME_VIA_VIEW:
                self._rename_via_view(migration)
            elif migration.migration_type == MigrationType.DEPRECATE_COLUMN:
                self._deprecate_column(migration)
            else:
                raise ValueError(
                    f"Unsupported migration type: {migration.migration_type}"
                )

            applied_at = datetime.now(tz=timezone.utc)
            migration.applied_at = applied_at
            self._record_migration(migration)

            duration = time.monotonic() - start
            logger.info(
                "Migration %s applied successfully in %.3fs.",
                migration.version,
                duration,
            )
            return MigrationResult(
                version=migration.version,
                success=True,
                already_applied=False,
                duration_seconds=duration,
            )

        except Exception as exc:  # pylint: disable=broad-except
            duration = time.monotonic() - start
            logger.error(
                "Migration %s failed after %.3fs: %s",
                migration.version,
                duration,
                exc,
                exc_info=True,
            )
            return MigrationResult(
                version=migration.version,
                success=False,
                already_applied=False,
                duration_seconds=duration,
                error=str(exc),
            )

    def apply_all(self, migrations: List[Migration]) -> List[MigrationResult]:
        """Apply a list of migrations in order, skipping already-applied ones.

        Migrations are applied in the order provided. If any migration fails,
        subsequent migrations are still attempted (fail-forward strategy). The
        caller should inspect each MigrationResult.success to determine whether
        manual intervention is required.

        Args:
            migrations: Ordered list of Migration objects to apply.

        Returns:
            List of MigrationResult objects, one per input migration, in the
            same order as the input list.
        """
        applied_versions = set(self.get_applied_migrations())
        results: List[MigrationResult] = []

        for migration in migrations:
            if migration.version in applied_versions:
                logger.info(
                    "Migration %s already in applied set — skipping.",
                    migration.version,
                )
                results.append(
                    MigrationResult(
                        version=migration.version,
                        success=True,
                        already_applied=True,
                        duration_seconds=0.0,
                    )
                )
                continue

            result = self.apply(migration)
            results.append(result)

            if not result.success:
                logger.warning(
                    "Migration %s failed; continuing with remaining migrations.",
                    migration.version,
                )

        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _ensure_migrations_table(self) -> None:
        """Create the _migrations audit table if it does not already exist.

        Uses google.api_core.exceptions.Conflict to handle the race condition
        where two processes attempt to create the table simultaneously.
        """
        table_ref = bigquery.Table(
            self._migrations_table_id,
            schema=_MIGRATIONS_TABLE_SCHEMA,
        )
        try:
            self._client.create_table(table_ref)
            logger.info("Created _migrations audit table: %s", self._migrations_table_id)
        except Conflict:
            # Table already exists — expected on every run after the first.
            logger.debug(
                "_migrations table already exists: %s", self._migrations_table_id
            )

    def _is_already_applied(self, checksum: Optional[str]) -> bool:
        """Check whether a migration with the given checksum has been applied.

        Args:
            checksum: MD5 hex digest of the migration definition.

        Returns:
            True if a row with this checksum exists in _migrations.
        """
        if checksum is None:
            return False
        query = (
            f"SELECT COUNT(*) AS cnt "
            f"FROM `{self._migrations_table_id}` "
            f"WHERE checksum = @checksum"
        )
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("checksum", "STRING", checksum)
            ]
        )
        rows = list(self._client.query(query, job_config=job_config).result())
        count = rows[0]["cnt"] if rows else 0
        return count > 0

    def _get_target_table(self) -> bigquery.Table:
        """Fetch the current Table object for the migration target.

        Returns:
            A google.cloud.bigquery.Table instance with the current schema.

        Raises:
            google.api_core.exceptions.NotFound: If the table does not exist.
        """
        return self._client.get_table(self._target_table_id)

    def _add_nullable_column(self, migration: Migration) -> None:
        """Add a new NULLABLE column to the target table.

        BigQuery allows adding NULLABLE columns without a table copy. The new
        column will return NULL for all existing rows.

        Args:
            migration: Migration with migration_type=ADD_NULLABLE_COLUMN.
                       migration.column_name and migration.column_type must be set.

        Raises:
            ValueError: If column_type is not specified.
            google.api_core.exceptions.BadRequest: If the column already exists
                or the type is invalid.
        """
        if not migration.column_type:
            raise ValueError(
                f"column_type is required for ADD_NULLABLE_COLUMN migration "
                f"(version={migration.version})"
            )

        table = self._get_target_table()
        new_field = bigquery.SchemaField(
            migration.column_name,
            migration.column_type,
            mode="NULLABLE",
            description=migration.description,
        )
        updated_schema = list(table.schema) + [new_field]
        table.schema = updated_schema

        self._client.update_table(table, ["schema"])
        logger.info(
            "Added NULLABLE column %s %s to %s.",
            migration.column_name,
            migration.column_type,
            self._target_table_id,
        )

    def _rename_via_view(self, migration: Migration) -> None:
        """Create a compatibility view that exposes the column under a new name.

        Because BigQuery does not support in-place column renames, this method
        creates (or replaces) a view named {table}_v{version_number} that
        SELECTs all columns from the base table but aliases the old column name
        to the new name encoded in migration.column_name using the convention
        "old_name:new_name".

        The view name format: {table}_v{version_numeric}
        For version="v2" → view is named "{table}_v2".

        Args:
            migration: Migration with migration_type=RENAME_VIA_VIEW.
                       migration.column_name must be "old_column:new_column".

        Raises:
            ValueError: If column_name does not contain a colon separator.
        """
        if ":" not in migration.column_name:
            raise ValueError(
                f"RENAME_VIA_VIEW requires column_name in 'old:new' format, "
                f"got: '{migration.column_name}' (version={migration.version})"
            )

        old_name, new_name = migration.column_name.split(":", 1)
        table = self._get_target_table()

        # Build SELECT list: alias the renamed column, pass through all others.
        select_parts = []
        for field in table.schema:
            if field.name == old_name:
                select_parts.append(f"`{old_name}` AS `{new_name}`")
            else:
                select_parts.append(f"`{field.name}`")

        if not any(f.name == old_name for f in table.schema):
            raise ValueError(
                f"Column '{old_name}' not found in table {self._target_table_id}. "
                f"Cannot create rename view."
            )

        view_name = f"{self._table}_v{migration.version.lstrip('v')}"
        view_id = f"{self._project}.{self._dataset}.{view_name}"
        select_clause = ", ".join(select_parts)
        view_query = f"SELECT {select_clause} FROM `{self._target_table_id}`"

        view_table = bigquery.Table(view_id)
        view_table.view_query = view_query
        view_table.description = (
            f"Compatibility view created by migration {migration.version}. "
            f"Renames '{old_name}' to '{new_name}'."
        )

        try:
            self._client.create_table(view_table)
            logger.info("Created rename view %s.", view_id)
        except Conflict:
            # View already exists — update it in place.
            existing_view = self._client.get_table(view_id)
            existing_view.view_query = view_query
            self._client.update_table(existing_view, ["view_query"])
            logger.info("Updated existing rename view %s.", view_id)

    def _deprecate_column(self, migration: Migration) -> None:
        """Mark a column as deprecated by updating its description.

        The column remains in the schema to avoid breaking existing readers.
        Its description is updated to "DEPRECATED: use {replacement}" where
        replacement is extracted from migration.description if it contains
        "use {something}", otherwise defaults to "see migration notes".

        Args:
            migration: Migration with migration_type=DEPRECATE_COLUMN.
        """
        table = self._get_target_table()

        # Parse replacement hint from description, e.g. "use currency_code".
        replacement = "see migration notes"
        lower_desc = migration.description.lower()
        if "use " in lower_desc:
            idx = lower_desc.index("use ") + 4
            replacement = migration.description[idx:].split()[0].rstrip(".,;")

        updated_schema = []
        column_found = False
        for field_obj in table.schema:
            if field_obj.name == migration.column_name:
                column_found = True
                deprecated_field = bigquery.SchemaField(
                    name=field_obj.name,
                    field_type=field_obj.field_type,
                    mode=field_obj.mode,
                    description=f"DEPRECATED: use {replacement}",
                )
                updated_schema.append(deprecated_field)
            else:
                updated_schema.append(field_obj)

        if not column_found:
            raise ValueError(
                f"Column '{migration.column_name}' not found in table "
                f"{self._target_table_id}. Cannot deprecate."
            )

        table.schema = updated_schema
        self._client.update_table(table, ["schema"])
        logger.info(
            "Deprecated column '%s' in %s (use %s).",
            migration.column_name,
            self._target_table_id,
            replacement,
        )

    def _record_migration(self, migration: Migration) -> None:
        """Insert a row into the _migrations audit table after successful apply.

        Args:
            migration: The migration that was just applied. Its applied_at
                       timestamp must be set before calling this method.
        """
        rows = [
            {
                "version": migration.version,
                "checksum": migration.checksum,
                "applied_at": migration.applied_at.isoformat()
                if migration.applied_at
                else datetime.now(tz=timezone.utc).isoformat(),
                "description": migration.description,
                "migration_type": migration.migration_type.value,
                "compatibility": migration.compatibility.value,
            }
        ]
        errors = self._client.insert_rows_json(self._migrations_table_id, rows)
        if errors:
            raise RuntimeError(
                f"Failed to record migration {migration.version} in audit table: "
                f"{errors}"
            )
        logger.debug(
            "Recorded migration %s in audit table %s.",
            migration.version,
            self._migrations_table_id,
        )
