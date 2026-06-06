"""
main.py — Entry point for the Enterprise Data Quality Framework (POC-09).

Modes:
    validate  — Run DQ validation on all datasets, print scorecards to stdout
    api       — Start the FastAPI REST server (uvicorn)
    ui        — Start the Streamlit dashboard
    all       — validate + api (api runs in background)

Usage:
    python main.py                    # default: validate mode
    python main.py validate           # run DQ checks, print scorecards
    python main.py api                # start FastAPI on port 8000
    python main.py ui                 # start Streamlit on port 8501
    python main.py all                # validate then start API server

Environment variables:
    DQ_DATA_DIR    — override data directory (default: ./data)
    DQ_REPORTS_DIR — override reports directory (default: ./reports)
    API_PORT       — FastAPI port (default: 8000)
"""

import logging
import os
import sys
from datetime import datetime, timezone

# Ensure the project root is on sys.path so `from src.xxx` works
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import settings
from src.logging_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

DATA_DIR = os.environ.get("DQ_DATA_DIR", os.path.join(ROOT, "data"))
REPORTS_DIR = os.environ.get("DQ_REPORTS_DIR", os.path.join(ROOT, "reports"))
API_PORT = settings.API_PORT
API_HOST = settings.API_HOST
CONFIG_PATH = os.path.join(ROOT, "config", "dq_rules.json")


# ─────────────────────────────────────────────────────────────
# Core validate function — importable and testable
# ─────────────────────────────────────────────────────────────

def run_validate(verbose: bool = True) -> dict:
    """
    Run DQ validation on all three datasets and return a summary dict.

    This is the primary demonstration of the full DQ pipeline:
        DataGenerator → DataProfiler → DQValidator → DQScorer → DQReporter

    Returns:
        dict: { dataset_name: scorecard_dict }
    """
    from src.api import _add_referential_rules, build_rules_for_dataset
    from src.data_generator import load_or_generate
    from src.profiler import DataProfiler
    from src.reporter import DQReporter
    from src.scorer import DQScorer
    from src.validator import DQValidator

    logger.info("=" * 70)
    logger.info("  ENTERPRISE DATA QUALITY FRAMEWORK")
    logger.info("  Run started: %sZ", datetime.now(timezone.utc).isoformat().replace("+00:00", ""))
    logger.info("=" * 70)

    # Step 1: Load / generate datasets
    logger.info("[Step 1] Loading datasets...")
    datasets = load_or_generate(DATA_DIR)
    for name, df in datasets.items():
        logger.info("  - %s: %d rows x %d columns", name, len(df), len(df.columns))

    # Step 2: Initialise framework components
    profiler = DataProfiler()
    scorer = DQScorer()
    reporter = DQReporter(output_dir=REPORTS_DIR)

    results_summary = {}

    # Step 3: For each dataset, run the full DQ pipeline
    for dataset_name, df in datasets.items():
        logger.info("[Step 2] Profiling: %s...", dataset_name)
        profile = profiler.profile(df, dataset_name=dataset_name)
        if verbose:
            logger.info(profile.summary())

        logger.info("[Step 3] Building rules for: %s...", dataset_name)
        rules = build_rules_for_dataset(dataset_name, datasets)
        rules = _add_referential_rules(rules, dataset_name)
        logger.info("  - %d rules configured", len(rules))
        for r in rules:
            logger.info("      [%-13s] %-28s col=%-25s sev=%s", r.dimension, r.__class__.__name__, r.column, r.severity)

        logger.info("[Step 4] Validating: %s...", dataset_name)
        validator = DQValidator(rules)
        validation_result = validator.validate(df, dataset_name=dataset_name)
        if verbose:
            validation_result.print_summary()

        logger.info("[Step 5] Scoring: %s...", dataset_name)
        scorecard = scorer.compute_scores(validation_result)
        if verbose:
            scorecard.print_scorecard()

        logger.info("[Step 6] Generating report: %s...", dataset_name)
        report = reporter.generate_report(profile, validation_result, scorecard)
        report_path = reporter.save_report(report, dataset_name)
        logger.info("  Report saved: %s", report_path)

        if verbose:
            logger.info(reporter.format_text_summary(report))

        results_summary[dataset_name] = scorecard.to_dict()

    # Final cross-dataset summary
    summary_lines = [
        "=" * 70,
        "  CROSS-DATASET DQ SUMMARY",
        "=" * 70,
        f"  {'Dataset':<20} {'Score':>8} {'Grade':>6} {'Passed':>8} {'Failed':>8}",
        f"  {'-'*55}",
    ]
    for name, sc in results_summary.items():
        summary_lines.append(
            f"  {name:<20} {sc['overall_score']:>7.1f} {sc['overall_grade']:>6} "
            f"{sc['passed_rules']:>8} {sc['failed_rules']:>8}"
        )
    logger.info("\n".join(summary_lines))

    return results_summary


def run_api():
    """Start the FastAPI server using uvicorn."""
    try:
        import uvicorn
    except ImportError:
        logger.error("uvicorn not installed. Run: pip install uvicorn[standard]")
        sys.exit(1)

    logger.info("Starting FastAPI server on http://%s:%d", API_HOST, API_PORT)
    logger.info("Docs: http://localhost:%d/docs", API_PORT)
    uvicorn.run("src.api:app", host=API_HOST, port=API_PORT, reload=False, log_level="info")


def run_ui():
    """Start the Streamlit dashboard."""
    import subprocess
    ui_port = str(settings.UI_PORT)
    ui_path = os.path.join(ROOT, "src", "ui.py")
    logger.info("Starting Streamlit dashboard...")
    logger.info("Open: http://localhost:%s", ui_port)
    subprocess.run(
        ["streamlit", "run", ui_path, "--server.port", ui_port, "--server.headless", "true"],
        check=True,
    )


# ─────────────────────────────────────────────────────────────
# CLI entrypoint
# ─────────────────────────────────────────────────────────────

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "validate"

    if mode == "validate":
        run_validate(verbose=True)

    elif mode == "api":
        run_api()

    elif mode == "ui":
        run_ui()

    elif mode == "all":
        # Validate first, then start API
        run_validate(verbose=True)
        logger.info("Starting API server after validation...")
        run_api()

    else:
        logger.error("Unknown mode: %s", mode)
        logger.error("Usage: python main.py [validate|api|ui|all]")
        sys.exit(1)


if __name__ == "__main__":
    main()
