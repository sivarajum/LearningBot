# Data Engineering → Data Architect Portfolio

A portfolio of 11 proof-of-concepts mapping engineering depth to **architect-level
responsibilities**. The index exists to answer one interviewer question directly:
*"Which of these proves you can own a data platform, not just build pipelines on it?"*

Each POC is rated on two axes that matter at the principal/architect level:

- **Fidelity** — does it run against real infrastructure, or simulate the concept?
  Simulations are honest learning tools; they are not operational evidence.
- **Maturity** — `tested + IaC` (production-shaped) vs `demo` (concept-shaped).

---

## Portfolio Matrix

| POC | Core competency | Architect responsibility it proves | Fidelity | Maturity |
|---|---|---|---|---|
| [Data-Contract-Registry](../Data-Contract-Registry) | Consumer-driven contracts, schema compatibility (BACKWARD/FORWARD/FULL) | **Interface governance** — preventing producer/consumer breakage at org scale | Real (in-process registry, BQ-backable) | Tested + Terraform |
| [BigQuery-Schema-Evolution](../BigQuery-Schema-Evolution) | Schema migration patterns, idempotent loads, property-based tests | **Change management** — evolving schemas without breaking history | Real (live BQ API calls) | Tested + Terraform |
| [Data-Quality-Framework](../Data-Quality-Framework) | 6 rule classes (freshness/validity/completeness/uniqueness/consistency), scoring | **Data SLAs** — quality as a measurable, enforced contract | Real (file/BQ data) | Tested |
| [Medallion-Architecture-dbt](../Medallion-Architecture-dbt) | Bronze/silver/gold with dbt, 112 SQL models | **Platform layering** — a standard every team builds on | Real (dbt run) | dbt tests |
| [Airflow-Orchestration](../Airflow-Orchestration) | DAG design, dependency management, operators | **Orchestration standard** — how work is scheduled and recovered | Real (Airflow) | Partial tests |
| [Real-Time-Streaming](../Real-Time-Streaming) | Topics/partitions/consumer-groups, windowed aggregation | Streaming **concepts** (Kafka mental model) | **Simulated** (in-memory broker) | Demo |
| [Multi-Cloud-Data-Lake](../Multi-Cloud-Data-Lake) | Lake zones, format/partition strategy across clouds | Lake **design concepts** | **Simulated** (cloud simulator) | Demo |
| [Enterprise-RAG-System](../Enterprise-RAG-System) | Chunking, embeddings, retrieval pipeline | GenAI platform **concepts** | Simulated | Demo |
| [LLM-Agent-Orchestration](../LLM-Agent-Orchestration) | Agent/tool routing, orchestration | Agentic platform **concepts** | Simulated | Demo |
| [Intelligent-Churn-Prediction](../Intelligent-Churn-Prediction) | Feature pipeline → model → serving | ML pipeline **concepts** | Simulated | Demo |
| [AI-Agents-Learning-Platform](../AI-Agents-Learning-Platform) | Multi-agent learning system | Agentic platform **concepts** | Simulated | Demo |

---

## How to read this portfolio

**The reliability core (lead with these).** Contracts + schema evolution + data
quality + medallion + orchestration form one coherent story: *how a data platform
stays trustworthy as it grows.* These five are tested, several are
Terraform-provisioned, and they run against real infrastructure. This is the
principal-data-engineer evidence.

**The concept demos (context, not evidence).** The streaming, lake, RAG, agent,
and churn POCs demonstrate that the concepts are understood end-to-end. They are
**explicitly labelled as simulations** where they don't touch real infra (see each
POC's "Scope & Fidelity" section). They are not presented as operational
experience — claiming otherwise is the fastest way to fail an architect interview.

---

## Architect-responsibility coverage

What the portfolio **proves** today and where the **deliberate gaps** are. Gaps are
listed because naming them is itself an architect signal.

| Responsibility | Covered by | Status |
|---|---|---|
| Interface / contract governance | Data-Contract-Registry | ✅ |
| Schema change management | BigQuery-Schema-Evolution | ✅ |
| Data quality / SLAs | Data-Quality-Framework | ✅ |
| Platform layering (medallion) | Medallion-Architecture-dbt | ✅ |
| Orchestration | Airflow-Orchestration | ✅ |
| **Lineage & catalog** | — | ⛳ planned (OpenLineage → DataHub/Marquez) |
| **Observability & data SLOs** | — | ⛳ planned (freshness/volume monitors + alerting) |
| **Governance / PII / RBAC** | — | ⛳ planned (column masking, retention on gold) |
| **Distributed compute at scale** | — | ⛳ planned (Spark/Flink job; today all pandas) |
| **CDC / streaming ingestion** | — | ⛳ planned (Debezium → bronze) |
| **CI/CD for data** | `.github/workflows/pocs-ci.yml` | ✅ (Tier-A) |
| **FinOps / cost governance** | — | ⛳ planned (scale-to-zero, budget guardrails) |

---

## Decision records

Every Tier-A POC ships an `ADR.md` capturing the decisions an architect is hired to
make: *what was chosen, what was rejected, the tradeoff, and what changes at 100×
scale.* Template: [ADR-TEMPLATE.md](./ADR-TEMPLATE.md). Code shows you can build;
ADRs show you can decide.
