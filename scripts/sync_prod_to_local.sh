#!/bin/bash
# Copyright (c) 2026 Brothertown Language

cd "$(dirname "${BASH_SOURCE[0]}")" && REPO_ROOT=$(git rev-parse --show-toplevel) && cd "$REPO_ROOT"

echo "Starting Production to Local Sync..."
PYTHONPATH=. uv run python scripts/sync_prod_to_local.py
