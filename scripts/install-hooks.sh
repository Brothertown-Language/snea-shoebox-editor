#!/bin/bash
# Install git hooks to prevent commits to main branch
#
# This script sets up pre-commit and post-commit hooks that enforce
# the branch-first workflow from AGENTS.md.
#
# Usage: ./scripts/install-hooks.sh
#
# After running:
#   git config core.hooksPath .githooks
#
# To verify:
#   git config core.hooksPath  # Should show ".githooks"

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_DIR="$PROJECT_ROOT/.githooks"

echo "Installing git hooks..."

# Create hooks directory if needed
mkdir -p "$HOOKS_DIR"

# Copy hooks
cp "$SCRIPT_DIR/../.githooks/pre-commit" "$HOOKS_DIR/pre-commit" 2>/dev/null || true
cp "$SCRIPT_DIR/../.githooks/post-commit" "$HOOKS_DIR/post-commit" 2>/dev/null || true

# Make executable
chmod +x "$HOOKS_DIR/pre-commit" "$HOOKS_DIR/post-commit"

# Configure git
cd "$PROJECT_ROOT"
git config core.hooksPath .githooks

echo ""
echo "✅ Git hooks installed successfully."
echo ""
echo "Hooks configured:"
echo "  - pre-commit: Blocks commits to main branch"
echo "  - post-commit: Warns after commits to main branch"
echo ""
echo "To verify: git config core.hooksPath"
echo "  Expected output: .githooks"