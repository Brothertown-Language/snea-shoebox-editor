#!/bin/bash
# Behavioral Test: cleanup-task-decomposition
# Verifies that cleanup atomic subtask routing is correct
#
# Co-authored with AI: <AgentName> (<ModelId>)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

SCENARIO_NAME="cleanup-task-decomposition"
SCENARIO_PROMPT="Show me the cleanup task routing for git-workflow after a PR merge"

echo "=== Behavioral Test: $SCENARIO_NAME ==="

behavior_run "$SCENARIO_NAME" "$SCENARIO_PROMPT"

OVERALL_RESULT=0

# Verify the agent references the cleanup subtask structure
assert_required_pattern_present "cleanup/verify-merge\|cleanup/issue-closure\|cleanup/branch-cleanup" "cleanup subtask references" || OVERALL_RESULT=1

echo ""
if [ "$OVERALL_RESULT" -eq 0 ]; then
    echo "PASS: $SCENARIO_NAME"
else
    echo "FAIL: $SCENARIO_NAME"
fi

exit $OVERALL_RESULT