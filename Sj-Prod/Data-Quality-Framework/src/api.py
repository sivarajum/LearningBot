"""
api.py — FastAPI REST API for the Enterprise Data Quality Framework.

Endpoints:
    GET  /health                          — Health check
    GET  /datasets                        — List datasets with basic stats
    GET  /datasets/{name}/profile         — Full column profile
    POST /datasets/{name}/validate        — Run DQ validation, return full report
    GET  /datasets/{name}/score           — DQ scorecard with grades
    GET  /datasets/{name}/rules           — List configured rules
    GET  /summary                         — Cross-dataset DQ summary
    GET  /concepts                        — DQ concepts explanation

Run:
    uvicorn src.api:app --reload --port 8000
"""

import json
import logging
import os
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware

# Internal imports
from .data_generator import load_or_generate
from .profiler import DataProfiler
from .reporter import DQReporter
from .rules.base_rule import BaseRule
from .scorer import DQScorer
from .settings import CORS_ORIGINS
from .validator import DQValidator

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Bootstrap
# ─────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "dq_rules.json")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Load datasets on startup
logger.info("Loading datasets...")
DATASETS = load_or_generate(DATA_DIR)

# Load rule config
with open(CONFIG_PATH) as f:
    RULE_CONFIG = json.load(f)

profiler = DataProfiler()
scorer = DQScorer()
reporter = DQReporter(output_dir=REPORTS_DIR)


# ─────────────────────────────────────────────────────────────
# Rule Factory — build BaseRule objects from JSON config
# ─────────────────────────────────────────────────────────────

def build_rules_for_dataset(dataset_name: str, datasets: Dict = None) -> List[BaseRule]:
    """
    Build a list of BaseRule objects from the JSON config for a given dataset.
    Injects reference_values for ReferentialIntegrityRule at runtime.
    """
    from .rules.completeness import CompletenessRatioRule, NotNullRule
    from .rules.consistency import CrossColumnRule, ReferentialIntegrityRule
    from .rules.freshness import DataFreshnessRule
    from .rules.uniqueness import UniquenessRatioRule, UniqueRule
    from .rules.validity import AllowedValuesRule, RegexRule, TypeRule, ValueRangeRule

    RULE_MAP = {
        "NotNullRule": NotNullRule,
        "CompletenessRatioRule": CompletenessRatioRule,
        "RegexRule": RegexRule,
        "ValueRangeRule": ValueRangeRule,
        "AllowedValuesRule": AllowedValuesRule,
        "TypeRule": TypeRule,
        "UniqueRule": UniqueRule,
        "UniquenessRatioRule": UniquenessRatioRule,
        "ReferentialIntegrityRule": ReferentialIntegrityRule,
        "CrossColumnRule": CrossColumnRule,
        "DataFreshnessRule": DataFreshnessRule,
    }

    configs = RULE_CONFIG.get(dataset_name, [])
    rules = []

    for cfg in configs:
        rule_type = cfg.get("rule")
        if rule_type not in RULE_MAP:
            logger.warning("RuleFactory: Unknown rule type: %s -- skipping", rule_type)
            continue

        cls = RULE_MAP[rule_type]
        name = cfg.get("name", f"{rule_type}_{cfg.get('column', 'unknown')}")
        column = cfg.get("column", "")
        severity = cfg.get("severity", "error")

        try:
            if rule_type == "NotNullRule":
                rules.append(cls(name=name, column=column, severity=severity))

            elif rule_type == "CompletenessRatioRule":
                rules.append(cls(name=name, column=column,
                                 threshold=cfg.get("threshold", 0.05), severity=severity))

            elif rule_type == "RegexRule":
                rules.append(cls(name=name, column=column,
                                 pattern=cfg["pattern"], severity=severity))

            elif rule_type == "ValueRangeRule":
                rules.append(cls(name=name, column=column,
                                 min_val=cfg.get("min_val"), max_val=cfg.get("max_val"),
                                 severity=severity))

            elif rule_type == "AllowedValuesRule":
                rules.append(cls(name=name, column=column,
                                 allowed_values=set(cfg["allowed_values"]), severity=severity))

            elif rule_type == "TypeRule":
                rules.append(cls(name=name, column=column,
                                 expected_type=cfg["expected_type"], severity=severity))

            elif rule_type == "UniqueRule":
                rules.append(cls(name=name, column=column, severity=severity))

            elif rule_type == "UniquenessRatioRule":
                rules.append(cls(name=name, column=column,
                                 threshold=cfg.get("threshold", 0.95), severity=severity))

            elif rule_type == "ReferentialIntegrityRule":
                ref_dataset = cfg.get("reference_dataset")
                ref_column = cfg.get("reference_column")
                if datasets and ref_dataset and ref_column:
                    ref_values = set(datasets[ref_dataset][ref_column].dropna().astype(str))
                else:
                    ref_values = set(cfg.get("reference_values", []))
                rules.append(cls(name=name, column=column,
                                 reference_values=ref_values, severity=severity))

            elif rule_type == "CrossColumnRule":
                rules.append(cls(name=name, column=column,
                                 column_b=cfg["column_b"],
                                 operator=cfg["operator"], severity=severity))

            elif rule_type == "DataFreshnessRule":
                rules.append(cls(name=name, column=column,
                                 max_age_hours=cfg.get("max_age_hours", 48), severity=severity))

        except (KeyError, ValueError, TypeError) as e:
            logger.error("RuleFactory: Failed to build rule %s: %s", name, e)

    return rules


# Add referential integrity for transactions → customers at runtime
def _add_referential_rules(rules: List[BaseRule], dataset_name: str) -> List[BaseRule]:
    """Inject runtime-resolved referential integrity rules."""
    from .rules.consistency import ReferentialIntegrityRule

    if dataset_name == "transactions":
        valid_cids = set(DATASETS["customers"]["customer_id"].dropna().astype(str))
        rules.append(
            ReferentialIntegrityRule(
                name="txn_customer_ref_integrity",
                column="customer_id",
                reference_values=valid_cids,
                severity="error",
            )
        )
    return rules


# ─────────────────────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Enterprise Data Quality Framework",
    description="POC-09: Custom DQ Framework — rule-based validation, profiling, scoring, and alerting.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "framework": "Enterprise Data Quality Framework",
        "version": "1.0.0",
        "datasets_loaded": list(DATASETS.keys()),
    }


@app.get("/datasets")
def list_datasets():
    """List all available datasets with basic shape information."""
    result = {}
    for name, df in DATASETS.items():
        result[name] = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
        }
    return {"datasets": result}


@app.get("/datasets/{name}/profile")
def get_profile(name: str = Path(..., min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")):
    """Return a full statistical profile of the dataset."""
    if name not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Dataset '{name}' not found. Available: {list(DATASETS.keys())}")

    df = DATASETS[name]
    profile = profiler.profile(df, dataset_name=name)
    return profile.to_dict()


@app.post("/datasets/{name}/validate")
def validate_dataset(name: str = Path(..., min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")):
    """Run all configured DQ rules against the dataset and return a full report."""
    if name not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Dataset '{name}' not found.")

    df = DATASETS[name]
    rules = build_rules_for_dataset(name, DATASETS)
    rules = _add_referential_rules(rules, name)

    if not rules:
        raise HTTPException(status_code=400, detail=f"No rules configured for dataset '{name}'.")

    validator = DQValidator(rules)
    validation_result = validator.validate(df, dataset_name=name)

    profile = profiler.profile(df, dataset_name=name)
    scorecard = scorer.compute_scores(validation_result)
    report = reporter.generate_report(profile, validation_result, scorecard)

    return report


@app.get("/datasets/{name}/score")
def get_score(name: str = Path(..., min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")):
    """Run validation and return only the DQ scorecard (scores + grades per dimension)."""
    if name not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Dataset '{name}' not found.")

    df = DATASETS[name]
    rules = build_rules_for_dataset(name, DATASETS)
    rules = _add_referential_rules(rules, name)

    if not rules:
        raise HTTPException(status_code=400, detail=f"No rules configured for dataset '{name}'.")

    validator = DQValidator(rules)
    validation_result = validator.validate(df, dataset_name=name)
    scorecard = scorer.compute_scores(validation_result)
    return scorecard.to_dict()


@app.get("/datasets/{name}/rules")
def list_rules(name: str = Path(..., min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")):
    """List all configured rules for a dataset."""
    if name not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Dataset '{name}' not found.")

    rules = build_rules_for_dataset(name, DATASETS)
    rules = _add_referential_rules(rules, name)

    return {
        "dataset": name,
        "rule_count": len(rules),
        "rules": [
            {
                "name": r.name,
                "type": r.__class__.__name__,
                "column": r.column,
                "dimension": r.dimension,
                "severity": r.severity,
            }
            for r in rules
        ],
    }


@app.get("/summary")
def get_summary():
    """Cross-dataset summary: overall DQ score and grade per dataset."""
    summary = {}

    for name, df in DATASETS.items():
        try:
            rules = build_rules_for_dataset(name, DATASETS)
            rules = _add_referential_rules(rules, name)
            if not rules:
                continue

            validator = DQValidator(rules)
            validation_result = validator.validate(df, dataset_name=name)
            scorecard = scorer.compute_scores(validation_result)

            summary[name] = {
                "overall_score": round(scorecard.overall_score, 2),
                "overall_grade": scorecard.overall_grade,
                "grade_description": scorecard.grade_description,
                "rows": len(df),
                "total_rules": scorecard.total_rules,
                "passed_rules": scorecard.passed_rules,
                "failed_rules": scorecard.failed_rules,
                "critical_issues": len(scorecard.critical_issues),
                "dimensions": {
                    dim: {
                        "score": round(ds.score_0_to_100, 1),
                        "grade": ds.grade,
                    }
                    for dim, ds in scorecard.dimension_scores.items()
                },
            }
        except (KeyError, ValueError, TypeError, RuntimeError) as e:
            logger.error("Failed to compute summary for dataset %s: %s", name, e)
            summary[name] = {"error": str(e)}

    return {"summary": summary}


@app.get("/concepts")
def get_concepts():
    """Return educational content about DQ dimensions and framework architecture."""
    return {
        "title": "Data Quality Framework — Core Concepts",
        "dimensions": {
            "completeness": {
                "definition": "The degree to which required data values are present.",
                "score_weight": "30%",
                "examples": [
                    "Customer email is null",
                    "Transaction amount is missing",
                    "Product name not populated",
                ],
                "rules": ["NotNullRule", "CompletenessRatioRule"],
                "real_world_impact": "At PayPal, 5% null merchant_id caused settlement batch failures.",
            },
            "validity": {
                "definition": "The degree to which data conforms to defined formats, types, and ranges.",
                "score_weight": "25%",
                "examples": [
                    "Email does not contain @ symbol",
                    "Age is -5 (invalid negative)",
                    "Status is 'ACTIV' instead of 'active'",
                ],
                "rules": ["RegexRule", "ValueRangeRule", "AllowedValuesRule", "TypeRule"],
                "real_world_impact": "At FedEx, invalid zip codes caused routing failures costing $2M/year.",
            },
            "uniqueness": {
                "definition": "The degree to which data values are free from unintended duplication.",
                "score_weight": "20%",
                "examples": [
                    "Duplicate customer IDs in CRM",
                    "Same transaction processed twice",
                    "Duplicate product SKUs",
                ],
                "rules": ["UniqueRule", "UniquenessRatioRule"],
                "real_world_impact": "At PayPal, duplicate transaction_id = double-posting in ledger.",
            },
            "consistency": {
                "definition": "The degree to which data is coherent within and across datasets.",
                "score_weight": "15%",
                "examples": [
                    "Transaction references a customer_id that doesn't exist",
                    "Shipment delivery_date < pickup_date",
                    "Invoice total != sum of line items",
                ],
                "rules": ["ReferentialIntegrityRule", "CrossColumnRule"],
                "real_world_impact": "Orphaned transaction records blocked monthly reconciliation at FedEx.",
            },
            "freshness": {
                "definition": "The degree to which data is sufficiently recent for its intended use.",
                "score_weight": "10%",
                "examples": [
                    "Risk model receiving yesterday's data instead of today's",
                    "Dashboard showing 48-hour-old inventory counts",
                    "Fraud model running on week-old transaction data",
                ],
                "rules": ["DataFreshnessRule"],
                "real_world_impact": "Stale transaction data caused PayPal fraud model to miss new attack patterns.",
            },
        },
        "scoring": {
            "methodology": "Weighted average of dimension scores",
            "grades": {
                "A (90-100)": "Production-ready",
                "B (75-89)": "Minor issues — monitor closely",
                "C (60-74)": "Significant issues — remediation needed",
                "D (45-59)": "Serious problems — investigate before use",
                "F (<45)": "Data not fit for use",
            },
        },
        "architecture": {
            "layers": [
                "1. Data Generator — synthetic data with known issues",
                "2. Profiler — auto-profile any DataFrame (stats, distributions)",
                "3. Rules Engine — extensible rule classes per DQ dimension",
                "4. Validator — orchestrates rule execution, collects results",
                "5. Scorer — computes weighted 0-100 scores with letter grades",
                "6. Reporter — assembles JSON reports + alerts + recommendations",
                "7. API (FastAPI) — REST interface for all DQ operations",
                "8. UI (Streamlit) — interactive dashboard for exploration",
            ]
        },
    }
