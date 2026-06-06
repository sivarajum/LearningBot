# RAG Stack Choices
- Embeddings: Vertex vs OpenAI vs OSS; consider cost/latency/IP.
- Vector stores: managed (AlloyDB pgvector) vs self-hosted.
- Inference: hosted LLM vs OSS on Run/GKE.
- Decision: speed to market -> hosted; control/IP -> OSS; DB residency -> pgvector.
