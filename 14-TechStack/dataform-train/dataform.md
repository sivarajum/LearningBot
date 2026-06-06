# Google Dataform: Trainer Script With Explanations

Use this script as a read-through for a training video. Each section pairs the talking points with short explanations so the audience understands the why behind every feature.

## 1) What Dataform Is (and Why It Matters)
- Cloud-based transformation layer built for BigQuery; similar to dbt but native in the Google Cloud ecosystem.
- Goal: organize SQL transformations, automate runs, and keep data quality high without leaving SQL.
- Audience: analytics engineers, data engineers, and BI teams who already think in SQL.

## 2) Core Ideas (Explain the Value)

### SQL-Based Development & Scaling
- You write SQLX (SQL plus config) instead of bespoke pipelines. This keeps the learning curve low and reviews simple.
- Scaling rides on BigQuery, so performance tuning follows familiar BigQuery patterns (partition, cluster, incremental builds).

### Version Control Integration
- Works with GitHub/GitLab so every change is code-reviewed. Rollbacks are just git history.
- CI-friendly: run checks on pull requests before merging to main.

### Table Dependency Management
- You declare sources and refs; Dataform orders runs automatically. No manual DAG wiring.
- Lineage stays current: easier debugging and impact analysis when upstream data changes.

### Centralized Code Management
- One repo houses SQL models, docs, tests, and helpers. This improves ownership and makes onboarding faster.

### Code Reusability With JavaScript
- Shared helpers live in `includes/`. Use JS to avoid copy-paste in SQL (e.g., standard currency conversions or KPI formulas).
- DRY by design: change the helper once, update every model that calls it.

### Data Quality & Testing
- Assertions (tests) run before publish. Catch null keys, duplicates, or business-rule breaks early.
- Treat tests as gates: if they fail, the model does not ship.

### Data Documentation
- Document tables and columns inline with the SQLX file. Docs stay next to the code that defines the field.
- Reduces tribal knowledge and speeds up BI/self-serve adoption.

## 3) Project Structure (Show and Explain)

### Core Configuration Files
- dataform.json: project settings, default datasets, and BigQuery connection details; also naming conventions.
- package.json: JS dependencies and scripts for custom functions or checks.
- workflow_settings.yaml: orchestration (schedules, dependency chains, concurrency/safe settings).

### Directories
- definitions/: SQLX models grouped by layer (staging, intermediate, mart) or domain. Each file is a table/view with logic + docs.
- includes/: shared JS utilities for reusable expressions, business rules, and quality helpers.
- tests/: assertions and custom rules to validate integrity and business expectations.

### Example Layout
```
my-dataform-project/
├── dataform.json
├── package.json
├── workflow_settings.yaml
├── definitions/
│   ├── staging/
│   │   ├── customers.sqlx
│   │   └── orders.sqlx
│   ├── intermediate/
│   │   └── customer_metrics.sqlx
│   └── marts/
│       └── customer_summary.sqlx
├── includes/
│   ├── utils.js
│   └── business_logic.js
└── tests/
    └── assertions.sqlx
```

## 4) Explain a Simple Flow (Stage → Intermediate → Mart)
- Stage: clean raw `customers` and `orders` (types, dedupe, rename). Keep logic light here.
- Intermediate: `customer_metrics.sqlx` aggregates orders per customer (spend, frequency, LTV, churn flags).
- Mart: `customer_summary.sqlx` joins metrics with dimensions to serve BI and activation.
- Tests: assertions ensure primary keys are unique, required columns are not null, and referential integrity holds before publish.
- Docs: table/column descriptions live beside the SQLX so new teammates see meaning and logic together.

## 5) Best Practices (Tell Them Why)
- Layering: staging for hygiene, intermediate for business logic, marts for consumption. This isolates blast radius and clarifies ownership.
- DRY with JS helpers: move repeated expressions (e.g., date buckets, currency fx) to `includes/` so updates are single-source.
- Naming defaults: set dataset and prefix/suffix rules in dataform.json to avoid writing to the wrong dataset.
- Testing discipline: add assertions for keys, nulls, duplicates, and business rules (e.g., revenue >= 0) to stop bad data early.
- Reviews and docs: require PRs; ship a brief doc line with every new column to prevent drift.
- Scheduling: align workflow_settings.yaml with upstream availability; avoid overlapping writes that create contention.

## 6) Common Pitfalls (And Fixes)
- Missing dependencies: always declare sources/refs so execution order and lineage stay correct.
- Copy-paste SQL: extract to JS helpers to cut maintenance time.
- Sparse documentation: add column descriptions as you add columns; do not defer.
- Dataset mix-ups: rely on defaults in dataform.json; avoid hardcoding dataset names in models.

## 7) Performance Pointers
- Prefer incremental models; partition and cluster BigQuery tables to cut scan costs.
- Trim columns early; avoid SELECT * in wide joins.
- Reuse logic via helpers so optimizations are applied everywhere at once.

## 8) Quick Start Checklist
- Create dataform.json with default datasets and naming conventions.
- Scaffold definitions/ with staging, intermediate, and mart folders.
- Add one JS helper in includes/ (e.g., standard date truncation or fx conversion).
- Write one staging model and one assertion (not-null primary key) to establish the pattern.
- Document each column as you add it; keep docs close to code.

Use these explanations as your narration while walking through the repo, showing file locations, and demoing a small change (edit a model, run tests, view lineage). The audience should grasp both how to do it and why each step matters.


Title & Hook (0:00–0:20)

“Welcome! Today we’ll master Google Dataform—how to build SQL-based transformations, manage dependencies, and guarantee data quality at scale.”
“If you know SQL, you can ship production-grade pipelines with version control, tests, and docs built in.”
Agenda (0:20–0:40)

What Dataform is and where it fits
Core features: SQL workflows, Git integration, dependencies, reusability, tests, docs
Project structure walkthrough
Example: staging → intermediate → marts
Best practices and next steps
1) What is Google Dataform? (0:40–1:20)

Cloud-based transformation layer on BigQuery, similar to dbt, optimized for SQL-first teams.
Solves: organizing transformations, automating runs, enforcing data quality, collaborating via Git.
2) Core Features (1:20–3:30)

SQL-Based Development & Scaling: author, version, and execute SQL workflows; scale with BigQuery.
Version Control Integration: GitHub/GitLab for branching, reviews, rollbacks; CI-friendly.
Table Dependency Management: declare sources, track lineage, run in dependency order.
Centralized Code: single repo for SQL logic and docs; clearer ownership and history.
Code Reusability with JavaScript: shared functions in includes/; DRY patterns; call JS helpers inside SQLX.
Data Quality & Testing: assertions to validate integrity/accuracy; catch issues before publish.
Data Documentation: inline table/column docs; keep meaning close to code.
3) Project Structure (3:30–6:00)

dataform.json: project config, default datasets, BigQuery connection, naming conventions.
package.json: JS dependencies and scripts for custom functions/tests.
workflow_settings.yaml: orchestration—scheduling, dependency chains, execution settings.
definitions/: SQLX models (tables/views), organized by layer (staging, intermediate, mart) or domain.
includes/: shared JS utilities and business logic; helpers for transformations and tests.
tests/: assertions and custom rules.
4) Visual Layout Example (describe on screen) (6:00–7:00)

Show a tree:
definitions/staging/customers.sqlx, definitions/staging/orders.sqlx
definitions/intermediate/customer_metrics.sqlx
definitions/marts/customer_summary.sqlx
includes/utils.js, includes/business_logic.js
tests/assertions.sqlx
5) How a Simple Flow Runs (7:00–9:00)

Staging layer cleans raw customers and orders (light transforms, type casting).
Intermediate layer customer_metrics.sqlx aggregates orders per customer, computes LTV/churn flags.
Mart layer customer_summary.sqlx joins metrics + dimensions for BI/activation.
Assertions validate row counts, null checks on keys, referential integrity.
Docs live alongside SQLX—new columns are described where they’re defined.
6) Best Practices (9:00–10:30)

Layering: staging → intermediate → marts; keep business logic out of staging.
DRY: move repeated expressions into includes/ JS helpers.
Naming: consistent prefixes/suffixes per layer; define defaults in dataform.json.
Testing: assert primary keys, not-null, uniqueness, and business rules before publishing.
Reviews: use Git PRs; add lightweight docs with each change.
Scheduling: align workflow_settings.yaml with upstream data availability; avoid overlapping writes.
7) Common Pitfalls & Fixes (10:30–11:30)

Missing dependencies: declare sources/refs so runs order correctly.
Copy-paste SQL: extract to JS helpers.
Sparse docs: add column descriptions as you add columns.
Unscoped datasets: set defaults in dataform.json to avoid writing to the wrong dataset.
8) Comparison (11:30–12:00)

Dataform vs dbt: similar SQL + tests + docs; Dataform is native in BigQuery UI and integrates tightly with Google Cloud.
When to choose: if BigQuery-first and want native console experience; if multi-warehouse, dbt may fit better.
9) Performance Tips (12:00–13:00)

Use incremental models where possible; partition and cluster BigQuery tables.
Prune columns early in staging; avoid SELECT * in wide joins.
Reuse CTEs via helpers; prefer deterministic logic in JS functions.
10) Wrap-Up & Next Steps (13:00–14:00)

Recap: SQL-first transforms, Git-powered workflows, dependencies, tests, docs.
Next actions:
Create dataform.json with dataset defaults.
Scaffold definitions/ layers and an includes/utils.js helper.
Add one assertion per model (keys, not-null).
Document columns as you go.
Call to action: “Open your repo, add a staging model and an assertion now—ship a clean mart in minutes.”
Use this as your read-through script; add live console/demo cutaways where you show editing customers.sqlx, running assertions, and viewing lineage in the UI.

