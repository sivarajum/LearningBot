# Vector Databases - Interview Questions & Answers

This file contains 24 interview-style questions with detailed answers, examples, and code snippets focusing on vector databases: beginner (Q1-Q8), intermediate (Q9-Q16), advanced (Q17-Q24).

---

## Beginner Level (Q1-Q8)

Q1: What is a vector database and when would you use one?

Answer:
- A vector database stores and indexes high-dimensional vectors (embeddings) used for semantic similarity search. Use-cases: RAG, semantic search, recommendations, image search, anomaly detection.

Code (simple explanation using a toy DB):
```python
# Toy vector store
class SimpleStore:
	def __init__(self):
		self.vectors = {}
	def add(self, id, vec):
		self.vectors[id] = vec
	def search(self, q, k=5):
		# naive linear scan
		import numpy as np
		sims = []
		for i,v in self.vectors.items():
			sims.append((i, np.dot(q,v)/(np.linalg.norm(q)*np.linalg.norm(v)+1e-8)))
		return sorted(sims, key=lambda x: x[1], reverse=True)[:k]

store = SimpleStore()
store.add('a', [0.1,0.2,0.3])
print(store.search([0.1,0.2,0.3]))
```

Q2: What is an embedding? How do you produce one?

Answer:
- An embedding is a numeric vector representation of text, image, or other data produced by ML models (transformers, sentence encoders). Use models like OpenAI embeddings, SentenceTransformers, Cohere.

Code (OpenAI embeddings example):
```python
from openai import OpenAI
client = OpenAI()
resp = client.embeddings.create(model='text-embedding-3-small', input='Hello world')
vector = resp.data[0].embedding
print(len(vector))
```

Q3: Which similarity metrics are common and why?

Answer:
- Cosine similarity: common for normalized embeddings, scale-invariant.
- Euclidean (L2): distance-based, useful for certain embeddings.
- Dot product: used for non-normalized vectors.

Example:
```python
import numpy as np
v1 = np.array([0.1,0.2,0.3])
v2 = np.array([0.11,0.19,0.31])
cosine = np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2))
print('cosine', cosine)
```

Q4: What is ANNS and why not just brute-force search?

Answer:
- ANNS = Approximate Nearest Neighbor Search. Brute force is O(n) and too slow for millions/billions of vectors. ANNS algorithms (HNSW, IVF, PQ) provide sub-linear or faster search with acceptable accuracy trade-offs.

Q5: What is HNSW?

Answer:
- HNSW (Hierarchical Navigable Small World) builds a graph overlay with multiple layers, using greedy search to find nearest neighbors quickly. Pros: fast and accurate. Cons: memory-intensive.

Q6: How do you store metadata with vectors and why?

Answer:
- Metadata (source, timestamp, category) is stored alongside vectors to enable filtering and context. You can filter by metadata during queries to restrict results.

Example (Pinecone upsert with metadata):
```python
from pinecone import Pinecone
pc = Pinecone(api_key='KEY')
idx = pc.Index('docs')
idx.upsert([('id1', [0.1,0.2,...], {'source':'wiki', 'year':2023})])
```

Q7: What are common pitfalls for beginners?

Answer:
- Using too small/large chunk sizes, ignoring metadata, not normalizing vectors, using expensive settings in production, not monitoring recall/precision.

Q8: What's the simplest vector DB to start with?

Answer:
- Chroma or a simple local FAISS instance; both are easy for prototyping.

---

## Intermediate Level (Q9-Q16)

Q9: How do you choose an index type for your workload?

Answer:
- Consider: dataset size, required latency, memory available, update frequency. HNSW for low latency & high accuracy; IVF or PQ for very large datasets; LSH for simple approximate needs.

Q10: What is reranking and when do you use it?

Answer:
- Reranking re-scores candidate results using a more accurate (often more expensive) model, like a cross-encoder or LLM, to improve final ordering after a fast initial retrieval.

Example (reranking pseudo-code):
```python
candidates = vector_search(q, top_k=50)
reranked = cross_encoder.rank(q, candidates)
return reranked[:5]
```

Q11: How to support metadata filtering efficiently?

Answer:
- Use vector DBs that support metadata filtering at query time (Pinecone, Weaviate, Qdrant). Store metadata as structured fields. For large scale, maintain inverted indices for metadata filters.

Q12: How do you handle updates and deletes at scale?

Answer:
- Use incremental upserts; for deletes mark tombstones if immediate deletion is expensive; periodically compact/archive obsolete vectors; use versioning.

Q13: How can you compress vectors to save memory?

Answer:
- Use PQ (product quantization), OPQ (optimized PQ), int8 quantization, or float16 storage. Trade accuracy vs memory.

Q14: How to evaluate vector DB accuracy?

Answer:
- Metrics: precision@k, recall@k, MAP, NDCG. Use ground truth retrieval sets, compute metrics comparing retrieved vs expected results.

Q15: What is hybrid search? Provide use-cases.

Answer:
- Hybrid search combines keyword matching plus semantic vector search. Use-cases: e-commerce (product exact matches + similar items), legal search (exact phrases + related docs).

Q16: How to monitor and alert on retrieval quality?

Answer:
- Monitor precision/recall if labelled queries exist; log top results, feedback loop for user clicks; track latency, throughput, error rates. Set alerts for drops in quality/latency spikes.

---

## Advanced Level (Q17-Q24)

Q17: How to design a vector DB system for billions of vectors?

Answer:
- Use sharding, distributed indices (Milvus, Pinecone), partition by time or namespaces, ensure horizontal scaling, use PQ and IVF to save memory, maintain cold/hot tiers, parallelize queries across shards and merge results.

Q18: What is semantic caching?

Answer:
- Cache results based on semantic equivalence rather than exact queries. Use approximation or clustering of query vectors so similar queries hit the same cache entry.

Q19: How to build multi-modal vector search?

Answer:
- Normalize heterogeneous embeddings (text, image, audio) into a shared space or use separate indexes with cross-modal retrieval layers, apply fusion/reranking.

Q20: How to do A/B testing for retrieval improvements?

Answer:
- Run parallel experiments with traffic split; measure business metrics (click-through, conversion) and technical metrics (precision@k, latency). Keep statistical significance and experiment length in mind.

Q21: How do you combine vector DBs with databases (RDB/NoSQL)?

Answer:
- Keep metadata in RDB/NoSQL; store vector IDs in RDB for joins; use vector DB for similarity search returning IDs which you fetch from primary DB for full records.

Q22: How to secure vector databases in production?

Answer:
- Use network isolation, authentication, encryption at rest/in transit, access control on metadata, logging/monitoring, rotate keys, use VPCs.

Q23: What are challenges of deploying self-hosted vector DBs?

Answer:
- Ops complexity (scaling, high availability), resource-heavy indices (HNSW memory), upgrades, backups, data migrations, maintaining latency at scale.

Q24: Future directions: What features are emerging?

Answer:
- Vector DBs adding: multimodal embeddings, built-in retrievers/rerankers, real-time vector pipelines, cloud-native serverless options, stronger ML integrations, privacy-preserving search, on-device vector stores.

---

## Quick Cheatsheet: Common Commands & Patterns

- Upsert (batch), Query with filter, Fetch by ID, Delete by ID, Rebuild index (bulk), Export/backup.
- Common optimization knobs: ef, ef_construction (HNSW), n_probes (IVF), PQ parameters.

