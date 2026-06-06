# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a collection of **production-grade systems** for data engineering, ML, and AI. Each system is a self-contained Python project in its own directory with independent dependencies.

## Common Commands

### Running a System

Each system has a `main.py` entry point with a consistent CLI pattern:

```bash
cd <System-Directory>
pip install -r requirements.txt
python main.py              # default mode (varies per system)
python main.py api          # FastAPI server on port 8000
python main.py ui           # Streamlit dashboard on port 8501
python main.py all          # both API + UI
```

Some systems have additional modes: `pipeline`, `validate`, `simulate`, `generate`, `stats`.

### Docker

Every system has a `Dockerfile` and `docker-compose.yml`:

```bash
cd <System-Directory>
docker compose up --build
```

### Linting

A shared `ruff.toml` at the Sj-Prod root applies to all sub-projects:

```bash
ruff check .                    # lint all systems
ruff check <System-Directory>   # lint one system
ruff format .                   # format
```

### Testing

Some systems have tests (BigQuery-Schema-Evolution, Data-Contract-Registry, Data-Quality-Framework, Airflow-Orchestration). Run from within each system directory:

```bash
cd <System-Directory>
pytest                      # runs unit tests (default)
pytest -m "not integration" # explicitly skip integration tests
pytest tests/test_foo.py    # single test file
pytest tests/test_foo.py::test_bar  # single test
```

BigQuery-Schema-Evolution and Data-Contract-Registry use `pytest.ini` with `--cov=src --cov-fail-under=80`. Integration tests are marked `@pytest.mark.integration` and require GCP credentials.

### Medallion-Architecture-dbt (special)

This system uses dbt + DuckDB with a local `.venv`:

```bash
cd Medallion-Architecture-dbt
source .venv/bin/activate
python main.py pipeline    # generate data + run dbt
dbt run --project-dir medallion_dbt --profiles-dir medallion_dbt
dbt test --project-dir medallion_dbt --profiles-dir medallion_dbt
```

## Architecture Pattern

Most systems follow a consistent three-layer structure:

- **`src/`** — Core logic modules (domain-specific pipeline, data generators, models)
- **`src/api.py`** — FastAPI app exposing REST endpoints (`app` object used by uvicorn)
- **`src/ui.py`** — Streamlit dashboard (adds project root to `sys.path` before imports)
- **`main.py`** — CLI entry point that dispatches to pipeline/api/ui modes

Systems that require API keys (Enterprise-RAG-System, LLM-Agent-Orchestration) have `.env.example` files. Both work without keys using fallback/extractive modes.

## Ruff Configuration

- Line length: 120, target Python 3.11+
- `E402` suppressed in `ui.py`/`main.py` (intentional `sys.path` manipulation before imports)
- `F811`/`F401`/`E402` suppressed in test files
- Import sorting enabled (`I` rules)

## Planning & Tracking

Three files track project status. Always consult and update these when working on tasks:

- **`master-plan.md`** — The master plan. Contains all todos and in-progress work. Check here first to understand what needs to be done.
- **`todo-plan.md`** — Detailed todo/in-progress items. Add new work items here; move items to in-progress as you start them.
- **`complete-plan.md`** — Completed work. Move items here from `todo-plan.md`/`master-plan.md` once finished.

When starting a task, mark it in-progress in `master-plan.md`/`todo-plan.md`. When finishing, move it to `complete-plan.md`.

## Notable Structural Variations

- **Airflow-Orchestration**: Has `dags/` (DAG definitions) and `plugins/` (custom operators/callbacks) alongside `src/`
- **BigQuery-Schema-Evolution**: Uses `src/migration/` and `src/pipeline/` sub-packages; tests split into `tests/unit/` and `tests/integration/`
- **Data-Contract-Registry**: Uses `src/contracts/` and `src/registry/` sub-packages; contract definitions in `contracts/*.yaml`
- **Medallion-Architecture-dbt**: Has `medallion_dbt/` dbt project (models/macros/tests in SQL) plus Python `src/` for data generation and UI
