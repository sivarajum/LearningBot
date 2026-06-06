#!/bin/bash

# TechStack Learning Hub - Local Server Startup Script

echo "🚀 Starting TechStack Learning Hub..."
echo ""
echo "📚 Server will be available at:"
echo "   http://localhost:8000/website.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    python3 -m http.server 8000
# Fallback to Python 2
elif command -v python &> /dev/null; then
    python -m SimpleHTTPServer 8000
else
    echo "❌ Error: Python is not installed"
    echo "Please install Python or use Node.js http-server instead"
    exit 1
fi

