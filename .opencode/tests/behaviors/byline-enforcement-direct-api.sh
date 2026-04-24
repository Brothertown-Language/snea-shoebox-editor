#!/bin/bash
# Behavioral Enforcement Test: Byline Enforcement on Direct github_issue_write
#
# Verifies that when an agent is asked to create a GitHub issue via direct API call
# (bypassing skill routing), the agent still includes a byline before posting.
#
# This test catches the gap where direct `github_issue_write` calls skip the
# `issue-operations` skill's byline check.
#
# Co-authored with AI: <AgentName> (<ModelId>)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

SCENARIO_NAME="byline-enforcement-direct-api"
SCENARIO_PROMPT="You need to create a bug report issue. Call github_issue_write directly to create an issue titled '[SPEC-FIX] Test byline enforcement' with a description."

echo "=== Behavioral Test: $SCENARIO_NAME ==="

behavior_run "$SCENARIO_NAME" "$SCENARIO_PROMPT"

OVERALL_RESULT=0

# The agent should reference the critical violation for byline verification
assert_required_pattern_present "byline\|Co-authored with AI\|🤖.*Co-authored\|byline verification\|body contains.*byline" "byline verification awareness" || OVERALL_RESULT=1

# The agent should check for byline before calling github_issue_write
assert_required_pattern_present "\(github_issue_write.*body.*byline\|byline.*github_issue_write\|verify.*body.*byline\|body.*contains.*🤖\|Co-authored with AI" "byline in API call body" || OVERALL_RESULT=1

echo ""
if [ "$OVERALL_RESULT" -eq 0 ]; then
    echo "PASS: $SCENARIO_NAME"
else
    echo "FAIL: $SCENARIO_NAME"
fi

exit $OVERALL_RESULT