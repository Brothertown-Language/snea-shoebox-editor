#!/bin/bash

# Path Resolution Boilerplate
cd "$(dirname "${BASH_SOURCE[0]}")" && REPO_ROOT=$(git rev-parse --show-toplevel) && cd "$REPO_ROOT"

LOG_FILE="tmp/mock_viewer.log"

echo "Stopping any existing Mock Viewer instances..."
pkill -f "streamlit run tests/ui/mocks/view_mocks.py" || true

# Also kill anything on port 8502 to be safe
fuser -k 8502/tcp || true

echo "Starting SNEA Mock Viewer in the background..."
mkdir -p tmp
export PYTHONUNBUFFERED=1

# Run the mock viewer in background
# PYTHONPATH=. is required so mocks can import from src/
nohup bash -c "PYTHONPATH=. uv run streamlit run tests/ui/mocks/view_mocks.py --server.port 8502" > "$LOG_FILE" 2>&1 &

PID=$!
echo "Mock Viewer started with PID: $PID"
echo "Logs are being written to $LOG_FILE"
