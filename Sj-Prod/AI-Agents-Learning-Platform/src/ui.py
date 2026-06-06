"""Streamlit dashboard for the AI Agents Learning Platform."""

import logging
import os

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Agents Learning Platform", layout="wide")
st.title("AI Agents Learning Platform")
st.caption("Explore frameworks, patterns, and interactive demos for AI agent systems")


def api_get(path: str) -> dict:
    try:
        return requests.get(f"{API_URL}{path}", timeout=10).json()
    except requests.ConnectionError:
        st.error("Cannot reach the API. Is the server running?")
        st.stop()


def api_post(path: str, data: dict) -> dict:
    try:
        return requests.post(f"{API_URL}{path}", json=data, timeout=30).json()
    except requests.ConnectionError:
        st.error("Cannot reach the API. Is the server running?")
        st.stop()


# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["Frameworks", "Patterns", "Compare", "Interactive Demos"])

# ========== TAB 1: Frameworks ==========
with tab1:
    st.header("AI Agent Frameworks")
    data = api_get("/frameworks")
    frameworks = data.get("frameworks", {})

    # Category filter
    categories = sorted(set(f["category"] for f in frameworks.values()))
    selected_cat = st.selectbox("Filter by category", ["All"] + categories)

    for key, fw in frameworks.items():
        if selected_cat != "All" and fw["category"] != selected_cat:
            continue

        with st.expander(f"{fw['name']} ({fw['category']})", expanded=False):
            st.write(f"**{fw['description']}**")
            st.write(f"Best for: {fw['best_for']}")
            st.write(f"Complexity: {fw['complexity']} | Language: {fw['language']}")
            st.write(f"GitHub Stars: {fw['github_stars']} | License: {fw['license']}")
            st.write("**Key Features:**")
            for feat in fw["key_features"]:
                st.write(f"- {feat}")

# ========== TAB 2: Patterns ==========
with tab2:
    st.header("Agent Design Patterns")
    data = api_get("/patterns")
    patterns = data.get("patterns", {})

    for key, pat in patterns.items():
        with st.expander(f"{pat['name']}", expanded=False):
            st.write(f"**{pat['description']}**")
            st.code(pat["flow"], language=None)

            col1, col2 = st.columns(2)
            with col1:
                st.write("**Strengths:**")
                for s in pat["strengths"]:
                    st.write(f"- {s}")
            with col2:
                st.write("**Weaknesses:**")
                for w in pat["weaknesses"]:
                    st.write(f"- {w}")

            st.write(f"**Example:** {pat['example_use']}")

# ========== TAB 3: Compare ==========
with tab3:
    st.header("Framework Comparison")
    data = api_get("/comparisons")
    comparisons = data.get("comparisons", [])

    if comparisons:
        df = pd.DataFrame(comparisons)
        df = df.set_index("dimension")

        # Radar chart
        fig = go.Figure()
        for col in df.columns:
            fig.add_trace(go.Scatterpolar(
                r=df[col].tolist() + [df[col].tolist()[0]],
                theta=df.index.tolist() + [df.index.tolist()[0]],
                name=col,
                fill="toself",
                opacity=0.6,
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            height=500,
            margin=dict(t=40, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Table view
        st.subheader("Score Table (1-5)")
        st.dataframe(df, use_container_width=True)

# ========== TAB 4: Interactive Demos ==========
with tab4:
    st.header("Interactive Agent Pattern Demos")
    st.write("Run simulated agent patterns to see how they work step-by-step.")

    demos = api_get("/demos").get("demos", {})
    selected_demo = st.selectbox("Select a pattern to demo", list(demos.keys()),
                                  format_func=lambda x: demos[x])
    task_input = st.text_input("Task for the agent:", value="How to build a scalable web application")

    if st.button("Run Demo", type="primary", disabled=not task_input):
        with st.spinner(f"Running {demos[selected_demo]} demo..."):
            result = api_post("/demos/run", {"pattern": selected_demo, "task": task_input})

        st.success(f"Completed in {result['elapsed_seconds']}s")
        st.divider()

        pattern = result["pattern"]
        data = result["result"]

        if pattern == "react":
            st.subheader("ReAct Agent Trace")
            for step in data:
                stype = step["type"]
                if stype == "thought":
                    st.info(f"**Thought:** {step['content']}")
                elif stype == "action":
                    st.warning(f"**Action:** [{step['tool']}] {step['input']}")
                elif stype == "observation":
                    st.success(f"**Observation:** {step['content']}")
                elif stype == "answer":
                    st.markdown(f"**Final Answer:** {step['content']}")

        elif pattern == "plan_and_execute":
            st.subheader("Plan")
            for i, step in enumerate(data["plan"], 1):
                st.write(f"{i}. {step}")
            st.subheader("Execution")
            for ex in data["executions"]:
                st.write(f"**Step {ex['step']}** ({ex['status']}, {ex['duration_ms']}ms): {ex['result']}")
            st.subheader("Final Answer")
            st.markdown(data["final_answer"])

        elif pattern == "reflection":
            for i, iteration in enumerate(data["iterations"], 1):
                st.subheader(f"Iteration {i}")
                st.write(f"**Draft:** {iteration['draft']}")
                critique = iteration["critique"]
                st.metric("Score", critique["score"])
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Strengths:**")
                    for s in critique.get("strengths", []):
                        st.write(f"- {s}")
                with col2:
                    st.write("**Issues:**")
                    for s in critique.get("issues", []):
                        st.write(f"- {s}")
            st.subheader("Final Output")
            st.markdown(data["final_output"])

        elif pattern == "multi_agent_debate":
            for key, agent in data["agents"].items():
                st.subheader(agent["role"])
                st.write(agent["argument"])
            st.subheader("Synthesis")
            st.markdown(data["synthesis"])
            st.write(f"**Recommendation:** {data['recommendation']}")
