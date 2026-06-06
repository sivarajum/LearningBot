@echo off
REM TechStack Learning Hub - Local Server Startup Script (Windows)

echo Starting TechStack Learning Hub...
echo.
echo Server will be available at:
echo    http://localhost:8000/website.html
echo.
echo Press Ctrl+C to stop the server
echo.

REM Check if Python 3 is available
python -m http.server 8000 2>nul
if errorlevel 1 (
    python -m SimpleHTTPServer 8000
)

