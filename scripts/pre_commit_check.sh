#!/bin/bash
set -e

# Mandatory Path Resolution
cd "$(dirname "${BASH_SOURCE[0]}")" && REPO_ROOT=$(git rev-parse --show-toplevel) && cd "$REPO_ROOT"

# Check if arguments are provided
if [ "$#" -eq 0 ]; then
    if [ -f "tmp/commit_files.txt" ]; then
        echo "Reading target files from tmp/commit_files.txt..."
        TARGET_FILES=()
        while IFS= read -r line || [[ -n "$line" ]]; do
            TARGET_FILES+=("$line")
        done < tmp/commit_files.txt
        set -- "${TARGET_FILES[@]}"
    else
        echo "Usage: $0 <file1> <file2> ... OR ensure tmp/commit_files.txt exists."
        exit 1
    fi
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

# 3. Check for any other uncommitted changes in the repository
echo "Checking for OTHER uncommitted changes in the repository..."
git status --porcelain

echo "--- SECURITY INSPECTION COMPLETE ---"
