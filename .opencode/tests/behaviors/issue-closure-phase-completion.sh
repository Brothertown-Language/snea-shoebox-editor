#!/bin/bash
# Behavioral Enforcement Test: Issue Closure Phase Completion
#
# Verifies that issue-closure.md correctly maps "Implements" keyword to
# completeness-check-required behavior and does NOT close issues with
# incomplete phases.
#
# Co-authored with AI: OpenCode (ollama-cloud/glm-5)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

# helpers.sh computes PROJECT_DIR from the main repo. For worktree tests,
# we need the worktree root (three levels up from behaviors/).
WORKTREE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

SCENARIO_NAME="issue-closure-phase-completion"
SCENARIO_PROMPT="When processing a PR body with 'Implements #N' where the spec #N has incomplete phases, the cleanup/issue-closure task must NOT close #N. Instead, it must require a completeness check first."

echo "=== Behavioral Test: $SCENARIO_NAME ==="

# For this content-verification behavioral test, we inspect the worktree file directly.
ISSUE_CLOSURE_FILE=".opencode/skills/git-workflow/tasks/cleanup/issue-closure.md"
WORKTREE_FILE="$WORKTREE_ROOT/$ISSUE_CLOSURE_FILE"

if [ ! -f "$WORKTREE_FILE" ]; then
    echo "FAIL: $SCENARIO_NAME — $ISSUE_CLOSURE_FILE not found"
    exit 1
fi

OVERALL_RESULT=0

# Verify 1: Keyword classification table contains "Implements" mapped to "completeness check required"
if ! grep -q 'Implements\s*#.*completeness check required' "$WORKTREE_FILE"; then
    echo "FAIL: $SCENARIO_NAME — 'Implements' keyword not mapped to 'completeness check required' in classification table"
    OVERALL_RESULT=1
else
    echo "PASS: $SCENARIO_NAME — 'Implements' keyword maps to 'completeness check required'"
fi

# Verify 2: Closure behavior table shows "implements" → "do NOT close if ANY phases/SCs remain incomplete"
if ! grep -q 'implements.*do NOT close if ANY phases' "$WORKTREE_FILE"; then
    echo "FAIL: $SCENARIO_NAME — closure behavior table does NOT show 'implements' → 'do NOT close if ANY phases remain incomplete'"
    OVERALL_RESULT=1
else
    echo "PASS: $SCENARIO_NAME — closure behavior table correctly prevents closing incomplete implements issues"
fi

# Verify 3: Step 4a contains Phase-Completion Verification (MANDATORY FIRST)
if ! grep -q 'Phase-Completion Verification (MANDATORY FIRST)' "$WORKTREE_FILE"; then
    echo "FAIL: $SCENARIO_NAME — Step 4a Phase-Completion Verification heading missing"
    OVERALL_RESULT=1
else
    echo "PASS: $SCENARIO_NAME — Step 4a Phase-Completion Verification heading present"
fi

# Verify 4: Step 4a explicitly says incomplete phases must skip closure
if ! grep -q 'If ANY phase is incomplete' "$WORKTREE_FILE"; then
    echo "FAIL: $SCENARIO_NAME — Step 4a does not explicitly check for incomplete phases"
    OVERALL_RESULT=1
else
    echo "PASS: $SCENARIO_NAME — Step 4a explicitly checks for incomplete phases"
fi

echo ""
if [ "$OVERALL_RESULT" -eq 0 ]; then
    echo "PASS: $SCENARIO_NAME"
else
    echo "FAIL: $SCENARIO_NAME"
fi

exit $OVERALL_RESULT
