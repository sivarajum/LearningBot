# Vector Databases - Learning Guide & Paths

Three recommended learning paths: Fast Track (2 weeks), Comprehensive (6-8 weeks), Interview Prep (1-2 weeks). Each path contains weekly/day-by-day milestones, success criteria, and resources.

---

## PATH 1: Fast Track (1-2 weeks)

Goal: Build a working vector search system quickly and understand core trade-offs.

Week 1 — Foundation
- Day 1: Concepts & Setup (3 hours)
  - Read: `what.md` - Overview, Core Concepts
  - Install: Chroma / FAISS locally
  - Try: Run a simple embedding (OpenAI or local SBERT)
- Day 2: Ingest & Chunking (4 hours)
  - Implement chunker for long docs (300-500 words)
  - Create embeddings and upsert 1000 doc vectors
- Day 3: Basic Querying (3 hours)
  - Implement simple search (top-k) and return results
  - Add basic metadata filtering
- Day 4: Hybrid + Rerank (4 hours)
  - Add keyword search + vector merge
  - Try a small reranker (cross-encoder or LLM)
- Day 5: Deploy a simple API (3 hours)
  - Wrap search in FastAPI/Flask and serve queries

Success Criteria (end of Week 1):
- Working prototype that returns relevant results for queries
- Basic knowledge of index types and when to use them

Optional Week 2 — Polish
- Add monitoring, caching, small optimizations, and cost check.

---

## PATH 2: Comprehensive Mastery (6-8 weeks)

Goal: Become an expert who can design, build, and operate production vector DB systems.

Phase 1 — Fundamentals (Week 1-2)
- Read entire `what.md`
- Run all beginner examples
- Build simple pipeline: chunk -> embed -> upsert -> query

Phase 2 — Retrieval & Quality (Week 3-4)
- Implement HNSW and IVF experiments
- Implement reranking and hybrid search
- Build ground-truth test sets and measure precision@k/recall@k

Phase 3 — Scaling & Production (Week 5-6)
- Learn sharding and partitioning strategies
- Implement caching and semantic cache
- Deploy on Milvus or managed Pinecone
- Setup monitoring and alerts (precision/latency/cost)

Phase 4 — Advanced (Week 7-8)
- Multimodal retrieval (images + text)
- Privacy-preserving search (Pseudonymization, differential privacy)
- Cost optimizations (quantization, batching)
- Large-scale evaluation & user feedback loops

Success Criteria:
- Can design system for 100M+ vectors
- Can tune index for desired latency/accuracy
- Implemented monitoring and cost controls
- Demonstrated measurable retrieval improvements

---

## PATH 3: Interview Preparation (1-2 weeks)

Goal: Prepare to answer vector database interview questions and design problems.

Week 1 — Q&A and Core Coding
- Day 1-2: Memorize core concepts (what.md)
- Day 3-4: Code sample problems: implement naive search, hybrid search, reranker
- Day 5: Whiteboard design: shard+cache+metrics

Week 2 — Mock Interviews & System Design
- Run 3 mock interviews focusing on system design and trade-offs
- Practice explaining index parameter impacts (ef, n_probes, PQ m/nbits)

Success Criteria:
- Confidently answer Q1-Q24 from `Interview.md`
- Can design a production system under constraints
- Can explain trade-offs succinctly

---

## Recommended Tools & Resources
- Tutorials: Milvus docs, Pinecone docs, Weaviate docs, FAISS guide
- Libraries: `sentence-transformers`, `openai` (embeddings), `chromadb`, `qdrant-client`
- Datasets: MS MARCO, Natural Questions, custom corpora
- Evaluation: trec_eval, pytrec_eval

---

## Checkpoints & Metrics
- Prototype: returns relevant results for 80% of sample queries
- Intermediate: precision@5 >= 0.6 on ground truth set
- Advanced: stable <200ms p95 latency on production hardware

---

## Quick Start Commands
```bash
# Create Python venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run a quick demo (Chroma local)
python -c "from openai import OpenAI; print('install complete')"
```

