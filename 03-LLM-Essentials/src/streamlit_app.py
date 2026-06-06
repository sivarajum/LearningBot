"""
Streamlit UI for LLM Chatbot
"""
import streamlit as st
import logging
from chatbot import Chatbot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="LLM Chatbot",
    page_icon="💬",
    layout="wide"
)

# Initialize session state
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
if "messages" not in st.session_state:
    st.session_state.messages = []


def initialize_chatbot(
    model_name: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    memory_type: str = "buffer"
):
    """Initialize chatbot"""
    try:
        with st.spinner("Initializing chatbot..."):
            st.session_state.chatbot = Chatbot(
                llm_provider="openai",
                model_name=model_name,
                temperature=temperature,
                memory_type=memory_type
            )
            st.success("Chatbot initialized!")
    except Exception as e:
        st.error(f"Error initializing chatbot: {e}")


# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Model selection
    model_name = st.selectbox(
        "Model",
        ["gpt-3.5-turbo", "gpt-4", "text-davinci-003"],
        index=0
    )
    
    # Temperature
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
    
    # Memory type
    memory_type = st.selectbox(
        "Memory Type",
        ["buffer", "summary"],
        index=0
    )
    
    # Initialize button
    if st.button("Initialize Chatbot"):
        initialize_chatbot(model_name, temperature, memory_type)
    
    # Clear memory button
    if st.session_state.chatbot is not None:
        if st.button("Clear Memory"):
            st.session_state.chatbot.clear_memory()
            st.session_state.messages = []
            st.success("Memory cleared!")
    
    # Status
    st.subheader("Status")
    if st.session_state.chatbot is not None:
        st.success("✅ Chatbot Ready")
    else:
        st.warning("⚠️ Chatbot not initialized")


# Main content
st.title("💬 LLM Chatbot")
st.markdown("Conversational AI chatbot with memory and prompt engineering")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response
    if st.session_state.chatbot is None:
        response = "Please initialize the chatbot first using the sidebar."
    else:
        try:
            response = st.session_state.chatbot.chat(prompt)
        except Exception as e:
            response = f"Error: {e}"
    
    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    if st.session_state.chatbot is not None:
        st.session_state.chatbot.clear_memory()
    st.rerun()

