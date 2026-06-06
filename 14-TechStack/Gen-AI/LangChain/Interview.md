# LangChain Interview Questions and Answers

## Beginner Level Questions

### Q1: What is LangChain and what problem does it solve?

**Answer:**

LangChain is an open-source Python framework for building applications powered by large language models (LLMs). It abstracts away the complexity of working with LLMs by providing:

- **Unified Interface**: Work with OpenAI, Claude, Llama, and other models through a single API
- **Component Composition**: Combine LLMs, prompts, memory, tools, and retrievers into chains
- **Prompt Management**: Template and reuse complex prompts
- **Memory Systems**: Maintain conversation context automatically

**Problem It Solves:**
Without LangChain, building even simple LLM applications requires 500+ lines of boilerplate code for:
- API integration with multiple providers
- Prompt engineering and versioning
- Conversation history management
- Tool integration
- Error handling and retries

With LangChain, you write clean, reusable code in just 50 lines.

**Example:**
```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4")
prompt = ChatPromptTemplate.from_template("Explain {concept}")
chain = prompt | llm

result = chain.invoke({"concept": "machine learning"})
print(result.content)
```

---

### Q2: What are the core components of LangChain?

**Answer:**

The main building blocks are:

1. **LLMs**: The language models (OpenAI, Anthropic, Llama, etc.)
2. **Prompts**: Templates for instructions to the LLM
3. **Chains**: Sequences of operations (LLM calls, tools, logic)
4. **Memory**: Maintains conversation history and context
5. **Tools**: External functions the LLM can call
6. **Retrievers**: Fetch relevant documents for RAG
7. **Output Parsers**: Extract structured data from responses
8. **Agents**: Autonomous systems that decide when to use tools

**Visual Relationship:**
```
User Input → Prompt Template → LLM → Output Parser → Response
                ↑
            Memory (context)
                ↓
            Tools (external actions)
```

---

### Q3: How do you install and configure LangChain?

**Answer:**

**Installation:**
```bash
# Core library
pip install langchain

# With OpenAI
pip install langchain-openai

# With community integrations
pip install langchain-community

# Vector stores
pip install langchain-chroma
```

**Configuration:**
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

os.environ["OPENAI_API_KEY"] = "sk-..."
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "..."

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4", temperature=0.7)
```

---

### Q4: What is LCEL (LangChain Expression Language)?

**Answer:**

LCEL is a declarative way to build chains using the pipe operator (`|`). It's more readable and maintainable than traditional syntax.

**Traditional Way:**
```python
from langchain.chains import LLMChain

chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run(input="hello")
```

**LCEL Way:**
```python
chain = prompt | llm | output_parser
result = chain.invoke({"input": "hello"})
```

**Benefits:**
- More intuitive and Pythonic
- Built-in streaming support
- Better error handling
- Easier debugging

---

### Q5: Explain the difference between LLMs, ChatModels, and local models in LangChain

**Answer:**

| Type | Example | Use Case |
|------|---------|----------|
| **LLM** | OpenAI's text-davinci | Text completion, token prediction |
| **ChatModel** | GPT-4, Claude | Conversational, message-based |
| **Local** | Llama via Ollama | Privacy, offline, cost-effective |

**Code:**
```python
from langchain_openai import OpenAI, ChatOpenAI
from langchain_community.llms import Ollama

# Text completion
llm = OpenAI(model="text-davinci-003")

# Chat model (recommended)
chat = ChatOpenAI(model="gpt-4")

# Local model
local_llm = Ollama(model="llama2")
```

ChatModels are preferred for most modern applications.

---

### Q6: How do you handle API errors and retries in LangChain?

**Answer:**

LangChain has built-in retry mechanisms:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4",
    max_retries=3,           # Retry up to 3 times
    timeout=30,              # 30-second timeout
    temperature=0.7
)

result = llm.invoke("Your prompt")
```

**Using Callbacks for Custom Error Handling:**
```python
from langchain.callbacks import BaseCallbackHandler

class ErrorHandlingCallback(BaseCallbackHandler):
    def on_llm_error(self, error, **kwargs):
        print(f"LLM Error: {error}")
        # Custom error handling logic

llm = ChatOpenAI(callbacks=[ErrorHandlingCallback()])
```

---

### Q7: What are the different types of memory in LangChain?

**Answer:**

| Memory Type | Description | Use Case |
|-------------|-------------|----------|
| **Buffer** | Stores all messages | Short conversations |
| **Summary** | Summarizes old messages | Long conversations |
| **Token-based** | Limits by token count | Cost control |
| **Entity** | Tracks entities mentioned | Multi-turn conversations with context |
| **Custom** | User-defined | Special requirements |

**Example:**
```python
from langchain.memory import ConversationSummaryMemory, ConversationBufferMemory

# Stores all messages
buffer_memory = ConversationBufferMemory()

# Summarizes when too long
summary_memory = ConversationSummaryMemory(llm=llm)

# Token-limited
from langchain.memory import ConversationTokenBufferMemory
token_memory = ConversationTokenBufferMemory(llm=llm, max_token_limit=500)
```

---

### Q8: How do you create a simple chatbot with LangChain?

**Answer:**

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI

# Setup
llm = ChatOpenAI(model="gpt-4")
memory = ConversationBufferMemory()

# Create conversation
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# Multi-turn conversation
print(conversation.invoke({"input": "Hi, I'm Alice"})["response"])
print(conversation.invoke({"input": "What's my name?"})["response"])
print(conversation.invoke({"input": "Tell me a joke"})["response"])
```

---

## Intermediate Level Questions

### Q1: How do you build an agent with tools in LangChain?

**Answer:**

Agents use tools to perform tasks and reason about which tool to use.

```python
from langchain.tools import tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain import hub

# Define tools
@tool
def calculator(expression: str) -> str:
    """Useful for math calculations"""
    return str(eval(expression))

@tool
def search(query: str) -> str:
    """Search for information"""
    return f"Results for {query}"

# Create agent
llm = ChatOpenAI(model="gpt-4")
tools = [calculator, search]
prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Use agent
result = executor.invoke({
    "input": "Calculate 5*3 and search for machine learning"
})
print(result["output"])
```

**ReAct Loop:**
```
Thought → Action → Observation → Thought → ... → Final Answer
```

---

### Q2: Explain RAG (Retrieval Augmented Generation) and its implementation

**Answer:**

RAG combines document retrieval with LLM generation to provide context-aware answers.

**Architecture:**
```
User Query → Vector Search → Relevant Docs → LLM + Context → Answer
```

**Implementation:**
```python
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate

# 1. Load documents
loader = WebBaseLoader("https://python.langchain.com/docs/")
docs = loader.load()

# 2. Split documents
splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
splits = splitter.split_documents(docs)

# 3. Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(splits, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# 4. Create RAG chain
llm = ChatOpenAI(model="gpt-4")
prompt = ChatPromptTemplate.from_template(
    "Answer based on context:\n{context}\n\nQuestion: {input}"
)
qa_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, qa_chain)

# 5. Query
result = rag_chain.invoke({"input": "What is LangChain?"})
print(result["answer"])
```

---

### Q3: How do you optimize token usage and costs?

**Answer:**

**Monitoring Costs:**
```python
from langchain.callbacks import get_openai_callback

with get_openai_callback() as cb:
    result = llm.invoke("Your prompt")
    print(f"Total tokens: {cb.total_tokens}")
    print(f"Cost: ${cb.total_cost}")
```

**Cost Reduction Strategies:**
```python
# 1. Use cheaper models for simple tasks
fast_llm = ChatOpenAI(model="gpt-3.5-turbo")  # Cheaper
smart_llm = ChatOpenAI(model="gpt-4")          # More capable

# 2. Implement caching
from langchain.globals import set_llm_cache
from langchain.cache import SQLiteCache

set_llm_cache(SQLiteCache(database_path=".langchain.db"))

# 3. Optimize prompts (fewer tokens)
prompt = "Extract name and age:\n{text}"  # Concise

# 4. Batch requests
responses = await asyncio.gather(
    llm.ainvoke(query1),
    llm.ainvoke(query2),
    llm.ainvoke(query3)
)

# 5. Use token counters
from langchain.callbacks import TokenCounterCallback

counter = TokenCounterCallback()
llm.invoke("Your prompt", callbacks=[counter])
print(f"Tokens used: {counter.token_count}")
```

---

### Q4: What are the differences between chains and agents?

**Answer:**

| Aspect | Chains | Agents |
|--------|--------|--------|
| **Decision Making** | Predefined flow | Dynamic (LLM decides) |
| **Tool Usage** | Fixed sequence | As needed |
| **Flexibility** | Less flexible | More flexible |
| **Predictability** | Predictable | Can be unpredictable |
| **Control** | Developer controlled | Model controlled |

**Chain Example (Fixed):**
```python
# Step 1 → Step 2 → Step 3
search_chain = query | retriever | llm | parser
```

**Agent Example (Dynamic):**
```python
# LLM decides: Should I search? Should I calculate?
agent = create_react_agent(llm, [search_tool, calc_tool])
```

---

### Q5: How do you handle long documents and context windows?

**Answer:**

**Chunking Strategy:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Characters per chunk
    chunk_overlap=200,      # Overlap for context
    separators=["\n\n", "\n", " ", ""]  # Split on these
)

chunks = splitter.split_documents(documents)
```

**Map-Reduce for Large Documents:**
```python
from langchain.chains import MapReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

# Map: Process each chunk
map_prompt = ChatPromptTemplate.from_template(
    "Summarize: {text}"
)
map_chain = map_prompt | llm

# Reduce: Combine summaries
reduce_prompt = ChatPromptTemplate.from_template(
    "Combine these summaries: {text}"
)
reduce_chain = reduce_prompt | llm

mr_chain = MapReduceDocumentsChain(
    map_chain=map_chain,
    reduce_chain=reduce_chain,
    document_variable_name="text"
)
```

---

### Q6: How do you implement streaming responses?

**Answer:**

```python
from langchain_openai import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Enable streaming
llm = ChatOpenAI(
    model="gpt-4",
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

# Stream output in real-time
for chunk in llm.stream("Explain quantum computing"):
    print(chunk.content, end="", flush=True)
```

**Custom Streaming Callback:**
```python
from langchain.callbacks.base import BaseCallbackHandler

class MyStreamingCallback(BaseCallbackHandler):
    def on_llm_new_token(self, token, **kwargs):
        print(token, end="", flush=True)

llm.invoke("Your prompt", callbacks=[MyStreamingCallback()])
```

---

### Q7: What are output parsers and how do you use them?

**Answer:**

Output parsers extract structured data from LLM responses.

**Types:**
```python
from langchain.output_parsers import (
    JsonOutputParser,
    PydanticOutputParser,
    CommaSeparatedListOutputParser,
    StructuredOutputParser,
)

# JSON output
json_parser = JsonOutputParser()

# Comma-separated list
list_parser = CommaSeparatedListOutputParser()

# Structured with Pydantic
from pydantic import BaseModel, Field

class Person(BaseModel):
    name: str = Field(description="person's name")
    age: int = Field(description="person's age")

pydantic_parser = PydanticOutputParser(pydantic_object=Person)

# Use in chain
prompt = ChatPromptTemplate.from_template(
    "Extract person info:\n{format_instructions}\n\nText: {text}"
).partial(format_instructions=pydantic_parser.get_format_instructions())

chain = prompt | llm | pydantic_parser
result = chain.invoke({"text": "My name is Alice and I'm 30 years old"})
```

---

### Q8: How do you debug chains and agents?

**Answer:**

**Built-in Debugging:**
```python
# Enable verbose mode
chain = ConversationChain(llm=llm, memory=memory, verbose=True)
result = chain.invoke({"input": "Hello"})
```

**Using LangSmith:**
```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-key"
os.environ["LANGCHAIN_PROJECT"] = "my-project"

# All calls automatically traced
llm.invoke("Your prompt")
```

**Custom Debugging:**
```python
from langchain.callbacks import BaseCallbackHandler

class DebugCallback(BaseCallbackHandler):
    def on_chain_start(self, serialized, inputs, **kwargs):
        print(f"Chain started: {serialized.get('name')}")
        print(f"Inputs: {inputs}")

    def on_llm_start(self, serialized, prompts, **kwargs):
        print(f"LLM called with prompts: {prompts}")

    def on_chain_end(self, outputs, **kwargs):
        print(f"Chain output: {outputs}")

chain.invoke({"input": "test"}, callbacks=[DebugCallback()])
```

---

## Advanced Level Questions

### Q1: How do you design a multi-agent system?

**Answer:**

**Architecture:**
```
User Input → Router Agent → Specialized Agents → Aggregator → Output
                         ↓
                 [Data Agent, Code Agent, Writing Agent]
```

**Implementation:**
```python
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnableBranch

class SpecializedAgent:
    def __init__(self, name, description, tools):
        self.name = name
        self.description = description
        self.tools = tools
        self.llm = ChatOpenAI(model="gpt-4")

    def create_executor(self):
        from langchain import hub
        prompt = hub.pull("hwchase17/react")
        agent = create_react_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools)

# Create specialized agents
data_agent = SpecializedAgent(
    "DataAnalyst",
    "Analyzes data and statistics",
    [stat_tool, viz_tool]
)

code_agent = SpecializedAgent(
    "CodeWriter",
    "Writes and reviews code",
    [exec_tool, lint_tool]
)

# Router to delegate tasks
router_llm = ChatOpenAI(model="gpt-4")

# Aggregate results
def aggregate_results(results):
    return f"Combined insights: {results}"
```

---

### Q2: Explain how to implement custom memory systems

**Answer:**

**Custom Memory Class:**
```python
from langchain.schema import BaseMemory
from langchain.pydantic_v1 import BaseModel
import json
from pathlib import Path

class PersistentMemory(BaseMemory):
    buffer: str = ""
    file_path: str = "memory.json"

    class Config:
        arbitrary_types_allowed = True

    @property
    def memory_variables(self):
        return ["history"]

    def load_from_disk(self):
        if Path(self.file_path).exists():
            with open(self.file_path) as f:
                data = json.load(f)
                self.buffer = data.get("buffer", "")

    def save_to_disk(self):
        with open(self.file_path, 'w') as f:
            json.dump({"buffer": self.buffer}, f)

    def get_memory_variables(self, inputs):
        self.load_from_disk()
        return {"history": self.buffer}

    def save_context(self, inputs, outputs):
        input_str = json.dumps(inputs)
        output_str = json.dumps(outputs)
        self.buffer += f"User: {input_str}\nAssistant: {output_str}\n"
        self.save_to_disk()

    def clear(self):
        self.buffer = ""
        self.save_to_disk()
```

---

### Q3: How do you handle edge cases in agents?

**Answer:**

**Edge Cases and Solutions:**

1. **Agent Infinite Loop:**
```python
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    max_iterations=10,           # Stop after 10 steps
    early_stopping_method="generate",  # Stop if confident
    return_intermediate_steps=True
)
```

2. **Tool Errors:**
```python
@tool
def risky_tool(query: str) -> str:
    """Tool that might fail"""
    try:
        # Tool logic
        return "success"
    except Exception as e:
        return f"Error: {str(e)}"
```

3. **Empty Responses:**
```python
result = executor.invoke({"input": "query"})
if result.get("output") == "":
    fallback_response = "I couldn't find an answer"
    result["output"] = fallback_response
```

4. **Hallucinations:**
```python
prompt = ChatPromptTemplate.from_template(
    """Answer ONLY from the provided context.
    If information is not in the context, say 'I don't know'.

    Context: {context}
    Question: {question}"""
)
```

---

### Q4: How do you implement and optimize semantic search?

**Answer:**

**Vector Store Selection:**
```python
# For small datasets (< 100K)
from langchain_chroma import Chroma
vectorstore = Chroma.from_documents(docs, embeddings)

# For large scale (> 100K)
from langchain_pinecone import Pinecone
vectorstore = Pinecone.from_documents(
    docs,
    embeddings,
    index_name="production",
    namespace="documents"
)

# Metadata filtering
results = vectorstore.similarity_search(
    "machine learning",
    k=5,
    filter={"source": "arxiv"}
)
```

**Optimization Strategies:**
```python
# 1. Better embeddings
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# 2. Hybrid search (semantic + keyword)
bm25_retriever = BM25Retriever.from_documents(docs)
dense_retriever = vectorstore.as_retriever()

from langchain.retrievers import EnsembleRetriever
ensemble = EnsembleRetriever(
    retrievers=[bm25_retriever, dense_retriever],
    weights=[0.5, 0.5]
)

# 3. Reranking results
from langchain_cohere import CohereRerank
compressor = CohereRerank()
from langchain.retrievers import ContextualCompressionRetriever
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=retriever
)
```

---

### Q5: How do you build a production-ready LLM application?

**Answer:**

**Key Components:**

```python
# 1. Environment & Configuration
import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    langchain_api_key: str = os.getenv("LANGCHAIN_API_KEY")
    model: str = "gpt-4"
    max_retries: int = 3

settings = Settings()

# 2. Error Handling
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def call_llm(llm, prompt):
    return llm.invoke(prompt)

# 3. Monitoring
from langchain.callbacks import get_openai_callback

with get_openai_callback() as cb:
    result = llm.invoke(prompt)
    logger.info(f"Tokens: {cb.total_tokens}, Cost: ${cb.total_cost}")

# 4. Caching
from langchain.globals import set_llm_cache
from langchain.cache import SQLiteCache
set_llm_cache(SQLiteCache(database_path=".langchain.db"))

# 5. Async Support
import asyncio
async def process_batch(queries):
    results = await asyncio.gather(*[
        llm.ainvoke(q) for q in queries
    ])
    return results

# 6. Logging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
```

---

### Q6: How do you handle context window limitations?

**Answer:**

**Context Window Management:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import MapReduceDocumentsChain

# 1. Know your model's limit
model_limits = {
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "claude-3-opus": 200000
}

# 2. Smart chunking
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

# 3. Summarization strategy
from langchain.chains.summarize import load_summarize_chain

chain = load_summarize_chain(
    llm,
    chain_type="map_reduce",
    return_intermediate_steps=False
)
summary = chain.run(documents)

# 4. Selective retrieval
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 5. Token counting
from langchain.callbacks import get_openai_callback

with get_openai_callback() as cb:
    response = llm.invoke(prompt)
    available_tokens = model_limits["gpt-4"] - cb.prompt_tokens
```

---

### Q7: How do you implement custom tools and integrations?

**Answer:**

**Creating Custom Tools:**
```python
from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import Optional

# Simple tool
@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b

# Tool with description
@tool("search_api")
def search(query: str, limit: int = 10) -> str:
    """Search external API"""
    # Implementation
    return f"Results for {query}"

# Complex tool with input schema
class SearchInput(BaseModel):
    query: str = Field(description="Search query")
    limit: int = Field(default=10, description="Result limit")
    source: Optional[str] = Field(default=None, description="Source")

@tool("advanced_search", args_schema=SearchInput)
def advanced_search(query: str, limit: int = 10, source: None = None):
    """Advanced search with multiple parameters"""
    pass

# Use in agent
tools = [multiply, search, advanced_search]
agent = create_react_agent(llm, tools, prompt)
```

---

### Q8: How do you scale LangChain applications?

**Answer:**

**Scaling Strategies:**

```python
# 1. Distributed Processing
from langchain.callbacks import LambdaCallback
import concurrent.futures

def process_in_parallel(queries, num_workers=4):
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(llm.invoke, q) for q in queries]
        return [f.result() for f in concurrent.futures.as_completed(futures)]

# 2. Async Operations
import asyncio

async def batch_process(queries):
    tasks = [llm.ainvoke(q) for q in queries]
    return await asyncio.gather(*tasks)

# 3. Caching & Memoization
from functools import lru_cache
from langchain.globals import set_llm_cache
from langchain.cache import RedisCache
import redis

redis_client = redis.Redis.from_url("redis://localhost")
set_llm_cache(RedisCache(redis_client=redis_client))

# 4. Load Balancing
class LoadBalancedLLM:
    def __init__(self, models):
        self.models = models
        self.current = 0

    def invoke(self, prompt):
        model = self.models[self.current % len(self.models)]
        self.current += 1
        return model.invoke(prompt)

models = [
    ChatOpenAI(model="gpt-4"),
    ChatOpenAI(model="gpt-3.5-turbo"),
]
balanced_llm = LoadBalancedLLM(models)

# 5. Rate Limiting
from langchain.callbacks import BaseCallbackHandler
import time

class RateLimitCallback(BaseCallbackHandler):
    def __init__(self, max_calls_per_minute=60):
        self.max_calls_per_minute = max_calls_per_minute
        self.calls = []

    def on_llm_start(self, **kwargs):
        now = time.time()
        self.calls = [c for c in self.calls if now - c < 60]

        if len(self.calls) >= self.max_calls_per_minute:
            wait_time = 60 - (now - self.calls[0])
            time.sleep(wait_time)

        self.calls.append(now)
```

---

## References & Further Learning

- **Official Docs**: https://python.langchain.com
- **LangChain GitHub**: https://github.com/langchain-ai/langchain
- **LangSmith**: https://smith.langchain.com
- **LangChain Hub**: https://smith.langchain.com/hub
- **Community Discord**: https://discord.gg/6adMQxSpJS
