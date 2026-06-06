# LangChain Framework

## Overview

LangChain is an open-source framework for building applications powered by large language models (LLMs). It provides modular components for prompt management, memory, chains, agents, and retrieval — making it straightforward to build complex LLM-powered workflows.

## Core Components

### Chains
Chains combine multiple components into a single pipeline. A simple chain might take user input, format it into a prompt, send it to an LLM, and return the result. More complex chains can include retrieval steps, tool usage, and conditional logic.

### Retrievers
Retrievers fetch relevant documents from a data source given a query. LangChain supports vector store retrievers (ChromaDB, Pinecone, FAISS), keyword retrievers (BM25), and ensemble retrievers that combine multiple strategies.

### Agents
Agents use LLMs to decide which tools to invoke and in what order. They can dynamically choose between web search, database queries, calculators, or custom tools based on the user's question. ReAct and function-calling are common agent patterns.

### Memory
Memory modules allow chains to maintain state across interactions. ConversationBufferMemory stores the full conversation history, while ConversationSummaryMemory compresses older messages into a running summary.

## RAG with LangChain

Retrieval-Augmented Generation (RAG) is one of the most popular LangChain patterns. The flow is:
1. Load documents using document loaders (PDF, markdown, web pages)
2. Split documents into chunks using text splitters
3. Embed chunks and store in a vector database
4. At query time, retrieve relevant chunks via similarity search
5. Pass retrieved chunks as context to the LLM for answer generation

## Why LangChain?

- Reduces boilerplate for LLM application development
- Provides a unified interface across different LLM providers (OpenAI, Anthropic, Hugging Face)
- Rich ecosystem of integrations with vector stores, tools, and data sources
- Active community and frequent updates
