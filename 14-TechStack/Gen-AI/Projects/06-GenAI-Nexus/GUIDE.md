# GenAI Nexus — Comprehensive Project Guide

**Version:** 1.0 | **Last Updated:** 2026-03-06

> **One project. 27 Gen-AI tools. One unified startup advisor pipeline. Runs fully local with Ollama.**

GenAI Nexus is a hands-on educational project that integrates **every major Gen-AI tool category** into a single cohesive application — an AI Startup Advisor that analyzes a business idea through 26 different AI/ML techniques and produces a complete startup plan.

---

## Table of Contents

1. [What Is GenAI Nexus?](#1-what-is-genai-nexus)
2. [Architecture Overview](#2-architecture-overview)
3. [The 27 Gen-AI Tools (Complete Map)](#3-the-27-gen-ai-tools-complete-map)
4. [Project Structure](#4-project-structure)
5. [Installation & Setup](#5-installation--setup)
6. [Running the Application](#6-running-the-application)
7. [Module Deep Dives](#7-module-deep-dives)
   - [7.1 LLM Clients (OpenAI, Claude, Gemini)](#71-llm-clients)
   - [7.2 LLM Router](#72-llm-router)
   - [7.3 NLP Text Processor](#73-nlp-text-processor)
   - [7.4 Embeddings & Vector Store](#74-embeddings--vector-store)
   - [7.5 RAG Pipeline (Basic → Advanced → LlamaIndex)](#75-rag-pipeline)
   - [7.6 LangChain Analysis Chains](#76-langchain-analysis-chains)
   - [7.7 LangGraph Stateful Workflow](#77-langgraph-stateful-workflow)
   - [7.8 Agents (ReAct, CrewAI, AutoGen)](#78-agents)
   - [7.9 Prompt Engineering & Few-Shot](#79-prompt-engineering--few-shot)
   - [7.10 Safety & Guardrails](#710-safety--guardrails)
   - [7.11 HuggingFace Models](#711-huggingface-models)
   - [7.12 Custom Models (Keras & Transfer Learning)](#712-custom-models)
   - [7.13 Training (PEFT/LoRA, RLHF, Distributed)](#713-training)
   - [7.14 Optimization (Quantization & vLLM)](#714-optimization)
   - [7.15 Cloud Deployment (AWS SageMaker + Bedrock)](#715-cloud-deployment)
8. [Pipeline Orchestration](#8-pipeline-orchestration)
9. [Knowledge Base & Data](#9-knowledge-base--data)
10. [Testing](#10-testing)
11. [Key Design Patterns](#11-key-design-patterns)
12. [Learning Path (Beginner → Advanced)](#12-learning-path)
13. [Extending the Project](#13-extending-the-project)

---

## 1. What Is GenAI Nexus?

**Problem:** Learning 26+ Gen-AI tools in isolation lacks context and integration understanding.

**Solution:** GenAI Nexus builds a *real* application — an **AI Startup Advisor** — that uses every tool with purpose:

| Input                                  | Pipeline                         | Output                                                                                                                                                                         |
| -------------------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `"AI-powered legal document analyzer"` | 27 Gen-AI tools working together | Complete startup plan (market research, competitive analysis, technical architecture, team plan, stress test, pitch deck, code skeleton, sentiment analysis, validated output) |

**Key features:**
- **4 execution modes:** `demo` (no API keys), `local` (Ollama, zero cost), `quick` (API keys, skip training), `full` (all 27 tools)
- **2 entry points:** CLI (`main.py`) and Web UI (`app.py` via Streamlit)
- **Fully modular:** Every module works standalone with its own `demo()` function
- **Graceful degradation:** Missing libraries or API keys → automatic demo/fallback mode

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       ENTRY POINTS                               │
│  main.py (CLI)     app.py (Streamlit Web UI)                    │
└──────────┬──────────────────┬────────────────────────────────────┘
           │                  │
           ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              PIPELINE ORCHESTRATOR                                │
│  pipeline/startup_advisor.py                                     │
│  StartupAdvisor.run(mode="demo"|"quick"|"full")                 │
└──────────┬──────────────────────────────────────────────────────┘
           │
    ┌──────┴──────────────────────────────────────────────┐
    │                                                      │
    ▼                                                      ▼
┌────────────────────┐                      ┌─────────────────────┐
│  STAGE 1            │                      │  STAGE 2-4           │
│  LangGraph Workflow │                      │  LLM Router          │
│  (7-node graph)     │                      │  AgenticAI           │
│                     │                      │  HuggingFace         │
│  ┌───────────┐      │                      └─────────────────────┘
│  │Preprocess │──┐   │                                │
│  │(NLP)      │  │   │                      ┌─────────┴───────────┐
│  └───────────┘  │   │                      │  STAGE 5-8 (full)    │
│  ┌───────────┐  │   │                      │  Keras Training      │
│  │Research   │──┤   │                      │  Transfer Learning   │
│  │(AdvRAG)   │  │   │                      │  PEFT/LoRA           │
│  └───────────┘  │   │                      │  Quantization        │
│  ┌───────────┐  │   │                      │  vLLM Serving        │
│  │Analyze    │──┤   │                      │  AWS Deployment      │
│  │(LangChain)│  │   │                      └─────────────────────┘
│  └───────────┘  │   │
│  ┌───────────┐  │   │
│  │Team Plan  │──┤   │
│  │(CrewAI)   │  │   │
│  └───────────┘  │   │
│  ┌───────────┐  │   │
│  │Debate     │──┤   │
│  │(AutoGen)  │  │   │
│  └───────────┘  │   │
│  ┌───────────┐  │   │
│  │Validate   │──┤   │
│  │(Guardrails│  │   │
│  └───────────┘  │   │
│  ┌───────────┐  │   │
│  │Output     │──┘   │
│  │(Report)   │      │
│  └───────────┘      │
└─────────────────────┘

                    ┌──────────────────────────┐
                    │  SHARED INFRASTRUCTURE    │
                    │  • Embeddings Service     │
                    │  • ChromaDB Vector Store  │
                    │  • Prompt Templates       │
                    │  • Few-Shot Examples      │
                    │  • Knowledge Base (data/) │
                    │  • Config (settings.py)   │
                    └──────────────────────────┘
```

### Data Flow Summary

```
User Input (startup idea)
    │
    ├── NLP preprocessing → cleaned text, keywords, entities, startup components
    ├── Advanced RAG → knowledge base retrieval (HyDE + hybrid search + reranking)
    ├── LangChain LCEL → 4-stage sequential analysis (market → competitive → technical → report)
    ├── CrewAI → 4-agent C-suite team (CEO, CTO, CMO, CFO) generate role-specific plans
    ├── AutoGen → 3-agent debate (Optimist vs Skeptic → Mediator synthesizes)
    ├── Guardrails → hallucination detection, content safety, schema validation
    ├── LLM Router → routes tasks to best LLM (OpenAI/Claude/Gemini)
    ├── ReAct Agent → autonomous code generation with tool use
    ├── HuggingFace → market sentiment scoring from news headlines
    ├── [full mode] Keras → domain-specific LSTM sentiment model
    ├── [full mode] Transfer Learning → DistilBERT fine-tuned on legal domain
    ├── [full mode] PEFT/LoRA → fine-tune LLaMA on startup advisory Q&A
    ├── [full mode] RLHF → human feedback collection + reward scoring
    ├── [full mode] Quantization → INT8/INT4/GGUF model compression
    ├── [full mode] vLLM → high-throughput inference serving
    ├── [full mode] AWS → SageMaker deployment + Bedrock fallback
    │
    ▼
StartupPlan (market research + competitive analysis + technical plan
             + team plans + debate outcome + pitch content + code skeleton
             + sentiment score + validation status)
    │
    ▼
Output: Markdown report (startup_plan.md)
```

---

## 3. The 27 Gen-AI Tools (Complete Map)

| #   | Tool Category          | Source File                            | What It Does in GenAI Nexus                                                         |
| --- | ---------------------- | -------------------------------------- | ----------------------------------------------------------------------------------- |
| 1   | **OpenAI GPT**         | `src/llm/openai_client.py`             | Market research, business plan generation, function calling                         |
| 2   | **Claude (Anthropic)** | `src/llm/claude_client.py`             | Competitive analysis (long-context), code skeleton, multi-turn advisory             |
| 3   | **Gemini (Google)**    | `src/llm/gemini_client.py`             | Multimodal analysis, structured JSON output, pitch deck content                     |
| 4   | **Ollama (Local LLM)** | `src/llm/ollama_client.py`             | Run entire pipeline locally via LLaMA/Mistral/Qwen — zero API cost                  |
| 5   | **LLM Routing**        | `src/llm/llm_router.py`                | Routes tasks to optimal LLM (local-first when `--local` flag)                       |
| 6   | **NLP/spaCy**          | `src/nlp/text_processor.py`            | Text cleaning, tokenization, NER, keyword extraction, startup component extraction  |
| 7   | **Embeddings**         | `src/embeddings/embedding_service.py`  | OpenAI + HuggingFace embeddings, semantic search, cosine similarity, caching        |
| 8   | **Vector Database**    | `src/vectorstore/chroma_store.py`      | ChromaDB for knowledge base storage, metadata-filtered search                       |
| 9   | **Basic RAG**          | `src/rag/basic_rag.py`                 | Retrieve-Augment-Generate pipeline with chunking                                    |
| 10  | **Advanced RAG**       | `src/rag/advanced_rag.py`              | HyDE, hybrid search (0.7 semantic + 0.3 BM25), cross-encoder reranking, multi-hop   |
| 11  | **LlamaIndex**         | `src/rag/llama_indexer.py`             | Alternative indexing with startup case studies and market reports                   |
| 12  | **LangChain (LCEL)**   | `src/chains/analysis_chains.py`        | 4-stage sequential chain (Market → Competitive → Technical → Report)                |
| 13  | **LangGraph**          | `src/graph/startup_workflow.py`        | 7-node stateful workflow with conditional edges, error recovery                     |
| 14  | **Agentic AI (ReAct)** | `src/agents/agentic_core.py`           | Autonomous agent with 4 tools, Thought→Action→Observation loop                      |
| 15  | **CrewAI**             | `src/agents/crew_team.py`              | 4-agent C-suite team (CEO, CTO, CMO, CFO) with sequential task execution            |
| 16  | **AutoGen**            | `src/agents/autogen_debate.py`         | 3-agent debate (Optimist, Skeptic, Mediator) for stress testing                     |
| 17  | **Guardrails AI**      | `src/safety/output_validator.py`       | Hallucination detection, content safety, schema validation, auto-correction         |
| 18  | **Prompt Engineering** | `src/prompts/prompt_templates.py`      | CoT prompts, persona prompts, ReAct prompt, XML-tagged outputs                      |
| 19  | **Few-Shot Learning**  | `src/prompts/few_shot_examples.py`     | Market sizing examples, competitive moat examples, self-consistency prompting       |
| 20  | **HuggingFace**        | `src/huggingface/hf_models.py`         | Sentiment analysis, NER, zero-shot classification, summarization                    |
| 21  | **Keras**              | `src/models/sentiment_model.py`        | Custom bidirectional LSTM for legal tech sentiment classification                   |
| 22  | **Transfer Learning**  | `src/models/transfer_adapter.py`       | DistilBERT fine-tuning for legal domain classification (5 categories)               |
| 23  | **PEFT/LoRA**          | `src/training/peft_trainer.py`         | Parameter-efficient fine-tuning on startup advisory Q&A (0.1% trainable params)     |
| 24  | **RLHF**               | `src/training/rlhf_feedback.py`        | Human feedback collection, reward scoring, DPO dataset preparation                  |
| 25  | **Model Quantization** | `src/optimization/quantizer.py`        | INT8/INT4/GGUF quantization with benchmarks and recommendations                     |
| 26  | **vLLM**               | `src/optimization/inference_server.py` | PagedAttention inference server, streaming, batch generation, OpenAI-compatible API |
| 27  | **AWS AI/ML**          | `src/cloud/aws_client.py`              | SageMaker endpoint deployment, Bedrock Claude API, Comprehend, Textract             |

---

## 4. Project Structure

```
06-GenAI-Nexus/
├── main.py                          # CLI entry point (argparse)
├── app.py                           # Streamlit web UI (10 tabs)
├── requirements.txt                 # 47 Python dependencies
├── .env.example                     # Template for API keys (31 vars)
├── README.md                        # Project overview + tool coverage map
│
├── config/
│   └── settings.py                  # Pydantic BaseSettings (all config)
│
├── pipeline/
│   └── startup_advisor.py           # Main orchestrator (ties all 27 tools)
│
├── src/
│   ├── llm/                         # LLM Provider Clients
│   │   ├── openai_client.py         #   OpenAI GPT-4o-mini (market analysis, function calling)
│   │   ├── claude_client.py         #   Claude 3 Haiku (competitor analysis, code gen)
│   │   ├── gemini_client.py         #   Gemini 1.5 Flash (multimodal, structured output)
│   │   ├── ollama_client.py         #   Ollama local LLM (LLaMA, Mistral, Qwen — zero cost)
│   │   └── llm_router.py           #   Task-based routing (local-first when --local)
│   │
│   ├── nlp/
│   │   └── text_processor.py        # Text cleaning, NER, keywords, startup components
│   │
│   ├── embeddings/
│   │   └── embedding_service.py     # OpenAI + HuggingFace embeddings, caching
│   │
│   ├── vectorstore/
│   │   └── chroma_store.py          # ChromaDB with sample knowledge + fallback search
│   │
│   ├── rag/
│   │   ├── basic_rag.py             # Retrieve-Augment-Generate with chunking
│   │   ├── advanced_rag.py          # HyDE, hybrid search, reranking, multi-hop
│   │   └── llama_indexer.py         # LlamaIndex with case studies and reports
│   │
│   ├── chains/
│   │   └── analysis_chains.py       # LangChain LCEL 4-stage sequential chain
│   │
│   ├── graph/
│   │   └── startup_workflow.py      # LangGraph 7-node stateful workflow
│   │
│   ├── agents/
│   │   ├── agentic_core.py          # ReAct agent (Thought→Action→Observation)
│   │   ├── crew_team.py             # CrewAI 4-agent C-suite team
│   │   └── autogen_debate.py        # AutoGen 3-agent debate (optimist/skeptic/mediator)
│   │
│   ├── safety/
│   │   └── output_validator.py      # Guardrails: hallucination, safety, schema validation
│   │
│   ├── prompts/
│   │   ├── prompt_templates.py      # CoT, persona, ReAct prompts + registry
│   │   └── few_shot_examples.py     # Market sizing, moat, pitch examples
│   │
│   ├── huggingface/
│   │   └── hf_models.py             # Sentiment, NER, zero-shot, summarization pipelines
│   │
│   ├── models/
│   │   ├── sentiment_model.py       # Keras BiLSTM sentiment classifier
│   │   └── transfer_adapter.py      # DistilBERT fine-tuning for legal domain
│   │
│   ├── training/
│   │   ├── peft_trainer.py          # LoRA/QLoRA fine-tuning on LLaMA
│   │   ├── rlhf_feedback.py         # Human preference collection + reward model
│   │   └── distributed_trainer.py   # DDP + DeepSpeed ZeRO + FSDP configs
│   │
│   ├── optimization/
│   │   ├── quantizer.py             # INT8/INT4/GGUF quantization + benchmarks
│   │   └── inference_server.py      # vLLM async server with PagedAttention
│   │
│   └── cloud/
│       └── aws_client.py            # SageMaker endpoints + Bedrock + Comprehend
│
├── data/
│   └── knowledge_base/
│       ├── market_data.txt           # Legal tech market data (TAM, CAGR, segments)
│       └── startup_reports.txt       # Competitor case studies (Harvey AI, Ironclad, Clio)
│
└── tests/
    ├── test_llm.py                   # LLM client tests (15 tests)
    ├── test_rag.py                   # RAG pipeline tests (17 tests)
    ├── test_agents.py                # Agent tests (14 tests)
    └── test_pipeline.py              # Full pipeline + NLP + prompts + safety tests (20+ tests)
```

---

## 5. Installation & Setup

### Prerequisites

- Python 3.12+
- pip (or conda)
- (Optional) GPU with CUDA for training modules
- (Optional) API keys for live LLM calls

### Step 1: Install Dependencies

```bash
cd 14-TechStack/Gen-AI/Projects/06-GenAI-Nexus
pip install -r requirements.txt
```

**Key dependencies (47 total):**

| Category          | Packages                                                                                      |
| ----------------- | --------------------------------------------------------------------------------------------- |
| **LLM Providers** | `openai`, `anthropic`, `google-generativeai`                                                  |
| **Orchestration** | `langchain`, `langchain-openai`, `langchain-anthropic`, `langchain-google-genai`, `langgraph` |
| **RAG**           | `chromadb`, `llama-index`                                                                     |
| **Agents**        | `crewai`, `pyautogen`                                                                         |
| **Safety**        | `guardrails-ai`                                                                               |
| **NLP**           | `spacy`, `nltk`                                                                               |
| **Embeddings**    | `sentence-transformers`                                                                       |
| **HuggingFace**   | `transformers`, `datasets`, `accelerate`                                                      |
| **Training**      | `peft`, `trl` (RLHF), `bitsandbytes`, `deepspeed`                                             |
| **ML**            | `keras`, `torch`                                                                              |
| **Optimization**  | `vllm`, `auto-gptq`                                                                           |
| **Cloud**         | `boto3`, `sagemaker`                                                                          |
| **Web**           | `streamlit`                                                                                   |

### Step 2: Configure API Keys (Optional)

```bash
cp .env.example .env
# Edit .env with your keys:
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_API_KEY=AI...
```

> **No API keys? No problem.** Every module has a complete `demo` mode with realistic mock responses. You can explore the entire project without any API keys.

### Step 3: Verify Installation

```bash
# Run all tests (demo mode, no keys needed)
python -m pytest tests/ -v

# Run a single module demo
python -c "from src.llm.openai_client import demo; demo()"
```

---

## 6. Running the Application

### CLI Mode

```bash
# Demo mode (no API keys needed, fast)
python main.py --idea "AI-powered legal document analyzer" --mode demo

# Quick mode (needs API keys, skips training)
python main.py --idea "AI-powered legal document analyzer" --mode quick

# Full mode (all 27 tools, needs GPU + all keys)
python main.py --idea "AI-powered legal document analyzer" --mode full

# Run an individual module demo
python main.py --demo-individual openai_client
python main.py --demo-individual advanced_rag
python main.py --demo-individual crew_team
```

### Streamlit Web UI

```bash
streamlit run app.py
```

Opens a web interface with 10 tabs:
1. **Overview** — Full startup plan summary
2. **Market Research** — TAM/SAM/SOM analysis
3. **Competitive** — Competitor landscape table
4. **Technical** — Architecture recommendation
5. **Team Plan** — CEO/CTO/CMO/CFO strategies
6. **Debate** — Optimist vs Skeptic stress test
7. **Pitch Content** — Investor pitch material
8. **Code Skeleton** — MVP code generation
9. **Sentiment** — Market sentiment scoring
10. **Module Demos** — Run any of the 26 modules individually

### Output

The pipeline generates a `startup_plan.md` file containing all 9 sections of the startup analysis. Example output structure:

```markdown
# STARTUP PLAN: AI-POWERED LEGAL DOCUMENT ANALYZER
- Market Research (TAM $45.2B, 18.9% CAGR)
- Competitive Landscape (Harvey AI, Ironclad, Clio analysis)
- Technical Architecture (FastAPI + Claude + pgvector + AWS)
- Executive Team Plans (CEO, CTO, CMO, CFO strategies)
- Devil's Advocate Debate (risks identified and mitigated)
- Pitch Content (30-second elevator pitch)
- Code Skeleton (MVP implementation)
- Market Sentiment (BULLISH/BEARISH/NEUTRAL)
- Validation Status (✅ PASSED / ⚠️ Review needed)
```

---

## 7. Module Deep Dives

### 7.1 LLM Clients

#### OpenAI Client (`src/llm/openai_client.py` — 277 lines)

**Purpose:** Market research and business plan generation using GPT-4o-mini.

**Key capabilities:**
- **Chat Completions** — `analyze_market()` sends structured prompts for market analysis
- **Function Calling** — `generate_business_plan()` uses OpenAI's tool/function calling to get structured JSON (revenue model, competitive moat, GTM, team plan)
- **Async Parallel** — `parallel_analysis()` runs multiple analyses concurrently via `asyncio.gather()`
- **Streaming** — `stream_analysis()` yields tokens as they're generated

```python
client = OpenAIClient()  # auto-detects demo mode if no API key
result = client.analyze_market("AI legal document analyzer")
# → AnalysisResult(content="...", model="gpt-4o-mini", tokens_used=450)
```

#### Claude Client (`src/llm/claude_client.py` — 270 lines)

**Purpose:** Competitive analysis (leveraging Claude's 200K context) and code generation.

**Key capabilities:**
- **Long-Context Analysis** — `analyze_competitors()` sends the full startup idea + market context in one call
- **Code Generation** — `generate_code_skeleton()` produces MVP code with specified tech stack
- **Multi-Turn Conversation** — `multi_turn_advisor()` maintains conversation history for iterative advisory

```python
client = ClaudeClient()
result = client.analyze_competitors("AI legal document analyzer")
# → ClaudeResponse with competitor table: Harvey AI, Ironclad, Clio
```

#### Gemini Client (`src/llm/gemini_client.py` — 253 lines)

**Purpose:** Multimodal analysis and structured output.

**Key capabilities:**
- **Multimodal Input** — `analyze_image_and_text()` processes both image (base64) and text
- **Structured JSON Output** — `structured_market_data()` returns typed JSON (market_size, cagr, competitors)
- **Pitch Content** — `pitch_deck_content()` generates investor presentation material

```python
client = GeminiClient()
result = client.structured_market_data("AI legal document analyzer")
# → GeminiResponse with structured={"market_size_usd_billions": 45.2, "cagr_percent": 18.9, ...}
```

### 7.2 LLM Router

**File:** `src/llm/llm_router.py` (149 lines)

Routes tasks to the optimal LLM based on task type:

| TaskType              | Routed To | Reason                  |
| --------------------- | --------- | ----------------------- |
| `MARKET_RESEARCH`     | OpenAI    | Strong function calling |
| `COMPETITOR_ANALYSIS` | Claude    | 200K context window     |
| `CODE_GENERATION`     | Claude    | Best code quality       |
| `PITCH_CONTENT`       | Gemini    | Creative content        |
| `MULTIMODAL`          | Gemini    | Native multimodal       |
| `FAST_SUMMARY`        | Gemini    | Low latency             |

```python
router = LLMRouter()
result = router.route(TaskType.COMPETITOR_ANALYSIS, {"startup_idea": "AI legal"})
# Automatically calls Claude client
```

### 7.3 NLP Text Processor

**File:** `src/nlp/text_processor.py` (259 lines)

**Pipeline:** clean → tokenize → split_sentences → extract_entities → extract_keywords → extract_startup_components

**Key features:**
- HTML/URL removal, whitespace normalization
- spaCy NER (ORG, PRODUCT, MONEY, GPE, PERSON, DATE) with regex fallback
- Domain-aware keyword extraction (boosted terms: saas, api, ai, ml, llp, tam)
- Startup component extraction: problem, solution, customer, technology, market

```python
proc = TextProcessor()
result = proc.process("AI-powered legal document analyzer using NLP for law firms")
# → ProcessedText(cleaned="...", word_count=9, keywords=["ai", "legal", "nlp"],
#                 entities=[...], startup_components={"technology": "AI, NLP", ...})
```

### 7.4 Embeddings & Vector Store

#### Embedding Service (`src/embeddings/embedding_service.py` — 286 lines)

**Supports 3 backends:**
1. **OpenAI** — `text-embedding-3-small` (1536 dimensions)
2. **HuggingFace** — `all-MiniLM-L6-v2` (384 dimensions)
3. **Demo** — deterministic MD5-based fake embeddings (384 dimensions)

**Features:** batch embedding, cosine similarity, semantic search, disk-based cache (JSON)

#### ChromaDB Vector Store (`src/vectorstore/chroma_store.py` — 267 lines)

**Preloaded knowledge:** 5 sample documents (Harvey AI competitor, Ironclad competitor, market data, research, GTM strategy)

**Features:**
- `add_documents()` — ingest with metadata
- `search()` — semantic similarity search with metadata filtering
- `search_by_type()` — filter by document type (competitor, market, strategy)
- **Fallback:** keyword overlap search when ChromaDB is unavailable

### 7.5 RAG Pipeline

Three progressive RAG implementations:

#### Basic RAG (`src/rag/basic_rag.py` — 200 lines)

```
Query → TextChunker (500 chars, 50 overlap) → ChromaDB search → Augment prompt → LLM generate
```

- `TextChunker`: fixed-size chunking with sentence-boundary awareness
- System prompt enforces grounded answers only (no hallucination)

#### Advanced RAG (`src/rag/advanced_rag.py` — 302 lines)

```
Query → HyDE hypothetical doc → Hybrid Search (0.7×semantic + 0.3×BM25) → Cross-Encoder Rerank → LLM generate
```

- **HyDE (Hypothetical Document Embeddings):** generates a hypothetical ideal answer, then searches for similar real documents
- **Hybrid Search:** combines semantic similarity (70%) with BM25 keyword matching (30%)
- **Cross-Encoder Reranking:** uses `cross-encoder/ms-marco` to re-score candidates
- **Multi-hop Q&A:** decomposes complex queries into sub-queries, answers each, then synthesizes

#### LlamaIndex (`src/rag/llama_indexer.py` — 271 lines)

Alternative indexing approach with rich inline data:
- 3 startup case studies (Ironclad, Harvey AI, Clio) with metrics
- 2 market reports (TAM/SAM, segment breakdown, geographic split)
- Methods: `query()`, `summarize()`, `keyword_search()`

### 7.6 LangChain Analysis Chains

**File:** `src/chains/analysis_chains.py` (246 lines)

Uses **LangChain Expression Language (LCEL)** to build a 4-stage sequential pipeline:

```
Stage 1: Market Analysis
    ↓ (output feeds as context to next)
Stage 2: Competitive Analysis
    ↓
Stage 3: Technical Plan
    ↓
Stage 4: Final Report (synthesizes all above)
```

Each stage is a `ChatPromptTemplate | LLM | StrOutputParser` chain.
Uses `RunnablePassthrough.assign()` for context injection between stages.

Also supports `run_parallel_analysis()` — runs all stages simultaneously (independent analysis).

### 7.7 LangGraph Stateful Workflow

**File:** `src/graph/startup_workflow.py` (435 lines)

The **spine** of the entire pipeline. A LangGraph `StateGraph` with 8 nodes:

```
START → preprocess_node → research_node → analyze_node → team_plan_node
                                                              ↓
        error_node ←── [FAILED] ←── validate_node ←── debate_node
              ↓                          ↓ [PASSED]
            RETRY                    output_node → END
```

**State management:** `WorkflowState` dataclass accumulates results through the pipeline (market_research, competitive_analysis, technical_plan, team_assignments, debate_outcome, validation results).

**Conditional edge:** After validation, routes to `output_node` (if passed) or `error_node` (if failed, for recovery/retry).

**Fallback:** If LangGraph is not installed, executes all nodes sequentially.

### 7.8 Agents

#### ReAct Agent (`src/agents/agentic_core.py` — 317 lines)

Implements the **Thought → Action → Observation** loop:

```
Thought: I need to research the legal tech market
Action: search_market("legal tech AI 2024")
Observation: Legal tech market is $45.2B...
Thought: Now I should generate the MVP code
Action: generate_code("AI legal analyzer")
Observation: class LegalDocAnalyzer:...
Final Answer: [synthesized result]
```

**4 built-in tools:**
| Tool                 | Purpose                  |
| -------------------- | ------------------------ |
| `search_market`      | Market data retrieval    |
| `search_competitors` | Competitor intelligence  |
| `generate_code`      | MVP code skeleton        |
| `create_pitch`       | Elevator pitch narrative |

Max 10 iterations. Falls back to LangChain `AgentExecutor` when API keys available.

#### CrewAI Team (`src/agents/crew_team.py` — 328 lines)

4-agent executive team, each with detailed persona:

| Agent   | Role             | Expertise                      | Output                                               |
| ------- | ---------------- | ------------------------------ | ---------------------------------------------------- |
| **CEO** | Chief Executive  | 3x founder, fundraising expert | 18-month roadmap with milestones                     |
| **CTO** | Chief Technology | Stanford CS, ex-Google/Stripe  | Technical architecture (FastAPI + Claude + pgvector) |
| **CMO** | Chief Marketing  | Clio growth expert             | 4-channel GTM strategy                               |
| **CFO** | Chief Financial  | Former VC analyst              | Month-by-month financial model (M3→M18)              |

Process: `sequential` — CEO → CTO → CMO → CFO, each builds on previous output.

#### AutoGen Debate (`src/agents/autogen_debate.py` — 243 lines)

3-agent adversarial stress test:

| Agent        | Role      | Goal                                            |
| ------------ | --------- | ----------------------------------------------- |
| **Optimist** | Bull case | Finds every reason the startup will succeed     |
| **Skeptic**  | Bear case | Finds fatal flaws and risks                     |
| **Mediator** | Synthesis | Weighs both sides, produces balanced assessment |

Uses `GroupChat` with `round_robin` speaker selection. `extract_risks()` parses identified risks from debate output.

### 7.9 Prompt Engineering & Few-Shot

#### Prompt Templates (`src/prompts/prompt_templates.py` — 270 lines)

**Prompt registry** with versioned, typed prompts:

| Prompt                 | Version | Technique                                                 |
| ---------------------- | ------- | --------------------------------------------------------- |
| `market_research`      | v2      | Chain-of-Thought with XML tags (`<thinking>`, `<output>`) |
| `competitive_analysis` | v1      | Structured analysis framework                             |
| `technical_plan`       | v1      | Architecture decision prompt                              |
| `pitch_narrative`      | v1      | Elevator pitch formula                                    |

**6 persona system prompts:** STARTUP_ANALYST, CEO, CTO, CMO, CFO, plus ReAct agent prompt.

#### Few-Shot Examples (`src/prompts/few_shot_examples.py` — 220 lines)

| Task             | Examples                      | Technique                                  |
| ---------------- | ----------------------------- | ------------------------------------------ |
| Market Sizing    | HR tech TAM + Legal tech TAM  | Step-by-step calculation                   |
| Competitive Moat | Stripe moats + Legal AI moats | Framework-based analysis                   |
| Pitch Narrative  | 30-second elevator pitch      | Hook → Problem → Solution → Traction → Ask |

**Advanced prompting methods:**
- `build_few_shot_prompt()` — standard few-shot
- `build_zero_shot_cot()` — "Let's think step by step"
- `self_consistency_prompt()` — 3 independent reasoning paths

### 7.10 Safety & Guardrails

**File:** `src/safety/output_validator.py` (300 lines)

Three composable validators:

| Validator                  | What It Catches                                                                            |
| -------------------------- | ------------------------------------------------------------------------------------------ |
| **HallucinationDetector**  | "100% market share", "1000% growth", uncited dollar figures, fabricated company names      |
| **ContentSafetyValidator** | Insider trading language, regulatory avoidance, fake reviews, spam references              |
| **StartupReportValidator** | Missing sections (market, competitor, revenue, team), insufficient numbers/data, too short |

**Methods:**
- `validate_report(text)` → `(passed: bool, issues: list[str])`
- `validate_market_data(data)` → validates TAM/CAGR/growth ranges
- `correct_common_errors(text)` → auto-fix formatting issues

### 7.11 HuggingFace Models

**File:** `src/huggingface/hf_models.py` (260 lines)

**5 HuggingFace pipeline integrations:**

| Pipeline                 | Model                                              | Use Case                                            |
| ------------------------ | -------------------------------------------------- | --------------------------------------------------- |
| Sentiment Analysis       | `distilbert-base-uncased-finetuned-sst-2-english`  | Market news sentiment                               |
| NER                      | `dbmdz/bert-large-cased-finetuned-conll03-english` | Extract companies, money, locations                 |
| Zero-Shot Classification | `facebook/bart-large-mnli`                         | Classify startup domain (legal tech, fintech, etc.) |
| Summarization            | `sshleifer/distilbart-cnn-12-6`                    | Summarize long articles                             |
| Aggregate Scoring        | Custom                                             | Market sentiment score: BULLISH/BEARISH/NEUTRAL     |

```python
hf = HuggingFaceModels()
score = hf.market_sentiment_score([
    "AI tools for legal tech gain adoption",
    "Investors pour money into AI startups",
    "Challenges remain for AI in legal industry",
])
# → {"overall": 0.35, "positive_pct": 0.67, "interpretation": "BULLISH"}
```

### 7.12 Custom Models

#### Keras LSTM Sentiment Model (`src/models/sentiment_model.py` — 235 lines)

**Architecture:**
```
Input (string) → TextVectorization (vocab=5000, maxlen=50)
    → Embedding (64d, mask_zero=True)
    → Bidirectional LSTM (32 units)
    → Dropout(0.3)
    → Dense(16, relu)
    → Dense(1, sigmoid)
    ≈ 350K trainable parameters
```

**Training data:** 20 labeled legal tech news snippets (10 positive, 10 negative).

#### Transfer Learning Adapter (`src/models/transfer_adapter.py` — 330 lines)

**Fine-tunes DistilBERT** for 5-class legal domain classification:

| Label       | Examples                                 |
| ----------- | ---------------------------------------- |
| `contract`  | "This agreement shall be governed by..." |
| `financial` | "Series A funding closed at $5M..."      |
| `technical` | "AI system achieves 94% accuracy..."     |
| `market`    | "TAM expansion driven by AI adoption..." |
| `strategy`  | "Beachhead market: NDA review for..."    |

**Two modes:**
- **Feature extraction** — freeze base, train only classification head (fast)
- **Full fine-tune** — all layers trainable (better accuracy)

Also provides `extract_features()` — get CLS token embedding (768d) for downstream tasks.

### 7.13 Training

#### PEFT/LoRA Trainer (`src/training/peft_trainer.py` — 331 lines)

**Fine-tunes LLaMA-3.2-1B** on 5 startup advisory Q&A pairs using LoRA:

| Parameter            | Value              |
| -------------------- | ------------------ |
| LoRA rank (r)        | 8                  |
| LoRA alpha           | 16                 |
| Target modules       | q_proj, v_proj     |
| Dropout              | 0.1                |
| QLoRA (4-bit)        | Yes (NF4)          |
| **Trainable params** | **~0.1% of total** |

Training data: expert-quality Q&A pairs on pricing, SOC2, acquisition channels, fundraising, LTV/CAC.

#### RLHF Feedback Pipeline (`src/training/rlhf_feedback.py` — 347 lines)

**3 components:**

1. **HumanFeedbackCollector** — collects preference pairs (chosen vs rejected responses), stores as JSONL
2. **RewardModel** — heuristic-based scoring:
   - Positive signals: specificity, numbers, benchmarks, examples (+0.05 each)
   - Negative signals: vague phrases like "it depends", "generally" (-0.05 each)
   - Length bonus/penalty
3. **RLHFPipeline** — combines collection → scoring → DPO dataset preparation

**Sample preference:** Specific, actionable advice (*"Target solo practitioners using Clio who review NDAs... offer 6 months free"*) preferred over generic advice (*"Market on social media, attend networking events"*).

#### Distributed Training (`src/training/distributed_trainer.py` — 303 lines)

Demonstrates large-scale training setup:

| Feature               | Implementation                                                   |
| --------------------- | ---------------------------------------------------------------- |
| DDP                   | `torch.distributed + DistributedDataParallel`                    |
| DeepSpeed ZeRO        | Stage 1 (optimizer), Stage 2 (+gradients), Stage 3 (+parameters) |
| FSDP                  | PyTorch native Fully Sharded Data Parallel                       |
| Gradient Accumulation | Configurable (default: 8 steps)                                  |
| Cost Estimation       | AWS p4d.24xlarge pricing calculator                              |

**Memory estimates:**
| ZeRO Stage | Memory/GPU (7B model) |
| ---------- | --------------------- |
| Stage 0    | ~24GB                 |
| Stage 1    | ~12GB                 |
| Stage 2    | ~6GB                  |
| Stage 3    | ~3GB                  |

### 7.14 Optimization

#### Model Quantizer (`src/optimization/quantizer.py` — 260 lines)

**4 quantization methods:**

| Method      | Size Reduction | Speed Improvement | Accuracy Drop |
| ----------- | -------------- | ----------------- | ------------- |
| FP16        | 2x             | 1.6x              | 0.5%          |
| INT8        | 4x             | 2.5x              | 1.2%          |
| INT4 (NF4)  | 8x             | 3.7x              | 2.9%          |
| GGUF Q4_K_M | 6.7x           | 4.5x              | 2.6%          |

Features: `recommend_quantization()` based on constraints (GPU memory, latency, accuracy target, deployment type), `estimate_memory()` for any model size/dtype, GGUF export commands.

#### vLLM Inference Server (`src/optimization/inference_server.py` — 344 lines)

**Key vLLM innovations demonstrated:**
- **PagedAttention** — manages KV cache like OS virtual memory → 24x more throughput
- **Continuous Batching** — new requests join mid-computation
- **Tensor Parallelism** — split model across GPUs
- **OpenAI-compatible API** — drop-in replacement

Features: async `generate()`, `generate_stream()` (token-by-token streaming), `batch_generate()` (concurrent requests), server launch command, client code generation.

### 7.15 Cloud Deployment

**File:** `src/cloud/aws_client.py` (434 lines)

**5 AWS services integrated:**

| Service                | Use Case                                                    |
| ---------------------- | ----------------------------------------------------------- |
| **SageMaker**          | Deploy model as real-time endpoint (`ml.g4dn.xlarge`)       |
| **SageMaker Training** | Launch training jobs on `ml.p4d.24xlarge` (HuggingFace DLC) |
| **Bedrock**            | Managed Claude API (fallback LLM with no infrastructure)    |
| **Comprehend**         | Managed sentiment analysis + entity detection               |
| **Textract**           | Document text extraction (OCR)                              |

```python
aws = AWSClient(aws_key="...", aws_secret="...")
# Deploy model
status = aws.deploy_endpoint(SageMakerConfig(instance_type="ml.g4dn.xlarge"))
# Invoke deployed model
result = aws.invoke_endpoint("startup-advisor-endpoint", {"inputs": "legal tech advice"})
# Fallback to Bedrock
response = aws.bedrock_invoke("What is the TAM for legal tech?")
```

---

## 8. Pipeline Orchestration

**File:** `pipeline/startup_advisor.py` (280 lines)

The `StartupAdvisor` class ties all 27 tools together in a staged execution:

| Stage       | Tools Used                                                      | Mode         | Output                                                                           |
| ----------- | --------------------------------------------------------------- | ------------ | -------------------------------------------------------------------------------- |
| **Stage 1** | LangGraph → NLP, AdvRAG, LangChain, CrewAI, AutoGen, Guardrails | All modes    | Market research, competitive analysis, tech plan, team plans, debate, validation |
| **Stage 2** | LLM Router (OpenAI/Claude/Gemini)                               | All modes    | Pitch content                                                                    |
| **Stage 3** | ReAct Agent                                                     | All modes    | Code skeleton                                                                    |
| **Stage 4** | HuggingFace                                                     | All modes    | Market sentiment score                                                           |
| **Stage 5** | Keras                                                           | quick + full | Domain sentiment model                                                           |
| **Stage 6** | Transfer Learning (DistilBERT)                                  | quick + full | Legal domain classifier                                                          |
| **Stage 7** | PEFT/LoRA                                                       | quick + full | Fine-tuned LLM                                                                   |
| **Stage 8** | Quantization + vLLM                                             | full only    | Compressed model + inference                                                     |

**Output:** `StartupPlan` dataclass → `save()` writes a formatted Markdown report.

---

## 9. Knowledge Base & Data

### Market Data (`data/knowledge_base/market_data.txt`)

Comprehensive legal tech market intelligence:
- **TAM:** $45.2B (2024), growing to $127.8B by 2030 at 18.9% CAGR
- **AI Legal Tech specifically:** $1.2B → $16.1B at 44.4% CAGR
- **Segment breakdown:** Contract Management (28%), eDiscovery (22%), Legal Research (18%), Compliance (15%), Billing (12%), Document Management (5%)
- **Buyer segments:** BigLaw 8% of firms / 45% of spend, Small firms 80% of firms / 25% of spend
- **Pricing benchmarks:** Clio $49-149/user/mo, Harvey AI $5K-20K/mo, Ironclad $30K-200K/yr
- **Key insight:** No AI-native solution at $199-999/month for small/mid firms

### Startup Reports (`data/knowledge_base/startup_reports.txt`)

Competitor case studies with detailed metrics:
- **Harvey AI** — $100M+ Series B, BigLaw focus, GPT-4 powered
- **Ironclad** — $333M total funding, enterprise CLM
- **Clio** — $1.1B funding, $1.6B valuation, 150K+ law firms
- **ContractPodAi** — $115M Series C, enterprise AI CLM
- Competitive moat framework, fundraising benchmarks, key metrics

---

## 10. Testing

### Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Individual test files
python -m pytest tests/test_llm.py -v
python -m pytest tests/test_rag.py -v
python -m pytest tests/test_agents.py -v
python -m pytest tests/test_pipeline.py -v
```

### Test Coverage

| Test File          | Tests | What's Tested                                                                                                                |
| ------------------ | ----- | ---------------------------------------------------------------------------------------------------------------------------- |
| `test_llm.py`      | 15    | All 3 LLM clients (demo mode), router (all task types), streaming                                                            |
| `test_rag.py`      | 17    | Text chunking, ChromaDB, Basic RAG, Advanced RAG (HyDE, decomposer, multihop), LlamaIndex                                    |
| `test_agents.py`   | 14    | ReAct agent (tools, execution, tracking), CrewAI team (all roles), AutoGen debate (both sides, risk extraction)              |
| `test_pipeline.py` | 20+   | NLP processor, prompt engineering, few-shot builder, guardrails validation, embeddings, full pipeline (demo mode), plan save |

**All tests run in demo mode by default** — no API keys or GPU required.

---

## 11. Key Design Patterns

### Pattern 1: Universal Demo Mode

Every module follows this pattern:

```python
class SomeModule:
    def __init__(self):
        self._demo = True
        try:
            import some_library
            self._demo = False
        except ImportError:
            pass

    def some_method(self, input):
        if self._demo:
            return DEMO_RESPONSE  # Realistic mock data
        # Real implementation...
```

**Why:** Makes every module independently runnable, testable, and educational without external dependencies.

### Pattern 2: Dataclass-First Outputs

Every module returns typed dataclasses:

```python
@dataclass
class AnalysisResult:
    content: str
    model: str
    tokens_used: int
```

**Why:** Type safety, IDE autocomplete, self-documenting APIs.

### Pattern 3: Standalone `demo()` Functions

Every module has a `demo()` function and `if __name__ == "__main__": demo()`:

```bash
# Run ANY module standalone
python src/llm/openai_client.py
python src/agents/crew_team.py
python src/optimization/quantizer.py
```

**Why:** Supports both pipeline integration and individual learning/experimentation.

### Pattern 4: Progressive Enhancement

```
Basic RAG → Advanced RAG (adds HyDE, hybrid, reranking) → LlamaIndex (alternative approach)
Single LLM → Router (picks best LLM per task) → Multi-agent (parallel agents)
Simple prompt → CoT → Few-shot → Self-consistency
```

**Why:** Shows how each tool builds on the previous, making complexity incremental.

### Pattern 5: Pydantic Settings Configuration

```python
# config/settings.py
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    openai_api_key: str = ""
    demo_mode: bool = True

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key)
```

**Why:** Type-safe config, `.env` loading, property-based key validation.

---

## 12. Learning Path (Beginner → Advanced)

### Beginner (Week 1-2)

Start with the simplest modules:

1. **NLP Text Processor** — `src/nlp/text_processor.py` → understand text preprocessing
2. **Prompt Templates** — `src/prompts/prompt_templates.py` → learn CoT prompting
3. **OpenAI Client** — `src/llm/openai_client.py` → basic LLM API calls
4. **Basic RAG** — `src/rag/basic_rag.py` → retrieve + augment + generate
5. **Embeddings** — `src/embeddings/embedding_service.py` → vector representations

**Run each:** `python src/<module>.py` and read the code.

### Intermediate (Week 3-4)

Build on fundamentals:

6. **ChromaDB** — `src/vectorstore/chroma_store.py` → vector database operations
7. **LLM Router** — `src/llm/llm_router.py` → multi-model orchestration
8. **Advanced RAG** — `src/rag/advanced_rag.py` → HyDE, hybrid search, reranking
9. **LangChain Chains** — `src/chains/analysis_chains.py` → LCEL pipeline composition
10. **Few-Shot Builder** — `src/prompts/few_shot_examples.py` → advanced prompting
11. **Guardrails** — `src/safety/output_validator.py` → output validation
12. **HuggingFace** — `src/huggingface/hf_models.py` → pipeline API for NLP tasks

### Advanced (Week 5-6)

Complex orchestration and agents:

13. **LangGraph Workflow** — `src/graph/startup_workflow.py` → stateful multi-step pipelines
14. **ReAct Agent** — `src/agents/agentic_core.py` → autonomous tool-using agent
15. **CrewAI Team** — `src/agents/crew_team.py` → multi-agent collaboration
16. **AutoGen Debate** — `src/agents/autogen_debate.py` → adversarial multi-agent
17. **Pipeline Orchestrator** — `pipeline/startup_advisor.py` → full system integration

### Expert (Week 7-8)

ML training and production:

18. **Keras Model** — `src/models/sentiment_model.py` → custom LSTM from scratch
19. **Transfer Learning** — `src/models/transfer_adapter.py` → DistilBERT fine-tuning
20. **PEFT/LoRA** — `src/training/peft_trainer.py` → parameter-efficient LLM fine-tuning
21. **RLHF** — `src/training/rlhf_feedback.py` → human feedback loop
22. **Distributed** — `src/training/distributed_trainer.py` → multi-GPU training
23. **Quantization** — `src/optimization/quantizer.py` → model compression
24. **vLLM** — `src/optimization/inference_server.py` → production serving
25. **AWS** — `src/cloud/aws_client.py` → cloud deployment

---

## 13. Extending the Project

### Add a New LLM Provider

1. Create `src/llm/new_provider_client.py` following the pattern in `openai_client.py`
2. Add demo responses and dataclass outputs
3. Register in `llm_router.py`'s `_ROUTING_TABLE`
4. Add tests in `tests/test_llm.py`

### Add a New Agent

1. Create `src/agents/new_agent.py` with demo mode
2. Integrate into `startup_workflow.py` as a new node
3. Add to `pipeline/startup_advisor.py`

### Add a New Knowledge Domain

1. Add market data to `data/knowledge_base/`
2. Update `chroma_store.py` SAMPLE_KNOWLEDGE
3. Update prompt templates for the domain
4. Modify TRAINING_DATA in `sentiment_model.py` and `transfer_adapter.py`

### Add a New Tool Category

1. Create appropriate module under `src/`
2. Include demo mode, dataclass output, standalone `demo()` function
3. Wire into `startup_workflow.py` or `startup_advisor.py`
4. Add tests
5. Update `_TOOL_REGISTRY` in `startup_advisor.py`

---

## Quick Reference

| What              | Command                                                                                                                                               |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Run full demo     | `python main.py --idea "your idea" --mode demo`                                                                                                       |
| Run web UI        | `streamlit run app.py`                                                                                                                                |
| Run single module | `python src/llm/openai_client.py`                                                                                                                     |
| Run all tests     | `python -m pytest tests/ -v`                                                                                                                          |
| List all modules  | `python main.py --demo-individual help`                                                                                                               |
| Check environment | `python -c "from config.settings import Settings; s=Settings(); print(f'OpenAI: {s.has_openai}, Claude: {s.has_anthropic}, Gemini: {s.has_google}')"` |

---

*GenAI Nexus — Learn 27 Gen-AI tools by building one unified application. Runs fully local with Ollama.*
