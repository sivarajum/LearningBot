# LangChain - Complete Guide (Basic to Advanced)

## 🎯 What is LangChain?

**LangChain** is a framework for developing applications powered by language models. It provides tools to build LLM applications with chains, agents, memory, and more. You use it in Modules 03 and 05 for chatbots and RAG systems.

### Why LangChain?
- **LLM Orchestration**: Chain multiple LLM calls
- **Memory**: Conversation history management
- **Tools**: Connect LLMs to external data
- **Agents**: Autonomous decision-making
- **RAG**: Built-in retrieval-augmented generation

---

## 📚 Learning Path: Basic → Intermediate → Advanced

---

## 🟢 LEVEL 1: BASIC (Getting Started)

### Basic LangChain Usage

```python
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Initialize LLM
llm = OpenAI(temperature=0.7)

# Create prompt template
prompt = PromptTemplate(
    input_variables=["topic"],
    template="Explain {topic} in simple terms."
)

# Create chain
chain = LLMChain(llm=llm, prompt=prompt)

# Run chain
result = chain.run("machine learning")
print(result)
```

### Key Concepts

#### 1. **LLMs**
```python
from langchain.llms import OpenAI
llm = OpenAI(temperature=0.7)
response = llm("What is AI?")
```

#### 2. **Prompts**
```python
from langchain.prompts import PromptTemplate

prompt = PromptTemplate(
    input_variables=["name"],
    template="Hello, {name}!"
)
```

#### 3. **Chains**
```python
from langchain.chains import LLMChain
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run(name="Alice")
```

#### 4. **Memory**
```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory()
memory.save_context({"input": "Hi"}, {"output": "Hello!"})
```

### Basic Example: Simple Chatbot

```python
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

llm = OpenAI(temperature=0.7)
memory = ConversationBufferMemory()

chain = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

response = chain.predict(input="What is machine learning?")
print(response)
```

---

## 🟡 LEVEL 2: INTERMEDIATE (Production Patterns)

### RAG (Retrieval-Augmented Generation)

```python
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQA

# Load documents
loader = PyPDFLoader("document.pdf")
documents = loader.load()

# Split documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
texts = text_splitter.split_documents(documents)

# Create embeddings
embeddings = OpenAIEmbeddings()

# Create vector store
vectorstore = Pinecone.from_documents(texts, embeddings)

# Create QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# Query
result = qa_chain.run("What is the main topic?")
```

### Agents

```python
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType

tools = [
    Tool(
        name="Search",
        func=search_function,
        description="Search for information"
    ),
    Tool(
        name="Calculator",
        func=calculator_function,
        description="Perform calculations"
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

result = agent.run("What is 2+2 and search for AI news?")
```

### Memory Types

```python
# Buffer Memory (stores all history)
from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory()

# Summary Memory (summarizes old conversations)
from langchain.memory import ConversationSummaryMemory
memory = ConversationSummaryMemory(llm=llm)

# Entity Memory (remembers entities)
from langchain.memory import ConversationEntityMemory
memory = ConversationEntityMemory(llm=llm)
```

### Custom Chains

```python
from langchain.chains import LLMChain, SimpleSequentialChain

# Chain 1: Generate topic
topic_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["input"],
        template="Generate a topic about {input}"
    )
)

# Chain 2: Explain topic
explain_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["topic"],
        template="Explain {topic} in detail"
    )
)

# Sequential chain
overall_chain = SimpleSequentialChain(
    chains=[topic_chain, explain_chain],
    verbose=True
)

result = overall_chain.run("technology")
```

---

## 🔴 LEVEL 3: ADVANCED (Production Excellence)

### Advanced RAG Patterns

#### Multi-Query Retriever

```python
from langchain.retrievers.multi_query import MultiQueryRetriever

retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),
    llm=llm
)

# Generates multiple queries and retrieves diverse results
docs = retriever.get_relevant_documents("query")
```

#### Contextual Compression

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever()
)

# Retrieves and compresses documents
docs = compression_retriever.get_relevant_documents("query")
```

### Advanced Agents

#### ReAct Agent

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

# Get ReAct prompt
prompt = hub.pull("hwchase17/react")

# Create agent
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = agent_executor.invoke({"input": "What's the weather and calculate 5*5?"})
```

#### Custom Tools

```python
from langchain.tools import Tool
from langchain.utilities import GoogleSearchAPIWrapper

search = GoogleSearchAPIWrapper()

tool = Tool(
    name="Google Search",
    description="Search Google for current information",
    func=search.run
)

agent = initialize_agent([tool], llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
```

### Streaming Responses

```python
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

llm = OpenAI(
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
    temperature=0.7
)

# Response streams as it's generated
response = llm("Tell me a long story")
```

### Callbacks and Monitoring

```python
from langchain.callbacks import LangChainTracer

tracer = LangChainTracer()
tracer.load_default_session()

chain = LLMChain(llm=llm, prompt=prompt, callbacks=[tracer])
result = chain.run("query")
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Simple Chain
```
Input → Prompt → LLM → Output
```

### Pattern 2: Sequential Chain
```
Input → Chain 1 → Chain 2 → Chain 3 → Output
```

### Pattern 3: RAG Chain
```
Query → Embed → Vector Search → Retrieve → LLM → Output
```

### Pattern 4: Agent Chain
```
Input → Agent → Tool Selection → Tool Execution → LLM → Output
```

---

## 🔗 Integration with Your POCs

### Module 03: LLM Chatbot
- **File**: `03-LLM-Essentials/src/chatbot.py`
- **Usage**: Conversation chains, memory management
- **Features**: Buffer memory, conversation history

### Module 05: RAG System
- **File**: `05-Generative-AI-RAG/src/rag_pipeline.py`
- **Usage**: RAG chains, vector stores, retrieval
- **Features**: Document loading, chunking, embeddings, QA chains

---

## 📊 Best Practices

### 1. **Use Appropriate Memory Type**
```python
# Short conversations: BufferMemory
# Long conversations: SummaryMemory
# Entity tracking: EntityMemory
```

### 2. **Optimize Chunk Size**
```python
# Too small: Loses context
# Too large: Exceeds token limits
# Optimal: 500-1000 tokens
```

### 3. **Handle Errors**
```python
try:
    result = chain.run(input)
except Exception as e:
    # Handle gracefully
    result = "I'm sorry, I encountered an error."
```

### 4. **Use Streaming for UX**
```python
# Better user experience
llm = OpenAI(streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
```

### 5. **Monitor Token Usage**
```python
# Track costs
from langchain.callbacks import get_openai_callback

with get_openai_callback() as cb:
    result = chain.run("query")
    print(f"Tokens: {cb.total_tokens}, Cost: ${cb.total_cost}")
```

---

## 🎯 Key Takeaways

1. **LangChain = LLM Orchestration Framework**
2. **Chains = Sequential LLM Operations**
3. **Agents = Autonomous Tool Use**
4. **RAG = Retrieval + Generation**
5. **Memory = Conversation Context**

---

## 📚 Next Steps

1. ✅ Read this guide
2. 📊 Review `Visual.md` for flows
3. 💬 Practice `Interview.md` questions
4. 🏗️ Build with Module 03/05
5. 🎯 Explain it confidently

