#!/bin/bash
# Behavioral Enforcement Test Runner
#
# Discovers and executes all behavioral test scripts in .opencode/tests/behaviors/
# (excluding helpers.sh and template.sh).
#
# Usage:
#   bash .opencode/tests/behaviors/run-all.sh           # Run all behavioral tests
#   bash .opencode/tests/behaviors/run-all.sh --list    # List discovered tests
#   bash .opencode/tests/behaviors/run-all.sh --dry-run # Show what would run without executing
#
# Exit code 0 only if ALL tests pass.
#
# Co-authored with AI: <AgentName> (<ModelId>)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXCLUDE_FILES=("helpers.sh" "template.sh" "run-all.sh")

LIST_ONLY=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --list)
            LIST_ONLY=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: bash .opencode/tests/behaviors/run-all.sh [--list] [--dry-run]" >&2
            exit 1
            ;;
    esac
done

is_excluded() {
    local filename="$1"
    for excluded in "${EXCLUDE_FILES[@]}"; do
        if [ "$filename" = "$excluded" ]; then
            return 0
        fi
    done
    return 1
}

TEST_FILES=()
if [ -d "$SCRIPT_DIR" ]; then
    for file in "$SCRIPT_DIR"/*.sh; do
        [ -f "$file" ] || continue
        filename="$(basename "$file")"
        is_excluded "$filename" && continue
        TEST_FILES+=("$file")
    done
fi

TEST_FILES=($(for f in "${TEST_FILES[@]}"; do echo "$f"; done | sort))

if [ "$LIST_ONLY" = true ]; then
    echo "Discovered behavioral test scripts:"
    for file in "${TEST_FILES[@]}"; do
        echo "  $(basename "$file")"
    done
    echo ""
    echo "Total: ${#TEST_FILES[@]} test(s)"
    exit 0
fi

if [ "$DRY_RUN" = true ]; then
    echo "=== Behavioral Enforcement Test Runner (dry-run) ==="
    echo ""
    echo "Would run ${#TEST_FILES[@]} behavioral test(s):"
    for file in "${TEST_FILES[@]}"; do
        echo "  $(basename "$file")"
    done
    exit 0
fi

echo "=== Behavioral Enforcement Tests ==="
echo "Running ${#TEST_FILES[@]} test(s)..."
echo ""

OVERALL_RESULT=0
PASS_COUNT=0
FAIL_COUNT=0

for test_file in "${TEST_FILES[@]}"; do
    test_name="$(basename "$test_file")"
    echo "--- Running: $test_name ---"
    if bash "$test_file"; then
        PASS_COUNT=$((PASS_COUNT + 1))
        echo "  PASSED: $test_name"
    else
        OVERALL_RESULT=1
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo "  FAILED: $test_name"
    fi
    echo ""
done

echo "=== Results ==="
echo "Passed: $PASS_COUNT"
echo "Failed: $FAIL_COUNT"
echo "Total:  ${#TEST_FILES[@]}"
echo ""

if [ "$OVERALL_RESULT" -eq 0 ]; then
    echo "ALL TESTS PASSED"
else
    echo "SOME TESTS FAILED"
fi

exit $OVERALL_RESULT