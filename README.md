# LearningBot

Full-stack learning and portfolio repository — 10 production-grade systems (1,056+ tests), 14 learning modules, Next.js viewer, and 4K cheat sheets.

## Production Systems (Sj-Prod)

10 independently deployable Python systems, each with FastAPI, Streamlit, Docker, tests, and documentation:

| # | System | Tests | Stack |
|---|--------|-------|-------|
| 1 | [Data-Contract-Registry](Sj-Prod/Data-Contract-Registry) | 136 | YAML schemas, compatibility checking, consumer-driven contracts |
| 2 | [Data-Quality-Framework](Sj-Prod/Data-Quality-Framework) | 155 | 5 DQ dimensions, weighted scoring, profiling, reporting |
| 3 | [Intelligent-Churn-Prediction](Sj-Prod/Intelligent-Churn-Prediction) | 85 | XGBoost pipeline, feature engineering, prediction API |
| 4 | [Medallion-Architecture-dbt](Sj-Prod/Medallion-Architecture-dbt) | 83+41 | dbt + DuckDB, bronze/silver/gold layers, SQL tests |
| 5 | [AI-Agents-Learning-Platform](Sj-Prod/AI-Agents-Learning-Platform) | 133 | 8 frameworks, 6 patterns, interactive demos |
| 6 | [Real-Time-Streaming](Sj-Prod/Real-Time-Streaming) | 90 | Kafka-style broker, partitions, windowed processing |
| 7 | [Multi-Cloud-Data-Lake](Sj-Prod/Multi-Cloud-Data-Lake) | 91 | AWS/Azure/GCP simulation, Parquet lake, metrics |
| 8 | [Airflow-Orchestration](Sj-Prod/Airflow-Orchestration) | 139 | 5 DAGs, custom operators, simulator (no Airflow needed) |
| 9 | [Enterprise-RAG-System](Sj-Prod/Enterprise-RAG-System) | 79 | ChromaDB, sentence-transformers, extractive fallback |
| 10 | [LLM-Agent-Orchestration](Sj-Prod/LLM-Agent-Orchestration) | 59 | LangGraph, 3-agent pipeline, offline fallback |

### Production Standards

Every system includes:
- `src/settings.py` — centralized environment-based configuration
- `src/logging_config.py` — structured logging (no print statements)
- `.env.example` — documented environment variables
- `RUNNING.md` — build, test, and deploy instructions
- `Dockerfile` + `docker-compose.yml` — container deployment
- Hardened CORS, input validation, specific exception handling

### Quick Start (any system)

```bash
cd Sj-Prod/<System-Name>
pip install -r requirements.txt
python main.py api          # FastAPI on :8000
python main.py ui           # Streamlit on :8501
pytest                      # Run tests
docker compose up --build   # Docker deployment
```

## Learning Modules

14 markdown-based study guides covering ML, AI, cloud platforms, and career development:

| Module | Topic |
|--------|-------|
| 01 | ML Fundamentals |
| 02 | Cloud AI Platform |
| 03 | LLM Essentials |
| 04 | End-to-End ML Pipeline |
| 05 | Generative AI & RAG |
| 06 | MLOps Automation |
| 07 | MLOps Specialization |
| 08 | Advanced Feature Engineering |
| 09 | Data Mesh |
| 10 | Interview Preparation |
| 11 | Negotiation |
| 12 | Career Development |
| 14 | Tech Stack Reference |

## Learning Viewer

Next.js 16 app (React 19, TypeScript, Tailwind) for browsing learning content:

```bash
cd learning-viewer && npm install && npm run dev
# Opens on http://localhost:3000
```

## 4K Cheat Sheets

Generated 3840x2160 PNG cheat sheets:

```bash
python generate_all_4k_cheatsheets.py   # Generate all 17 sheets
```

## Linting

```bash
ruff check Sj-Prod/                     # Lint all systems
```
