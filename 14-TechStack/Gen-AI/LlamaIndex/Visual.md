# LlamaIndex: Visual Guide & Architecture Diagrams

## Table of Contents
1. [Ecosystem Overview](#ecosystem-overview)
2. [RAG Pipeline Architecture](#rag-pipeline-architecture)
3. [Index Types Comparison](#index-types-comparison)
4. [Query Engine vs Chat Engine](#query-engine-vs-chat-engine)
5. [Agent Architecture](#agent-architecture)
6. [Workflow Event-Driven Architecture](#workflow-event-driven-architecture)
7. [LlamaIndex vs LangChain Comparison](#llamaindex-vs-langchain-comparison)
8. [Data Connector Ecosystem](#data-connector-ecosystem)
9. [Production Deployment](#production-deployment)
10. [Learning Path](#learning-path)

---

## Ecosystem Overview

### LlamaIndex Complete Ecosystem

```mermaid
graph TD
    A["User Application"] --> B["LlamaIndex Framework"]

    B --> C["Data Layer"]
    C --> C1["Data Connectors<br/>(LlamaHub 300+)"]
    C --> C2["Document Loaders"]
    C --> C3["Node Parsers"]
    C --> C4["Text Splitters"]

    B --> D["Index Layer"]
    D --> D1["VectorStoreIndex"]
    D --> D2["SummaryIndex"]
    D --> D3["TreeIndex"]
    D --> D4["KeywordTableIndex"]
    D --> D5["KnowledgeGraphIndex"]

    B --> E["Query Layer"]
    E --> E1["Query Engine"]
    E --> E2["Chat Engine"]
    E --> E3["Retriever"]
    E --> E4["Response Synthesizer"]
    E --> E5["Router Query Engine"]

    B --> F["Agent Layer"]
    F --> F1["ReAct Agent"]
    F --> F2["OpenAI Agent"]
    F --> F3["Function Calling"]
    F --> F4["Multi-Agent"]

    B --> G["Orchestration"]
    G --> G1["Workflows"]
    G --> G2["Events"]
    G --> G3["Steps"]
    G --> G4["Streaming"]

    B --> H["Production"]
    H --> H1["LlamaCloud"]
    H --> H2["LlamaParse"]
    H --> H3["LlamaExtract"]
    H --> H4["Observability"]

    style A fill:#E8F4F8
    style B fill:#7C3AED,color:#fff
    style C fill:#FF6B6B
    style D fill:#4ECDC4
    style E fill:#45B7D1
    style F fill:#FFEAA7
    style G fill:#96CEB4
    style H fill:#DDA15E
```

### Core Component Relationship Map

```mermaid
graph TB
    DOCS["Documents<br/>(Raw Data)"] --> PARSER["Node Parser<br/>(Chunking)"]
    PARSER --> NODES["Nodes<br/>(Chunks + Metadata)"]
    NODES --> INDEX["Index<br/>(Organization)"]
    INDEX --> RETRIEVER["Retriever<br/>(Search)"]
    RETRIEVER --> SYNTHESIZER["Response Synthesizer<br/>(Generation)"]

    LLM["LLM<br/>(GPT-4, Claude, Llama)"] --> SYNTHESIZER
    LLM --> AGENT["Agent<br/>(Reasoning)"]
    EMBED["Embedding Model<br/>(OpenAI, HuggingFace)"] --> INDEX
    EMBED --> RETRIEVER

    TOOLS["Tools<br/>(Query Engines, APIs)"] --> AGENT
    MEMORY["Memory<br/>(Chat History)"] --> AGENT
    RETRIEVER --> AGENT

    AGENT --> RESPONSE["Response"]
    SYNTHESIZER --> RESPONSE

    style DOCS fill:#FF6B6B
    style PARSER fill:#FF6B6B
    style NODES fill:#FF6B6B
    style INDEX fill:#4ECDC4
    style RETRIEVER fill:#45B7D1
    style SYNTHESIZER fill:#45B7D1
    style LLM fill:#FFEAA7
    style EMBED fill:#FFEAA7
    style AGENT fill:#B4A7D6
    style TOOLS fill:#96CEB4
    style MEMORY fill:#96CEB4
    style RESPONSE fill:#E8F4F8
```

---

## RAG Pipeline Architecture

### Full RAG Pipeline (Load → Parse → Index → Retrieve → Generate)

```mermaid
sequenceDiagram
    participant Source as Data Source
    participant Loader as Document Loader
    participant Parser as Node Parser
    participant Embed as Embedding Model
    participant VectorDB as Vector Store
    participant Index as VectorStoreIndex
    participant Retriever as Retriever
    participant LLM as LLM
    participant Synth as Response Synthesizer
    participant User as User

    Note over Source,User: === INGESTION PHASE ===
    Source ->> Loader: Load raw data (PDF, web, DB)
    Loader ->> Loader: Create Document objects
    Loader ->> Parser: Raw documents
    Parser ->> Parser: Split into Nodes (chunks)
    Parser ->> Embed: Node text content
    Embed ->> Embed: Generate embeddings
    Embed ->> VectorDB: Store vectors + metadata
    VectorDB ->> Index: Build index structure

    Note over Source,User: === QUERY PHASE ===
    User ->> Index: Natural language query
    Index ->> Embed: Embed query
    Embed ->> VectorDB: Similarity search
    VectorDB ->> Retriever: Top-K relevant nodes
    Retriever ->> Synth: Retrieved context + query
    Synth ->> LLM: Prompt with context
    LLM ->> Synth: Generated response
    Synth ->> User: Final answer with sources
```

### RAG Pipeline Stages Detail

```mermaid
graph LR
    subgraph LOAD["1. Load"]
        L1["SimpleDirectoryReader"]
        L2["LlamaHub Connectors"]
        L3["DatabaseReader"]
        L4["APIReader"]
        L5["LlamaParse (PDFs)"]
    end

    subgraph PARSE["2. Parse"]
        P1["SentenceSplitter"]
        P2["TokenTextSplitter"]
        P3["SemanticSplitter"]
        P4["HierarchicalNodeParser"]
        P5["Metadata Extraction"]
    end

    subgraph INDEX["3. Index"]
        I1["VectorStoreIndex"]
        I2["SummaryIndex"]
        I3["TreeIndex"]
        I4["KeywordTableIndex"]
        I5["KnowledgeGraphIndex"]
    end

    subgraph RETRIEVE["4. Retrieve"]
        R1["Top-K Similarity"]
        R2["MMR (Max Marginal)"]
        R3["Auto-Merging"]
        R4["Recursive Retrieval"]
        R5["Fusion Retrieval"]
    end

    subgraph GENERATE["5. Generate"]
        G1["Compact Synthesizer"]
        G2["Tree Summarize"]
        G3["Refine"]
        G4["Simple Summarize"]
        G5["Accumulate"]
    end

    LOAD --> PARSE --> INDEX --> RETRIEVE --> GENERATE

    style LOAD fill:#FF6B6B,color:#fff
    style PARSE fill:#E17055,color:#fff
    style INDEX fill:#4ECDC4,color:#fff
    style RETRIEVE fill:#45B7D1,color:#fff
    style GENERATE fill:#96CEB4,color:#fff
```

### Advanced RAG Patterns

```mermaid
graph TD
    subgraph NAIVE["Naive RAG"]
        N1["Query"] --> N2["Retrieve Top-K"]
        N2 --> N3["Stuff into Prompt"]
        N3 --> N4["Generate Answer"]
    end

    subgraph ADVANCED["Advanced RAG"]
        A1["Query"] --> A2["Query Transformation"]
        A2 --> A3["HyDE / Sub-Questions"]
        A3 --> A4["Multi-Index Retrieval"]
        A4 --> A5["Reranking (Cohere, Cross-Encoder)"]
        A5 --> A6["Context Compression"]
        A6 --> A7["Generate with Citations"]
    end

    subgraph MODULAR["Modular RAG"]
        M1["Query"] --> M2["Route to Best Index"]
        M2 --> M3["Recursive Retrieval"]
        M3 --> M4["Auto-Merging Nodes"]
        M4 --> M5["Sentence Window Retrieval"]
        M5 --> M6["Agentic Synthesis"]
    end

    style NAIVE fill:#FF6B6B,color:#fff
    style ADVANCED fill:#4ECDC4,color:#fff
    style MODULAR fill:#7C3AED,color:#fff
```

---

## Index Types Comparison

### Index Types Architecture

```mermaid
graph TD
    subgraph VS["VectorStoreIndex"]
        VS1["Documents"] --> VS2["Embeddings"]
        VS2 --> VS3["Vector Store<br/>(Pinecone, Chroma, Weaviate)"]
        VS3 --> VS4["Similarity Search"]
        VS4 --> VS5["Top-K Nodes"]
    end

    subgraph SI["SummaryIndex (List)"]
        SI1["Documents"] --> SI2["Sequential Nodes"]
        SI2 --> SI3["Iterate All Nodes"]
        SI3 --> SI4["Summarize Each"]
        SI4 --> SI5["Combine Summaries"]
    end

    subgraph TI["TreeIndex"]
        TI1["Leaf Nodes<br/>(Chunks)"] --> TI2["Parent Summaries"]
        TI2 --> TI3["Root Summary"]
        TI3 --> TI4["Top-Down Traversal"]
        TI4 --> TI5["Select Best Branch"]
    end

    subgraph KW["KeywordTableIndex"]
        KW1["Documents"] --> KW2["Extract Keywords<br/>(LLM or Regex)"]
        KW2 --> KW3["Keyword → Node Map"]
        KW3 --> KW4["Keyword Match"]
        KW4 --> KW5["Relevant Nodes"]
    end

    subgraph KG["KnowledgeGraphIndex"]
        KG1["Documents"] --> KG2["Extract Triplets<br/>(Subject, Predicate, Object)"]
        KG2 --> KG3["Build Graph"]
        KG3 --> KG4["Graph Traversal"]
        KG4 --> KG5["Related Entities"]
    end

    style VS fill:#4ECDC4,color:#fff
    style SI fill:#FF6B6B,color:#fff
    style TI fill:#45B7D1,color:#fff
    style KW fill:#FFEAA7
    style KG fill:#B4A7D6
```

### Index Selection Decision Tree

```mermaid
graph TD
    START["What's your use case?"] --> Q1{"Need semantic<br/>similarity search?"}

    Q1 -->|Yes| Q2{"Large or small<br/>corpus?"}
    Q1 -->|No| Q3{"Need full-text<br/>analysis?"}

    Q2 -->|Large| VS["VectorStoreIndex<br/>✅ Best for scale<br/>✅ Fast retrieval<br/>⚠️ Embedding cost"]
    Q2 -->|Small| Q4{"Budget for<br/>embeddings?"}

    Q4 -->|Yes| VS
    Q4 -->|No| SI["SummaryIndex<br/>✅ No embeddings<br/>✅ Complete coverage<br/>⚠️ Slow for large docs"]

    Q3 -->|Yes| SI
    Q3 -->|No| Q5{"Hierarchical<br/>content?"}

    Q5 -->|Yes| TI["TreeIndex<br/>✅ Efficient traversal<br/>✅ Multi-level summary<br/>⚠️ Build cost"]
    Q5 -->|No| Q6{"Keyword-based<br/>lookup?"}

    Q6 -->|Yes| KW["KeywordTableIndex<br/>✅ Fast keyword match<br/>✅ Lightweight<br/>⚠️ No semantics"]
    Q6 -->|No| KG["KnowledgeGraphIndex<br/>✅ Entity relationships<br/>✅ Reasoning<br/>⚠️ Complex setup"]

    style START fill:#7C3AED,color:#fff
    style VS fill:#4ECDC4,color:#fff
    style SI fill:#FF6B6B,color:#fff
    style TI fill:#45B7D1,color:#fff
    style KW fill:#FFEAA7
    style KG fill:#B4A7D6
```

### Index Type Comparison Matrix

| Feature | VectorStore | Summary | Tree | Keyword | KnowledgeGraph |
|---------|:-----------:|:-------:|:----:|:-------:|:--------------:|
| **Speed (Query)** | ⚡ Fast | 🐢 Slow | ⚡ Fast | ⚡ Fast | 🔄 Medium |
| **Speed (Build)** | 🔄 Medium | ⚡ Fast | 🐢 Slow | ⚡ Fast | 🐢 Slow |
| **Semantic Search** | ✅ Yes | ❌ No | ✅ Partial | ❌ No | ✅ Partial |
| **Full Coverage** | ❌ Top-K only | ✅ All nodes | ✅ Traversal | ❌ Keyword match | 🔄 Partial |
| **Embedding Cost** | 💰 High | 💚 Free | 💰 Medium | 💚 Free | 💰 Medium |
| **Best For** | General RAG | Summarization | Hierarchical docs | FAQ/Lookup | Entity relations |
| **Scalability** | ✅ Excellent | ⚠️ Linear | ✅ Good | ✅ Good | ⚠️ Complex |

---

## Query Engine vs Chat Engine

### Query Engine Flow

```mermaid
sequenceDiagram
    participant User
    participant QE as Query Engine
    participant Retriever as Retriever
    participant Synth as Response Synthesizer
    participant LLM as LLM

    User ->> QE: "What is the revenue for Q3?"
    QE ->> Retriever: Find relevant nodes
    Retriever ->> Retriever: Similarity search
    Retriever ->> QE: Top-K nodes

    QE ->> Synth: Nodes + Query
    Synth ->> LLM: Prompt with context
    LLM ->> Synth: Raw response
    Synth ->> QE: Structured response
    QE ->> User: Answer + source nodes

    Note over User,LLM: Single turn - no memory
```

### Chat Engine Flow

```mermaid
sequenceDiagram
    participant User
    participant CE as Chat Engine
    participant Memory as Chat Memory
    participant QE as Query Engine
    participant LLM as LLM

    User ->> CE: "Tell me about Q3 revenue"
    CE ->> Memory: Load chat history
    Memory ->> CE: Previous messages
    CE ->> CE: Condense question with history
    CE ->> QE: Standalone query
    QE ->> LLM: Retrieve + Generate
    LLM ->> CE: Response
    CE ->> Memory: Save exchange
    CE ->> User: "Q3 revenue was $2.5B..."

    User ->> CE: "How does it compare to Q2?"
    CE ->> Memory: Load chat history
    Memory ->> CE: [Q3 revenue context]
    CE ->> CE: Condense: "Compare Q3 vs Q2 revenue"
    CE ->> QE: Standalone query
    QE ->> LLM: Retrieve + Generate
    LLM ->> CE: Response
    CE ->> Memory: Save exchange
    CE ->> User: "Q3 was 15% higher than Q2..."

    Note over User,LLM: Multi-turn with memory
```

### Chat Engine Modes

```mermaid
graph TD
    CE["Chat Engine"] --> M1["CondenseQuestion Mode"]
    CE --> M2["ContextChat Mode"]
    CE --> M3["ReAct Mode"]
    CE --> M4["SimpleChatEngine"]

    M1 --> M1D["Condenses follow-up question<br/>using chat history into<br/>standalone query → Query Engine"]
    M2 --> M2D["Retrieves context every turn<br/>Prepends to system prompt<br/>Most common for RAG chat"]
    M3 --> M3D["Uses ReAct agent loop<br/>Can use tools + query engine<br/>Most flexible but slower"]
    M4 --> M4D["Direct LLM chat<br/>No retrieval<br/>Simple conversation"]

    style CE fill:#7C3AED,color:#fff
    style M1 fill:#4ECDC4,color:#fff
    style M2 fill:#45B7D1,color:#fff
    style M3 fill:#FF6B6B,color:#fff
    style M4 fill:#FFEAA7
```

---

## Agent Architecture

### LlamaIndex Agent Architecture

```mermaid
graph TD
    USER["User Query"] --> AGENT["Agent"]

    AGENT --> REASON["Reasoning Loop<br/>(ReAct / OpenAI Function)"]

    REASON --> DECIDE{"Decision"}

    DECIDE -->|"Need Info"| TOOL["Tool Selection"]
    DECIDE -->|"Ready"| FINAL["Final Answer"]

    TOOL --> T1["QueryEngineTool<br/>(RAG over docs)"]
    TOOL --> T2["FunctionTool<br/>(Custom Python)"]
    TOOL --> T3["APITool<br/>(External APIs)"]
    TOOL --> T4["CodeInterpreter<br/>(Execute code)"]

    T1 --> OBS["Observation"]
    T2 --> OBS
    T3 --> OBS
    T4 --> OBS

    OBS --> REASON

    FINAL --> USER2["User Response<br/>+ Sources + Reasoning"]

    MEMORY["Memory<br/>(Chat History)"] --> AGENT
    SYSTEM["System Prompt<br/>(Instructions)"] --> AGENT

    style USER fill:#E8F4F8
    style AGENT fill:#7C3AED,color:#fff
    style REASON fill:#FF6B6B,color:#fff
    style TOOL fill:#4ECDC4,color:#fff
    style FINAL fill:#96CEB4,color:#fff
    style MEMORY fill:#FFEAA7
    style SYSTEM fill:#FFEAA7
    style USER2 fill:#E8F4F8
```

### ReAct Agent Loop Detail

```mermaid
sequenceDiagram
    participant User
    participant Agent as ReAct Agent
    participant LLM as LLM
    participant Tool1 as QueryEngineTool
    participant Tool2 as CalculatorTool
    participant Memory as Memory

    User ->> Agent: "What was AAPL revenue and what's 15% of it?"
    Agent ->> Memory: Load history
    Agent ->> LLM: Thought: I need AAPL revenue first

    Note over LLM: Step 1: Think → Act → Observe
    LLM ->> Agent: Action: QueryEngine("AAPL revenue")
    Agent ->> Tool1: query("AAPL revenue latest")
    Tool1 ->> Agent: Observation: "$394.3B in FY2023"

    Agent ->> LLM: Thought: Now calculate 15%
    Note over LLM: Step 2: Think → Act → Observe
    LLM ->> Agent: Action: Calculator("394.3 * 0.15")
    Agent ->> Tool2: calculate("394.3 * 0.15")
    Tool2 ->> Agent: Observation: "59.145"

    Agent ->> LLM: Thought: I have both answers
    Note over LLM: Step 3: Think → Final Answer
    LLM ->> Agent: Final: "AAPL revenue was $394.3B, 15% is $59.1B"

    Agent ->> Memory: Save full exchange
    Agent ->> User: Final Answer with reasoning trace
```

### Multi-Agent Architecture

```mermaid
graph TD
    USER["User"] --> ORCHESTRATOR["Orchestrator Agent"]

    ORCHESTRATOR --> A1["Research Agent<br/>(RAG over documents)"]
    ORCHESTRATOR --> A2["Analysis Agent<br/>(Data processing)"]
    ORCHESTRATOR --> A3["Writing Agent<br/>(Report generation)"]

    A1 --> T1["Document QueryEngine"]
    A1 --> T2["Web Search Tool"]

    A2 --> T3["Calculator Tool"]
    A2 --> T4["Code Interpreter"]

    A3 --> T5["Template Engine"]
    A3 --> T6["Formatting Tool"]

    A1 --> SHARED["Shared State<br/>(Context Object)"]
    A2 --> SHARED
    A3 --> SHARED

    SHARED --> ORCHESTRATOR
    ORCHESTRATOR --> USER2["Final Report"]

    style USER fill:#E8F4F8
    style ORCHESTRATOR fill:#7C3AED,color:#fff
    style A1 fill:#FF6B6B,color:#fff
    style A2 fill:#4ECDC4,color:#fff
    style A3 fill:#45B7D1,color:#fff
    style SHARED fill:#FFEAA7
    style USER2 fill:#E8F4F8
```

---

## Workflow Event-Driven Architecture

### Workflow Basics

```mermaid
graph TD
    START["StartEvent"] --> STEP1["Step 1: Parse Input"]
    STEP1 -->|"ParsedEvent"| STEP2["Step 2: Retrieve Context"]
    STEP2 -->|"RetrievedEvent"| STEP3["Step 3: Generate Response"]
    STEP3 -->|"GeneratedEvent"| STEP4["Step 4: Validate Output"]

    STEP4 -->|"ValidEvent"| END["StopEvent<br/>(Return result)"]
    STEP4 -->|"InvalidEvent"| STEP3

    style START fill:#96CEB4,color:#fff
    style STEP1 fill:#4ECDC4,color:#fff
    style STEP2 fill:#45B7D1,color:#fff
    style STEP3 fill:#FF6B6B,color:#fff
    style STEP4 fill:#FFEAA7
    style END fill:#7C3AED,color:#fff
```

### Workflow Internal Architecture

```mermaid
graph TD
    subgraph WORKFLOW["Workflow"]
        direction TB
        CTX["Context<br/>(Shared State)"]

        subgraph EVENTS["Event System"]
            E1["StartEvent"]
            E2["CustomEvent1"]
            E3["CustomEvent2"]
            E4["StopEvent"]
        end

        subgraph STEPS["Steps (Decorated Functions)"]
            S1["@step(StartEvent)"]
            S2["@step(CustomEvent1)"]
            S3["@step(CustomEvent2)"]
        end

        E1 --> S1
        S1 -->|"emit"| E2
        E2 --> S2
        S2 -->|"emit"| E3
        E3 --> S3
        S3 -->|"emit"| E4

        CTX -.->|"shared access"| S1
        CTX -.->|"shared access"| S2
        CTX -.->|"shared access"| S3
    end

    style WORKFLOW fill:#f5f5f5
    style CTX fill:#FFEAA7
    style EVENTS fill:#4ECDC4,color:#fff
    style STEPS fill:#FF6B6B,color:#fff
```

### Branching & Loops in Workflows

```mermaid
graph TD
    START["StartEvent"] --> CLASSIFY["Classify Query<br/>@step"]

    CLASSIFY -->|"SimpleEvent"| SIMPLE["Direct Answer<br/>@step"]
    CLASSIFY -->|"ComplexEvent"| COMPLEX["Multi-Step RAG<br/>@step"]
    CLASSIFY -->|"AgentEvent"| AGENTIC["Agent Loop<br/>@step"]

    SIMPLE --> VALIDATE["Validate<br/>@step"]
    COMPLEX --> VALIDATE
    AGENTIC --> VALIDATE

    VALIDATE -->|"PassEvent"| END["StopEvent"]
    VALIDATE -->|"FailEvent"| RETRY{"Retry Count < 3?"}

    RETRY -->|"Yes"| CLASSIFY
    RETRY -->|"No"| FALLBACK["Fallback Response<br/>@step"]
    FALLBACK --> END

    style START fill:#96CEB4,color:#fff
    style CLASSIFY fill:#7C3AED,color:#fff
    style SIMPLE fill:#4ECDC4,color:#fff
    style COMPLEX fill:#45B7D1,color:#fff
    style AGENTIC fill:#FF6B6B,color:#fff
    style VALIDATE fill:#FFEAA7
    style END fill:#7C3AED,color:#fff
    style FALLBACK fill:#DDA15E,color:#fff
```

### Workflow Code Structure

```python
from llama_index.core.workflow import (
    Workflow, StartEvent, StopEvent, step, Event, Context
)

# Custom Events
class RetrieveEvent(Event):
    query: str

class SynthesizeEvent(Event):
    query: str
    context: str

# Workflow Definition
class RAGWorkflow(Workflow):
    @step
    async def parse_query(self, ctx: Context, ev: StartEvent) -> RetrieveEvent:
        query = ev.get("query")
        await ctx.set("original_query", query)
        return RetrieveEvent(query=query)

    @step
    async def retrieve(self, ctx: Context, ev: RetrieveEvent) -> SynthesizeEvent:
        nodes = self.index.as_retriever().retrieve(ev.query)
        context = "\n".join([n.text for n in nodes])
        return SynthesizeEvent(query=ev.query, context=context)

    @step
    async def synthesize(self, ctx: Context, ev: SynthesizeEvent) -> StopEvent:
        response = self.llm.complete(f"Context: {ev.context}\nQuery: {ev.query}")
        return StopEvent(result=str(response))

# Run
workflow = RAGWorkflow()
result = await workflow.run(query="What is LlamaIndex?")
```

---

## LlamaIndex vs LangChain Comparison

### Architecture Philosophy

```mermaid
graph LR
    subgraph LLAMA["LlamaIndex"]
        direction TB
        LL1["Data-Centric<br/>RAG-First Design"]
        LL2["Index Abstraction"]
        LL3["Node/Document Model"]
        LL4["Query Engines"]
        LL5["Workflows (event-driven)"]
        LL1 --> LL2 --> LL3 --> LL4 --> LL5
    end

    subgraph LANG["LangChain"]
        direction TB
        LC1["Chain-Centric<br/>General Purpose"]
        LC2["LCEL Composition"]
        LC3["Prompt/Chain/Agent"]
        LC4["Broad Integrations"]
        LC5["LangGraph (graph-based)"]
        LC1 --> LC2 --> LC3 --> LC4 --> LC5
    end

    LLAMA ~~~ LANG

    style LLAMA fill:#7C3AED,color:#fff
    style LANG fill:#150458,color:#fff
```

### Feature Comparison Matrix

| Feature | LlamaIndex | LangChain |
|---------|:---------:|:---------:|
| **Primary Focus** | Data indexing & RAG | General LLM orchestration |
| **Index Types** | 5+ specialized indexes | VectorStore focus |
| **Document Parsing** | LlamaParse (PDF, tables) | Basic loaders |
| **Node/Chunk Model** | First-class Nodes with metadata | Documents (simpler) |
| **Query Engine** | Built-in, multiple modes | Manual chain building |
| **Chat Engine** | Built-in with modes | ConversationChain |
| **Agents** | ReAct, OpenAI, Custom | ReAct, OpenAI, Plan-Execute |
| **Multi-Agent** | Orchestrator pattern | LangGraph supervisor |
| **Workflows** | Event-driven Workflows | LangGraph (graph-based) |
| **Streaming** | Native in Workflows | LCEL streaming |
| **Observability** | LlamaTrace, callbacks | LangSmith |
| **Managed Service** | LlamaCloud | LangServe, LangSmith |
| **Community Size** | Growing (35K+ GitHub ⭐) | Larger (90K+ GitHub ⭐) |
| **Learning Curve** | Moderate (RAG-focused) | Steep (broad surface) |
| **Best For** | RAG applications | General LLM apps |

### When to Use Which

```mermaid
graph TD
    START["What are you building?"] --> Q1{"Primary use case?"}

    Q1 -->|"RAG / Search"| Q2{"Complex documents?<br/>(Tables, PDFs, mixed)"}
    Q1 -->|"Agents / Tools"| Q3{"Multi-agent<br/>orchestration?"}
    Q1 -->|"General LLM App"| LANG["Use LangChain<br/>Broader ecosystem"]

    Q2 -->|Yes| LLAMA["Use LlamaIndex<br/>Better parsing + indexing"]
    Q2 -->|No| EITHER["Either works well<br/>LlamaIndex slightly easier"]

    Q3 -->|Yes| LANGGRAPH["Use LangGraph<br/>Better multi-agent support"]
    Q3 -->|No| Q4{"Need specialized<br/>query routing?"}

    Q4 -->|Yes| LLAMA
    Q4 -->|No| LANG

    style START fill:#7C3AED,color:#fff
    style LLAMA fill:#7C3AED,color:#fff
    style LANG fill:#150458,color:#fff
    style LANGGRAPH fill:#150458,color:#fff
    style EITHER fill:#4ECDC4,color:#fff
```

---

## Data Connector Ecosystem

### LlamaHub Data Connectors (300+)

```mermaid
graph TD
    HUB["LlamaHub<br/>(300+ Connectors)"] --> FILE["File-Based"]
    HUB --> DB["Databases"]
    HUB --> CLOUD["Cloud Storage"]
    HUB --> SAAS["SaaS Apps"]
    HUB --> WEB["Web & APIs"]
    HUB --> CUSTOM["Custom"]

    FILE --> F1["PDF (LlamaParse)"]
    FILE --> F2["DOCX, PPTX, XLSX"]
    FILE --> F3["CSV, JSON, XML"]
    FILE --> F4["Markdown, HTML"]
    FILE --> F5["Images (multi-modal)"]

    DB --> D1["PostgreSQL"]
    DB --> D2["MongoDB"]
    DB --> D3["MySQL"]
    DB --> D4["BigQuery"]
    DB --> D5["Snowflake"]

    CLOUD --> C1["S3"]
    CLOUD --> C2["GCS"]
    CLOUD --> C3["Azure Blob"]
    CLOUD --> C4["Google Drive"]
    CLOUD --> C5["Dropbox"]

    SAAS --> S1["Notion"]
    SAAS --> S2["Slack"]
    SAAS --> S3["Confluence"]
    SAAS --> S4["Salesforce"]
    SAAS --> S5["GitHub/GitLab"]

    WEB --> W1["Web Scraper"]
    WEB --> W2["Wikipedia"]
    WEB --> W3["YouTube Transcripts"]
    WEB --> W4["arXiv Papers"]
    WEB --> W5["Twitter/Reddit"]

    style HUB fill:#7C3AED,color:#fff
    style FILE fill:#FF6B6B,color:#fff
    style DB fill:#4ECDC4,color:#fff
    style CLOUD fill:#45B7D1,color:#fff
    style SAAS fill:#FFEAA7
    style WEB fill:#96CEB4,color:#fff
    style CUSTOM fill:#DDA15E
```

### Vector Store Integrations

```mermaid
graph LR
    INDEX["LlamaIndex"] --> MANAGED["Managed"]
    INDEX --> SELF["Self-Hosted"]
    INDEX --> LOCAL["Local/Embedded"]

    MANAGED --> M1["Pinecone"]
    MANAGED --> M2["Weaviate Cloud"]
    MANAGED --> M3["Qdrant Cloud"]
    MANAGED --> M4["Zilliz (Milvus)"]

    SELF --> S1["Milvus"]
    SELF --> S2["Elasticsearch"]
    SELF --> S3["pgvector"]
    SELF --> S4["Redis"]

    LOCAL --> L1["ChromaDB"]
    LOCAL --> L2["FAISS"]
    LOCAL --> L3["LanceDB"]
    LOCAL --> L4["DuckDB"]

    style INDEX fill:#7C3AED,color:#fff
    style MANAGED fill:#4ECDC4,color:#fff
    style SELF fill:#FF6B6B,color:#fff
    style LOCAL fill:#FFEAA7
```

---

## Production Deployment

### LlamaCloud Production Architecture

```mermaid
graph TD
    subgraph CLIENT["Client Application"]
        APP["Your App"]
        SDK["LlamaIndex SDK"]
    end

    subgraph LLAMACLOUD["LlamaCloud (Managed)"]
        PARSE["LlamaParse<br/>(Document Parsing)"]
        EXTRACT["LlamaExtract<br/>(Structured Extraction)"]
        MANAGED_INDEX["Managed Index<br/>(Cloud-hosted)"]
        MANAGED_RET["Managed Retriever<br/>(Cloud-hosted)"]
    end

    subgraph INFRA["Your Infrastructure"]
        VDB["Vector Database<br/>(Pinecone/Weaviate)"]
        LLM_API["LLM API<br/>(OpenAI/Anthropic)"]
        CACHE["Cache Layer<br/>(Redis)"]
        MONITOR["Observability<br/>(LlamaTrace)"]
    end

    APP --> SDK
    SDK --> PARSE
    SDK --> EXTRACT
    SDK --> MANAGED_INDEX
    SDK --> MANAGED_RET

    MANAGED_INDEX --> VDB
    MANAGED_RET --> VDB
    SDK --> LLM_API
    SDK --> CACHE
    SDK --> MONITOR

    style CLIENT fill:#E8F4F8
    style LLAMACLOUD fill:#7C3AED,color:#fff
    style INFRA fill:#4ECDC4,color:#fff
```

### Self-Hosted Production Pipeline

```mermaid
graph TD
    subgraph INGEST["Ingestion Pipeline"]
        SRC["Data Sources"] --> LOAD["Document Loader"]
        LOAD --> PARSE["LlamaParse API"]
        PARSE --> CHUNK["Node Parser<br/>(Semantic Splitter)"]
        CHUNK --> EMBED["Embedding Model<br/>(batch processing)"]
        EMBED --> STORE["Vector Store<br/>(Pinecone/pgvector)"]
    end

    subgraph SERVE["Query Pipeline"]
        USER["User Query"] --> API["FastAPI / Flask"]
        API --> CACHE["Redis Cache"]
        CACHE -->|miss| QE["Query Engine"]
        QE --> RET["Retriever"]
        RET --> STORE
        RET --> RERANK["Reranker<br/>(Cohere / Cross-Encoder)"]
        RERANK --> SYNTH["Response Synthesizer"]
        SYNTH --> LLM["LLM"]
        LLM --> API
        API --> USER
    end

    subgraph OPS["Operations"]
        TRACE["LlamaTrace<br/>(Observability)"]
        EVAL["RAG Evaluation<br/>(Faithfulness, Relevancy)"]
        GUARD["Guardrails<br/>(NeMo / Guardrails AI)"]
    end

    QE -.-> TRACE
    QE -.-> EVAL
    API -.-> GUARD

    style INGEST fill:#FF6B6B,color:#fff
    style SERVE fill:#4ECDC4,color:#fff
    style OPS fill:#FFEAA7
```

---

## Learning Path

### LlamaIndex Learning Roadmap

```mermaid
graph TD
    subgraph BEGINNER["🟢 Beginner (Week 1-2)"]
        B1["Install LlamaIndex"] --> B2["SimpleDirectoryReader"]
        B2 --> B3["VectorStoreIndex basics"]
        B3 --> B4["Simple query engine"]
        B4 --> B5["Chat engine basics"]
    end

    subgraph INTERMEDIATE["🟡 Intermediate (Week 3-4)"]
        I1["Node parsers & chunking"] --> I2["Multiple index types"]
        I2 --> I3["Custom retrievers"]
        I3 --> I4["Response synthesizer modes"]
        I4 --> I5["Agents with tools"]
    end

    subgraph ADVANCED["🔴 Advanced (Week 5-8)"]
        A1["Advanced RAG patterns"] --> A2["Workflows (event-driven)"]
        A2 --> A3["Multi-agent systems"]
        A3 --> A4["Custom LLM/Embedding"]
        A4 --> A5["RAG evaluation & optimization"]
    end

    subgraph PRODUCTION["🟣 Production (Week 9+)"]
        P1["LlamaCloud integration"] --> P2["LlamaParse for complex docs"]
        P2 --> P3["Observability (LlamaTrace)"]
        P3 --> P4["Deployment (Docker/K8s)"]
        P4 --> P5["Performance tuning"]
    end

    BEGINNER --> INTERMEDIATE
    INTERMEDIATE --> ADVANCED
    ADVANCED --> PRODUCTION

    style BEGINNER fill:#96CEB4,color:#fff
    style INTERMEDIATE fill:#FFEAA7
    style ADVANCED fill:#FF6B6B,color:#fff
    style PRODUCTION fill:#7C3AED,color:#fff
```

### Key Resources

| Resource | URL | Level |
|----------|-----|-------|
| Official Docs | docs.llamaindex.ai | All |
| LlamaHub | llamahub.ai | Beginner |
| LlamaCloud | cloud.llamaindex.ai | Production |
| GitHub | github.com/run-llama/llama_index | All |
| Discord | discord.gg/llamaindex | Community |
| YouTube (Jerry Liu) | LlamaIndex channel | Beginner-Intermediate |
| RAG Course (DeepLearning.AI) | deeplearning.ai | Intermediate |
| Building Production RAG | docs.llamaindex.ai/en/stable/optimizing/ | Advanced |

---

## Performance Characteristics

### Latency Breakdown by Operation

```mermaid
graph LR
    subgraph FAST["⚡ Fast (<100ms)"]
        F1["Keyword lookup"]
        F2["Cached query"]
        F3["Simple embedding"]
    end

    subgraph MEDIUM["🔄 Medium (100ms-2s)"]
        M1["Vector similarity search"]
        M2["Node parsing"]
        M3["Single LLM call"]
    end

    subgraph SLOW["🐢 Slow (2s-30s)"]
        S1["Document ingestion"]
        S2["Tree index build"]
        S3["Multi-step agent"]
    end

    subgraph VERY_SLOW["⏳ Very Slow (30s+)"]
        V1["Full corpus re-index"]
        V2["Knowledge graph build"]
        V3["Complex workflow pipeline"]
    end

    style FAST fill:#96CEB4,color:#fff
    style MEDIUM fill:#FFEAA7
    style SLOW fill:#FF6B6B,color:#fff
    style VERY_SLOW fill:#7C3AED,color:#fff
```

### Optimization Strategies

| Bottleneck | Strategy | Impact |
|-----------|----------|--------|
| **Embedding latency** | Batch embeddings, cache results | 3-5x faster |
| **LLM calls** | Use smaller models for routing, cache responses | 2-4x faster |
| **Retrieval** | Use approximate NN (HNSW), pre-filter metadata | 5-10x faster |
| **Document parsing** | Use LlamaParse async, parallel processing | 3-8x faster |
| **Re-ranking** | Use lightweight cross-encoders, limit candidates | 2x faster |
| **Index build** | Incremental updates, avoid full rebuilds | 10x+ faster |
