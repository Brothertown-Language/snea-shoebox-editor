---
name: approval-gate
description: Use when user says "approved", "go", or any implementation instruction, or when authorization needs verification. Triggers on: approval, authorized, implement, start work, go ahead, needs-approval label, batch approval, multiple issues approved, interdependency analysis.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: approval-gate

## Overview

Authorization Gatekeeper ensuring all code changes follow the spec + authorization workflow. The agent MUST invoke this skill before implementation begins.

## Persona

You are an Authorization Gatekeeper. Your focus is ensuring all code changes follow the spec + authorization workflow.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `verify-qa-mode` | Detect spec-less implementation requests, switch to Q/A mode | ~800 |
| `verify-authorization` | Check explicit auth and needs-approval label; delegates branch creation to `git-workflow --task pre-work` | ~400 |
| `verify-sub-issues` | Verify sub-issue structure for multi-task specs | ~480 |
| `verify-codebase` | Re-evaluate codebase state, detect staleness | ~400 |
| `verify-already-implemented` | Check if all success criteria are already met; autoclose if so | ~400 |
| `verify-blockers` | Check for blocking issues/dependencies | ~320 |
| `verify-open-questions` | Check for unresolved questions in spec | ~370 |
| `verify-fix-spec` | For bug reports, verify fix spec sub-issue exists before closure | ~250 |
| `search-prompt-fail` | Search GitHub Issues for existing spec/plan candidates before Q/A halt; present candidates or report failure | ~300 |
| `verify-closed-issue` | Verify that a closed issue was legitimately closed via merged PR; enforce "closed ≠ verified" rule | ~350 |
| `screen-issue` | Per-issue screening for pre-implementation analysis (Gate 1 + Gate 2 + screening categories); dispatched as parallel sub-agents | ~3,000 |
| `pre-implementation-analysis` | Cross-issue merge of screening results, dependency graph, execution plan for assemble-batch | ~500 |
| `verify-schema-api-knowledge` | Verify that the agent has performed live verification before making schema/API/code claims; gate before proceeding | ~350 |
| `reconcile-issue-graph` | Act on graph traversal findings: auto-close verified-complete, reopen verified-incomplete, flag uncertain | ~600 |
| `post-implementation` | Push branch, generate compare URL, HALT | ~480 |
| `completion` | Ensure mandatory completion steps run regardless of workflow outcome | ~150 |

## Invocation

- `/skill approval-gate --task verify-authorization` - Check auth before work
- `/skill approval-gate --task verify-sub-issues` - Check sub-issue structure
- `/skill approval-gate --task verify-codebase` - Check codebase state
- `/skill approval-gate --task verify-already-implemented` - Check if spec already implemented
- `/skill approval-gate --task verify-blockers` - Check for blockers
- `/skill approval-gate --task verify-open-questions` - Check for unresolved questions
- `/skill approval-gate --task verify-fix-spec` - Verify fix spec exists for bug reports
- `/skill approval-gate --task search-prompt-fail` - Search for existing spec/plan candidates before Q/A halt
- `/skill approval-gate --task verify-closed-issue` - Verify closed issue was legitimately closed via merged PR
- `/skill approval-gate --task verify-schema-api-knowledge` - Verify schema/API/code knowledge before claims
- `/skill approval-gate --task reconcile-issue-graph` - Act on graph traversal findings
- `/skill approval-gate --task pre-implementation-analysis` - Analyze interdependencies and expand sub-issues for all approved issues, then yield to assemble-batch
- `/skill approval-gate --task screen-issue` - Per-issue screening (dispatched as sub-agent from pre-implementation-analysis)
- `/skill approval-gate --task post-implementation` - After implementation done
- `/skill approval-gate --task completion` - Invoke when workflow halts at any point
- `/skill approval-gate` - Overview only

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps (authorization result comment, status report) are never skipped. It is idempotent and safe to invoke multiple times.

## Operating Protocol

1. **Mandatory invocation (no decision point):** The agent MUST invoke approval-gate when it encounters `approved`/`go`, authorization questions, or implementation start. Never prompt for invocation — just invoke the skill.
2. **Two-gate authorization model:** Spec approval → plan creation. Plan approval → implementation. Each gate requires explicit authorization. **Exception: Spec-to-plan cascade** — when a spec is approved and a plan already exists, the plan inherits the spec's approval status automatically (see Step 5b in `verify-authorization.md`).
3. **Pre-Implementation Verification:** Verify spec or plan exists as GitHub Issue, verify authorization, verify sub-issues under plan (multi-task) — all consolidated in `verify-authorization` Step 5 as the single readiness check. The `github-sub-issues` verification gate is superseded by `verify-authorization`.
4. **Multi-task cascade:** When plan has sub-issues, authorization cascades from plan to ALL sub-issues. Complete ALL phases, report ONCE, HALT ONCE.
5. **Spec-to-plan approval cascade:** When a spec is approved and a plan already exists that references the spec (`Spec: #N` in plan body), the plan inherits the spec's approval status. The `needs-approval` label is removed from the plan and a comment documents the cascade. If multiple plans reference the spec, the most recent plan by creation date is cascade-approved and older plans are superseded. If no plan exists, the cascade does NOT apply — the standard flow (spec approval → writing-plans create → plan needs approval) continues. See `verify-authorization.md` Step 5b for the complete cascade procedure.
6. **Spec revision revocation:** If a spec is revised (status contains `REVISED - NEEDS APPROVAL` — in either prose or numeric format), find linked plan issues by searching for `[PLAN]` issues referencing the spec number in their body and mark them for audit. Revision of a spec revokes approval on its linked plan — including cascaded approval. Prose format example: `STATUS: in progress — {concern} (REVISED - NEEDS APPROVAL)`. Numeric format example: `STATUS: 1.1 (REVISED - NEEDS APPROVAL)`.
7. **Auto-dispatch after verification:** When all verification gates pass, auto-dispatch to the next skill in the chain. See Dispatch Order below.

## Dispatch Order

After `verify-authorization` completes successfully (all gates pass), the skill auto-dispatches based on approval context:

```
Spec approved (no existing plan)
  → verify-authorization (all gates pass)
  → writing-plans --task create (auto-dispatched to create plan issue)
  → Plan retains needs-approval label (requires separate plan approval)

Spec approved (existing plan found)
  → verify-authorization (all gates pass)
  → Step 5b: cascade approval to existing plan (remove needs-approval, add comment)
  → Plan is now approved → skip to plan-approved dispatch path
  → sub-issue verification (Step 5 of verify-authorization, if multi-phase)
  → pre-implementation-analysis → divide-and-conquer/assemble-batch → ...

Plan approved
  → verify-authorization (all gates pass)
  → git-workflow --task pre-work (MANDATORY: worktree creation and environment setup)
  → sub-issue verification (Step 5 of verify-authorization, if multi-phase)
  → pre-implementation-analysis (expand sub-issues, classify, build flat item list)
  → divide-and-conquer/assemble-batch (dispatch sub-agents, squash-merge into batch branch)
  → verification-before-completion
  → finishing-a-development-branch
  → git-workflow/review-prep

Already implemented
  → verify-authorization (all gates pass)
  → verify-already-implemented (detects implementation)
  → Auto-close (no dispatch)
```

**Spec approval dispatches to plan creation, NOT implementation.** The plan then requires its own approval before implementation begins — **unless the cascade applies** (spec approved + existing plan = plan inherits approval). See `verify-authorization.md` Step 5b for cascade conditions.

**Dispatch context detection:**
- Spec approval: Issue title contains `[SPEC` or has `spec` label
- Plan approval: Issue has `plan` label or `[PLAN]` prefix in title
- See `verify-authorization.md` Step 5 for full procedure

**⚠️ MANDATORY WORKTREE STEP:** `git-workflow --task pre-work` MUST be invoked between plan approval and any implementation. This step creates the feature branch worktree, sets `WORKTREE_PATH`, and verifies branch state. Skipping this step is a CRITICAL GUIDELINE VIOLATION (see `000-critical-rules.md`).

**Circular dispatch prevention:** Spec approval dispatches to `writing-plans`, which creates a plan. Plan approval dispatches to `executing-plans`. The plan requires its own approval before `executing-plans` can run.

## Authorization Requirements

| Requirement | Description |
|-------------|-------------|
| **Spec or Plan exists as GitHub Issue** | No local fallback — GitHub Issues only |
| **Two-gate authorization** | Spec approval → plan creation; Plan approval → implementation. Exception: spec-to-plan cascade (see below) |
| **Spec-to-plan approval cascade** | When a spec is approved and a plan already exists referencing the spec, the plan inherits the spec's approval status. `needs-approval` label is removed and a comment documents the cascade. Most recent plan is approved; older plans are superseded. If no plan exists, standard flow applies. |
| **Explicit authorization** | User says `approved`, `go`, `approved: N.M`, or `approved: {concern}` — OVERRIDES `needs-approval` label |
| **Open questions resolved** | No unresolved items in spec or plan |
| **Sub-issues verified under plan** | Multi-task plans require phase-level sub-issues (verified in `verify-authorization` Step 5 — single authoritative gate) |
| **Fix spec for bug reports** | Bug reports must have a fix spec sub-issue before closure (per `000-critical-rules.md`) |
| **Implementation includes** | All file modifications that alter behavior: source code, skill files, guideline files, config files, test files, TypeScript plugins |

## Fix Spec Verification for Bug Reports

Bug reports require a fix spec sub-issue before they can be considered complete. This verification is performed by the `verify-fix-spec` task.

| Check | Action |
|-------|--------|
| Bug report has fix spec sub-issue with `[SPEC] Fix:` title | ✅ Pass — fix spec exists |
| Bug report has fix spec sub-issue via `spec` label | ✅ Pass — fix spec exists |
| Bug report has NO fix spec sub-issue | ❌ Fail — invoke `issue-review --task analyze-and-spec` to create one |
| Bug report is NOT a bug report | ⏭️ Skip — this check does not apply |

This check is invoked:
- During `verify-already-implemented` for bug reports
- During `issue-review --task analyze-and-spec` already-handled path
- Before closing any issue that has `bug` label or bug report language

## Authorization Scope Rules

| Rule | Scope |
|------|-------|
| **Issue-bound** | Authorization applies ONLY to the specific issue |
| **Session-bound** | New session = new authorization required |
| **Single-use** | Authorization for current phase/task only |
| **Plan-bound** | Changes to plan invalidate authorization |
| **External input invalidates** | Bug reports, PR feedback require re-authorization |
| **Revision ≠ implementation** | Spec updates don't authorize code changes |
| **Reference ≠ cascade** | Issue mentions in body/comments do NOT cascade |
| **Confirmation ≠ authorization** | Confirming an observation does NOT authorize implementation |
| **Discussion conclusion ≠ authorization** | Verbal agreement, consensus, or opinion expressed in discussion does NOT constitute explicit authorization — see `020-go-prohibitions.md` §1 |
| **Batch carry-forward** | Authorization carries forward within a batch via persisted batch state file; no re-authorization needed between issues |

## Post-Implementation Workflow

1. Push feature branch to remote
2. Generate compare URL for review
3. Report completion to issue (NO URL) and URL in chat
4. HALT — do NOT create PR without explicit instruction
5. WAIT for "create a PR" instruction

## Sub-Agent Tasks

### Execution Mode Table

| Task | Words | Mode |
|------|-------|------|
| `verify-authorization` | 3,319 | sub-agent |
| `verify-qa-mode` | 2,188 | sub-agent |
| `verify-already-implemented` | 1,902 | sub-agent |
| `verify-closed-issue` | 1,763 | sub-agent |
| `verify-sub-issues` | 1,449 | sub-agent |
| `post-implementation` | 1,183 | sub-agent |
| `screen-issue` | 3,037 | sub-agent |
| `pre-implementation-analysis` | ~3,100 | sub-agent (receives screen-issue results) |
| `verify-fix-spec` | 1,017 | sub-agent |
| `verify-blockers` | 722 | inline |
| `verify-codebase` | 726 | inline |
| `verify-open-questions` | 531 | inline |
| `reconcile-issue-graph` | ~600 | inline |
| `completion` | 769 | inline |
| `search-prompt-fail` | ~300 | inline |
| `verify-schema-api-knowledge` | ~350 | inline |

### Result Contracts (Sub-Agent Tasks)

#### screen-issue

```yaml
status: DONE | DONE_WITH_CONCERNS | BLOCKED | OVERFLOW
task: screen-issue
issue_number: <N>
classification: included | excluded | scope-reduced
category: <already-implemented|superseded|moot|partially-implemented|meta-non-code|null>
exclude_reason: <reason|null>
reduce_reason: <reason|null>
reduced_scope: {completed_phases: [], remaining_phases: []}
flat_items: [{issue: <N>, title: <str>, phase: <str>}]
gate_evidence: {gate1_called: bool, gate1_sub_issues_verified: bool, gate1_closure_legitimacy: bool, gate2_criteria_extracted: bool, gate2_criteria_verified: bool, final_classification: <str>}
requires_developer: bool
developer_reason: <reason|null>
file_references: [<path>]
symbol_references: [<name>]
concerns: [<str>]
```

#### verify-authorization

```yaml
status: DONE | BLOCKED
task: verify-authorization
issue_number: <N>
authorization_result: authorized | unauthorized | needs_approval
cascade_applied: bool
sub_issues_verified: bool
gates_passed: [gate_name]
blocking_reason: <reason|null>
```

#### verify-qa-mode

```yaml
status: DONE
task: verify-qa-mode
mode: qa_mode | implementation_mode
spec_found: bool
spec_candidates: [<issue_number>]
routing: <next_task|null>
```

#### verify-already-implemented

```yaml
status: DONE
task: verify-already-implemented
issue_number: <N>
classification: already_implemented | partially_implemented | not_implemented
evidence_summary: <str>
auto_close_performed: bool
```

#### verify-closed-issue

```yaml
status: DONE
task: verify-closed-issue
issue_number: <N>
legitimate: bool
state_reason: <str>
merged_pr_evidence: <url|null>
action: none | reopen | flag
```

#### verify-sub-issues

```yaml
status: DONE
task: verify-sub-issues
parent_issue: <N>
sub_issues_count: <int>
all_verified: bool
missing_sub_issues: [<phase>]
auto_created: bool
```

#### post-implementation

```yaml
status: DONE
task: post-implementation
branch_pushed: bool
compare_url: <url>
issues_reported: [<N>]
```

#### pre-implementation-analysis

```yaml
status: DONE | BLOCKED
task: pre-implementation-analysis
screening_results_count: <int>
included: [<issue_number>]
excluded: [{issue: <N>, reason: <str>}]
scope_reduced: [{issue: <N>, remaining_phases: []}]
dependency_graph: {serial: [<N>], parallel_groups: [[<N>]]}
execution_plan_presented: bool
requires_developer: bool
developer_reason: <str|null>
batch_state_file: <path>
```

#### verify-fix-spec

```yaml
status: DONE
task: verify-fix-spec
bug_report: <N>
fix_spec_exists: bool
fix_spec_issue: <N|null>
action: none | create_fix_spec
```

#### reconcile-issue-graph

```yaml
status: DONE | DONE_WITH_UNCERTAIN
task: reconcile-issue-graph
root_issue: <N>
auto_closed: [<N>]
reopened: [<N>]
no_action: [<N>]
requires_dev_action: [{issue: <N>, current: <state>, needed: <state>, reason: <str>}]
nodes_visited: <N>
```

### Dispatch Context Schema (All Sub-Agent Tasks)

```yaml
issue_number: <N>
batch_peers: [<N>]  # screen-issue only
session_vars:
  GIT_OWNER: <from-session>
  GIT_REPO: <from-session>
  DEV_NAME: <from-session>
  DEV_EMAIL: <from-session>
  WORKTREE_PATH: <from-session>
```

## Adversarial Verification Requirements

Every task in this skill that reads a metadata claim (label, comment, STATUS marker, sub-issue state, authorization history) MUST verify that claim against actual state before trusting it for workflow decisions. This extends the `065-verification-honesty.md` principle from code verification to metadata verification.

### Verification Table

| Metadata Claim | Verification Action | Tool Call | Problem Class |
|----------------|-------------------|-----------|---------------|
| `needs-approval` label present | Check issue comments for explicit authorization ("approved"/"go") from a developer | `github_issue_read(method=get_comments)` | MISSING-ELEMENT |
| `needs-approval` label absent | Verify no pending authorization is needed (issue state is actually authorized) | `github_issue_read(method=get_labels)` | STRUCTURE-VIOLATION |
| Authorization comment exists | Verify author is a developer (not bot/agent); verify scope matches current issue; verify comment is not superseded by revision | `github_issue_read(method=get_comments)` → filter by author association | CONFLICTING |
| STATUS marker value | Compare STATUS against actual content maturity per ground-truth classification | `github_issue_read(method=get)` → parse body content | STRUCTURE-VIOLATION |
| Authorization currency | Verify spec has not been revised after most recent authorization comment | `github_issue_read(method=get_comments)` → compare revision timestamps | STRUCTURE-VIOLATION |
| Sub-issue state (open/closed) | Verify sub-issue state via GitHub API, not from cached or claimed state | `github_issue_read(method=get, issue_number=N)` → check `state` field | VERIFICATION-GAP |
| Fix spec existence | Verify fix spec sub-issue exists and has correct labels/STATUS for its maturity | `github_issue_read(method=get_sub_issues)` → verify each child | MISSING-TRACEABILITY |
| Batch screening dispatch (>3 issues) | Verify `screen-issue` sub-agents were dispatched (not inline screening) when batch size > 3 | Check for `task(subagent_type="general")` dispatch calls per issue | STRUCTURE-VIOLATION |

### Evidence Artifacts

Every adversarial verification check MUST produce an evidence artifact — a tool call result that demonstrates the verification was performed. Assertions without tool call evidence are verification honesty violations per `065-verification-honesty.md`.

**Evidence format:**

```
Check: [what was verified]
Tool: [tool call and parameters]
Result: [actual state found]
Classification: [STRUCTURE-VIOLATION|MISSING-ELEMENT|CONFLICTING|VERIFICATION-GAP|MISSING-TRACEABILITY]
Action: [auto-fix|conditional|flag-for-review]
```

### Finding Classification

Findings from adversarial verification follow the same three-tier model as `spec-auditor` ground-truth:

| Classification | When | Action |
|----------------|------|--------|
| auto-fix | Safe, mechanical corrections (stale label, mismatched STATUS) | Apply fix, note in evidence |
| conditional | Requires scope/safety check before applying (authorization claim vs actual) | Verify scope, then apply if safe |
| flag-for-review | Requires domain judgment (conflicting authorization, ambiguous state) | Report in findings, do not apply |

## Cross-References

- Related skills: `git-workflow` (branch operations, cleanup), `pr-creation-workflow` (PR timing), `issue-review` (authorization status)
- Related guidelines: `010-approval-gate.md`, `000-critical-rules.md`, `065-verification-honesty.md`
- Authorization classification: See `010-approval-gate.md` §Action Authorization Classification
- Related skill tasks: `approval-gate --task verify-authorization` (sub-issue verification is Step 5 — single authoritative gate), `git-workflow --task cleanup` (post-merge closure)
- Superseded: `github-sub-issues` verification gate is superseded by `approval-gate --task verify-authorization` Step 5
- Related subtask: `spec-auditor --task ground-truth` (adversarial metadata verification model)
- Label state machine: `141-planning-status-tracking.md §10` (label add/remove actions for this skill)

## Mandate Tiering Enforcement

Rules are classified into two tiers per `000-critical-rules.md` → "Mandate Tiering":

| Tier | Behavior | Examples |
|------|----------|----------|
| **Tier 1 (Non-Yielding)** | Enforced REGARDLESS of developer authorization | Worktree requirement, branch protection, human-only merge, no `/tmp/`, path rules |
| **Tier 2 (Authorization-Waivable)** | Yields to explicit developer authorization | Spec-before-code, plan-before-implementation, `needs-approval` label |

**Enforcement rule:** When `verify-authorization` confirms developer authorization exists, Tier 2 mandates are satisfied by that authorization. Tier 1 mandates are NEVER satisfied by authorization — they are independently enforced. An agent with developer authorization MUST still create a worktree, MUST still not commit to main/dev, MUST still not merge PRs.

**For simple work** (docs, runbooks, minor config): developer authorization IS the process — no spec/plan required. **For complex work**: developer authorization means "begin the process"; spec/plan creation is part of the authorized work.

```yaml+symbolic
schema_version: "1.0"
  last_updated: "2026-04-14T12:00:00Z"
rules:
  - id: approval-gate-skill-001
    title: "Pre-implementation authorization verification"
    conditions:
      all:
        - "spec_exists == true"
        - "user_authorized == false"
    actions:
      - HALT
    conflicts_with: []
    requires: [approval-gate-001]
    triggers: [git-workflow]
    source: "approval-gate/SKILL.md §Authorization Requirements"

  - id: approval-gate-skill-002
    title: "Multi-task cascade: authorization extends from plan to all sub-issues"
    conditions:
      all:
        - "plan_has_sub_issues == true"
        - "user_authorized == true"
    actions:
      - PROCEED
    conflicts_with: []
    requires: [approval-gate-002]
    triggers: [divide-and-conquer, executing-plans]
    source: "approval-gate/SKILL.md §Multi-task cascade"

  - id: approval-gate-skill-003
    title: "Post-implementation: push then halt"
    conditions:
      all:
        - "implementation_complete == true"
        - "pr_not_created == true"
    actions:
      - INVOKE(git-workflow)
      - HALT
    conflicts_with: []
    requires: []
    triggers: [git-workflow]
    source: "approval-gate/SKILL.md §Post-Implementation Workflow"

  - id: approval-gate-skill-004
    title: "Search before Q/A halt when no spec/plan found"
    conditions:
      all:
        - "implementation_requested == true"
        - "matching_spec_exists == false"
        - "matching_plan_exists == false"
    actions:
      - INVOKE(search-prompt-fail)
      - PRESENT(candidates_or_failure)
      - HALT
    conflicts_with: []
    requires: []
    triggers: [approval-gate, brainstorming, spec-creation]
    source: "approval-gate/SKILL.md §search-prompt-fail task"

  - id: approval-gate-skill-010
    title: "Verify schema/API/code knowledge before claims"
    conditions:
      all:
        - "agent_about_to_make_structural_claim == true"
        - "verification_performed == false"
    actions:
      - INVOKE(verify-schema-api-knowledge)
    conflicts_with: []
    requires: []
    triggers: [engineering-approach]
    source: "approval-gate/SKILL.md §verify-schema-api-knowledge task"

  - id: approval-gate-skill-005
    title: "Spec-to-plan approval cascade"
    conditions:
      all:
        - "spec_approved == true"
        - "spec_has_existing_plan == true"
    actions:
      - REMOVE_LABEL(needs-approval, plan)
      - ADD_COMMENT(cascade approval documentation)
      - PROCEED_TO(plan-approved dispatch path)
    conflicts_with: []
    requires: [approval-gate-002]
    triggers: [writing-plans]
    source: "approval-gate/SKILL.md §Spec-to-plan Approval Cascade"
```