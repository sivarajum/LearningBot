"""
main.py — Entry point for POC-07: Enterprise Airflow Orchestration Platform
============================================================================

Usage:
    python main.py api                  # Start FastAPI server (port 8000)
    python main.py ui                   # Start Streamlit UI (port 8501)
    python main.py all                  # Start both (API + UI) simultaneously
    python main.py simulate             # Simulate all DAGs and print results
    python main.py simulate <dag_id>    # Simulate a specific DAG

Examples:
    python main.py simulate etl_transactions_pipeline
    python main.py simulate data_quality_pipeline
    python main.py simulate multi_source_etl_customer_journey
    python main.py simulate etl_sales
    python main.py api
    python main.py ui
"""

import sys
import os
import subprocess
import threading
import time
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Ensure the project root is in sys.path so `from src.xxx import yyy` works
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.logging_config import setup_logging
from src.settings import API_HOST, API_PORT, LOG_LEVEL, UI_PORT

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ANSI colours for terminal output
# ---------------------------------------------------------------------------
_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_GREEN  = "\033[32m"
_RED    = "\033[31m"
_YELLOW = "\033[33m"
_BLUE   = "\033[34m"
_CYAN   = "\033[36m"
_GREY   = "\033[90m"

def c(text, color): return f"{color}{text}{_RESET}"
def bold(text): return c(text, _BOLD)
def green(text): return c(text, _GREEN)
def red(text): return c(text, _RED)
def yellow(text): return c(text, _YELLOW)
def blue(text): return c(text, _BLUE)
def cyan(text): return c(text, _CYAN)
def grey(text): return c(text, _GREY)


# ---------------------------------------------------------------------------
# Simulate mode
# ---------------------------------------------------------------------------

def run_simulate(dag_ids: list = None):
    """Run DAG simulations and print a formatted trace to the terminal."""
    print()
    print(bold("=" * 70))
    print(bold("  POC-07: Airflow Orchestration — DAG Simulator"))
    print(bold("=" * 70))
    print()

    try:
        from src.simulator import get_simulator, STATUS_COLORS
    except ImportError as e:
        print(red(f"  Cannot import simulator: {e}"))
        print(yellow("  Make sure you are in the POC-07 directory and have installed requirements:"))
        print(yellow("    pip install -r requirements.txt"))
        sys.exit(1)

    sim = get_simulator()
    all_dags = sim.list_dags()

    if not all_dags:
        print(red("  No DAGs found. Check the dags/ directory."))
        sys.exit(1)

    if dag_ids:
        # Validate requested dag_ids
        available_ids = {d.dag_id for d in all_dags}
        invalid = [d for d in dag_ids if d not in available_ids]
        if invalid:
            print(red(f"  Unknown DAG(s): {invalid}"))
            print(f"  Available: {sorted(available_ids)}")
            sys.exit(1)
        target_dags = [d for d in all_dags if d.dag_id in dag_ids]
    else:
        # Default: simulate the 5 main DAGs (skip dynamic duplicates)
        priority_ids = [
            "etl_transactions_pipeline",
            "data_quality_pipeline",
            "multi_source_etl_customer_journey",
            "sensor_vendor_file_pipeline",
            "etl_sales",
        ]
        id_set = {d.dag_id for d in all_dags}
        target_ids = [pid for pid in priority_ids if pid in id_set]
        target_dags = [d for d in all_dags if d.dag_id in target_ids]
        if not target_dags:
            target_dags = all_dags[:3]

    print(f"  Running simulations for {bold(str(len(target_dags)))} DAG(s):\n")
    for d in target_dags:
        print(f"    {cyan('•')} {d.dag_id}")
    print()

    overall_results = []

    for dag_info in target_dags:
        dag_id = dag_info.dag_id
        print(bold(f"{'─' * 70}"))
        print(bold(f"  DAG: {dag_id}"))
        print(f"  Schedule: {dag_info.schedule} | Tasks: {len(dag_info.tasks)}")
        print(bold(f"{'─' * 70}"))

        t0 = time.time()
        try:
            result = sim.simulate(dag_id)
        except Exception as exc:
            print(red(f"  SIMULATION ERROR: {exc}"))
            continue

        elapsed = time.time() - t0

        # Print task trace
        for tr in result.task_results:
            status_icon = {
                "success": green("✓"),
                "failed": red("✗"),
                "skipped": yellow("→"),
                "running": blue("⟳"),
                "pending": grey("○"),
                "upstream_failed": red("↑"),
            }.get(tr.status, "?")

            duration = f"{tr.duration_ms}ms"
            xcom_count = len(tr.xcoms_pushed) if tr.xcoms_pushed else 0
            xcom_str = f" | {xcom_count} XCom(s)" if xcom_count else ""
            retry_str = f" | attempt {tr.attempt}" if tr.attempt > 1 else ""

            print(f"  {status_icon}  {tr.task_id:<45} {duration:>8}{retry_str}{xcom_str}")

            if tr.error and tr.status == "failed":
                print(f"     {red('Error:')} {tr.error[:80]}")

            if tr.xcoms_pushed:
                for k, v in tr.xcoms_pushed.items():
                    v_str = json.dumps(v, default=str)
                    if len(v_str) > 60:
                        v_str = v_str[:57] + "..."
                    print(f"     {grey('XCom:')} {k} = {v_str}")

        print()

        # Summary
        succeeded = sum(1 for t in result.task_results if t.status == "success")
        failed = sum(1 for t in result.task_results if t.status == "failed")
        skipped = sum(1 for t in result.task_results if t.status == "skipped")
        total = len(result.task_results)

        status_str = green("SUCCESS") if result.status == "success" else red("FAILED")
        print(f"  Status: {bold(status_str)}")
        print(f"  Tasks:  {green(str(succeeded))} succeeded / {red(str(failed))} failed / {yellow(str(skipped))} skipped / {total} total")
        print(f"  XComs:  {len(result.xcoms)} values stored")
        print(f"  Time:   {elapsed:.2f}s")
        print()

        overall_results.append({
            "dag_id": dag_id,
            "status": result.status,
            "tasks": total,
            "succeeded": succeeded,
            "failed": failed,
        })

    # Grand summary
    print(bold("=" * 70))
    print(bold("  SUMMARY"))
    print(bold("=" * 70))
    for r in overall_results:
        icon = green("✓") if r["status"] == "success" else red("✗")
        print(f"  {icon}  {r['dag_id']:<50} {r['succeeded']}/{r['tasks']} tasks")
    print()


# ---------------------------------------------------------------------------
# API mode
# ---------------------------------------------------------------------------

def run_api(port: int = API_PORT, reload: bool = True):
    """Start the FastAPI server."""
    print(green(f"\n  Starting FastAPI on http://localhost:{port}"))
    print(f"  Docs: http://localhost:{port}/docs\n")
    logger.info("Starting FastAPI server on %s:%d", API_HOST, port)

    try:
        import uvicorn
        uvicorn.run(
            "src.api:app",
            host=API_HOST,
            port=port,
            reload=reload,
            log_level=LOG_LEVEL.lower(),
        )
    except ImportError:
        print(red("  uvicorn not installed. Run: pip install uvicorn[standard]"))
        sys.exit(1)


# ---------------------------------------------------------------------------
# UI mode
# ---------------------------------------------------------------------------

def run_ui(port: int = UI_PORT):
    """Start the Streamlit UI."""
    print(green(f"\n  Starting Streamlit UI on http://localhost:{port}\n"))
    logger.info("Starting Streamlit UI on port %d", port)

    try:
        import streamlit.web.cli as stcli
        sys.argv = [
            "streamlit", "run", str(ROOT / "src" / "ui.py"),
            "--server.port", str(port),
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false",
        ]
        stcli.main()
    except ImportError:
        # Fallback to subprocess
        result = subprocess.run(
            [
                sys.executable, "-m", "streamlit", "run",
                str(ROOT / "src" / "ui.py"),
                "--server.port", str(port),
                "--server.address", "0.0.0.0",
                "--browser.gatherUsageStats", "false",
            ],
            cwd=str(ROOT),
        )
        if result.returncode != 0:
            print(red("  streamlit not installed. Run: pip install streamlit"))
            sys.exit(1)


# ---------------------------------------------------------------------------
# All mode (run API + UI together)
# ---------------------------------------------------------------------------

def run_all(api_port: int = API_PORT, ui_port: int = UI_PORT):
    """Start both API and UI in separate threads."""
    print(green("\n  Starting API + UI together...\n"))

    api_thread = threading.Thread(
        target=run_api,
        kwargs={"port": api_port, "reload": False},
        daemon=True,
    )
    api_thread.start()

    # Give API a moment to bind
    time.sleep(2)

    # UI runs in the main thread (Streamlit requires the main thread)
    run_ui(port=ui_port)


# ---------------------------------------------------------------------------
# List mode
# ---------------------------------------------------------------------------

def run_list():
    """Print all available DAGs."""
    try:
        from src.simulator import get_simulator
    except ImportError as e:
        print(red(f"Cannot import simulator: {e}"))
        sys.exit(1)

    sim = get_simulator()
    dags = sim.list_dags()

    print()
    print(bold(f"  {'DAG ID':<50} {'SCHEDULE':<15} {'TASKS':<8} {'OWNER'}"))
    print(f"  {'─'*50} {'─'*15} {'─'*8} {'─'*20}")

    for d in sorted(dags, key=lambda x: x.dag_id):
        print(f"  {cyan(d.dag_id):<60} {d.schedule:<15} {len(d.tasks):<8} {d.owner}")

    print()
    print(f"  Total: {bold(str(len(dags)))} DAGs")
    print()


# ---------------------------------------------------------------------------
# CLI parsing
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="POC-07: Enterprise Airflow Orchestration Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "mode",
        choices=["api", "ui", "all", "simulate", "list"],
        help="Run mode",
    )
    parser.add_argument(
        "dag_ids",
        nargs="*",
        help="DAG ID(s) to simulate (only for 'simulate' mode)",
    )
    parser.add_argument("--api-port", type=int, default=API_PORT)
    parser.add_argument("--ui-port", type=int, default=UI_PORT)

    args = parser.parse_args()

    setup_logging()
    logger.info("Starting Airflow Orchestration Platform in '%s' mode", args.mode)

    if args.mode == "simulate":
        run_simulate(dag_ids=args.dag_ids or None)

    elif args.mode == "list":
        run_list()

    elif args.mode == "api":
        run_api(port=args.api_port)

    elif args.mode == "ui":
        run_ui(port=args.ui_port)

    elif args.mode == "all":
        run_all(api_port=args.api_port, ui_port=args.ui_port)


if __name__ == "__main__":
    main()
