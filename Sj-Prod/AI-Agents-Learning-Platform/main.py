"""Entry point: launch the AI Agents Learning Platform API and/or UI."""

import subprocess
import sys
from pathlib import Path

from src.logging_config import setup_logging
from src.settings import API_HOST, API_PORT, UI_PORT

PROJECT_ROOT = Path(__file__).parent


def main():
    setup_logging()

    mode = sys.argv[1] if len(sys.argv) > 1 else "api"

    if mode == "api":
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
        print("Usage: python main.py [api|ui|all]")
        print("  api  - Start the FastAPI server (default)")
        print("  ui   - Start the Streamlit dashboard")
        print("  all  - Start both API and UI")
        sys.exit(1)


if __name__ == "__main__":
    main()
