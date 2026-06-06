"""Streamlit dashboard for churn prediction."""

import os
import requests
import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Churn Prediction Dashboard", layout="wide")
st.title("Customer Churn Prediction Dashboard")


# --- Helper ---
def api_get(path: str) -> dict:
    try:
        return requests.get(f"{API_URL}{path}", timeout=5).json()
    except requests.ConnectionError:
        st.error("Cannot reach the API. Ensure the API service is running.")
        st.stop()


def api_post(path: str, payload: dict) -> dict:
    try:
        return requests.post(f"{API_URL}{path}", json=payload, timeout=10).json()
    except requests.ConnectionError:
        st.error("Cannot reach the API. Ensure the API service is running.")
        st.stop()


# --- Model Info Section ---
info = api_get("/model-info")
metrics = info.get("metrics", {})

st.header("Model Performance")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Accuracy", f"{metrics.get('accuracy', 0):.2%}")
col2.metric("Precision", f"{metrics.get('precision', 0):.2%}")
col3.metric("Recall", f"{metrics.get('recall', 0):.2%}")
col4.metric("F1 Score", f"{metrics.get('f1', 0):.2%}")

st.divider()

# --- Feature Importance Chart ---
feat_imp = info.get("feature_importance", {})
if feat_imp:
    st.header("Feature Importance")
    fig_imp = px.bar(
        x=list(feat_imp.values()),
        y=list(feat_imp.keys()),
        orientation="h",
        labels={"x": "Importance", "y": "Feature"},
        color=list(feat_imp.values()),
        color_continuous_scale="Teal",
    )
    fig_imp.update_layout(height=400, yaxis=dict(autorange="reversed"), showlegend=False)
    st.plotly_chart(fig_imp, use_container_width=True)

# --- Confusion Matrix Heatmap ---
cm = metrics.get("confusion_matrix")
if cm:
    st.header("Confusion Matrix")
    fig_cm = ff.create_annotated_heatmap(
        z=cm,
        x=["No Churn", "Churn"],
        y=["No Churn", "Churn"],
        colorscale="Blues",
        showscale=True,
    )
    fig_cm.update_layout(
        xaxis_title="Predicted", yaxis_title="Actual",
        height=400, yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig_cm, use_container_width=True)

st.divider()

# --- Individual Prediction Form ---
st.header("Predict Customer Churn")
with st.form("predict_form"):
    c1, c2 = st.columns(2)
    tenure = c1.slider("Tenure (months)", 1, 72, 12)
    monthly = c1.slider("Monthly Charges ($)", 20.0, 120.0, 65.0, step=1.0)
    tickets = c1.slider("Support Tickets", 0, 10, 2)
    contract = c2.selectbox("Contract Type", ["month-to-month", "one_year", "two_year"])
    payment = c2.selectbox(
        "Payment Method",
        ["electronic_check", "mailed_check", "bank_transfer", "credit_card"],
    )
    internet = c2.selectbox("Internet Service", ["DSL", "Fiber", "No"])
    submitted = st.form_submit_button("Predict Churn Risk")

if submitted:
    payload = {
        "tenure": tenure,
        "monthly_charges": monthly,
        "contract_type": contract,
        "payment_method": payment,
        "internet_service": internet,
        "num_support_tickets": tickets,
    }
    result = api_post("/predict", payload)
    prob = result["churn_probability"]

    color = "red" if prob >= 0.5 else ("orange" if prob >= 0.3 else "green")
    st.subheader(f":{color}[Churn Risk: {prob:.1%}]")
    st.write(f"**Prediction:** {result['prediction'].replace('_', ' ').title()}")

    st.write("**Top Contributing Features:**")
    for name, imp in result["top_contributing_features"]:
        st.write(f"- {name}: {imp:.4f}")
