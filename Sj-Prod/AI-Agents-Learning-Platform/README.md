# AI Agents Learning Platform

AI agent frameworks and patterns explorer — 8 frameworks, 6 patterns, interactive demos. FastAPI API + Streamlit dashboard. No LLM API key required.

## What It Does

- **Knowledge Base**: Structured data on 8 AI agent frameworks and 6 agentic design patterns
- **Framework Comparison**: Quantitative scoring across 6 dimensions (setup, multi-agent, production readiness, RAG, flexibility, community)
- **Interactive Demos**: 4 agent pattern demos (ReAct, Plan-and-Execute, Reflection, Multi-Agent Debate) as deterministic Python — no LLM calls needed
- **REST API**: FastAPI endpoints for framework data, pattern details, and live demos
- **Dashboard**: Three-tab Streamlit UI (framework explorer, pattern visualizer, demo runner)

## Frameworks Covered

| Framework | Complexity | Best For |
|-----------|------------|----------|
| LangChain | Medium | General-purpose LLM apps |
| LangGraph | Medium-High | Multi-agent workflows with loops |
| AutoGen | Medium | Multi-agent collaborative problem solving |
| CrewAI | Low-Medium | Team-based workflows with roles |
| OpenAI Assistants | Low | Quick deployment, minimal infra |
| Claude Agent SDK | Low-Medium | Reliable, safe agents with Claude |
| LlamaIndex | Medium | RAG and data-augmented LLM apps |
| DSPy | High | Systematic prompt optimization |

## Quick Start

```bash
pip install -r requirements.txt
python main.py api         # API on :8005
python main.py ui          # Dashboard on :8501
python main.py all         # Both
```

## Testing

```bash
pytest                     # 133 tests, 98.67% coverage
```

## Docker

```bash
docker compose up --build
```

See [RUNNING.md](RUNNING.md) for full build, test, and deployment instructions.
