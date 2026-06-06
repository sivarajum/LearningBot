"""Streamlit frontend for the Enterprise RAG System."""

import logging
import os

import requests
import streamlit as st

logger = logging.getLogger(__name__)

API_URL: str = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="RAG Document Q&A", layout="wide")
st.title("Enterprise RAG System")
st.caption("Ask questions about your documents using Retrieval-Augmented Generation")

# -- Sidebar: Indexing Controls ------------------------------------------------

with st.sidebar:
    st.header("Document Indexing")

    doc_dir = st.text_input("Document directory", value="./sample_docs")

    if st.button("Index Documents", type="primary"):
        with st.spinner("Indexing documents..."):
            try:
                resp = requests.post(
                    f"{API_URL}/ingest",
                    json={"directory": doc_dir},
                    timeout=120,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(
                        f"Indexed **{data['chunks_indexed']}** chunks "
                        f"from **{len(data['files_found'])}** files "
                        f"in {data['elapsed_seconds']}s"
                    )
                    st.write("**Files indexed:**")
                    for f in data["files_found"]:
                        st.write(f"- {f}")
                else:
                    st.error(resp.json().get("detail", "Indexing failed"))
            except requests.ConnectionError:
                logger.error("Cannot connect to API at %s for indexing", API_URL)
                st.error("Cannot connect to API. Is the server running?")
            except requests.Timeout:
                logger.error("Indexing request timed out after 120s")
                st.error("Indexing request timed out. Try a smaller document set.")
            except requests.RequestException as exc:
                logger.error("Indexing request failed: %s", exc)
                st.error(f"Indexing request failed: {exc}")

    st.divider()
    st.header("Collection Stats")

    try:
        stats = requests.get(f"{API_URL}/stats", timeout=5).json()
        st.metric("Total Chunks", stats.get("total_chunks", 0))
        st.caption(f"Model: {stats.get('embedding_model', 'N/A')}")
        st.caption(f"Collection: {stats.get('collection', 'N/A')}")
    except requests.ConnectionError:
        logger.debug("API not available at %s for stats", API_URL)
        st.info("API not available. Start the server to see stats.")
    except requests.Timeout:
        logger.warning("Stats request timed out")
        st.info("Stats request timed out.")
    except requests.RequestException as exc:
        logger.warning("Failed to fetch stats: %s", exc)
        st.info("API not available. Start the server to see stats.")

# -- Main Area: Q&A Interface -------------------------------------------------

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if question := st.chat_input("Ask a question about your documents..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Query the API
    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            try:
                resp = requests.post(
                    f"{API_URL}/query",
                    json={"question": question, "k": 5},
                    timeout=60,
                )

                if resp.status_code == 200:
                    data = resp.json()
                    answer = data["answer"]
                    st.markdown(answer)

                    # Show sources in an expander
                    if data.get("sources"):
                        with st.expander(
                            f"Sources ({len(data['sources'])} chunks retrieved)"
                        ):
                            for i, src in enumerate(data["sources"], 1):
                                score_pct = f"{src['score']:.0%}"
                                st.markdown(
                                    f"**{i}. {src['source']}** "
                                    f"(chunk {src['chunk_index']}, "
                                    f"similarity: {score_pct})"
                                )
                                st.caption(src.get("preview", ""))
                                st.divider()

                    st.caption(
                        f"Model: {data['model_used']} | "
                        f"Time: {data['elapsed_seconds']}s"
                    )

                    # Store assistant message
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )
                else:
                    error_msg = resp.json().get("detail", "Query failed")
                    st.error(error_msg)

            except requests.ConnectionError:
                logger.error("Cannot connect to API at %s for query", API_URL)
                st.error(
                    "Cannot connect to the API server. "
                    "Make sure it is running on " + API_URL
                )
            except requests.Timeout:
                logger.error("Query request timed out after 60s")
                st.error("Query timed out. The server may be overloaded.")
            except requests.RequestException as exc:
                logger.error("Query request failed: %s", exc)
                st.error(f"Query request failed: {exc}")
