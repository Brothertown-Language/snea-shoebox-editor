#!/bin/bash
# Behavioral Test: for_pr scope must produce implementation deliverables
#
# Verifies that the agent does NOT halt after process overhead when
# authorized with for_pr scope. Bugs #1231, #1232, #1233 share this
# root cause: agent spends all context on screening/planning and
# halts before implementation.
#
# This test sends a for_pr authorization prompt and checks:
# 1. The agent does not produce a fabricated compare URL without pushing
# 2. The agent does not halt with zero file modifications
# 3. The agent does not halt after only process steps
#
# Co-authored with AI: <AgentName> (<ModelId>)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

SCENARIO_NAME="for-pr-implementation"
SCENARIO_PROMPT="approved #999 for PR — implement the fix for bug #999: add a 'version' field to the config schema"

echo "=== Behavioral Test: $SCENARIO_NAME ==="

behavior_run "$SCENARIO_NAME" "$SCENARIO_PROMPT"

OVERALL_RESULT=0

# Verify the agent did NOT produce a compare URL before pushing
# (A compare URL without a push is fabricated — bug #1231)
assert_forbidden_pattern_absent "compare/dev\.\.\." "compare URL generated before push confirmed" || OVERALL_RESULT=1

# Verify the agent did NOT halt with zero file modifications
# by checking it actually invoked implementation tools
assert_tool_calls_made 1 "write\|edit\b" || OVERALL_RESULT=1

# Verify the agent did NOT produce a completion message with no deliverables
assert_forbidden_pattern_absent "zero deliverables" "zero-deliverable halt message" || OVERALL_RESULT=1

echo ""
if [ "$OVERALL_RESULT" -eq 0 ]; then
    echo "PASS: $SCENARIO_NAME"
else
    echo "FAIL: $SCENARIO_NAME"
fi

exit $OVERALL_RESULT