# ADR-002: Schema evolution + idempotent loads on BigQuery

- **Status:** Accepted
- **Date:** 2026-05-19
- **Context layer:** storage

## Context

BigQuery does not support full `ALTER TABLE` DDL. Schemas still have to evolve, and
pipeline runs retry — a retried load must not double-write. Both problems are
silent-corruption risks: a botched migration loses history, a non-idempotent load
inflates metrics. We need migration patterns that stay within BQ's actual API and a
load protocol that is safe under arbitrary retries.

## Decision

Constrain schema change to **three audited, versioned patterns** —
`ADD_NULLABLE_COLUMN` (`update_table`), `RENAME_VIA_VIEW` (aliasing view), and
`DEPRECATE_COLUMN` (description update) — each checksummed (MD5 of type+column) and
recorded in a `_migrations` audit table. Pair it with an **`IdempotentLoader`**:
pre-flight `COUNT WHERE _load_id = …`, then `MERGE … WHEN NOT MATCHED` stamping every
row with `_load_id`, deduped on `(_load_id, primary_key)`.

## Alternatives considered

| Option | Why rejected |
|---|---|
| Drop + recreate table on schema change | Destroys history and breaks every reader mid-flight. Unacceptable for append-only fact tables. |
| `WRITE_TRUNCATE` per run for "idempotency" | Idempotent only for full-refresh tables; impossible for incremental/partitioned loads and wasteful at scale. |
| Dedup downstream in a view | Pushes the cost to every reader forever and never fixes the stored duplicates. |
| Trust BQ load-job retry semantics | Load-job retries are not exactly-once across *pipeline* retries; the `_load_id` pre-flight is what closes that gap. |

## Consequences

- **Positive:** Migrations are reversible-by-design (nullable adds, view renames keep
  old data readable) and fully audited. Loads are exactly-once under retry.
- **Negative / cost:** `MERGE` is more expensive than append; the pre-flight COUNT is
  a second query per load. `RENAME_VIA_VIEW` accumulates aliasing views that need
  eventual cleanup.
- **Risk accepted:** Property-based tests (Hypothesis) cover FLOAT64/TIMESTAMP/STRING
  round-trips but not every BQ type. Precision contracts are asserted, not assumed.

## What changes at 100×

At high partition counts, the pre-flight `COUNT(*)` becomes the bottleneck — replace
it with a partitioned `_load_id` registry table or partition-pruned existence check
so the cost scales with the touched partition, not the whole table. `MERGE` cost
forces a split: high-volume append paths move to insert-only with async dedup, while
`MERGE` is reserved for low-volume upsert dimensions.
