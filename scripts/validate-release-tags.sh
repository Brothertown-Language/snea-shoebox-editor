#!/usr/bin/env bash
# validate-release-tags.sh — Tag validation gate for releases
#
# Verifies that all submodules are on tagged commits before a release
# from the main worktree (worktrees/main/).
#
# Usage:
#   ./scripts/validate-release-tags.sh              # Run from worktrees/main/
#   ./scripts/validate-release-tags.sh /path/to/wt  # Specify worktree path
#
# Exit codes:
#   0: All submodules on tagged commits
#   1: One or more submodules not on tagged commits
#   2: No submodules found or invalid worktree

set -euo pipefail

WORKTREE_DIR="${1:-.}"

if [ ! -d "$WORKTREE_DIR/.git" ] && [ ! -f "$WORKTREE_DIR/.git" ]; then
    echo "ERROR: Not a git worktree: $WORKTREE_DIR" >&2
    exit 2
fi

cd "$WORKTREE_DIR"

if [ ! -f ".gitmodules" ]; then
    echo "No submodules found — validation passed trivially."
    exit 0
fi

FAILED=0
PASSED=0
TOTAL=0

while IFS= read -r submodule_path; do
    TOTAL=$((TOTAL + 1))
    if [ ! -d "$submodule_path" ]; then
        echo "WARN: Submodule path missing: $submodule_path" >&2
        FAILED=$((FAILED + 1))
        continue
    fi

    if (cd "$submodule_path" && git describe --exact-match HEAD >/dev/null 2>&1); then
        TAG=$(cd "$submodule_path" && git describe --exact-match HEAD)
        echo "  OK: $submodule_path @ $TAG"
        PASSED=$((PASSED + 1))
    else
        COMMIT=$(cd "$submodule_path" && git rev-parse --short HEAD)
        BRANCH=$(cd "$submodule_path" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
        echo "  FAIL: $submodule_path @ $COMMIT ($BRANCH) — NOT on a tagged release"
        FAILED=$((FAILED + 1))
    fi
done < <(git config --file .gitmodules --get-regexp path | awk '{print $2}')

echo ""
echo "Results: $PASSED/$TOTAL submodules on tagged releases"

if [ "$FAILED" -gt 0 ]; then
    echo ""
    echo "ERROR: $FAILED submodule(s) not on tagged commits." >&2
    echo "Tag all submodules on their main branch before releasing." >&2
    exit 1
fi

exit 0