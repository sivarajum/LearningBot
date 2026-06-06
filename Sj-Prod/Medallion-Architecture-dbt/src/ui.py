"""
ui.py — Streamlit dashboard for the Medallion Architecture POC.

Four tabs:
  1. Overview        — architecture diagram + layer stats
  2. Explore Layers  — select layer + model → preview data table
  3. Run Pipeline    — trigger pipeline, show logs, before/after counts
  4. Lineage         — interactive lineage graph (Plotly)
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

import requests
import streamlit as st

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Medallion Architecture — dbt + DuckDB",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

API_BASE = "http://localhost:8000"

LAYER_COLOURS = {
    "source": "#8B4513",  # brown
    "bronze": "#CD7F32",  # bronze
    "silver": "#C0C0C0",  # silver
    "gold": "#FFD700",    # gold
}

LAYER_DESCRIPTIONS = {
    "bronze": "Raw ingest — type casts only, no business logic. System of record.",
    "silver": "Cleansed and validated — deduplication, enrichment, business rules applied.",
    "gold": "Aggregated business metrics — KPIs ready for BI tools and stakeholders.",
}

# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------


def api_get(path: str, timeout: int = 10) -> Optional[Any]:
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return None
    except Exception as exc:  # noqa: BLE001
        logger.error("API GET %s failed: %s", path, exc)
        st.error(f"API error: {exc}")
        return None


def api_post(path: str, timeout: int = 120) -> Optional[Any]:
    try:
        r = requests.post(f"{API_BASE}{path}", timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return None
    except Exception as exc:  # noqa: BLE001
        logger.error("API POST %s failed: %s", path, exc)
        st.error(f"API error: {exc}")
        return None


def api_available() -> bool:
    health = api_get("/health", timeout=3)
    return health is not None


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("Medallion Architecture")
    st.caption("dbt + DuckDB | POC-08")
    st.divider()
    st.markdown("**Layers**")
    st.markdown("- Bronze: Raw Ingest")
    st.markdown("- Silver: Cleaned & Validated")
    st.markdown("- Gold: Business Metrics")
    st.divider()

    if api_available():
        health = api_get("/health")
        if health:
            col1, col2 = st.columns(2)
            with col1:
                dbt_ok = health.get("dbt_installed", False)
                st.metric("dbt", "OK" if dbt_ok else "Missing")
            with col2:
                wh_ok = health.get("warehouse_exists", False)
                st.metric("Warehouse", "Ready" if wh_ok else "Empty")
        st.success("API connected")
    else:
        st.error("API offline — start with: `python main.py api`")
    st.divider()
    st.caption("POC-08 | Lead DE Interview Prep")

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview", "Explore Layers", "Run Pipeline", "Lineage"]
)

# ===========================================================================
# TAB 1: Overview
# ===========================================================================

with tab1:
    st.header("Medallion Architecture — Bronze / Silver / Gold")

    # ASCII diagram
    st.subheader("Architecture Diagram")
    ascii_diagram = """
    ┌──────────────────────────────────────────────────────────────────────┐
    │                    MEDALLION ARCHITECTURE                            │
    │                    dbt + DuckDB (local warehouse)                    │
    └──────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │ SOURCE FILES │     │    BRONZE    │     │    SILVER    │
    │              │ --> │   (Raw       │ --> │  (Cleaned    │
    │ customers.csv│     │    Ingest)   │     │   Validated) │
    │ orders.csv   │     │              │     │              │
    │ products.csv │     │ Type casts   │     │ Dedup        │
    └──────────────┘     │ Metadata     │     │ Validate     │
                         │ _ingested_at │     │ Enrich       │
                         └──────────────┘     └──────────────┘
                                                      │
                                                      v
                                             ┌──────────────┐
                                             │     GOLD     │
                                             │  (Business   │
                                             │   Metrics)   │
                                             │              │
                                             │ CLV          │
                                             │ Revenue      │
                                             │ Product Perf │
                                             └──────────────┘
    """
    st.code(ascii_diagram, language=None)

    # Plotly funnel diagram
    try:
        import plotly.graph_objects as go

        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.subheader("Data Flow — Row Count Funnel")

            layers_data = api_get("/layers") if api_available() else None

            if layers_data:
                labels = []
                values = []
                colours = []
                for layer in ["bronze", "silver", "gold"]:
                    info = layers_data.get(layer, {})
                    total = info.get("total_rows", 0)
                    labels.append(f"{layer.upper()}<br>{total:,} rows")
                    values.append(max(total, 1))
                    colours.append(LAYER_COLOURS[layer])

                fig = go.Figure(
                    go.Funnel(
                        y=labels,
                        x=values,
                        marker_color=colours,
                        textinfo="value+percent initial",
                        opacity=0.85,
                    )
                )
                fig.update_layout(
                    title="Row Counts per Layer",
                    height=350,
                    margin=dict(l=20, r=20, t=40, b=20),
                    paper_bgcolor="#0e1117",
                    font_color="#fafafa",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Run the pipeline first to see row-count metrics.")

        with col_r:
            st.subheader("Layer Stats")
            if layers_data:
                for layer in ["bronze", "silver", "gold"]:
                    info = layers_data.get(layer, {})
                    total = info.get("total_rows", 0)
                    models = info.get("models", [])
                    colour = LAYER_COLOURS[layer]
                    st.markdown(
                        f"""
                        <div style='border-left: 4px solid {colour}; padding: 8px 12px; margin: 6px 0; background: #1e1e2e; border-radius: 4px;'>
                        <b style='color:{colour}'>{layer.upper()}</b><br>
                        <small>Models: {len(models)}</small><br>
                        <b>{total:,}</b> total rows
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("API not available or pipeline not run.")
    except ImportError:
        st.warning("Plotly not installed — pip install plotly")

    # Concepts
    st.subheader("Key Concepts")
    concepts_data = api_get("/concepts") if api_available() else None
    if concepts_data:
        for concept in concepts_data[:6]:
            with st.expander(concept["term"]):
                st.write(concept["definition"])
    else:
        st.info("Connect to the API to see concepts.")

# ===========================================================================
# TAB 2: Explore Layers
# ===========================================================================

with tab2:
    st.header("Explore Medallion Layers")

    if not api_available():
        st.error("API is not running. Start it with: `python main.py api`")
    else:
        layers_info = api_get("/layers")

        col_sel_layer, col_sel_model = st.columns(2)
        with col_sel_layer:
            selected_layer = st.selectbox(
                "Select Layer",
                ["bronze", "silver", "gold"],
                format_func=lambda x: x.upper(),
            )
        with col_sel_model:
            model_options = []
            if layers_info and selected_layer in layers_info:
                model_options = layers_info[selected_layer].get("models", [])
            selected_model = st.selectbox("Select Model", model_options)

        if selected_layer and selected_model:
            layer_detail = api_get(f"/layers/{selected_layer}")
            if layer_detail:
                row_count = layer_detail.get("row_counts", {}).get(selected_model, -1)

                info_col1, info_col2, info_col3 = st.columns(3)
                with info_col1:
                    st.metric(
                        "Layer",
                        selected_layer.upper(),
                        help=LAYER_DESCRIPTIONS.get(selected_layer),
                    )
                with info_col2:
                    st.metric("Model", selected_model)
                with info_col3:
                    if row_count >= 0:
                        st.metric("Row Count", f"{row_count:,}")
                    else:
                        st.metric("Row Count", "Not materialised")

                st.markdown(
                    f"*{LAYER_DESCRIPTIONS.get(selected_layer, '')}*"
                )

            preview_limit = st.slider("Preview rows", min_value=5, max_value=100, value=20, step=5)
            preview = api_get(f"/layers/{selected_layer}/{selected_model}?limit={preview_limit}")

            if preview and preview.get("data"):
                import pandas as pd

                df = pd.DataFrame(preview["data"])
                st.dataframe(df, use_container_width=True, height=400)
                st.caption(f"Showing {len(df)} of {row_count if row_count >= 0 else '?'} rows")
            elif preview and not preview.get("data"):
                st.warning("No data returned — has the pipeline been run?")
            else:
                st.error("Could not fetch preview data.")

# ===========================================================================
# TAB 3: Run Pipeline
# ===========================================================================

with tab3:
    st.header("Run Full Pipeline")
    st.markdown(
        "Triggers: data generation → dbt bronze → dbt silver → dbt gold → dbt tests"
    )

    if not api_available():
        st.error("API is not running. Start it with: `python main.py api`")
    else:
        status = api_get("/pipeline/status")
        is_running = status.get("running", False) if status else False

        col_btn, col_status = st.columns([1, 2])
        with col_btn:
            run_clicked = st.button(
                "Run Pipeline",
                disabled=is_running,
                type="primary",
                use_container_width=True,
            )
        with col_status:
            if is_running:
                st.warning("Pipeline is running...")
            elif status and status.get("last_result"):
                last = status["last_result"]
                if last.get("success"):
                    st.success(
                        f"Last run succeeded in {last.get('duration_seconds', 0):.1f}s"
                    )
                else:
                    st.error("Last run failed. See details below.")

        if run_clicked:
            result = api_post("/pipeline/run")
            if result:
                st.info(result.get("message", "Pipeline started."))
                with st.spinner("Waiting for pipeline to complete..."):
                    for _ in range(60):  # poll up to 60 × 3s = 3 min
                        time.sleep(3)
                        poll = api_get("/pipeline/status")
                        if poll and not poll.get("running", True):
                            break
                    else:
                        st.warning("Pipeline taking longer than expected — check API logs.")
                st.rerun()

        # Show last result details
        if status and status.get("last_result"):
            last = status["last_result"]

            st.subheader("Last Run Details")

            meta_col1, meta_col2, meta_col3 = st.columns(3)
            with meta_col1:
                st.metric("Status", "SUCCESS" if last.get("success") else "FAILED")
            with meta_col2:
                st.metric("Duration", f"{last.get('duration_seconds', 0):.1f}s")
            with meta_col3:
                st.metric("Started", last.get("started_at", "N/A")[:19])

            if last.get("errors"):
                st.error("Errors:")
                for err in last["errors"]:
                    st.code(err)

            # Steps
            if last.get("steps"):
                st.subheader("Pipeline Steps")
                for step in last["steps"]:
                    icon = "OK" if step.get("success") else "FAIL"
                    duration = step.get("duration_seconds", 0)
                    label = step.get("command", "")[-60:]
                    with st.expander(f"[{icon}] {label} ({duration:.1f}s)"):
                        stdout_tail = step.get("stdout_tail", "")
                        stderr_tail = step.get("stderr_tail", "")
                        if stdout_tail:
                            st.text("stdout (tail):")
                            st.code(stdout_tail, language="text")
                        if stderr_tail:
                            st.text("stderr (tail):")
                            st.code(stderr_tail, language="text")

            # Layer stats after run
            if last.get("layer_stats"):
                st.subheader("Row Counts per Layer")
                rows_data = []
                for layer, ls in last["layer_stats"].items():
                    for model, count in ls.get("row_counts", {}).items():
                        rows_data.append(
                            {"Layer": layer.upper(), "Model": model, "Row Count": count}
                        )
                if rows_data:
                    import pandas as pd

                    df_stats = pd.DataFrame(rows_data)
                    st.dataframe(df_stats, use_container_width=True, hide_index=True)

        else:
            st.info("No pipeline has been run yet. Click 'Run Pipeline' to start.")

# ===========================================================================
# TAB 4: Lineage
# ===========================================================================

with tab4:
    st.header("Data Lineage Graph")
    st.markdown(
        "Visual representation of data flow: "
        "Source CSV files → Bronze → Silver → Gold"
    )

    if not api_available():
        st.error("API is not running. Start it with: `python main.py api`")
    else:
        lineage = api_get("/lineage")

        if lineage:
            try:
                import plotly.graph_objects as go

                nodes = lineage.get("nodes", [])
                edges = lineage.get("edges", [])

                # Assign x/y positions by layer
                layer_order = {"source": 0, "bronze": 1, "silver": 2, "gold": 3}
                layer_nodes: Dict[str, List] = {
                    "source": [], "bronze": [], "silver": [], "gold": []
                }
                for node in nodes:
                    layer_nodes[node["layer"]].append(node)

                pos: Dict[str, tuple] = {}
                for layer_name, layer_nodes_list in layer_nodes.items():
                    x = layer_order[layer_name] * 3
                    n = len(layer_nodes_list)
                    for i, node in enumerate(layer_nodes_list):
                        y = (i - (n - 1) / 2) * 2
                        pos[node["id"]] = (x, y)

                # Build edge traces
                edge_traces = []
                for edge in edges:
                    x0, y0 = pos.get(edge["from"], (0, 0))
                    x1, y1 = pos.get(edge["to"], (0, 0))
                    edge_traces.append(
                        go.Scatter(
                            x=[x0, x1, None],
                            y=[y0, y1, None],
                            mode="lines",
                            line=dict(width=1.5, color="#555"),
                            hoverinfo="none",
                            showlegend=False,
                        )
                    )

                # Build node traces per layer
                node_traces = []
                for layer_name in ["source", "bronze", "silver", "gold"]:
                    layer_node_list = [n for n in nodes if n["layer"] == layer_name]
                    if not layer_node_list:
                        continue
                    xs = [pos[n["id"]][0] for n in layer_node_list]
                    ys = [pos[n["id"]][1] for n in layer_node_list]
                    labels = [n["id"] for n in layer_node_list]
                    colour = LAYER_COLOURS.get(layer_name, "#888")
                    node_traces.append(
                        go.Scatter(
                            x=xs,
                            y=ys,
                            mode="markers+text",
                            marker=dict(size=28, color=colour, line=dict(width=2, color="#fff")),
                            text=labels,
                            textposition="top center",
                            textfont=dict(size=9, color="#fff"),
                            name=layer_name.upper(),
                            hoverinfo="text",
                            hovertext=labels,
                        )
                    )

                fig = go.Figure(data=edge_traces + node_traces)
                fig.update_layout(
                    title="Medallion Architecture — Data Lineage DAG",
                    showlegend=True,
                    xaxis=dict(
                        showgrid=False,
                        zeroline=False,
                        showticklabels=False,
                        tickvals=[0, 3, 6, 9],
                        ticktext=["SOURCE", "BRONZE", "SILVER", "GOLD"],
                    ),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    height=600,
                    paper_bgcolor="#0e1117",
                    plot_bgcolor="#0e1117",
                    font_color="#fafafa",
                    margin=dict(l=20, r=20, t=60, b=20),
                )
                # Layer dividers
                for i, (x_pos, label) in enumerate(
                    [(0, "SOURCE"), (3, "BRONZE"), (6, "SILVER"), (9, "GOLD")]
                ):
                    colour = LAYER_COLOURS.get(label.lower(), "#888")
                    fig.add_annotation(
                        x=x_pos,
                        y=-4.5,
                        text=f"<b>{label}</b>",
                        showarrow=False,
                        font=dict(size=13, color=colour),
                    )

                st.plotly_chart(fig, use_container_width=True)

            except ImportError:
                st.warning("Plotly not installed — pip install plotly")
                # Fallback text lineage
                st.subheader("Text Lineage")
                for edge in edges:
                    st.markdown(f"  `{edge['from']}` → `{edge['to']}`")

            # Table view
            st.subheader("Lineage Table")
            import pandas as pd

            edge_df = pd.DataFrame(edges)
            edge_df.columns = ["Source Node", "Target Node"]
            st.dataframe(edge_df, use_container_width=True, hide_index=True)

        else:
            st.error("Could not fetch lineage data from API.")
