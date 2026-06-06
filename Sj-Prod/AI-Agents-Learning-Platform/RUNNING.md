# AI Agents Learning Platform -- Running Guide

## Prerequisites

- Python 3.11 or later
- pip (comes with Python)
- Docker and Docker Compose (optional, for containerized deployment)

## Install

```bash
cd Sj-Prod/AI-Agents-Learning-Platform
pip install -r requirements.txt
```

## Running Tests

```bash
# Run the full test suite with coverage
pytest

# Run a single test file
pytest tests/test_knowledge_base.py
pytest tests/test_demos.py
pytest tests/test_api.py

# Run a specific test class or test
pytest tests/test_api.py::TestHealth
pytest tests/test_api.py::TestHealth::test_health_returns_200

# Run without coverage enforcement
pytest --no-cov

# Run with verbose output
pytest -v
```

The project requires 80% code coverage to pass (configured in `pytest.ini`).

## Running the System

The `main.py` entry point supports three modes:

### API only (default)

Starts the FastAPI server on port 8000 with auto-reload.

```bash
python main.py api
```

### UI only

Starts the Streamlit dashboard on port 8501. Requires the API to already be running.

```bash
python main.py ui
```

### Both API and UI

Starts the API server and Streamlit dashboard together.

```bash
python main.py all
```

## Running with Docker

Build and start both services:

```bash
docker compose up --build
```

This starts:

- **API** on `http://localhost:8000`
- **UI** on `http://localhost:8501`

The UI container waits for the API health check to pass before starting.

To run in the background:

```bash
docker compose up --build -d
```

To stop:

```bash
docker compose down
```

## API Endpoint Reference

Base URL: `http://localhost:8000`

| Method | Path                | Description                                      |
|--------|---------------------|--------------------------------------------------|
| GET    | `/health`           | Health check. Returns `{"status": "healthy"}`     |
| GET    | `/frameworks`       | List all 8 AI agent frameworks                    |
| GET    | `/frameworks?category=orchestration` | Filter frameworks by category       |
| GET    | `/frameworks/{name}`| Get details for a specific framework (e.g. `langchain`) |
| GET    | `/patterns`         | List all 6 agent design patterns                  |
| GET    | `/patterns/{name}`  | Get details for a specific pattern (e.g. `react`) |
| GET    | `/comparisons`      | Get the framework comparison matrix (scores 1-5)  |
| GET    | `/demos`            | List available interactive demos                  |
| POST   | `/demos/run`        | Run a demo. Body: `{"pattern": "react", "task": "..."}` |

### Framework categories

- `orchestration` -- LangChain, LangGraph
- `multi-agent` -- AutoGen, CrewAI
- `platform` -- OpenAI Assistants, Claude Agent SDK
- `rag` -- LlamaIndex
- `optimization` -- DSPy

### Available demo patterns

- `react` -- ReAct (Reason + Act)
- `plan_and_execute` -- Plan and Execute
- `reflection` -- Reflection / Self-Critique
- `multi_agent_debate` -- Multi-Agent Debate

### Example API calls

```bash
# Health check
curl http://localhost:8000/health

# List all frameworks
curl http://localhost:8000/frameworks

# Get a specific framework
curl http://localhost:8000/frameworks/langchain

# Filter frameworks by category
curl "http://localhost:8000/frameworks?category=orchestration"

# List patterns
curl http://localhost:8000/patterns

# Run a demo
curl -X POST http://localhost:8000/demos/run \
  -H "Content-Type: application/json" \
  -d '{"pattern": "react", "task": "How to scale microservices"}'
```

## Production Deployment Notes

### Environment variables

| Variable  | Default                | Description                  |
|-----------|------------------------|------------------------------|
| `API_URL` | `http://localhost:8000`| API base URL used by the UI  |

### Security considerations

- The API currently allows all CORS origins (`*`). Restrict `allow_origins` in `src/api.py` for production.
- No authentication is configured. Add API key or OAuth middleware for production use.
- The demos are simulated (no real LLM calls), so there is no risk of prompt injection or runaway costs.

### Scaling

- The API is stateless and can be horizontally scaled behind a load balancer.
- For production, run uvicorn with multiple workers: `uvicorn src.api:app --workers 4 --host 0.0.0.0 --port 8000`.
- Consider using gunicorn as the process manager: `gunicorn src.api:app -k uvicorn.workers.UvicornWorker -w 4`.

### Linting

```bash
# From the Sj-Prod directory (uses shared ruff.toml)
ruff check AI-Agents-Learning-Platform/
ruff format AI-Agents-Learning-Platform/
```
