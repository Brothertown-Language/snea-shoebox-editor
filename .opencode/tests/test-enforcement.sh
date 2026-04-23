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

SCENARIO_FILTER=()
TAG_FILTER=()
CHANGED_FILTER=false
BASE_BRANCH="dev"
LIST_ONLY=false
LIST_TAGS_ONLY=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --scenario)
            SCENARIO_FILTER+=("$2")
            shift 2
            ;;
        --tag)
            TAG_FILTER+=("$2")
            shift 2
            ;;
        --changed)
            CHANGED_FILTER=true
            shift
            ;;
        --base)
            BASE_BRANCH="$2"
            shift 2
            ;;
        --list)
            LIST_ONLY=true
            shift
            ;;
        --list-tags)
            LIST_TAGS_ONLY=true
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: bash .opencode/tests/test-enforcement.sh [--scenario NAME]... [--tag TAG]... [--changed] [--base BRANCH] [--list] [--list-tags]" >&2
            exit 1
            ;;
    esac
done

LOGDIR="$PROJECT_DIR/.opencode/tmp/enforcement-test-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$LOGDIR"

TIMEOUT=120
MODEL="${ENFORCEMENT_TEST_MODEL:-ollama-cloud/glm-5.1}"
WITH_TEST_HOME="$PROJECT_DIR/.opencode/tests/with-test-home"

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
SCENARIOS["red-phase-gate-writing-plans"]="Does .opencode/skills/writing-plans/tasks/create.md contain an explicit RED verification checkpoint between test writing and implementation that requires tool-call evidence of test failure?"
SCENARIOS["red-phase-gate-writing-plans-skillmd"]="Does .opencode/skills/writing-plans/SKILL.md document that plans must include RED verification checkpoints (Step 2) between writing the test and implementing?"
SCENARIOS["red-phase-enforcement-incremental-build"]="Does .opencode/guidelines/091-incremental-build.md contain an Enforcement Mechanism section requiring RED test verification before implementation?"
SCENARIOS["red-phase-enforcement-critical-rules-xref"]="Does .opencode/guidelines/000-critical-rules.md reference the Enforcement Mechanism section in 091-incremental-build.md for RED phase verification?"
SCENARIOS["dispatch-chain-enforcement-gate"]="Does .opencode/skills/approval-gate/SKILL.md contain an Enforcement checkpoint rules section in the Dispatch Order that requires verification of each mandatory step's output artifacts with specific artifact types and evidence requirements?"
SCENARIOS["dispatch-artifact-requirements"]="Does .opencode/guidelines/000-critical-rules.md §Bypassing Mandatory Skill Invocations contain artifact verification requirements referencing specific output artifacts for each dispatch chain step?"
SCENARIOS["review-prep-format-self-check"]="Does .opencode/skills/git-workflow/tasks/review-prep.md contain a Format verification section that requires checking URL label context, URL format context, and element ordering before sending chat output?"
SCENARIOS["checklist-chat-output-format"]="Does .opencode/skills/finishing-a-development-branch/tasks/checklist.md contain a Chat Output Format section that requires verifying executive summary, outcome, URL label, URL presence, AI byline, and correct ordering?"
SCENARIOS["dispatch-checkpoint-live-verification"]="Does .opencode/skills/approval-gate/SKILL.md contain an evidence requirement that mandates tool-call artifact evidence for each dispatch chain verification gate?"
SCENARIOS["spec-creation-red-gate"]="Does .opencode/skills/spec-creation/tasks/write.md contain a Step 0.5 RED Gate requiring enforcement test assertions verified in RED state before spec assembly?"
SCENARIOS["analyze-and-spec-red-gate"]="Does .opencode/skills/issue-review/tasks/analyze-and-spec.md contain a Step 4.1 RED Gate requiring enforcement test assertions verified in RED state before fix spec sub-issue creation?"
SCENARIOS["ui-engineer-red-gate"]="Does .opencode/skills/ui-engineer/tasks/implement.md contain a Step 0.5 RED Gate requiring enforcement test assertions verified in RED state before UI implementation?"
SCENARIOS["gap-fill-precedence-principle"]="Does .opencode/skills/approval-gate/tasks/verify-authorization.md contain a Gap-Fill Precedence Principle section stating that when authorization_scope gap-fill actions cover a missing artifact requirement it is a gap-fill trigger not a blocking gate?"
SCENARIOS["gap-fill-precedence-for-pr"]="Does .opencode/skills/approval-gate/tasks/verify-authorization.md Gap-Fill Precedence Principle section explicitly state that for_pr scope with auto_create_spec means a bug report missing fix spec is a gap-fill trigger not a blocking gate?"
SCENARIOS["gap-fill-precedence-standard-scope"]="Does .opencode/skills/approval-gate/tasks/verify-authorization.md Gap-Fill Precedence Principle section state that standard scope without auto_create_spec means a bug report missing fix spec remains a blocking gate?"
SCENARIOS["screen-issue-gap-fill-awareness"]="Does .opencode/skills/approval-gate/tasks/screen-issue.md contain a note that screening sub-agents must not block on missing specs when authorization_scope gap-fill actions include auto_create_spec?"
SCENARIOS["gap-fill-precedence-before-step5c"]="Does .opencode/skills/approval-gate/tasks/verify-authorization.md place the Gap-Fill Precedence Principle before Step 5c so it is evaluated before blocking gates?"
SCENARIOS["cleanup-sc-verification-gate"]="Does .opencode/skills/git-workflow/tasks/cleanup.md contain a Step 2.6 SC-Verification Gate that verifies success criteria before closing any issue?"
SCENARIOS["cleanup-phase-completion-gate"]="Does .opencode/skills/git-workflow/tasks/cleanup.md contain a Step 2.6.5 Phase-Completion Gate that prevents closing multi-phase specs after partial merges?"
SCENARIOS["scope-next-phase-resolution"]="Does .opencode/skills/approval-gate/enforcement/scope-parsing.md contain a Next Phase Resolution section with resolve_next_phase logic?"
SCENARIOS["scope-phase-n-resolution"]="Does .opencode/skills/approval-gate/enforcement/scope-parsing.md contain an Approved for Phase N Resolution section with resolve_phase_n logic?"

# Tags per scenario for --tag filtering
declare -A SCENARIO_TAGS
SCENARIO_TAGS["bug-report"]="skill-invocation debugging"
SCENARIO_TAGS["create-spec"]="skill-invocation brainstorming"
SCENARIO_TAGS["simple-question"]="skill-invocation"
SCENARIO_TAGS["implement-request"]="skill-invocation approval"
SCENARIO_TAGS["post-merge-cleanup"]="skill-invocation git-workflow"
SCENARIO_TAGS["symptom-patch"]="skill-invocation issue-review"
SCENARIO_TAGS["incremental-build-guideline"]="content-verification incremental-build"
SCENARIO_TAGS["monolithic-implementation-violation"]="content-verification incremental-build"
SCENARIO_TAGS["item-decomposition-step"]="content-verification incremental-build"
SCENARIO_TAGS["brainstorming-top-down"]="content-verification incremental-build"
SCENARIO_TAGS["writing-plans-bottom-up"]="content-verification incremental-build"
SCENARIO_TAGS["executing-plans-tdd"]="content-verification incremental-build"
SCENARIO_TAGS["divide-conquer-tdd"]="content-verification incremental-build"
SCENARIO_TAGS["agents-md-incremental"]="content-verification incremental-build"
SCENARIO_TAGS["worktree-handoff-step"]="content-verification git-workflow"
SCENARIO_TAGS["scope-auto-resolve-guideline"]="content-verification approval"
SCENARIO_TAGS["scope-auto-resolve-step"]="content-verification approval"
SCENARIO_TAGS["worktree-mandate"]="skill-invocation worktree"
SCENARIO_TAGS["offer-to-edit-bypass"]="skill-invocation brainstorming"
SCENARIO_TAGS["bug-discovery-no-auth"]="skill-invocation debugging"
SCENARIO_TAGS["confirmation-not-auth"]="skill-invocation"
SCENARIO_TAGS["pipeline-scoped-halt"]="skill-invocation approval"
SCENARIO_TAGS["silent-halt-with-search"]="skill-invocation brainstorming"
SCENARIO_TAGS["pr-creation-guard"]="skill-invocation"
SCENARIO_TAGS["post-implementation-format"]="skill-invocation verification"
SCENARIO_TAGS["sub-issue-structure"]="skill-invocation issue-operations"
SCENARIO_TAGS["read-comments-before-action"]="skill-invocation"
SCENARIO_TAGS["per-sc-evidence-table"]="content-verification verification"
SCENARIO_TAGS["vbc-per-sc-evidence-skill"]="content-verification verification"
SCENARIO_TAGS["finishing-sc-verification"]="content-verification verification"
SCENARIO_TAGS["sc-to-test-traceability"]="content-verification sc-precision"
SCENARIO_TAGS["red-phase-ordering"]="content-verification sc-precision"
SCENARIO_TAGS["sc-traceability-example"]="content-verification sc-precision"
SCENARIO_TAGS["approval-gate-sc-traceability"]="content-verification approval sc-precision"
SCENARIO_TAGS["approval-gate-red-phase"]="content-verification approval sc-precision"
SCENARIO_TAGS["executable-verification-commands"]="content-verification sc-precision"
SCENARIO_TAGS["vague-verification-antipattern"]="content-verification sc-precision"
SCENARIO_TAGS["sc-assertion-tdd-cycle"]="content-verification incremental-build"
SCENARIO_TAGS["red-state-before-implementation"]="content-verification incremental-build"
SCENARIO_TAGS["validate-executable-verification"]="content-verification writing-plans"
SCENARIO_TAGS["semantic-intent-spec-creation"]="content-verification spec-creation"
SCENARIO_TAGS["narrow-sc-table-exemption"]="content-verification spec-creation"
SCENARIO_TAGS["semantic-intent-writing-plans"]="content-verification writing-plans"
SCENARIO_TAGS["why-specific-value-tdd"]="content-verification writing-plans"
SCENARIO_TAGS["verification-mechanics-brainstorming"]="content-verification brainstorming"
SCENARIO_TAGS["sc-precision-audit"]="content-verification spec-auditor sc-precision"
SCENARIO_TAGS["url-sourcing-rule1-pr"]="content-verification git-workflow url-sourcing"
SCENARIO_TAGS["url-sourcing-rule1-review-prep"]="content-verification git-workflow url-sourcing"
SCENARIO_TAGS["url-sourcing-rule2-character-match"]="content-verification git-workflow url-sourcing"
SCENARIO_TAGS["url-sourcing-guideline-rules"]="content-verification url-sourcing"
SCENARIO_TAGS["url-sourcing-issue-operations"]="content-verification issue-operations url-sourcing"
SCENARIO_TAGS["identity-echo-validation"]="content-verification session-enforcement"
SCENARIO_TAGS["secret-exfiltration-violation"]="content-verification session-enforcement"
SCENARIO_TAGS["read-secrets-in-output"]="skill-invocation session-enforcement"
SCENARIO_TAGS["red-phase-gate-executing-plans"]="content-verification incremental-build"
SCENARIO_TAGS["red-phase-gate-skillmd"]="content-verification incremental-build"
SCENARIO_TAGS["red-phase-gate-writing-plans"]="content-verification writing-plans"
SCENARIO_TAGS["red-phase-gate-writing-plans-skillmd"]="content-verification writing-plans"
SCENARIO_TAGS["red-phase-enforcement-incremental-build"]="content-verification incremental-build"
SCENARIO_TAGS["red-phase-enforcement-critical-rules-xref"]="content-verification incremental-build"
SCENARIO_TAGS["dispatch-chain-enforcement-gate"]="content-verification approval"
SCENARIO_TAGS["dispatch-artifact-requirements"]="content-verification approval"
SCENARIO_TAGS["review-prep-format-self-check"]="content-verification git-workflow"
SCENARIO_TAGS["checklist-chat-output-format"]="content-verification verification"
SCENARIO_TAGS["dispatch-checkpoint-live-verification"]="content-verification approval"
SCENARIO_TAGS["spec-creation-red-gate"]="content-verification spec-creation"
SCENARIO_TAGS["analyze-and-spec-red-gate"]="content-verification issue-review"
SCENARIO_TAGS["ui-engineer-red-gate"]="content-verification ui-engineer"
SCENARIO_TAGS["gap-fill-precedence-principle"]="content-verification approval"
SCENARIO_TAGS["gap-fill-precedence-for-pr"]="content-verification approval"
SCENARIO_TAGS["gap-fill-precedence-standard-scope"]="content-verification approval"
SCENARIO_TAGS["screen-issue-gap-fill-awareness"]="content-verification approval"
SCENARIO_TAGS["gap-fill-precedence-before-step5c"]="content-verification approval"
SCENARIO_TAGS["cleanup-sc-verification-gate"]="content-verification git-workflow"
SCENARIO_TAGS["cleanup-phase-completion-gate"]="content-verification git-workflow"
SCENARIO_TAGS["scope-next-phase-resolution"]="content-verification approval"
SCENARIO_TAGS["scope-phase-n-resolution"]="content-verification approval"
SCENARIO_TAGS["enforcement-module-adversarial"]="content-verification enforcement-module"
SCENARIO_TAGS["enforcement-module-scope-parsing"]="content-verification enforcement-module"
SCENARIO_TAGS["enforcement-module-auto-dispatch"]="content-verification enforcement-module"
SCENARIO_TAGS["enforcement-module-closed-issue"]="content-verification enforcement-module"
SCENARIO_TAGS["enforcement-module-sub-issue"]="content-verification enforcement-module"
SCENARIO_TAGS["enforcement-module-completion"]="content-verification enforcement-module"
SCENARIO_TAGS["enforcement-module-result-validation"]="content-verification enforcement-module"
SCENARIO_TAGS["enforcement-module-overflow"]="content-verification enforcement-module"
SCENARIO_TAGS["enforcement-module-work-state"]="content-verification enforcement-module"
SCENARIO_TAGS["task-file-enforcement-refs"]="content-verification approval"
SCENARIO_TAGS["dev-edit-guard-plugin"]="content-verification session-enforcement"
SCENARIO_TAGS["dev-edit-guard-trigger"]="content-verification session-enforcement"
SCENARIO_TAGS["dev-edit-guard-pair-mode"]="content-verification session-enforcement"

# File-to-scenario mapping for --changed filtering
# Maps glob patterns to scenario names
declare -A FILE_SCENARIO_MAP
FILE_SCENARIO_MAP[".opencode/guidelines/091-incremental-build.md"]="incremental-build-guideline monolithic-implementation-violation item-decomposition-step sc-assertion-tdd-cycle red-state-before-implementation red-phase-enforcement-incremental-build red-phase-enforcement-critical-rules-xref"
FILE_SCENARIO_MAP[".opencode/guidelines/000-critical-rules.md"]="scope-auto-resolve-guideline monolithic-implementation-violation identity-echo-validation secret-exfiltration-violation url-sourcing-guideline-rules dispatch-artifact-requirements red-phase-enforcement-critical-rules-xref"
FILE_SCENARIO_MAP[".opencode/guidelines/020-go-prohibitions.md"]="scope-auto-resolve-guideline pipeline-scoped-halt"
FILE_SCENARIO_MAP[".opencode/skills/approval-gate/"]="item-decomposition-step scope-auto-resolve-step approval-gate-sc-traceability approval-gate-red-phase dispatch-chain-enforcement-gate dispatch-artifact-requirements dispatch-checkpoint-live-verification gap-fill-precedence-principle gap-fill-precedence-for-pr gap-fill-precedence-standard-scope screen-issue-gap-fill-awareness gap-fill-precedence-before-step5c task-file-enforcement-refs scope-next-phase-resolution scope-phase-n-resolution enforcement-module-adversarial enforcement-module-scope-parsing enforcement-module-auto-dispatch enforcement-module-closed-issue enforcement-module-sub-issue"
FILE_SCENARIO_MAP[".opencode/skills/brainstorming/"]="brainstorming-top-down verification-mechanics-brainstorming"
FILE_SCENARIO_MAP[".opencode/skills/writing-plans/"]="writing-plans-bottom-up validate-executable-verification semantic-intent-writing-plans why-specific-value-tdd red-phase-gate-writing-plans red-phase-gate-writing-plans-skillmd"
FILE_SCENARIO_MAP[".opencode/skills/executing-plans/"]="executing-plans-tdd red-phase-gate-executing-plans red-phase-gate-skillmd"
FILE_SCENARIO_MAP[".opencode/skills/divide-and-conquer/"]="divide-conquer-tdd enforcement-module-completion enforcement-module-result-validation enforcement-module-overflow enforcement-module-work-state"
FILE_SCENARIO_MAP[".opencode/skills/git-workflow/"]="worktree-handoff-step cleanup-sc-verification-gate cleanup-phase-completion-gate review-prep-format-self-check url-sourcing-rule1-review-prep url-sourcing-rule1-pr url-sourcing-rule2-character-match"
FILE_SCENARIO_MAP[".opencode/skills/verification-before-completion/"]="per-sc-evidence-table vbc-per-sc-evidence-skill"
FILE_SCENARIO_MAP[".opencode/skills/finishing-a-development-branch/"]="finishing-sc-verification checklist-chat-output-format"
FILE_SCENARIO_MAP[".opencode/guidelines/080-code-standards.md"]="sc-to-test-traceability red-phase-ordering sc-traceability-example"
FILE_SCENARIO_MAP[".opencode/guidelines/140-planning-spec-creation.md"]="executable-verification-commands vague-verification-antipattern"
FILE_SCENARIO_MAP[".opencode/skills/spec-creation/"]="semantic-intent-spec-creation narrow-sc-table-exemption spec-creation-red-gate"
FILE_SCENARIO_MAP[".opencode/skills/spec-auditor/"]="sc-precision-audit"
FILE_SCENARIO_MAP[".opencode/skills/issue-operations/"]="sub-issue-structure url-sourcing-issue-operations"
FILE_SCENARIO_MAP[".opencode/skills/issue-review/"]="analyze-and-spec-red-gate"
FILE_SCENARIO_MAP[".opencode/skills/ui-engineer/"]="ui-engineer-red-gate"
FILE_SCENARIO_MAP[".opencode/skills/session-enforcement.ts"]="identity-echo-validation secret-exfiltration-violation read-secrets-in-output dev-edit-guard-plugin dev-edit-guard-pair-mode"
FILE_SCENARIO_MAP[".opencode/plugins/session-enforcement.ts"]="identity-echo-validation secret-exfiltration-violation dev-edit-guard-plugin dev-edit-guard-pair-mode"
FILE_SCENARIO_MAP[".opencode/scripts/session_context_identity.py"]="identity-echo-validation"
FILE_SCENARIO_MAP[".opencode/scripts/session_context_triggers.py"]="dev-edit-guard-trigger"
FILE_SCENARIO_MAP["AGENTS.md"]="agents-md-incremental"

# --list: print scenario names and exit
if [ "$LIST_ONLY" = true ]; then
    for name in $(echo "${!SCENARIOS[@]}" | tr ' ' '\n' | sort); do
        echo "$name"
    done
    exit 0
fi

# --list-tags: print tag names and exit
if [ "$LIST_TAGS_ONLY" = true ]; then
    declare -A ALL_TAGS
    for name in "${!SCENARIO_TAGS[@]}"; do
        for tag in ${SCENARIO_TAGS[$name]}; do
            ALL_TAGS[$tag]=1
        done
    done
    for tag in $(echo "${!ALL_TAGS[@]}" | tr ' ' '\n' | sort); do
        echo "$tag"
    done
    exit 0
fi

# Build filtered scenario list
SCENARIO_NAMES=($(echo "${!SCENARIOS[@]}" | tr ' ' '\n' | sort))
FILTERED_SCENARIOS=()

if [ ${#SCENARIO_FILTER[@]} -gt 0 ] || [ ${#TAG_FILTER[@]} -gt 0 ] || [ "$CHANGED_FILTER" = true ]; then
    for name in "${SCENARIO_NAMES[@]}"; do
        INCLUDE=false
        if [ ${#SCENARIO_FILTER[@]} -gt 0 ]; then
            for filter_name in "${SCENARIO_FILTER[@]}"; do
                if [ "$name" = "$filter_name" ]; then
                    INCLUDE=true
                    break
                fi
            done
        fi
        if [ ${#TAG_FILTER[@]} -gt 0 ]; then
            TAGS_FOR="${SCENARIO_TAGS[$name]:-}"
            for filter_tag in "${TAG_FILTER[@]}"; do
                for tag in $TAGS_FOR; do
                    if [ "$tag" = "$filter_tag" ]; then
                        INCLUDE=true
                        break 2
                    fi
                done
            done
        fi
        if [ "$CHANGED_FILTER" = true ]; then
            for file_glob in "${!FILE_SCENARIO_MAP[@]}"; do
                CHANGED=$(git diff --name-only "$BASE_BRANCH" -- "$file_glob" 2>/dev/null || true)
                if [ -n "$CHANGED" ]; then
                    for scenario_name in ${FILE_SCENARIO_MAP[$file_glob]}; do
                        if [ "$name" = "$scenario_name" ]; then
                            INCLUDE=true
                            break 2
                        fi
                    done
                fi
            done
        fi
        if [ "$INCLUDE" = true ]; then
            FILTERED_SCENARIOS+=("$name")
        fi
    done

    if [ ${#FILTERED_SCENARIOS[@]} -eq 0 ]; then
        if [ ${#SCENARIO_FILTER[@]} -gt 0 ]; then
            echo "ERROR: Unknown scenario: ${SCENARIO_FILTER[*]}" >&2
            echo "Run with --list to see available scenarios." >&2
            exit 1
        fi
        if [ ${#TAG_FILTER[@]} -gt 0 ]; then
            echo "ERROR: Unknown tag: ${TAG_FILTER[*]}" >&2
            echo "Run with --list-tags to see available tags." >&2
            exit 1
        fi
        echo "No scenarios matched --changed filter (no relevant files changed against $BASE_BRANCH)." >&2
        exit 0
    fi

    SCENARIO_NAMES=("${FILTERED_SCENARIOS[@]}")
fi

# Validate --scenario names
for filter_name in "${SCENARIO_FILTER[@]}"; do
    FOUND=false
    for name in "${!SCENARIOS[@]}"; do
        if [ "$name" = "$filter_name" ]; then
            FOUND=true
            break
        fi
    done
    if [ "$FOUND" = false ]; then
        echo "ERROR: Unknown scenario '$filter_name'" >&2
        echo "Run with --list to see available scenarios." >&2
        exit 1
    fi
done

# Validate --tag names
for filter_tag in "${TAG_FILTER[@]}"; do
    FOUND=false
    for name in "${!SCENARIO_TAGS[@]}"; do
        for tag in ${SCENARIO_TAGS[$name]}; do
            if [ "$tag" = "$filter_tag" ]; then
                FOUND=true
                break 2
            fi
        done
    done
    if [ "$FOUND" = false ]; then
        echo "ERROR: Unknown tag '$filter_tag'" >&2
        echo "Run with --list-tags to see available tags." >&2
        exit 1
    fi
done

TOTAL_SCENARIOS=${#SCENARIOS[@]}
RUN_COUNT=${#SCENARIO_NAMES[@]}

echo "=== Enforcement Integration Test ==="
echo "Log dir: $LOGDIR"
echo "Model: $MODEL"
echo "Mode: isolated (with-test-home wrapper)"
echo "Scenarios: $RUN_COUNT / $TOTAL_SCENARIOS"
echo ""
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
EXPECTED_SKILLS["red-phase-gate-writing-plans"]=""
EXPECTED_SKILLS["red-phase-gate-writing-plans-skillmd"]=""
EXPECTED_SKILLS["red-phase-enforcement-incremental-build"]=""
EXPECTED_SKILLS["red-phase-enforcement-critical-rules-xref"]=""
EXPECTED_SKILLS["dispatch-chain-enforcement-gate"]=""
EXPECTED_SKILLS["dispatch-artifact-requirements"]=""
EXPECTED_SKILLS["review-prep-format-self-check"]=""
EXPECTED_SKILLS["checklist-chat-output-format"]=""
EXPECTED_SKILLS["dispatch-checkpoint-live-verification"]=""
EXPECTED_SKILLS["spec-creation-red-gate"]=""
EXPECTED_SKILLS["analyze-and-spec-red-gate"]=""
EXPECTED_SKILLS["ui-engineer-red-gate"]=""
EXPECTED_SKILLS["gap-fill-precedence-principle"]=""
EXPECTED_SKILLS["gap-fill-precedence-for-pr"]=""
EXPECTED_SKILLS["gap-fill-precedence-standard-scope"]=""
EXPECTED_SKILLS["screen-issue-gap-fill-awareness"]=""
EXPECTED_SKILLS["gap-fill-precedence-before-step5c"]=""
EXPECTED_SKILLS["cleanup-sc-verification-gate"]=""
EXPECTED_SKILLS["cleanup-phase-completion-gate"]=""
EXPECTED_SKILLS["scope-next-phase-resolution"]=""
EXPECTED_SKILLS["scope-phase-n-resolution"]=""
EXPECTED_SKILLS["enforcement-module-adversarial"]=""
EXPECTED_SKILLS["enforcement-module-scope-parsing"]=""
EXPECTED_SKILLS["enforcement-module-auto-dispatch"]=""
EXPECTED_SKILLS["enforcement-module-closed-issue"]=""
EXPECTED_SKILLS["enforcement-module-sub-issue"]=""
EXPECTED_SKILLS["enforcement-module-completion"]=""
EXPECTED_SKILLS["enforcement-module-result-validation"]=""
EXPECTED_SKILLS["enforcement-module-overflow"]=""
EXPECTED_SKILLS["enforcement-module-work-state"]=""
EXPECTED_SKILLS["task-file-enforcement-refs"]=""
EXPECTED_SKILLS["dev-edit-guard-plugin"]=""
EXPECTED_SKILLS["dev-edit-guard-trigger"]=""
EXPECTED_SKILLS["dev-edit-guard-pair-mode"]=""

RESULTS_FILE="$LOGDIR/results.md"

echo "# Enforcement Integration Test Results" > "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "Date: $(date -Iseconds)" >> "$RESULTS_FILE"
echo "Model: $MODEL" >> "$RESULTS_FILE"
echo "Mode: isolated (with-test-home)" >> "$RESULTS_FILE"
echo "Scenarios run: $RUN_COUNT / $TOTAL_SCENARIOS" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

OVERALL_PASS=true

for scenario_name in "${SCENARIO_NAMES[@]}"; do
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
echo "- **Scenarios run:** $RUN_COUNT / $TOTAL_SCENARIOS" >> "$RESULTS_FILE"
echo "- **Plugin infrastructure loaded:** Verified per-scenario from run logs" >> "$RESULTS_FILE"
echo "- **Skill invocation by model:** Depends on model behavior (non-deterministic)" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

echo ""
echo "=== Scenarios Run: $RUN_COUNT / $TOTAL_SCENARIOS ==="

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

# RED Phase Gate in writing-plans/tasks/create.md (explicit RED verification checkpoint)
RED_GATE_WP_CREATE=$(grep -c "RED.*verification.*checkpoint\|Step 2.*Run test.*verify RED\|CHECKPOINT.*must produce tool-call evidence\|RED verification checkpoint\|RED.*test.*failure.*evidence" "$PLANS_CREATE_FILE" 2>/dev/null || echo "0")
if [ "$RED_GATE_WP_CREATE" -ge 1 ]; then
    echo "  writing-plans/create RED verification checkpoint: FOUND"
    echo "- **writing-plans/create RED verification checkpoint:** FOUND" >> "$RESULTS_FILE"
else
    echo "  writing-plans/create RED verification checkpoint: MISSING"
    echo "- **writing-plans/create RED verification checkpoint:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# RED Phase Gate documented in writing-plans SKILL.md
RED_GATE_WP_SKILL=$(grep -c "Step 2.*Run test.*verify RED\|RED.*verification.*checkpoint\|mandatory.*checkpoint\|must include.*RED.*verification\|Step 2.*CHECKPOINT" "$WRITING_PLANS_SKILL" 2>/dev/null || echo "0")
if [ "$RED_GATE_WP_SKILL" -ge 1 ]; then
    echo "  writing-plans SKILL.md RED verification checkpoint: FOUND"
    echo "- **writing-plans SKILL.md RED verification checkpoint:** FOUND" >> "$RESULTS_FILE"
else
    echo "  writing-plans SKILL.md RED verification checkpoint: MISSING"
    echo "- **writing-plans SKILL.md RED verification checkpoint:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# RED Phase Enforcement Mechanism in 091-incremental-build.md
RED_ENF_IB=$(grep -c "Enforcement Mechanism" "$INCBUILD_FILE" 2>/dev/null || echo "0")
if [ "$RED_ENF_IB" -ge 1 ]; then
    echo "  091 Enforcement Mechanism section: FOUND"
    echo "- **091 Enforcement Mechanism section:** FOUND" >> "$RESULTS_FILE"
else
    echo "  091 Enforcement Mechanism section: MISSING"
    echo "- **091 Enforcement Mechanism section:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# RED Phase Enforcement Mechanism content (must reference executing-plans Step 5.5 and writing-plans Step 2)
if [ "$RED_ENF_IB" -ge 1 ]; then
    RED_ENF_CONTENT=$(grep -c "executing-plans.*Step 5.5\|Step 5.5.*executing-plans\|dispatching.*divide-and-conquer.*RED" "$INCBUILD_FILE" 2>/dev/null || echo "0")
    RED_ENF_WP=$(grep -c "writing-plans.*Step 2\|plan template.*RED\|RED verification step.*tool-call evidence" "$INCBUILD_FILE" 2>/dev/null || echo "0")
    RED_ENF_GIT=$(grep -c "git log.*order\|test.*commit.*precede.*implementation.*commit" "$INCBUILD_FILE" 2>/dev/null || echo "0")
    RED_ENF_HALT=$(grep -c "HALT.*RED\|no RED test artifact\|MUST HALT" "$INCBUILD_FILE" 2>/dev/null || echo "0")
    if [ "$RED_ENF_CONTENT" -ge 1 ] && [ "$RED_ENF_WP" -ge 1 ] && [ "$RED_ENF_HALT" -ge 1 ]; then
        echo "  091 Enforcement Mechanism content: FOUND"
        echo "- **091 Enforcement Mechanism content:** FOUND" >> "$RESULTS_FILE"
    else
        echo "  091 Enforcement Mechanism content: MISSING (executing-plans ref=$RED_ENF_CONTENT, writing-plans ref=$RED_ENF_WP, git log=$RED_ENF_GIT, halt=$RED_ENF_HALT)"
        echo "- **091 Enforcement Mechanism content:** MISSING" >> "$RESULTS_FILE"
        GUIDELINE_PASS=false
        OVERALL_PASS=false
    fi
fi

# RED Phase Enforcement cross-reference in 000-critical-rules.md pointing to 091 Enforcement Mechanism
RED_ENF_XREF=$(grep -c "Enforcement Mechanism.*091\|091.*Enforcement Mechanism" "$CRITICAL_RULES_FILE" 2>/dev/null || echo "0")
if [ "$RED_ENF_XREF" -ge 1 ]; then
    echo "  000-critical-rules Enforcement Mechanism xref: FOUND"
    echo "- **000-critical-rules Enforcement Mechanism xref:** FOUND" >> "$RESULTS_FILE"
else
    echo "  000-critical-rules Enforcement Mechanism xref: MISSING"
    echo "- **000-critical-rules Enforcement Mechanism xref:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Dispatch chain enforcement gate in approval-gate SKILL.md
AGATE_SKILL_FILE="$PROJECT_DIR/.opencode/skills/approval-gate/SKILL.md"
DISPATCH_GATE=$(grep -c "Enforcement checkpoint rules.*MANDATORY\|evidence requirement.*MANDATORY\|tool-call artifact evidence" "$AGATE_SKILL_FILE" 2>/dev/null || echo "0")
if [ "$DISPATCH_GATE" -ge 1 ]; then
    echo "  dispatch chain enforcement gate with evidence: FOUND"
    echo "- **dispatch chain enforcement gate with evidence:** FOUND" >> "$RESULTS_FILE"
else
    echo "  dispatch chain enforcement gate with evidence: MISSING"
    echo "- **dispatch chain enforcement gate with evidence:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Dispatch chain artifact verification requirements in 000-critical-rules.md
DISPATCH_ARTIFACT=$(grep -c "Artifact verification.*MANDATORY\|Required Evidence Artifact" "$CRITICAL_RULES_FILE" 2>/dev/null || echo "0")
if [ "$DISPATCH_ARTIFACT" -ge 1 ]; then
    echo "  000-critical-rules dispatch artifact requirements: FOUND"
    echo "- **000-critical-rules dispatch artifact requirements:** FOUND" >> "$RESULTS_FILE"
else
    echo "  000-critical-rules dispatch artifact requirements: MISSING"
    echo "- **000-critical-rules dispatch artifact requirements:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# review-prep format self-check
REVIEW_PREP_FORMAT_FILE="$PROJECT_DIR/.opencode/skills/git-workflow/tasks/review-prep.md"
RP_FORMAT=$(grep -c "Format verification.*MANDATORY\|Chat Output Format.*MANDATORY\|format verification.*check before posting\|Live Verification.*Chat Output Format" "$REVIEW_PREP_FORMAT_FILE" 2>/dev/null || echo "0")
if [ "$RP_FORMAT" -ge 1 ]; then
    echo "  review-prep format self-check: FOUND"
    echo "- **review-prep format self-check:** FOUND" >> "$RESULTS_FILE"
else
    echo "  review-prep format self-check: MISSING"
    echo "- **review-prep format self-check:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# checklist chat output format
FINISHING_CHECKLIST_FILE="$PROJECT_DIR/.opencode/skills/finishing-a-development-branch/tasks/checklist.md"
CL_FORMAT=$(grep -c "Chat Output Format" "$FINISHING_CHECKLIST_FILE" 2>/dev/null || echo "0")
if [ "$CL_FORMAT" -ge 1 ]; then
    echo "  checklist Chat Output Format section: FOUND"
    echo "- **checklist Chat Output Format section:** FOUND" >> "$RESULTS_FILE"
else
    echo "  checklist Chat Output Format section: MISSING"
    echo "- **checklist Chat Output Format section:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Dispatch checkpoint live verification / evidence requirement in approval-gate SKILL.md
AG_EVIDENCE=$(grep -c "evidence requirement.*MANDATORY\|tool-call artifact.*evidence\|MUST.*explicitly.*invoke.*verification\|tool-call artifact.*confirm" "$AGATE_SKILL_FILE" 2>/dev/null || echo "0")
if [ "$AG_EVIDENCE" -ge 1 ]; then
    echo "  dispatch chain evidence requirement: FOUND"
    echo "- **dispatch chain evidence requirement:** FOUND" >> "$RESULTS_FILE"
else
    echo "  dispatch chain evidence requirement: MISSING"
    echo "- **dispatch chain evidence requirement:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# spec-creation RED Gate in write.md
SPEC_WRITE_RED=$(grep -c "Step 0.5.*RED Gate\|RED Gate.*Enforcement Test\|enforcement test assertions.*RED state.*before spec" "$SPEC_WRITE_FILE" 2>/dev/null || echo "0")
if [ "$SPEC_WRITE_RED" -ge 1 ]; then
    echo "  spec-creation/write RED Gate: FOUND"
    echo "- **spec-creation/write RED Gate:** FOUND" >> "$RESULTS_FILE"
else
    echo "  spec-creation/write RED Gate: MISSING"
    echo "- **spec-creation/write RED Gate:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# analyze-and-spec RED Gate in analyze-and-spec.md
ANALYZE_SPEC_FILE="$PROJECT_DIR/.opencode/skills/issue-review/tasks/analyze-and-spec.md"
ANALYZE_SPEC_RED=$(grep -c "Step 4.1.*RED Gate\|RED Gate.*Fix Spec.*Enforcement Test\|enforcement test assertions.*RED state.*before.*fix spec" "$ANALYZE_SPEC_FILE" 2>/dev/null || echo "0")
if [ "$ANALYZE_SPEC_RED" -ge 1 ]; then
    echo "  analyze-and-spec RED Gate: FOUND"
    echo "- **analyze-and-spec RED Gate:** FOUND" >> "$RESULTS_FILE"
else
    echo "  analyze-and-spec RED Gate: MISSING"
    echo "- **analyze-and-spec RED Gate:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# ui-engineer RED Gate in implement.md
UI_IMPL_FILE="$PROJECT_DIR/.opencode/skills/ui-engineer/tasks/implement.md"
UI_ENGINEER_RED=$(grep -c "Step 0.5.*RED Gate\|RED Gate.*UI.*Enforcement Test\|enforcement test assertions.*RED state.*before.*UI\|test-ui.*mandatory prerequisite\|test-ui.*MANDATORY prerequisite" "$UI_IMPL_FILE" 2>/dev/null || echo "0")
if [ "$UI_ENGINEER_RED" -ge 1 ]; then
    echo "  ui-engineer/implement RED Gate: FOUND"
    echo "- **ui-engineer/implement RED Gate:** FOUND" >> "$RESULTS_FILE"
else
    echo "  ui-engineer/implement RED Gate: MISSING"
    echo "- **ui-engineer/implement RED Gate:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

echo ""
echo "" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

# Gap-Fill Precedence Principle in verify-authorization.md
VERIFY_AUTH_FILE="$PROJECT_DIR/.opencode/skills/approval-gate/tasks/verify-authorization.md"
GAP_FILL_PRECEDENCE=$(grep -c "Gap-Fill Precedence Principle\|gap-fill trigger.*not a blocking gate\|gap-fill actions cover.*missing artifact" "$VERIFY_AUTH_FILE" 2>/dev/null || echo "0")
if [ "$GAP_FILL_PRECEDENCE" -ge 1 ]; then
    echo "  verify-authorization Gap-Fill Precedence Principle: FOUND"
    echo "- **verify-authorization Gap-Fill Precedence Principle:** FOUND" >> "$RESULTS_FILE"
else
    echo "  verify-authorization Gap-Fill Precedence Principle: MISSING"
    echo "- **verify-authorization Gap-Fill Precedence Principle:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Gap-Fill Precedence Principle explicit for_pr reference
GAP_FILL_FORPR=$(grep -c "for_pr.*auto_create_spec\|bug report.*fix spec.*gap-fill\|missing fix spec.*gap-fill trigger" "$VERIFY_AUTH_FILE" 2>/dev/null || echo "0")
if [ "$GAP_FILL_FORPR" -ge 1 ]; then
    echo "  verify-authorization gap-fill for_pr bug report: FOUND"
    echo "- **verify-authorization gap-fill for_pr bug report:** FOUND" >> "$RESULTS_FILE"
else
    echo "  verify-authorization gap-fill for_pr bug report: MISSING"
    echo "- **verify-authorization gap-fill for_pr bug report:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Gap-Fill Precedence Principle standard scope preserves blocking
GAP_FILL_STANDARD=$(grep -c "standard.*blocking\|scope.*without.*auto_create_spec.*blocking\|gap-fill.*does not cover.*blocking" "$VERIFY_AUTH_FILE" 2>/dev/null || echo "0")
if [ "$GAP_FILL_STANDARD" -ge 1 ]; then
    echo "  verify-authorization gap-fill standard scope blocking: FOUND"
    echo "- **verify-authorization gap-fill standard scope blocking:** FOUND" >> "$RESULTS_FILE"
else
    echo "  verify-authorization gap-fill standard scope blocking: MISSING"
    echo "- **verify-authorization gap-fill standard scope blocking:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# screen-issue gap-fill awareness
SCREEN_GAP_FILL=$(grep -c "gap-fill\|auto_create_spec\|authorization_scope.*gap-fill" "$PROJECT_DIR/.opencode/skills/approval-gate/tasks/screen-issue.md" 2>/dev/null || echo "0")
if [ "$SCREEN_GAP_FILL" -ge 1 ]; then
    echo "  screen-issue gap-fill awareness: FOUND"
    echo "- **screen-issue gap-fill awareness:** FOUND" >> "$RESULTS_FILE"
else
    echo "  screen-issue gap-fill awareness: MISSING"
    echo "- **screen-issue gap-fill awareness:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Gap-Fill Precedence Principle placed before Step 5c
GAP_FILL_BEFORE_5C=$(grep -n "Gap-Fill Precedence\|Step 5c" "$VERIFY_AUTH_FILE" 2>/dev/null | head -5)
GAP_FILL_LINE=$(echo "$GAP_FILL_BEFORE_5C" | grep "Gap-Fill Precedence" | head -1 | grep -oP '^\d+' || echo "0")
STEP5C_LINE=$(echo "$GAP_FILL_BEFORE_5C" | grep "Step 5c" | head -1 | grep -oP '^\d+' || echo "0")
if [ "$GAP_FILL_LINE" -gt 0 ] && [ "$STEP5C_LINE" -gt 0 ] && [ "$GAP_FILL_LINE" -lt "$STEP5C_LINE" ]; then
    echo "  verify-authorization Gap-Fill Precedence before Step 5c: FOUND"
    echo "- **verify-authorization Gap-Fill Precedence before Step 5c:** FOUND" >> "$RESULTS_FILE"
else
    echo "  verify-authorization Gap-Fill Precedence before Step 5c: MISSING"
    echo "- **verify-authorization Gap-Fill Precedence before Step 5c:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

SKILL_CARD_SCRIPT="$PROJECT_DIR/.opencode/skills/skill-creator/scripts/validate_skill_cards.py"
SKILL_CARD_PASS=true

# Cleanup SC-Verification Gate in cleanup.md
CLEANUP_FILE="$PROJECT_DIR/.opencode/skills/git-workflow/tasks/cleanup.md"
SC_GATE=$(grep -c "SC-Verification Gate\|sc_verification_gate\|Verify each success criterion" "$CLEANUP_FILE" 2>/dev/null || echo "0")
if [ "$SC_GATE" -ge 1 ]; then
    echo "  cleanup SC-Verification Gate: FOUND"
    echo "- **cleanup SC-Verification Gate:** FOUND" >> "$RESULTS_FILE"
else
    echo "  cleanup SC-Verification Gate: MISSING"
    echo "- **cleanup SC-Verification Gate:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Cleanup Phase-Completion Gate in cleanup.md
PHASE_GATE=$(grep -c "Phase-Completion Gate\|phase_completion_gate\|closing a multi-phase spec after a partial merge" "$CLEANUP_FILE" 2>/dev/null || echo "0")
if [ "$PHASE_GATE" -ge 1 ]; then
    echo "  cleanup Phase-Completion Gate: FOUND"
    echo "- **cleanup Phase-Completion Gate:** FOUND" >> "$RESULTS_FILE"
else
    echo "  cleanup Phase-Completion Gate: MISSING"
    echo "- **cleanup Phase-Completion Gate:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Next Phase Resolution in scope-parsing.md
SCOPE_PARSING_FILE="$PROJECT_DIR/.opencode/skills/approval-gate/enforcement/scope-parsing.md"
NEXT_PHASE=$(grep -c "resolve_next_phase\|Next Phase Resolution\|for_next_phase" "$SCOPE_PARSING_FILE" 2>/dev/null || echo "0")
if [ "$NEXT_PHASE" -ge 1 ]; then
    echo "  scope-parsing Next Phase Resolution: FOUND"
    echo "- **scope-parsing Next Phase Resolution:** FOUND" >> "$RESULTS_FILE"
else
    echo "  scope-parsing Next Phase Resolution: MISSING"
    echo "- **scope-parsing Next Phase Resolution:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

# Phase N Resolution in scope-parsing.md
PHASE_N=$(grep -c "resolve_phase_n\|Approved for Phase N Resolution\|for_phase_N" "$SCOPE_PARSING_FILE" 2>/dev/null || echo "0")
if [ "$PHASE_N" -ge 1 ]; then
    echo "  scope-parsing Phase N Resolution: FOUND"
    echo "- **scope-parsing Phase N Resolution:** FOUND" >> "$RESULTS_FILE"
else
    echo "  scope-parsing Phase N Resolution: MISSING"
    echo "- **scope-parsing Phase N Resolution:** MISSING" >> "$RESULTS_FILE"
    GUIDELINE_PASS=false
    OVERALL_PASS=false
fi

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
