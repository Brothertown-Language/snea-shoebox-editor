#!/bin/bash

# Path Resolution Boilerplate
cd "$(dirname "${BASH_SOURCE[0]}")" && REPO_ROOT=$(git rev-parse --show-toplevel) && cd "$REPO_ROOT"

# Run the mock viewer
# PYTHONPATH=. is required so mocks can import from src/
echo "Starting SNEA Mock Viewer..."
PYTHONPATH=. uv run streamlit run tests/ui/mocks/view_mocks.py
