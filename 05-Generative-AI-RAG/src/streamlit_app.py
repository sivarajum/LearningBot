"""
Streamlit UI for RAG System
"""
import streamlit as st
import logging
from rag_pipeline import RAGPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="RAG Data Documentation",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = None
if "messages" not in st.session_state:
    st.session_state.messages = []


def initialize_pipeline():
    """Initialize RAG pipeline"""
    if st.session_state.rag_pipeline is None:
        try:
            with st.spinner("Initializing RAG pipeline..."):
                st.session_state.rag_pipeline = RAGPipeline(
                    vector_store_type="chroma",
                    embedding_model="huggingface",
                    llm_provider="openai"
                )
                st.success("Pipeline initialized!")
        except Exception as e:
            st.error(f"Error initializing pipeline: {e}")


def build_pipeline(data_dir: str):
    """Build RAG pipeline from documents"""
    if st.session_state.rag_pipeline is None:
        initialize_pipeline()
    
    try:
        with st.spinner("Building pipeline from documents..."):
            st.session_state.rag_pipeline.build_pipeline(data_dir)
            st.success("Pipeline built successfully!")
    except Exception as e:
        st.error(f"Error building pipeline: {e}")


# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Initialize pipeline button
    if st.button("Initialize Pipeline"):
        initialize_pipeline()
    
    # Build pipeline section
    st.subheader("Build Pipeline")
    data_dir = st.text_input("Data Directory", value="data/documents")
    if st.button("Build from Documents"):
        build_pipeline(data_dir)
    
    # Settings
    st.subheader("Settings")
    k_docs = st.slider("Number of documents to retrieve", 1, 10, 4)
    
    # Pipeline status
    st.subheader("Pipeline Status")
    if st.session_state.rag_pipeline is not None:
        if st.session_state.rag_pipeline.qa_chain is not None:
            st.success("✅ Pipeline Ready")
        else:
            st.warning("⚠️ Pipeline not built")
    else:
        st.error("❌ Pipeline not initialized")


# Main content
st.title("🤖 RAG Data Documentation System")
st.markdown("Ask questions about your data documentation using Retrieval-Augmented Generation")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("View Sources"):
                for i, source in enumerate(message["sources"]):
                    st.markdown(f"**Source {i+1}:**")
                    st.text(source["content"][:200] + "...")
                    if "metadata" in source:
                        st.json(source["metadata"])

# Chat input
if prompt := st.chat_input("Ask a question about your documentation..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response
    if st.session_state.rag_pipeline is None or st.session_state.rag_pipeline.qa_chain is None:
        response = "Please initialize and build the pipeline first."
        sources = []
    else:
        try:
            # Update retriever k if needed
            if k_docs != 4:
                st.session_state.rag_pipeline.create_qa_chain(k=k_docs)
            
            # Query pipeline
            result = st.session_state.rag_pipeline.query(prompt)
            response = result["answer"]
            sources = result["source_documents"]
        except Exception as e:
            response = f"Error: {e}"
            sources = []
    
    # Add assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "sources": sources
    })
    
    with st.chat_message("assistant"):
        st.markdown(response)
        if sources:
            with st.expander("View Sources"):
                for i, source in enumerate(sources):
                    st.markdown(f"**Source {i+1}:**")
                    st.text(source["content"][:200] + "...")
                    if "metadata" in source:
                        st.json(source["metadata"])

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()

