#!/bin/bash

# Path Resolution Boilerplate
cd "$(dirname "${BASH_SOURCE[0]}")" && REPO_ROOT=$(git rev-parse --show-toplevel) && cd "$REPO_ROOT"

# Find and kill the mock viewer process
# We search for the specific streamlit command line to avoid killing other streamlit apps
echo "Stopping SNEA Mock Viewer..."
pkill -f "streamlit run tests/ui/mocks/view_mocks.py" || true

# Also ensure port 8502 is cleared
fuser -k 8502/tcp || true
