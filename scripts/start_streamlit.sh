#!/bin/bash
# Copyright (c) 2026 Brothertown Language

# Script to start Streamlit in a persistent background process
# This ensures it continues running even after the Junie session exits.

# Ensure we are in the project root using git
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
if [ -z "$PROJECT_ROOT" ]; then
    echo "Error: Could not find project root via git."
    exit 1
fi
cd "$PROJECT_ROOT" || exit 1

LOG_FILE="tmp/streamlit.log"

echo "Project root: $PROJECT_ROOT"
echo "Stopping any existing Streamlit instances..."
pkill -f "streamlit run src/frontend/app.py" || true

echo "Starting Streamlit in the background..."
mkdir -p tmp
export PYTHONUNBUFFERED=1

# Portable way to find 'uv'
UV_CMD="uv"
if ! command -v uv &> /dev/null; then
    if [ -f "$HOME/.local/bin/uv" ]; then
        UV_CMD="$HOME/.local/bin/uv"
    else
        echo "Error: 'uv' command not found and not at $HOME/.local/bin/uv"
        exit 1
    fi
fi

nohup $UV_CMD run --extra local python -m streamlit run src/frontend/app.py --server.address 0.0.0.0 --server.port 8501 > "$LOG_FILE" 2>&1 &

PID=$!
echo "Streamlit started with PID: $PID"
echo "Logs are being written to $LOG_FILE"
