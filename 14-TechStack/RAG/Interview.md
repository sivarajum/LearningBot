# RAG Interview Questions and Answers

## Beginner Level Questions

### Q1: What is RAG and how does it work?

**Answer:**
RAG (Retrieval-Augmented Generation) is a technique that combines retrieval-based and generation-based approaches to improve LLM responses by grounding them in retrieved information.

**How it Works:**
1. **Query**: User asks a question
2. **Retrieval**: System retrieves relevant documents from knowledge base
3. **Augmentation**: Retrieved documents are added to the prompt
4. **Generation**: LLM generates response using retrieved context
5. **Response**: User receives grounded, accurate response

**Key Components:**
- **Retriever**: Finds relevant documents
- **Vector Database**: Stores document embeddings
- **Generator**: LLM that generates responses
- **Knowledge Base**: Collection of documents

**Example:**
```python
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI

# Initialize components
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts(texts, embeddings)
llm = OpenAI()

# RAG pipeline
def rag_query(question):
    # Retrieve relevant documents
    docs = vectorstore.similarity_search(question, k=3)
    
    # Create context
    context = "\n".join([doc.page_content for doc in docs])
    
    # Generate response
    prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    response = llm(prompt)
    
    return response
```

### Q2: What are the advantages of RAG over fine-tuning?

**Answer:**

**RAG Advantages:**
- **Up-to-date information**: Can access latest information without retraining
- **Reduced hallucinations**: Grounded in retrieved facts
- **Transparency**: Can cite sources and explain answers
- **Domain-specific**: Easy to add domain-specific knowledge
- **Cost-effective**: No need to retrain models
- **Flexibility**: Easy to update knowledge base

**Fine-tuning Advantages:**
- **Task-specific**: Optimized for specific tasks
- **Consistent style**: Maintains consistent output style
- **No retrieval overhead**: Faster inference
- **Better for specialized tasks**: Can learn task-specific patterns

**When to Use RAG:**
- Need access to latest information
- Domain-specific knowledge required
- Transparency and citations important
- Knowledge base changes frequently

**When to Use Fine-tuning:**
- Task-specific optimization needed
- Consistent output style required
- Specialized domain knowledge
- Stable knowledge base

### Q3: Explain the RAG architecture and components.

**Answer:**

**RAG Architecture:**

**1. Document Processing:**
- Load and chunk documents
- Create embeddings
- Store in vector database

**2. Retrieval:**
- Encode user query
- Search similar documents
- Rank and filter results

**3. Augmentation:**
- Combine retrieved documents
- Create context for LLM
- Format prompt

**4. Generation:**
- Generate response using LLM
- Use retrieved context
- Return answer with sources

**Components:**
- **Embeddings Model**: Converts text to vectors
- **Vector Database**: Stores and searches embeddings
- **Retriever**: Finds relevant documents
- **LLM**: Generates responses
- **Prompt Template**: Formats prompt with context

**Example:**
```python
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA

# Load documents
loader = TextLoader("documents.txt")
documents = loader.load()

# Split documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
texts = text_splitter.split_documents(documents)

# Create embeddings
embeddings = OpenAIEmbeddings()

# Create vector store
vectorstore = Chroma.from_documents(texts, embeddings)

# Create RAG chain
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# Query
response = qa_chain.run("What is RAG?")
```

### Q4: What are the different RAG retrieval strategies?

**Answer:**

**Retrieval Strategies:**

**1. Similarity Search:**
- Vector similarity (cosine, dot product)
- Semantic similarity
- Fast and effective

**2. Hybrid Search:**
- Combines vector and keyword search
- Better recall
- More comprehensive results

**3. Reranking:**
- Initial retrieval with similarity search
- Rerank results with cross-encoder
- Better precision

**4. Multi-query Retrieval:**
- Generate multiple query variations
- Retrieve for each query
- Combine and deduplicate results

**Example:**
```python
from langchain.retrievers import BM25Retriever
from langchain.vectorstores import FAISS

# Hybrid search
vectorstore = FAISS.from_texts(texts, embeddings)
bm25_retriever = BM25Retriever.from_texts(texts)

def hybrid_search(query, k=5):
    # Vector search
    vector_results = vectorstore.similarity_search(query, k=k)
    
    # Keyword search
    keyword_results = bm25_retriever.get_relevant_documents(query)
    
    # Combine and deduplicate
    combined_results = combine_results(vector_results, keyword_results)
    
    return combined_results
```

### Q5: How do you chunk documents for RAG?

**Answer:**

**Chunking Strategies:**

**1. Fixed-size Chunking:**
- Split into fixed-size chunks
- Simple and fast
- May break context

**2. Sentence-based Chunking:**
- Split at sentence boundaries
- Preserves sentence context
- Better for semantic search

**3. Paragraph-based Chunking:**
- Split at paragraph boundaries
- Preserves paragraph context
- Good for longer documents

**4. Sliding Window Chunking:**
- Overlapping chunks
- Preserves context across boundaries
- More chunks but better coverage

**Example:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Recursive character text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)

chunks = text_splitter.split_text(text)

# Sentence-based chunking
from langchain.text_splitter import SentenceTransformersTokenTextSplitter

splitter = SentenceTransformersTokenTextSplitter(
    chunk_overlap=50
)

chunks = splitter.split_text(text)
```

## Intermediate Level Questions

### Q6: Explain advanced RAG techniques: Reranking and Query Expansion.

**Answer:**

**Reranking:**
- Improve retrieval precision
- Use cross-encoder models
- Rerank initial retrieval results
- Better relevance scoring

**Query Expansion:**
- Generate query variations
- Expand user query
- Retrieve for multiple queries
- Combine results

**Example:**
```python
from sentence_transformers import CrossEncoder

# Reranking
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank_results(query, documents, top_k=5):
    # Score pairs
    pairs = [[query, doc] for doc in documents]
    scores = cross_encoder.predict(pairs)
    
    # Sort by score
    ranked_docs = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )
    
    return [doc for doc, score in ranked_docs[:top_k]]

# Query expansion
from langchain.llms import OpenAI

def expand_query(query):
    llm = OpenAI()
    prompt = f"Generate 3 query variations for: {query}"
    variations = llm(prompt)
    return variations.split("\n")
```

### Q7: How do you evaluate RAG systems?

**Answer:**

**Evaluation Metrics:**

**1. Retrieval Metrics:**
- **Recall@K**: Percentage of relevant documents retrieved
- **Precision@K**: Percentage of retrieved documents that are relevant
- **MRR**: Mean Reciprocal Rank

**2. Generation Metrics:**
- **BLEU**: N-gram overlap with reference
- **ROUGE**: Recall-oriented evaluation
- **BERTScore**: Semantic similarity

**3. End-to-end Metrics:**
- **Faithfulness**: Answer grounded in context
- **Answer Relevance**: Answer relevance to question
- **Context Precision**: Relevance of retrieved context

**Example:**
```python
from ragas import evaluate
from datasets import Dataset

# Evaluation dataset
dataset = Dataset.from_dict({
    "question": ["What is RAG?"],
    "contexts": [["RAG is a technique..."]],
    "answer": ["RAG is Retrieval-Augmented Generation..."],
    "ground_truth": ["RAG combines retrieval and generation"]
})

# Evaluate
results = evaluate(
    dataset=dataset,
    metrics=[
        "context_precision",
        "faithfulness",
        "answer_relevance"
    ]
)
```

### Q8: Explain RAG with multiple knowledge bases and sources.

**Answer:**

**Multiple Knowledge Bases:**
- Use multiple vector stores
- Route queries to relevant knowledge base
- Combine results from multiple sources
- Handle different document types

**Strategies:**

**1. Routing:**
- Route queries to relevant knowledge base
- Use classification or keywords
- Retrieve from selected knowledge base

**2. Parallel Retrieval:**
- Retrieve from all knowledge bases
- Combine and rank results
- More comprehensive but slower

**3. Hierarchical Retrieval:**
- Retrieve from general knowledge base first
- Then retrieve from specific knowledge base
- Combine results

**Example:**
```python
def multi_kb_rag(query, knowledge_bases):
    # Route to relevant knowledge base
    relevant_kb = route_query(query, knowledge_bases)
    
    # Retrieve from relevant knowledge base
    docs = relevant_kb.similarity_search(query, k=5)
    
    # Also retrieve from general knowledge base
    general_docs = knowledge_bases['general'].similarity_search(query, k=3)
    
    # Combine results
    combined_docs = combine_results(docs, general_docs)
    
    # Generate response
    response = generate_response(query, combined_docs)
    
    return response
```

## Advanced Level Questions

### Q9: How do you handle RAG for long documents and conversations?

**Answer:**

**Long Documents:**
- Use hierarchical chunking
- Create document summaries
- Use map-reduce approach
- Implement document compression

**Conversations:**
- Maintain conversation history
- Use conversation-aware retrieval
- Handle follow-up questions
- Implement context window management

**Example:**
```python
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Conversational RAG
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=OpenAI(),
    retriever=vectorstore.as_retriever(),
    memory=memory
)

# Chat
response = qa_chain.run("What is RAG?")
response = qa_chain.run("How does it work?")  # Uses conversation history
```

### Q10: Explain RAG optimization techniques.

**Answer:**

**Optimization Techniques:**

**1. Embedding Optimization:**
- Use better embedding models
- Fine-tune embeddings for domain
- Use multimodal embeddings

**2. Retrieval Optimization:**
- Improve chunking strategy
- Use better retrieval methods
- Implement reranking
- Optimize vector database

**3. Generation Optimization:**
- Use better prompts
- Implement prompt engineering
- Use few-shot examples
- Optimize LLM parameters

**4. System Optimization:**
- Cache embeddings
- Batch processing
- Async retrieval
- Optimize vector database queries

**Example:**
```python
# Optimized RAG pipeline
def optimized_rag(query):
    # Cache embeddings
    if query in embedding_cache:
        query_embedding = embedding_cache[query]
    else:
        query_embedding = embeddings.embed_query(query)
        embedding_cache[query] = query_embedding
    
    # Batch retrieval
    docs = vectorstore.similarity_search_with_score(
        query_embedding,
        k=10
    )
    
    # Rerank
    reranked_docs = rerank_results(query, docs, top_k=5)
    
    # Generate with optimized prompt
    prompt = create_optimized_prompt(query, reranked_docs)
    response = llm(prompt)
    
    return response
```

---

## Key Takeaways

1. **RAG combines retrieval and generation** for improved LLM responses
2. **Retrieval strategies** include similarity search, hybrid search, and reranking
3. **Document chunking** is crucial for effective retrieval
4. **Reranking and query expansion** improve retrieval quality
5. **Evaluation metrics** measure retrieval and generation quality
6. **Multiple knowledge bases** enable domain-specific RAG
7. **Conversational RAG** handles multi-turn conversations
8. **Optimization techniques** improve RAG performance and efficiency

