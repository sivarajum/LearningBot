# RAG Patterns and Best Practices

## What is RAG?

Retrieval-Augmented Generation (RAG) is a technique that enhances LLM responses by providing relevant external knowledge as context. Instead of relying solely on the model's training data, RAG retrieves pertinent documents from a knowledge base and includes them in the prompt, leading to more accurate and grounded answers.

## Architecture Patterns

### Basic RAG
The simplest pattern: embed a query, retrieve top-k similar documents from a vector store, and pass them as context to an LLM. This works well for straightforward question-answering over a single knowledge base.

### Multi-Stage RAG
Adds a re-ranking step after initial retrieval. The first stage uses fast vector similarity search to get a broad set of candidates. A cross-encoder model then re-ranks these candidates for higher precision before sending to the LLM.

### Hybrid RAG
Combines dense retrieval (vector embeddings) with sparse retrieval (keyword matching like BM25). This captures both semantic similarity and exact keyword matches, improving recall for queries that contain specific terms or identifiers.

### Agentic RAG
Uses an LLM agent to decide when and how to retrieve information. The agent can reformulate queries, search multiple data sources, and iteratively refine its search strategy before generating a final answer.

## Chunking Strategies

Choosing the right chunk size is critical for RAG performance:
- **Small chunks (200-500 tokens)**: Higher precision, more specific matches, but may lose context.
- **Large chunks (1000-2000 tokens)**: More context per chunk, but may include irrelevant information and reduce retrieval precision.
- **Overlap**: Adding 10-20% overlap between chunks ensures that information at chunk boundaries is not lost.

## Evaluation Metrics

- **Retrieval Precision**: What fraction of retrieved documents are actually relevant?
- **Retrieval Recall**: What fraction of all relevant documents were retrieved?
- **Answer Faithfulness**: Does the generated answer accurately reflect the retrieved context?
- **Answer Relevance**: Does the answer actually address the user's question?

## Common Pitfalls

1. **Chunk size mismatch**: Chunks that are too large dilute relevance; chunks that are too small lose context.
2. **Missing metadata**: Not storing source information makes it impossible to cite sources or filter results.
3. **Ignoring embedding model choice**: Different embedding models have different strengths. Domain-specific fine-tuned models often outperform general-purpose ones.
4. **No fallback handling**: Always handle the case where no relevant documents are found gracefully.
