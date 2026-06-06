# RAG: Retrieval-Augmented Generation

## Core Concepts

### RAG Fundamentals

Retrieval-Augmented Generation (RAG) is a technique that combines the strengths of retrieval-based and generation-based approaches to natural language processing. By retrieving relevant information from a knowledge base and using it to condition generation, RAG systems can produce more accurate, up-to-date, and contextually relevant responses.

**Key Components:**
- **Retriever**: Finds relevant documents or passages from a knowledge base
- **Generator**: Uses retrieved information to generate coherent responses
- **Knowledge Base**: Collection of documents, passages, or structured data
- **Embeddings**: Vector representations of text for semantic similarity search

**Advantages:**
- Access to up-to-date information without retraining
- Reduced hallucinations through grounding in retrieved facts
- Better handling of domain-specific knowledge
- Improved transparency and explainability

### RAG Architecture Patterns

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class RetrievedDocument:
    """Represents a retrieved document with metadata"""
    content: str
    score: float
    metadata: Dict[str, Any]
    source: str
    chunk_id: str

@dataclass
class RAGQuery:
    """Represents a RAG query with context"""
    question: str
    context: Optional[List[RetrievedDocument]] = None
    metadata: Dict[str, Any] = None

@dataclass
class RAGResponse:
    """Represents a RAG response"""
    answer: str
    retrieved_docs: List[RetrievedDocument]
    confidence_score: float
    generation_metadata: Dict[str, Any]

class BaseRetriever(ABC):
    """Abstract base class for retrieval components"""

    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 5) -> List[RetrievedDocument]:
        """Retrieve relevant documents for a query"""
        pass

    @abstractmethod
    async def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the knowledge base"""
        pass

class BaseGenerator(ABC):
    """Abstract base class for generation components"""

    @abstractmethod
    async def generate(self, query: RAGQuery, **kwargs) -> str:
        """Generate response using retrieved context"""
        pass

class RAGPipeline:
    """Main RAG pipeline coordinating retrieval and generation"""

    def __init__(self, retriever: BaseRetriever, generator: BaseGenerator):
        self.retriever = retriever
        self.generator = generator
        self.query_history = []

    async def query(self, question: str, top_k: int = 5, **generation_kwargs) -> RAGResponse:
        """Execute RAG query"""
        try:
            # Retrieve relevant documents
            retrieved_docs = await self.retriever.retrieve(question, top_k=top_k)

            # Create RAG query with context
            rag_query = RAGQuery(
                question=question,
                context=retrieved_docs,
                metadata={"top_k": top_k, "timestamp": str(datetime.now())}
            )

            # Generate response
            answer = await self.generator.generate(rag_query, **generation_kwargs)

            # Calculate confidence score
            confidence_score = self._calculate_confidence(retrieved_docs, answer)

            # Create response
            response = RAGResponse(
                answer=answer,
                retrieved_docs=retrieved_docs,
                confidence_score=confidence_score,
                generation_metadata={
                    "retrieval_count": len(retrieved_docs),
                    "top_score": retrieved_docs[0].score if retrieved_docs else 0.0,
                    **generation_kwargs
                }
            )

            # Log query
            self.query_history.append({
                "query": question,
                "response": response,
                "timestamp": datetime.now()
            })

            return response

        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            raise

    def _calculate_confidence(self, docs: List[RetrievedDocument], answer: str) -> float:
        """Calculate confidence score based on retrieval quality"""
        if not docs:
            return 0.0

        # Simple confidence based on top retrieval score and answer length
        top_score = docs[0].score
        answer_length = len(answer.split())

        # Normalize and combine factors
        confidence = min(top_score, 1.0) * min(answer_length / 100, 1.0)
        return confidence

    def get_query_history(self) -> List[Dict[str, Any]]:
        """Get query history for analysis"""
        return self.query_history
```

## Vector Databases and Embeddings

### Embedding Models

```python
import torch
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating text embeddings"""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name, device=self.device)

    def encode_texts(self, texts: Union[str, List[str]],
                    batch_size: int = 32,
                    normalize_embeddings: bool = True) -> np.ndarray:
        """Encode texts to embeddings"""

        if isinstance(texts, str):
            texts = [texts]

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=normalize_embeddings,
                convert_to_numpy=True
            )

            return embeddings

        except Exception as e:
            logger.error(f"Embedding encoding failed: {e}")
            raise

    def encode_query(self, query: str) -> np.ndarray:
        """Encode a single query"""
        return self.encode_texts([query])[0]

    def calculate_similarity(self, query_embedding: np.ndarray,
                           document_embeddings: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between query and documents"""
        # Cosine similarity
        dot_product = np.dot(document_embeddings, query_embedding)
        query_norm = np.linalg.norm(query_embedding)
        doc_norms = np.linalg.norm(document_embeddings, axis=1)

        similarities = dot_product / (query_norm * doc_norms + 1e-8)
        return similarities

    async def batch_encode(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """Asynchronously encode texts in batches"""
        import asyncio

        def encode_batch(batch):
            return self.encode_texts(batch, batch_size=batch_size)

        # Split into batches
        batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]

        # Encode batches (could be parallelized further)
        loop = asyncio.get_event_loop()
        embeddings_list = []

        for batch in batches:
            embeddings = await loop.run_in_executor(None, encode_batch, batch)
            embeddings_list.extend(embeddings)

        return embeddings_list

class DocumentChunker:
    """Service for chunking documents for embedding"""

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Chunk text into smaller pieces"""

        words = text.split()
        chunks = []

        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)

            if len(chunk_words) >= 50:  # Minimum chunk size
                chunk = {
                    "text": chunk_text,
                    "start_idx": i,
                    "end_idx": min(i + self.chunk_size, len(words)),
                    "word_count": len(chunk_words),
                    "metadata": metadata or {}
                }
                chunks.append(chunk)

        return chunks

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunk multiple documents"""

        all_chunks = []

        for doc_idx, doc in enumerate(documents):
            text = doc.get("content", doc.get("text", ""))
            metadata = doc.get("metadata", {})
            metadata["document_id"] = doc.get("id", f"doc_{doc_idx}")

            chunks = self.chunk_text(text, metadata)

            for chunk_idx, chunk in enumerate(chunks):
                chunk["chunk_id"] = f"{metadata['document_id']}_chunk_{chunk_idx}"
                all_chunks.append(chunk)

        return all_chunks

# Usage example
async def create_embedding_pipeline():
    """Create a complete embedding pipeline"""

    # Initialize services
    embedder = EmbeddingService()
    chunker = DocumentChunker(chunk_size=256, overlap=32)

    # Sample documents
    documents = [
        {
            "id": "doc1",
            "content": "Large language models are powerful AI systems that can generate human-like text...",
            "metadata": {"source": "ai_paper", "year": 2023}
        },
        {
            "id": "doc2",
            "content": "Retrieval-augmented generation combines retrieval and generation for better responses...",
            "metadata": {"source": "ml_research", "year": 2023}
        }
    ]

    # Chunk documents
    chunks = chunker.chunk_documents(documents)
    print(f"Created {len(chunks)} chunks")

    # Encode chunks
    chunk_texts = [chunk["text"] for chunk in chunks]
    embeddings = await embedder.batch_encode(chunk_texts)

    # Create embeddings database
    embeddings_db = []
    for chunk, embedding in zip(chunks, embeddings):
        embeddings_db.append({
            **chunk,
            "embedding": embedding
        })

    return embedder, embeddings_db
```

### Vector Database Implementation

```python
import faiss
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class VectorDatabase:
    """In-memory vector database using FAISS"""

    def __init__(self, dimension: int = 384, index_type: str = "IndexFlatIP"):
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.documents = []
        self.id_mapping = {}

        self._initialize_index()

    def _initialize_index(self):
        """Initialize FAISS index"""
        if self.index_type == "IndexFlatIP":
            # Inner product (cosine similarity with normalized vectors)
            self.index = faiss.IndexFlatIP(self.dimension)
        elif self.index_type == "IndexIVFFlat":
            # IVF with flat quantizer (faster for large datasets)
            quantizer = faiss.IndexFlatIP(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the vector database"""

        if not documents:
            return True

        try:
            # Extract embeddings and metadata
            embeddings = []
            doc_metadata = []

            for doc in documents:
                embedding = doc.get("embedding")
                if embedding is not None:
                    embeddings.append(embedding)
                    doc_metadata.append({
                        "id": doc.get("chunk_id", doc.get("id")),
                        "text": doc.get("text", ""),
                        "metadata": doc.get("metadata", {}),
                        "score": 0.0  # Will be set during search
                    })

            if not embeddings:
                logger.warning("No embeddings found in documents")
                return False

            # Convert to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)

            # Add to FAISS index
            self.index.add(embeddings_array)

            # Store document metadata
            start_idx = len(self.documents)
            self.documents.extend(doc_metadata)

            # Update ID mapping
            for i, doc in enumerate(doc_metadata):
                self.id_mapping[doc["id"]] = start_idx + i

            # Train IVF index if needed
            if hasattr(self.index, 'is_trained') and not self.index.is_trained:
                self.index.train(embeddings_array)

            logger.info(f"Added {len(documents)} documents to vector database")
            return True

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""

        try:
            # Ensure query embedding is correct shape
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)

            # Search FAISS index
            scores, indices = self.index.search(query_embedding.astype(np.float32), top_k)

            # Format results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.documents):  # Valid index
                    doc = self.documents[idx].copy()
                    doc["score"] = float(score)
                    results.append(doc)

            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def save_index(self, filepath: str):
        """Save FAISS index to disk"""
        try:
            faiss.write_index(self.index, filepath)
            logger.info(f"Saved index to {filepath}")

            # Save metadata
            metadata_file = filepath + ".metadata.json"
            metadata = {
                "dimension": self.dimension,
                "index_type": self.index_type,
                "documents": self.documents,
                "id_mapping": self.id_mapping,
                "created_at": str(datetime.now())
            }

            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save index: {e}")

    def load_index(self, filepath: str):
        """Load FAISS index from disk"""
        try:
            self.index = faiss.read_index(filepath)
            logger.info(f"Loaded index from {filepath}")

            # Load metadata
            metadata_file = filepath + ".metadata.json"
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

                self.dimension = metadata.get("dimension", self.dimension)
                self.index_type = metadata.get("index_type", self.index_type)
                self.documents = metadata.get("documents", [])
                self.id_mapping = metadata.get("id_mapping", {})

        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            "total_documents": len(self.documents),
            "dimension": self.dimension,
            "index_type": self.index_type,
            "index_size": self.index.ntotal if self.index else 0
        }

class ChromaVectorDB:
    """Vector database using Chroma"""

    def __init__(self, collection_name: str = "rag_documents", persist_directory: str = "./chroma_db"):
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.collection = self.client.get_or_create_collection(name=collection_name)
        except ImportError:
            raise ImportError("Chroma not installed. Install with: pip install chromadb")

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to Chroma collection"""

        try:
            ids = []
            embeddings = []
            metadatas = []
            documents_text = []

            for doc in documents:
                doc_id = doc.get("chunk_id", doc.get("id"))
                embedding = doc.get("embedding")
                text = doc.get("text", "")
                metadata = doc.get("metadata", {})

                if embedding is not None:
                    ids.append(doc_id)
                    embeddings.append(embedding.tolist() if hasattr(embedding, 'tolist') else embedding)
                    metadatas.append(metadata)
                    documents_text.append(text)

            if ids:
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    documents=documents_text
                )

            return True

        except Exception as e:
            logger.error(f"Failed to add documents to Chroma: {e}")
            return False

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search Chroma collection"""

        try:
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)

            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )

            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "score": results['distances'][0][i] if 'distances' in results else 0.0
                }
                formatted_results.append(result)

            return formatted_results

        except Exception as e:
            logger.error(f"Chroma search failed: {e}")
            return []

# Usage example
def create_vector_database(documents: List[Dict[str, Any]], use_chroma: bool = False):
    """Create and populate vector database"""

    if use_chroma:
        db = ChromaVectorDB()
    else:
        db = VectorDatabase(dimension=384)  # For MiniLM embeddings

    success = db.add_documents(documents)
    if success:
        logger.info("Vector database created successfully")
        return db
    else:
        raise RuntimeError("Failed to create vector database")
```

## Advanced Retrieval Mechanisms

### Hybrid Retrieval System

```python
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import logging

logger = logging.getLogger(__name__)

class BM25Retriever:
    """BM25-based sparse retrieval"""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents = []
        self.doc_freq = {}
        self.doc_lengths = []
        self.avg_doc_length = 0

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents for BM25 indexing"""

        try:
            self.documents = documents
            self.doc_lengths = [len(doc.get("text", "").split()) for doc in documents]
            self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0

            # Build document frequency
            self.doc_freq = {}
            for doc in documents:
                text = doc.get("text", "").lower()
                words = set(self._tokenize(text))
                for word in words:
                    self.doc_freq[word] = self.doc_freq.get(word, 0) + 1

            return True

        except Exception as e:
            logger.error(f"Failed to add documents to BM25: {e}")
            return False

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        # Remove punctuation and split
        text = re.sub(r'[^\w\s]', '', text)
        return text.lower().split()

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search using BM25"""

        try:
            query_terms = self._tokenize(query)
            scores = []

            N = len(self.documents)

            for i, doc in enumerate(self.documents):
                doc_text = doc.get("text", "")
                doc_terms = self._tokenize(doc_text)
                doc_length = self.doc_lengths[i]

                score = 0
                for term in query_terms:
                    if term in self.doc_freq:
                        tf = doc_terms.count(term)
                        df = self.doc_freq[term]
                        idf = np.log((N - df + 0.5) / (df + 0.5))

                        numerator = tf * (self.k1 + 1)
                        denominator = tf + self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length)
                        score += idf * numerator / denominator

                scores.append((i, score))

            # Sort by score
            scores.sort(key=lambda x: x[1], reverse=True)

            # Format results
            results = []
            for idx, score in scores[:top_k]:
                doc = self.documents[idx].copy()
                doc["score"] = score
                results.append(doc)

            return results

        except Exception as e:
            logger.error(f"BM25 search failed: {e}")
            return []

class HybridRetriever:
    """Combines dense and sparse retrieval"""

    def __init__(self, dense_retriever: BaseRetriever, sparse_retriever: BM25Retriever,
                 alpha: float = 0.5):
        self.dense_retriever = dense_retriever
        self.sparse_retriever = sparse_retriever
        self.alpha = alpha  # Weight for dense vs sparse

    async def retrieve(self, query: str, top_k: int = 5) -> List[RetrievedDocument]:
        """Hybrid retrieval combining dense and sparse methods"""

        try:
            # Get dense retrieval results
            dense_results = await self.dense_retriever.retrieve(query, top_k=top_k*2)

            # Get sparse retrieval results
            sparse_results = self.sparse_retriever.search(query, top_k=top_k*2)

            # Combine results using reciprocal rank fusion
            combined_results = self._reciprocal_rank_fusion(
                dense_results, sparse_results, top_k=top_k
            )

            return combined_results

        except Exception as e:
            logger.error(f"Hybrid retrieval failed: {e}")
            return []

    def _reciprocal_rank_fusion(self, dense_results: List[RetrievedDocument],
                               sparse_results: List[Dict[str, Any]], top_k: int) -> List[RetrievedDocument]:
        """Combine results using Reciprocal Rank Fusion"""

        # Create score mapping
        score_map = {}

        # Add dense results
        for rank, result in enumerate(dense_results):
            doc_id = result.chunk_id
            score = 1.0 / (rank + 60)  # RRF constant k=60
            score_map[doc_id] = {"dense_score": score, "result": result}

        # Add sparse results
        for rank, result in enumerate(sparse_results):
            doc_id = result.get("chunk_id", result.get("id"))
            score = 1.0 / (rank + 60)
            if doc_id in score_map:
                score_map[doc_id]["sparse_score"] = score
            else:
                score_map[doc_id] = {"sparse_score": score, "result": result}

        # Calculate combined scores
        final_results = []
        for doc_id, scores in score_map.items():
            dense_score = scores.get("dense_score", 0)
            sparse_score = scores.get("sparse_score", 0)

            # Weighted combination
            combined_score = self.alpha * dense_score + (1 - self.alpha) * sparse_score

            result = scores["result"]
            if isinstance(result, dict):
                result = RetrievedDocument(
                    content=result.get("text", ""),
                    score=combined_score,
                    metadata=result.get("metadata", {}),
                    source=result.get("source", "unknown"),
                    chunk_id=doc_id
                )
            else:
                result.score = combined_score

            final_results.append(result)

        # Sort by combined score
        final_results.sort(key=lambda x: x.score, reverse=True)

        return final_results[:top_k]

class QueryExpansionRetriever:
    """Retriever with query expansion capabilities"""

    def __init__(self, base_retriever: BaseRetriever, expansion_model=None):
        self.base_retriever = base_retriever
        self.expansion_model = expansion_model

    async def retrieve(self, query: str, top_k: int = 5, expand_query: bool = True) -> List[RetrievedDocument]:
        """Retrieve with optional query expansion"""

        if not expand_query or not self.expansion_model:
            return await self.base_retriever.retrieve(query, top_k)

        try:
            # Expand query
            expanded_queries = await self._expand_query(query)

            # Retrieve for each expanded query
            all_results = []
            for expanded_query in expanded_queries:
                results = await self.base_retriever.retrieve(expanded_query, top_k=top_k)
                all_results.extend(results)

            # Deduplicate and rerank
            deduplicated = self._deduplicate_results(all_results)
            reranked = self._rerank_results(deduplicated, query)

            return reranked[:top_k]

        except Exception as e:
            logger.error(f"Query expansion retrieval failed: {e}")
            return await self.base_retriever.retrieve(query, top_k)

    async def _expand_query(self, query: str) -> List[str]:
        """Expand query using various techniques"""

        expanded = [query]  # Original query

        # Simple synonym expansion (placeholder)
        synonyms = {
            "machine learning": ["ML", "artificial intelligence", "AI"],
            "neural network": ["neural net", "deep learning", "DL"],
            "database": ["data store", "data warehouse", "DB"]
        }

        for term, syns in synonyms.items():
            if term in query.lower():
                for syn in syns:
                    expanded_query = query.replace(term, syn)
                    expanded.append(expanded_query)

        # Add related terms (placeholder for more sophisticated expansion)
        if "python" in query.lower():
            expanded.append(query + " programming language")

        return expanded[:5]  # Limit expansions

    def _deduplicate_results(self, results: List[RetrievedDocument]) -> List[RetrievedDocument]:
        """Remove duplicate results"""

        seen_ids = set()
        deduplicated = []

        for result in results:
            if result.chunk_id not in seen_ids:
                seen_ids.add(result.chunk_id)
                deduplicated.append(result)

        return deduplicated

    def _rerank_results(self, results: List[RetrievedDocument], original_query: str) -> List[RetrievedDocument]:
        """Rerank results based on original query"""

        # Simple reranking based on query term frequency
        query_terms = set(original_query.lower().split())

        for result in results:
            text = result.content.lower()
            term_matches = sum(1 for term in query_terms if term in text)
            result.score *= (1 + term_matches * 0.1)  # Boost score

        results.sort(key=lambda x: x.score, reverse=True)
        return results
```

## Generation Integration

### RAG-Enhanced Generator

```python
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RAGGenerator(BaseGenerator):
    """Generator that integrates retrieved context"""

    def __init__(self, model_name: str = "microsoft/DialoGPT-medium",
                 max_context_length: int = 2048, device: str = "auto"):
        self.model_name = model_name
        self.max_context_length = max_context_length
        self.device = device if device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")

        self._load_model()

    def _load_model(self):
        """Load the generation model"""
        try:
            logger.info(f"Loading generation model: {self.model_name}")

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                load_in_8bit=True if self.device == "cuda" else False,
            )

            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
            )

            logger.info("Generation model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load generation model: {e}")
            raise

    async def generate(self, query: RAGQuery, **kwargs) -> str:
        """Generate response using retrieved context"""

        try:
            # Prepare context from retrieved documents
            context = self._prepare_context(query.context)

            # Create prompt with context
            prompt = self._create_prompt(query.question, context)

            # Generate response
            generation_kwargs = {
                "max_length": kwargs.get("max_length", 512),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "do_sample": kwargs.get("do_sample", True),
                "num_return_sequences": 1,
                "pad_token_id": self.tokenizer.eos_token_id,
                "return_full_text": False
            }

            # Override with any provided kwargs
            generation_kwargs.update(kwargs)

            logger.info(f"Generating response for query: {query.question[:50]}...")

            outputs = self.generator(prompt, **generation_kwargs)

            if outputs and len(outputs) > 0:
                generated_text = outputs[0]['generated_text'].strip()
                return generated_text
            else:
                return "I apologize, but I couldn't generate a response."

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return "I apologize, but an error occurred while generating the response."

    def _prepare_context(self, retrieved_docs: Optional[List[RetrievedDocument]]) -> str:
        """Prepare context string from retrieved documents"""

        if not retrieved_docs:
            return ""

        # Sort by score and take top documents
        sorted_docs = sorted(retrieved_docs, key=lambda x: x.score, reverse=True)
        top_docs = sorted_docs[:3]  # Limit context to top 3 documents

        context_parts = []
        for i, doc in enumerate(top_docs):
            # Format each document
            context_part = f"Document {i+1} (Score: {doc.score:.3f}):\n{doc.content}\n"
            context_parts.append(context_part)

        context = "\n".join(context_parts)

        # Truncate if too long
        if len(context) > self.max_context_length // 2:  # Leave room for question and generation
            context = context[:self.max_context_length // 2] + "..."

        return context

    def _create_prompt(self, question: str, context: str) -> str:
        """Create prompt with context and question"""

        if context:
            prompt = f"""Based on the following context, please answer the question.

Context:
{context}

Question: {question}

Answer:"""
        else:
            prompt = f"Question: {question}\n\nAnswer:"

        return prompt

class ChainOfThoughtGenerator(RAGGenerator):
    """Generator that uses chain-of-thought reasoning"""

    async def generate(self, query: RAGQuery, **kwargs) -> str:
        """Generate with chain-of-thought reasoning"""

        try:
            context = self._prepare_context(query.context)

            # Create chain-of-thought prompt
            prompt = self._create_cot_prompt(query.question, context)

            generation_kwargs = {
                "max_length": kwargs.get("max_length", 1024),  # Longer for CoT
                "temperature": kwargs.get("temperature", 0.3),  # Lower temperature for reasoning
                "top_p": kwargs.get("top_p", 0.9),
                "do_sample": kwargs.get("do_sample", True),
                "num_return_sequences": 1,
                "pad_token_id": self.tokenizer.eos_token_id,
                "return_full_text": False
            }

            generation_kwargs.update(kwargs)

            outputs = self.generator(prompt, **generation_kwargs)

            if outputs and len(outputs) > 0:
                full_response = outputs[0]['generated_text'].strip()

                # Extract final answer from chain-of-thought
                final_answer = self._extract_final_answer(full_response)
                return final_answer
            else:
                return "I apologize, but I couldn't generate a response."

        except Exception as e:
            logger.error(f"Chain-of-thought generation failed: {e}")
            return "I apologize, but an error occurred while generating the response."

    def _create_cot_prompt(self, question: str, context: str) -> str:
        """Create chain-of-thought prompt"""

        if context:
            prompt = f"""Based on the following context, please answer the question using step-by-step reasoning.

Context:
{context}

Question: {question}

Let's think step by step:
1. First, understand what the question is asking.
2. Look at the relevant information from the context.
3. Reason through the information logically.
4. Provide a clear, concise answer.

Reasoning:"""
        else:
            prompt = f"""Please answer the question using step-by-step reasoning.

Question: {question}

Let's think step by step:
1. Break down the question.
2. Consider what information is needed.
3. Reason through the answer logically.
4. Provide a final answer.

Reasoning:"""

        return prompt

    def _extract_final_answer(self, full_response: str) -> str:
        """Extract final answer from chain-of-thought response"""

        # Look for common patterns
        patterns = [
            r"Final Answer:\s*(.+)",
            r"Answer:\s*(.+)",
            r"Therefore,\s*(.+)",
            r"So,\s*(.+)"
        ]

        for pattern in patterns:
            import re
            match = re.search(pattern, full_response, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()

        # If no clear final answer, return the last paragraph
        paragraphs = full_response.split('\n\n')
        return paragraphs[-1].strip() if paragraphs else full_response.strip()

class MultiStepGenerator(RAGGenerator):
    """Generator that breaks down complex queries into steps"""

    async def generate(self, query: RAGQuery, **kwargs) -> str:
        """Generate response in multiple steps for complex queries"""

        try:
            # Determine if query needs multi-step reasoning
            if not self._is_complex_query(query.question):
                return await super().generate(query, **kwargs)

            # Step 1: Decompose the question
            decomposition = await self._decompose_question(query.question, query.context)

            # Step 2: Answer each sub-question
            step_answers = []
            for sub_question in decomposition["sub_questions"]:
                step_context = self._filter_context_for_question(query.context, sub_question)
                step_query = RAGQuery(question=sub_question, context=step_context)

                step_answer = await super().generate(step_query, max_length=256, **kwargs)
                step_answers.append({
                    "question": sub_question,
                    "answer": step_answer
                })

            # Step 3: Synthesize final answer
            synthesis_query = RAGQuery(
                question=f"Synthesize a comprehensive answer from these steps: {query.question}",
                context=query.context
            )

            synthesis_prompt = self._create_synthesis_prompt(query.question, step_answers)
            synthesis_query.question = synthesis_prompt

            final_answer = await super().generate(synthesis_query, **kwargs)

            return final_answer

        except Exception as e:
            logger.error(f"Multi-step generation failed: {e}")
            return await super().generate(query, **kwargs)

    def _is_complex_query(self, question: str) -> bool:
        """Determine if a query is complex enough for multi-step reasoning"""

        complex_indicators = [
            "compare", "contrast", "explain why", "how does",
            "what are the differences", "analyze", "evaluate",
            "multiple", "several", "various"
        ]

        question_lower = question.lower()
        return any(indicator in question_lower for indicator in complex_indicators)

    async def _decompose_question(self, question: str, context: Optional[List[RetrievedDocument]]) -> Dict[str, Any]:
        """Decompose complex question into simpler sub-questions"""

        # Simple decomposition logic (could be enhanced with a dedicated model)
        decomposition_prompt = f"""Break down this complex question into 2-3 simpler sub-questions:

Question: {question}

Sub-questions:
1."""

        # Use base generation for decomposition
        outputs = self.generator(decomposition_prompt, max_length=256, temperature=0.3)
        decomposition_text = outputs[0]['generated_text'].strip()

        # Parse sub-questions
        lines = decomposition_text.split('\n')
        sub_questions = []

        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering
                clean_line = re.sub(r'^\d+\.?\s*', '', line)
                clean_line = re.sub(r'^-\s*', '', clean_line)
                if clean_line:
                    sub_questions.append(clean_line)

        return {
            "original_question": question,
            "sub_questions": sub_questions[:3]  # Limit to 3 sub-questions
        }

    def _filter_context_for_question(self, context: Optional[List[RetrievedDocument]],
                                   question: str) -> Optional[List[RetrievedDocument]]:
        """Filter context relevant to a specific sub-question"""

        if not context:
            return context

        # Simple filtering based on keyword overlap
        question_terms = set(question.lower().split())

        filtered_context = []
        for doc in context:
            doc_terms = set(doc.content.lower().split())
            overlap = len(question_terms.intersection(doc_terms))

            if overlap > 0:
                # Adjust score based on relevance
                adjusted_doc = RetrievedDocument(
                    content=doc.content,
                    score=doc.score * (overlap / len(question_terms)),
                    metadata=doc.metadata,
                    source=doc.source,
                    chunk_id=doc.chunk_id
                )
                filtered_context.append(adjusted_doc)

        # Sort by adjusted score
        filtered_context.sort(key=lambda x: x.score, reverse=True)
        return filtered_context[:3]  # Return top 3 relevant docs

    def _create_synthesis_prompt(self, original_question: str, step_answers: List[Dict[str, Any]]) -> str:
        """Create prompt for synthesizing final answer"""

        steps_text = "\n".join([
            f"Step {i+1}: {step['question']}\nAnswer: {step['answer']}"
            for i, step in enumerate(step_answers)
        ])

        synthesis_prompt = f"""Based on the following step-by-step analysis, provide a comprehensive final answer to: {original_question}

Step-by-step analysis:
{steps_text}

Final comprehensive answer:"""

        return synthesis_prompt
```

## RAG Evaluation and Optimization

### Evaluation Framework

```python
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
import re
import logging
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class RAGEvaluator:
    """Comprehensive evaluation framework for RAG systems"""

    def __init__(self):
        self.metrics_history = defaultdict(list)

    def evaluate_retrieval(self, queries: List[str], retrieved_docs: List[List[RetrievedDocument]],
                          ground_truth: List[List[str]]) -> Dict[str, float]:
        """Evaluate retrieval quality"""

        if len(queries) != len(retrieved_docs) or len(queries) != len(ground_truth):
            raise ValueError("Queries, retrieved docs, and ground truth must have same length")

        retrieval_metrics = {
            "precision@1": [],
            "precision@3": [],
            "precision@5": [],
            "recall@1": [],
            "recall@3": [],
            "recall@5": [],
            "mrr": [],  # Mean Reciprocal Rank
            "map": []   # Mean Average Precision
        }

        for query_docs, gt_docs in zip(retrieved_docs, ground_truth):
            retrieved_ids = [doc.chunk_id for doc in query_docs]
            gt_ids = set(gt_docs)

            # Calculate precision and recall at different k
            for k in [1, 3, 5]:
                retrieved_k = retrieved_ids[:k]
                relevant_retrieved = len(set(retrieved_k) & gt_ids)

                precision = relevant_retrieved / k if k > 0 else 0
                recall = relevant_retrieved / len(gt_ids) if gt_ids else 0

                retrieval_metrics[f"precision@{k}"].append(precision)
                retrieval_metrics[f"recall@{k}"].append(recall)

            # Calculate MRR
            mrr = 0
            for rank, doc_id in enumerate(retrieved_ids, 1):
                if doc_id in gt_ids:
                    mrr = 1.0 / rank
                    break
            retrieval_metrics["mrr"].append(mrr)

            # Calculate AP (Average Precision)
            ap = 0
            relevant_found = 0
            for rank, doc_id in enumerate(retrieved_ids, 1):
                if doc_id in gt_ids:
                    relevant_found += 1
                    ap += relevant_found / rank
            ap = ap / len(gt_ids) if gt_ids else 0
            retrieval_metrics["map"].append(ap)

        # Calculate averages
        avg_metrics = {}
        for metric_name, values in retrieval_metrics.items():
            avg_metrics[metric_name] = np.mean(values)

        # Store in history
        for metric, value in avg_metrics.items():
            self.metrics_history[f"retrieval_{metric}"].append(value)

        return avg_metrics

    def evaluate_generation(self, generated_answers: List[str], reference_answers: List[str],
                          contexts: List[List[RetrievedDocument]] = None) -> Dict[str, float]:
        """Evaluate generation quality"""

        generation_metrics = {}

        # BLEU score (simplified implementation)
        generation_metrics["bleu_score"] = self._calculate_bleu(generated_answers, reference_answers)

        # ROUGE scores (simplified)
        rouge_scores = self._calculate_rouge(generated_answers, reference_answers)
        generation_metrics.update(rouge_scores)

        # Semantic similarity (placeholder - would use embedding similarity)
        generation_metrics["semantic_similarity"] = self._calculate_semantic_similarity(
            generated_answers, reference_answers
        )

        # Factual consistency
        if contexts:
            generation_metrics["factual_consistency"] = self._evaluate_factual_consistency(
                generated_answers, contexts
            )

        # Answer relevance
        generation_metrics["answer_relevance"] = self._evaluate_answer_relevance(
            generated_answers, contexts
        )

        # Store in history
        for metric, value in generation_metrics.items():
            self.metrics_history[f"generation_{metric}"].append(value)

        return generation_metrics

    def evaluate_end_to_end(self, rag_responses: List[RAGResponse],
                          ground_truth_answers: List[str]) -> Dict[str, float]:
        """Evaluate end-to-end RAG performance"""

        generated_answers = [response.answer for response in rag_responses]
        retrieved_contexts = [response.retrieved_docs for response in rag_responses]

        # Generation quality
        gen_metrics = self.evaluate_generation(generated_answers, ground_truth_answers, retrieved_contexts)

        # Retrieval quality (if ground truth retrieval available)
        # This would require ground truth retrieved documents

        # Response quality metrics
        response_metrics = {
            "avg_response_length": np.mean([len(ans.split()) for ans in generated_answers]),
            "avg_confidence": np.mean([r.confidence_score for r in rag_responses]),
            "response_diversity": self._calculate_response_diversity(generated_answers)
        }

        # Combine all metrics
        e2e_metrics = {**gen_metrics, **response_metrics}

        # Store in history
        for metric, value in e2e_metrics.items():
            self.metrics_history[f"e2e_{metric}"].append(value)

        return e2e_metrics

    def _calculate_bleu(self, generated: List[str], reference: List[str]) -> float:
        """Calculate BLEU score (simplified n-gram matching)"""

        def get_ngrams(text: str, n: int) -> Dict[str, int]:
            words = text.split()
            ngrams = {}
            for i in range(len(words) - n + 1):
                ngram = tuple(words[i:i+n])
                ngrams[ngram] = ngrams.get(ngram, 0) + 1
            return ngrams

        total_bleu = 0
        for gen, ref in zip(generated, reference):
            gen_1gram = get_ngrams(gen, 1)
            ref_1gram = get_ngrams(ref, 1)

            # Calculate unigram precision
            matching_count = 0
            total_count = 0

            for ngram, count in gen_1gram.items():
                matching_count += min(count, ref_1gram.get(ngram, 0))
                total_count += count

            precision = matching_count / total_count if total_count > 0 else 0

            # Brevity penalty
            gen_len = len(gen.split())
            ref_len = len(ref.split())
            brevity_penalty = min(1.0, gen_len / ref_len) if ref_len > 0 else 0

            bleu = brevity_penalty * precision
            total_bleu += bleu

        return total_bleu / len(generated) if generated else 0

    def _calculate_rouge(self, generated: List[str], reference: List[str]) -> Dict[str, float]:
        """Calculate ROUGE scores (simplified)"""

        def rouge_n(generated: str, reference: str, n: int) -> float:
            gen_ngrams = set(tuple(generated.split()[i:i+n]) for i in range(len(generated.split()) - n + 1))
            ref_ngrams = set(tuple(reference.split()[i:i+n]) for i in range(len(reference.split()) - n + 1))

            overlap = len(gen_ngrams & ref_ngrams)
            return overlap / len(ref_ngrams) if ref_ngrams else 0

        rouge1_scores = []
        rouge2_scores = []

        for gen, ref in zip(generated, reference):
            rouge1_scores.append(rouge_n(gen, ref, 1))
            rouge2_scores.append(rouge_n(gen, ref, 2))

        return {
            "rouge1": np.mean(rouge1_scores),
            "rouge2": np.mean(rouge2_scores)
        }

    def _calculate_semantic_similarity(self, generated: List[str], reference: List[str]) -> float:
        """Calculate semantic similarity (placeholder)"""
        # In practice, use embedding similarity
        return 0.75  # Placeholder

    def _evaluate_factual_consistency(self, answers: List[str], contexts: List[List[RetrievedDocument]]) -> float:
        """Evaluate factual consistency with retrieved context"""

        consistency_scores = []

        for answer, context_docs in zip(answers, contexts):
            if not context_docs:
                consistency_scores.append(0.0)
                continue

            # Simple consistency check: count overlapping key terms
            answer_terms = set(re.findall(r'\b\w+\b', answer.lower()))
            context_text = ' '.join([doc.content for doc in context_docs])
            context_terms = set(re.findall(r'\b\w+\b', context_text.lower()))

            overlap = len(answer_terms & context_terms)
            total_terms = len(answer_terms)

            consistency = overlap / total_terms if total_terms > 0 else 0
            consistency_scores.append(consistency)

        return np.mean(consistency_scores)

    def _evaluate_answer_relevance(self, answers: List[str], contexts: List[List[RetrievedDocument]]) -> float:
        """Evaluate answer relevance to the query (placeholder)"""
        # In practice, this would use query-answer relevance models
        return 0.8  # Placeholder

    def _calculate_response_diversity(self, answers: List[str]) -> float:
        """Calculate diversity of generated answers"""

        if len(answers) < 2:
            return 0.0

        # Simple diversity based on unique n-grams
        all_ngrams = set()
        total_ngrams = 0

        for answer in answers:
            words = answer.split()
            for i in range(len(words) - 1):
                ngram = tuple(words[i:i+2])
                all_ngrams.add(ngram)
                total_ngrams += 1

        return len(all_ngrams) / total_ngrams if total_ngrams > 0 else 0

    def get_evaluation_history(self) -> Dict[str, List[float]]:
        """Get evaluation metrics history"""
        return dict(self.metrics_history)

    def save_evaluation_report(self, filepath: str, latest_metrics: Dict[str, float]):
        """Save evaluation report"""

        report = {
            "timestamp": str(datetime.now()),
            "latest_metrics": latest_metrics,
            "historical_averages": {
                metric: np.mean(values) if values else 0.0
                for metric, values in self.metrics_history.items()
            },
            "historical_trends": dict(self.metrics_history)
        }

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Evaluation report saved to {filepath}")

class RAGOptimizer:
    """Optimization system for RAG pipelines"""

    def __init__(self, evaluator: RAGEvaluator):
        self.evaluator = evaluator
        self.optimization_trials = []

    def optimize_retrieval(self, retriever: BaseRetriever, validation_queries: List[str],
                          validation_contexts: List[List[RetrievedDocument]]) -> Dict[str, Any]:
        """Optimize retrieval parameters"""

        # Parameter grid for optimization
        param_grid = {
            "top_k": [3, 5, 10],
            "similarity_threshold": [0.0, 0.1, 0.2],
            "rerank": [True, False]
        }

        best_params = None
        best_score = 0

        # Grid search (simplified)
        import itertools
        for params in itertools.product(*param_grid.values()):
            param_dict = dict(zip(param_grid.keys(), params))

            # Evaluate with these parameters
            # This would require running retrieval with different params
            score = self._evaluate_param_combination(param_dict, retriever, validation_queries)

            if score > best_score:
                best_score = score
                best_params = param_dict

            self.optimization_trials.append({
                "params": param_dict,
                "score": score,
                "timestamp": str(datetime.now())
            })

        return {
            "best_params": best_params,
            "best_score": best_score,
            "trials": self.optimization_trials
        }

    def _evaluate_param_combination(self, params: Dict[str, Any], retriever: BaseRetriever,
                                  queries: List[str]) -> float:
        """Evaluate a parameter combination"""

        # Placeholder scoring based on parameters
        # In practice, run actual retrieval and evaluation
        score = 0.5  # Base score

        if params["top_k"] == 5:
            score += 0.1
        if params["similarity_threshold"] == 0.1:
            score += 0.05
        if params["rerank"]:
            score += 0.1

        return score

    def optimize_generation(self, generator: BaseGenerator, test_queries: List[RAGQuery],
                          reference_answers: List[str]) -> Dict[str, Any]:
        """Optimize generation parameters"""

        param_grid = {
            "temperature": [0.1, 0.3, 0.7, 1.0],
            "top_p": [0.9, 0.95],
            "max_length": [256, 512, 1024]
        }

        best_params = None
        best_score = 0

        import itertools
        for params in itertools.product(*param_grid.values()):
            param_dict = dict(zip(param_grid.keys(), params))

            # Generate answers with these parameters
            generated_answers = []
            for query in test_queries:
                try:
                    answer = await generator.generate(query, **param_dict)
                    generated_answers.append(answer)
                except:
                    generated_answers.append("")

            # Evaluate
            if generated_answers and reference_answers:
                metrics = self.evaluator.evaluate_generation(generated_answers, reference_answers)
                score = metrics.get("semantic_similarity", 0) * 0.4 + \
                       metrics.get("factual_consistency", 0) * 0.6

                if score > best_score:
                    best_score = score
                    best_params = param_dict

        return {
            "best_params": best_params,
            "best_score": best_score
        }
```

This comprehensive guide covers RAG fundamentals, vector databases, advanced retrieval mechanisms, generation integration, and evaluation frameworks. The code examples demonstrate production-ready implementations for building scalable RAG systems with proper evaluation and optimization capabilities.
