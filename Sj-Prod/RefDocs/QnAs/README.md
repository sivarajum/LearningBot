# Data Interview Q&A — Architect · Engineer · Principal

A deep, tradeoff-first interview prep set for **Data Engineer**, **Data Architect**, and
**Principal Data Engineer** roles. Every answer follows the same shape:

> **Question → Strong answer → Alternatives → The tradeoff → What separates junior / senior / principal answers**

Because the thing that gets you hired at senior+ is **architectural trade-off reasoning** —
being able to say *"I chose BigQuery here because of X, and I accepted the trade-off of Y;
the alternative was Z, which I rejected because…"* — not vocabulary recall.

## Contents

- **[Data-Engineering-Interview-QnA.md](./Data-Engineering-Interview-QnA.md)** — the full document:
  1. The meta-skill: how to answer a tradeoff question
  2. The Warehouse Question (BigQuery vs Snowflake vs Redshift) — the canonical "why X / what's the alternative"
  3. Ingestion & loading (incl. the BQ streaming-insert vs Storage Write API vs batch-load deep dive)
  4. Batch vs streaming, CDC, exactly-once & idempotency
  5. Data modeling (Kimball vs Inmon vs Data Vault, SCD, partitioning vs clustering vs sharding)
  6. Architecture patterns (Lambda/Kappa, lakehouse, data mesh)
  7. Reliability & ops (observability/SLOs, backpressure, late data, schema evolution, cost)
  8. Principal-level (build vs buy, migration, influence, tech strategy)
  9. Full question bank by level (breadth)

## How to drill

1. Read the question, **answer out loud before reading the answer**.
2. Then check: did you name the alternative? Did you state what you gave up? Did you ground it in numbers?
3. If your answer was "it depends" — it depends *on what*? Name the variable. That's the whole game.
