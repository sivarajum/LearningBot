# Master Plan — Sj-Prod Systems

Goal: Transform all systems from POC-level to production-grade.

Prioritized by setup complexity: non-GCP/minimal install first, GCP-dependent last.

---

## Tier 1 — Non-GCP, Minimal Setup (pip install only)

### 1. Data-Contract-Registry
- **Status:** PRODUCTION-READY
- **Deps:** pyyaml, jsonschema, pytest (pure Python, no cloud)
- **Tests:** 136 passing, 97.22% coverage (exceeds 80% gate)
- **Completed:**
  - [x] API layer (FastAPI) with 10 endpoints
  - [x] Streamlit UI for browsing/validating contracts
  - [x] Comprehensive test suite (96 core + 40 API tests)
  - [x] Docker production config with docker-compose
  - [x] RUNNING.md with build/test/deploy instructions
  - [x] Route ordering bug fix in api.py
  - [x] Coverage gate passing (97.22% > 80%)

### 2. Data-Quality-Framework
- **Status:** PRODUCTION-READY
- **Deps:** fastapi, pandas, faker (pure Python, no cloud)
- **Tests:** 155 passing (96 core + 59 API tests)
- **Completed:**
  - [x] Full DQ pipeline (profiler, validator, scorer, reporter)
  - [x] API tests for all 8 endpoints
  - [x] Docker production config
  - [x] RUNNING.md with build/test/deploy instructions
  - [x] Health check endpoint

### 3. Intelligent-Churn-Prediction
- **Status:** PRODUCTION-READY
- **Deps:** scikit-learn, xgboost, fastapi, streamlit (pure Python ML)
- **Tests:** 75 passing, 92-100% coverage on all testable modules
- **Completed:**
  - [x] Full test suite (data gen, feature eng, model, pipeline, API)
  - [x] Docker production config
  - [x] RUNNING.md with build/test/deploy instructions

### 4. Medallion-Architecture-dbt
- **Status:** PRODUCTION-READY
- **Deps:** dbt-duckdb, DuckDB, fastapi, streamlit (local DB)
- **Tests:** 83 Python tests passing + 41 dbt SQL tests
- **Completed:**
  - [x] Python tests (data generator, pipeline, API)
  - [x] Docker production config
  - [x] RUNNING.md with build/test/deploy instructions

### 5. AI-Agents-Learning-Platform
- **Status:** PRODUCTION-READY
- **Deps:** fastapi, streamlit (pure Python)
- **Tests:** 107 passing, 100% coverage on testable modules
- **Completed:**
  - [x] Full test suite (knowledge base, demos, API)
  - [x] Docker production config
  - [x] RUNNING.md with build/test/deploy instructions

### 6. Real-Time-Streaming
- **Status:** PRODUCTION-READY
- **Deps:** fastapi, streamlit, pandas (simulated streaming)
- **Tests:** 90 passing, 99-100% on core modules
- **Completed:**
  - [x] Full test suite (broker, producer, processor, API)
  - [x] Docker production config
  - [x] RUNNING.md with build/test/deploy instructions

### 7. Multi-Cloud-Data-Lake
- **Status:** PRODUCTION-READY
- **Deps:** fastapi, streamlit, pandas, pyarrow (simulated clouds)
- **Tests:** 91 passing, 100% on core modules
- **Completed:**
  - [x] Full test suite (cloud simulator, lake builder, API)
  - [x] Docker production config
  - [x] RUNNING.md with build/test/deploy instructions

### 8. Airflow-Orchestration
- **Status:** PRODUCTION-READY
- **Deps:** fastapi, streamlit, pandas (simulator mode, no real Airflow needed)
- **Tests:** 139 passing (validation operator + simulator + API + DAG structure)
- **Completed:**
  - [x] Expanded test suite (simulator, API, DAG validation)
  - [x] Docker production config
  - [x] RUNNING.md with build/test/deploy instructions

---

## Tier 2 — Requires API Keys (works with fallback mode)

### 9. Enterprise-RAG-System
- **Status:** PRODUCTION-READY
- **Deps:** langchain, chromadb, sentence-transformers (optional: openai, anthropic)
- **Tests:** 63 passing
- **Completed:**
  - [x] **Fixed requirements.txt** — replaced 517-line conda dump with 29-line clean deps
  - [x] Full test suite (document loader, embeddings, RAG pipeline, API)
  - [x] Docker production config
  - [x] RUNNING.md with build/test/deploy instructions
  - [x] Fallback mode works without API keys

### 10. LLM-Agent-Orchestration
- **Status:** PRODUCTION-READY
- **Deps:** langgraph, langchain (optional: openai, anthropic)
- **Tests:** 59 passing
- **Completed:**
  - [x] **Fixed requirements.txt** — replaced 519-line conda dump with 18-line clean deps
  - [x] Full test suite (state, agents, orchestrator, tools, API)
  - [x] Docker production config
  - [x] RUNNING.md with build/test/deploy instructions
  - [x] Fallback mode works without API keys

---

## Tier 3 — Requires GCP Credentials

### 11. BigQuery-Schema-Evolution
- **Status:** DEFERRED (requires GCP credentials)
- **Deps:** google-cloud-bigquery (requires GCP project + credentials)
- **Already has:** tests (unit + integration), 80% coverage, hypothesis-based property tests

---

## Cross-Cutting Concerns

- [x] All systems have RUNNING.md with build/test/deploy instructions
- [x] All systems have comprehensive test suites
- [x] All systems have Docker configs (Dockerfile + docker-compose.yml)
- [x] All systems have health check endpoints
- [x] Bloated requirements.txt files cleaned up (Enterprise-RAG, LLM-Agent)
- [ ] Standardize logging across all systems (future enhancement)
- [ ] Add shared GitHub Actions CI workflow (future enhancement)
- [ ] Add pre-commit hooks (ruff, mypy) (future enhancement)
