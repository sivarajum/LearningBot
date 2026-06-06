"""Entry point: launch the Multi-Cloud Data Lake API and/or UI."""

import logging
import subprocess
import sys
from pathlib import Path

from src.logging_config import setup_logging
from src.settings import API_HOST, API_PORT, CUSTOMERS_PER_CLOUD, TRANSACTIONS_PER_CLOUD, UI_PORT

PROJECT_ROOT = Path(__file__).parent
logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()

    mode = sys.argv[1] if len(sys.argv) > 1 else "api"

    if mode == "pipeline":
        from src.cloud_simulator import generate_cloud_data, save_cloud_data
        from src.lake_builder import build_lake

        logger.info("Generating cloud data (%d customers, %d transactions per cloud)...",
                     CUSTOMERS_PER_CLOUD, TRANSACTIONS_PER_CLOUD)
        data = generate_cloud_data(
            customers_per_cloud=CUSTOMERS_PER_CLOUD,
            transactions_per_cloud=TRANSACTIONS_PER_CLOUD,
        )
        saved = save_cloud_data(data)
        for cloud, files in saved.items():
            logger.info("  %s: %s", cloud, files)

        logger.info("Building data lake...")
        build_lake()
        logger.info("Done!")

    elif mode == "api":
        import uvicorn

        uvicorn.run("src.api:app", host=API_HOST, port=API_PORT, reload=True)

    elif mode == "ui":
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "src/ui.py",
            "--server.port", str(UI_PORT), "--server.address", "0.0.0.0",
        ], cwd=PROJECT_ROOT)

    elif mode == "all":
        api_proc = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "src.api:app",
            "--host", API_HOST, "--port", str(API_PORT),
        ], cwd=PROJECT_ROOT)
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", "src/ui.py",
                "--server.port", str(UI_PORT), "--server.address", "0.0.0.0",
            ], cwd=PROJECT_ROOT)
        finally:
            api_proc.terminate()

    else:
        logger.error("Unknown mode: %s", mode)
        logger.info("Usage: python main.py [pipeline|api|ui|all]")
        logger.info("  pipeline - Generate cloud data and build the lake")
        logger.info("  api      - Start the FastAPI server (default)")
        logger.info("  ui       - Start the Streamlit dashboard")
        logger.info("  all      - Start both API and UI")
        sys.exit(1)


if __name__ == "__main__":
    main()
