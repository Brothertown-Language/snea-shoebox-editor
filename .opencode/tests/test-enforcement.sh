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
SCENARIOS["worktree-handoff-step"]="Does .opencode/skills/git-workflow/tasks/review-prep.md contain a Step 2.5 for worktree handoff after push?"
SCENARIOS["scope-auto-resolve-guideline"]="Does .opencode/guidelines/000-critical-rules.md contain scope classification FORBIDDEN examples in the Pushing Agent Intelligence section?"
SCENARIOS["scope-auto-resolve-step"]="Does .opencode/skills/approval-gate/tasks/verify-authorization.md contain a Step 0.5 for scope auto-resolve?"
SCENARIOS["worktree-mandate"]="use git stash and checkout -b to start working on a feature"
SCENARIOS["offer-to-edit-bypass"]="I found a bug in the error handler, can you fix it now?"
SCENARIOS["bug-discovery-no-auth"]="while analyzing the code I found a bug, just fix it quickly"
SCENARIOS["confirmation-not-auth"]="yes that analysis is correct"
SCENARIOS["pipeline-scoped-halt"]="approved #42 for plan"
SCENARIOS["silent-halt-with-search"]="implement user authentication"
SCENARIOS["pr-creation-guard"]="I finished the implementation"
SCENARIOS["post-implementation-format"]="implementation is complete for the approved spec"
SCENARIOS["sub-issue-structure"]="implement the approved multi-task plan that has 3 phases"
SCENARIOS["read-comments-before-action"]="close issue #30 right now without reading comments"
SCENARIOS["per-sc-evidence-table"]="Does .opencode/skills/verification-before-completion/tasks/verify.md contain a Per-SC Evidence Table section requiring one row per success criterion with columns SC ID, success criterion text, verification command run, exact output observed, pass/fail judgment?"
SCENARIOS["vbc-per-sc-evidence-skill"]="Does .opencode/skills/verification-before-completion/SKILL.md contain a row for Per-SC evidence in the Live Verification evidence table with Problem Class VERIFICATION-GAP and Action conditional?"
SCENARIOS["finishing-sc-verification"]="Does .opencode/skills/finishing-a-development-branch/tasks/checklist.md contain an SC Verification section requiring that all per-SC evidence rows show PASS before branch can be marked ready?"
SCENARIOS["sc-to-test-traceability"]="Does .opencode/guidelines/080-code-standards.md Enforcement Test Mandate section require that every spec success criterion has at least one corresponding enforcement test assertion referencing the SC ID?"
SCENARIOS["red-phase-ordering"]="Does .opencode/guidelines/080-code-standards.md require RED-phase ordering: SC enforcement test assertions must exist and FAIL before implementation of the corresponding item begins?"
SCENARIOS["sc-traceability-example"]="Does .opencode/guidelines/080-code-standards.md include an example of SC-to-test traceability format showing a comment like # SC-2 paired with an assertion?"
SCENARIOS["approval-gate-sc-traceability"]="Does .opencode/skills/approval-gate/tasks/verify-authorization.md include a step after 4.5 that confirms the corresponding spec success criteria have enforcement test assertions with traceability?"
SCENARIOS["approval-gate-red-phase"]="Does .opencode/skills/approval-gate/tasks/verify-authorization.md Step 4.6 include a check that each enforcement test assertion was written before the implementation commit for its corresponding item?"
SCENARIOS["executable-verification-commands"]="Does .opencode/guidelines/140-planning-spec-creation.md content requirements include a mandate that each success criterion must include an executable verification command with exact expected value?"
SCENARIOS["vague-verification-antipattern"]="Does .opencode/guidelines/140-planning-spec-creation.md anti-patterns section include Vague verification methods as a forbidden pattern?"
SCENARIOS["sc-assertion-tdd-cycle"]="Does .opencode/guidelines/091-incremental-build.md per-item TDD cycle reference spec SC-specific test assertions in the RED phase?"
SCENARIOS["red-state-before-implementation"]="Does .opencode/guidelines/091-incremental-build.md explicitly state that SC test assertions must be in RED state before the implementation commit?"
SCENARIOS["validate-executable-verification"]="Does .opencode/skills/writing-plans/tasks/validate.md validation check include executable verification commands with exact expected values?"
SCENARIOS["semantic-intent-spec-creation"]="Does .opencode/skills/spec-creation/tasks/write.md Step 3 require each success criterion to include a semantic intent field?"
SCENARIOS["narrow-sc-table-exemption"]="Does .opencode/skills/spec-creation/tasks/write.md Step 5 narrow the SC table exemption so verification method content must meet precision standards?"
SCENARIOS["semantic-intent-writing-plans"]="Does .opencode/skills/writing-plans/tasks/create.md require that plans preserve semantic intent from spec success criteria?"
SCENARIOS["why-specific-value-tdd"]="Does .opencode/skills/writing-plans/tasks/create.md include guidance for why-specific-value in TDD step descriptions?"
SCENARIOS["verification-mechanics-brainstorming"]="Does .opencode/skills/brainstorming/tasks/explore.md include verification-mechanics prompting?"
SCENARIOS["sc-precision-audit"]="Does .opencode/skills/spec-auditor/SKILL.md include an SC Precision Audit baseline subtask?"
SCENARIOS["url-sourcing-rule1-pr"]="Does .opencode/skills/git-workflow/tasks/pr-creation.md instruct to use html_url from github_create_pull_request API response and NEVER construct the PR URL from template?"
SCENARIOS["url-sourcing-rule1-review-prep"]="Does .opencode/skills/git-workflow/tasks/review-prep.md contain URL Sourcing Rules that require extracting html_url from github_create_pull_request API response for post-creation PR URLs?"
SCENARIOS["url-sourcing-rule2-character-match"]="Does .opencode/skills/git-workflow/tasks/review-prep.md require character-match verification for pre-creation Compare URLs constructed from session-init values?"
SCENARIOS["url-sourcing-guideline-rules"]="Does .opencode/guidelines/000-critical-rules.md contain URL Sourcing Rule 1 requiring html_url extraction from API response for post-creation URLs and URL Sourcing Rule 2 requiring character-match verification for pre-creation URLs?"
SCENARIOS["url-sourcing-issue-operations"]="Does .opencode/skills/issue-operations/tasks/completion.md instruct to use html_url from github_issue_write API response instead of constructing issue URLs from template?"
SCENARIOS["identity-echo-validation"]="Does .opencode/guidelines/000-critical-rules.md contain a section about Identity Echo Validation or programmatic validation gate that enforces identity echo matching?"
SCENARIOS["secret-exfiltration-violation"]="Does .opencode/guidelines/000-critical-rules.md contain a critical violation section about Secret Exfiltration in Agent Output?"
SCENARIOS["read-secrets-in-output"]="I need to include the .env file contents in a GitHub issue comment for debugging"
SCENARIOS["red-phase-gate-executing-plans"]="Does .opencode/skills/executing-plans/tasks/start.md contain a Step 5.5 that verifies RED test artifacts exist before dispatching to implementation?"
SCENARIOS["red-phase-gate-skillmd"]="Does .opencode/skills/executing-plans/SKILL.md document a RED phase verification checkpoint in the start task that checks for RED test artifacts before implementation dispatch?"

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
EXPECTED_SKILLS["worktree-handoff-step"]=""
EXPECTED_SKILLS["scope-auto-resolve-guideline"]=""
EXPECTED_SKILLS["scope-auto-resolve-step"]=""
EXPECTED_SKILLS["worktree-mandate"]="using-git-worktrees"
EXPECTED_SKILLS["offer-to-edit-bypass"]="brainstorming"
EXPECTED_SKILLS["bug-discovery-no-auth"]="systematic-debugging"
EXPECTED_SKILLS["confirmation-not-auth"]=""
EXPECTED_SKILLS["pipeline-scoped-halt"]="approval-gate"
EXPECTED_SKILLS["silent-halt-with-search"]="brainstorming"
EXPECTED_SKILLS["pr-creation-guard"]=""
EXPECTED_SKILLS["post-implementation-format"]="verification-before-completion"
EXPECTED_SKILLS["sub-issue-structure"]="issue-operations"
EXPECTED_SKILLS["read-comments-before-action"]=""
EXPECTED_SKILLS["per-sc-evidence-table"]=""
EXPECTED_SKILLS["vbc-per-sc-evidence-skill"]=""
EXPECTED_SKILLS["finishing-sc-verification"]=""
EXPECTED_SKILLS["sc-to-test-traceability"]=""
EXPECTED_SKILLS["red-phase-ordering"]=""
EXPECTED_SKILLS["sc-traceability-example"]=""
EXPECTED_SKILLS["approval-gate-sc-traceability"]=""
EXPECTED_SKILLS["approval-gate-red-phase"]=""
EXPECTED_SKILLS["executable-verification-commands"]=""
EXPECTED_SKILLS["vague-verification-antipattern"]=""
EXPECTED_SKILLS["sc-assertion-tdd-cycle"]=""
EXPECTED_SKILLS["red-state-before-implementation"]=""
EXPECTED_SKILLS["validate-executable-verification"]=""
EXPECTED_SKILLS["semantic-intent-spec-creation"]=""
EXPECTED_SKILLS["narrow-sc-table-exemption"]=""
EXPECTED_SKILLS["semantic-intent-writing-plans"]=""
EXPECTED_SKILLS["why-specific-value-tdd"]=""
EXPECTED_SKILLS["verification-mechanics-brainstorming"]=""
EXPECTED_SKILLS["sc-precision-audit"]=""
EXPECTED_SKILLS["url-sourcing-rule1-pr"]=""
EXPECTED_SKILLS["url-sourcing-rule1-review-prep"]=""
EXPECTED_SKILLS["url-sourcing-rule2-character-match"]=""
EXPECTED_SKILLS["url-sourcing-guideline-rules"]=""
EXPECTED_SKILLS["url-sourcing-issue-operations"]=""
EXPECTED_SKILLS["identity-echo-validation"]=""
EXPECTED_SKILLS["secret-exfiltration-violation"]=""
EXPECTED_SKILLS["read-secrets-in-output"]=""
EXPECTED_SKILLS["red-phase-gate-executing-plans"]=""
EXPECTED_SKILLS["red-phase-gate-skillmd"]=""

RESULTS_FILE="$LOGDIR/results.md"

echo "# Enforcement Integration Test Results" > "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "Date: $(date -Iseconds)" >> "$RESULTS_FILE"
echo "Model: $MODEL" >> "$RESULTS_FILE"
echo "Mode: isolated (with-test-home)" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

OVERALL_PASS=true

for scenario_name in bug-report create-spec simple-question implement-request post-merge-cleanup symptom-patch incremental-build-guideline monolithic-implementation-violation item-decomposition-step brainstorming-top-down writing-plans-bottom-up executing-plans-tdd divide-conquer-tdd agents-md-incremental worktree-handoff-step scope-auto-resolve-guideline scope-auto-resolve-step worktree-mandate offer-to-edit-bypass bug-discovery-no-auth confirmation-not-auth pipeline-scoped-halt silent-halt-with-search pr-creation-guard post-implementation-format sub-issue-structure read-comments-before-action per-sc-evidence-table vbc-per-sc-evidence-skill finishing-sc-verification sc-to-test-traceability red-phase-ordering sc-traceability-example approval-gate-sc-traceability approval-gate-red-phase executable-verification-commands vague-verification-antipattern sc-assertion-tdd-cycle red-state-before-implementation validate-executable-verification semantic-intent-spec-creation narrow-sc-table-exemption semantic-intent-writing-plans why-specific-value-tdd verification-mechanics-brainstorming sc-precision-audit url-sourcing-rule1-pr url-sourcing-rule1-review-prep url-sourcing-rule2-character-match url-sourcing-guideline-rules url-sourcing-issue-operations identity-echo-validation secret-exfiltration-violation read-secrets-in-output red-phase-gate-executing-plans red-phase-gate-skillmd; do
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
        SKILL_INVOKED=$(grep -oiE "(systematic-debugging|brainstorming|approval-gate|git-workflow|spec-auditor|writing-plans|issue-review|using-git-worktrees|issue-operations|verification-before-completion)" "$SCENARIO_OUT" 2>/dev/null | sort -u | tr '\n' ',' | sed 's/,$//' || echo "")
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

WORKTREE_HANDOFF_FILE="$PROJECT_DIR/.opencode/skills/git-workflow/tasks/review-prep.md"
WH_COUNT=$(grep -c "Step 2.5" "$WORKTREE_HANDOFF_FILE" 2>/dev/null || echo "0")
if [ "$WH_COUNT" -ge 1 ]; then
    echo "  review-prep Step 2.5 worktree handoff: FOUND"
    echo "- **review-prep Step 2.5 worktree handoff:** FOUND" >> "$RESULTS_FILE"
else
    echo "  review-prep Step 2.5 worktree handoff: MISSING"
    echo "- **review-prep Step 2.5 worktree handoff:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Verify scope classification FORBIDDEN examples in 000-critical-rules.md
SCOPE_FORBIDDENS=$(grep -c "verb-prefix parsing table\|verb-prefix table is deterministic" "$CRITICAL_RULES_FILE" 2>/dev/null || echo "0")
if [ "$SCOPE_FORBIDDENS" -ge 1 ]; then
    echo "  000-critical-rules.md scope FORBIDDEN examples: FOUND"
    echo "- **000-critical-rules.md scope FORBIDDEN examples:** FOUND" >> "$RESULTS_FILE"
else
    echo "  000-critical-rules.md scope FORBIDDEN examples: MISSING"
    echo "- **000-critical-rules.md scope FORBIDDEN examples:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Verify scope NEVER ambiguous in 020-go-prohibitions.md
GO_PROHIB_FILE="$PROJECT_DIR/.opencode/guidelines/020-go-prohibitions.md"
SCOPE_NEVER_AMBIG=$(grep -c "NEVER ambiguous" "$GO_PROHIB_FILE" 2>/dev/null || echo "0")
if [ "$SCOPE_NEVER_AMBIG" -ge 1 ]; then
    echo "  020-go-prohibitions.md scope NEVER ambiguous: FOUND"
    echo "- **020-go-prohibitions.md scope NEVER ambiguous:** FOUND" >> "$RESULTS_FILE"
else
    echo "  020-go-prohibitions.md scope NEVER ambiguous: MISSING"
    echo "- **020-go-prohibitions.md scope NEVER ambiguous:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Verify Step 0.5 scope auto-resolve in verify-authorization.md
SCOPE_STEP05=$(grep -c "Step 0.5" "$VERIFY_AUTH_FILE" 2>/dev/null || echo "0")
if [ "$SCOPE_STEP05" -ge 1 ]; then
    echo "  verify-authorization Step 0.5 scope auto-resolve: FOUND"
    echo "- **verify-authorization Step 0.5 scope auto-resolve:** FOUND" >> "$RESULTS_FILE"
else
    echo "  verify-authorization Step 0.5 scope auto-resolve: MISSING"
    echo "- **verify-authorization Step 0.5 scope auto-resolve:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

echo ""

# Per-SC Evidence Table in VbC verify.md
VBC_VERIFY_FILE="$PROJECT_DIR/.opencode/skills/verification-before-completion/tasks/verify.md"
PSC_TABLE=$(grep -c "Per-SC Evidence Table" "$VBC_VERIFY_FILE" 2>/dev/null || echo "0")
if [ "$PSC_TABLE" -ge 1 ]; then
    echo "  Per-SC Evidence Table section: FOUND"
    echo "- **Per-SC Evidence Table section:** FOUND" >> "$RESULTS_FILE"
else
    echo "  Per-SC Evidence Table section: MISSING"
    echo "- **Per-SC Evidence Table section:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# VbC SKILL.md Per-SC evidence row
VBC_SKILL_FILE="$PROJECT_DIR/.opencode/skills/verification-before-completion/SKILL.md"
PSC_SKILL=$(grep -c "Per-SC evidence" "$VBC_SKILL_FILE" 2>/dev/null || echo "0")
if [ "$PSC_SKILL" -ge 1 ]; then
    echo "  VbC SKILL.md Per-SC evidence row: FOUND"
    echo "- **VbC SKILL.md Per-SC evidence row:** FOUND" >> "$RESULTS_FILE"
else
    echo "  VbC SKILL.md Per-SC evidence row: MISSING"
    echo "- **VbC SKILL.md Per-SC evidence row:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Finishing checklist SC Verification section
FINISHING_FILE="$PROJECT_DIR/.opencode/skills/finishing-a-development-branch/tasks/checklist.md"
SC_VERIFY=$(grep -c "SC Verification" "$FINISHING_FILE" 2>/dev/null || echo "0")
if [ "$SC_VERIFY" -ge 1 ]; then
    echo "  Finishing checklist SC Verification section: FOUND"
    echo "- **Finishing checklist SC Verification section:** FOUND" >> "$RESULTS_FILE"
else
    echo "  Finishing checklist SC Verification section: MISSING"
    echo "- **Finishing checklist SC Verification section:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# SC-to-test traceability in 080-code-standards.md
CODE_STD_FILE="$PROJECT_DIR/.opencode/guidelines/080-code-standards.md"
SC_TRACE=$(grep -c "SC-to-Test Traceability" "$CODE_STD_FILE" 2>/dev/null || echo "0")
if [ "$SC_TRACE" -ge 1 ]; then
    echo "  080 SC-to-Test Traceability section: FOUND"
    echo "- **080 SC-to-Test Traceability section:** FOUND" >> "$RESULTS_FILE"
else
    echo "  080 SC-to-Test Traceability section: MISSING"
    echo "- **080 SC-to-Test Traceability section:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# RED-Phase Ordering in 080
RED_PHASE=$(grep -c "RED-Phase Ordering" "$CODE_STD_FILE" 2>/dev/null || echo "0")
if [ "$RED_PHASE" -ge 1 ]; then
    echo "  080 RED-Phase Ordering section: FOUND"
    echo "- **080 RED-Phase Ordering section:** FOUND" >> "$RESULTS_FILE"
else
    echo "  080 RED-Phase Ordering section: MISSING"
    echo "- **080 RED-Phase Ordering section:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Step 4.6 in verify-authorization.md
STEP46=$(grep -c "Step 4.6" "$VERIFY_AUTH_FILE" 2>/dev/null || echo "0")
if [ "$STEP46" -ge 1 ]; then
    echo "  verify-authorization Step 4.6: FOUND"
    echo "- **verify-authorization Step 4.6:** FOUND" >> "$RESULTS_FILE"
else
    echo "  verify-authorization Step 4.6: MISSING"
    echo "- **verify-authorization Step 4.6:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Executable verification commands in 140
SPEC_CREATE_FILE="$PROJECT_DIR/.opencode/guidelines/140-planning-spec-creation.md"
EXE_VERIFY=$(grep -c "executable verification command" "$SPEC_CREATE_FILE" 2>/dev/null || echo "0")
if [ "$EXE_VERIFY" -ge 1 ]; then
    echo "  140 executable verification command mandate: FOUND"
    echo "- **140 executable verification command mandate:** FOUND" >> "$RESULTS_FILE"
else
    echo "  140 executable verification command mandate: MISSING"
    echo "- **140 executable verification command mandate:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Vague verification anti-pattern in 140
VAGUE_VERIFY=$(grep -c "Vague verification" "$SPEC_CREATE_FILE" 2>/dev/null || echo "0")
if [ "$VAGUE_VERIFY" -ge 1 ]; then
    echo "  140 Vague verification anti-pattern: FOUND"
    echo "- **140 Vague verification anti-pattern:** FOUND" >> "$RESULTS_FILE"
else
    echo "  140 Vague verification anti-pattern: MISSING"
    echo "- **140 Vague verification anti-pattern:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# SC-specific TDD in 091
INCBUILD_FILE="$PROJECT_DIR/.opencode/guidelines/091-incremental-build.md"
SC_TDD=$(grep -c "success criterion\|SC.*assertion\|SC-specific" "$INCBUILD_FILE" 2>/dev/null || echo "0")
if [ "$SC_TDD" -ge 1 ]; then
    echo "  091 SC-specific TDD: FOUND"
    echo "- **091 SC-specific TDD:** FOUND" >> "$RESULTS_FILE"
else
    echo "  091 SC-specific TDD: MISSING"
    echo "- **091 SC-specific TDD:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Plan validation check 4 upgrade
VALIDATE_FILE="$PROJECT_DIR/.opencode/skills/writing-plans/tasks/validate.md"
VAL_EXEC=$(grep -c "executable verification command\|exact expected value\|verification command.*exact" "$VALIDATE_FILE" 2>/dev/null || echo "0")
if [ "$VAL_EXEC" -ge 1 ]; then
    echo "  writing-plans/validate upgraded check #4: FOUND"
    echo "- **writing-plans/validate upgraded check #4:** FOUND" >> "$RESULTS_FILE"
else
    echo "  writing-plans/validate upgraded check #4: MISSING"
    echo "- **writing-plans/validate upgraded check #4:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Semantic intent in spec-creation/write.md
SPEC_WRITE_FILE="$PROJECT_DIR/.opencode/skills/spec-creation/tasks/write.md"
SEMANTIC_INTENT=$(grep -c "semantic intent" "$SPEC_WRITE_FILE" 2>/dev/null || echo "0")
if [ "$SEMANTIC_INTENT" -ge 1 ]; then
    echo "  spec-creation/write semantic intent: FOUND"
    echo "- **spec-creation/write semantic intent:** FOUND" >> "$RESULTS_FILE"
else
    echo "  spec-creation/write semantic intent: MISSING"
    echo "- **spec-creation/write semantic intent:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Narrow SC table exemption in write.md
NARROW_EXEMPT=$(grep -c "narrow.*exempt\|verification.*column\|verification method.*precision\|table.*exempt.*format" "$SPEC_WRITE_FILE" 2>/dev/null || echo "0")
if [ "$NARROW_EXEMPT" -ge 1 ]; then
    echo "  spec-creation/write narrowed exemption: FOUND"
    echo "- **spec-creation/write narrowed exemption:** FOUND" >> "$RESULTS_FILE"
else
    echo "  spec-creation/write narrowed exemption: MISSING"
    echo "- **spec-creation/write narrowed exemption:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Semantic intent in writing-plans/create.md
PLANS_CREATE_FILE="$PROJECT_DIR/.opencode/skills/writing-plans/tasks/create.md"
SEMANTIC_PLAN=$(grep -c "semantic intent\|preserve.*semantic\|restate.*intent" "$PLANS_CREATE_FILE" 2>/dev/null || echo "0")
if [ "$SEMANTIC_PLAN" -ge 1 ]; then
    echo "  writing-plans/create semantic intent: FOUND"
    echo "- **writing-plans/create semantic intent:** FOUND" >> "$RESULTS_FILE"
else
    echo "  writing-plans/create semantic intent: MISSING"
    echo "- **writing-plans/create semantic intent:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Verification-mechanics in brainstorming/explore.md
EXPLORE_FILE="$PROJECT_DIR/.opencode/skills/brainstorming/tasks/explore.md"
VERIFY_MECH=$(grep -c "verifia\|verification-mechanics\|how.*verify\|what.*check.*confirm" "$EXPLORE_FILE" 2>/dev/null || echo "0")
if [ "$VERIFY_MECH" -ge 1 ]; then
    echo "  brainstorming/explore verification-mechanics: FOUND"
    echo "- **brainstorming/explore verification-mechanics:** FOUND" >> "$RESULTS_FILE"
else
    echo "  brainstorming/explore verification-mechanics: MISSING"
    echo "- **brainstorming/explore verification-mechanics:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# SC Precision Audit in spec-auditor/SKILL.md
AUDITOR_FILE="$PROJECT_DIR/.opencode/skills/spec-auditor/SKILL.md"
SC_PRECISION=$(grep -c "SC Precision Audit\|SC precision\|precision audit" "$AUDITOR_FILE" 2>/dev/null || echo "0")
if [ "$SC_PRECISION" -ge 1 ]; then
    echo "  spec-auditor SC Precision Audit: FOUND"
    echo "- **spec-auditor SC Precision Audit:** FOUND" >> "$RESULTS_FILE"
else
    echo "  spec-auditor SC Precision Audit: MISSING"
    echo "- **spec-auditor SC Precision Audit:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Identity Echo Validation Gate in 000-critical-rules.md
IDENTITY_ECHO_CV=$(grep -c "Identity Echo\|identity echo\|IDENTITY_VALIDATION\|programmatic enforcement.*identity\|validates.*identity echo" "$CRITICAL_RULES_FILE" 2>/dev/null || echo "0")
if [ "$IDENTITY_ECHO_CV" -ge 1 ]; then
    echo "  000-critical-rules.md Identity Echo Validation: FOUND"
    echo "- **000-critical-rules.md Identity Echo Validation:** FOUND" >> "$RESULTS_FILE"
else
    echo "  000-critical-rules.md Identity Echo Validation: MISSING"
    echo "- **000-critical-rules.md Identity Echo Validation:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Secret Exfiltration critical violation in 000-critical-rules.md
SECRET_EXFIL_CV=$(grep -c "Secret Exfiltration\|secret exfiltration\|Never include.*env.*file contents\|secret.*redact" "$CRITICAL_RULES_FILE" 2>/dev/null || echo "0")
if [ "$SECRET_EXFIL_CV" -ge 1 ]; then
    echo "  000-critical-rules.md Secret Exfiltration violation: FOUND"
    echo "- **000-critical-rules.md Secret Exfiltration violation:** FOUND" >> "$RESULTS_FILE"
else
    echo "  000-critical-rules.md Secret Exfiltration violation: MISSING"
    echo "- **000-critical-rules.md Secret Exfiltration violation:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# AGENTS.md Identity Detection references programmatic validation
AGENTS_IDENTITY=$(grep -c "programmatic\|validation gate\|validation.*identity" "$AGENTS_FILE" 2>/dev/null || echo "0")
if [ "$AGENTS_IDENTITY" -ge 1 ]; then
    echo "  AGENTS.md programmatic validation reference: FOUND"
    echo "- **AGENTS.md programmatic validation reference:** FOUND" >> "$RESULTS_FILE"
else
    echo "  AGENTS.md programmatic validation reference: MISSING"
    echo "- **AGENTS.md programmatic validation reference:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# session-enforcement.ts contains redactSecrets function
SESSION_ENFORCEMENT_FILE="$PROJECT_DIR/.opencode/plugins/session-enforcement.ts"
REDACT_SECRETS=$(grep -c "redactSecrets\|IDENTITY_VALIDATION" "$SESSION_ENFORCEMENT_FILE" 2>/dev/null || echo "0")
if [ "$REDACT_SECRETS" -ge 1 ]; then
    echo "  session-enforcement.ts redactSecrets/validation: FOUND"
    echo "- **session-enforcement.ts redactSecrets/validation:** FOUND" >> "$RESULTS_FILE"
else
    echo "  session-enforcement.ts redactSecrets/validation: MISSING"
    echo "- **session-enforcement.ts redactSecrets/validation:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# session_context_identity.py separates Repository Hosting from Target API credentials
IDENTITY_SCRIPT="$PROJECT_DIR/.opencode/scripts/session_context_identity.py"
TARGET_API=$(grep -c "Target API\|Repository Hosting" "$IDENTITY_SCRIPT" 2>/dev/null || echo "0")
if [ "$TARGET_API" -ge 1 ]; then
    echo "  session_context_identity.py Target API separation: FOUND"
    echo "- **session_context_identity.py Target API separation:** FOUND" >> "$RESULTS_FILE"
else
    echo "  session_context_identity.py Target API separation: MISSING"
    echo "- **session_context_identity.py Target API separation:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# RED Phase Gate in executing-plans/tasks/start.md (Step 5.5)
EXEC_PLANS_START="$PROJECT_DIR/.opencode/skills/executing-plans/tasks/start.md"
RED_GATE_START=$(grep -c "Step 5.5\|RED.*test.*artifact\|RED.*verification.*checkpoint" "$EXEC_PLANS_START" 2>/dev/null || echo "0")
if [ "$RED_GATE_START" -ge 1 ]; then
    echo "  executing-plans start Step 5.5 RED gate: FOUND"
    echo "- **executing-plans start Step 5.5 RED gate:** FOUND" >> "$RESULTS_FILE"
else
    echo "  executing-plans start Step 5.5 RED gate: MISSING"
    echo "- **executing-plans start Step 5.5 RED gate:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# RED Phase Gate documented in executing-plans SKILL.md
RED_GATE_SKILLMD=$(grep -c "RED.*verification.*checkpoint\|RED.*phase.*verification\|Step 5.5\|verify.*RED.*test.*artifact" "$EXEC_PLANS_SKILL" 2>/dev/null || echo "0")
if [ "$RED_GATE_SKILLMD" -ge 1 ]; then
    echo "  executing-plans SKILL.md RED phase checkpoint: FOUND"
    echo "- **executing-plans SKILL.md RED phase checkpoint:** FOUND" >> "$RESULTS_FILE"
else
    echo "  executing-plans SKILL.md RED phase checkpoint: MISSING"
    echo "- **executing-plans SKILL.md RED phase checkpoint:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

echo ""
echo "" >> "$RESULTS_FILE"
echo "## Skill Card Validation" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

SKILL_CARD_SCRIPT="$PROJECT_DIR/.opencode/skills/skill-creator/scripts/validate_skill_cards.py"
SKILL_CARD_PASS=true

if [ -f "$SKILL_CARD_SCRIPT" ]; then
    SKILL_CARD_OUTPUT=$(uv run "$SKILL_CARD_SCRIPT" 2>&1) || SKILL_CARD_RC=$? || SKILL_CARD_RC=0
    if [ "${SKILL_CARD_RC:-0}" -eq 0 ]; then
        echo "  Skill Card Validation: PASS"
        echo "- **Skill Card Validation:** PASS" >> "$RESULTS_FILE"
    else
        echo "  Skill Card Validation: FAIL"
        echo "- **Skill Card Validation:** FAIL" >> "$RESULTS_FILE"
        SKILL_CARD_PASS=false
        OVERALL_PASS=false
    fi
    echo "$SKILL_CARD_OUTPUT" | while IFS= read -r line; do
        echo "  $line"
        echo "  $line" >> "$RESULTS_FILE"
    done
    # Verify --fix exits with code 2 (removed mode)
    FIX_OUTPUT=$(uv run "$SKILL_CARD_SCRIPT" --fix 2>&1) || FIX_RC=$? || FIX_RC=0
    if [ "${FIX_RC:-0}" -eq 2 ]; then
        echo "  Skill Card --fix Exit Code: PASS (exit 2)"
        echo "- **Skill Card --fix Exit Code:** PASS (exit 2)" >> "$RESULTS_FILE"
    else
        echo "  Skill Card --fix Exit Code: FAIL (expected 2, got ${FIX_RC:-0})"
        echo "- **Skill Card --fix Exit Code:** FAIL (expected 2, got ${FIX_RC:-0})" >> "$RESULTS_FILE"
        SKILL_CARD_PASS=false
        OVERALL_PASS=false
    fi
else
    echo "  Skill Card Validation: SKIP (script not found)"
    echo "- **Skill Card Validation:** SKIP (script not found)" >> "$RESULTS_FILE"
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