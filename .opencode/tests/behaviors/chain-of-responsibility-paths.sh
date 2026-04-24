#!/bin/bash
# Behavioral Enforcement Test: Chain-of-Responsibility Path Routing
#
# Verifies that the AI agent actually routes through the
# chain-of-responsibility paths defined in approval-gate/SKILL.md.
#
# When given a simple single-issue approval, the agent should demonstrate
# awareness of scope-based dispatch path selection (fast-path vs medium-path
# vs full-path) rather than treating all approvals identically.
#
# Co-authored with AI: <AgentName> (<ModelId>)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

SCENARIO_NAME="chain-of-responsibility-paths"
SCENARIO_PROMPT="I want to implement issue #5. It's a single issue with no sub-issues. The spec is already approved. How should the approval-gate dispatch chain route this? What path does it take?"

echo "=== Behavioral Test: $SCENARIO_NAME ==="

behavior_run "$SCENARIO_NAME" "$SCENARIO_PROMPT"

OVERALL_RESULT=0

# The agent should reference scope auto-resolve or scope parsing
assert_required_pattern_present "scope.*auto.*resolve\|scope-auto-resolve\|scope.*parsing\|authorization.*scope\|scope resolve\|path.*routing" "scope-based dispatch path awareness" || OVERALL_RESULT=1

# The agent should reference the chain-of-responsibility dispatch concept
assert_required_pattern_present "fast-path\|medium-path\|full-path\|chain.of.responsibility\|dispatch.*path\|routing.*path\|path.*selection\|path.*criteria" "chain-of-responsibility path reference" || OVERALL_RESULT=1

echo ""
if [ "$OVERALL_RESULT" -eq 0 ]; then
    echo "PASS: $SCENARIO_NAME"
else
    echo "FAIL: $SCENARIO_NAME"
fi

exit $OVERALL_RESULT