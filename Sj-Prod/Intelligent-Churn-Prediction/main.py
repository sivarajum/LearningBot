"""Entry point: train the model (if needed) then launch the API and UI."""

import logging
import subprocess
import sys
from pathlib import Path

from src.logging_config import setup_logging
from src.settings import API_HOST, API_PORT, MODEL_PATH, UI_PORT

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent


def ensure_model() -> None:
    """Run the training pipeline if no model bundle exists."""
    if MODEL_PATH.exists():
        logger.info("Model already exists at %s", MODEL_PATH)
        return
    logger.info("No model found — running training pipeline...")
    from src.pipeline import run_pipeline

    run_pipeline()


def main() -> None:
    setup_logging()
    ensure_model()

    mode = sys.argv[1] if len(sys.argv) > 1 else "api"

    if mode == "pipeline":
        from src.pipeline import run_pipeline

        run_pipeline()

    elif mode == "api":
        import uvicorn

        uvicorn.run(
            "src.api:app",
            host=API_HOST,
            port=API_PORT,
            reload=True,
        )

    elif mode == "ui":
        subprocess.run(
            [
                sys.executable, "-m", "streamlit", "run", "src/ui.py",
                "--server.port", str(UI_PORT),
                "--server.address", "0.0.0.0",
            ],
            cwd=PROJECT_ROOT,
        )

    elif mode == "all":
        # Start API in background, then launch UI
        api_proc = subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn", "src.api:app",
                "--host", API_HOST,
                "--port", str(API_PORT),
            ],
            cwd=PROJECT_ROOT,
        )
        try:
            subprocess.run(
                [
                    sys.executable, "-m", "streamlit", "run", "src/ui.py",
                    "--server.port", str(UI_PORT),
                    "--server.address", "0.0.0.0",
                ],
                cwd=PROJECT_ROOT,
            )
        finally:
            api_proc.terminate()

    else:
        logger.error("Unknown mode: %s", mode)
        logger.info("Usage: python main.py [pipeline|api|ui|all]")
        logger.info("  pipeline  - Run the training pipeline")
        logger.info("  api       - Start the FastAPI server (default)")
        logger.info("  ui        - Start the Streamlit dashboard")
        logger.info("  all       - Start both API and UI")
        sys.exit(1)


if __name__ == "__main__":
    main()
