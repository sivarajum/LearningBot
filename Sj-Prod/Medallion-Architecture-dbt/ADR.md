# ADR-004: Medallion (bronze/silver/gold) with dbt as the transformation standard

- **Status:** Accepted
- **Date:** 2026-05-18
- **Context layer:** transformation

## Context

Without a layering convention, every team invents its own path from raw to
consumable, transformations duplicate, and there is no agreed boundary between "data
as it arrived" and "data fit to serve." We need a standard that separates
responsibilities (ingest fidelity vs. business logic vs. serving shape) and makes
lineage and tests first-class.

## Decision

Adopt the **medallion pattern** — bronze (raw, append-only, source-faithful), silver
(cleaned, conformed, deduped), gold (business-level, serving-shaped) — implemented in
**dbt** with tests and schema contracts at each layer (`models/{bronze,silver,gold}/
schema.yml`). dbt's ref-graph gives lineage and incremental builds for free.

## Alternatives considered

| Option | Why rejected |
|---|---|
| Hand-written SQL scripts orchestrated by Airflow | No lineage graph, no built-in tests, no incremental model — every dependency is manual and fragile. |
| Stored procedures in the warehouse | Logic locked to one engine, no version control discipline, poor testability. |
| Two layers (raw → mart) | Collapsing silver removes the conformance boundary; business logic leaks into cleaning and re-use dies. |
| Spark notebooks | Overkill for warehouse-native SQL transforms; adds a cluster to operate for no benefit at this scale. |

## Consequences

- **Positive:** Clear ownership boundaries, free lineage + incremental builds, tests
  co-located with models. The pattern is teachable and uniform across teams.
- **Negative / cost:** Three physical layers multiply storage and build time; trivial
  pipelines pay medallion overhead they may not need.
- **Risk accepted:** dbt is warehouse-centric — pushing all logic into SQL is the
  right call here but caps what's expressible vs. a general compute engine.

## What changes at 100×

The layers hold; the bottleneck moves to **build orchestration and cost**. Full-graph
`dbt run` becomes too slow/expensive, forcing state-based selection (`state:modified+`)
and incremental everywhere. Gold fans out into per-domain data products with
contracts (ties to ADR-001), and lineage stops being a dbt-internal graph and must
emit to a platform catalog (OpenLineage) so non-dbt consumers can see it.
