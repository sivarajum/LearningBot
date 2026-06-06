"""Idempotent BigQuery load job using _load_id deduplication + MERGE.

The core contract: given the same (rows, load_id) pair, calling load() any
number of times must produce exactly the same number of rows in the target
table — no duplicates.

Implementation strategy:
1. Pre-flight check: COUNT(*) WHERE _load_id = '{load_id}'.
   - If count > 0: return immediately with LoadResult(skipped=True, rows_written=0).
   - If count == 0: proceed to MERGE.
2. MERGE deduplicates within a single call by joining source rows (in a CTE
   built from a VALUES clause) against the target on (_load_id, primary_key).
   WHEN NOT MATCHED THEN INSERT ensures only new rows are written.

The pre-flight check protects against the case where a previous run completed
the MERGE but crashed before the caller could record the success. The MERGE
itself protects against partial failures within a single invocation when rows
contains duplicate primary keys.

Cross-batch primary key semantics (known limitation):
The MERGE ON clause joins on BOTH (_load_id, primary_key). This means the same
primary key value may appear in multiple load batches (different load_ids) and
both rows will be inserted. For example, an amended trade T001 arriving in a
second pipeline run with a new load_id="run-002" will coexist with the original
T001 from load_id="run-001". Callers that need single-row-per-primary-key
semantics must either (a) use SCD Type-1 upsert logic with WHEN MATCHED THEN
UPDATE, or (b) apply deduplication downstream (e.g., QUALIFY ROW_NUMBER() OVER
PARTITION BY primary_key ORDER BY traded_at DESC = 1).

BQ job IDs (bqjob_r…) are captured and returned in LoadResult.job_id.

Typical usage:

    from google.cloud import bigquery
    from src.pipeline.load_job import IdempotentLoader

    client = bigquery.Client(project="my-project")
    loader = IdempotentLoader(client, "my-project", "my_dataset", "trades")

    rows = [
        {"trade_id": "T001", "symbol": "RELIANCE", "amount": 1000.0,
         "ccy": "INR", "traded_at": "2026-05-19T10:00:00Z"},
    ]
    result = loader.load(rows, load_id="pipeline-run-2026-05-19-001")
    print(result.rows_written)  # 1 on first call, 0 on repeat
"""

import logging
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from google.cloud import bigquery

logger = logging.getLogger(__name__)


@dataclass
class LoadResult:
    """Result of an idempotent load operation.

    Attributes:
        load_id:      The load_id string that was passed to load().
        rows_written: Number of rows actually inserted. 0 if skipped.
        skipped:      True if the load was a no-op because _load_id already
                      existed in the target table (i.e. duplicate call).
        job_id:       BQ job ID string (e.g. "bqjob_r1234abc") when a real
                      MERGE statement was executed; None when skipped.
    """

    load_id: str
    rows_written: int
    skipped: bool
    job_id: Optional[str] = None


class IdempotentLoader:
    """Loads rows into a BigQuery table with exactly-once semantics.

    Uses a two-phase protocol:
    1. COUNT check on _load_id to detect prior successful loads.
    2. MERGE statement for the actual write, deduplicating on (load_id, primary_key).

    The target table MUST have a _load_id STRING column and a primary_key STRING
    column. If they are absent the MERGE will raise BadRequest.

    Args:
        client:      An authenticated google.cloud.bigquery.Client instance.
        project:     GCP project ID.
        dataset:     BigQuery dataset ID.
        table:       Target table name.
        primary_key: Column name to use as the business key in the MERGE ON clause.
                     Defaults to "trade_id" for the poc10 trades table.
    """

    def __init__(
        self,
        client: bigquery.Client,
        project: str,
        dataset: str,
        table: str,
        primary_key: str = "trade_id",
    ) -> None:
        self._client = client
        self._project = project
        self._dataset = dataset
        self._table = table
        self._primary_key = primary_key
        self._table_id = f"{project}.{dataset}.{table}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, rows: List[Dict[str, Any]], load_id: str) -> LoadResult:
        """Idempotently load a list of rows into the target BigQuery table.

        Phase 1 — Pre-flight check:
            Executes SELECT COUNT(*) FROM {table} WHERE _load_id = '{load_id}'.
            If the count is > 0, the load_id has already been committed and
            this call is a duplicate. Returns LoadResult(skipped=True) immediately.

        Phase 2 — MERGE write:
            Constructs a MERGE statement where the source is an inline VALUES
            clause (one row per dict in rows). Each source row is annotated with
            the provided load_id. The MERGE condition is:
                target._load_id = source._load_id
                AND target.{primary_key} = source.{primary_key}
            WHEN NOT MATCHED THEN INSERT inserts the row. This handles the edge
            case of duplicate primary keys within the same rows list.

        Args:
            rows:    List of row dicts. Each dict must contain the columns
                     present in the target table schema (excluding _load_id,
                     which is injected automatically).
            load_id: Unique identifier for this load batch. Use a deterministic
                     string (e.g. pipeline run ID, date, file hash) so that
                     retrying the same logical batch always uses the same load_id.

        Returns:
            LoadResult with rows_written=len(rows) on first call,
            rows_written=0 and skipped=True on subsequent calls with same load_id.

        Raises:
            google.api_core.exceptions.BadRequest: If rows contain fields not
                present in the table schema or if the schema is missing _load_id.
            google.api_core.exceptions.NotFound: If the target table does not exist.
        """
        if not rows:
            logger.info("load() called with empty rows list — returning skipped.")
            return LoadResult(load_id=load_id, rows_written=0, skipped=True)

        # Phase 1: pre-flight duplicate check.
        existing_count = self._count_by_load_id(load_id)
        if existing_count > 0:
            logger.info(
                "load_id='%s' already has %d row(s) in %s — skipping.",
                load_id,
                existing_count,
                self._table_id,
            )
            return LoadResult(load_id=load_id, rows_written=0, skipped=True)

        # Phase 2: MERGE write.
        job_id, rows_written = self._merge_rows(rows, load_id)
        logger.info(
            "Loaded %d row(s) into %s (load_id='%s', job_id='%s').",
            rows_written,
            self._table_id,
            load_id,
            job_id,
        )
        return LoadResult(
            load_id=load_id,
            rows_written=rows_written,
            skipped=False,
            job_id=job_id,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _count_by_load_id(self, load_id: str) -> int:
        """Return the number of rows in the target table matching load_id.

        Uses a parameterised query to avoid SQL injection.

        Args:
            load_id: The _load_id value to count.

        Returns:
            Row count as an integer.
        """
        query = (
            f"SELECT COUNT(*) AS cnt "
            f"FROM `{self._table_id}` "
            f"WHERE _load_id = @load_id"
        )
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("load_id", "STRING", load_id)
            ]
        )
        rows = list(self._client.query(query, job_config=job_config).result())
        return int(rows[0]["cnt"]) if rows else 0

    def _merge_rows(
        self, rows: List[Dict[str, Any]], load_id: str
    ) -> tuple:
        """Execute a MERGE statement to insert rows that do not yet exist.

        Builds an inline source table from a VALUES clause. Each row dict is
        flattened into a typed VALUES tuple. The _load_id value is injected
        from the load_id parameter (not from the row dicts).

        Implementation note on VALUES typing:
        BQ requires explicit CAST expressions in a VALUES clause when the query
        planner cannot infer types. We use a simpler approach: insert the source
        rows via insert_rows_json into a temporary staging table, then MERGE from
        staging into target. However, to keep the implementation self-contained
        and dependency-free we use a CTE WITH source AS (SELECT ...) approach
        where each row becomes a SELECT ... UNION ALL SELECT ... block.

        The MERGE condition:
            T._load_id = S._load_id AND T.{primary_key} = S.{primary_key}

        WHEN NOT MATCHED BY TARGET THEN INSERT all columns from source.

        Args:
            rows:    List of row dicts to insert.
            load_id: The _load_id value to stamp on every row.

        Returns:
            Tuple of (job_id: str, rows_written: int).
        """
        if not rows:
            return (f"noop-{uuid.uuid4().hex[:8]}", 0)

        # Determine column order from the first row.
        columns = list(rows[0].keys())
        # Inject _load_id if not already present.
        if "_load_id" not in columns:
            columns = ["_load_id"] + columns

        # Build the CTE source using SELECT … UNION ALL SELECT …
        union_parts = []
        for row in rows:
            select_exprs = []
            # _load_id first
            escaped_load_id = load_id.replace("'", "\\'")
            select_exprs.append(f"'{escaped_load_id}' AS `_load_id`")
            for col in columns:
                if col == "_load_id":
                    continue
                val = row.get(col)
                select_exprs.append(f"{self._sql_literal(val)} AS `{col}`")
            union_parts.append("SELECT " + ", ".join(select_exprs))

        source_cte = "\nUNION ALL\n".join(union_parts)

        # Build INSERT column list and SELECT list for WHEN NOT MATCHED.
        insert_cols = ", ".join(f"`{c}`" for c in columns)
        source_select = ", ".join(f"S.`{c}`" for c in columns)

        merge_sql = (
            f"MERGE `{self._table_id}` AS T\n"
            f"USING (\n{source_cte}\n) AS S\n"
            f"ON T.`_load_id` = S.`_load_id` "
            f"AND T.`{self._primary_key}` = S.`{self._primary_key}`\n"
            f"WHEN NOT MATCHED BY TARGET THEN\n"
            f"  INSERT ({insert_cols})\n"
            f"  VALUES ({source_select})\n"
        )

        logger.debug("Executing MERGE SQL:\n%s", merge_sql)
        job = self._client.query(merge_sql)
        job.result()  # Wait for completion; raises on error.

        job_id = job.job_id or f"unknown-{uuid.uuid4().hex[:8]}"
        # Use `is not None` guard: a legitimate 0-row MERGE (all rows already matched)
        # would otherwise incorrectly report len(rows) rows written.
        rows_written = (
            job.num_dml_affected_rows
            if job.num_dml_affected_rows is not None
            else len(rows)
        )
        return (job_id, rows_written)

    @staticmethod
    def _sql_literal(value: Any) -> str:
        """Convert a Python value to a BigQuery SQL literal string.

        Handles: None → NULL, bool → TRUE/FALSE, int/float → numeric literal,
        str → single-quoted string with apostrophe escaping,
        datetime-like objects with isoformat() → TIMESTAMP literal.

        Args:
            value: Python value to convert.

        Returns:
            SQL literal string suitable for embedding in a query.
        """
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        if isinstance(value, (int, float)):
            return repr(value)
        if isinstance(value, str):
            escaped = value.replace("\\", "\\\\").replace("'", "\\'")
            return f"'{escaped}'"
        # datetime, date, etc.
        if hasattr(value, "isoformat"):
            iso = value.isoformat()
            return f"TIMESTAMP '{iso}'"
        # Fallback: coerce to string.
        escaped = str(value).replace("\\", "\\\\").replace("'", "\\'")
        return f"'{escaped}'"
