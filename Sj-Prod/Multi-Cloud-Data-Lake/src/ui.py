"""Streamlit dashboard for the Multi-Cloud Data Lake."""

import logging
import os

import requests
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Multi-Cloud Data Lake", layout="wide")
st.title("Multi-Cloud Data Lake Dashboard")
st.caption("Unified analytics across AWS, Azure, and GCP")


def api_get(path: str) -> dict:
    try:
        return requests.get(f"{API_URL}{path}", timeout=10).json()
    except requests.ConnectionError:
        logger.error("Cannot reach the API at %s", API_URL)
        st.error("Cannot reach the API. Is the server running?")
        st.stop()


# --- Sidebar ---
with st.sidebar:
    st.header("Data Management")
    if st.button("Regenerate All Data", type="primary"):
        with st.spinner("Generating cloud data and building lake..."):
            r = requests.post(f"{API_URL}/generate", timeout=120)
            if r.status_code == 200:
                st.success(f"Done in {r.json()['elapsed_seconds']}s")
                st.rerun()

    st.divider()
    st.header("Cloud Sources")
    clouds = api_get("/clouds")
    for cloud, files in clouds.get("clouds", {}).items():
        st.write(f"**{cloud.upper()}**: {', '.join(files)}")

    st.divider()
    st.header("Lake Tables")
    tables = api_get("/lake/tables")
    for t in tables.get("tables", []):
        st.write(f"- {t}")

# --- Main: Analytics ---
summary = api_get("/analytics/summary")

# Top metrics
st.header("Cross-Cloud Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Total Customers", f"{summary['total_customers']:,}")
col2.metric("Total Transactions", f"{summary['total_transactions']:,}")
total_rev = sum(summary.get("revenue_by_cloud", {}).values())
col3.metric("Total Revenue", f"${total_rev:,.2f}")

st.divider()

# Cloud comparison charts
chart1, chart2 = st.columns(2)

with chart1:
    st.subheader("Customers by Cloud")
    cbc = summary.get("customers_by_cloud", {})
    fig = px.pie(values=list(cbc.values()), names=list(cbc.keys()),
                 color=list(cbc.keys()),
                 color_discrete_map={"aws": "#FF9900", "azure": "#0089D6", "gcp": "#4285F4"})
    fig.update_layout(height=350, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader("Revenue by Cloud")
    rbc = summary.get("revenue_by_cloud", {})
    fig = px.bar(x=list(rbc.keys()), y=list(rbc.values()),
                 labels={"x": "Cloud", "y": "Revenue ($)"},
                 color=list(rbc.keys()),
                 color_discrete_map={"aws": "#FF9900", "azure": "#0089D6", "gcp": "#4285F4"})
    fig.update_layout(height=350, margin=dict(t=20, b=20), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

chart3, chart4 = st.columns(2)

with chart3:
    st.subheader("Revenue by Category")
    rcat = summary.get("revenue_by_category", {})
    fig = px.bar(x=list(rcat.keys()), y=list(rcat.values()),
                 labels={"x": "Category", "y": "Revenue ($)"},
                 color=list(rcat.values()), color_continuous_scale="Viridis")
    fig.update_layout(height=350, margin=dict(t=20, b=20), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with chart4:
    st.subheader("Customer Plans Distribution")
    plans = summary.get("customers_by_plan", {})
    fig = px.pie(values=list(plans.values()), names=list(plans.keys()),
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(height=350, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

# Active rate comparison
st.divider()
st.subheader("Active Customer Rate by Cloud")
active = summary.get("active_rate_by_cloud", {})
if active:
    fig = px.bar(x=list(active.keys()),
                 y=[v * 100 for v in active.values()],
                 labels={"x": "Cloud", "y": "Active Rate (%)"},
                 color=list(active.keys()),
                 color_discrete_map={"aws": "#FF9900", "azure": "#0089D6", "gcp": "#4285F4"})
    fig.update_layout(height=300, showlegend=False, yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig, use_container_width=True)

# Data explorer
st.divider()
st.header("Data Explorer")
table_list = api_get("/lake/tables").get("tables", [])
if table_list:
    selected_table = st.selectbox("Select table", table_list)
    cloud_filter = st.selectbox("Filter by cloud", ["All", "aws", "azure", "gcp"])
    params = {"limit": 50}
    if cloud_filter != "All":
        params["cloud"] = cloud_filter
    result = api_get(f"/lake/{selected_table}?{'&'.join(f'{k}={v}' for k,v in params.items())}")
    st.write(f"Showing {result['returned']} of {result['total_rows']} rows")
    if result["data"]:
        st.dataframe(pd.DataFrame(result["data"]), use_container_width=True)
