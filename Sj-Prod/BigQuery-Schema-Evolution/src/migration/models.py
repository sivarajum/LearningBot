"""Data models for BigQuery schema migrations.

Defines the core dataclasses and enums used throughout the migration system.
Compatibility modes follow Apache Avro schema evolution conventions.
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class CompatibilityMode(Enum):
    """Avro-style schema compatibility modes.

    BACKWARD: New schema readers can read data written by old schema.
              Safe for ADD NULLABLE COLUMN — old writers omit the field,
              new readers see NULL.
    FORWARD:  Old schema readers can read data written by new schema.
              New data may have extra fields; old readers ignore them.
    FULL:     Both BACKWARD and FORWARD simultaneously. Achievable with
              purely nullable additions when the old schema has no required
              fields that are removed.
    """

    BACKWARD = "BACKWARD"
    FORWARD = "FORWARD"
    FULL = "FULL"


class MigrationType(Enum):
    """Supported BigQuery schema migration operations.

    ADD_NULLABLE_COLUMN:  Adds a new NULLABLE column to an existing table via
                          client.update_table(). BQ allows this without a full
                          table rewrite. This is BACKWARD compatible because
                          existing rows gain a NULL value for the new column.

    RENAME_VIA_VIEW:      BQ does not support in-place column renames. This
                          migration creates a view named {table}_v{version}
                          that aliases the old column to the new name, giving
                          downstream consumers a migration window.

    DEPRECATE_COLUMN:     Updates the column description to "DEPRECATED: use
                          {replacement}" via client.update_table(). The column
                          remains in the schema to avoid breaking existing
                          readers. Callers should follow up with a
                          RENAME_VIA_VIEW migration in the next cycle.
    """

    ADD_NULLABLE_COLUMN = "add_nullable_column"
    RENAME_VIA_VIEW = "rename_via_view"
    DEPRECATE_COLUMN = "deprecate_column"


@dataclass
class Migration:
    """Represents a single versioned schema migration step.

    Attributes:
        version:        Monotonically increasing identifier, e.g. "v1", "v2".
                        The runner applies migrations in lexicographic order;
                        use zero-padded integers for correctness beyond v9
                        (e.g. "v01", "v02").
        description:    Human-readable description of what this migration does
                        and why. Stored in the _migrations audit table.
        migration_type: The operation to perform on the BQ table.
        column_name:    Target column for the migration. For RENAME_VIA_VIEW
                        this is the *old* column name (source side of alias).
        column_type:    BQ standard SQL type for ADD_NULLABLE_COLUMN
                        (STRING, INT64, FLOAT64, TIMESTAMP, DATE, BOOL, etc.).
                        Ignored for RENAME_VIA_VIEW and DEPRECATE_COLUMN.
        compatibility:  Avro-style compatibility claim. The runner does not
                        enforce this automatically — it is a documentation
                        contract for downstream consumers.
        applied_at:     Timestamp set by the runner on successful application.
                        None if not yet applied.
        checksum:       MD5 hex digest of the canonical migration definition.
                        Computed from (version, migration_type, column_name,
                        column_type). Used for idempotency: if the _migrations
                        table already contains this checksum, the migration is
                        considered already-applied and skipped without error.
    """

    version: str
    description: str
    migration_type: MigrationType
    column_name: str
    column_type: Optional[str] = None
    compatibility: CompatibilityMode = CompatibilityMode.BACKWARD
    applied_at: Optional[datetime] = None
    checksum: Optional[str] = None

    def __post_init__(self) -> None:
        """Compute checksum if not provided."""
        if self.checksum is None:
            self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Compute a deterministic MD5 checksum over the migration definition.

        The checksum covers the fields that define the migration's intent:
        version, type, column name, and column type. It deliberately excludes
        description, compatibility, and applied_at so that cosmetic edits to
        a migration's description do not invalidate an already-applied run.

        Returns:
            Lowercase hex MD5 digest string (32 characters).
        """
        payload = json.dumps(
            {
                "version": self.version,
                "migration_type": self.migration_type.value,
                "column_name": self.column_name,
                "column_type": self.column_type,
            },
            sort_keys=True,
        )
        return hashlib.md5(payload.encode("utf-8")).hexdigest()


@dataclass
class MigrationResult:
    """Result of attempting to apply a single migration.

    Attributes:
        version:          Migration version identifier, mirrors Migration.version.
        success:          True if the migration was applied or was already applied.
                          False only on error (BQ API failure, permission denied, etc.).
        already_applied:  True if the migration was skipped because its checksum
                          already existed in the _migrations audit table. When True,
                          rows_written is 0 and the overall result is still a success.
        duration_seconds: Wall-clock time in seconds from start to finish of the
                          apply() call, including all BQ API round-trips.
        error:            Exception message if success is False; None otherwise.
    """

    version: str
    success: bool
    already_applied: bool
    duration_seconds: float
    error: Optional[str] = None
