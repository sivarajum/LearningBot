# Schema CHANGELOG — poc10_schema_evolution.trades

This file tracks every schema change applied to the `trades` table, in reverse
chronological order (newest first). Each entry includes the Avro compatibility
classification so downstream consumers can assess upgrade risk.

Compatibility modes follow Apache Avro conventions:
- **BACKWARD**: New schema readers can read data written by old schema writers.
- **FORWARD**: Old schema readers can read data written by new schema writers.
- **FULL**: Both BACKWARD and FORWARD simultaneously.

---

## v3 — 2026-05-19

**Compatibility:** BACKWARD

**Migration type:** deprecate_column

**Column:** legacy_currency_code

**Description:** Deprecated legacy_currency_code; use currency_code (v2) instead. The column
remains in the physical schema to avoid breaking existing readers. Downstream
pipelines should migrate to the `trades_v2` view (introduced in v2) which
exposes the column under the new name `currency_code`. The physical column will
be eligible for removal after the next major schema version.

---

## v2 — 2026-05-19

**Compatibility:** BACKWARD

**Migration type:** rename_via_view

**Column:** ccy -> currency_code

**Description:** Renamed `ccy` to `currency_code` for clarity and alignment with
ISO 4217 naming conventions used elsewhere in the platform. Because BigQuery
does not support in-place column renames, a compatibility view `trades_v2` was
created that aliases `ccy AS currency_code`. New consumers should query
`trades_v2`; existing consumers reading from `trades` directly continue to see
the `ccy` column name without changes.

**View created:** `poc10_schema_evolution.trades_v2`

---

## v1 — 2026-05-19

**Compatibility:** FULL

**Migration type:** add_nullable_column

**Column:** risk_score FLOAT64

**Description:** Added nullable `risk_score` FLOAT64 column for downstream risk models.
The column defaults to NULL for all existing rows. New pipelines writing risk
scores may populate this field; pipelines unaware of the field continue to
insert rows without it and receive NULL on read. This migration is FULL
compatible: new readers handle NULL gracefully, old readers ignore the extra
field.

---

## v0 — baseline

**Schema (baseline — no migration required):**

| Column | Type | Mode | Description |
|---|---|---|---|
| trade_id | STRING | REQUIRED | Unique trade identifier |
| symbol | STRING | REQUIRED | Instrument symbol (e.g. RELIANCE, NSE:NIFTY50) |
| amount | FLOAT64 | REQUIRED | Trade notional in base currency |
| ccy | STRING | REQUIRED | Currency code (ISO 4217) |
| traded_at | TIMESTAMP | REQUIRED | UTC timestamp of trade execution |
| _load_id | STRING | REQUIRED | Idempotency key set by the pipeline load job |
