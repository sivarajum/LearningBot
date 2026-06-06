# LangChain - Visual Learning Guide

## 🎨 Visual Learning: Chains, Agents, RAG Flows

---

## 📊 Core Concepts

### LangChain Architecture

```mermaid
graph TB
    subgraph "LangChain Components"
        A[LLMs<br/>OpenAI, HuggingFace]
        B[Prompts<br/>Templates]
        C[Chains<br/>Sequential Logic]
        D[Agents<br/>Tool Use]
        E[Memory<br/>Context]
        F[Vector Stores<br/>Embeddings]
    end
    
    subgraph "Applications"
        G[Chatbots]
        H[RAG Systems]
        I[Agents]
        J[Q&A Systems]
    end
    
    A --> C
    B --> C
    C --> D
    E --> C
    F --> C
    
    C --> G
    C --> H
    D --> I
    C --> J
    
    style A fill:#4285f4
    style C fill:#34a853
    style D fill:#ea4335
    style F fill:#fbbc04
```

---

## 🔗 Chain Flows

### Simple Chain Flow

```mermaid
sequenceDiagram
    participant User
    participant Chain
    participant Prompt
    participant LLM
    participant Response
    
    User->>Chain: Input
    Chain->>Prompt: Format Input
    Prompt->>LLM: Send Prompt
    LLM->>Response: Generate Text
    Response->>Chain: Return Result
    Chain->>User: Output
```

### Sequential Chain Flow

```mermaid
flowchart LR
    A[Input] --> B[Chain 1]
    B --> C[Output 1]
    C --> D[Chain 2]
    D --> E[Output 2]
    E --> F[Chain 3]
    F --> G[Final Output]
    
    style B fill:#4285f4
    style D fill:#34a853
    style F fill:#ea4335
```

### Chain with Memory

```mermaid
graph TB
    A[User Input] --> B[Chain]
    B --> C[Load Memory]
    C --> D[Combine Context]
    D --> E[LLM]
    E --> F[Response]
    F --> G[Update Memory]
    G --> H[Return Response]
    
    style C fill:#4285f4
    style G fill:#34a853
```

---

## 🔍 RAG (Retrieval-Augmented Generation) Flow

### Complete RAG Pipeline

```mermaid
graph TB
    subgraph "Document Processing"
        A[Documents] --> B[Load Documents]
        B --> C[Split into Chunks]
        C --> D[Generate Embeddings]
        D --> E[Store in Vector DB]
    end
    
    subgraph "Query Processing"
        F[User Query] --> G[Embed Query]
        G --> H[Vector Search]
        H --> I[Retrieve Top-K]
    end
    
    subgraph "Generation"
        I --> J[Combine Context]
        J --> K[Create Prompt]
        K --> L[LLM Generation]
        L --> M[Response]
    end
    
    E --> H
    
    style D fill:#4285f4
    style H fill:#34a853
    style L fill:#ea4335
```

### RAG Detailed Flow

```mermaid
sequenceDiagram
    participant User
    participant RAG
    participant Embedder
    participant VectorDB
    participant Retriever
    participant LLM
    
    User->>RAG: Query
    RAG->>Embedder: Embed Query
    Embedder->>VectorDB: Search Similar
    VectorDB-->>Retriever: Top-K Documents
    Retriever->>RAG: Context
    RAG->>LLM: Query + Context
    LLM-->>RAG: Generated Response
    RAG-->>User: Answer
```

### RAG Architecture (Your Module 05)

```mermaid
graph TB
    A[PDF/Markdown Files] --> B[Document Loader]
    B --> C[Text Splitter]
    C --> D[Chunk Documents]
    D --> E[Embedding Model]
    E --> F[Vector Embeddings]
    F --> G[Pinecone/Chroma]
    
    H[User Query] --> I[Query Embedding]
    I --> J[Vector Search]
    G --> J
    J --> K[Retrieve Top-K]
    K --> L[LangChain RAG Chain]
    L --> M[LLM Generation]
    M --> N[Response]
    
    style E fill:#4285f4
    style G fill:#34a853
    style L fill:#ea4335
```

---

## 🤖 Agent Flows

### Agent Decision Flow

```mermaid
flowchart TD
    A[User Input] --> B[Agent]
    B --> C{Need Tool?}
    C -->|Yes| D[Select Tool]
    C -->|No| E[LLM Response]
    
    D --> F[Execute Tool]
    F --> G[Get Tool Result]
    G --> H[Add to Context]
    H --> I{More Actions?}
    I -->|Yes| C
    I -->|No| J[Final Response]
    E --> J
    
    style C fill:#4285f4
    style D fill:#34a853
    style F fill:#ea4335
```

### ReAct Agent Flow

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant LLM
    participant Tools
    participant Response
    
    User->>Agent: Question
    Agent->>LLM: Think
    LLM-->>Agent: Action Needed
    
    alt Use Tool
        Agent->>Tools: Execute Tool
        Tools-->>Agent: Result
        Agent->>LLM: Observation
        LLM-->>Agent: Next Action
    else Final Answer
        Agent->>LLM: Generate Answer
        LLM-->>Response: Final Answer
        Response-->>User: Response
    end
```

---

## 💬 Chatbot Flow (Module 03)

### Conversation Flow with Memory

```mermaid
graph TB
    A[User Message] --> B[Chatbot]
    B --> C[Load Conversation History]
    C --> D[Combine with New Message]
    D --> E[Create Prompt]
    E --> F[LLM Generation]
    F --> G[Response]
    G --> H[Update Memory]
    H --> I[Return Response]
    
    style C fill:#4285f4
    style H fill:#34a853
```

### Memory Types Comparison

```mermaid
mindmap
  root((Memory Types))
    Buffer Memory
      Stores All History
      Simple
      Token Limit
    Summary Memory
      Summarizes Old
      Saves Tokens
      May Lose Details
    Entity Memory
      Tracks Entities
      Person/Place/Thing
      Contextual
```

---

## 🔄 Document Processing Flow

### Document Loading and Chunking

```mermaid
flowchart TD
    A[Document Sources] --> B{Document Type?}
    B -->|PDF| C[PDF Loader]
    B -->|TXT| D[Text Loader]
    B -->|Markdown| E[Markdown Loader]
    
    C --> F[Text Extraction]
    D --> F
    E --> F
    
    F --> G[Text Splitter]
    G --> H[Chunk Size: 1000]
    H --> I[Chunk Overlap: 200]
    I --> J[Document Chunks]
    
    style G fill:#4285f4
    style J fill:#34a853
```

### Embedding and Storage

```mermaid
sequenceDiagram
    participant Chunks
    participant Embedder
    participant VectorDB
    participant Index
    
    Chunks->>Embedder: Text Chunks
    Embedder->>Embedder: Generate Embeddings
    Embedder->>VectorDB: Store Vectors
    VectorDB->>Index: Create Index
    Index-->>VectorDB: Index Ready
```

---

## 🎯 Query Processing Flow

### Query to Response Flow

```mermaid
flowchart LR
    A[Query] --> B[Embed Query]
    B --> C[Vector Search]
    C --> D[Top-K Results]
    D --> E[Re-rank]
    E --> F[Select Best]
    F --> G[Create Prompt]
    G --> H[LLM]
    H --> I[Response]
    
    style B fill:#4285f4
    style C fill:#34a853
    style H fill:#ea4335
```

### Multi-Step Query Processing

```mermaid
graph TB
    A[Complex Query] --> B[Query Decomposition]
    B --> C[Query 1]
    B --> D[Query 2]
    B --> E[Query 3]
    
    C --> F[Search 1]
    D --> G[Search 2]
    E --> H[Search 3]
    
    F --> I[Combine Results]
    G --> I
    H --> I
    
    I --> J[LLM Synthesis]
    J --> K[Final Answer]
    
    style B fill:#4285f4
    style I fill:#34a853
    style J fill:#ea4335
```

---

## 🛠️ Tool Integration Flow

### Agent with Tools

```mermaid
graph TB
    A[Agent] --> B{Decision}
    B -->|Search| C[Search Tool]
    B -->|Calculate| D[Calculator Tool]
    B -->|API Call| E[API Tool]
    
    C --> F[Tool Result]
    D --> F
    E --> F
    
    F --> G[Add to Context]
    G --> H{More Actions?}
    H -->|Yes| B
    H -->|No| I[Final Response]
    
    style B fill:#4285f4
    style F fill:#34a853
```

---

## 📊 Performance Optimization

### Caching Strategy

```mermaid
mindmap
  root((LangChain Optimization))
    Caching
      LLM Cache
        Same Query = Cached
      Embedding Cache
        Reuse Embeddings
    Batching
      Batch Requests
      Reduce API Calls
    Streaming
      Real-time Response
      Better UX
```

---

## 🎯 Key Visual Takeaways

1. **Chains**: Sequential LLM operations
2. **RAG**: Retrieve → Augment → Generate
3. **Agents**: Think → Act → Observe → Repeat
4. **Memory**: Context management
5. **Tools**: External integration

---

## 📚 Next Steps

1. ✅ Review these diagrams
2. 🏗️ Draw them yourself
3. 💬 Use in interviews
4. 🔗 Connect to your POCs

---

**Visual learning helps!** Use these to explain LangChain in interviews.

