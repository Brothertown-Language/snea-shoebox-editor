#!/usr/bin/env bash
# validate-release-tags.sh — Tag validation gate for releases
#
# Verifies that all submodules are on tagged commits before a release.
# Optional: --semver for semantic version enforcement (monotonic increase)
# Optional: --branch <name> for branch-membership check
#
# Usage:
#   ./.opencode/scripts/validate-release-tags.sh                          # Default: tag check only
#   ./.opencode/scripts/validate-release-tags.sh --semver                 # Tag + semver check
#   ./.opencode/scripts/validate-release-tags.sh --branch dev             # Tag + branch-membership check
#   ./.opencode/scripts/validate-release-tags.sh --semver --branch dev    # All checks
#   ./.opencode/scripts/validate-release-tags.sh /path/to/wt              # Specify worktree path
#
# Exit codes:
#   0: All submodules on tagged commits (and semver/branch checks pass)
#   1: One or more submodules not on tagged commits (or semver/branch checks fail)
#   2: No submodules found or invalid worktree

set -euo pipefail

DO_SEMVER=0
CHECK_BRANCH=""
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

verify_tag_platform() {
    local platform="$1"
    local owner_repo="$2"
    local tag="$3"
    case "$platform" in
        github)
            gh release view "$tag" --repo "$owner_repo" >/dev/null 2>&1
            ;;
        gitbucket)
            local gitbucket_url
            gitbucket_url=$(git -C . config --get remote.origin.url | sed 's|/[^/]*$||')
            curl -sf "$gitbucket_url/api/v3/repos/$owner_repo/git/refs/tags/$tag" >/dev/null 2>&1
            ;;
        *)
            echo "ERROR: Unknown platform for $owner_repo. Supported: github, gitbucket" >&2
            return 1
            ;;
    esac
}

while [ $# -gt 0 ]; do
    case "$1" in
        --semver)
            DO_SEMVER=1
            shift
            ;;
        --branch)
            CHECK_BRANCH="$2"
            shift 2
            ;;
        *)
            WORKTREE_DIR="$1"
            shift
            ;;
    esac
done

normalize_version() {
    local ver="$1"
    ver="${ver#v}"
    echo "$ver"
}

compare_versions() {
    local v1="$1"
    local v2="$2"
    v1="$(normalize_version "$v1")"
    v2="$(normalize_version "$v2")"
    local i1 i2
    i1="$(echo "$v1" | cut -d. -f1)"
    i2="$(echo "$v2" | cut -d. -f1)"
    if [ "$i1" -gt "$i2" ]; then echo "gt"; return; fi
    if [ "$i1" -lt "$i2" ]; then echo "lt"; return; fi
    local m1 m2
    m1="$(echo "$v1" | cut -d. -f2)"
    m2="$(echo "$v2" | cut -d. -f2)"
    if [ "$m1" -gt "$m2" ]; then echo "gt"; return; fi
    if [ "$m1" -lt "$m2" ]; then echo "lt"; return; fi
    local p1 p2
    p1="$(echo "$v1" | cut -d. -f3)"
    p2="$(echo "$v2" | cut -d. -f3)"
    if [ "$p1" -gt "$p2" ]; then echo "gt"; return; fi
    if [ "$p1" -lt "$p2" ]; then echo "lt"; return; fi
    echo "eq"
}

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

declare -A PREVIOUS_TAGS

while IFS= read -r submodule_path; do
    TOTAL=$((TOTAL + 1))
    if [ ! -d "$submodule_path" ]; then
        echo "WARN: Submodule path missing: $submodule_path" >&2
        FAILED=$((FAILED + 1))
        continue
    fi

    PLATFORM=$(detect_platform "$submodule_path")

    if (cd "$submodule_path" && git describe --exact-match HEAD >/dev/null 2>&1); then
        TAG=$(cd "$submodule_path" && git describe --exact-match HEAD)
        PLATFORM_STATUS=""

        if [[ "$PLATFORM" != "unknown" ]]; then
            OWNER_REPO=$(cd "$submodule_path" && git remote get-url origin 2>/dev/null | sed -E 's|.*[:/]([^/]+/[^/]+)(\.git)?$|\1|')
            if [[ -n "$OWNER_REPO" ]]; then
                if verify_tag_platform "$PLATFORM" "$OWNER_REPO" "$TAG" 2>/dev/null; then
                    PLATFORM_STATUS=" [verified on $PLATFORM]"
                else
                    PLATFORM_STATUS=" [WARN: tag not found on $PLATFORM remote]"
                    echo "  WARN: $submodule_path @ $TAG — tag not verified on $PLATFORM remote" >&2
                fi
            fi
        fi

        echo "  OK: $submodule_path @ $TAG$PLATFORM_STATUS"
        PASSED=$((PASSED + 1))

        if [ "$DO_SEMVER" -eq 1 ]; then
            NORMALIZED="$(normalize_version "$TAG")"
            if ! echo "$NORMALIZED" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+'; then
                echo "  WARN: $submodule_path @ $TAG — non-semver tag format (allowed with warning)" >&2
            fi

            if [ -n "${PREVIOUS_TAGS[$submodule_path]+x}" ]; then
                PREV_TAG="${PREVIOUS_TAGS[$submodule_path]}"
                CMP="$(compare_versions "$TAG" "$PREV_TAG")"
                if [ "$CMP" = "lt" ]; then
                    echo "  FAIL: $submodule_path @ $TAG — downgrade from $PREV_TAG detected (blocked)" >&2
                    FAILED=$((FAILED + 1))
                    PASSED=$((PASSED - 1))
                fi
            fi

            PREVIOUS_TAGS["$submodule_path"]="$TAG"
        fi

        if [ -n "$CHECK_BRANCH" ]; then
            SHA=$(cd "$submodule_path" && git rev-parse HEAD)
            (cd "$submodule_path" && git fetch origin >/dev/null 2>&1 || true)
            BRANCH_REF=$(cd "$submodule_path" && git rev-parse --verify "origin/$CHECK_BRANCH" 2>/dev/null || git rev-parse --verify "$CHECK_BRANCH" 2>/dev/null || true)
            if [ -z "$BRANCH_REF" ]; then
                echo "  FAIL: $submodule_path — branch '$CHECK_BRANCH' not found" >&2
                FAILED=$((FAILED + 1))
                PASSED=$((PASSED - 1))
            elif ! (cd "$submodule_path" && git merge-base --is-ancestor "$SHA" "$BRANCH_REF" 2>/dev/null); then
                SHORT_SHA=$(cd "$submodule_path" && git rev-parse --short HEAD)
                echo "  FAIL: $submodule_path @ $SHORT_SHA is NOT on $CHECK_BRANCH" >&2
                FAILED=$((FAILED + 1))
                PASSED=$((PASSED - 1))
            fi
        fi
    else
        COMMIT=$(cd "$submodule_path" && git rev-parse --short HEAD)
        BRANCH=$(cd "$submodule_path" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
        echo "  FAIL: $submodule_path @ $COMMIT ($BRANCH) — NOT on a tagged release"
        FAILED=$((FAILED + 1))
    fi
done < <(git config --file .gitmodules --get-regexp path | awk '{print $2}')

echo ""
echo "Results: $PASSED/$TOTAL submodules on tagged releases"

if [ "$DO_SEMVER" -eq 1 ]; then
    echo "  (semver monotonic check enabled)"
fi
if [ -n "$CHECK_BRANCH" ]; then
    echo "  (branch-membership check: $CHECK_BRANCH)"
fi

if [ "$FAILED" -gt 0 ]; then
    echo ""
    echo "ERROR: $FAILED submodule(s) not on tagged commits." >&2
    echo "Tag all submodules on their main branch before releasing." >&2
    exit 1
fi

exit 0