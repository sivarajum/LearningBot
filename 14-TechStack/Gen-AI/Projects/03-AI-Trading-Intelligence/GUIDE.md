# AI Trading Intelligence — Complete Project Guide

**Version:** 1.0 | **Date:** March 6, 2026 | **Status:** Phase 1-2 DONE, Phase 3-5 In Progress

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Installation & Setup](#2-installation--setup)
3. [Environment Configuration](#3-environment-configuration)
4. [Architecture & Module Plan](#4-architecture--module-plan)
5. [Code Plan (Module-by-Module)](#5-code-plan-module-by-module)
6. [Test Plan](#6-test-plan)
7. [Deployment Plan](#7-deployment-plan)
8. [Monitoring & Observability](#8-monitoring--observability)
9. [GenAI Skills Usage Strategy](#9-genai-skills-usage-strategy)
10. [Phase-by-Phase Execution Timeline](#10-phase-by-phase-execution-timeline)
11. [Risk & Mitigation](#11-risk--mitigation)
12. [Cost Strategy](#12-cost-strategy)

---

## 1. Project Overview

Build an autonomous algorithmic trading system for Indian markets (NSE/BSE) with: 29+ quantitative strategies, ML-powered signal generation, multi-agent governance (AlphaLab, RiskGuard, ExecOps, DataPulse), SEBI-compliant execution, and cloud-native infrastructure on GCP.

### Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Sharpe Ratio | 0.819 (best) | > 1.5 (ensemble) |
| Max Drawdown | 18.2% (best) | < 15% |
| Win Rate | ~52% | > 55% |
| Strategies backtested | 109 | 186+ |
| Tests passing | 5,661 | 6,000+ |
| Monthly GCP cost | ₹5,000 | ₹5,000 (hard cap) |

---

## 2. Installation & Setup

### 2.1 Prerequisites

```mermaid
flowchart LR
    subgraph PREREQ["✅ Prerequisites"]
        style PREREQ fill:#1a3a2e,color:#e0e0e0,stroke:#4caf50,stroke-width:2px
        PY["Python 3.12"]:::green
        POETRY["Poetry 1.8.3"]:::green
        GC["gcloud CLI"]:::blue
        Docker["Docker"]:::blue
        TF["Terraform 1.6.x"]:::orange
    end

    subgraph ACCOUNTS["🔑 Required Accounts"]
        style ACCOUNTS fill:#3a2a1a,color:#e0e0e0,stroke:#ff9800,stroke-width:2px
        ZERODHA["Zerodha Account<br/>Kite API key"]:::orange
        GCP["GCP Account<br/>ai-trading-prod project"]:::blue
        CLAUDE["Anthropic API Key<br/>Claude for agents"]:::purple
        GEMINI["Google AI Key<br/>Gemini Flash (free)"]:::green
    end

    PREREQ --> ACCOUNTS

    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
    classDef purple fill:#9C27B0,color:#fff,stroke:#6A1B9A
```

### 2.2 Setup Steps

1. **Clone repo** and install Poetry
2. **Install dependencies** — `poetry install`
3. **GCP authentication** — `gcloud auth login` + `gcloud auth application-default login`
4. **Set project** — `gcloud config set project ai-trading-prod`
5. **Verify BigQuery access** — `bq ls ai_trading_machine`
6. **Kite API setup** — Get API key from Zerodha Developer Console
7. **Environment file** — Create `.env` with all keys
8. **Run tests** — `PYTHONPATH=src python -m pytest tests/unit/sjarvis/ -q`

### 2.3 Existing Directory Structure

```
ai-trading-machine/
├── src/sjarvis/
│   ├── domain/              # Pure business logic
│   │   ├── backtesting/     # BacktestEngine, metrics
│   │   ├── governance/      # Circuit breaker, validator
│   │   ├── trading/         # Order, Position, Portfolio
│   │   ├── strategy/        # Signal, StrategyBase
│   │   ├── compliance/      # SEBI validator
│   │   └── risk/            # VaR, drawdown, limits
│   ├── application/         # Use cases
│   │   ├── strategy_runners/ # 186 unique runners
│   │   ├── strategy_registry.py # 195 entries
│   │   ├── trading/         # Order placement
│   │   └── pipelines/       # Signal generation
│   ├── infrastructure/      # External adapters
│   │   ├── bigquery/        # BQ client, repos
│   │   ├── kite/            # Kite API client
│   │   ├── firestore/       # State stores
│   │   └── pubsub/          # Message bus
│   ├── interface/           # Entry points
│   │   ├── workers/         # 9 Cloud Run workers
│   │   └── api/             # FastAPI
│   └── assistant/           # Jarvis AI agents
│       ├── agents/          # 4 agents
│       └── tools/           # Agent tools
├── tests/                   # 5,661+ tests
├── scripts/                 # Operational scripts
├── config/                  # YAML/JSON configs
├── infra/terraform/sjarvis/ # Terraform IaC
└── bigquery/                # DDLs + procedures
```

---

## 3. Environment Configuration

### 3.1 Environment Variables

```mermaid
flowchart TD
    subgraph ENV["🔐 Environment"]
        style ENV fill:#2d1b4e,color:#e0e0e0,stroke:#8e6cc0,stroke-width:2px
        GCP_ENV["GCP<br/>GCP_PROJECT_ID<br/>BQ_DATASET<br/>BQ_DATA_PROJECT"]:::blue
        KITE_ENV["Kite API<br/>KITE_API_KEY<br/>KITE_ACCESS_TOKEN"]:::orange
        LLM_ENV["LLM<br/>ANTHROPIC_API_KEY<br/>GOOGLE_API_KEY"]:::purple
        TRADE_ENV["Trading<br/>ENVIRONMENT=paper<br/>TOTAL_CAPITAL_INR"]:::green
    end

    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
    classDef purple fill:#9C27B0,color:#fff,stroke:#6A1B9A
```

### 3.2 Key Config Files

| Config | Path | Purpose |
|--------|------|---------|
| Symbol universe | `config/symbol_universe.yaml` | 374 NSE symbols |
| Market holidays | `config/market-holidays.json` | NSE trading calendar |
| Backtest periods | `config/backtesting/backtest_periods.json` | 7 walk-forward periods |
| Paper trading | `config/paper_trading.yaml` | Paper trading settings |
| Kill switch | `config/kill_switch.yaml` | Emergency halt |

---

## 4. Architecture & Module Plan

### 4.1 Clean Architecture Layers

```mermaid
flowchart TB
    subgraph LAYERS["🏗️ Clean Architecture"]
        style LAYERS fill:#1e3a5f,color:#e0e0e0,stroke:#4a90d9,stroke-width:2px
        DOM["Domain Layer<br/>Pure business logic<br/>stdlib only"]:::green
        APP["Application Layer<br/>Use cases, runners<br/>imports domain"]:::blue
        INFRA["Infrastructure Layer<br/>BigQuery, Kite, Firestore<br/>implements domain ports"]:::orange
        IFACE["Interface Layer<br/>Workers, API, CLI<br/>wires everything"]:::purple
        ASST["Assistant Layer<br/>AI agents, tools<br/>thin facades only"]:::teal
    end

    DOM --> APP --> INFRA --> IFACE --> ASST

    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
    classDef purple fill:#9C27B0,color:#fff,stroke:#6A1B9A
    classDef teal fill:#009688,color:#fff,stroke:#00695C
```

### 4.2 Data Flow

```mermaid
flowchart LR
    subgraph DAILY["Daily Trading Flow"]
        style DAILY fill:#1a2a3a,color:#e0e0e0,stroke:#42a5f5,stroke-width:2px
        FETCH["Kite API<br/>OHLCV fetch"]:::blue
        BQ3["BigQuery<br/>Store + retrieve"]:::purple
        STRAT["Strategy Runners<br/>29+ strategies"]:::green
        SIG2["Signal Generation<br/>BUY/SELL/HOLD"]:::orange
        GOV2["Governance Pipeline<br/>CB + SEBI + Risk"]:::red
        EXEC2["Kite API<br/>Order execution"]:::teal
        FILL["BigQuery<br/>fills_fact write"]:::purple
    end

    FETCH --> BQ3 --> STRAT --> SIG2 --> GOV2 --> EXEC2 --> FILL

    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
    classDef purple fill:#9C27B0,color:#fff,stroke:#6A1B9A
    classDef red fill:#F44336,color:#fff,stroke:#C62828
    classDef teal fill:#009688,color:#fff,stroke:#00695C
```

---

## 5. Code Plan (Module-by-Module)

> **Note:** This documents the STRUCTURE and PURPOSE — not implementation code.

### 5.1 Strategy Runner Pattern

```mermaid
flowchart LR
    subgraph PATTERN["Strategy Runner Pattern"]
        style PATTERN fill:#2d1b4e,color:#e0e0e0,stroke:#8e6cc0,stroke-width:2px
        BASE["StrategyBase ABC<br/>generate_signal()"]:::purple
        FETCH2["DataFetcher<br/>OHLCV + indicators"]:::blue
        SIGNAL2["Signal Dataclass<br/>symbol, direction, confidence"]:::green
        REG["StrategyRegistry<br/>195 entries"]:::orange
    end
    BASE --> FETCH2 --> SIGNAL2 --> REG
    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
    classDef purple fill:#9C27B0,color:#fff,stroke:#6A1B9A
```

**Existing modules (Phase 1-2 DONE):**
- 14 daily EOD strategy runners
- 3 intraday runners
- 3 options runners
- 3 futures runners
- 6 ML/sentiment runners
- Strategy registry with 195 entries

### 5.2 Remaining Work (Phase 3-5)

**Phase 3 — Advanced Strategies:**
- Ensemble optimizer (4 methods, SEBI-compliant weighting)
- StrategyMetaLearner (requires 10+ weeks of weekly metrics)
- Parallel backtest with ProcessPoolExecutor

**Phase 4 — Live Trading Readiness:**
- Fix 7 FATAL issues (Telegram dispatch, race conditions, silent ACK)
- Wire circuit breaker into all workers
- Implement DLQ consumer for failed messages

**Phase 5 — Production:**
- 60-day paper trading window (target: May 2026)
- Go-live checklist validation
- P&L drift detector (paper vs backtest)

---

## 6. Test Plan

### 6.1 Current Test Suite

```mermaid
flowchart TD
    subgraph TESTS["🧪 Test Suite — 5,661 Tests"]
        style TESTS fill:#1a3a2e,color:#e0e0e0,stroke:#4caf50,stroke-width:2px
        UT["Unit Tests<br/>5,586 passing<br/>73.65% coverage"]:::green
        ARCH["Architecture Tests<br/>Clean Architecture validation"]:::blue
        SEBI3["SEBI Tests<br/>Compliance verification"]:::orange
        PERF["Performance Tests<br/>Latency benchmarks"]:::red
    end
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
    classDef red fill:#F44336,color:#fff,stroke:#C62828
```

### 6.2 Test Commands

| Command | Scope |
|---------|-------|
| `PYTHONPATH=src python -m pytest tests/unit/sjarvis/ -q` | All unit tests |
| `PYTHONPATH=src python -m pytest tests/architecture/ -v` | Architecture validation |
| `PYTHONPATH=src python -m pytest tests/ -m sebi -v` | SEBI compliance |
| `PYTHONPATH=src python -m pytest tests/performance/ -v` | Performance benchmarks |

### 6.3 Test Coverage Targets

| Module | Current | Target |
|--------|---------|--------|
| Domain | ~85% | 90% |
| Application | ~75% | 80% |
| Infrastructure | ~65% | 75% |
| Interface | ~60% | 70% |
| **Overall** | **73.65%** | **80%** |

---

## 7. Deployment Plan

### 7.1 GCP Deployment Architecture

```mermaid
flowchart TB
    subgraph DEPLOY["☁️ GCP Production"]
        style DEPLOY fill:#1e3a5f,color:#e0e0e0,stroke:#4a90d9,stroke-width:2px

        GIT["GitHub<br/>main branch"]:::grey --> ACT["GitHub Actions<br/>sjarvis-build.yml"]:::blue
        ACT --> REG["Artifact Registry<br/>Docker images"]:::purple
        REG --> CR2["Cloud Run<br/>11 services<br/>Scale-to-zero"]:::green
        CR2 --> PS2["Pub/Sub<br/>9 topics + DLQs"]:::orange
        PS2 --> BQ4["BigQuery<br/>Data warehouse"]:::purple
        BQ4 --> FS3["Firestore<br/>State management"]:::teal

        SCHED2["Cloud Scheduler<br/>9 cron jobs"]:::orange --> PS2
    end

    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
    classDef purple fill:#9C27B0,color:#fff,stroke:#6A1B9A
    classDef teal fill:#009688,color:#fff,stroke:#00695C
    classDef grey fill:#546E7A,color:#fff,stroke:#37474F
```

### 7.2 Deployment Commands

| Step | Command |
|------|---------|
| Lint | `python -m black src tests && python -m isort --profile black src tests && poetry run ruff check --fix src tests` |
| Test | `PYTHONPATH=src python -m pytest tests/unit/sjarvis/ -q --tb=short` |
| Cost guard | `./scripts/gcp/cost_guard.sh --terraform` |
| Terraform | `cd infra/terraform/sjarvis && terraform apply` |
| Health check | `./scripts/gcp/gcp_health_check.sh` |

### 7.3 Cost Protection Rules

| Rule | Enforcement |
|------|-------------|
| Zero always-on instances | `min_instance_count = 0` everywhere |
| CPU throttling always on | Never use `--no-cpu-throttling` |
| No uptime checks on workers | Prevents scale-to-zero |
| Budget: ₹5,000/month hard cap | Billing budget alerts at 25%/50%/80%/100% |

---

## 8. Monitoring & Observability

### 8.1 Health Check

```mermaid
flowchart TB
    subgraph HEALTH["🔍 Health Check — 21 Checks"]
        style HEALTH fill:#1e3a5f,color:#e0e0e0,stroke:#4a90d9,stroke-width:2px
        H1["Cloud Run Services<br/>All Ready=True"]:::green
        H2["Pub/Sub Backlogs<br/>All at 0"]:::green
        H3["Scheduler States<br/>9 ENABLED"]:::blue
        H4["ackDeadline<br/>≥ 300s all subs"]:::orange
        H5["Kite Token<br/>Valid in Secret Mgr"]:::purple
        H6["BigQuery Data<br/>Today's data exists"]:::teal
    end
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
    classDef purple fill:#9C27B0,color:#fff,stroke:#6A1B9A
    classDef teal fill:#009688,color:#fff,stroke:#00695C
```

### 8.2 Key Alerts

| Alert | Condition | Action |
|-------|-----------|--------|
| Circuit breaker OPEN | Drawdown > 20% | Stop all trading, alert Telegram |
| Pub/Sub retry storm | Backlog > 100 | Run `purge_pubsub_backlogs.sh` |
| GCP cost > ₹3,500 | 70% of budget | Review active services |
| Kite token expired | Auth fails | Run token rotation scheduler |
| Zero signals generated | No signals in 24h | Check signal worker + data freshness |

---

## 9. GenAI Skills Usage Strategy

| # | Skill | Module | Implementation |
|---|-------|--------|---------------|
| 1 | LangGraph | Agent orchestrator | Multi-agent state machine for trading decisions |
| 2 | CrewAI | AlphaLab | Quant research team collaboration |
| 3 | RAG | Strategy knowledge | Strategy docs + past performance retrieval |
| 4 | LlamaIndex | Document indexing | SEBI circulars, financial reports |
| 5 | Embeddings | Regime matching | Market regime similarity search |
| 6 | Vector DBs | Firestore + Pinecone | Strategy vectors, regime embeddings |
| 7 | Claude API | Agent reasoning | AlphaLab + RiskGuard decisions |
| 8 | Gemini API | Sentiment | Free-tier news sentiment analysis |
| 9 | Guardrails | Trade validation | SEBI limits, position constraints |
| 10 | Prompt Engineering | All agents | CoT reasoning for trade decisions |
| 11 | PEFT | FinBERT | Fine-tune for Indian market sentiment |
| 12 | XGBoost/ML | Signal generation | ML-based strategy signals |
| 13 | HMM | Regime detection | Bull/bear/sideways market states |
| 14 | Transfer Learning | XGBoost | General → NSE-specific models |

---

## 10. Phase-by-Phase Execution Timeline

```mermaid
gantt
    title AI Trading Intelligence — Timeline
    dateFormat YYYY-MM-DD
    axisFormat %b %d

    section Phase 1-2: DONE ✅
    Data ingestion + 374 symbols        :done, p1, 2025-12-01, 30d
    29 strategy runners                  :done, p2, 2025-12-15, 45d
    Walk-forward backtesting             :done, p3, 2026-01-15, 30d
    Cloud Run deployment (11 services)   :done, p4, 2026-02-01, 28d

    section Phase 3: Advanced (Current)
    Fix 7 FATAL issues                   :active, p5, 2026-03-01, 14d
    Ensemble optimizer                   :p6, 2026-03-15, 14d
    Parallel backtest engine             :p7, 2026-03-29, 10d

    section Phase 4: Paper Trading
    60-day paper trading window          :p8, 2026-03-15, 60d
    P&L drift detector                   :p9, 2026-04-01, 7d
    StrategyMetaLearner activation       :p10, 2026-04-15, 14d

    section Phase 5: Live Trading
    Go-live checklist                    :p11, 2026-05-15, 7d
    Controlled live (1% capital)         :p12, 2026-05-22, 21d
    Full live deployment                 :p13, 2026-06-12, 14d
```

---

## 11. Risk & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Kite API downtime | Medium | High | Fallback to cached data, retry with backoff |
| Strategy overfitting | High | High | Walk-forward validation, 7 OOS periods |
| GCP cost overrun | Medium | Medium | ₹5K hard cap, cost_guard.sh, scale-to-zero |
| SEBI compliance breach | Low | Critical | Automated validation, manual approval required |
| Pub/Sub retry storm | Medium | High | 600s ackDeadline, DLQ, purge script |
| Market flash crash | Low | Critical | Circuit breaker (20% DD), kill switch |

---

## 12. Cost Strategy

| Component | Monthly Cost | Optimization |
|-----------|-------------|--------------|
| Cloud Run (11 services) | ₹300 | Scale-to-zero, CPU throttling |
| BigQuery | ₹500 | Partitioned tables, column pruning |
| Firestore | ₹100 | Minimal writes, batch operations |
| Pub/Sub | ₹50 | DLQ prevents retry storms |
| Kite API | ₹0 | Free with brokerage |
| Gemini Flash | ₹0 | Free tier (15 RPM) |
| Claude API | ₹1,000 | Cache agent patterns |
| **Total** | **~₹2,000-3,000** | **Budget: ₹5,000 hard cap** |
