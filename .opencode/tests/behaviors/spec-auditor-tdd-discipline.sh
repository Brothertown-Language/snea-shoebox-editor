#!/bin/bash
# Behavioral Enforcement Test: Spec Auditor TDD Discipline
#
# Verifies that spec-auditor task files include TDD discipline checks:
# - sc-precision.md includes behavioral test mandate verification
# - content-quality.md includes TDD-DISCIPLINE-GAP
#
# Co-authored with AI: OpenCode (ollama-cloud/glm-5)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

# helpers.sh computes PROJECT_DIR from the main repo. For worktree tests,
# we need the worktree root (three levels up from behaviors/).
WORKTREE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

SCENARIO_NAME="spec-auditor-tdd-discipline"
SCENARIO_PROMPT="The spec-auditor must include TDD discipline checks: sc-precision.md must verify behavioral test mandates, and content-quality.md must flag TDD-DISCIPLINE-GAP."

echo "=== Behavioral Test: $SCENARIO_NAME ==="

SC_PRECISION_FILE=".opencode/skills/spec-auditor/tasks/sc-precision.md"
CONTENT_QUALITY_FILE=".opencode/skills/spec-auditor/tasks/content-quality.md"
WORKTREE_SC="$WORKTREE_ROOT/$SC_PRECISION_FILE"
WORKTREE_CQ="$WORKTREE_ROOT/$CONTENT_QUALITY_FILE"

if [ ! -f "$WORKTREE_SC" ]; then
    echo "FAIL: $SCENARIO_NAME — $SC_PRECISION_FILE not found"
    exit 1
fi
if [ ! -f "$WORKTREE_CQ" ]; then
    echo "FAIL: $SCENARIO_NAME — $CONTENT_QUALITY_FILE not found"
    exit 1
fi

OVERALL_RESULT=0

# Verify 1: sc-precision.md has a TDD discipline check (behavioral test mandate verification)
if ! grep -qi 'TDD discipline check' "$WORKTREE_SC"; then
    echo "FAIL: $SCENARIO_NAME — sc-precision.md missing 'TDD discipline check' heading"
    OVERALL_RESULT=1
else
    echo "PASS: $SCENARIO_NAME — sc-precision.md contains 'TDD discipline check'"
fi

if ! grep -qi 'behavioral enforcement test' "$WORKTREE_SC"; then
    echo "FAIL: $SCENARIO_NAME — sc-precision.md missing behavioral enforcement test mandate verification"
    OVERALL_RESULT=1
else
    echo "PASS: $SCENARIO_NAME — sc-precision.md verifies behavioral enforcement test mandate"
fi

# Verify 2: sc-precision.md finding format includes TDD-DISCIPLINE-GAP
if ! grep -q 'TDD-DISCIPLINE-GAP' "$WORKTREE_SC"; then
    echo "FAIL: $SCENARIO_NAME — sc-precision.md finding format missing TDD-DISCIPLINE-GAP"
    OVERALL_RESULT=1
else
    echo "PASS: $SCENARIO_NAME — sc-precision.md finding format includes TDD-DISCIPLINE-GAP"
fi

# Verify 3: content-quality.md checks table includes TDD-DISCIPLINE-GAP
if ! grep -q 'TDD-DISCIPLINE-GAP' "$WORKTREE_CQ"; then
    echo "FAIL: $SCENARIO_NAME — content-quality.md missing TDD-DISCIPLINE-GAP in checks table"
    OVERALL_RESULT=1
else
    echo "PASS: $SCENARIO_NAME — content-quality.md checks table includes TDD-DISCIPLINE-GAP"
fi

# Verify 4: content-quality.md auto-fix classification table includes TDD-DISCIPLINE-GAP
if ! grep -q 'TDD discipline' "$WORKTREE_CQ"; then
    echo "FAIL: $SCENARIO_NAME — content-quality.md missing 'TDD discipline' row in checks table"
    OVERALL_RESULT=1
else
    echo "PASS: $SCENARIO_NAME — content-quality.md contains 'TDD discipline' check row"
fi

echo ""
if [ "$OVERALL_RESULT" -eq 0 ]; then
    echo "PASS: $SCENARIO_NAME"
else
    echo "FAIL: $SCENARIO_NAME"
fi

exit $OVERALL_RESULT
