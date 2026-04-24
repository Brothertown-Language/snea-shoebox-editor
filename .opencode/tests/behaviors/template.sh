#!/bin/bash
# Behavioral Enforcement Test Template
#
# Copy this template to create a new behavioral test.
# Replace PLACEHOLDER values with your test-specific content.
#
# Usage:
#   cp template.sh my-new-test.sh
#   Edit my-new-test.sh with your test specifics
#   bash .opencode/tests/behaviors/my-new-test.sh
#
# Behavioral tests verify that the agent ACTUALLY BEHAVES differently
# after a rule change, not just that the rule text exists in a file.
#
# Behavioral TDD cycle:
#   RED:   Write behavioral test expecting agent to follow new rule (test fails)
#   GREEN: Make guideline/skill change that causes agent to follow rule
#   REFACTOR: Verify content-verification also passes; clean up
#
# Co-authored with AI: <AgentName> (<ModelId>)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

SCENARIO_NAME="PLACEHOLDER_SCENARIO_NAME"
SCENARIO_PROMPT="PLACEHOLDER_PROMPT_MESSAGE"

echo "=== Behavioral Test: $SCENARIO_NAME ==="

behavior_run "$SCENARIO_NAME" "$SCENARIO_PROMPT"

OVERALL_RESULT=0

# Example: Verify the agent made at least 1 tool call for verification
# assert_tool_calls_made 1 "srclight_get" "github_issue_read" || OVERALL_RESULT=1

# Example: Verify a forbidden pattern is absent from agent output
# assert_forbidden_pattern_absent "(unverified)" "unverified escape hatch" || OVERALL_RESULT=1

# Example: Verify a required pattern is present in agent output
# assert_required_pattern_present "decline to answer" "decline-to-verify language" || OVERALL_RESULT=1

# Example: Verify a specific skill was invoked
# assert_skill_invoked "verification-enforcement" || OVERALL_RESULT=1

# Example: Verify a skill was NOT invoked when it shouldn't be
# assert_no_skill_invoked "some-incorrect-skill" || OVERALL_RESULT=1

echo ""
if [ "$OVERALL_RESULT" -eq 0 ]; then
    echo "PASS: $SCENARIO_NAME"
else
    echo "FAIL: $SCENARIO_NAME"
fi

exit $OVERALL_RESULT