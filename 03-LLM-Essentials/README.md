# Module 03: LLM Essentials - Chatbot Application

## Overview
Conversational AI chatbot using Large Language Models with LangChain, demonstrating prompt engineering, conversation memory, and user-friendly interfaces.

## Architecture
- **LLM**: OpenAI GPT-3.5/GPT-4
- **Framework**: LangChain
- **Memory**: Conversation buffer or summary memory
- **UI**: Streamlit web interface

## Features
- ✅ Multiple LLM support (OpenAI)
- ✅ Conversation memory
- ✅ Prompt engineering
- ✅ Streamlit UI
- ✅ Configurable temperature and memory

## Quick Start

### Prerequisites
- OpenAI API key
- Python 3.9+

### Installation
```bash
pip install -r requirements.txt
```

### Setup
1. Set environment variables:
```bash
export OPENAI_API_KEY="your-api-key"
```

2. Run Streamlit UI:
```bash
streamlit run src/streamlit_app.py
```

3. Or use programmatically:
```python
from src.chatbot import Chatbot

chatbot = Chatbot(
    llm_provider="openai",
    model_name="gpt-3.5-turbo",
    memory_type="buffer"
)

response = chatbot.chat("Hello!")
print(response)
```

## Usage

### Streamlit UI
1. Open the Streamlit app
2. Configure model settings in sidebar
3. Initialize chatbot
4. Start chatting!

### Programmatic Usage
```python
# Initialize
chatbot = Chatbot(
    model_name="gpt-3.5-turbo",
    temperature=0.7,
    memory_type="buffer"
)

# Chat
response = chatbot.chat("What is machine learning?")

# Get history
history = chatbot.get_conversation_history()

# Clear memory
chatbot.clear_memory()
```

## Configuration Options

### Models
- `gpt-3.5-turbo` (default, fast, cost-effective)
- `gpt-4` (more capable, slower, more expensive)
- `text-davinci-003` (legacy)

### Memory Types
- `buffer`: Stores all conversation history
- `summary`: Summarizes old conversations

### Temperature
- `0.0-0.3`: More deterministic, focused
- `0.7`: Balanced (default)
- `1.0-2.0`: More creative, varied

## Project Structure
```
03-LLM-Essentials/
├── src/
│   ├── chatbot.py
│   └── streamlit_app.py
├── requirements.txt
└── README.md
```

## Success Metrics
- Response time <3s
- Context retention
- Multi-turn coherence
- User satisfaction

## Next Steps
- Add HuggingFace model support
- Implement Redis for persistent memory
- Add conversation export
- Deploy to cloud
