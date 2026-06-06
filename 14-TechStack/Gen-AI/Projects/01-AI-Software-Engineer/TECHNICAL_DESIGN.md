# Autonomous AI Software Engineer — Technical Design Document

**Version:** 1.0 | **Date:** March 6, 2026 | **Status:** Pre-Implementation Blueprint

---

## 1. System Overview

An autonomous coding agent that accepts tasks (GitHub issues, Jira tickets), understands codebases via RAG, plans implementations, writes multi-file code, runs/fixes tests, and creates PRs — inspired by Devin, OpenHands, and Cursor Agents.

---

## 2. High-Level Architecture

```mermaid
graph TB
    subgraph INPUT["📥 Task Input Layer"]
        style INPUT fill:#1e3a5f,color:#e0e0e0,stroke:#4a90d9,stroke-width:2px
        GH["🐙 GitHub Issues"]:::blue
        JR["📋 Jira Tickets"]:::orange
        SL["💬 Slack Messages"]:::yellow
        CLI["⌨️ CLI Commands"]:::green
    end

    subgraph ORCH["🧠 Agent Orchestrator — LangGraph"]
        style ORCH fill:#2d1b4e,color:#e0e0e0,stroke:#8e6cc0,stroke-width:2px
        PM["📋 Planner Agent<br/>Claude Opus"]:::purple
        CA["💻 Coder Agent<br/>GPT-4o / DeepSeek"]:::blue
        TA["🧪 Tester Agent<br/>Gemini Flash"]:::green
        RA["👁️ Reviewer Agent<br/>Claude Sonnet"]:::orange
        DA["📝 Documenter Agent<br/>GPT-4o-mini"]:::teal
    end

    subgraph KNOW["📚 Knowledge Layer"]
        style KNOW fill:#1a3a2e,color:#e0e0e0,stroke:#4caf50,stroke-width:2px
        IDX["🗂️ Codebase Index<br/>LlamaIndex + Tree-sitter"]:::green
        VDB["🔮 Vector Store<br/>Pinecone / ChromaDB"]:::purple
        RAG["📖 RAG Pipeline<br/>Hybrid Search + Rerank"]:::orange
    end

    subgraph EXEC["⚙️ Execution Sandbox"]
        style EXEC fill:#3a2a1a,color:#e0e0e0,stroke:#ff9800,stroke-width:2px
        FS["📁 File System"]:::yellow
        TERM["🖥️ Terminal"]:::grey
        DOCK["🐳 Docker Container"]:::blue
    end

    subgraph SAFE["🛡️ Safety & Quality"]
        style SAFE fill:#3a1a1a,color:#e0e0e0,stroke:#ef5350,stroke-width:2px
        GR["🚧 Guardrails AI"]:::red
        LINT["📏 Linters + Security"]:::orange
        COST["💰 Cost Guard"]:::green
    end

    subgraph OUT["📤 Output"]
        style OUT fill:#1a2a3a,color:#e0e0e0,stroke:#42a5f5,stroke-width:2px
        PR["🔀 Pull Request"]:::blue
        LOG["📊 Audit Trail"]:::teal
    end

    INPUT --> ORCH
    ORCH --> KNOW
    ORCH --> EXEC
    ORCH --> SAFE
    SAFE --> OUT
    EXEC --> OUT

    PM --> CA --> TA
    TA -->|fail| CA
    TA -->|pass| RA
    RA -->|issues| CA
    RA -->|approved| DA --> PR

    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0,stroke-width:1px
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32,stroke-width:1px
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100,stroke-width:1px
    classDef purple fill:#9C27B0,color:#fff,stroke:#6A1B9A,stroke-width:1px
    classDef red fill:#F44336,color:#fff,stroke:#C62828,stroke-width:1px
    classDef yellow fill:#FFC107,color:#000,stroke:#FF8F00,stroke-width:1px
    classDef teal fill:#009688,color:#fff,stroke:#00695C,stroke-width:1px
    classDef grey fill:#546E7A,color:#fff,stroke:#37474F,stroke-width:1px
```

---

## 3. Agent State Machine

```mermaid
stateDiagram-v2
    [*] --> TaskReceived
    TaskReceived --> Understanding : Parse task

    state Understanding {
        [*] --> IndexCodebase : LlamaIndex scan
        IndexCodebase --> RetrieveContext : RAG retrieval
        RetrieveContext --> AnalyzeDeps : Dependency graph
        AnalyzeDeps --> [*]
    }

    Understanding --> Planning : Context ready
    Planning --> Coding : Plan approved

    state Coding {
        [*] --> SelectFiles
        SelectFiles --> GenerateCode : LLM generation
        GenerateCode --> Validate : Guardrails check
        Validate --> [*]
    }

    Coding --> Testing : Code written
    Testing --> Coding : ❌ Tests fail
    Testing --> Reviewing : ✅ Tests pass
    Reviewing --> Coding : 🔄 Issues found
    Reviewing --> Documentation : ✅ Approved
    Documentation --> PRCreation
    PRCreation --> [*] : 🎉 Complete
```

---

## 4. Module Deep Dives

### 4.1 Codebase Indexing Pipeline

```mermaid
flowchart LR
    subgraph INGEST["Ingestion"]
        style INGEST fill:#1a2a3a,color:#e0e0e0,stroke:#42a5f5,stroke-width:2px
        REPO["Git Clone"]:::blue --> AST["Tree-sitter<br/>AST Parse"]:::green
        AST --> CHUNK["Smart Chunker<br/>Function-level"]:::orange
        CHUNK --> EMB["code-search-ada-002<br/>Embeddings"]:::purple
    end

    subgraph STORE["Storage"]
        style STORE fill:#2d1b4e,color:#e0e0e0,stroke:#8e6cc0,stroke-width:2px
        EMB --> PINE["Pinecone<br/>Code Vectors"]:::purple
        AST --> PG["PostgreSQL<br/>File Tree + Metadata"]:::blue
    end

    subgraph RETRIEVE["Retrieval"]
        style RETRIEVE fill:#1a3a2e,color:#e0e0e0,stroke:#4caf50,stroke-width:2px
        PINE --> HYB["Hybrid Search<br/>Semantic + Keyword"]:::green
        PG --> HYB
        HYB --> RERANK["Cross-Encoder<br/>Re-rank"]:::orange
        RERANK --> CTX["Context Builder<br/>Token-aware packing"]:::teal
    end

    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
    classDef purple fill:#9C27B0,color:#fff,stroke:#6A1B9A
    classDef teal fill:#009688,color:#fff,stroke:#00695C
```

### 4.2 Multi-Agent Communication

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant P as 📋 Planner
    participant K as 📚 Knowledge
    participant C as 💻 Coder
    participant T as 🧪 Tester
    participant R as 👁️ Reviewer

    U->>P: "Add dark mode to settings page"
    P->>K: Query codebase structure
    K-->>P: File tree, component graph, styles
    P->>C: Plan: [1. Theme context, 2. Settings UI, 3. CSS vars]

    loop For each step
        C->>K: Get file contents
        K-->>C: Code + patterns
        C->>C: Generate code changes
        C->>T: Run tests
        alt Tests fail
            T-->>C: Error + stack trace
        else Tests pass
            T-->>R: All green ✅
        end
    end

    R->>R: Check quality + patterns
    R-->>U: PR created ✅
```

### 4.3 Sandbox Execution Environment

```mermaid
flowchart TD
    subgraph SANDBOX["🐳 Docker Sandbox"]
        style SANDBOX fill:#1a2a3a,color:#e0e0e0,stroke:#42a5f5,stroke-width:2px
        FS2["📁 File System<br/>Read / Write / Create"]:::blue
        TERM2["🖥️ Terminal<br/>pip, npm, make, pytest"]:::grey
        NET["🌐 Network<br/>Clone, install packages"]:::green
        TIMEOUT["⏱️ Timeout Guard<br/>Max 30 min per task"]:::red
    end

    subgraph LIMITS["Resource Limits"]
        style LIMITS fill:#3a1a1a,color:#e0e0e0,stroke:#ef5350,stroke-width:2px
        CPU["CPU: 4 cores"]:::orange
        MEM["RAM: 8 GB"]:::orange
        DISK["Disk: 20 GB"]:::orange
        TOKEN["Tokens: 500K budget"]:::yellow
    end

    SANDBOX --> LIMITS

    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
    classDef red fill:#F44336,color:#fff,stroke:#C62828
    classDef yellow fill:#FFC107,color:#000,stroke:#FF8F00
    classDef grey fill:#546E7A,color:#fff,stroke:#37474F
```

### 4.4 Safety & Quality Gates

```mermaid
flowchart LR
    CODE_OUT["Generated Code"] --> GUARD["Guardrails AI<br/>Schema Validation"]:::red
    GUARD --> LINT2["Linters<br/>black, ruff, eslint"]:::orange
    LINT2 --> SEC["Security Scan<br/>bandit, semgrep"]:::red
    SEC --> TYPE["Type Check<br/>mypy / TypeScript"]:::blue
    TYPE --> TEST2["Test Suite<br/>pytest / jest"]:::green
    TEST2 --> REVIEW["Self-Review<br/>Claude Sonnet"]:::purple

    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
    classDef purple fill:#9C27B0,color:#fff,stroke:#6A1B9A
    classDef red fill:#F44336,color:#fff,stroke:#C62828
```

---

## 5. Technology Justification

| Component | Chosen | Alternative | Why Chosen |
|-----------|--------|-------------|------------|
| **Orchestration** | LangGraph | Prefect, Airflow | Purpose-built for LLM agent state machines with conditional edges |
| **Codebase RAG** | LlamaIndex + Pinecone | LangChain + FAISS | LlamaIndex excels at document indexing; Pinecone scales to millions of vectors |
| **Code Parsing** | Tree-sitter | regex, AST module | Language-agnostic, incremental parsing, function-level chunking |
| **Code LLM** | Claude Opus + GPT-4o | DeepSeek alone | Routing by strength: Claude for planning/review, GPT-4o for generation |
| **Embeddings** | code-search-ada-002 | all-MiniLM-L6 | Purpose-built for code semantic search — 4× better retrieval on code benchmarks |
| **Sandbox** | Docker container | VM, subprocess | Lightweight isolation, reproducible, resource-limited |
| **Safety** | Guardrails AI | custom regex | Structured validation framework with retry + fix loops |
| **Fine-tuning** | QLoRA on DeepSeek-Coder | Full fine-tune | 0.1% trainable params, runs on single GPU, 97% quality of full |

---

## 6. Data Flow Summary

```mermaid
flowchart TD
    TASK["Task Input<br/>GitHub / Jira / CLI"]:::blue --> PARSE["Parse + Classify<br/>Task Router"]:::grey
    PARSE --> INDEX["Codebase RAG<br/>LlamaIndex + Pinecone"]:::purple
    INDEX --> PLAN["Planner Agent<br/>Multi-step plan"]:::purple
    PLAN --> GEN["Coder Agent<br/>Multi-file generation"]:::blue
    GEN --> SANDBOX2["Sandbox Execution<br/>Docker + Tests"]:::orange
    SANDBOX2 -->|fail| GEN
    SANDBOX2 -->|pass| REVIEW2["Review Agent<br/>Quality check"]:::green
    REVIEW2 -->|issues| GEN
    REVIEW2 -->|approved| OUTPUT2["PR + Audit Log"]:::teal

    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
    classDef purple fill:#9C27B0,color:#fff,stroke:#6A1B9A
    classDef teal fill:#009688,color:#fff,stroke:#00695C
    classDef grey fill:#546E7A,color:#fff,stroke:#37474F
```

---

## 7. Target Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Task completion rate | > 70% | Tasks completed without human intervention |
| Code quality score | > 8/10 | Automated lint + human review |
| Test pass rate | > 95% | Generated code passes existing + new tests |
| Time-to-PR | < 30 min | Task assignment to PR creation |
| Cost per task | < $2 | Total LLM API cost |
| Security vulnerabilities | 0 critical | bandit + semgrep scans |

---

## 8. GenAI Skills Matrix

| Skill | Module | Role |
|-------|--------|------|
| LangGraph | Orchestrator | Agent state machine with conditional edges |
| LangChain | Tools | Tool wrappers for file/terminal/browser access |
| CrewAI | Multi-agent | 5-agent team with role delegation |
| AutoGen | Debate | Code review discussion between agents |
| RAG | Knowledge | Codebase context retrieval |
| Advanced RAG | Knowledge | HyDE + hybrid search + cross-encoder reranking |
| LlamaIndex | Indexing | Codebase document indexing and querying |
| Embeddings | Search | code-search-ada-002 for code similarity |
| Vector DBs | Storage | Pinecone for scalable vector storage |
| OpenAI GPT | Coder | Code generation and fast tasks |
| Claude API | Planner/Reviewer | Planning (Opus) and review (Sonnet) |
| Gemini API | Tester | Fast, cheap test analysis |
| Guardrails | Safety | Output validation and constraint enforcement |
| Prompt Engineering | All agents | CoT reasoning, persona prompts |
| Few-Shot | Coder | Examples of good code patterns |
| PEFT Fine-tuning | Custom model | QLoRA on DeepSeek-Coder for domain adaptation |
| RLHF | Improvement | Self-improvement loop from human feedback |
| Transfer Learning | Model | General code model → project-specific |
| HuggingFace | Models | Model hub for open-source models |
| Keras | Training | Custom classifier training |
| NLP | Code understanding | AST analysis, entity extraction |
| Distributed Training | Scale | Multi-GPU fine-tuning |
| Model Quantization | Serving | INT8/INT4 for self-hosted models |
| Inference Engines | Serving | vLLM for fast inference |
| AWS AI/ML | Cloud | SageMaker deployment, Bedrock access |
