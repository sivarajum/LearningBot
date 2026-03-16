# Personal Learning Platform — Master Execution Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform LearningBot from a text-heavy document database into a visual-first, fast-lookup personal learning weapon with working POC demos for interview preparation.

**Architecture:** Three independent phases executed sequentially. Each phase is self-contained with its own agent context, goals, and deliverables. Phases do not share state — each starts fresh.

**Tech Stack:**
- Phase 1: Markdown (Mermaid diagrams, tables, cheat sheets)
- Phase 2: Python, FastAPI, LangChain, Docker, Streamlit
- Phase 3: Next.js 16, React 19, TypeScript, Tailwind CSS

---

## Agent Protocol (All Phases)

Each phase uses 3 parallel agents:

### Agent 1: MAKER
- **Role:** Builds the deliverable
- **Goal:** Create working, complete output for each task
- **Style:** Move fast, ship working code/content, don't over-polish

### Agent 2: REVIEWER
- **Role:** Quality gate
- **Goal:** Verify correctness, completeness, and fitness for purpose
- **Checks:** Does it work? Is it accurate? Does it match the spec? Any bugs?
- **Output:** APPROVED or ISSUES list with specific fixes needed

### Agent 3: CRITIC
- **Role:** Devil's advocate
- **Goal:** Challenge decisions, find what's missing, ensure it's actually useful
- **Checks:** Would this actually help in a 30-second lookup? Is the visual clear? Would this impress in an interview? Is this over-engineered?
- **Output:** APPROVED or CONCERNS list with specific improvements

**Workflow per task:**
```
MAKER builds → REVIEWER checks → CRITIC challenges
  ↓                ↓                    ↓
  If both APPROVED → merge as final version
  If issues found → MAKER fixes → re-review
```

---

# PHASE 1: Visual Cheatsheets (Top 30 Technologies)

## Phase 1 Context Block (Copy this for fresh agent start)

```
PHASE: 1 — Visual Cheatsheets
GOAL: Create a cheatsheet.md for each of the top 30 interview-relevant
      technologies. Each cheatsheet is a 30-second visual refresher —
      NOT a tutorial, NOT an explainer. It's what you'd glance at in
      the elevator before walking into an interview.

WHAT WE ACHIEVE: 30 cheatsheet.md files, each containing:
  - 1 architecture diagram (Mermaid) — the mental model
  - 1 comparison table — "when to use X vs Y"
  - 5 things you always forget — commands, configs, gotchas
  - 1 interview killer answer — your go-to response
  - Total: fits on one screen, scannable in 30 seconds

LOCATION: /Users/sivarajumalladi/Documents/GitHub/LearningBot/14-TechStack/
  Each cheatsheet goes into the corresponding technology folder.
  e.g., Priority-TechStack/BigQuery/cheatsheet.md

EXISTING FILES TO REFERENCE:
  - what.md (comprehensive guide — extract key points FROM this)
  - Visual.md (existing diagrams — simplify FROM these)
  - Interview.md (Q&A — pick the best ONE answer)
  - guide.md (practical patterns — pick top 5 gotchas)

AGENT ROLES:
  MAKER: Creates the cheatsheet.md files
  REVIEWER: Checks accuracy, completeness, Mermaid syntax validity
  CRITIC: Checks if it's actually useful in 30 seconds, not too verbose

FORMAT TEMPLATE:
---
# {Technology} — Cheatsheet

## Architecture (30-second mental model)
```mermaid
{simplified architecture diagram}
```

## When to use vs alternatives
| Need | Use | Not |
|------|-----|-----|
| ... | ... | ... |

## 5 things you always forget
1. ...
2. ...
3. ...
4. ...
5. ...

## Interview killer answer
> "{One paragraph that demonstrates deep understanding}"
---
```

### Target Technologies (30 total, grouped by batch)

**Batch 1: Core Data & Cloud (10)**
1. BigQuery
2. Vertex-AI
3. Apache-Spark
4. Apache-Airflow
5. Kafka
6. Docker
7. Kubernetes
8. FastAPI
9. Snowflake
10. dbt

**Batch 2: AI/ML & GenAI (10)**
11. LangChain
12. LangGraph
13. Vector-Databases
14. MLflow
15. RAG (Retrieval-Augmented Generation)
16. Prompt Engineering
17. Embeddings
18. HuggingFace
19. Fine-Tuning (PEFT/LoRA)
20. TensorFlow/PyTorch

**Batch 3: Infrastructure & Supporting (10)**
21. Streamlit
22. PostgreSQL
23. Redis
24. MongoDB
25. Terraform
26. GitHub Actions
27. GCP Cloud Run
28. GCP Pub/Sub
29. GCP Cloud Functions
30. Elasticsearch

---

### Task 1.1: Batch 1 Cheatsheets — Core Data & Cloud

**Files:**
- Create: `14-TechStack/Priority-TechStack/BigQuery/cheatsheet.md`
- Create: `14-TechStack/Priority-TechStack/Vertex-AI/cheatsheet.md`
- Create: `14-TechStack/Priority-TechStack/Apache-Spark/cheatsheet.md`
- Create: `14-TechStack/Priority-TechStack/Apache-Airflow/cheatsheet.md`
- Create: `14-TechStack/Priority-TechStack/Kafka/cheatsheet.md`
- Create: `14-TechStack/Priority-TechStack/Docker/cheatsheet.md`
- Create: `14-TechStack/Priority-TechStack/Kubernetes/cheatsheet.md`
- Create: `14-TechStack/Priority-TechStack/FastAPI/cheatsheet.md`
- Create: `14-TechStack/Priority-TechStack/Snowflake/cheatsheet.md`
- Create: `14-TechStack/dbt/cheatsheet.md`
- Reference: Each technology's `what.md`, `Visual.md`, `Interview.md`, `guide.md`

- [ ] **Step 1: MAKER — Read existing content for all 10 technologies**
  Read `what.md`, `Visual.md`, `Interview.md` for each. Extract: key architecture, top comparison, 5 gotchas, best interview answer.

- [ ] **Step 2: MAKER — Create all 10 cheatsheet.md files**
  Follow the format template exactly. Each file must:
  - Have exactly 1 Mermaid diagram (simplified, not the full Visual.md diagram)
  - Have exactly 1 comparison table (3-5 rows)
  - Have exactly 5 numbered "things you always forget"
  - Have exactly 1 interview killer answer (2-3 sentences max)
  - Be under 60 lines total

- [ ] **Step 3: REVIEWER — Validate all 10 cheatsheets**
  Check each for: Mermaid syntax correctness, factual accuracy, completeness of all 4 sections, no copy-paste from what.md (must be distilled).

- [ ] **Step 4: CRITIC — Challenge all 10 cheatsheets**
  For each, answer: Can I scan this in 30 seconds? Is the diagram the RIGHT mental model? Is the comparison table the comparison I'd actually need? Are the 5 gotchas things I'd genuinely forget (not obvious basics)?

- [ ] **Step 5: MAKER — Fix issues from Reviewer and Critic**

- [ ] **Step 6: Commit batch 1**
  ```bash
  git add 14-TechStack/Priority-TechStack/*/cheatsheet.md 14-TechStack/dbt/cheatsheet.md
  git commit -m "feat: add visual cheatsheets for 10 core data & cloud technologies"
  ```

---

### Task 1.2: Batch 2 Cheatsheets — AI/ML & GenAI

**Files:**
- Create: `14-TechStack/Priority-TechStack/LangChain/cheatsheet.md`
- Create: `14-TechStack/Priority-TechStack/LangGraph/cheatsheet.md` (if exists, else `14-TechStack/Gen-AI/LangGraph/cheatsheet.md`)
- Create: `14-TechStack/Priority-TechStack/Vector-Databases/cheatsheet.md`
- Create: `14-TechStack/Priority-TechStack/MLflow/cheatsheet.md`
- Create: `14-TechStack/RAG/cheatsheet.md`
- Create: `14-TechStack/Gen-AI/PromptEngineering/cheatsheet.md`
- Create: `14-TechStack/Gen-AI/Embeddings/cheatsheet.md`
- Create: `14-TechStack/Gen-AI/HuggingFace/cheatsheet.md`
- Create: `14-TechStack/Gen-AI/PEFT-FineTuning/cheatsheet.md`
- Create: `14-TechStack/MachineLearning/cheatsheet.md` (TensorFlow/PyTorch combined)

- [ ] **Step 1: MAKER — Read existing content for all 10 technologies**
- [ ] **Step 2: MAKER — Create all 10 cheatsheet.md files**
- [ ] **Step 3: REVIEWER — Validate all 10 cheatsheets**
- [ ] **Step 4: CRITIC — Challenge all 10 cheatsheets**
- [ ] **Step 5: MAKER — Fix issues from Reviewer and Critic**
- [ ] **Step 6: Commit batch 2**
  ```bash
  git commit -m "feat: add visual cheatsheets for 10 AI/ML & GenAI technologies"
  ```

---

### Task 1.3: Batch 3 Cheatsheets — Infrastructure & Supporting

**Files:**
- Create: `14-TechStack/Priority-TechStack/Streamlit/cheatsheet.md`
- Create: `14-TechStack/Databases/PostgreSQL/cheatsheet.md` (or wherever PostgreSQL lives)
- Create: `14-TechStack/Databases/Redis/cheatsheet.md`
- Create: `14-TechStack/Databases/MongoDB/cheatsheet.md`
- Create: `14-TechStack/DevOps/Terraform/cheatsheet.md`
- Create: `14-TechStack/DevOps/GitHubActions/cheatsheet.md`
- Create: `14-TechStack/GCP/Cloud-Run/cheatsheet.md`
- Create: `14-TechStack/GCP/PubSub/cheatsheet.md`
- Create: `14-TechStack/GCP/Cloud-Functions/cheatsheet.md`
- Create: `14-TechStack/Databases/Elasticsearch/cheatsheet.md`

- [ ] **Step 1: MAKER — Read existing content for all 10 technologies**
- [ ] **Step 2: MAKER — Create all 10 cheatsheet.md files**
- [ ] **Step 3: REVIEWER — Validate all 10 cheatsheets**
- [ ] **Step 4: CRITIC — Challenge all 10 cheatsheets**
- [ ] **Step 5: MAKER — Fix issues from Reviewer and Critic**
- [ ] **Step 6: Commit batch 3**
  ```bash
  git commit -m "feat: add visual cheatsheets for 10 infrastructure & supporting technologies"
  ```

---

# PHASE 2: Working POCs (3 Deployable Projects)

## Phase 2 Context Block (Copy this for fresh agent start)

```
PHASE: 2 — Working POCs
GOAL: Build 3 fully functional, deployable proof-of-concept projects
      that can be demoed live in interviews. Each must go from
      `docker-compose up` to working demo in under 60 seconds.

WHAT WE ACHIEVE:
  - POC-01: Churn Prediction — end-to-end ML pipeline with FastAPI + Streamlit
  - POC-02: RAG System — document Q&A with LangChain + vector DB
  - POC-05: LLM Agent Orchestration — multi-agent system with LangGraph

LOCATION: /Users/sivarajumalladi/Documents/GitHub/LearningBot/POCs/

EXISTING DOCS TO REFERENCE:
  - POC-01: POCs/POC-01-Intelligent-Churn-Prediction/README.md
  - POC-02: POCs/POC-02-Enterprise-RAG-System/README.md
  - POC-05: POCs/POC-05-LLM-Agent-Orchestration/README.md
  These contain complete architecture diagrams and component specs.
  Build the code to match the documented architecture.

CONSTRAINTS:
  - Each POC must run with `docker-compose up` (no cloud dependencies for demo)
  - Use SQLite/local files instead of BigQuery/cloud DBs for local demo
  - Use open-source/free models where possible (avoid API key requirements for core demo)
  - Include sample data so demo works out of the box
  - Clean, readable code — interviewer will read it

AGENT ROLES:
  MAKER: Writes all source code, Dockerfiles, docker-compose.yml
  REVIEWER: Tests that it builds, runs, and produces correct output
  CRITIC: Challenges architecture decisions, code quality, interview-readiness
```

### Task 2.1: POC-02 — Enterprise RAG System (Build First — Most Interview-Relevant)

**Files:**
- Create: `POCs/POC-02-Enterprise-RAG-System/src/main.py` — FastAPI server
- Create: `POCs/POC-02-Enterprise-RAG-System/src/rag_pipeline.py` — RAG core logic
- Create: `POCs/POC-02-Enterprise-RAG-System/src/embeddings.py` — Embedding + vector store
- Create: `POCs/POC-02-Enterprise-RAG-System/src/document_loader.py` — Document ingestion
- Create: `POCs/POC-02-Enterprise-RAG-System/src/ui.py` — Streamlit frontend
- Create: `POCs/POC-02-Enterprise-RAG-System/requirements.txt`
- Create: `POCs/POC-02-Enterprise-RAG-System/Dockerfile`
- Create: `POCs/POC-02-Enterprise-RAG-System/docker-compose.yml`
- Create: `POCs/POC-02-Enterprise-RAG-System/sample_docs/` — 5-10 sample markdown docs
- Create: `POCs/POC-02-Enterprise-RAG-System/.env.example`
- Reference: `POCs/POC-02-Enterprise-RAG-System/README.md` (existing architecture)

- [ ] **Step 1: MAKER — Create project structure and requirements.txt**
  ```
  langchain>=0.2.0
  langchain-community>=0.2.0
  langchain-openai>=0.1.0
  chromadb>=0.4.0
  sentence-transformers>=2.0.0
  fastapi>=0.110.0
  uvicorn>=0.27.0
  streamlit>=1.30.0
  python-dotenv>=1.0.0
  python-multipart>=0.0.9
  ```

- [ ] **Step 2: MAKER — Implement document_loader.py**
  Load markdown/text/PDF documents, split into chunks (RecursiveCharacterTextSplitter), return Document objects.

- [ ] **Step 3: MAKER — Implement embeddings.py**
  Initialize ChromaDB local persistent store. Embed documents using sentence-transformers (all-MiniLM-L6-v2 — free, no API key). Provide similarity_search method.

- [ ] **Step 4: MAKER — Implement rag_pipeline.py**
  RetrievalQA chain: query → retrieve top-k chunks → format prompt → generate answer. Support both OpenAI (if key provided) and a fallback local response mode for demo without API keys.

- [ ] **Step 5: MAKER — Implement main.py (FastAPI)**
  Endpoints:
  - `POST /ingest` — upload and index documents
  - `POST /query` — ask a question, get RAG answer with sources
  - `GET /health` — health check
  - `GET /stats` — document count, chunk count

- [ ] **Step 6: MAKER — Implement ui.py (Streamlit)**
  - Document upload sidebar
  - Chat-style Q&A interface
  - Shows retrieved source chunks
  - Displays similarity scores

- [ ] **Step 7: MAKER — Create sample_docs/**
  Use 5-10 of the existing LearningBot markdown files as sample documents (e.g., BigQuery what.md, LangChain what.md). This makes the demo self-referential and interesting.

- [ ] **Step 8: MAKER — Create Dockerfile and docker-compose.yml**
  ```yaml
  services:
    api:
      build: .
      ports: ["8000:8000"]
      volumes: ["./data:/app/data"]
    ui:
      build: .
      command: streamlit run src/ui.py --server.port 8501
      ports: ["8501:8501"]
  ```

- [ ] **Step 9: REVIEWER — Build and run, verify all endpoints work**
  ```bash
  cd POCs/POC-02-Enterprise-RAG-System
  docker-compose up --build
  # Test: curl http://localhost:8000/health
  # Test: upload sample doc via /ingest
  # Test: query via /query
  # Test: open http://localhost:8501 for Streamlit UI
  ```

- [ ] **Step 10: CRITIC — Review for interview readiness**
  Can you walk through this code with an interviewer? Is the architecture clean? Are there obvious anti-patterns? Would you be proud showing this?

- [ ] **Step 11: MAKER — Fix issues, final commit**
  ```bash
  git add POCs/POC-02-Enterprise-RAG-System/
  git commit -m "feat: POC-02 Enterprise RAG System — working implementation"
  ```

---

### Task 2.2: POC-01 — Intelligent Churn Prediction System

**Files:**
- Create: `POCs/POC-01-Intelligent-Churn-Prediction/src/data_generator.py` — Synthetic customer data
- Create: `POCs/POC-01-Intelligent-Churn-Prediction/src/feature_engineering.py` — Feature pipeline
- Create: `POCs/POC-01-Intelligent-Churn-Prediction/src/model.py` — Train/predict (scikit-learn + XGBoost)
- Create: `POCs/POC-01-Intelligent-Churn-Prediction/src/api.py` — FastAPI prediction server
- Create: `POCs/POC-01-Intelligent-Churn-Prediction/src/ui.py` — Streamlit dashboard
- Create: `POCs/POC-01-Intelligent-Churn-Prediction/src/pipeline.py` — End-to-end orchestration
- Create: `POCs/POC-01-Intelligent-Churn-Prediction/requirements.txt`
- Create: `POCs/POC-01-Intelligent-Churn-Prediction/Dockerfile`
- Create: `POCs/POC-01-Intelligent-Churn-Prediction/docker-compose.yml`
- Create: `POCs/POC-01-Intelligent-Churn-Prediction/data/sample_customers.csv`
- Reference: `POCs/POC-01-Intelligent-Churn-Prediction/README.md`

- [ ] **Step 1: MAKER — Create data_generator.py**
  Generate 10,000 synthetic customers with: tenure, monthly_charges, total_charges, contract_type, payment_method, num_support_tickets, internet_service, churn_label. Realistic distributions.

- [ ] **Step 2: MAKER — Create feature_engineering.py**
  Feature pipeline: handle missing values, encode categoricals, create derived features (avg_monthly_spend, tenure_bucket, support_ticket_rate), normalize numerics. Return feature matrix + labels.

- [ ] **Step 3: MAKER — Create model.py**
  Train XGBoost classifier. Include: train/test split, cross-validation, feature importance, classification report, confusion matrix. Save model with joblib. Prediction method returns probability + explanation (top contributing features via SHAP or feature importance).

- [ ] **Step 4: MAKER — Create api.py (FastAPI)**
  Endpoints:
  - `POST /predict` — single customer prediction with explanation
  - `POST /batch-predict` — batch predictions
  - `GET /model-info` — accuracy, feature importance, training date
  - `GET /health`

- [ ] **Step 5: MAKER — Create ui.py (Streamlit)**
  - Dashboard with model metrics (accuracy, precision, recall, F1)
  - Feature importance chart
  - Individual prediction form (input customer features → get churn risk)
  - Batch upload CSV → predictions table
  - Confusion matrix visualization

- [ ] **Step 6: MAKER — Create pipeline.py**
  End-to-end: generate data → engineer features → train model → save model → start API. Demonstrates pipeline orchestration pattern.

- [ ] **Step 7: MAKER — Create Docker + docker-compose**
- [ ] **Step 8: REVIEWER — Build, run, verify predictions are reasonable**
- [ ] **Step 9: CRITIC — Review for interview readiness**
- [ ] **Step 10: MAKER — Fix issues, final commit**
  ```bash
  git add POCs/POC-01-Intelligent-Churn-Prediction/
  git commit -m "feat: POC-01 Churn Prediction — working ML pipeline with API + dashboard"
  ```

---

### Task 2.3: POC-05 — LLM Agent Orchestration System

**Files:**
- Create: `POCs/POC-05-LLM-Agent-Orchestration/src/orchestrator.py` — LangGraph state machine
- Create: `POCs/POC-05-LLM-Agent-Orchestration/src/agents/researcher.py` — Research agent
- Create: `POCs/POC-05-LLM-Agent-Orchestration/src/agents/writer.py` — Writer agent
- Create: `POCs/POC-05-LLM-Agent-Orchestration/src/agents/reviewer.py` — Reviewer agent
- Create: `POCs/POC-05-LLM-Agent-Orchestration/src/tools/search.py` — Search tool
- Create: `POCs/POC-05-LLM-Agent-Orchestration/src/tools/calculator.py` — Calculator tool
- Create: `POCs/POC-05-LLM-Agent-Orchestration/src/api.py` — FastAPI server
- Create: `POCs/POC-05-LLM-Agent-Orchestration/src/ui.py` — Streamlit UI with agent flow visualization
- Create: `POCs/POC-05-LLM-Agent-Orchestration/requirements.txt`
- Create: `POCs/POC-05-LLM-Agent-Orchestration/Dockerfile`
- Create: `POCs/POC-05-LLM-Agent-Orchestration/docker-compose.yml`
- Reference: `POCs/POC-05-LLM-Agent-Orchestration/README.md`

- [ ] **Step 1: MAKER — Define state schema and agent interfaces**
  LangGraph TypedDict state: messages, current_agent, research_results, draft_content, review_feedback, iteration_count, status.

- [ ] **Step 2: MAKER — Implement tools (search, calculator)**
  Search tool: uses DuckDuckGo search (free, no API key). Calculator: evaluates math expressions safely.

- [ ] **Step 3: MAKER — Implement researcher agent**
  Takes a topic → uses search tool → summarizes findings → returns structured research output.

- [ ] **Step 4: MAKER — Implement writer agent**
  Takes research → writes structured content (article, report, analysis). Uses LLM for generation.

- [ ] **Step 5: MAKER — Implement reviewer agent**
  Takes draft → evaluates quality, accuracy, completeness → returns feedback or approval.

- [ ] **Step 6: MAKER — Implement orchestrator (LangGraph)**
  State machine: START → researcher → writer → reviewer → (if feedback) → writer → reviewer → END. Max 3 iterations. Conditional edges based on review score.

- [ ] **Step 7: MAKER — Implement API + UI**
  API: POST /run with topic, GET /status/{run_id}. UI: input topic, show agent flow in real-time (which agent is active, intermediate outputs).

- [ ] **Step 8: MAKER — Create Docker + docker-compose**
- [ ] **Step 9: REVIEWER — Build, run, verify agent flow executes correctly**
- [ ] **Step 10: CRITIC — Review for interview readiness**
- [ ] **Step 11: MAKER — Fix issues, final commit**
  ```bash
  git add POCs/POC-05-LLM-Agent-Orchestration/
  git commit -m "feat: POC-05 LLM Agent Orchestration — working multi-agent system with LangGraph"
  ```

---

# PHASE 3: Enhanced Local Viewer

## Phase 3 Context Block (Copy this for fresh agent start)

```
PHASE: 3 — Enhanced Local Viewer
GOAL: Upgrade the existing Next.js learning-viewer to be a fast,
      keyboard-driven personal lookup tool optimized for speed and visuals.

WHAT WE ACHIEVE:
  - Cmd+K global search across all 903 files (fuzzy, instant)
  - Visual mode toggle (shows only diagrams + tables + cheatsheets)
  - Favorites/pins (top 20 topics pinned to sidebar)
  - Cheatsheet-first view (cheatsheet.md shown before what.md)
  - Table of Contents sidebar (already built, just needs wiring)

LOCATION: /Users/sivarajumalladi/Documents/GitHub/LearningBot/learning-viewer/

EXISTING APP STATE:
  - Next.js 16 + React 19 + Tailwind CSS 4
  - Working folder explorer with file tree (Explorer.tsx, 355 lines)
  - Markdown renderer with Mermaid diagrams (MarkdownRenderer.tsx, 139 lines)
  - Content tree crawler with caching (content-tree.ts)
  - API routes: /api/tree, /api/content
  - TableOfContents component EXISTS but is NOT wired into the UI
  - Search: filename-only filter in sidebar (no full-text search)
  - Build: SUCCEEDS, dev server works at localhost:3000
  - Dark theme only

KEY FILES:
  - src/components/Explorer.tsx — main UI, modify for Cmd+K + favorites + visual mode
  - src/components/MarkdownRenderer.tsx — modify for visual mode filtering
  - src/components/TableOfContents.tsx — wire into main UI
  - src/lib/content-tree.ts — extend for full-text search indexing
  - src/lib/types.ts — add types for favorites, search results
  - src/app/api/ — add search API route

AGENT ROLES:
  MAKER: Implements the features in TypeScript/React
  REVIEWER: Tests that the app builds, features work, no regressions
  CRITIC: Tests UX — is Cmd+K truly instant? Is visual mode useful? Would you actually use this daily?
```

### Task 3.1: Cmd+K Global Search

**Files:**
- Create: `learning-viewer/src/components/SearchModal.tsx` — Cmd+K modal with fuzzy search
- Create: `learning-viewer/src/app/api/search/route.ts` — Full-text search API
- Modify: `learning-viewer/src/lib/content-tree.ts` — Add search index building
- Modify: `learning-viewer/src/lib/types.ts` — Add SearchResult type
- Modify: `learning-viewer/src/components/Explorer.tsx` — Add Cmd+K listener, integrate modal

- [ ] **Step 1: MAKER — Add SearchResult type to types.ts**
  ```typescript
  export interface SearchResult {
    path: string;
    name: string;
    breadcrumbs: string[];
    matchType: 'filename' | 'heading' | 'content';
    matchContext: string; // surrounding text snippet
    score: number;
  }
  ```

- [ ] **Step 2: MAKER — Add search index to content-tree.ts**
  Build an in-memory index: for each .md file, extract filename, h1/h2/h3 headings, and first 500 chars of content. Cache alongside the tree. Fuzzy match against query using simple substring + heading priority scoring.

- [ ] **Step 3: MAKER — Create search API route**
  `GET /api/search?q=bigquery&limit=10` → returns top-N SearchResult[]. Priority: filename match > heading match > content match. Case-insensitive.

- [ ] **Step 4: MAKER — Create SearchModal.tsx**
  - Opens on Cmd+K (Mac) / Ctrl+K (Windows)
  - Input field with instant results as you type (debounced 150ms)
  - Results show: icon (file/heading), name, breadcrumbs, match context snippet
  - Arrow keys navigate, Enter selects, Escape closes
  - Styled: dark overlay, centered modal, tailwind

- [ ] **Step 5: MAKER — Wire into Explorer.tsx**
  Add global keydown listener for Cmd+K. On result select, set selectedPath and close modal.

- [ ] **Step 6: REVIEWER — Test search works**
  Start dev server, press Cmd+K, type "bigquery", verify results show BigQuery files with context. Test edge cases: empty query, no results, special characters.

- [ ] **Step 7: CRITIC — Test speed and usefulness**
  Is it instant (<200ms)? Do the right files show up first? Is the modal UI clean and keyboard-navigable? Would you use this over the sidebar filter?

- [ ] **Step 8: MAKER — Fix issues, commit**
  ```bash
  git commit -m "feat: add Cmd+K global search with fuzzy matching"
  ```

---

### Task 3.2: Visual Mode Toggle

**Files:**
- Create: `learning-viewer/src/components/VisualModeRenderer.tsx` — Strips text, shows only diagrams + tables + cheatsheet sections
- Modify: `learning-viewer/src/components/Explorer.tsx` — Add visual mode toggle button
- Modify: `learning-viewer/src/components/MarkdownRenderer.tsx` — Support visual mode prop

- [ ] **Step 1: MAKER — Create VisualModeRenderer.tsx**
  Parse markdown content and extract ONLY:
  - Mermaid code blocks → render as diagrams
  - Tables (markdown tables) → render as tables
  - Headings that precede the above → render as section headers
  - "cheatsheet" or "## 5 things" or "## Interview killer" sections → render fully
  Everything else: hidden.

- [ ] **Step 2: MAKER — Add toggle to Explorer.tsx**
  Toggle button in the content header: "Visual" / "Full" mode. Icon: Eye / EyeOff from Lucide. Persisted in localStorage.

- [ ] **Step 3: MAKER — Pass visualMode prop to renderer**
  When visual mode is ON, use VisualModeRenderer. When OFF, use existing MarkdownRenderer.

- [ ] **Step 4: REVIEWER — Test visual mode**
  Open a content-heavy file (BigQuery Visual.md). Toggle visual mode. Verify: only diagrams and tables show. Toggle back: full content returns.

- [ ] **Step 5: CRITIC — Is this actually useful?**
  Does visual mode show the RIGHT things? Is anything important hidden? Would you actually use this toggle?

- [ ] **Step 6: MAKER — Fix issues, commit**
  ```bash
  git commit -m "feat: add visual mode toggle — shows only diagrams, tables, and cheatsheets"
  ```

---

### Task 3.3: Favorites/Pins + Cheatsheet-First View

**Files:**
- Modify: `learning-viewer/src/components/Explorer.tsx` — Add favorites section to sidebar
- Modify: `learning-viewer/src/lib/types.ts` — Add favorites types
- Modify: `learning-viewer/src/lib/content-tree.ts` — Detect cheatsheet.md files, prioritize in tree

- [ ] **Step 1: MAKER — Add favorites to Explorer.tsx**
  - Star icon next to each file in the tree
  - "Favorites" section pinned to top of sidebar (above tree)
  - Stored in localStorage (no backend needed)
  - Max 20 favorites

- [ ] **Step 2: MAKER — Cheatsheet-first ordering**
  In the file tree, if a folder has `cheatsheet.md`, show it FIRST in that folder's file list (before guide.md, what.md, etc.). Visual indicator: lightning bolt icon.

- [ ] **Step 3: MAKER — Auto-open cheatsheet on folder click**
  When user clicks a folder name (not expand arrow), auto-select its cheatsheet.md if it exists. This means one click → cheatsheet view.

- [ ] **Step 4: REVIEWER — Test favorites persist across reloads**
- [ ] **Step 5: CRITIC — Is the UX intuitive?**
- [ ] **Step 6: MAKER — Fix issues, commit**
  ```bash
  git commit -m "feat: add favorites, cheatsheet-first ordering, and auto-open"
  ```

---

### Task 3.4: Wire Table of Contents Sidebar

**Files:**
- Modify: `learning-viewer/src/components/Explorer.tsx` — Add right sidebar for TOC
- Modify: `learning-viewer/src/components/TableOfContents.tsx` — Minor adjustments if needed

- [ ] **Step 1: MAKER — Add TOC to Explorer layout**
  Three-pane layout: [sidebar | content | TOC]. TOC sidebar: 200px, collapsible. Shows for files with 3+ headings, auto-hides for short files.

- [ ] **Step 2: MAKER — Wire TOC to content**
  Pass current markdown content to TableOfContents component. Click heading → smooth scroll. Active heading highlighted as user scrolls.

- [ ] **Step 3: REVIEWER — Test TOC with various files**
- [ ] **Step 4: CRITIC — Does this add value or just clutter?**
- [ ] **Step 5: MAKER — Fix issues, commit**
  ```bash
  git commit -m "feat: wire table of contents sidebar for content navigation"
  ```

---

# Execution Summary

| Phase | Tasks | Deliverables | Est. Effort |
|-------|-------|-------------|-------------|
| **Phase 1** | 3 batches × 10 cheatsheets | 30 cheatsheet.md files | 2-3 hours |
| **Phase 2** | 3 POCs | 3 working, dockerized applications | 6-10 hours |
| **Phase 3** | 4 viewer features | Enhanced Next.js viewer | 3-4 hours |

**Total: 11-17 hours of focused work**

**Execution order:** Phase 1 → Phase 2 → Phase 3 (each phase starts fresh with its context block)

**Phase transition protocol:**
1. Complete all tasks in current phase
2. Commit all changes
3. Clear agent context
4. Start new phase with the Phase Context Block copied into the fresh agent
5. Agents reference ONLY the context block + files listed — no prior phase memory needed
