#!/usr/bin/env bash
# validate-submodule-refs.sh — Branch-membership validation for submodule SHAs
#
# Verifies that each submodule's checked-out SHA exists on the specified branch.
# A SHA is considered "on" a branch if it is an ancestor of (or equal to) the
# branch tip — meaning the branch contains this commit in its history.
#
# Usage:
#   ./.opencode/scripts/validate-submodule-refs.sh              # Default: dev branch
#   ./.opencode/scripts/validate-submodule-refs.sh --branch main # Check main branch
#
# Exit codes:
#   0: All submodules on specified branch
#   1: One or more submodules NOT on specified branch
#   2: No submodules found or invalid worktree

set -euo pipefail

BRANCH="dev"
WORKTREE_DIR="."

detect_platform() {
    local remote_url
    remote_url=$(git config --file .gitmodules --get "submodule.$1.url" 2>/dev/null || git -C "$1" remote get-url origin 2>/dev/null)
    if [[ "$remote_url" == *"github.com"* ]]; then
        echo "github"
    elif [[ -n "$remote_url" ]]; then
        echo "gitbucket"
    else
        echo "unknown"
    fi
}

while [ $# -gt 0 ]; do
    case "$1" in
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        *)
            WORKTREE_DIR="$1"
            shift
            ;;
    esac
done

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

    SHA=$(cd "$submodule_path" && git rev-parse HEAD)
    SHORT_SHA=$(cd "$submodule_path" && git rev-parse --short HEAD)

    (cd "$submodule_path" && git fetch origin >/dev/null 2>&1 || true)

    BRANCH_REF=$(cd "$submodule_path" && git rev-parse --verify "origin/$BRANCH" 2>/dev/null || git rev-parse --verify "$BRANCH" 2>/dev/null || true)

    if [ -z "$BRANCH_REF" ]; then
        echo "  FAIL: $submodule_path @ $SHORT_SHA — branch '$BRANCH' not found" >&2
        FAILED=$((FAILED + 1))
        continue
    fi

    PLATFORM=$(detect_platform "$submodule_path")

    if (cd "$submodule_path" && git merge-base --is-ancestor "$SHA" "$BRANCH_REF" 2>/dev/null); then
        echo "  PASS: $submodule_path @ $SHORT_SHA is on $BRANCH [$PLATFORM]"
        PASSED=$((PASSED + 1))
    else
        echo "  FAIL: $submodule_path @ $SHORT_SHA is NOT on $BRANCH [$PLATFORM]"
        FAILED=$((FAILED + 1))
    fi
done < <(git config --file .gitmodules --get-regexp path | awk '{print $2}')

echo ""
echo "Results: $PASSED/$TOTAL submodules on $BRANCH"

if [ "$FAILED" -gt 0 ]; then
    echo ""
    echo "ERROR: $FAILED submodule(s) NOT on $BRANCH." >&2
    exit 1
fi

exit 0