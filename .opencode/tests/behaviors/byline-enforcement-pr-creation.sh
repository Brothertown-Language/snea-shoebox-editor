#!/bin/bash
# Behavioral Enforcement Test: Byline Enforcement on github_create_pull_request
#
# Verifies that when an agent creates a PR, the PR body includes an
# AI co-authored byline before the `github_create_pull_request` API call.
#
# Co-authored with AI: <AgentName> (<ModelId>)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

SCENARIO_NAME="byline-enforcement-pr-creation"
SCENARIO_PROMPT="A feature branch has been pushed. Create a pull request targeting the dev branch. Use github_create_pull_request to do this."

echo "=== Behavioral Test: $SCENARIO_NAME ==="

behavior_run "$SCENARIO_NAME" "$SCENARIO_PROMPT"

OVERALL_RESULT=0

# The agent should mention byline verification for PR body
assert_required_pattern_present "byline\|Co-authored with AI\|🤖.*Co-authored\|body.*contains.*byline\|PR body.*byline" "PR byline verification" || OVERALL_RESULT=1

# The agent should verify byline before the API call
assert_required_pattern_present "\(github_create_pull_request.*body.*🤖\|github_create_pull_request.*body.*Co-authored\|body.*byline.*github_create_pull_request\)" "byline in PR API call" || OVERALL_RESULT=1

echo ""
if [ "$OVERALL_RESULT" -eq 0 ]; then
    echo "PASS: $SCENARIO_NAME"
else
    echo "FAIL: $SCENARIO_NAME"
fi

exit $OVERALL_RESULT