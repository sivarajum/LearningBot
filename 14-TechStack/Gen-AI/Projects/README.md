# 🚀 GenAI Real-World Projects

> **5 projects that are ruling and breaking things in the world right now — built with every GenAI skill in this repository**

---

## 📋 Project Overview

```mermaid
graph TB
    subgraph Hub["🧠 GenAI Projects Hub"]
        direction TB
        P1["🤖 01 — AI Software Engineer<br/><i>Autonomous coding agents</i>"]
        P2["💊 02 — AI Drug Discovery<br/><i>Molecular design + clinical AI</i>"]
        P3["📈 03 — AI Trading Intelligence<br/><i>Multi-agent NSE/BSE trading</i>"]
        P4["🔍 04 — Enterprise Knowledge AI<br/><i>RAG search + deep research</i>"]
        P5["🎬 05 — AI Content Studio<br/><i>Video, image, voice generation</i>"]
    end

    subgraph Skills["🧰 27 GenAI Skills"]
        direction LR
        S1["LLMs: OpenAI · Claude · Gemini"]
        S2["RAG: LlamaIndex · Embeddings · Vectors"]
        S3["Agents: LangGraph · CrewAI · Autogen"]
        S4["Training: RLHF · PEFT · Distributed"]
        S5["Infra: Inference · Quantization · AWS"]
    end

    P1 --- S1 & S2 & S3
    P2 --- S4 & S2 & S1
    P3 --- S3 & S1 & S5
    P4 --- S2 & S1 & S3
    P5 --- S4 & S5 & S1

    style Hub fill:#1a1a2e,color:#fff,stroke:#00B4D8,stroke-width:3px
    style Skills fill:#0f3460,color:#fff,stroke:#FFB703,stroke-width:2px

    style P1 fill:#E63946,color:#fff,stroke:#E63946,stroke-width:2px
    style P2 fill:#00B4D8,color:#fff,stroke:#00B4D8,stroke-width:2px
    style P3 fill:#2ECC71,color:#fff,stroke:#2ECC71,stroke-width:2px
    style P4 fill:#9B59B6,color:#fff,stroke:#9B59B6,stroke-width:2px
    style P5 fill:#FFB703,color:#000,stroke:#FFB703,stroke-width:2px

    style S1 fill:#E74C3C,color:#fff,stroke:#E74C3C
    style S2 fill:#3498DB,color:#fff,stroke:#3498DB
    style S3 fill:#F39C12,color:#fff,stroke:#F39C12
    style S4 fill:#8E44AD,color:#fff,stroke:#8E44AD
    style S5 fill:#1ABC9C,color:#fff,stroke:#1ABC9C
```

---

## 🗂️ The Projects

### [01 — AI Software Engineer](./01-AI-Software-Engineer/PLAN.md) 🤖
> Inspired by **Devin, OpenHands, Cursor, GitHub Copilot**

Build an autonomous AI coding agent that can understand requirements, plan implementation, write code, run tests, fix bugs, and create PRs — replacing weeks of work with hours.

| Key Stat | Value |
|----------|-------|
| Real-world proof | Nubank: 6M LOC migration, 8-12x faster, 20x cost savings |
| Architecture | Multi-agent: Planner → Coder → Reviewer → Executor |
| Core skills | LangGraph, RAG, CrewAI, ClaudeAPI, Guardrails |

---

### [02 — AI Drug Discovery](./02-AI-Drug-Discovery/PLAN.md) 💊
> Inspired by **AlphaFold 3, Isomorphic Labs, Insilico Medicine, Recursion**

AI pipeline that identifies drug targets from literature, predicts protein structures, generates novel molecules, screens candidates computationally, and provides clinical trial intelligence.

| Key Stat | Value |
|----------|-------|
| Real-world proof | Insilico: drug to Phase II in 30 months (vs 12 years traditional) |
| Architecture | Target ID → Structure → Generation → Screening → Clinical |
| Core skills | Keras, DistributedTraining, RLHF, NLP, HuggingFace |

---

### [03 — AI Trading Intelligence](./03-AI-Trading-Intelligence/PLAN.md) 📈
> Inspired by **Renaissance Technologies, Two Sigma, Citadel, sjarvis**

Autonomous multi-agent trading system for NSE/BSE with 29+ strategy runners, LLM-powered analysis, real-time risk management, and SEBI compliance — modeled directly after the sjarvis codebase.

| Key Stat | Value |
|----------|-------|
| Real-world proof | sjarvis: 374 symbols, 4,216 tests, 29 strategies, paper trading live |
| Architecture | Data → Intelligence → Governance → Execution → Output |
| Core skills | LangGraph, AgenticAI, GeminiAPI, Embeddings, RLHF |

---

### [04 — Enterprise Knowledge AI](./04-Enterprise-Knowledge-AI/PLAN.md) 🔍
> Inspired by **Perplexity, Glean, Google NotebookLM, OpenAI Deep Research**

Enterprise-grade knowledge system with multi-source RAG, autonomous deep research agents, and verified report generation with citations — replacing analysts with AI researchers.

| Key Stat | Value |
|----------|-------|
| Real-world proof | Perplexity: 100M+ monthly users, $9B valuation. Glean: 1000+ enterprises |
| Architecture | Sources → Ingestion → Knowledge → AI → Output |
| Core skills | RAG, AdvancedRAG, LlamaIndex, Vector-Databases, LangGraph |

---

### [05 — AI Content Studio](./05-AI-Content-Studio/PLAN.md) 🎬
> Inspired by **Sora, Runway Gen-3, Midjourney V6, ElevenLabs, Adobe Firefly**

Multi-modal content factory that generates images, videos, voiceovers, and music from text — producing 1,000+ branded assets per day at $0.50/asset instead of $50-500.

| Key Stat | Value |
|----------|-------|
| Real-world proof | Midjourney: 16M+ users, $200M+ revenue. Adobe Firefly: 6.5B+ images |
| Architecture | Brief → Creative Director → Generators → QA → Composition |
| Core skills | HuggingFace, PEFT, DistributedTraining, RLHF, NLP |

---

## 🧬 Skills Matrix — Which Skills Power Which Project

```mermaid
graph LR
    subgraph Legend["📖 Legend"]
        direction LR
        H["🟢 Heavy use"]
        M["🟡 Moderate use"]
        L["🔵 Light use"]
    end

    style Legend fill:#1a1a2e,color:#fff,stroke:#FFB703,stroke-width:2px
    style H fill:#2ECC71,color:#fff,stroke:#2ECC71
    style M fill:#F39C12,color:#fff,stroke:#F39C12
    style L fill:#3498DB,color:#fff,stroke:#3498DB
```

| GenAI Skill | 🤖 AI CodeAgent | 💊 Drug Discovery | 📈 Trading | 🔍 Knowledge AI | 🎬 Content Studio |
|-------------|:-:|:-:|:-:|:-:|:-:|
| **OpenAI-GPT** | 🟢 | 🟡 | 🟡 | 🟢 | 🟢 |
| **ClaudeAPI** | 🟢 | 🟡 | 🟢 | 🟢 | 🟢 |
| **GeminiAPI** | 🟡 | 🔵 | 🟢 | 🟡 | 🟢 |
| **HuggingFace** | 🟡 | 🟢 | 🟡 | 🟡 | 🟢 |
| **Keras** | 🔵 | 🟢 | 🟡 | 🔵 | 🟢 |
| **NLP** | 🟡 | 🟢 | 🟡 | 🟢 | 🟢 |
| **RAG** | 🟢 | 🟡 | 🟡 | 🟢 | 🟡 |
| **AdvancedRAG** | 🟢 | 🟡 | 🟡 | 🟢 | 🟡 |
| **LlamaIndex** | 🟢 | 🟡 | 🔵 | 🟢 | 🟡 |
| **LangChain** | 🟢 | 🟡 | 🟢 | 🟢 | 🟡 |
| **LangGraph** | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| **Embeddings** | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| **Vector-Databases** | 🟢 | 🟢 | 🟡 | 🟢 | 🟡 |
| **AgenticAI** | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| **CrewAI** | 🟢 | 🟢 | 🟡 | 🟢 | 🟢 |
| **Autogen** | 🟢 | 🟡 | 🟡 | 🟢 | 🟡 |
| **Guardrails** | 🟢 | 🟡 | 🟢 | 🟢 | 🟢 |
| **PromptEngineering** | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| **RLHF** | 🟡 | 🟢 | 🟢 | 🟡 | 🟢 |
| **PEFT-FineTuning** | 🟡 | 🟢 | 🟡 | 🟡 | 🟢 |
| **TransferLearning** | 🟡 | 🟢 | 🟡 | 🟡 | 🟢 |
| **FewShotZeroShot** | 🟢 | 🟡 | 🟡 | 🟢 | 🟢 |
| **ModelQuantization** | 🟡 | 🟢 | 🟡 | 🟡 | 🟢 |
| **InferenceEngines** | 🟡 | 🟢 | 🟢 | 🟡 | 🟢 |
| **DistributedTraining** | 🔵 | 🟢 | 🟡 | 🔵 | 🟢 |
| **AWS-AI-ML** | 🟡 | 🟢 | 🟡 | 🟡 | 🟢 |

**Coverage: 27/27 skills used across all 5 projects — zero gaps.**

---

## 🗺️ Project Interconnections

```mermaid
graph TB
    subgraph Ecosystem["🌐 GenAI Projects Ecosystem"]
        P1_2["🤖 AI Software<br/>Engineer"]
        P2_2["💊 Drug<br/>Discovery"]
        P3_2["📈 Trading<br/>Intelligence"]
        P4_2["🔍 Knowledge<br/>AI"]
        P5_2["🎬 Content<br/>Studio"]
    end

    P4_2 -->|"Research feeds<br/>all projects"| P1_2
    P4_2 -->|"Literature<br/>mining"| P2_2
    P4_2 -->|"Market<br/>research"| P3_2
    P4_2 -->|"Brand<br/>intelligence"| P5_2

    P1_2 -->|"Auto-builds<br/>integrations"| P2_2
    P1_2 -->|"Codes trading<br/>strategies"| P3_2
    P1_2 -->|"Builds content<br/>pipelines"| P5_2

    P3_2 -->|"Budget allocation<br/>for compute"| P2_2
    P3_2 -->|"ROI models<br/>for campaigns"| P5_2

    P5_2 -->|"Visualises<br/>molecules"| P2_2
    P5_2 -->|"Trading<br/>dashboards"| P3_2

    style Ecosystem fill:#1a1a2e,color:#fff,stroke:#00B4D8,stroke-width:3px
    style P1_2 fill:#E63946,color:#fff,stroke:#E63946,stroke-width:3px
    style P2_2 fill:#00B4D8,color:#fff,stroke:#00B4D8,stroke-width:3px
    style P3_2 fill:#2ECC71,color:#fff,stroke:#2ECC71,stroke-width:3px
    style P4_2 fill:#9B59B6,color:#fff,stroke:#9B59B6,stroke-width:3px
    style P5_2 fill:#FFB703,color:#000,stroke:#FFB703,stroke-width:3px
```

---

## 🚧 Status

| Project | Architecture | Implementation | Tests |
|---------|:-:|:-:|:-:|
| 01 — AI Software Engineer | ✅ PLAN.md | 🔜 Pending | 🔜 Pending |
| 02 — AI Drug Discovery | ✅ PLAN.md | 🔜 Pending | 🔜 Pending |
| 03 — AI Trading Intelligence | ✅ PLAN.md | 🔜 Pending | 🔜 Pending |
| 04 — Enterprise Knowledge AI | ✅ PLAN.md | 🔜 Pending | 🔜 Pending |
| 05 — AI Content Studio | ✅ PLAN.md | 🔜 Pending | 🔜 Pending |

> **Next:** Pick a project and start implementation. Each project will get `src/`, `tests/`, `config/`, and component-specific modules.
