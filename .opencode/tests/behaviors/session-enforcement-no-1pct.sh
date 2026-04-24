#!/bin/bash
# Behavioral Enforcement Test: Session Enforcement No 1% Rule
#
# Verifies that session-enforcement.ts does NOT contain the old "1% Rule"
# or "1% chance" heuristic, and instead contains "Deterministic Dispatch".
#
# Co-authored with AI: OpenCode (ollama-cloud/glm-5)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

# helpers.sh computes PROJECT_DIR from the main repo. For worktree tests,
# we need the worktree root (three levels up from behaviors/).
WORKTREE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

SCENARIO_NAME="session-enforcement-no-1pct"
SCENARIO_PROMPT="The session-enforcement.ts plugin output must not reference '1% Rule' or '1% chance'. It must use 'Deterministic Dispatch' instead."

echo "=== Behavioral Test: $SCENARIO_NAME ==="

SESSION_FILE=".opencode/plugins/session-enforcement.ts"
WORKTREE_FILE="$WORKTREE_ROOT/$SESSION_FILE"

if [ ! -f "$WORKTREE_FILE" ]; then
    echo "FAIL: $SCENARIO_NAME — $SESSION_FILE not found"
    exit 1
fi

OVERALL_RESULT=0

# Verify 1: "1% Rule" is ABSENT from the file
if grep -qi '1% Rule' "$WORKTREE_FILE"; then
    echo "FAIL: $SCENARIO_NAME — forbidden pattern '1% Rule' found in session-enforcement.ts"
    OVERALL_RESULT=1
else
    echo "PASS: $SCENARIO_NAME — '1% Rule' is absent from session-enforcement.ts"
fi

# Verify 2: "1% chance" is ABSENT from the file
if grep -qi '1% chance' "$WORKTREE_FILE"; then
    echo "FAIL: $SCENARIO_NAME — forbidden pattern '1% chance' found in session-enforcement.ts"
    OVERALL_RESULT=1
else
    echo "PASS: $SCENARIO_NAME — '1% chance' is absent from session-enforcement.ts"
fi

# Verify 3: "Deterministic Dispatch" is PRESENT in the file
if ! grep -qi 'Deterministic Dispatch' "$WORKTREE_FILE"; then
    echo "FAIL: $SCENARIO_NAME — required pattern 'Deterministic Dispatch' missing from session-enforcement.ts"
    OVERALL_RESULT=1
else
    echo "PASS: $SCENARIO_NAME — 'Deterministic Dispatch' is present in session-enforcement.ts"
fi

echo ""
if [ "$OVERALL_RESULT" -eq 0 ]; then
    echo "PASS: $SCENARIO_NAME"
else
    echo "FAIL: $SCENARIO_NAME"
fi

exit $OVERALL_RESULT
