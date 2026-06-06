# Data Interview Q&A — Data Engineer · Data Architect · Principal Data Engineer

> Tradeoff-first prep. Every answer: **claim → alternative → what you give up → level-up note.**
> Last compiled June 2026. Sources at the end.
X
---

## 0. The meta-skill — how to answer ANY tradeoff question

This is the single pattern interviewers reward at senior+. Memorise the *shape*, not the answers.

1. **Clarify the constraint.** "What's the top constraint here — latency, cost, team size, or compliance?" Designing before confirming the constraint is the #1 mid-level mistake.
2. **Ground in numbers** (back-of-envelope). events/sec → MB/sec → TB/day. Parquet compresses ~4–8×. A decision attached to a number reads as senior; an adjective ("it's fast") reads as junior.
3. **Name options, pick a winner, state the sacrifice.** Use the literal words *"the tradeoff here is…"*. Never say "it depends" without naming **what** it depends on.
4. **Close with failure modes.** "If this fails in prod, the most likely reason is…" — this is what separates a principal from a senior.

**Junior** lists features. **Senior** compares options and picks one. **Principal** ties the choice to org cost, team capability, a 2-year migration path, and the failure mode — and says when they'd revisit the decision.

---

## 1. The Warehouse Question — "Why BigQuery? What's the alternative?"

This is the canonical question and the one you named. Here it is in full depth.

### Q1.1 — "You picked BigQuery. Why? What would have made you choose Snowflake or Redshift instead?"

**Strong answer (the decision framework):**

I choose BigQuery when three things are true: **(a)** the org is already on GCP, **(b)** workloads are spiky/unpredictable so I want *true serverless* with no cluster to size, and **(c)** I want zero infra ops — no warehouse to suspend, no nodes to resize. BigQuery is the only one of the three that is genuinely serverless: you don't provision compute at all; Google allocates slots per query.

I would switch to the alternatives when the constraint changes:

| Choose…       | When the deciding constraint is…                                                           | Because…                                                                                                                                                   |
| ------------- | ------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **BigQuery**  | GCP-native, spiky/ad-hoc query patterns, minimal ops, petabyte scans, built-in ML          | Truly serverless; per-TB-scanned pricing rewards intermittent use; tight Looker/Vertex/Ads integration                                                     |
| **Snowflake** | Multi-cloud or cross-company data sharing; many concurrent users; predictable cost control | Storage/compute separation → isolated virtual warehouses (ETL doesn't starve BI); per-second compute billing is predictable; best data-sharing/marketplace |
| **Redshift**  | Deeply AWS-invested; steady predictable workloads; team has tuning expertise               | Native S3/Glue/Kinesis/IAM integration; Spectrum queries S3 in place; RA3 + Serverless now exist; cheapest *if* you tune distribution/sort keys            |

**The core architectural difference** (the thing interviewers want you to articulate):

- **Snowflake** = storage/compute *separation* you control. You spin up N virtual warehouses on the same data. ETL on a big warehouse, analysts on a small one, no interference. You manage warehouse sizing + auto-suspend.
- **BigQuery** = storage/compute separation Google *hides*. No warehouses. Slots are auto-allocated. Less control over a pathological query, but nothing to operate.
- **Redshift** = historically coupled storage+compute (provisioned nodes). RA3 decoupled storage; Serverless (matured by 2026) added auto-scaling. Most control, most tuning burden.

**The tradeoff, stated crisply:**
- **Control vs. simplicity:** Redshift gives the most control and demands the most tuning; BigQuery gives the least control and the least ops.
- **Cost predictability vs. variable cost:** Snowflake/Redshift = per-resource, predictable. BigQuery on-demand = per-TB-scanned, *brilliant when idle, dangerous when someone runs `SELECT *` on a 50TB table*. This is why BQ cost governance (partition pruning, `--maximum_bytes_billed`, slot reservations) is a first-class DE skill.

**Level-up note:**
- *Junior:* "BigQuery is serverless and fast."
- *Senior:* the table above + "I'd reserve flat-rate slots once on-demand spend gets lumpy."
- *Principal:* "The warehouse is rarely the real decision — it's a 5-year lock-in to a cloud's IAM, lineage, and egress model. I'd choose based on where the company's gravity (other data, governance, team skills) already is, and I'd keep transformation in dbt/SQL so the warehouse stays swappable. The migration cost dominates the per-query cost."

### Q1.2 — "BigQuery on-demand vs. flat-rate (slots/capacity) pricing — when do you flip?"

- **On-demand** ($/TB scanned): great for spiky, low-volume, exploratory. No commitment. Risk: an unbounded query bankrupts you; cost is *unpredictable*.
- **Flat-rate / capacity (reserved slots)**: fixed $/month for guaranteed compute. Flip when monthly on-demand spend exceeds the cost of a slot commitment **and** you want predictable bills + workload isolation (separate reservations for ETL vs. BI so a heavy load doesn't starve dashboards).
- **Tradeoff:** on-demand trades cost-predictability for zero-commitment; flat-rate trades flexibility for a capped, isolatable bill. **Rule of thumb:** model both at current volume; flip when reserved is cheaper at ~60–70% utilisation, because that's when you stop paying for idle.

---

## 2. Ingestion & Loading — the "sync vs streaming" deep dive

### Q2.1 — "How do you get data INTO BigQuery? Streaming inserts, the Storage Write API, or batch load — why?" (your "sync as BQ why / alternative" question)

There are **three** ways, and naming all three + their tradeoffs is the senior signal:

| Method                                               | Latency       | Cost                                   | Semantics                                              | Use when                                        |
| ---------------------------------------------------- | ------------- | -------------------------------------- | ------------------------------------------------------ | ----------------------------------------------- |
| **Batch load job** (`bq load` / `LoadJobConfig`)     | Minutes–hours | **Free** (no insert cost; pay storage) | Atomic per job; re-runnable                            | Default. Hourly/daily files from GCS. Cheapest. |
| **Legacy streaming inserts** (`tabledata.insertAll`) | Seconds       | $0.05/GB                               | **At-least-once** → possible dupes                     | Near-real-time, low volume, dupes tolerable     |
| **Storage Write API**                                | Seconds       | Cheaper than legacy streaming          | **Exactly-once** (via stream offsets) + commit control | Modern real-time. Replaces legacy streaming.    |

**The answer:**
- **Default to batch.** It's free and atomic. If the business doesn't need sub-minute freshness, streaming is wasted money and added failure surface. (The "default to batch unless latency < 5 min" rule.)
- **For real-time, use the Storage Write API, not legacy streaming inserts.** The Write API gives **exactly-once** via stream offsets and a commit step, costs less, and supports pending/committed streams so you control visibility. Legacy `insertAll` is at-least-once — you *will* get duplicates and must dedupe downstream.
- **Why not always stream?** Streaming buffer rows aren't immediately available for some operations, you pay per GB, and you inherit dedupe/ordering complexity. Batch sidesteps all of it.

**The tradeoff:** batch trades freshness for cost + simplicity + atomicity; streaming trades cost + complexity for sub-minute latency. **Exactly-once is free with the Write API and expensive-to-fake with legacy streaming** — that's the modern senior answer.

**Level-up note:**
- *Junior:* "Use streaming inserts for real-time."
- *Senior:* "Storage Write API for exactly-once; batch when freshness allows because it's free."
- *Principal:* "I'd push back on the 'real-time' requirement first — most 'real-time' dashboards are fine at 5-minute micro-batch, which is 1/10th the cost and 1/3rd the failure modes. Real-time is a *business* decision with a price tag, not a default."

### Q2.2 — "CDC: log-based vs query-based — which and why?"

- **Query-based CDC** (poll a table on `updated_at`): simple, works anywhere. **Misses hard deletes**, adds read load to the source OLTP, and has polling latency.
- **Log-based CDC** (Debezium reading MySQL binlog / Postgres WAL): captures **every** change including deletes, near-zero source load, sub-second latency.
- **Answer:** log-based when the source supports it **and** you need delete detection **or** sub-second latency. Query-based for a quick-and-dirty sync where deletes don't matter.
- **Failure mode (say this):** "Schema evolution breaks the CDC pipeline unless I put a **schema registry with forward/backward compatibility** in front of it." (Ties to contract testing.)
- **Reference design:** Debezium → Kafka (one topic per table, partitioned by PK) → Flink/Spark `MERGE` upserts into the warehouse → reconcile row counts hourly, alert on replication lag.

### Q2.3 — "How do you achieve exactly-once processing?"

The senior one-liner: **"True exactly-once delivery is impossible; you achieve *effectively*-exactly-once through idempotent writes — the event may be delivered multiple times, but the final state reflects it once."**

Pattern: **deterministic event IDs → at-least-once delivery (Kafka `acks=all`) → idempotent sink (`MERGE`/`UPSERT` on the ID)**. For DB sinks, commit the consumer offset **in the same transaction** as the data write (transactional outbox). Kafka's transactional API can atomically commit output + offsets. This exact phrasing is explicitly called out as the junior↔senior separator.

---

## 3. Batch vs Streaming & Architecture Patterns

### Q3.1 — "Batch or streaming for this pipeline?"
- **Default batch** unless the latency SLA is **< 5 minutes**. Batch is simpler, cheaper, deterministic, debuggable (you can re-run yesterday).
- **Streaming** only when the business truly needs it: fraud (<500ms), live ops dashboards, real-time personalisation. Streaming costs you watermarks, state management, exactly-once, and 24/7 on-call.
- **Tradeoff:** latency vs. operational complexity + cost. Saying "I'd start batch, add a speed layer only if the SLA forces it" is the mature answer.

### Q3.2 — "Lambda vs Kappa architecture?"
- **Lambda** = batch layer (accurate, reprocessable history) + speed layer (low-latency recent) merged at serving. Use only when you need **both** sub-second freshness **and** periodic full historical reprocessing. **Failure mode: code divergence** between the two implementations of the same logic.
- **Kappa** = stream-only; reprocess by **replaying the event log**. Single codebase (kills the divergence problem). Limitation: replaying petabytes is slow/costly — works best with bounded retention (30–90 days).
- **Tradeoff:** Lambda buys accuracy at the cost of two codebases; Kappa buys one codebase at the cost of expensive replay.

### Q3.3 — "Data Lake vs Warehouse vs Lakehouse?"
- **Lake** (S3/GCS + Parquet): cheap, any format, schema-on-read. No ACID, no governance, easy to turn into a swamp.
- **Warehouse** (BQ/Snowflake/Redshift): ACID, fast SQL, governed. Pricier, structured-first.
- **Lakehouse** (Delta/Iceberg/Hudi on object store): ACID + time-travel + schema evolution **on** cheap lake storage, with one open format both Spark and SQL engines read. The 2026 default for new builds.
- **The architect nuance:** *Medallion (bronze/silver/gold) is a layering strategy; star schema (Kimball) is a modeling pattern that lives in the gold layer.* Interviewers love catching candidates who conflate them. Most "lakehouses" are still Kimball star schemas underneath.

### Q3.4 — "Data Mesh — when does it help and when does it hurt?"
- **Mesh** decentralises ownership: each domain owns its data **as a product**, central team provides self-serve platform + federated catalog + data contracts.
- **Helps** at large orgs where a central data team is the bottleneck and domains have the maturity to own pipelines.
- **Hurts** at small/mid orgs — it's an *organisational* solution to an *organisational* problem; imposing it on a 5-person data team just adds coordination overhead with no central efficiency to reclaim.
- **Principal framing:** "Mesh is a Conway's-law play. Adopt it when team topology, not technology, is the constraint."

---

## 4. Data Modeling

### Q4.1 — "Kimball vs Inmon vs Data Vault vs One Big Table?"
- **Kimball (dimensional / star schema):** facts + dimensions, denormalised, built for query speed and BI. **The 2026 default**, even inside "lakehouses."
- **Inmon (3NF enterprise warehouse):** normalised single source of truth, marts built downstream. Heavier, slower to deliver, strong for highly-regulated single-version-of-truth needs.
- **Data Vault:** hubs/links/satellites, optimised for auditability, source-tracking, and constant schema change. Great for compliance + many volatile sources; verbose to query (needs a presentation layer on top).
- **One Big Table (OBT / wide denormalised):** one flat table per use case. Columnar warehouses (BQ/Snowflake) make this cheap and fast; kills join complexity. Cost: duplication, harder to maintain consistency.
- **Tradeoff:** normalization (Inmon/Vault) optimises *write integrity & flexibility*; denormalization (Kimball/OBT) optimises *read speed & simplicity*. On columnar cloud warehouses the pendulum has swung toward Kimball/OBT because storage is cheap and joins are the cost.

### Q4.2 — "Slowly Changing Dimensions — which type?"
- **Type 0** keep original. **Type 1** overwrite (no history). **Type 2** add a new row + effective/expiry dates + current flag (full history — the default for customer/product dims). **Type 3** add a column (limited prior-value history). **Type 4/6** history table / hybrid.
- **Answer:** Type 2 when you must answer "what did this look like *at the time*?" (most dims). Type 1 when history is noise. **The cost of Type 2 is table growth + every query must filter `is_current` or join on the as-of date.**

### Q4.3 — "Partitioning vs Clustering vs Sharding — distinguish them."
- **Partitioning** (BQ: by DATE; warehouses: by date/range): physically splits a table so queries **prune** scans. Partition by the **most common filter column (usually date)**. This is the #1 BQ cost lever — `WHERE date >=` scans one partition, not the table.
- **Clustering** (BQ) / sort keys (Redshift): orders data *within* partitions on high-cardinality filter/join columns → less scan + faster joins. Layer it on top of partitioning.
- **Sharding** (multiple tables/DBs, e.g. `events_20260605`): splits across *objects/nodes*. Old BQ anti-pattern — prefer one partitioned table over date-sharded tables (sharding explodes metadata). Sharding belongs in OLTP/Kafka (partition by `user_id`/`device_id` for parallelism).
- **Over-partitioning warning:** 10K+ partitions create metadata overhead; target ~50–200 for daily data. Handle skew with **salting** (random suffix on hot keys, aggregate in consumer).

---

## 5. Reliability, Observability & Cost (the senior/principal core)

### Q5.1 — "What do you monitor in a production pipeline?"
Five layers (name all five):
1. **Pipeline health** — job status, last successful run, duration trend.
2. **Data freshness** — time since last update; alert on SLA breach.
3. **Data volume** — row/byte counts with anomaly detection (a 50% drop is a bug signal, not just a metric).
4. **Data quality** — test pass rates, null %, schema drift.
5. **Infrastructure** — Kafka consumer lag, Spark memory, checkpoint duration, **cloud spend**.

Tier alerts: **P1** = pipeline down/stale (page someone), **P2** = quality degradation / cost spike (ticket). A senior answer turns this into **data SLOs** ("gold.orders freshness < 2h, 99% of days") with error budgets.

### Q5.2 — "Backpressure — what is it and how do you handle it?"
Downstream can't keep pace with upstream (100K/s in, 50K/s sink). Fixes **in priority order**: (1) scale the bottleneck, (2) buffer strategically, (3) propagate backpressure signals, (4) shed/sample load. Detect via **Kafka consumer lag**: linearly increasing = sustained under-capacity; spiky = transient burst.

### Q5.3 — "Late-arriving data?"
- **Watermarks** — drop/route events later than threshold (e.g. window close + 5 min).
- **Reprocessing** — nightly batch recomputes affected partitions correctly.
- **Append-only + dedupe-at-read** — append late events with original timestamps.
- **Choice = consistency need:** finance → reprocessing (must be correct); marketing dashboard → watermark (good-enough, cheap).

### Q5.4 — "Schema evolution without downtime?"
- **Serialization:** Avro/Protobuf + schema registry; allow only backward/forward-compatible changes.
- **Pipeline:** never `SELECT *` — select by name; schema-on-read (Parquet + Spark).
- **Storage:** Delta/Iceberg native schema evolution (`mergeSchema`).
- **Governance:** track versions in catalog; alert on breaking changes *before* prod. Backward-compatible evolution = old consumers read new data = safe rollback.
- **The safe-change rule:** add nullable/defaulted columns = safe; add required column or narrow a type (FLOAT→INT) = breaking.

### Q5.5 — "Cut cost on a 50TB/day platform — where?"
Where the money actually is, in order of leverage:
1. **Storage format:** Parquet + ZSTD (30–50% off).
2. **Partition + Z-order/cluster** to minimise scan (up to 90% off — the single biggest lever).
3. **Compute:** spot instances for batch (60–70% off); autoscale streaming by lag.
4. **Lifecycle tiering:** hot 7d → warm 30d (standard S3) → cold 1y+ (Glacier).
5. **Warehouse hygiene:** per-team budgets, auto-suspend after ~2 min idle, `maximum_bytes_billed` caps.
> At 50TB/day, optimised vs. naive is ≈ **$500K/year**. Cost is an engineered constraint, not a monthly surprise.

---

## 6. Principal / Staff — leadership, strategy, influence

These are open-ended; structure beats trivia. STAR + tradeoff + business framing.

### Q6.1 — "Build vs. buy a data platform component?"
Decide on: **(a)** is it core differentiation or undifferentiated heavy lifting? **(b)** total cost of ownership incl. on-call & opportunity cost, not just license; **(c)** team capacity to operate it; **(d)** lock-in/exit cost. Buy the undifferentiated (orchestration, catalog), build the thing that's your actual edge. Principal answer names the **2-year TCO and the team-headcount cost of "build."**

### Q6.2 — "Lead a migration from on-prem/legacy to cloud."
- **Strangler-fig, not big-bang.** Run old + new in parallel, migrate domain by domain, dual-write and reconcile, cut over per-domain when row counts match.
- Sequence by **value × risk**: migrate a low-risk high-value domain first to prove the pattern.
- **Reconciliation is the deliverable** — automated row/sum parity checks gate each cutover.
- Name the rollback plan and the data-validation gate. The risk is silent data drift, not the lift-and-shift.

### Q6.3 — "How do you set technical direction / get buy-in across teams?"
Write it down (RFC/ADR), quantify the tradeoff, pilot small, let the data win the argument. Influence at principal = **artifacts + evidence**, not authority. Mentor by code review and design review, not by doing the work for them.

### Q6.4 — "A stakeholder demands real-time; engineering says it's 10× cost. Resolve it."
Reframe as a **price-tag decision, not a technical fight**: quantify the cost delta and the business value of each latency tier (real-time vs 5-min vs hourly), present three options with numbers, let the business own the call. Most "real-time" needs evaporate at the 5-minute micro-batch price point. This is the capital-preservation instinct applied to engineering.

### Q6.5 — "Biggest architecture mistake you've made?"
(Have a real one.) The strong shape: a decision that was *locally* right but *globally* wrong — e.g. optimising signal when sizing was the edge, or building infra before validating alpha (95/5 trap). Principal-grade reflection = "the failure was predictable; I'd written no pre-mortem. Now I write the failure mode first."

---

## 7. Question bank by level (breadth — drill these out loud)

### Data Engineer (core)
- Explain OLTP vs OLAP and why you don't run analytics on the OLTP DB.
- Normalize vs denormalize — when each, on a columnar warehouse.
- Write a query to find the 2nd-highest salary per department (window functions).
- How does a columnar store make analytics fast? (projection + compression + predicate pushdown.)
- Idempotent pipeline design — how do you make a re-run safe?
- Partition a 10TB fact table — on what column and why?
- Star schema vs OBT for a dashboard — pick one, defend it.
- Orchestrate dependencies + retries + backfill — why Airflow over cron?
- Handle a poison message in a Kafka consumer.
- Dedupe a stream with at-least-once delivery.

### Data Architect (design & governance)
- Differences between conceptual, logical, physical models.
- Design for **both** real-time analytics and batch in one architecture.
- Data fabric vs data mesh — define and contrast.
- Implement a data catalog + lineage across on-prem + cloud.
- GDPR/residency: design for right-to-erasure and per-country data residency.
- Master Data Management — what it is, why it matters.
- Multi-tenancy with data isolation — how.
- Operational + analytical workloads in a microservices estate (CQRS, CDC).
- Data quality framework spanning many domains.
- Balance data accessibility vs. security/governance.

### Principal Data Engineer (scale, strategy, system design)
- Design log aggregation for 10K servers × 50K lines/s (≈250 GB/s). (Fluent Bit → Kafka 200+ brokers → Flink → ES hot / S3 cold; tiered retention mandatory.)
- Design real-time fraud detection at 5K txns/s, <100ms. (Kafka by merchant_id → Flink stateful features → feature store in Redis → ONNX scoring → manual override path.)
- Design CDC OLTP→warehouse, <5-min lag. (Debezium → Kafka → Flink MERGE → schema registry → reconcile.)
- Design a feature store serving batch training + real-time inference without train/serve skew. (Offline Delta + online Redis; point-in-time-correct joins.)
- Design data quality for 500 tables / 200 pipelines. (YAML contracts → Great Expectations/dbt gates → DataHub health scores.)
- Cut cost 40% on a 50TB/day platform — where and how much each lever buys.
- Build vs buy the orchestration/catalog/lakehouse layer.
- Lead a zero-downtime migration with reconciliation gates.

---

## 8. The 12 phrases that signal seniority

Drop these *with* substance, never as buzzwords:

1. "The tradeoff here is X vs Y; for this constraint I pick X and give up Y."
2. "Effectively-exactly-once via idempotent writes — at-least-once delivery, idempotent sink."
3. "I'd default to batch unless the SLA is under five minutes."
4. "Partition by the dominant filter column to prune scans — that's the cost lever."
5. "Log-based CDC because query-based misses deletes."
6. "Medallion is layering; star schema is modeling — they're orthogonal."
7. "Schema registry with backward compatibility so rollbacks stay safe."
8. "A 50% volume drop is a bug signal, not just a metric."
9. "Storage Write API for exactly-once, not legacy streaming inserts."
10. "Reframe 'real-time' as a price-tag decision."
11. "Strangler-fig migration with row-count reconciliation gates."
12. "If this fails in prod, the most likely reason is…"

---

## Sources

- [Data Engineering System Design Interview Questions (2026) — Datavidhya](https://datavidhya.com/blog/data-engineering-system-design-interview-questions/)
- [Snowflake vs BigQuery vs Redshift 2026 Comparison — Reintech](https://reintech.io/blog/snowflake-vs-bigquery-vs-redshift-2026-comparison)
- [62 Data Architecture Interview Questions — Adaface](https://www.adaface.com/blog/data-architecture-interview-questions/)
- [Data Engineer Interview Questions 2026 — Tredence](https://www.tredence.com/blog/data-engineer-interview-questions-2026)
- [25 Data Modeling Interview Questions (2026) — DataDriven](https://datadriven.io/data-modeling-interview-practice)
- [41 Data Lakehouse Architect Interview Questions — ResumeDesign](https://resumedesign.ai/interview-questions/data-lakehouse-architect/)
- [Top 50 Principal Data Engineer Interview Questions — Index.dev](https://www.index.dev/interview-questions/principal-data-engineer)
- [Data Engineer Interview Questions: 150+ — InterviewQuery](https://www.interviewquery.com/p/data-engineer-interview-questions)
- BigQuery loading semantics (Storage Write API exactly-once, streaming inserts, batch load) — Google Cloud BigQuery documentation.
