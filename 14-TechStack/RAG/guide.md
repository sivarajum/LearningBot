# RAG Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```python
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA

# Load documents
loader = TextLoader("document.txt")
documents = loader.load()

# Split
text_splitter = CharacterTextSplitter(chunk_size=1000)
texts = text_splitter.split_documents(documents)

# Create embeddings
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(texts, embeddings)

# Create QA chain
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever()
)
```

### 2. **Basic Query**
```python
result = qa.run("What is the document about?")
print(result)
```

## Level 2 – Production Patterns

### Advanced Retrieval
```python
from langchain.retrievers import ContextualCompressionRetriever

compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever()
)
```

### Multi-Step RAG
```python
# Query expansion
expanded_query = expand_query(original_query)

# Multi-retrieval
results1 = vectorstore1.search(expanded_query)
results2 = vectorstore2.search(expanded_query)

# Combine and rerank
combined = combine_results(results1, results2)
reranked = rerank(combined, original_query)
```

## Level 3 – Architect Playbook

### Production RAG
```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/rag")
def rag_query(query: str):
    results = qa.run(query)
    return {"answer": results}
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Load docs | `TextLoader()` | Load documents |
| Create embeddings | `OpenAIEmbeddings()` | Generate embeddings |
| Query | `qa.run()` | Query RAG system |

## Checklist Before Production

- [ ] Choose appropriate chunking strategy
- [ ] Select embedding model
- [ ] Set up vector database
- [ ] Implement query expansion
- [ ] Set up reranking
- [ ] Monitor performance
- [ ] Optimize retrieval
- [ ] Test accuracy
