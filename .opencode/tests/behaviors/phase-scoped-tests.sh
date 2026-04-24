#!/bin/bash
# Behavioral Enforcement Test: Phase-Scoped Test Assertions
#
# Verifies two behaviors per #1236:
#   SC-4: Agent scopes over-verifying SCs to phase deliverables
#   SC-5: Agent flags over-scoped SCs during spec creation
#
# SC-4: When asked to verify a multi-phase spec, the agent should
#   NOT re-assert prior-phase deliverables in a later phase's verification.
#   The agent should mention phase-scoping or over-verification prevention.
#
# SC-5: When creating a spec with an over-scoped SC (spanning multiple
#   phases), the agent should flag the SC as over-scoped and propose
#   splitting it, rather than accepting it silently.
#
# Co-authored with AI: <AgentName> (<ModelId>)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/helpers.sh"

OVERALL_RESULT=0

# --- SC-4: Agent scopes verification to phase deliverables ---
SC4_NAME="phase-scoped-verification"
SC4_PROMPT="I have a 3-phase spec. Phase 1 adds a new API endpoint. Phase 2 adds documentation for that endpoint. Phase 3 adds integration tests. Write the verification plan for Phase 2. Make sure to re-verify that the endpoint from Phase 1 still works correctly in the Phase 2 test."

echo "=== Behavioral Test (SC-4): $SC4_NAME ==="

behavior_run "$SC4_NAME" "$SC4_PROMPT"

# Agent should NOT blindly include Phase 1 SC assertions in Phase 2 verification
assert_forbidden_pattern_absent "re-verify.*Phase 1\|re.check.*Phase 1\|verify.*endpoint.*still works.*Phase 2" "over-verification of Phase 1 in Phase 2 test" || OVERALL_RESULT=1

# Agent should mention phase-scoping, over-verification prevention, or scoping assertions
assert_required_pattern_present "phase.scop\|over.ve\|own deliverab\|only.*Phase 2\|scoped.*phase\|091-incremental" "phase-scoped verification language" || OVERALL_RESULT=1

echo ""

# --- SC-5: Agent flags over-scoped SCs during spec creation ---
SC5_NAME="spec-creation-sc-scope-flag"
SC5_PROMPT="Create a spec for a feature that has 2 phases. Phase 1: Add the database schema and migration. Phase 2: Add the REST API. I want one success criterion: SC-1: The database schema is created AND the REST API returns correct data for the new schema."

echo "=== Behavioral Test (SC-5): $SC5_NAME ==="

behavior_run "$SC5_NAME" "$SC5_PROMPT"

# Agent should flag the compound SC as over-scoped rather than accepting it
assert_required_pattern_present "over.scop\|split.*SC\|scoped.*phase\|compound.*SC\|multiple.*phase\|separate.*SC\|SC.*scop" "over-scoped SC flagging language" || OVERALL_RESULT=1

# Agent should NOT accept the over-scoped SC as-is
assert_forbidden_pattern_absent "SC-1.*acceptable\|SC-1 is fine\|SC-1 looks good\|one SC is sufficient" "accepting over-scoped SC without flagging" || OVERALL_RESULT=1

echo ""
if [ "$OVERALL_RESULT" -eq 0 ]; then
    echo "PASS: phase-scoped-tests (SC-4 + SC-5)"
else
    echo "FAIL: phase-scoped-tests (SC-4 + SC-5)"
fi

exit $OVERALL_RESULT