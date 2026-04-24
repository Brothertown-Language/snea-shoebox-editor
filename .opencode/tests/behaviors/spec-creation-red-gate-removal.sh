#!/bin/bash
# Behavioral Enforcement Test: Spec Creation RED Gate Removal
#
# Verifies that spec-creation/tasks/write.md does NOT have the old Step 0.5
# RED gate, and instead includes behavioral test mandate language for
# Success Criteria.
#
# Co-authored with AI: OpenCode (ollama-cloud/glm-5)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

# helpers.sh computes PROJECT_DIR from the main repo. For worktree tests,
# we need the worktree root (three levels up from behaviors/).
WORKTREE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

SCENARIO_NAME="spec-creation-red-gate-removal"
SCENARIO_PROMPT="The spec-creation write task must no longer contain the Step 0.5 RED gate. Instead it must mandate behavioral test inclusion in Success Criteria."

echo "=== Behavioral Test: $SCENARIO_NAME ==="

WRITE_FILE=".opencode/skills/spec-creation/tasks/write.md"
WORKTREE_FILE="$WORKTREE_ROOT/$WRITE_FILE"

if [ ! -f "$WORKTREE_FILE" ]; then
    echo "FAIL: $SCENARIO_NAME — $WRITE_FILE not found"
    exit 1
fi

OVERALL_RESULT=0

# Verify 1: Step 0.5 RED Gate heading is ABSENT
if grep -q '### Step 0\.5.*RED Gate' "$WORKTREE_FILE"; then
    echo "FAIL: $SCENARIO_NAME — forbidden Step 0.5 RED Gate heading still present in write.md"
    OVERALL_RESULT=1
else
    echo "PASS: $SCENARIO_NAME — Step 0.5 RED Gate heading is absent"
fi

# Verify 2: Step 0.5 Behavioral Test Mandate heading is PRESENT
if ! grep -q '### Step 0\.5.*Behavioral Test Mandate' "$WORKTREE_FILE"; then
    echo "FAIL: $SCENARIO_NAME — required Step 0.5 Behavioral Test Mandate heading missing"
    OVERALL_RESULT=1
else
    echo "PASS: $SCENARIO_NAME — Step 0.5 Behavioral Test Mandate heading present"
fi

# Verify 3: Behavioral test mandate language for Success Criteria exists
if ! grep -qi 'behavioral enforcement tests' "$WORKTREE_FILE"; then
    echo "FAIL: $SCENARIO_NAME — behavioral enforcement test mandate language missing"
    OVERALL_RESULT=1
else
    echo "PASS: $SCENARIO_NAME — behavioral enforcement test mandate language present"
fi

# Verify 4: RED state (test fails before change) language exists in SC context
if ! grep -qi 'RED state' "$WORKTREE_FILE"; then
    echo "FAIL: $SCENARIO_NAME — RED state language missing in Success Criteria section"
    OVERALL_RESULT=1
else
    echo "PASS: $SCENARIO_NAME — RED state language present in Success Criteria section"
fi

echo ""
if [ "$OVERALL_RESULT" -eq 0 ]; then
    echo "PASS: $SCENARIO_NAME"
else
    echo "FAIL: $SCENARIO_NAME"
fi

exit $OVERALL_RESULT
