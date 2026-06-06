# POC-10: BigQuery Schema Evolution + Idempotency Harness

A production-grade BigQuery schema migration runner with idempotent load jobs and
a comprehensive test suite that demonstrates real cloud API calls.

Built as part of a Data Engineering portfolio (2026-05-19).

---

## What This POC Demonstrates

### 1. Schema Migration Patterns

BigQuery does not support the full DDL ALTER TABLE semantics of traditional
databases. This POC demonstrates the three patterns that cover 95% of real
schema evolution needs:

| Pattern | BQ Operation | Avro Compatibility |
|---|---|---|
| `ADD_NULLABLE_COLUMN` | `client.update_table()` with expanded schema | FULL |
| `RENAME_VIA_VIEW` | `client.create_table()` with a view that aliases old → new | BACKWARD |
| `DEPRECATE_COLUMN` | `client.update_table()` updating field description | BACKWARD |

Each migration is versioned (v1, v2, …), checksummed (MD5 of type + column),
and recorded in a `_migrations` audit table within the same dataset.

### 2. Idempotency via `_load_id` + MERGE

The `IdempotentLoader` class provides exactly-once semantics for pipeline runs:

1. **Pre-flight check**: `SELECT COUNT(*) WHERE _load_id = '{load_id}'` — if
   the load_id already exists, the call returns immediately with
   `LoadResult(skipped=True, rows_written=0)`.
2. **MERGE write**: A `MERGE ... WHEN NOT MATCHED THEN INSERT` statement stamps
   every row with `_load_id` and deduplicates within the batch on
   `(_load_id, primary_key)`.

This two-phase protocol is safe under retries: a partial MERGE followed by a
retry will not double-insert because the pre-flight COUNT check will detect the
already-committed rows.

### 3. Property-Based Testing with Hypothesis

`tests/integration/test_property_based.py` uses the `hypothesis` library to
generate hundreds of random FLOAT64 values, TIMESTAMP values, and STRING values,
round-trip them through BigQuery, and assert precision contracts. Key findings:

- FLOAT64: No precision loss for normal doubles in [-1e307, 1e307].
- TIMESTAMP: Microsecond precision preserved; nanoseconds do not exist in Python
  `datetime` objects (the truncation documented in BQ docs is not observable
  from Python).
- STRING: Full UTF-8 preservation including multi-byte Unicode.

---

## Directory Structure

```
POC-10-BigQuery-Schema-Evolution/
├── src/
│   ├── migration/
│   │   ├── models.py       # Migration, MigrationResult, CompatibilityMode, MigrationType
│   │   ├── runner.py       # MigrationRunner: apply(), apply_all(), _ensure_migrations_table()
│   │   └── changelog.py    # ChangelogManager: add_entry(), generate_changelog()
│   └── pipeline/
│       └── load_job.py     # IdempotentLoader: load() with COUNT check + MERGE
├── tests/
│   ├── conftest.py         # Shared unit test fixtures (mock BQ client, sample migrations)
│   ├── unit/               # Offline unit tests — pytest tests/unit/ -v
│   └── integration/        # Live BQ tests — pytest tests/integration/ -m integration
├── terraform/              # BQ dataset + service account + IAM
├── CHANGELOG.md            # Schema version history
├── requirements.txt
└── pytest.ini
```

---

## Running Tests

### Unit Tests (offline, no GCP credentials needed)

```bash
pip install -r requirements.txt
pytest tests/unit/ -v
```

Expected output: all tests pass, 0 network calls.

### Integration Tests (requires GCP credentials)

Ensure Application Default Credentials are configured:

```bash
gcloud auth application-default login
```

Run all integration tests against the `ai-trading-prod` project:

```bash
pytest tests/integration/ -v --bq-project ai-trading-prod -m integration
```

Run a specific integration test file:

```bash
pytest tests/integration/test_idempotency.py -v \
    --bq-project ai-trading-prod -m integration
```

Run with coverage:

```bash
pytest tests/unit/ --cov=src --cov-report=term-missing
```

---

## The Idempotency Contract

### What is `_load_id`?

`_load_id` is a STRING column added to every data table loaded by this pipeline.
It contains a deterministic identifier for the logical load batch — typically a
pipeline run ID, a date string, or a hash of the source file.

```python
# Good: deterministic, reusable across retries
load_id = f"trades-{date.today().isoformat()}-{source_file_hash}"

# Bad: UUID generated at runtime — each retry produces a new ID
load_id = str(uuid.uuid4())  # do NOT do this
```

### Why MERGE > INSERT OVERWRITE?

| Strategy | Drawback |
|---|---|
| INSERT (no dedup) | Duplicates on retry. Not idempotent. |
| INSERT OVERWRITE (partition replace) | Wipes the entire partition. Loses data if the pipeline processes a partial day. |
| MERGE on `_load_id` | Exactly-once per `load_id`. Safe to retry. No data loss on partial runs. |

The MERGE approach adds one extra BQ slot-second per load call (the COUNT query)
but provides a strong correctness guarantee that is worth the cost.

---

## The Schema Migration Workflow

### Adding a New Migration

1. Define a `Migration` object in your pipeline configuration:

```python
from src.migration.models import Migration, MigrationType, CompatibilityMode

new_migration = Migration(
    version="v4",
    description="Add nullable settled_at TIMESTAMP for T+2 settlement tracking.",
    migration_type=MigrationType.ADD_NULLABLE_COLUMN,
    column_name="settled_at",
    column_type="TIMESTAMP",
    compatibility=CompatibilityMode.BACKWARD,
)
```

2. Append it to the migrations list in your runner entrypoint.

3. Run the migration:

```python
from google.cloud import bigquery
from src.migration.runner import MigrationRunner

client = bigquery.Client(project="ai-trading-prod")
runner = MigrationRunner(client, "ai-trading-prod", "poc10_schema_evolution", "trades")
results = runner.apply_all(all_migrations)

for r in results:
    print(f"{r.version}: {'skipped' if r.already_applied else 'applied'} in {r.duration_seconds:.3f}s")
```

4. Update CHANGELOG.md (or use `ChangelogManager.add_entry()` to auto-append).

### Migration Ordering

Migrations are applied in the order they appear in the list passed to
`apply_all()`. Use zero-padded version strings for correct lexicographic
ordering beyond v9: `v01`, `v02`, …, `v10`.

---

## BQ-Specific Gotchas

### 1. ALTER TABLE DROP COLUMN Requires a Table Copy

BigQuery does not support `ALTER TABLE ... DROP COLUMN`. To remove a column:

1. Create a new table with the desired schema.
2. `INSERT INTO new_table SELECT col1, col2, ... (omitting the dropped col) FROM old_table`.
3. Drop the old table (after validation).
4. Rename the new table to the old name (via `bq cp` or `client.copy_table()`).

This is why `DEPRECATE_COLUMN` is a safer first step — it signals deprecation
without requiring a disruptive copy operation.

### 2. Partition Expiry is in Milliseconds in the API (but days in the Console)

The `BigQuery.Dataset.default_table_expiration_ms` field is in **milliseconds**.
The Cloud Console displays days. When setting programmatically:

```python
# 90 days
dataset.default_table_expiration_ms = 90 * 24 * 60 * 60 * 1000
```

A common mistake is passing `90` (thinking it is days) which sets expiry to
90 milliseconds — tables disappear almost immediately.

### 3. Streaming Buffer Lag in Integration Tests

After `insert_rows_json()` returns success, the rows are in the streaming buffer
and are **not immediately visible to `SELECT COUNT(*)`** queries. The buffer
typically drains within 0–90 seconds but is not guaranteed.

Mitigation used in this POC's integration tests:
- All count checks use polling loops with `time.sleep(2.0)` retries.
- `MERGE` statements (DML) bypass the streaming buffer and see committed data.
- For production pipelines, use Storage Write API (committed mode) for
  predictable consistency guarantees.

### 4. MERGE Does Not Work Against Streaming Buffer Rows

`MERGE` statements can only modify rows that are **not** in the streaming buffer.
If you use `insert_rows_json` to load rows and then immediately run a MERGE to
update them, the MERGE will not see the buffered rows. Use the BigQuery Storage
Write API (committed mode) or wait for the buffer to drain before running DML.

This POC uses streaming inserts only in integration test fixtures and the
property-based tests. The `IdempotentLoader.load()` method uses MERGE for the
actual write, targeting an initially-empty table.
