"""
main.py — Unified entry point for POC-08: Medallion Architecture with dbt + DuckDB.

Usage:
    python main.py pipeline   — generate data + run dbt bronze/silver/gold + tests
    python main.py api        — start FastAPI server (port 8000)
    python main.py ui         — start Streamlit dashboard (port 8501)
    python main.py all        — pipeline + api + ui (runs pipeline first, then api+ui in background)
    python main.py generate   — only generate synthetic CSV data
    python main.py stats      — print layer stats from DuckDB
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure src is importable before any src.* imports
# ---------------------------------------------------------------------------

ROOT = Path(__file__).parent.resolve()
SRC = ROOT / "src"

if str(SRC.parent) not in sys.path:
    sys.path.insert(0, str(SRC.parent))

# ---------------------------------------------------------------------------
# Logging — use centralized setup
# ---------------------------------------------------------------------------

from src.logging_config import setup_logging  # noqa: E402
from src.settings import API_HOST, API_PORT, DUCKDB_PATH, RAW_DATA_PATH, UI_PORT  # noqa: E402

setup_logging()
logger = logging.getLogger("main")


# ---------------------------------------------------------------------------
# Mode handlers
# ---------------------------------------------------------------------------


def mode_generate() -> None:
    """Generate synthetic CSV data only."""
    logger.info("Generating synthetic CSV data...")
    from src.data_generator import generate_all  # noqa: PLC0415

    paths = generate_all(ROOT / "data" / "raw")
    for name, path in paths.items():
        logger.info("  %s → %s (%d rows)", name, path, _count_csv(path))


def mode_pipeline() -> None:
    """Run the full Medallion pipeline: data → dbt bronze/silver/gold → tests."""
    from src.pipeline import MedallionPipeline  # noqa: PLC0415

    pipeline = MedallionPipeline(ROOT)
    result = pipeline.run_full_pipeline()

    summary_lines = [
        "",
        "=" * 70,
        f"  Pipeline {'SUCCEEDED' if result.success else 'FAILED'}",
        f"  Duration : {result.duration_seconds:.1f}s",
        f"  Started  : {result.started_at}",
        "=" * 70,
    ]
    for layer, stats in result.layer_stats.items():
        summary_lines.append(f"\n  {layer.upper()} layer:")
        for model, count in stats.row_counts.items():
            status = f"{count:>6,} rows" if count >= 0 else " not yet materialised"
            summary_lines.append(f"    {model:<45} {status}")

    if result.errors:
        summary_lines.append("\n  ERRORS:")
        for err in result.errors:
            summary_lines.append(f"    {err}")

    logger.info("\n".join(summary_lines))
    sys.exit(0 if result.success else 1)


def mode_api() -> None:
    """Start the FastAPI server."""
    logger.info("Starting FastAPI server on http://%s:%s", API_HOST, API_PORT)
    logger.info("API docs: http://localhost:%s/docs", API_PORT)
    _set_env()
    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "src.api:app",
            "--host",
            API_HOST,
            "--port",
            str(API_PORT),
            "--reload",
            "--log-level",
            "info",
        ],
        cwd=str(ROOT),
        check=False,
    )


def mode_ui() -> None:
    """Start the Streamlit UI."""
    logger.info("Starting Streamlit dashboard on http://localhost:%s", UI_PORT)
    _set_env()
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(ROOT / "src" / "ui.py"),
            "--server.port",
            str(UI_PORT),
            "--server.headless",
            "true",
        ],
        cwd=str(ROOT),
        check=False,
    )


def mode_stats() -> None:
    """Log layer stats from DuckDB (requires pipeline to have been run)."""
    from src.pipeline import MedallionPipeline  # noqa: PLC0415

    pipeline = MedallionPipeline(ROOT)
    lines = ["\nMedallion Architecture -- Layer Stats", "=" * 50]
    for layer in ["bronze", "silver", "gold"]:
        stats = pipeline.get_layer_stats(layer)
        lines.append(f"\n{layer.upper()} ({stats.total_rows:,} total rows)")
        for model, count in stats.row_counts.items():
            if count >= 0:
                lines.append(f"  {model:<45} {count:>6,} rows")
            else:
                lines.append(f"  {model:<45}  not materialised")
    logger.info("\n".join(lines))


def mode_all() -> None:
    """Run pipeline then launch api + ui concurrently."""
    import threading  # noqa: PLC0415

    # Step 1: pipeline (blocking)
    logger.info("Step 1/3 — Running full pipeline...")
    mode_pipeline_no_exit()

    # Step 2: api in background thread
    logger.info("Step 2/3 — Starting API server in background...")
    api_thread = threading.Thread(target=mode_api, daemon=True)
    api_thread.start()

    import time  # noqa: PLC0415

    time.sleep(2)  # give API a moment to start

    # Step 3: ui (blocking, foreground)
    logger.info("Step 3/3 — Starting Streamlit UI...")
    mode_ui()


def mode_pipeline_no_exit() -> None:
    """Like mode_pipeline but does not call sys.exit."""
    from src.pipeline import MedallionPipeline  # noqa: PLC0415

    pipeline = MedallionPipeline(ROOT)
    result = pipeline.run_full_pipeline()
    logger.info(
        "Pipeline %s in %.1fs",
        "SUCCEEDED" if result.success else "FAILED",
        result.duration_seconds,
    )
    if not result.success:
        logger.error("Pipeline errors: %s", result.errors)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _set_env() -> None:
    """Set env vars required by dbt and the API, using centralized settings."""
    os.environ.setdefault("RAW_DATA_PATH", RAW_DATA_PATH)
    os.environ.setdefault("DUCKDB_PATH", DUCKDB_PATH)


def _count_csv(path: Path) -> int:
    """Count data rows (excluding header) in a CSV file."""
    try:
        with open(path) as f:
            return sum(1 for _ in f) - 1
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not count rows in %s: %s", path, exc)
        return -1


def _print_usage() -> None:
    logger.info(__doc__)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _set_env()

    if len(sys.argv) < 2:
        _print_usage()
        sys.exit(0)

    mode = sys.argv[1].lower()

    dispatch = {
        "generate": mode_generate,
        "pipeline": mode_pipeline,
        "api": mode_api,
        "ui": mode_ui,
        "stats": mode_stats,
        "all": mode_all,
    }

    if mode not in dispatch:
        logger.error("Unknown mode: %r", mode)
        _print_usage()
        sys.exit(1)

    dispatch[mode]()
