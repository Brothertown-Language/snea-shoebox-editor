#!/bin/bash
# Behavioral Test: pr-creation-task-decomposition
# Verifies that pr-creation atomic subtask routing is correct
#
# Co-authored with AI: <AgentName> (<ModelId>)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

SCENARIO_NAME="pr-creation-task-decomposition"
SCENARIO_PROMPT="What are the steps in the pr-creation task for git-workflow?"

echo "=== Behavioral Test: $SCENARIO_NAME ==="

behavior_run "$SCENARIO_NAME" "$SCENARIO_PROMPT"

OVERALL_RESULT=0

# Verify the agent references the pr-creation subtask structure
assert_required_pattern_present "pr-creation/enforcement-gate\|pr-creation/squash-push\|pr-creation/create-pr" "pr-creation subtask references" || OVERALL_RESULT=1

echo ""
if [ "$OVERALL_RESULT" -eq 0 ]; then
    echo "PASS: $SCENARIO_NAME"
else
    echo "FAIL: $SCENARIO_NAME"
fi

exit $OVERALL_RESULT