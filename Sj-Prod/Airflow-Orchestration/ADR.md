# ADR-005: Airflow as the orchestration standard

- **Status:** Accepted
- **Date:** 2026-05-18
- **Context layer:** ingestion / transformation

## Context

Pipelines have dependencies, schedules, retries, and partial-failure recovery needs.
Without a single orchestration standard, scheduling lives in cron + bespoke scripts,
failures are invisible, and re-running "just the failed step" is impossible. We need
explicit DAGs, dependency-aware scheduling, and idempotent, retryable tasks.

## Decision

Standardise on **Airflow**: pipelines are explicit DAGs with declared task
dependencies, per-task retries, and operators that encapsulate the unit of work.
Tasks are designed idempotent so retries and backfills are safe, and orchestration
config is separated from task logic in `src/`.

## Alternatives considered

| Option | Why rejected |
|---|---|
| cron + shell scripts | No dependency graph, no retry semantics, no visibility into partial failure, no backfill. |
| Cloud-managed schedulers only (Cloud Scheduler / EventBridge) | Fine for triggers, but no DAG-level dependency management or task-level recovery. |
| Dagster / Prefect | Strong alternatives; Airflow chosen for ubiquity and operator ecosystem — the skill transfers to the most environments. The DAG-design judgment is portable regardless. |
| Orchestrating inside dbt | dbt owns the transform graph (ADR-004); it does not own cross-system ingestion, sensors, or external triggers. |

## Consequences

- **Positive:** Dependency-aware scheduling, retries, and backfill out of the box;
  failures are visible and recoverable at task granularity.
- **Negative / cost:** Airflow is operationally heavy (scheduler + workers + metadata
  DB) and tempts teams to put business logic in DAGs instead of tested `src/` modules.
- **Risk accepted:** Test coverage here is thinner than the data-quality/schema POCs
  (DAG integration tests are the known gap to close next).

## What changes at 100×

At thousands of DAGs the scheduler and metadata DB become the constraint — forcing
multi-scheduler HA, DAG-parsing budgets, and a hard rule that DAGs *orchestrate* but
never *compute*. Triggering shifts from time-based to **data-aware/event-driven**
(datasets, sensors) so pipelines fire on data readiness rather than wall-clock guesses,
and orchestration emits lineage/run events to the platform catalog.
