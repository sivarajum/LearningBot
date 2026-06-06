#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
VIEWER="$ROOT/learning-viewer"

# Install deps if missing
if [ ! -d "$VIEWER/node_modules" ]; then
  echo "Installing dependencies..."
  npm --prefix "$VIEWER" install
fi

echo "Starting LearningBot Explorer at http://localhost:3000"
npm --prefix "$VIEWER" run dev
