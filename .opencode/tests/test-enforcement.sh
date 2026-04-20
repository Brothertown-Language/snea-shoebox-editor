#!/bin/bash
# Session Enforcement Plugin + Skills Integration Test
#
# Tests that the session-enforcement plugin loads correctly and that
# the LLM invokes appropriate skills based on user prompts.
#
# Runs opencode-cli run sequentially for each test scenario.
# No server needed - uses standalone mode.
#
# Uses with-test-home wrapper to isolate XDG state, allowing tests to
# run from within an active opencode desktop session without conflicts.
#
# Usage:  bash .opencode/tests/test-enforcement.sh
# Output: .opencode/tmp/enforcement-test-<timestamp>/results.md

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOGDIR="$PROJECT_DIR/.opencode/tmp/enforcement-test-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$LOGDIR"

TIMEOUT=120
MODEL="${ENFORCEMENT_TEST_MODEL:-ollama-cloud/glm-5.1}"
WITH_TEST_HOME="$PROJECT_DIR/.opencode/tests/with-test-home"

echo "=== Enforcement Integration Test ==="
echo "Log dir: $LOGDIR"
echo "Model: $MODEL"
echo "Mode: isolated (with-test-home wrapper)"
echo ""

# Test scenarios: name -> "prompt message"
declare -A SCENARIOS
SCENARIOS["bug-report"]="I have a bug - my database query returns wrong results"
SCENARIOS["create-spec"]="I want to create a new feature spec for user authentication"
SCENARIOS["simple-question"]="What does the session-enforcement plugin do?"
SCENARIOS["implement-request"]="implement the skill invocation enforcement plugin"
SCENARIOS["post-merge-cleanup"]="PR merged, the work is done"
SCENARIOS["symptom-patch"]="I found a bug where the cleanup step was skipped, let me just add a close-issue call to fix it"
SCENARIOS["incremental-build-guideline"]="Does the file .opencode/guidelines/091-incremental-build.md exist with sections for mandate, scope classification, top-down decomposition, bottom-up design, per-item TDD, and anti-patterns?"
SCENARIOS["monolithic-implementation-violation"]="Does .opencode/guidelines/000-critical-rules.md contain a critical violation section about Monolithic Implementation skipping item decomposition that references 091-incremental-build.md?"
SCENARIOS["item-decomposition-step"]="Does .opencode/skills/approval-gate/tasks/verify-authorization.md contain a Step 4.5 for item decomposition verification?"
SCENARIOS["brainstorming-top-down"]="Does .opencode/skills/brainstorming/SKILL.md reference the top-down-analysis task?"
SCENARIOS["writing-plans-bottom-up"]="Does .opencode/skills/writing-plans/SKILL.md contain per-item bottom-up design sections?"
SCENARIOS["executing-plans-tdd"]="Does .opencode/skills/executing-plans/SKILL.md reference the per-item TDD cycle?"
SCENARIOS["divide-conquer-tdd"]="Does .opencode/skills/divide-and-conquer/SKILL.md dispatch context include tdd_phase?"
SCENARIOS["agents-md-incremental"]="Does AGENTS.md list incremental-build in the guidelines table?"

# Expected skill invocations per scenario (empty = no specific skill expected)
declare -A EXPECTED_SKILLS
EXPECTED_SKILLS["bug-report"]="systematic-debugging"
EXPECTED_SKILLS["create-spec"]="brainstorming"
EXPECTED_SKILLS["simple-question"]=""
EXPECTED_SKILLS["implement-request"]="approval-gate"
EXPECTED_SKILLS["post-merge-cleanup"]="git-workflow"
EXPECTED_SKILLS["symptom-patch"]="issue-review"
EXPECTED_SKILLS["incremental-build-guideline"]=""
EXPECTED_SKILLS["monolithic-implementation-violation"]=""
EXPECTED_SKILLS["item-decomposition-step"]=""
EXPECTED_SKILLS["brainstorming-top-down"]=""
EXPECTED_SKILLS["writing-plans-bottom-up"]=""
EXPECTED_SKILLS["executing-plans-tdd"]=""
EXPECTED_SKILLS["divide-conquer-tdd"]=""
EXPECTED_SKILLS["agents-md-incremental"]=""

RESULTS_FILE="$LOGDIR/results.md"

echo "# Enforcement Integration Test Results" > "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "Date: $(date -Iseconds)" >> "$RESULTS_FILE"
echo "Model: $MODEL" >> "$RESULTS_FILE"
echo "Mode: isolated (with-test-home)" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

OVERALL_PASS=true

for scenario_name in bug-report create-spec simple-question implement-request post-merge-cleanup symptom-patch incremental-build-guideline monolithic-implementation-violation item-decomposition-step brainstorming-top-down writing-plans-bottom-up executing-plans-tdd divide-conquer-tdd agents-md-incremental; do
    MESSAGE="${SCENARIOS[$scenario_name]}"
    EXPECTED="${EXPECTED_SKILLS[$scenario_name]}"
    SCENARIO_LOG="$LOGDIR/${scenario_name}.log"
    SCENARIO_OUT="$LOGDIR/${scenario_name}.out"

    echo ""
    echo "=== Testing scenario: $scenario_name ==="
    echo "Message: $MESSAGE"
    echo "Expected skill: ${EXPECTED:-none}"

    echo "## Scenario: $scenario_name" >> "$RESULTS_FILE"
    echo "" >> "$RESULTS_FILE"
    echo "**Message:** \`$MESSAGE\`" >> "$RESULTS_FILE"
    echo "**Expected skill:** ${EXPECTED:-none}" >> "$RESULTS_FILE"
    echo "" >> "$RESULTS_FILE"

    # Run opencode-cli in isolated mode via with-test-home wrapper
    # --print-logs goes to stderr, formatted output to stdout
    timeout $TIMEOUT bash "$WITH_TEST_HOME" opencode-cli run "$MESSAGE" \
        --model "$MODEL" \
        --print-logs \
        > "$SCENARIO_OUT" 2> "$SCENARIO_LOG" \
        || true

    # Small delay for file flush
    sleep 1

    # Check for plugin loading in stderr log
    PLUGIN_LOADED=$(grep -c "session-enforcement.ts loading plugin" "$SCENARIO_LOG" 2>/dev/null || echo "0")
    SKILL_COUNT=$(grep "service=skill count=" "$SCENARIO_LOG" 2>/dev/null | tail -1 | grep -oP 'count=\K[0-9]+' || echo "0")

    # Check for skill invocations in stderr log (formatted output)
    SKILL_INVOKED=""
    if [ -f "$SCENARIO_LOG" ]; then
        SKILL_INVOKED=$(grep -oP 'Skill "\K[^"]+' "$SCENARIO_LOG" 2>/dev/null | sort -u | tr '\n' ',' | sed 's/,$//' || echo "")
    fi
    # Fallback: check stdout for skill names
    if [ -z "$SKILL_INVOKED" ] && [ -f "$SCENARIO_OUT" ]; then
        SKILL_INVOKED=$(grep -oiE "(systematic-debugging|brainstorming|approval-gate|git-workflow|spec-auditor|writing-plans|issue-review)" "$SCENARIO_OUT" 2>/dev/null | sort -u | tr '\n' ',' | sed 's/,$//' || echo "")
    fi

    echo "**Results:**" >> "$RESULTS_FILE"
    echo "- Plugin loaded: $PLUGIN_LOADED instances" >> "$RESULTS_FILE"
    echo "- Skills discovered: $SKILL_COUNT" >> "$RESULTS_FILE"
    echo "- Skills invoked by model: ${SKILL_INVOKED:-none detected}" >> "$RESULTS_FILE"
    echo "" >> "$RESULTS_FILE"

    echo "  Plugin loaded: $PLUGIN_LOADED"
    echo "  Skills discovered: $SKILL_COUNT"
    echo "  Skills invoked: ${SKILL_INVOKED:-none detected}"

    # Determine pass/fail for plugin infrastructure
    if [ "$PLUGIN_LOADED" -ge 1 ] && [ "$SKILL_COUNT" -ge 1 ]; then
        INFRA_PASS="PASS"
    else
        INFRA_PASS="FAIL"
        OVERALL_PASS=false
    fi

    # Determine pass/fail for skill invocation
    if [ -n "$EXPECTED" ] && [ -n "$SKILL_INVOKED" ]; then
        if echo "$SKILL_INVOKED" | grep -qi "$EXPECTED"; then
            SKILL_PASS="PASS"
        else
            SKILL_PASS="PARTIAL (invoked: $SKILL_INVOKED, expected: $EXPECTED)"
        fi
    elif [ -z "$EXPECTED" ]; then
        SKILL_PASS="N/A (no specific skill expected)"
    else
        SKILL_PASS="FAIL (no skills detected)"
        OVERALL_PASS=false
    fi

    echo "  Infrastructure: $INFRA_PASS" >> "$RESULTS_FILE"
    echo "  Skill invocation: $SKILL_PASS" >> "$RESULTS_FILE"
    echo "" >> "$RESULTS_FILE"

    echo "  Infrastructure: $INFRA_PASS"
    echo "  Skill invocation: $SKILL_PASS"
    echo ""
done

# Summary
echo "## Summary" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "- **Overall:** $([ "$OVERALL_PASS" = true ] && echo 'PASS' || echo 'FAIL')" >> "$RESULTS_FILE"
echo "- **Plugin infrastructure loaded:** Verified per-scenario from run logs" >> "$RESULTS_FILE"
echo "- **Skill invocation by model:** Depends on model behavior (non-deterministic)" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

echo "## Key Plugin Events (from bug-report scenario)" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo '```' >> "$RESULTS_FILE"
grep -E "(loading plugin|service=skill count|session-enforcement|error|Error)" "$LOGDIR/bug-report.log" 2>/dev/null | head -20 >> "$RESULTS_FILE"
echo '```' >> "$RESULTS_FILE"

echo ""
echo "=== Guideline Content Verification ==="
echo "" >> "$RESULTS_FILE"
echo "## Guideline Content Verification" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

GUIDELINE_FILE="$PROJECT_DIR/.opencode/guidelines/091-incremental-build.md"
GUIDELINE_PASS=true

if [ -f "$GUIDELINE_FILE" ]; then
    echo "  091-incremental-build.md: EXISTS"
    echo "- **091-incremental-build.md:** EXISTS" >> "$RESULTS_FILE"
    for section in "Mandate" "Scope Classification" "Top-Down Decomposition" "Bottom-Up Design" "Per-Item TDD" "Anti-Patterns"; do
        COUNT=$(grep -c "## .*$section" "$GUIDELINE_FILE" 2>/dev/null || echo "0")
        if [ "$COUNT" -ge 1 ]; then
            echo "  Section '$section': FOUND"
            echo "  - Section \`$section\`: FOUND" >> "$RESULTS_FILE"
        else
            echo "  Section '$section': MISSING"
            echo "  - Section \`$section\`: MISSING" >> "$RESULTS_FILE"
            GUIDELINE_PASS=false
            OVERALL_PASS=false
        fi
    done
else
    echo "  091-incremental-build.md: MISSING"
    echo "- **091-incremental-build.md:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Verify Monolithic Implementation critical violation section
CRITICAL_RULES_FILE="$PROJECT_DIR/.opencode/guidelines/000-critical-rules.md"
if [ -f "$CRITICAL_RULES_FILE" ]; then
    MONO_COUNT=$(grep -c "Monolithic Implementation" "$CRITICAL_RULES_FILE" 2>/dev/null || echo "0")
    if [ "$MONO_COUNT" -ge 1 ]; then
        echo "  Monolithic Implementation section: FOUND"
        echo "- **Monolithic Implementation section:** FOUND" >> "$RESULTS_FILE"
    else
        echo "  Monolithic Implementation section: MISSING"
        echo "- **Monolithic Implementation section:** MISSING" >> "$RESULTS_FILE"
        GUIDELINE_PASS=false
        OVERALL_PASS=false
    fi
    # Verify cross-reference to 091-incremental-build.md
    XREF_COUNT=$(grep -c "091-incremental-build" "$CRITICAL_RULES_FILE" 2>/dev/null || echo "0")
    if [ "$XREF_COUNT" -ge 1 ]; then
        echo "  Cross-reference to 091-incremental-build.md: FOUND"
        echo "  - **Cross-reference to 091-incremental-build.md:** FOUND" >> "$RESULTS_FILE"
    else
        echo "  Cross-reference to 091-incremental-build.md: MISSING"
        echo "  - **Cross-reference to 091-incremental-build.md:** MISSING" >> "$RESULTS_FILE"
        GUIDELINE_PASS=false
        OVERALL_PASS=false
    fi
else
    echo "  000-critical-rules.md: MISSING"
    echo "- **000-critical-rules.md:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Verify Step 4.5 item decomposition verification
VERIFY_AUTH_FILE="$PROJECT_DIR/.opencode/skills/approval-gate/tasks/verify-authorization.md"
if [ -f "$VERIFY_AUTH_FILE" ]; then
    STEP45_COUNT=$(grep -c "Step 4.5" "$VERIFY_AUTH_FILE" 2>/dev/null || echo "0")
    if [ "$STEP45_COUNT" -ge 1 ]; then
        echo "  Step 4.5 item decomposition: FOUND"
        echo "- **Step 4.5 item decomposition:** FOUND" >> "$RESULTS_FILE"
    else
        echo "  Step 4.5 item decomposition: MISSING"
        echo "- **Step 4.5 item decomposition:** MISSING" >> "$RESULTS_FILE"
        GUIDELINE_PASS=false
        OVERALL_PASS=false
    fi
    # Verify reference to 091-incremental-build.md
    IBLD_XREF=$(grep -c "091-incremental-build" "$VERIFY_AUTH_FILE" 2>/dev/null || echo "0")
    if [ "$IBLD_XREF" -ge 1 ]; then
        echo "  verify-authorization cross-ref to 091: FOUND"
        echo "  - **verify-authorization cross-ref to 091:** FOUND" >> "$RESULTS_FILE"
    else
        echo "  verify-authorization cross-ref to 091: MISSING"
        echo "  - **verify-authorization cross-ref to 091:** MISSING" >> "$RESULTS_FILE"
        GUIDELINE_PASS=false
        OVERALL_PASS=false
    fi
else
    echo "  verify-authorization.md: MISSING"
    echo "- **verify-authorization.md:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Verify brainstorming top-down-analysis task reference
BRAINSTORMING_SKILL="$PROJECT_DIR/.opencode/skills/brainstorming/SKILL.md"
if [ -f "$BRAINSTORMING_SKILL" ]; then
    TD_COUNT=$(grep -c "top-down-analysis" "$BRAINSTORMING_SKILL" 2>/dev/null || echo "0")
    if [ "$TD_COUNT" -ge 1 ]; then
        echo "  brainstorming top-down-analysis: FOUND"
        echo "- **brainstorming top-down-analysis:** FOUND" >> "$RESULTS_FILE"
    else
        echo "  brainstorming top-down-analysis: MISSING"
        echo "- **brainstorming top-down-analysis:** MISSING" >> "$RESULTS_FILE"
        GUIDELINE_PASS=false
        OVERALL_PASS=false
    fi
else
    echo "  brainstorming/SKILL.md: MISSING"
    echo "- **brainstorming/SKILL.md:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Verify writing-plans bottom-up design sections
WRITING_PLANS_SKILL="$PROJECT_DIR/.opencode/skills/writing-plans/SKILL.md"
if [ -f "$WRITING_PLANS_SKILL" ]; then
    BU_COUNT=$(grep -c "bottom-up\|Bottom-Up" "$WRITING_PLANS_SKILL" 2>/dev/null || echo "0")
    if [ "$BU_COUNT" -ge 1 ]; then
        echo "  writing-plans bottom-up design: FOUND"
        echo "- **writing-plans bottom-up design:** FOUND" >> "$RESULTS_FILE"
    else
        echo "  writing-plans bottom-up design: MISSING"
        echo "- **writing-plans bottom-up design:** MISSING" >> "$RESULTS_FILE"
        GUIDELINE_PASS=false
        OVERALL_PASS=false
    fi
else
    echo "  writing-plans/SKILL.md: MISSING"
    echo "- **writing-plans/SKILL.md:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Verify executing-plans TDD cycle reference
EXEC_PLANS_SKILL="$PROJECT_DIR/.opencode/skills/executing-plans/SKILL.md"
if [ -f "$EXEC_PLANS_SKILL" ]; then
    TDD_EXEC=$(grep -c "per-item TDD\|TDD cycle\|091-incremental-build" "$EXEC_PLANS_SKILL" 2>/dev/null || echo "0")
    if [ "$TDD_EXEC" -ge 1 ]; then
        echo "  executing-plans TDD cycle: FOUND"
        echo "- **executing-plans TDD cycle:** FOUND" >> "$RESULTS_FILE"
    else
        echo "  executing-plans TDD cycle: MISSING"
        echo "- **executing-plans TDD cycle:** MISSING" >> "$RESULTS_FILE"
        GUIDELINE_PASS=false
        OVERALL_PASS=false
    fi
else
    echo "  executing-plans/SKILL.md: MISSING"
    echo "- **executing-plans/SKILL.md:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Verify divide-and-conquer TDD phase in dispatch context
DC_SKILL="$PROJECT_DIR/.opencode/skills/divide-and-conquer/SKILL.md"
if [ -f "$DC_SKILL" ]; then
    TDD_DC=$(grep -c "tdd_phase" "$DC_SKILL" 2>/dev/null || echo "0")
    if [ "$TDD_DC" -ge 1 ]; then
        echo "  divide-and-conquer tdd_phase: FOUND"
        echo "- **divide-and-conquer tdd_phase:** FOUND" >> "$RESULTS_FILE"
    else
        echo "  divide-and-conquer tdd_phase: MISSING"
        echo "- **divide-and-conquer tdd_phase:** MISSING" >> "$RESULTS_FILE"
        GUIDELINE_PASS=false
        OVERALL_PASS=false
    fi
else
    echo "  divide-and-conquer/SKILL.md: MISSING"
    echo "- **divide-and-conquer/SKILL.md:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Verify AGENTS.md lists incremental-build
AGENTS_FILE="$PROJECT_DIR/AGENTS.md"
if [ -f "$AGENTS_FILE" ]; then
    IBL_AGENTS=$(grep -c "incremental-build" "$AGENTS_FILE" 2>/dev/null || echo "0")
    if [ "$IBL_AGENTS" -ge 1 ]; then
        echo "  AGENTS.md incremental-build reference: FOUND"
        echo "- **AGENTS.md incremental-build reference:** FOUND" >> "$RESULTS_FILE"
    else
        echo "  AGENTS.md incremental-build reference: MISSING"
        echo "- **AGENTS.md incremental-build reference:** MISSING" >> "$RESULTS_FILE"
        GUIDELINE_PASS=false
        OVERALL_PASS=false
    fi
else
    echo "  AGENTS.md: MISSING"
    echo "- **AGENTS.md:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

echo ""
echo "=== Test Complete ==="
echo "Results: $RESULTS_FILE"
echo "Log directory: $LOGDIR"

if [ "$OVERALL_PASS" = true ]; then
    echo "OVERALL: PASS"
else
    echo "OVERALL: FAIL"
fi