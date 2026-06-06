# GenAI Nexus — AI Startup Advisor

**Project 06** — The first fully implemented project in the Gen-AI curriculum.

> One platform. 27 Gen-AI tools. One complete startup analysis. **Runs fully local with Ollama.**

---

## What It Does

You input a startup idea. GenAI Nexus runs it through **all 26 Gen-AI tool categories** and produces:

- Market research (TAM/SAM/SOM, trends, timing)
- Competitive landscape (real companies, real weaknesses, whitespace)
- Technical architecture (stack, AI pipeline, timeline)
- Executive team plan (CEO + CTO + CMO + CFO agents via CrewAI)
- Devil's advocate stress test (AutoGen multi-agent debate)
- Pitch deck content
- MVP code skeleton
- Market sentiment analysis
- Validated, hallucination-checked output

---

## Quick Start (No API Keys Needed)

```bash
cd Projects/06-GenAI-Nexus

# Install dependencies
pip install -r requirements.txt

# Run in demo mode (mock responses, no API keys needed)
python main.py --idea "AI legal document analyzer" --mode demo

# Run individual module demos
python main.py --demo-individual nlp
python main.py --demo-individual rag
python main.py --demo-individual crew

# Launch Streamlit UI
streamlit run app.py
```

### Run 100% Local with Ollama (No Cloud APIs, No Cost)

```bash
# 1. Install Ollama
brew install ollama && ollama serve

# 2. Pull required models (~12GB total)
ollama pull llama3.1:8b          # General analysis
ollama pull codellama:7b         # Code generation
ollama pull llama3.2:3b          # Fast summaries
ollama pull nomic-embed-text     # Local embeddings

# 3. Install minimal local dependencies
pip install -r requirements-local.txt

# 4. Run health check
./health_check.sh

# 5. Run the full pipeline locally
python main.py --idea "AI legal document analyzer" --local

# 6. Run Ollama module demo
python main.py --demo-individual ollama
```

---

## Architecture — 27 Tools, One Pipeline

```
User Input: "I want to build an AI legal document analyzer"
          ↓
[NLP]           Preprocess text, extract entities, keywords
          ↓
[LangGraph]     Stateful workflow orchestrates all stages
          ↓
[RAG + AdvRAG + LlamaIndex]   Research: competitors, market, trends
          ↓
[Embeddings + ChromaDB]       Store/retrieve knowledge chunks
          ↓
[Prompts + FewShot]           Structured chain-of-thought prompts
          ↓
[OpenAI + Claude + Gemini]    Parallel multi-LLM analysis
  OR [Ollama]                 100% local via LLaMA (--local flag)
          ↓
[LangChain]                   Chain: Market → Competitive → Technical
          ↓
[CrewAI]                      CEO/CTO/CMO/CFO agent team
          ↓
[AutoGen]                     Devil's advocate debate
          ↓
[AgenticAI]                   Autonomous code generation
          ↓
[HuggingFace + Keras]         Sentiment analysis on news
          ↓
[TransferLearning]            Domain-adapted classification
          ↓
[Guardrails]                  Validate outputs (no hallucinations)
          ↓
[RLHF + PEFT]                 Fine-tune on user feedback
          ↓
[Quantization + vLLM]         Serve optimized model fast
          ↓
[DistributedTraining]         Large-scale training setup
          ↓
[AWS SageMaker + Bedrock]     Cloud deployment config
          ↓
Output: Complete Startup Plan (market + tech + pitch + code)
```

---

## File Structure

```
06-GenAI-Nexus/
├── main.py                    # CLI entry point (--local flag for Ollama)
├── app.py                     # Streamlit web UI
├── requirements.txt           # All dependencies (cloud + local)
├── requirements-local.txt     # Minimal deps for local-only execution
├── health_check.sh            # Ollama + environment health check
├── .env.example               # API keys template
├── config/
│   └── settings.py            # Pydantic settings (incl. Ollama config)
├── data/
│   └── knowledge_base/        # Startup reports + market data
├── src/
│   ├── llm/                   # OpenAI, Claude, Gemini, Ollama, Router
│   ├── prompts/               # Prompt templates, few-shot examples
│   ├── nlp/                   # Text processing, NER
│   ├── embeddings/            # Embedding service
│   ├── vectorstore/           # ChromaDB
│   ├── rag/                   # Basic RAG, Advanced RAG, LlamaIndex
│   ├── chains/                # LangChain LCEL chains
│   ├── graph/                 # LangGraph workflow
│   ├── agents/                # AgenticAI, CrewAI, AutoGen
│   ├── safety/                # Guardrails validator
│   ├── huggingface/           # HuggingFace models
│   ├── models/                # Keras, TransferLearning
│   ├── training/              # PEFT, RLHF, DistributedTraining
│   ├── optimization/          # Quantization, vLLM
│   └── cloud/                 # AWS SageMaker + Bedrock
├── pipeline/
│   └── startup_advisor.py     # Main orchestrator
└── tests/
    ├── test_llm.py
    ├── test_ollama.py         # Ollama client tests (30 tests)
    ├── test_local_integration.py  # Local LLM integration tests (40 tests)
    ├── test_rag.py
    ├── test_agents.py
    └── test_pipeline.py
```

---

## 27 Gen-AI Tools — Coverage Map

| #   | Tool                   | File                                   | Startup Advisor Use                       |
| --- | ---------------------- | -------------------------------------- | ----------------------------------------- |
| 1   | OpenAI GPT             | `src/llm/openai_client.py`             | Market research, function calling         |
| 2   | Claude API             | `src/llm/claude_client.py`             | Long-context competitor analysis          |
| 3   | Gemini API             | `src/llm/gemini_client.py`             | Multimodal, pitch content                 |
| 4   | **Ollama (Local LLM)** | **`src/llm/ollama_client.py`**         | **Run entire pipeline locally via LLaMA** |
| 5   | LangChain              | `src/chains/analysis_chains.py`        | LCEL chain pipeline                       |
| 6   | LangGraph              | `src/graph/startup_workflow.py`        | Stateful workflow spine                   |
| 7   | RAG                    | `src/rag/basic_rag.py`                 | Knowledge retrieval                       |
| 8   | Advanced RAG           | `src/rag/advanced_rag.py`              | HyDE + hybrid search                      |
| 9   | LlamaIndex             | `src/rag/llama_indexer.py`             | Document indexing                         |
| 10  | Embeddings             | `src/embeddings/embedding_service.py`  | Semantic search                           |
| 11  | Vector Databases       | `src/vectorstore/chroma_store.py`      | ChromaDB storage                          |
| 12  | AgenticAI              | `src/agents/agentic_core.py`           | ReAct autonomous agent                    |
| 13  | CrewAI                 | `src/agents/crew_team.py`              | CEO+CTO+CMO+CFO team                      |
| 14  | AutoGen                | `src/agents/autogen_debate.py`         | Debate stress-test                        |
| 15  | Guardrails             | `src/safety/output_validator.py`       | Output validation                         |
| 16  | Prompt Engineering     | `src/prompts/prompt_templates.py`      | Chain-of-thought prompts                  |
| 17  | Few-Shot               | `src/prompts/few_shot_examples.py`     | Domain examples                           |
| 18  | NLP                    | `src/nlp/text_processor.py`            | Text preprocessing, NER                   |
| 19  | HuggingFace            | `src/huggingface/hf_models.py`         | Sentiment, zero-shot                      |
| 20  | Keras                  | `src/models/sentiment_model.py`        | Custom LSTM model                         |
| 21  | Transfer Learning      | `src/models/transfer_adapter.py`       | DistilBERT fine-tune                      |
| 22  | PEFT/LoRA              | `src/training/peft_trainer.py`         | Efficient fine-tuning                     |
| 23  | RLHF                   | `src/training/rlhf_feedback.py`        | Preference learning                       |
| 24  | Model Quantization     | `src/optimization/quantizer.py`        | INT8/INT4/GGUF                            |
| 25  | Inference Engines      | `src/optimization/inference_server.py` | vLLM serving                              |
| 26  | Distributed Training   | `src/training/distributed_trainer.py`  | DDP + ZeRO                                |
| 27  | AWS AI/ML              | `src/cloud/aws_client.py`              | SageMaker + Bedrock                       |

---

## API Keys (Optional)

All modules run in **demo mode** without API keys (graceful fallback).

To use real LLMs, copy `.env.example` to `.env` and add your keys:

```bash
cp .env.example .env
# Edit .env with your API keys
```

Keys needed per mode:
- `demo`: No keys needed
- `local`: No keys needed — uses Ollama (`python main.py --local`)
- `quick`: `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- `full`: All LLM keys + `AWS_ACCESS_KEY_ID`

---

## Running Tests

```bash
# All tests (demo mode, no API keys needed) — 138 tests
pytest tests/ -v

# Core tests
pytest tests/test_llm.py -v
pytest tests/test_rag.py -v
pytest tests/test_agents.py -v
pytest tests/test_pipeline.py -v

# Ollama / local LLM tests (30 + 40 tests)
pytest tests/test_ollama.py -v
pytest tests/test_local_integration.py -v
```

---

## Individual Module Demos

Every source file has a `demo()` function. Run any module standalone:

```bash
# LLM Clients
python src/llm/openai_client.py
python src/llm/claude_client.py
python src/llm/gemini_client.py
python src/llm/ollama_client.py      # Local LLM via Ollama

# RAG Pipeline
python src/rag/basic_rag.py
python src/rag/advanced_rag.py
python src/rag/llama_indexer.py

# Agents
python src/agents/agentic_core.py
python src/agents/crew_team.py
python src/agents/autogen_debate.py

# Training
python src/training/peft_trainer.py
python src/training/rlhf_feedback.py
python src/training/distributed_trainer.py

# Optimization
python src/optimization/quantizer.py
python src/optimization/inference_server.py

# Cloud
python src/cloud/aws_client.py
```

Or use the CLI shorthand:
```bash
python main.py --demo-individual openai
python main.py --demo-individual crew
python main.py --demo-individual quant
python main.py --demo-individual ollama   # Local LLM
```

---

## Design Principles

1. **Real patterns, not toys** — Each module demonstrates production patterns
2. **Graceful degradation** — Everything runs without API keys in demo mode
3. **Composable** — Each module works standalone OR as part of the pipeline
4. **Educational** — Detailed docstrings explain which tool is demonstrated and why

---

*GenAI Nexus — Part of the Gen-AI Full-Stack Curriculum*
*Project 06 of N*
