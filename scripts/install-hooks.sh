#!/bin/bash
# Install git hooks for branch protection
# Usage: ./scripts/install-hooks.sh

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
HOOKS_SRC="$REPO_ROOT/.githooks"

if [ ! -d "$HOOKS_SRC" ]; then
    echo "ERROR: .githooks directory not found at $HOOKS_SRC"
    echo "Please ensure the .githooks directory exists with hook scripts."
    exit 1
fi

echo "Installing git hooks from .githooks/..."

# Configure git to use .githooks directory
git config core.hooksPath .githooks

# Set executable permissions on hook scripts
chmod +x "$HOOKS_SRC/pre-commit"
chmod +x "$HOOKS_SRC/post-commit"

echo ""
echo "✅ Git hooks installed successfully!"
echo ""
echo "Protected branches:"
echo "  - main (production)"
echo "  - dev (integration)"
echo ""
echo "Hooks installed:"
echo "  - pre-commit: Blocks commits to protected branches"
echo "  - post-commit: Warns if commit made to protected branch"
echo ""
echo "To verify installation:"
echo "  git config core.hooksPath  (should output: .githooks)"
echo ""