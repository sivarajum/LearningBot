# Data Architect Portfolio — TODO Plans

Roadmap of the **deliberate gaps** in the POC portfolio (tracked as ⛳ in
[POCs/POC-Index/README.md](../POCs/POC-Index/README.md)). These are the holes that
matter for the senior-DE → principal/architect leap. None are closeable by polishing
existing POCs — each is a new capability.

**Ordering principle:** maximise leverage on what already exists (dbt + Airflow +
data-quality + contracts), kill the loudest interview objections first.

Status legend: `⬜ not started` · `🟡 in progress` · `✅ done`

---

## Priority 1 — Lineage & Catalog  ⬜
**Why first:** highest ROI. You already have dbt + Airflow producing a lineage graph;
this exposes it platform-wide. A data architect who can't speak to lineage is not
credible. Leverages existing assets — least new infra.

- **POC name:** `Data-Lineage-Catalog`
- **Build:**
  - Emit **OpenLineage** events from the existing dbt project (`Medallion-Architecture-dbt`) and Airflow DAGs (`Airflow-Orchestration`).
  - Land them in **Marquez** (lightweight, docker-compose) or DataHub.
  - Show **column-level lineage** bronze → silver → gold.
  - Wire one "impact analysis" query: *"if I change `silver.customers.email`, what gold tables/dashboards break?"* — ties directly to `Data-Contract-Registry`.
- **Architect signal:** lineage as a platform service, not a dbt-internal graph.
- **Proves responsibility:** Lineage & catalog (currently uncovered).
- **ADR to write:** OpenLineage vs. native dbt docs vs. Unity Catalog — why a neutral emitter.

## Priority 2 — Observability & Data SLOs  ⬜
**Why:** turns `Data-Quality-Framework` from a batch report into a reliability surface.
This is *the* reliability story and it's currently absent (prometheus/grafana only
appear in prose).

- **POC name:** `Data-Observability-SLO` (or extend Data-Quality-Framework)
- **Build:**
  - Emit freshness / volume / null-rate / distribution metrics to **Prometheus**.
  - **Grafana** dashboard + alert rules; define explicit **data SLOs** (e.g. "gold.orders freshness < 2h, 99% of days").
  - Page on SLO breach (Alertmanager → webhook).
  - Anomaly detection on volume (simple z-score / rolling-window is enough).
- **Architect signal:** data quality expressed as an enforced, alertable SLA.
- **Proves responsibility:** Observability & data SLOs (currently uncovered).
- **ADR to write:** SLO threshold-setting from data distributions vs. assumed constants.

## Priority 3 — Governance / PII / RBAC  ⬜
**Why:** architects are *accountable* for this. Zero coverage today.

- **POC name:** `Data-Governance-PII`
- **Build:**
  - **Column-level masking** + tokenization on PII in the medallion gold layer.
  - **RBAC** model: who can read raw PII vs. masked vs. aggregate.
  - **Retention / right-to-erasure** (GDPR-style) job that purges by subject key.
  - Classification tags (PII / sensitive / public) flowing into the catalog (P1).
- **Architect signal:** governance as policy-as-code, not a wiki page.
- **Proves responsibility:** Governance / PII / RBAC (currently uncovered).
- **ADR to write:** masking-at-rest vs. masking-at-query vs. tokenization-vault tradeoffs.

## Priority 4 — Distributed Compute at Scale  ⬜
**Why:** kills the "everything is pandas" objection. Today no POC touches a real
distributed engine — a real gap for *principal data engineer*.

- **POC name:** `Spark-Scale-Processing` (Spark or Flink)
- **Build:**
  - A non-trivial **Spark** job (or Flink) on a dataset large enough that partitioning matters.
  - Demonstrate **partition pruning, file sizing, shuffle, and skew handling** (intentional skew → salting fix).
  - Read/write a real table format (**Iceberg / Delta**) on object store (or duckdb+local for cost).
- **Architect signal:** you can reason about shuffle, skew, and file sizing — not just `df.groupby`.
- **Proves responsibility:** Distributed compute at scale (currently uncovered).
- **ADR to write:** when warehouse-native SQL (dbt) is enough vs. when you reach for Spark.

## Priority 5 — CDC / Streaming Ingestion  ⬜
**Why:** makes the streaming story *real* (the current streaming POC is an honest
in-memory simulator). CDC is the backbone of modern ingestion.

- **POC name:** `CDC-Ingestion`
- **Build:**
  - **Debezium** capturing row changes from Postgres → Kafka/Redpanda → bronze.
  - Handle **schema changes mid-stream** (ties to `BigQuery-Schema-Evolution` + `Data-Contract-Registry`).
  - Exactly-once / idempotent landing into bronze; late-data handling.
- **Architect signal:** event-driven ingestion with real delivery guarantees.
- **Proves responsibility:** CDC / streaming ingestion (currently uncovered).
- **ADR to write:** CDC (log-based) vs. batch extract vs. dual-write — why log-based wins.

## Priority 6 — FinOps / Cost Governance  ⬜
**Why:** architects own cost. **You already do this daily in sjarvis** (₹5K cap,
scale-to-zero, cost_guard) — it belongs in this portfolio as a first-class artifact.

- **POC name:** `Data-FinOps`
- **Build:**
  - Per-pipeline / per-query **cost attribution** (BQ bytes-scanned, slot-time, storage).
  - **Budget guardrails** + scale-to-zero patterns (port the sjarvis approach).
  - A "cost regression" check in CI: flag a dbt model whose bytes-scanned jumps >X%.
- **Architect signal:** cost as an engineered, monitored constraint — not a monthly surprise.
- **Proves responsibility:** FinOps / cost governance (currently uncovered).
- **ADR to write:** partition/cluster strategy as a cost decision; when to materialize vs. recompute.

---

## Cross-cutting hardening (existing Tier-A POCs)  ⬜
Smaller items that raise the bar on what already exists:

- ⬜ **Airflow test coverage** — 5,561 LOC but only 1 test file. Add DAG-integrity + operator integration tests (the ADR-005 named gap).
- ⬜ **Promote or honestly demote Tier-B demos** — RAG / LLM-Agent / Churn / AI-Agents: either add tests + a "Production path" section (done for Streaming & Multi-Cloud), or clearly mark as concept-only in their READMEs.
- ⬜ **Enforce coverage in CI** — currently CI reports coverage but doesn't gate (`-o addopts=""`). Once test coverage is raised, re-enable `--cov-fail-under` per POC.
- ⬜ **Top-level portfolio README** — link POC-Index from the repo root so the matrix is the first thing a reviewer sees.

---

## Done (for reference)
- ✅ POC-Index portfolio matrix + responsibility-coverage map
- ✅ ADRs for all 5 Tier-A POCs + ADR template
- ✅ CI/CD (`.github/workflows/pocs-ci.yml`) — lint + test, verified green (244 tests)
- ✅ Shared `ruff.toml`; dead-code cleanup; Airflow `json` import bug fixed
- ✅ "Production path" honesty sections on Real-Time-Streaming & Multi-Cloud-Data-Lake
