# GenAI Nexus — Technical Design Document

## End-to-End Local Execution with Local LLaMA

**Version:** 1.0 | **Date:** 2026-03-05

> How to run all 26 Gen-AI tools locally, including local LLaMA via Ollama, with zero cloud API dependency.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State Analysis](#2-current-state-analysis)
3. [Architecture: Local-First Design](#3-architecture-local-first-design)
4. [Component Readiness Matrix](#4-component-readiness-matrix)
5. [Local LLaMA Integration (Ollama)](#5-local-llama-integration-ollama)
6. [Code Changes Required](#6-code-changes-required)
7. [Dependency Resolution Strategy](#7-dependency-resolution-strategy)
8. [Execution Modes: Local-Only Configuration](#8-execution-modes-local-only-configuration)
9. [Hardware Requirements & Performance](#9-hardware-requirements--performance)
10. [End-to-End Run Playbook](#10-end-to-end-run-playbook)
11. [Known Limitations & Workarounds](#11-known-limitations--workarounds)
12. [Testing Strategy](#12-testing-strategy)

---

## 1. Executive Summary

**Goal:** Run GenAI Nexus end-to-end on a local machine with **zero cloud API calls**, using a local LLaMA model (via Ollama) as the universal LLM backend.

**Key finding:** The codebase is architecturally ready — every module already has a demo fallback. The gap is that there is **no local LLM provider** wired in. All real LLM calls go to OpenAI/Claude/Gemini APIs. We need to add an **Ollama client** and wire it into the Router + LangChain chains + LangGraph workflow.

**Effort estimate:**

| Category                           | Files to Create | Files to Modify | LOC      |
| ---------------------------------- | --------------- | --------------- | -------- |
| Ollama LLM client                  | 1               | 0               | ~200     |
| Router + settings integration      | 0               | 3               | ~80      |
| LangChain/LangGraph Ollama adapter | 0               | 2               | ~40      |
| RAG local embeddings config        | 0               | 2               | ~20      |
| Environment config                 | 0               | 2               | ~15      |
| **Total**                          | **1**           | **9**           | **~355** |

---

## 2. Current State Analysis

### What Already Works Locally (No Changes)

| Module                   | File                                  | Runs Locally? | Notes                                          |
| ------------------------ | ------------------------------------- | :-----------: | ---------------------------------------------- |
| NLP Text Processor       | `src/nlp/text_processor.py`           |       ✅       | spaCy fallback to regex if not installed       |
| Embeddings (HuggingFace) | `src/embeddings/embedding_service.py` |       ✅       | `all-MiniLM-L6-v2` runs fully local (384d)     |
| ChromaDB Vector Store    | `src/vectorstore/chroma_store.py`     |       ✅       | In-memory or local persistent storage          |
| Basic RAG                | `src/rag/basic_rag.py`                |       ⚠️       | Retrieval works locally, generation needs LLM  |
| Advanced RAG             | `src/rag/advanced_rag.py`             |       ⚠️       | HyDE/hybrid/rerank local, generation needs LLM |
| LlamaIndex               | `src/rag/llama_indexer.py`            |       ⚠️       | Indexing local, query needs LLM                |
| Prompt Templates         | `src/prompts/prompt_templates.py`     |       ✅       | Pure data, no external deps                    |
| Few-Shot Builder         | `src/prompts/few_shot_examples.py`    |       ✅       | Pure data, no external deps                    |
| Guardrails/Safety        | `src/safety/output_validator.py`      |       ✅       | All rule-based, no LLM needed                  |
| HuggingFace Models       | `src/huggingface/hf_models.py`        |       ✅       | Runs locally (downloads models on first use)   |
| Keras LSTM               | `src/models/sentiment_model.py`       |       ✅       | Pure local training (CPU or GPU)               |
| Transfer Learning        | `src/models/transfer_adapter.py`      |       ✅       | Local DistilBERT (downloads once, caches)      |
| RLHF Pipeline            | `src/training/rlhf_feedback.py`       |       ✅       | Heuristic reward model, no LLM calls           |
| Distributed Trainer      | `src/training/distributed_trainer.py` |       ✅       | Config + demo, no external deps                |
| Quantizer                | `src/optimization/quantizer.py`       |       ✅       | bitsandbytes + demo benchmarks                 |
| Knowledge Base           | `data/knowledge_base/`                |       ✅       | Static text files                              |

### What Needs API Keys Today (Must Fix for Local)

| Module             | File                                   | Current LLM             | What's Needed                       |
| ------------------ | -------------------------------------- | ----------------------- | ----------------------------------- |
| OpenAI Client      | `src/llm/openai_client.py`             | OpenAI API              | → Ollama OpenAI-compatible endpoint |
| Claude Client      | `src/llm/claude_client.py`             | Anthropic API           | → Ollama endpoint (or skip)         |
| Gemini Client      | `src/llm/gemini_client.py`             | Google API              | → Ollama endpoint (or skip)         |
| LLM Router         | `src/llm/llm_router.py`                | Routes to 3 APIs        | → Add `"local"` route to Ollama     |
| LangChain Chains   | `src/chains/analysis_chains.py`        | `ChatOpenAI`            | → `ChatOllama` or OpenAI-compat     |
| LangGraph Workflow | `src/graph/startup_workflow.py`        | Chains + Agents         | → Inherits from chains fix          |
| ReAct Agent        | `src/agents/agentic_core.py`           | LangChain Agent         | → Uses local LLM via chains         |
| CrewAI             | `src/agents/crew_team.py`              | CrewAI default LLM      | → Configure Ollama backend          |
| AutoGen            | `src/agents/autogen_debate.py`         | AutoGen default         | → Configure local endpoint          |
| PEFT/LoRA          | `src/training/peft_trainer.py`         | Downloads LLaMA from HF | → Use local model path              |
| vLLM Server        | `src/optimization/inference_server.py` | Requires model path     | → Point to local model              |
| AWS Client         | `src/cloud/aws_client.py`              | AWS APIs                | → Skip or mock (local has no AWS)   |

---

## 3. Architecture: Local-First Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                     LOCAL MACHINE (macOS / Linux)                     │
│                                                                       │
│  ┌─────────────────────┐      ┌───────────────────────────────┐      │
│  │  Ollama Server       │      │  GenAI Nexus Application      │      │
│  │  (background daemon) │◄────►│                               │      │
│  │                      │      │  CLI (main.py)                │      │
│  │  Models:             │      │  Streamlit (app.py)           │      │
│  │  • llama3.2:3b       │      │                               │      │
│  │  • llama3.1:8b       │      │  ┌───────────────────────┐   │      │
│  │  • codellama:7b      │      │  │ src/llm/ollama_client │   │      │
│  │  • nomic-embed-text  │      │  │ (NEW — to be created) │   │      │
│  │                      │      │  └───────────┬───────────┘   │      │
│  │  API: localhost:11434│      │              │               │      │
│  │  OpenAI-compat:      │      │  ┌───────────▼───────────┐   │      │
│  │    localhost:11434/v1│      │  │ LLM Router             │   │      │
│  └─────────────────────┘      │  │ (+ "local" route)      │   │      │
│                                │  └───────────┬───────────┘   │      │
│  ┌─────────────────────┐      │              │               │      │
│  │  ChromaDB (embedded) │      │  ┌───────────▼───────────┐   │      │
│  │  ./data/chroma_db    │◄────►│  │ Pipeline Orchestrator  │   │      │
│  └─────────────────────┘      │  │ (all 26 tools)         │   │      │
│                                │  └───────────────────────┘   │      │
│  ┌─────────────────────┐      │                               │      │
│  │  HuggingFace Cache   │      └───────────────────────────────┘      │
│  │  ~/.cache/huggingface│                                             │
│  └─────────────────────┘                                             │
└─────────────────────────────────────────────────────────────────────┘
```

### Why Ollama?

| Feature               | Ollama                           | llama.cpp               | LocalAI  | LM Studio |
| --------------------- | -------------------------------- | ----------------------- | -------- | --------- |
| OpenAI-compatible API | ✅ `/v1/chat/completions`         | ❌ (only server mode)    | ✅        | ✅         |
| One-command install   | ✅ `brew install ollama`          | ❌ (compile from source) | ⚠️ Docker | ✅         |
| Model management      | ✅ `ollama pull`                  | ❌ manual GGUF download  | ❌        | ✅ GUI     |
| LangChain integration | ✅ `ChatOllama` built-in          | ❌                       | ⚠️        | ❌         |
| CrewAI support        | ✅ native                         | ❌                       | ❌        | ❌         |
| Embeddings API        | ✅ `ollama pull nomic-embed-text` | ❌                       | ⚠️        | ❌         |
| Function calling      | ✅ (Llama 3.1+)                   | ⚠️                       | ⚠️        | ❌         |
| macOS Metal GPU       | ✅ auto-detected                  | ✅                       | ❌        | ✅         |

**Verdict:** Ollama is the only tool that gives us OpenAI-compatible API, LangChain native integration, embeddings, function calling, AND one-command install. It's the clear winner for local LLM.

---

## 4. Component Readiness Matrix

### Readiness Levels

- 🟢 **READY** — Works locally out of the box, no changes
- 🟡 **CONFIG ONLY** — Works locally with config/env change (no code changes)
- 🟠 **MINOR CODE** — Needs <20 lines of code changes
- 🔴 **NEW CODE** — Needs new file or >50 lines of changes
- ⚫ **SKIP** — Not applicable for local execution

| #   | Module               | Readiness | What's Needed                                   | Priority |
| --- | -------------------- | :-------: | ----------------------------------------------- | :------: |
| 1   | NLP Text Processor   |  🟢 READY  | —                                               |    —     |
| 2   | Prompt Templates     |  🟢 READY  | —                                               |    —     |
| 3   | Few-Shot Builder     |  🟢 READY  | —                                               |    —     |
| 4   | Guardrails/Safety    |  🟢 READY  | —                                               |    —     |
| 5   | Knowledge Base       |  🟢 READY  | —                                               |    —     |
| 6   | Embeddings (HF)      | 🟡 CONFIG  | Set `EMBEDDING_MODEL=huggingface` in .env       |    P1    |
| 7   | ChromaDB             |  🟢 READY  | —                                               |    —     |
| 8   | HuggingFace Models   | 🟡 CONFIG  | First run downloads ~1GB models, then cached    |    P2    |
| 9   | Keras LSTM           |  🟢 READY  | —                                               |    —     |
| 10  | Transfer Learning    | 🟡 CONFIG  | First run downloads DistilBERT (~250MB)         |    P2    |
| 11  | RLHF Pipeline        |  🟢 READY  | —                                               |    —     |
| 12  | Distributed Trainer  |  🟢 READY  | Demo mode only (no multi-GPU needed)            |    —     |
| 13  | Quantizer            | 🟡 CONFIG  | Needs `bitsandbytes` + local model path         |    P3    |
| 14  | **Ollama Client**    |   🔴 NEW   | **Create `src/llm/ollama_client.py`**           |  **P0**  |
| 15  | **LLM Router**       |  🟠 MINOR  | Add `"local"` route to Ollama client            |  **P0**  |
| 16  | **Settings**         |  🟠 MINOR  | Add Ollama config fields                        |  **P0**  |
| 17  | **LangChain Chains** |  🟠 MINOR  | Swap `ChatOpenAI` → `ChatOllama` when local     |  **P0**  |
| 18  | LangGraph Workflow   |  🟢 READY  | Inherits from chains fix (no direct LLM calls)  |    —     |
| 19  | Basic RAG            |  🟠 MINOR  | Pass local LLM to generate step                 |    P1    |
| 20  | Advanced RAG         |  🟠 MINOR  | Same as Basic RAG                               |    P1    |
| 21  | LlamaIndex           |  🟠 MINOR  | Configure `Ollama` LLM in LlamaIndex            |    P1    |
| 22  | ReAct Agent          |  🟠 MINOR  | LangChain agent uses ChatOllama                 |    P1    |
| 23  | CrewAI               |  🟠 MINOR  | Set `OPENAI_API_BASE=http://localhost:11434/v1` |    P1    |
| 24  | AutoGen              |  🟠 MINOR  | Configure local endpoint in OAI_CONFIG_LIST     |    P1    |
| 25  | PEFT/LoRA            | 🟡 CONFIG  | Set `PEFT_BASE_MODEL` to local path             |    P2    |
| 26  | vLLM Server          | 🟡 CONFIG  | Point to local model directory                  |    P2    |
| 27  | OpenAI Client        |  🟠 MINOR  | Add `base_url` override for Ollama compat       |    P1    |
| 28  | Claude Client        |  ⚫ SKIP   | No local equivalent; route to Ollama via Router |    —     |
| 29  | Gemini Client        |  ⚫ SKIP   | No local equivalent; route to Ollama via Router |    —     |
| 30  | AWS Client           |  ⚫ SKIP   | Cloud-only; runs in demo mode locally           |    —     |

---

## 5. Local LLaMA Integration (Ollama)

### 5.1 Prerequisites (One-Time Setup)

```bash
# 1. Install Ollama
brew install ollama          # macOS
# curl -fsSL https://ollama.ai/install.sh | sh  # Linux

# 2. Start Ollama server (runs in background)
ollama serve &

# 3. Pull models (sizes are for quantized GGUF versions)
ollama pull llama3.2:3b          # 2.0 GB — fastest, good for demo/quick mode
ollama pull llama3.1:8b          # 4.7 GB — best quality for local (recommended)
ollama pull codellama:7b         # 3.8 GB — specialized for code generation
ollama pull nomic-embed-text     # 274 MB — local embeddings (768d)

# 4. Verify
ollama list                      # Should show all 4 models
curl http://localhost:11434/v1/chat/completions \
  -d '{"model":"llama3.2:3b","messages":[{"role":"user","content":"hello"}]}'
```

### 5.2 Model Selection Strategy

| Task                 | Recommended Model  | Why                         |
| -------------------- | ------------------ | --------------------------- |
| Market research      | `llama3.1:8b`      | Best reasoning for analysis |
| Competitive analysis | `llama3.1:8b`      | Needs detailed output       |
| Code generation      | `codellama:7b`     | Specialized for code        |
| Pitch content        | `llama3.2:3b`      | Creative writing, speed OK  |
| Fast summary         | `llama3.2:3b`      | Low latency                 |
| Embeddings           | `nomic-embed-text` | 768d, fast, good quality    |
| Function calling     | `llama3.1:8b`      | Best tool-use support       |

### 5.3 Ollama OpenAI-Compatible API

Ollama exposes an **OpenAI-compatible endpoint** at `http://localhost:11434/v1/`:

```python
# This means the existing OpenAI client can work with Ollama!
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # Ollama ignores auth, but client requires a value
)

response = client.chat.completions.create(
    model="llama3.1:8b",
    messages=[{"role": "user", "content": "What is the TAM for legal tech?"}],
    temperature=0.3,
)
print(response.choices[0].message.content)
```

### 5.4 LangChain Integration

```python
# LangChain has native Ollama support
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.1:8b", temperature=0.3)
response = llm.invoke("Analyze the legal tech market")
```

### 5.5 CrewAI + Ollama

```python
# CrewAI supports Ollama natively via environment variables:
import os
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "ollama"
os.environ["OPENAI_MODEL_NAME"] = "llama3.1:8b"
```

### 5.6 AutoGen + Ollama

```python
# AutoGen uses OAI_CONFIG_LIST for model configuration:
config_list = [
    {
        "model": "llama3.1:8b",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
    }
]
```

---

## 6. Code Changes Required

### 6.1 NEW: `src/llm/ollama_client.py` (~200 LOC)

**Purpose:** Local LLM client using Ollama's API. Mirrors the pattern of `openai_client.py` but hits `localhost:11434`.

```python
"""
Gen-AI Tool: Local LLM (Ollama)
=================================
Demonstrates: Local LLM inference via Ollama, OpenAI-compatible API,
model selection per task, streaming, and function calling with LLaMA.

Role in GenAI Nexus: Run the ENTIRE pipeline locally — zero cloud API
calls, zero API keys, zero cost. Uses LLaMA 3 models via Ollama.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Generator

@dataclass
class OllamaConfig:
    base_url: str = "http://localhost:11434"
    default_model: str = "llama3.1:8b"
    code_model: str = "codellama:7b"
    fast_model: str = "llama3.2:3b"
    embedding_model: str = "nomic-embed-text"
    temperature: float = 0.3
    max_tokens: int = 2048
    timeout: int = 120


@dataclass
class OllamaResponse:
    content: str
    model: str
    tokens_used: int = 0


class OllamaClient:
    """
    Local LLM client via Ollama.
    Uses OpenAI-compatible API (localhost:11434/v1).
    """

    def __init__(self, config: OllamaConfig | None = None):
        self.config = config or OllamaConfig()
        self._available = False
        self._client = None

        try:
            from openai import OpenAI
            self._client = OpenAI(
                base_url=f"{self.config.base_url}/v1",
                api_key="ollama",
                timeout=self.config.timeout,
            )
            # Quick health check
            self._client.models.list()
            self._available = True
        except Exception:
            pass  # Ollama not running — fall back to demo

    @property
    def is_available(self) -> bool:
        return self._available

    def analyze_market(self, startup_idea: str) -> OllamaResponse:
        """Market research using local LLaMA."""
        return self._chat(
            model=self.config.default_model,
            system="You are a startup market analyst. Provide TAM/SAM/SOM analysis.",
            user=f"Analyze the market for: {startup_idea}",
        )

    def analyze_competitors(self, startup_idea: str) -> OllamaResponse:
        """Competitive analysis using local LLaMA."""
        return self._chat(
            model=self.config.default_model,
            system="You are a competitive intelligence analyst.",
            user=f"Analyze competitors for: {startup_idea}",
        )

    def generate_code(self, startup_idea: str, tech_stack: list[str] | None = None) -> OllamaResponse:
        """MVP code skeleton using CodeLlama."""
        stack = ", ".join(tech_stack or ["Python", "FastAPI"])
        return self._chat(
            model=self.config.code_model,
            system="You are an expert software architect. Generate MVP code.",
            user=f"Generate code skeleton for: {startup_idea}\nTech stack: {stack}",
        )

    def generate_pitch(self, startup_idea: str, market_data: dict | None = None) -> OllamaResponse:
        """Pitch content using fast model."""
        return self._chat(
            model=self.config.fast_model,
            system="You are a startup pitch expert.",
            user=f"Create a 30-second elevator pitch for: {startup_idea}",
        )

    def stream(self, prompt: str, model: str | None = None) -> Generator[str, None, None]:
        """Streaming generation."""
        if not self._available:
            for word in f"[Demo local] Response for: {prompt[:50]}".split():
                yield word + " "
            return

        response = self._client.chat.completions.create(
            model=model or self.config.default_model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _chat(self, model: str, system: str, user: str) -> OllamaResponse:
        """Core chat completion call."""
        if not self._available:
            return OllamaResponse(
                content=f"[Demo local — Ollama not running] Would use {model} for: {user[:80]}",
                model="demo",
            )

        response = self._client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        return OllamaResponse(
            content=response.choices[0].message.content,
            model=model,
            tokens_used=response.usage.total_tokens if response.usage else 0,
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Local embeddings via Ollama's nomic-embed-text."""
        if not self._available:
            import hashlib, math, random
            results = []
            for text in texts:
                seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
                rng = random.Random(seed)
                raw = [rng.gauss(0, 1) for _ in range(768)]
                mag = math.sqrt(sum(x * x for x in raw))
                results.append([x / mag for x in raw])
            return results

        import requests
        results = []
        for text in texts:
            resp = requests.post(
                f"{self.config.base_url}/api/embeddings",
                json={"model": self.config.embedding_model, "prompt": text},
            )
            results.append(resp.json()["embedding"])
        return results


def demo():
    print("=" * 60)
    print("DEMO: Local LLM via Ollama")
    print("=" * 60)
    client = OllamaClient()

    if client.is_available:
        print(f"✅ Ollama is running at {client.config.base_url}")
    else:
        print("⚠️  Ollama not running — using demo mode")
        print("   Install: brew install ollama && ollama serve")

    print("\n[1] Market Analysis (local LLaMA)")
    result = client.analyze_market("AI-powered legal document analyzer")
    print(f"  Model: {result.model}")
    print(f"  Response: {result.content[:200]}...")

    print("\n[2] Code Generation (CodeLlama)")
    code = client.generate_code("AI legal analyzer", ["Python", "FastAPI"])
    print(f"  Model: {code.model}")
    print(f"  Response: {code.content[:200]}...")

    print("\n[3] Streaming")
    print("  ", end="")
    for token in client.stream("Explain RAG in one sentence"):
        print(token, end="", flush=True)
    print()


if __name__ == "__main__":
    demo()
```

### 6.2 MODIFY: `config/settings.py` — Add Ollama config

```python
# Add these fields to the Settings class:

    # --- Local LLM (Ollama) ---
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.1:8b", alias="OLLAMA_MODEL")
    ollama_code_model: str = Field(default="codellama:7b", alias="OLLAMA_CODE_MODEL")
    ollama_fast_model: str = Field(default="llama3.2:3b", alias="OLLAMA_FAST_MODEL")
    ollama_embed_model: str = Field(default="nomic-embed-text", alias="OLLAMA_EMBED_MODEL")
    use_local_llm: bool = Field(default=False, alias="USE_LOCAL_LLM")

    @property
    def has_local_llm(self) -> bool:
        """Check if Ollama is configured for local LLM."""
        return self.use_local_llm
```

### 6.3 MODIFY: `src/llm/llm_router.py` — Add local route

```python
# Add to _ROUTING_TABLE logic:
# When USE_LOCAL_LLM=true, ALL tasks route to Ollama client

class LLMRouter:
    def __init__(self):
        # ... existing init ...
        self._ollama = None  # NEW
        if settings.use_local_llm:
            from src.llm.ollama_client import OllamaClient
            self._ollama = OllamaClient()

    def route(self, task: TaskType, payload: dict) -> RouterResult:
        # NEW: local override
        if self._ollama and self._ollama.is_available:
            return self._route_local(task, payload)
        # ... existing routing logic ...

    def _route_local(self, task: TaskType, payload: dict) -> RouterResult:
        idea = payload.get("startup_idea", "startup")
        if task == TaskType.CODE_GENERATION:
            r = self._ollama.generate_code(idea)
        elif task == TaskType.FAST_SUMMARY:
            r = self._ollama.generate_pitch(idea)
        else:
            r = self._ollama.analyze_market(idea)
        return RouterResult(content=r.content, model_used=r.model, task_type=task)
```

### 6.4 MODIFY: `src/chains/analysis_chains.py` — Use ChatOllama

```python
# In AnalysisChains.__init__(), change:

    def __init__(self):
        self._demo = True
        self._llm = None
        try:
            if settings.use_local_llm:
                from langchain_ollama import ChatOllama
                self._llm = ChatOllama(model=settings.ollama_model, temperature=0.3)
                self._demo = False
            elif settings.has_openai:
                from langchain_openai import ChatOpenAI
                self._llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
                self._demo = False
        except ImportError:
            pass
```

### 6.5 MODIFY: `src/agents/crew_team.py` — Ollama config for CrewAI

```python
# In StartupCrew.__init__(), add:

    if settings.use_local_llm:
        import os
        os.environ["OPENAI_API_BASE"] = f"{settings.ollama_base_url}/v1"
        os.environ["OPENAI_API_KEY"] = "ollama"
        os.environ["OPENAI_MODEL_NAME"] = settings.ollama_model
```

### 6.6 MODIFY: `src/agents/autogen_debate.py` — Ollama config for AutoGen

```python
# In StartupDebate.__init__(), add config_list:

    if settings.use_local_llm:
        self._config_list = [{
            "model": settings.ollama_model,
            "base_url": f"{settings.ollama_base_url}/v1",
            "api_key": "ollama",
        }]
```

### 6.7 MODIFY: `.env.example` — Add local LLM variables

```dotenv
# --- Local LLM (Ollama) ---
USE_LOCAL_LLM=true                      # Set to true for fully local execution
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_CODE_MODEL=codellama:7b
OLLAMA_FAST_MODEL=llama3.2:3b
OLLAMA_EMBED_MODEL=nomic-embed-text
EMBEDDING_MODEL=huggingface             # Use local embeddings (not OpenAI)
DEMO_MODE=false                         # Disable demo since we have local LLM
```

### 6.8 MODIFY: `main.py` — Add `--local` flag

```python
# Add to argparse:
parser.add_argument(
    "--local", action="store_true",
    help="Force local LLM mode (Ollama). Overrides .env settings.",
)

# In main(), after parsing:
if args.local:
    import os
    os.environ["USE_LOCAL_LLM"] = "true"
    os.environ["DEMO_MODE"] = "false"
    os.environ["EMBEDDING_MODEL"] = "huggingface"
```

---

## 7. Dependency Resolution Strategy

### 7.1 Core Dependencies (Always Needed)

```
pip install openai pydantic-settings python-dotenv streamlit chromadb
```

These are lightweight and work everywhere. `openai` SDK is reused for Ollama's OpenAI-compatible endpoint.

### 7.2 LangChain + Ollama Integration

```
pip install langchain langchain-community langchain-ollama langgraph
```

**Critical:** `langchain-ollama` is the official LangChain package for Ollama integration.

### 7.3 Agent Frameworks

```
pip install crewai pyautogen
```

Both support custom LLM endpoints. CrewAI uses `OPENAI_API_BASE` env var. AutoGen uses `config_list`.

### 7.4 HuggingFace / ML Stack (Local Training)

```
pip install transformers datasets accelerate sentence-transformers
pip install torch keras tensorflow        # Heavy — order matters
pip install peft trl bitsandbytes         # For PEFT/LoRA
```

**Note on PyTorch vs TensorFlow:**
- Keras needs exactly one backend: `tensorflow` OR `torch` (not both)
- For macOS Apple Silicon: `torch` with MPS backend is better
- Set `KERAS_BACKEND=torch` if using PyTorch

### 7.5 Optional (Heavy, Skip Unless Needed)

```
# vLLM — only on Linux with NVIDIA GPU
# pip install vllm

# DeepSpeed — only for distributed training
# pip install deepspeed

# spaCy model — only if you want NER (not regex fallback)
python -m spacy download en_core_web_sm
```

### 7.6 Full Local requirements-local.txt

```
# === LOCAL EXECUTION REQUIREMENTS ===
# Minimal set for full local end-to-end run

# Core
openai>=1.0                   # Also used for Ollama OpenAI-compat
pydantic-settings>=2.0
python-dotenv>=1.0
streamlit>=1.33
requests>=2.31

# Vector DB + Embeddings
chromadb>=0.4
sentence-transformers>=2.7

# LangChain + Ollama
langchain>=0.2
langchain-community>=0.2
langchain-ollama>=0.1
langgraph>=0.1

# Agents
crewai>=0.30
pyautogen>=0.2

# NLP
spacy>=3.7
nltk>=3.8

# HuggingFace
transformers>=4.40
datasets>=2.18
accelerate>=0.29

# ML Training (optional but enables full mode)
torch>=2.2
keras>=3.0
peft>=0.10
trl>=0.8
bitsandbytes>=0.43

# Safety
guardrails-ai>=0.4

# LlamaIndex
llama-index>=0.10
```

### 7.7 Dependency Conflicts to Watch

| Conflict                         | Root Cause                                       | Fix                                             |
| -------------------------------- | ------------------------------------------------ | ----------------------------------------------- |
| `keras` + `torch` + `tensorflow` | Keras 3 needs one backend, not both              | Set `KERAS_BACKEND=torch` and skip `tensorflow` |
| `bitsandbytes` on macOS          | Natively supports Linux CUDA only                | Skip on macOS — quantization runs in demo mode  |
| `vllm` on macOS                  | Linux + NVIDIA only                              | Skip — use Ollama for local serving instead     |
| `pyautogen` version conflict     | `pyautogen>=0.2` can conflict with `openai>=1.0` | Pin `pyautogen==0.2.35`                         |
| `crewai` + `langchain` versions  | CrewAI pins specific LangChain range             | Install CrewAI first, then LangChain            |

---

## 8. Execution Modes: Local-Only Configuration

### 8.1 Mode A: Demo (Zero Dependencies Beyond pip install)

```bash
# .env
DEMO_MODE=true
USE_LOCAL_LLM=false

# Run
python main.py --idea "AI legal analyzer" --mode demo
```

- **LLM:** Mock responses (no Ollama needed)
- **Embeddings:** Deterministic fake (MD5-based)
- **Training:** Simulated epochs with fake metrics
- **Good for:** Quick walkthrough, understanding the pipeline

### 8.2 Mode B: Local LLM (Ollama — Recommended)

```bash
# .env
DEMO_MODE=false
USE_LOCAL_LLM=true
EMBEDDING_MODEL=huggingface

# Prerequisites
ollama serve &
ollama pull llama3.1:8b
ollama pull codellama:7b
ollama pull nomic-embed-text

# Run
python main.py --idea "AI legal analyzer" --mode quick --local
```

- **LLM:** Local LLaMA via Ollama (real responses, zero API cost)
- **Embeddings:** Local HuggingFace `all-MiniLM-L6-v2`
- **Training:** Real Keras/DistilBERT training on CPU (or MPS on Mac)
- **Good for:** Full learning experience, real AI outputs, no budget

### 8.3 Mode C: Full Local (Everything Including Training)

```bash
# .env
DEMO_MODE=false
USE_LOCAL_LLM=true
EMBEDDING_MODEL=huggingface
PEFT_BASE_MODEL=/path/to/local/llama-3.2-1b  # Local model for PEFT

# Run
python main.py --idea "AI legal analyzer" --mode full --local
```

- **LLM:** Ollama for inference, local model for fine-tuning
- **Training:** PEFT/LoRA on local LLaMA weights (requires ~8GB RAM)
- **Good for:** Understanding the complete ML lifecycle locally

---

## 9. Hardware Requirements & Performance

### 9.1 Minimum Hardware

| Component | Demo Mode  | Quick + Local LLM   | Full + Training        |
| --------- | ---------- | ------------------- | ---------------------- |
| **RAM**   | 4 GB       | 16 GB               | 32 GB                  |
| **Disk**  | 2 GB       | 15 GB               | 25 GB                  |
| **GPU**   | Not needed | Not needed (CPU OK) | Recommended (MPS/CUDA) |
| **CPU**   | Any        | 4+ cores            | 8+ cores               |

### 9.2 Disk Space Breakdown

| Item                        | Size       | When Downloaded                         |
| --------------------------- | ---------- | --------------------------------------- |
| Python packages (pip)       | ~3 GB      | `pip install -r requirements-local.txt` |
| `llama3.1:8b` (Ollama)      | 4.7 GB     | `ollama pull llama3.1:8b`               |
| `llama3.2:3b` (Ollama)      | 2.0 GB     | `ollama pull llama3.2:3b`               |
| `codellama:7b` (Ollama)     | 3.8 GB     | `ollama pull codellama:7b`              |
| `nomic-embed-text` (Ollama) | 274 MB     | `ollama pull nomic-embed-text`          |
| HuggingFace models (cached) | ~1.5 GB    | Auto-download on first use              |
| ChromaDB data               | ~50 MB     | Generated during run                    |
| **Total**                   | **~15 GB** |                                         |

### 9.3 Performance Expectations (Local LLM)

| Task                                  | Apple M1/M2 (8GB) | Apple M2 Pro (16GB) | NVIDIA RTX 3090 |
| ------------------------------------- | ----------------- | ------------------- | --------------- |
| Market analysis (llama3.1:8b)         | ~15-25 sec        | ~8-12 sec           | ~3-5 sec        |
| Code generation (codellama:7b)        | ~12-20 sec        | ~6-10 sec           | ~2-4 sec        |
| Quick summary (llama3.2:3b)           | ~5-10 sec         | ~3-5 sec            | ~1-2 sec        |
| Embedding (nomic-embed-text)          | ~0.5 sec          | ~0.2 sec            | ~0.1 sec        |
| Full pipeline (quick mode)            | ~3-5 min          | ~2-3 min            | ~1-2 min        |
| Full pipeline (full mode w/ training) | ~20-30 min        | ~10-15 min          | ~5-8 min        |
| Keras LSTM training (5 epochs)        | ~30 sec           | ~15 sec             | ~5 sec          |
| DistilBERT fine-tune (3 epochs)       | ~2 min            | ~1 min              | ~20 sec         |

### 9.4 macOS Apple Silicon Optimizations

```bash
# PyTorch MPS (Metal Performance Shaders) — auto-detected
# Verify:
python -c "import torch; print(torch.backends.mps.is_available())"

# Keras backend — use PyTorch for MPS support
export KERAS_BACKEND=torch

# Ollama — auto-detects Metal, no config needed
ollama run llama3.1:8b "test"  # Should use Metal GPU
```

---

## 10. End-to-End Run Playbook

### Step-by-step local execution (after one-time setup):

```bash
# ── 1. Terminal 1: Start Ollama ─────────────────────────
ollama serve
# Keep running in background

# ── 2. Terminal 2: Run GenAI Nexus ──────────────────────
cd 14-TechStack/Gen-AI/Projects/06-GenAI-Nexus

# Create local .env
cat > .env << 'EOF'
DEMO_MODE=false
USE_LOCAL_LLM=true
EMBEDDING_MODEL=huggingface
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_CODE_MODEL=codellama:7b
OLLAMA_FAST_MODEL=llama3.2:3b
OLLAMA_EMBED_MODEL=nomic-embed-text
KERAS_BACKEND=torch
LOG_LEVEL=INFO
EOF

# Run the full pipeline
python main.py --idea "AI-powered legal document analyzer" --mode quick --local

# Or run individual modules
python main.py --demo-individual ollama    # Test Ollama client
python main.py --demo-individual rag       # Test RAG with local LLM
python main.py --demo-individual crew      # Test CrewAI with local LLM
python main.py --demo-individual hf        # Test HuggingFace locally

# Or launch the web UI
streamlit run app.py

# ── 3. Run Tests ────────────────────────────────────────
python -m pytest tests/ -v
```

### Expected Pipeline Output

```
╔══════════════════════════════════════════════════════════╗
║          GenAI Nexus — AI Startup Advisor                ║
║          26 Gen-AI Tools • One Complete Analysis         ║
╚══════════════════════════════════════════════════════════╝

► Stage 1: LangGraph Stateful Workflow
  ✓ NLP preprocessing (local)
  ✓ Advanced RAG retrieval (local ChromaDB + HuggingFace embeddings)
  ✓ LangChain analysis (local LLaMA via Ollama)
  ✓ CrewAI team planning (local LLaMA via Ollama)
  ✓ AutoGen debate (local LLaMA via Ollama)
  ✓ Guardrails validation (local rules)

► Stage 2: LLM Router (→ Ollama llama3.1:8b)
  ✓ Pitch content generated via llama3.2:3b

► Stage 3: AgenticAI — Code Generation
  ✓ Code skeleton generated via codellama:7b

► Stage 4: HuggingFace — Sentiment
  ✓ Market sentiment: BULLISH

► Stages 5-7: Training (quick mode skips or runs locally)
  ✓ Keras LSTM: 5 epochs, acc=0.85 (CPU)
  ✓ DistilBERT fine-tune: 3 epochs, acc=0.78 (CPU)
  ✓ PEFT/LoRA: demo mode (no local LLaMA weights)

════════════════════════════════════════════════════════════
✅ Analysis complete in 185.3s
   Tools used: 24
   Validation: ✅ PASSED
════════════════════════════════════════════════════════════
```

---

## 11. Known Limitations & Workarounds

### 11.1 Quality vs Cloud APIs

| Aspect              | Local LLaMA 8B |   GPT-4o-mini   | Claude 3 Haiku  |
| ------------------- | :------------: | :-------------: | :-------------: |
| Reasoning depth     |      6/10      |      8/10       |      8/10       |
| Code generation     |      7/10      |      8/10       |      9/10       |
| Structured output   |      5/10      |      9/10       |      8/10       |
| Function calling    |      6/10      |      9/10       |      8/10       |
| Speed (first token) |    2-5 sec     |     0.3 sec     |     0.5 sec     |
| Cost                |       ₹0       | ~₹3/1K requests | ~₹2/1K requests |
| Privacy             |   100% local   |      Cloud      |      Cloud      |

**Workaround for quality gap:** Use larger Ollama models: `llama3.1:70b` (40GB) or `mixtral:8x7b` (26GB) if you have the RAM.

### 11.2 Modules That Always Run in Demo Mode Locally

| Module              | Reason                              | Impact                               |
| ------------------- | ----------------------------------- | ------------------------------------ |
| AWS Client          | Requires AWS credentials + services | Low — cloud deployment is final step |
| vLLM Server         | Linux + NVIDIA GPU only             | Low — Ollama replaces this locally   |
| Distributed Trainer | Requires multi-GPU cluster          | None — educational demo only         |

### 11.3 macOS-Specific Issues

| Issue                               | Symptom                                             | Fix                                                                    |
| ----------------------------------- | --------------------------------------------------- | ---------------------------------------------------------------------- |
| `bitsandbytes` fails to install     | Compilation errors on macOS                         | `pip install bitsandbytes` — recent versions support macOS, or skip it |
| `torch.cuda.is_available()` = False | No NVIDIA GPU on Mac                                | Expected — use `torch.backends.mps.is_available()`                     |
| Keras picks wrong backend           | `ModuleNotFoundError: No module named 'tensorflow'` | `export KERAS_BACKEND=torch`                                           |
| Ollama slow on first request        | Model loading from disk (~10 sec)                   | Normal — subsequent requests are fast (model stays in memory)          |
| ChromaDB SQLite version error       | macOS ships old SQLite                              | `pip install pysqlite3-binary` and add shim                            |

### 11.4 Function Calling / Tool-Use Caveats

LLaMA 3.1+ supports function calling, but it's less reliable than GPT-4:
- **OpenAI client** function calling (`generate_business_plan`) may produce imperfect JSON
- **ReAct agent** tool parsing needs more robust regex for LLaMA outputs
- **Workaround:** Use the structured output prompt pattern instead of function calling API

---

## 12. Testing Strategy

### 12.1 Test Categories

| Category               | What                      | Requires                   |
| ---------------------- | ------------------------- | -------------------------- |
| **Unit tests (demo)**  | All 66+ tests             | Nothing (demo mocks)       |
| **Unit tests (local)** | Same tests with local LLM | Ollama running             |
| **Integration tests**  | Full pipeline end-to-end  | Ollama + all models pulled |
| **Smoke test**         | One quick pipeline run    | Ollama + `llama3.2:3b`     |

### 12.2 Running Tests

```bash
# Demo mode (no deps)
python -m pytest tests/ -v

# Local LLM mode (Ollama must be running)
USE_LOCAL_LLM=true python -m pytest tests/ -v

# Quick smoke test
USE_LOCAL_LLM=true python main.py --idea "test" --mode demo --local

# Test Ollama specifically
python -c "from src.llm.ollama_client import demo; demo()"
```

### 12.3 Health Check Script

```bash
#!/bin/bash
# health_check.sh — Verify all local dependencies
echo "=== GenAI Nexus Local Health Check ==="

# Python
python3 --version || echo "❌ Python not found"

# Ollama
curl -s http://localhost:11434/api/tags > /dev/null && echo "✅ Ollama running" || echo "❌ Ollama not running"

# Models
for model in llama3.1:8b codellama:7b llama3.2:3b nomic-embed-text; do
  ollama list | grep -q "$model" && echo "✅ $model" || echo "❌ $model not pulled"
done

# Python packages
python3 -c "import openai" 2>/dev/null && echo "✅ openai" || echo "❌ openai"
python3 -c "import langchain_ollama" 2>/dev/null && echo "✅ langchain-ollama" || echo "❌ langchain-ollama"
python3 -c "import chromadb" 2>/dev/null && echo "✅ chromadb" || echo "❌ chromadb"
python3 -c "import torch" 2>/dev/null && echo "✅ torch" || echo "❌ torch"
python3 -c "import transformers" 2>/dev/null && echo "✅ transformers" || echo "❌ transformers"
python3 -c "import crewai" 2>/dev/null && echo "✅ crewai" || echo "❌ crewai"
python3 -c "import streamlit" 2>/dev/null && echo "✅ streamlit" || echo "❌ streamlit"

# Disk space
echo ""
echo "Disk usage:"
du -sh ~/.ollama/models 2>/dev/null || echo "No Ollama models found"
du -sh ~/.cache/huggingface 2>/dev/null || echo "No HuggingFace cache found"
```

---

## Summary: What You Get

| Execution            |     Demo     |      Local LLM (Quick)       | Local LLM (Full) |
| -------------------- | :----------: | :--------------------------: | :--------------: |
| NLP preprocessing    |    ✅ mock    |         ✅ real spaCy         |   ✅ real spaCy   |
| Embeddings           |    ✅ fake    |          ✅ local HF          |    ✅ local HF    |
| Vector store         |  ✅ keyword   |          ✅ ChromaDB          |    ✅ ChromaDB    |
| RAG pipeline         |    ✅ mock    | ✅ real retrieval + local LLM |      ✅ real      |
| LangChain chains     |    ✅ mock    |         ✅ ChatOllama         |   ✅ ChatOllama   |
| LangGraph workflow   |    ✅ mock    |      ✅ real state graph      |      ✅ real      |
| LLM calls            |    ✅ mock    |        ✅ local LLaMA         |  ✅ local LLaMA   |
| CrewAI agents        |    ✅ mock    |        ✅ local LLaMA         |  ✅ local LLaMA   |
| AutoGen debate       |    ✅ mock    |        ✅ local LLaMA         |  ✅ local LLaMA   |
| ReAct agent          |    ✅ mock    |        ✅ local LLaMA         |  ✅ local LLaMA   |
| Guardrails           |    ✅ real    |            ✅ real            |      ✅ real      |
| HuggingFace          |    ✅ mock    |    ✅ real (local models)     |      ✅ real      |
| Keras training       | ✅ simulated  |          ✅ real CPU          |  ✅ real CPU/GPU  |
| Transfer Learning    | ✅ simulated  |          ✅ real CPU          |  ✅ real CPU/GPU  |
| PEFT/LoRA            | ✅ simulated  |         ✅ simulated          |   ✅ real local   |
| RLHF                 | ✅ simulated  |      ✅ real (heuristic)      |      ✅ real      |
| Quantization         | ✅ benchmarks |         ✅ benchmarks         | ✅ real (if GPU)  |
| vLLM serving         |    ✅ mock    |         ⚫ use Ollama         |   ⚫ use Ollama   |
| AWS services         |    ✅ mock    |            ⚫ skip            |      ⚫ skip      |
| **API cost**         |    **₹0**    |            **₹0**            |      **₹0**      |
| **Cloud dependency** |   **None**   |           **None**           |     **None**     |
