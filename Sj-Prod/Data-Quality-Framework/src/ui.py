"""
ui.py — Streamlit dashboard for the Enterprise Data Quality Framework.

Tabs:
    1. DQ Dashboard      — Overview: score gauges, grade badges, issue counts
    2. Dataset Explorer  — Column profile table + issue list per dataset
    3. Validation Results— Rule-by-rule results with color-coded pass/fail
    4. DQ Concepts       — Educational content: dimensions, scoring, architecture

Run:
    streamlit run src/ui.py
"""

import os
import sys
from typing import Any, Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Ensure src/ is on the path when running as `streamlit run src/ui.py`
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.api import _add_referential_rules, build_rules_for_dataset
from src.data_generator import load_or_generate
from src.profiler import DataProfiler
from src.reporter import DQReporter
from src.scorer import DIMENSION_WEIGHTS, DQScorer
from src.validator import DQValidator

# ─────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Enterprise Data Quality Framework",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# Load data (cached)
# ─────────────────────────────────────────────────────────────

DATA_DIR = os.path.join(_ROOT, "data")
REPORTS_DIR = os.path.join(_ROOT, "reports")

_profiler = DataProfiler()
_scorer = DQScorer()
_reporter = DQReporter(output_dir=REPORTS_DIR)


@st.cache_data(show_spinner="Loading datasets...")
def load_datasets() -> Dict[str, pd.DataFrame]:
    return load_or_generate(DATA_DIR)


@st.cache_data(show_spinner="Running DQ validation...")
def run_validation(dataset_name: str) -> Dict[str, Any]:
    """Run full DQ pipeline: validate + score + report. Returns report dict."""
    datasets = load_datasets()
    df = datasets[dataset_name]

    rules = build_rules_for_dataset(dataset_name, datasets)
    rules = _add_referential_rules(rules, dataset_name)

    validator = DQValidator(rules)
    validation_result = validator.validate(df, dataset_name=dataset_name)
    profile = _profiler.profile(df, dataset_name=dataset_name)
    scorecard = _scorer.compute_scores(validation_result)
    report = _reporter.generate_report(profile, validation_result, scorecard)
    return report


@st.cache_data(show_spinner="Computing all scores...")
def get_all_scores() -> Dict[str, Dict]:
    """Run validation on all datasets and return scorecards."""
    datasets = load_datasets()
    scores = {}
    for name in datasets.keys():
        try:
            report = run_validation(name)
            scores[name] = report["scorecard"]
        except Exception as e:
            scores[name] = {"error": str(e)}
    return scores


# ─────────────────────────────────────────────────────────────
# Helper: Gauge chart
# ─────────────────────────────────────────────────────────────

def make_gauge(score: float, title: str) -> go.Figure:
    """Create a Plotly gauge chart for a DQ score (0-100)."""
    if score >= 90:
        color = "#2ecc71"
    elif score >= 75:
        color = "#27ae60"
    elif score >= 60:
        color = "#f39c12"
    elif score >= 45:
        color = "#e67e22"
    else:
        color = "#e74c3c"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": title, "font": {"size": 14}},
        number={"suffix": "/100", "font": {"size": 18}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 45], "color": "#fadbd8"},
                {"range": [45, 60], "color": "#fdebd0"},
                {"range": [60, 75], "color": "#fef9e7"},
                {"range": [75, 90], "color": "#eafaf1"},
                {"range": [90, 100], "color": "#d5f5e3"},
            ],
            "threshold": {
                "line": {"color": "black", "width": 3},
                "thickness": 0.75,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        height=220,
        margin={"t": 60, "b": 10, "l": 10, "r": 10},
    )
    return fig


def grade_badge(grade: str) -> str:
    """Return an HTML-styled grade badge."""
    colors = {
        "A": ("#27ae60", "white"),
        "B": ("#2980b9", "white"),
        "C": ("#f39c12", "white"),
        "D": ("#e67e22", "white"),
        "F": ("#e74c3c", "white"),
    }
    bg, fg = colors.get(grade, ("#7f8c8d", "white"))
    return f'<span style="background:{bg};color:{fg};padding:4px 12px;border-radius:12px;font-weight:bold;font-size:18px;">{grade}</span>'


def severity_color(severity: str) -> str:
    return {"error": "#e74c3c", "warning": "#f39c12", "info": "#3498db"}.get(severity, "#7f8c8d")


def pass_fail_badge(passed: bool) -> str:
    if passed:
        return '<span style="background:#27ae60;color:white;padding:2px 8px;border-radius:6px;font-size:12px;">PASS</span>'
    return '<span style="background:#e74c3c;color:white;padding:2px 8px;border-radius:6px;font-size:12px;">FAIL</span>'


# ─────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("DQ Framework")
    st.caption("POC-09 — Enterprise Data Quality")
    st.divider()
    datasets = load_datasets()
    dataset_names = list(datasets.keys())
    selected_dataset = st.selectbox("Select Dataset", dataset_names, index=0)
    st.divider()
    st.markdown("**Framework Layers**")
    st.markdown("""
- Rules Engine
- DataProfiler
- DQValidator
- DQScorer
- DQReporter
- FastAPI
- Streamlit UI
""")
    st.divider()
    if st.button("Clear Cache & Reload"):
        st.cache_data.clear()
        st.rerun()

# ─────────────────────────────────────────────────────────────
# Tab layout
# ─────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "DQ Dashboard",
    "Dataset Explorer",
    "Validation Results",
    "DQ Concepts",
])

# ─────────────────────────────────────────────────────────────
# TAB 1: DQ Dashboard
# ─────────────────────────────────────────────────────────────

with tab1:
    st.header("DQ Dashboard — All Datasets")
    st.caption("Overall DQ scores, grades, and issue counts across all configured datasets.")

    all_scores = get_all_scores()

    # Top-level metrics row
    total_rules_all = sum(sc.get("total_rules", 0) for sc in all_scores.values() if "error" not in sc)
    total_failed_all = sum(sc.get("failed_rules", 0) for sc in all_scores.values() if "error" not in sc)
    total_critical = sum(len(sc.get("critical_issues", [])) for sc in all_scores.values() if "error" not in sc)
    avg_score = (
        sum(sc.get("overall_score", 0) for sc in all_scores.values() if "error" not in sc)
        / len([sc for sc in all_scores.values() if "error" not in sc])
        if all_scores else 0
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Datasets Monitored", len(datasets))
    col2.metric("Avg DQ Score", f"{avg_score:.1f}/100")
    col3.metric("Total Rules", total_rules_all)
    col4.metric("Critical Issues", total_critical, delta=f"-{total_failed_all} failed rules", delta_color="inverse")

    st.divider()

    # Per-dataset gauge + grade
    gauge_cols = st.columns(len(dataset_names))
    for i, name in enumerate(dataset_names):
        sc = all_scores.get(name, {})
        if "error" in sc:
            gauge_cols[i].error(f"{name}: {sc['error']}")
            continue

        score = sc.get("overall_score", 0)
        grade = sc.get("overall_grade", "?")
        grade_desc = sc.get("grade_description", "")
        passed = sc.get("passed_rules", 0)
        total = sc.get("total_rules", 0)
        failed = sc.get("failed_rules", 0)
        rows = sc.get("row_count", 0)

        with gauge_cols[i]:
            st.plotly_chart(make_gauge(score, name.capitalize()), use_container_width=True)
            st.markdown(f"Grade: {grade_badge(grade)}", unsafe_allow_html=True)
            st.caption(grade_desc)
            st.markdown(f"**{passed}/{total}** rules pass | **{failed}** failed | **{rows:,}** rows")

    st.divider()

    # Dimension heatmap
    st.subheader("Dimension Scores Heatmap")
    dim_data = []
    for name in dataset_names:
        sc = all_scores.get(name, {})
        if "error" in sc:
            continue
        for dim, dim_sc in sc.get("dimensions", {}).items():
            dim_data.append({
                "Dataset": name.capitalize(),
                "Dimension": dim.capitalize(),
                "Score": round(dim_sc.get("score", 0), 1),
                "Grade": dim_sc.get("grade", "?"),
            })

    if dim_data:
        dim_df = pd.DataFrame(dim_data)
        pivot = dim_df.pivot(index="Dimension", columns="Dataset", values="Score")

        fig_heat = px.imshow(
            pivot,
            text_auto=True,
            color_continuous_scale=[[0, "#e74c3c"], [0.45, "#e67e22"], [0.6, "#f39c12"],
                                     [0.75, "#27ae60"], [1.0, "#1abc9c"]],
            zmin=0, zmax=100,
            aspect="auto",
        )
        fig_heat.update_layout(
            title="DQ Score by Dimension and Dataset (0–100)",
            height=350,
            coloraxis_colorbar={"title": "Score"},
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # Alert summary table
    st.subheader("Issue Summary")
    issue_rows = []
    for name in dataset_names:
        sc = all_scores.get(name, {})
        if "error" in sc:
            continue
        for issue in sc.get("critical_issues", []):
            issue_rows.append({"Dataset": name, "Severity": "error", "Issue": issue[:120]})

    if issue_rows:
        st.dataframe(
            pd.DataFrame(issue_rows),
            use_container_width=True,
            column_config={"Severity": st.column_config.TextColumn(width="small")},
        )
    else:
        st.success("No critical issues detected across all datasets.")

# ─────────────────────────────────────────────────────────────
# TAB 2: Dataset Explorer
# ─────────────────────────────────────────────────────────────

with tab2:
    st.header(f"Dataset Explorer — {selected_dataset.capitalize()}")

    df = datasets[selected_dataset]
    report = run_validation(selected_dataset)
    profile = report["profile"]

    # Dataset metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", f"{profile['row_count']:,}")
    col2.metric("Columns", profile["column_count"])
    col3.metric("Duplicate Rows", profile["duplicate_rows"])
    col4.metric("Dup Rate", f"{profile['duplicate_rate'] * 100:.2f}%")

    st.divider()

    # Column profile table
    st.subheader("Column Profiles")
    col_rows = []
    for cp in profile["columns"]:
        col_rows.append({
            "Column": cp["column"],
            "Type": cp["inferred_type"],
            "Null Count": cp["null_count"],
            "Null %": f"{cp['null_rate'] * 100:.1f}%",
            "Distinct": cp["distinct_count"],
            "Distinct %": f"{cp['distinct_rate'] * 100:.1f}%",
            "Min": str(cp.get("min_value", ""))[:20],
            "Max": str(cp.get("max_value", ""))[:20],
            "Mean": str(cp.get("mean_value", ""))[:10] if cp.get("mean_value") is not None else "",
        })

    st.dataframe(pd.DataFrame(col_rows), use_container_width=True, height=350)

    # Null rate bar chart
    st.subheader("Null Rate by Column")
    null_data = pd.DataFrame([
        {"Column": cp["column"], "Null %": cp["null_rate"] * 100}
        for cp in profile["columns"]
    ])
    fig_null = px.bar(
        null_data, x="Column", y="Null %",
        color="Null %",
        color_continuous_scale=[[0, "#27ae60"], [0.1, "#f39c12"], [1.0, "#e74c3c"]],
        title="Null Rate (%) per Column",
        labels={"Null %": "Null Rate (%)"},
    )
    fig_null.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig_null, use_container_width=True)

    # Raw data sample
    st.subheader("Data Sample (first 20 rows)")
    st.dataframe(df.head(20), use_container_width=True)


# ─────────────────────────────────────────────────────────────
# TAB 3: Validation Results
# ─────────────────────────────────────────────────────────────

with tab3:
    st.header(f"Validation Results — {selected_dataset.capitalize()}")

    report = run_validation(selected_dataset)
    sc = report["scorecard"]
    val = report["validation"]
    alerts = report.get("alerts", [])
    recs = report.get("recommendations", [])

    # Scorecard header
    score = sc["overall_score"]
    grade = sc["overall_grade"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.plotly_chart(make_gauge(score, "Overall DQ Score"), use_container_width=True)
    with col2:
        st.markdown(f"### Grade: {grade_badge(grade)}", unsafe_allow_html=True)
        st.markdown(f"*{sc['grade_description']}*")
        st.metric("Rules Passed", sc["passed_rules"])
        st.metric("Rules Failed", sc["failed_rules"])
    with col3:
        st.metric("Total Rules", sc["total_rules"])
        st.metric("Row Count", f"{sc['row_count']:,}")
        st.metric("Critical Issues", len(sc.get("critical_issues", [])))
    with col4:
        st.metric("Validated At", val.get("validated_at", "")[:19])
        overall_pass = val.get("overall_passed", False)
        if overall_pass:
            st.success("Overall: PASSED")
        else:
            st.error("Overall: FAILED")

    st.divider()

    # Dimension score bars
    st.subheader("Scores by DQ Dimension")
    dim_cols = st.columns(5)
    dim_order = ["completeness", "validity", "uniqueness", "consistency", "freshness"]
    for i, dim in enumerate(dim_order):
        dim_sc = sc.get("dimensions", {}).get(dim, {})
        d_score = dim_sc.get("score", 0)
        d_grade = dim_sc.get("grade", "?")
        d_passed = dim_sc.get("passed_rules", 0)
        d_total = dim_sc.get("rule_count", 0)
        weight = int(DIMENSION_WEIGHTS.get(dim, 0) * 100)
        with dim_cols[i]:
            st.metric(
                label=f"{dim.capitalize()} ({weight}%)",
                value=f"{d_score:.1f}",
                delta=f"Grade {d_grade}",
            )
            st.progress(int(min(d_score, 100)))
            st.caption(f"{d_passed}/{d_total} rules pass")

    st.divider()

    # Rule-by-rule results table
    st.subheader("Rule Results")

    severity_filter = st.multiselect(
        "Filter by severity",
        ["error", "warning", "info"],
        default=["error", "warning", "info"],
    )
    status_filter = st.multiselect(
        "Filter by status",
        ["PASS", "FAIL"],
        default=["PASS", "FAIL"],
    )

    rule_rows = []
    for r in val.get("rule_results", []):
        sev = r.get("severity", "error")
        passed = r.get("passed", False)
        status_str = "PASS" if passed else "FAIL"

        if sev not in severity_filter:
            continue
        if status_str not in status_filter:
            continue

        rule_rows.append({
            "Rule": r["rule_name"],
            "Column": r["column"],
            "Dimension": r["dimension"],
            "Severity": sev.upper(),
            "Status": status_str,
            "Score": round(r.get("score", 0) * 100, 1),
            "Pass Rate": f"{r.get('pass_rate', 0) * 100:.1f}%",
            "Failures": r.get("failing_count", 0),
            "Total": r.get("total_count", 0),
        })

    if rule_rows:
        rule_df = pd.DataFrame(rule_rows)

        def color_status(val):
            return "background-color: #d5f5e3" if val == "PASS" else "background-color: #fadbd8"

        st.dataframe(
            rule_df.style.applymap(color_status, subset=["Status"]),
            use_container_width=True,
            height=400,
        )
    else:
        st.info("No rule results match the selected filters.")

    st.divider()

    # Alerts
    if alerts:
        st.subheader(f"Alerts ({len(alerts)})")
        for alert in alerts:
            sev = alert.get("severity", "info")
            msg = alert.get("message", "")
            rule = alert.get("rule_name", "")
            col = alert.get("column", "")
            if sev == "error":
                st.error(f"[{rule}] {col}: {msg}")
            elif sev == "warning":
                st.warning(f"[{rule}] {col}: {msg}")
            else:
                st.info(f"[{rule}] {col}: {msg}")

    # Recommendations
    if recs:
        st.subheader(f"Recommendations ({len(recs)})")
        for i, rec in enumerate(recs, 1):
            st.markdown(f"{i}. {rec}")

# ─────────────────────────────────────────────────────────────
# TAB 4: DQ Concepts
# ─────────────────────────────────────────────────────────────

with tab4:
    st.header("Data Quality Concepts")
    st.caption("A comprehensive reference guide for Data Architects and Principal Data Engineers.")

    st.subheader("The 5 DQ Dimensions (in this framework)")

    dim_info = {
        "Completeness (30%)": {
            "icon": ":white_check_mark:",
            "definition": "The degree to which required data values are present.",
            "rules": "NotNullRule, CompletenessRatioRule",
            "examples": ["Customer email is null", "Transaction amount missing", "Product name not populated"],
            "impact": "Missing data breaks downstream calculations, reporting, and ML features.",
            "real_world": "At PayPal: 5% null merchant_id caused settlement batch failures on Fridays.",
        },
        "Validity (25%)": {
            "icon": ":memo:",
            "definition": "The degree to which data conforms to defined formats, types, and business rules.",
            "rules": "RegexRule, ValueRangeRule, AllowedValuesRule, TypeRule",
            "examples": ["Email missing @ symbol", "Age = -5 (impossible)", "Status = 'ACTIV' (typo)"],
            "impact": "Invalid data causes ETL failures, incorrect analytics, and customer-facing errors.",
            "real_world": "At FedEx: invalid ZIP codes caused routing failures costing $2M+/year.",
        },
        "Uniqueness (20%)": {
            "icon": ":keycap_one:",
            "definition": "The degree to which data values are free from unintended duplication.",
            "rules": "UniqueRule, UniquenessRatioRule",
            "examples": ["Duplicate customer IDs", "Same transaction processed twice", "Duplicate product SKUs"],
            "impact": "Duplicates inflate counts, corrupt aggregations, and double-charge customers.",
            "real_world": "At PayPal: duplicate transaction_id = double-posting in the ledger (P0 incident).",
        },
        "Consistency (15%)": {
            "icon": ":link:",
            "definition": "The degree to which data is logically coherent within and across datasets.",
            "rules": "ReferentialIntegrityRule, CrossColumnRule",
            "examples": ["Transaction references non-existent customer_id", "end_date < start_date"],
            "impact": "Inconsistent data breaks joins, reconciliations, and multi-system processes.",
            "real_world": "At FedEx: orphaned shipments blocked monthly revenue reconciliation for 3 days.",
        },
        "Freshness (10%)": {
            "icon": ":clock1:",
            "definition": "The degree to which data is sufficiently recent for its intended use.",
            "rules": "DataFreshnessRule",
            "examples": ["Risk model receiving yesterday's transactions", "Dashboard showing 2-day-old inventory"],
            "impact": "Stale data causes wrong decisions — fraud model misses new attack patterns.",
            "real_world": "At PayPal: 6-hour stale data on fraud model = $500K undetected fraud in one batch.",
        },
    }

    for dim_name, info in dim_info.items():
        with st.expander(f"{dim_name}", expanded=False):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**Definition:** {info['definition']}")
                st.markdown(f"**Rules:** `{info['rules']}`")
                st.markdown("**Examples of violations:**")
                for ex in info["examples"]:
                    st.markdown(f"  - {ex}")
                st.markdown(f"**Business Impact:** {info['impact']}")
            with col2:
                st.info(f"**Real-World Example:**\n\n{info['real_world']}")

    st.divider()

    st.subheader("Scoring Methodology")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
**How scores are calculated:**

1. Each rule returns a score from 0.0 to 1.0
   - `score = (passing rows) / (total rows)`

2. Dimension score = average of all rule scores in that dimension × 100

3. Overall score = weighted average of dimension scores:
   - Completeness: 30%
   - Validity:     25%
   - Uniqueness:   20%
   - Consistency:  15%
   - Freshness:    10%

4. Letter grade assigned based on overall score
""")
    with col2:
        grades = pd.DataFrame([
            {"Grade": "A", "Score Range": "90–100", "Interpretation": "Production-ready"},
            {"Grade": "B", "Score Range": "75–89", "Interpretation": "Minor issues — monitor"},
            {"Grade": "C", "Score Range": "60–74", "Interpretation": "Remediation needed"},
            {"Grade": "D", "Score Range": "45–59", "Interpretation": "Investigate before use"},
            {"Grade": "F", "Score Range": "< 45",  "Interpretation": "Not fit for use"},
        ])
        st.dataframe(grades, use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("Framework Architecture")
    st.code("""
Enterprise DQ Framework — Architecture Layers

Layer 1: Data Generator
    Produces realistic datasets with known DQ issues for testing.
    Class: DataGenerator → customers.csv, transactions.csv, products.csv

Layer 2: Rules Engine (src/rules/)
    BaseRule (ABC) → every rule must implement validate(df) → RuleResult
    Dimensions:
        completeness/ : NotNullRule, CompletenessRatioRule
        validity/     : RegexRule, ValueRangeRule, AllowedValuesRule, TypeRule
        uniqueness/   : UniqueRule, UniquenessRatioRule
        consistency/  : ReferentialIntegrityRule, CrossColumnRule
        freshness/    : DataFreshnessRule

Layer 3: DataProfiler
    Auto-profiles any DataFrame → ColumnProfile, DatasetProfile
    No schema required — discovers statistics automatically.

Layer 4: DQValidator
    Orchestrates rule execution → ValidationResult
    Catches rule-level exceptions gracefully.

Layer 5: DQScorer
    ValidationResult → DQScoreCard (0-100 per dimension + letter grade)
    Weighted scoring: completeness 30%, validity 25%, uniqueness 20%,
                      consistency 15%, freshness 10%

Layer 6: DQReporter
    Assembles profile + validation + scorecard → full JSON report
    Generates alerts and auto-recommendations.

Layer 7: FastAPI (src/api.py)
    REST endpoints for all DQ operations.
    Rule factory: builds rule objects from config/dq_rules.json.

Layer 8: Streamlit (src/ui.py)
    Interactive dashboard: gauges, heatmaps, rule tables, concept guide.
""", language="text")

    st.divider()
    st.subheader("How to Add a Custom Rule")
    st.code("""
# Step 1: Create your rule class in the appropriate file
# src/rules/validity.py (or a new file for a new dimension)

from .base_rule import BaseRule, RuleResult
import pandas as pd

class PhoneFormatRule(BaseRule):
    dimension = "validity"

    def __init__(self, name: str, column: str, severity: str = "warning"):
        super().__init__(name=name, column=column, severity=severity)
        import re
        self._pattern = re.compile(r'^\\+?[1-9]\\d{7,14}$')

    def validate(self, df: pd.DataFrame) -> RuleResult:
        missing = self._check_column_exists(df)
        if missing:
            return missing

        non_null = df[self.column].dropna().astype(str)
        cleaned = non_null.str.replace(r'[\\s\\-\\(\\)]', '', regex=True)
        failing_mask = ~cleaned.str.match(self._pattern)
        return self._build_result(
            df,
            failing_mask=df[self.column].notna() & ~df[self.column].astype(str).str.replace(r'[\\s\\-\\(\\)]', '', regex=True).str.match(self._pattern),
            details=f"Column '{self.column}': {failing_mask.sum()} invalid phone numbers."
        )

# Step 2: Add to src/rules/__init__.py
from .validity import PhoneFormatRule

# Step 3: Add to config/dq_rules.json
{
  "rule": "PhoneFormatRule",
  "name": "phone_format_check",
  "column": "phone",
  "severity": "warning"
}

# Step 4: Add to build_rules_for_dataset() in src/api.py
elif rule_type == "PhoneFormatRule":
    rules.append(cls(name=name, column=column, severity=severity))
""", language="python")
