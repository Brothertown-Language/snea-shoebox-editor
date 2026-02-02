#!/bin/bash
# Copyright (c) 2026 Brothertown Language

# Exit on error
set -e

echo "Starting Cloudflare Build Process..."

# 1. Install uv
echo "Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Add uv to PATH
# The installer typically puts it in $HOME/.local/bin
export PATH="$HOME/.local/bin:$PATH"

# Verify uv installation
if ! command -v uv &> /dev/null; then
    echo "Error: uv could not be found in PATH"
    exit 1
fi

echo "uv version: $(uv --version)"

# 3. Sync dependencies
echo "Syncing dependencies with uv..."
uv sync --all-groups

# 4. Run Stlite bundling script
echo "Bundling frontend with Stlite..."
uv run python3 scripts/bundle_stlite.py

echo "Build complete."
