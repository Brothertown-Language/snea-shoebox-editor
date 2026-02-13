#!/bin/bash
set -e

# Mandatory Path Resolution
cd "$(dirname "${BASH_SOURCE[0]}")" && REPO_ROOT=$(git rev-parse --show-toplevel) && cd "$REPO_ROOT"

# Check if arguments are provided
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <file1> <file2> ..."
    exit 1
fi

echo "--- SECURITY INSPECTION START ---"

# 1. Check for ignored files
echo "Checking for ignored files..."
IGNORED=$(git check-ignore "$@" || true)

if [ -n "$IGNORED" ]; then
    echo "ERROR: The following files are ignored by git:"
    echo "$IGNORED"
    exit 1
fi
echo "✅ No ignored files detected."

# 2. Show current status of target files
echo "Verifying status of target files..."
git status --porcelain "$@"

echo "--- SECURITY INSPECTION COMPLETE ---"
