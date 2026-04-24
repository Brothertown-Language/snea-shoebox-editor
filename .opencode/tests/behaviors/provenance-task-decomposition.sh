#!/bin/bash
# Behavioral Test: provenance-task-decomposition
# Verifies that provenance atomic subtask routing is correct
#
# Co-authored with AI: <AgentName> (<ModelId>)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

SCENARIO_NAME="provenance-task-decomposition"
SCENARIO_PROMPT="How does the provenance task route to subtasks for submodule tracking?"

echo "=== Behavioral Test: $SCENARIO_NAME ==="

behavior_run "$SCENARIO_NAME" "$SCENARIO_PROMPT"

OVERALL_RESULT=0

assert_required_pattern_present "provenance/platform-detection\|provenance/dev-push-provenance\|provenance/promotion-provenance" "provenance subtask references" || OVERALL_RESULT=1

echo ""
if [ "$OVERALL_RESULT" -eq 0 ]; then
    echo "PASS: $SCENARIO_NAME"
else
    echo "FAIL: $SCENARIO_NAME"
fi

exit $OVERALL_RESULT