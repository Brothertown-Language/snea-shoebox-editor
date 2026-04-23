---
name: approval-gate
description: Use when user says "approved", "go", or any implementation instruction, or when authorization needs verification. Triggers on: approval, authorized, implement, start work, go ahead, needs-approval label, authorization set, multiple issues approved, interdependency analysis.
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
| `verify-qa-mode` | Detect spec-less implementation requests, switch to Q/A mode | ≈800 |
| `verify-authorization` | Check explicit auth and needs-approval label; delegates branch creation to `git-workflow --task pre-work` | ≈400 |
| `verify-authorization/scope-auto-resolve` | Step 0.5: Scope auto-resolve from authorization phrase | ≈200 |
| `verify-authorization/item-decomposition-check` | Step 4.5: Verify item decomposition in plan | ≈250 |
| `verify-authorization/sc-traceability-check` | Step 4.6: SC-to-test traceability and RED-phase ordering | ≈350 |
| `verify-authorization/sub-issue-verification` | Step 5: Verify sub-issue structure (authoritative gate) | ≈600 |
| `verify-authorization/spec-to-plan-cascade` | Step 5b: Spec-to-plan approval cascade | ≈400 |
| `verify-authorization/gap-fill-cascade` | Step 5b.5 + 5c: Gap-fill precedence and cascade execution | ≈500 |
| `verify-authorization/auto-dispatch` | Step 6: Scope-aware auto-dispatch + output lineage | ≈500 |
| `verify-sub-issues` | Verify sub-issue structure for multi-task specs | ≈480 |
| `verify-codebase` | Re-evaluate codebase state, detect staleness | ≈400 |
| `verify-already-implemented` | Check if all success criteria are already met; autoclose if so | ≈400 |
| `verify-blockers` | Check for blocking issues/dependencies | ≈320 |
| `verify-open-questions` | Check for unresolved questions in spec | ≈370 |
| `verify-fix-spec` | For bug reports, verify fix spec sub-issue exists before closure | ≈250 |
| `search-prompt-fail` | Search GitHub Issues for existing spec/plan candidates before Q/A halt; present candidates or report failure | ≈300 |
| `verify-closed-issue` | Verify that a closed issue was legitimately closed via merged PR; enforce "closed ≠ verified" rule | ≈350 |
| `screen-issue` | Per-issue screening for pre-implementation analysis (Gate 1 + Gate 2 + screening categories); dispatched as parallel sub-agents | ≈3,000 |
| `pre-implementation-analysis` | Cross-issue merge of screening results, dependency graph, execution plan for assemble-work | ≈500 |
| `verify-schema-api-knowledge` | Verify that the agent has performed live verification before making schema/API/code claims; gate before proceeding | ≈350 |
| `reconcile-issue-graph` | Act on graph traversal findings: auto-close verified-complete, reopen verified-incomplete, flag uncertain | ≈600 |
| `post-implementation` | Push branch, generate compare URL, HALT | ≈480 |
| `completion` | Ensure mandatory completion steps run regardless of workflow outcome | ≈150 |

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
- `/skill approval-gate --task pre-implementation-analysis` - Analyze interdependencies and expand sub-issues for all approved issues, then yield to assemble-work
- `/skill approval-gate --task screen-issue` - Per-issue screening (dispatched as sub-agent from pre-implementation-analysis)
- `/skill approval-gate --task post-implementation` - After implementation done
- `/skill approval-gate --task completion` - Invoke when workflow halts at any point
- `/skill approval-gate` - Overview only

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps (authorization result comment, status report) are never skipped. It is idempotent and safe to invoke multiple times.

## Operating Protocol

1. **Mandatory invocation (no decision point):** The agent MUST invoke approval-gate when it encounters `approved`/`go`, authorization questions, or implementation start. Never prompt for invocation — just invoke the skill.
2. **Two-gate authorization model:** Spec approval → plan creation. Plan approval → implementation. Each gate requires explicit authorization. **Exception: Spec-to-plan cascade** — when a spec is approved and a plan already exists, the plan inherits the spec's approval status automatically (see Step 5b in `verify-authorization.md`).
3. **Pre-Implementation Verification:** Verify spec or plan exists as GitHub Issue, verify authorization, verify sub-issues under plan (multi-task) — all consolidated in `verify-authorization` Step 5 as the single readiness check. The `issue-operations` `link-sub-issue` verification gate is superseded by `verify-authorization`.
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
  → pre-implementation-analysis → divide-and-conquer/assemble-work → ...

Plan approved
  → verify-authorization (all gates pass)
  → git-workflow --task pre-work (MANDATORY: worktree creation and environment setup)
  → sub-issue verification (Step 5 of verify-authorization, if multi-phase)
  → pre-implementation-analysis (expand sub-issues, classify, build flat item list)
  → divide-and-conquer/assemble-work (dispatch sub-agents, squash-merge into work branch)
  ── VERIFICATION GATE ──────────────────────────────────────────────────
  → Confirm assemble-work completed: work state file exists, all sub-agents returned
  → If skipped: INVOKE assemble-work before proceeding (MANDATORY, no bypass)
  ──────────────────────────────────────────────────────────────────────
  → verification-before-completion
  ── VERIFICATION GATE ──────────────────────────────────────────────────
  → Confirm VbC completed: success criteria verification results exist
  → If skipped: INVOKE verification-before-completion before proceeding (MANDATORY, no bypass)
  ──────────────────────────────────────────────────────────────────────
  → finishing-a-development-branch --task checklist
  ── VERIFICATION GATE ──────────────────────────────────────────────────
  → Confirm checklist completed: all checklist items verified via tool calls
  → If skipped: INVOKE checklist before proceeding (MANDATORY, no bypass)
  ──────────────────────────────────────────────────────────────────────
  → git-workflow --task review-prep
  ── VERIFICATION GATE ──────────────────────────────────────────────────
  → Confirm review-prep completed: compare URL generated and reported in correct format
   → If skipped: INVOKE review-prep before proceeding (MANDATORY, no bypass)
   ──────────────────────────────────────────────────────────────────────

Clearly simple work (Tier 2 waiver)
  → git-workflow --task pre-work (MANDATORY: worktree creation)
  → Direct implementation in worktree (no sub-agent dispatch for single-file changes)
  → verification-before-completion (simplified for docs/config)
  → finishing-a-development-branch --task checklist
  → git-workflow --task review-prep
  → HALT (compare URL output)

  **Classification check:** Before using this dispatch path, verify work meets ALL "clearly simple" criteria per `000-critical-rules.md` → "Simple Work Dispatch Path (Tier 2 Waiver)" → "Classification: Clearly Simple Work" table. If ANY criterion fails, use the full dispatch chain instead.

Already implemented
  → verify-authorization (all gates pass)
  → verify-already-implemented (detects implementation)
  → Auto-close (no dispatch)
```

**Enforcement checkpoint rules (MANDATORY):**

Before proceeding to the next step in the dispatch chain, the agent MUST confirm the previous step was completed by checking for its output artifacts. If any step was skipped, the agent MUST invoke it before proceeding — no step may be bypassed.

| Step | Output Artifacts to Confirm | On Missing |
| -- | -- | -- |
| `git-workflow --task pre-work` | `worktree.path` set, feature branch exists | HALT and invoke pre-work |
| `divide-and-conquer/assemble-work` | Work state file (`.opencode/tmp/work-*.md`), all sub-agents returned | HALT and invoke assemble-work |
| `verification-before-completion` | Success criteria verification results exist in chat output | HALT and invoke VbC |
| `finishing-a-development-branch --task checklist` | All checklist items verified via tool-call artifacts | HALT and invoke checklist |
| `git-workflow --task review-prep` | Compare URL generated and reported in correct format | HALT and invoke review-prep |

**Skipping any verification gate is a CRITICAL GUIDELINE VIOLATION.** The dispatch order is mandatory, not informational. An agent that proceeds past a gate without confirming the prior step's completion is violating the approval-gate enforcement protocol.

**Evidence requirement (MANDATORY):** Each verification gate in the dispatch chain MUST produce a tool-call artifact confirming the prior step completed. Reading chat history is NOT sufficient — the agent MUST explicitly invoke a verification tool or command and record the output as evidence. The enforcement checkpoint table above specifies what artifacts confirm each step. Proceeding past a gate without producing the corresponding evidence is a CRITICAL GUIDELINE VIOLATION.

**Spec approval dispatches to plan creation, NOT implementation.** The plan then requires its own approval before implementation begins — **unless the cascade applies** (spec approved + existing plan = plan inherits approval). See `verify-authorization.md` Step 5b for cascade conditions.

**Dispatch context detection:**
- Spec approval: Issue title contains `[SPEC` or has `spec` label
- Plan approval: Issue has `plan` label or `[PLAN]` prefix in title
- See `verify-authorization.md` Step 5 for full procedure

**⚠️ MANDATORY WORKTREE STEP:** `git-workflow --task pre-work` MUST be invoked between plan approval and any implementation. This step creates the feature branch worktree, sets `worktree.path`, and verifies branch state. Skipping this step is a CRITICAL GUIDELINE VIOLATION (see `000-critical-rules.md`).

**Circular dispatch prevention:** Spec approval dispatches to `writing-plans`, which creates a plan. Plan approval dispatches to `executing-plans`. The plan requires its own approval before `executing-plans` can run.

**⚠️ AUTO-DISPATCH ENFORCEMENT:** After `pre-implementation-analysis` completes with `requires_developer: false`, the agent MUST proceed to the next step in the dispatch chain without halting. "Yield" means "produce output and continue," NOT "present output and wait." The only valid halt after analysis is when a screening sub-agent returned `requires_developer: true` per the exhaustive conditions in `screen-issue.md`.

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
| **Output lineage cascade** | When user approves an investigation/review issue whose sole deliverable is creating a spec, approval cascades to the spec. See `verify-authorization.md` Step 2.1 for the complete cascade procedure. |

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
| **Work carry-forward** | Authorization carries forward within a work set via persisted work state file; no re-authorization needed between issues |
| **Pipeline authorization (scope-horizon)** | Authorization phrases specify a scope horizon — the pipeline stage where work stops. Everything below is gap-filled and auto-approved. Everything above is unauthorized. See Authorization Scope Model below. |
| **Hard HALT at scope boundary** | Agent MUST NOT proceed past `halt_at` pipeline stage without re-authorization. Scope boundary is a hard wall, not a soft suggestion. |

## Authorization Scope Model

### Scope Values

| Scope | Meaning | HALT After | Gap-Fill | PR Strategy |
|-------|---------|------------|----------|--------------|
| `standard` | Default: all artifacts must pre-exist | review-prep | None | individual |
| `for_spec` | Authorization extends through spec creation | spec_created | None | none |
| `for_plan` | Authorization extends through plan creation | plan_created | auto-create spec | none |
| `for_implementation` | Authorization extends through implementation | implementation_complete | auto-create spec+plan, auto-approve plan | individual |
| `for_code_review` | Authorization extends through code review | code_review_ready | auto-create spec+plan, auto-approve plan | individual |
| `for_pr` | Full pipeline authorization, including PR creation | pr_created | auto-create spec+plan, auto-approve plan, auto-create PR | stacked |
| `pr_only` | PR creation only (assumes code exists on branch) | pr_created | None | stacked |
| `review_only` | Code review only (assumes code/PR exists) | code_review_ready | None | individual |

### Scope Detection (Verb-Prefix Parsing)

| Verb Pattern | Detected Scope |
|---------------|---------------|
| "approved #N to PR" / "approved #N for PR" / "approved #N through PR" | `for_pr` |
| "approved #N to review" / "approved #N for review" / "approved #N through review" | `for_code_review` |
| "approved #N to implementation" / "approved #N for implementation" | `for_implementation` |
| "approved #N to plan" / "approved #N for plan" | `for_plan` |
| "approved #N to spec" / "approved #N for spec" | `for_spec` |
| "PR only" / "PR just" | `pr_only` |
| "review only" / "review just" | `review_only` |
| "approved" / "go" / "approved #N" (no scope qualifier) | `standard` |

### Unified Dispatch Path (Work-of-1)

**Every authorization follows the same pipeline regardless of issue count.** There is no single-task exemption — the dispatch chain is unified:

```
verify-authorization → gap-fill (if scope >= for_plan) → git-workflow pre-work
→ pre-implementation-analysis → divide-and-conquer/assemble-work
→ verification-before-completion → finishing-a-development-branch checklist
→ git-workflow review-prep → [HALT at halt_at or continue to PR creation]
```

Whether the plan has 1 sub-issue or 10, the same skills are invoked. The `pr_strategy` field determines PR creation behavior, not issue count.

### PR Strategy Is Scope-Dependent

| Scope | PR Strategy | Behavior |
|-------|-------------|----------|
| `standard`, `for_implementation`, `for_code_review` | individual | Separate PR per issue |
| `for_pr`, `pr_only` | stacked | Single stacked PR for all issues in work set |
| `for_spec`, `for_plan` | none | No PR (spec/plan creation only) |
| `review_only` | individual | Review existing PRs |

When `halt_at < pr_created`, no PR is created — the agent halts before reaching the PR creation stage.

## Post-Implementation Workflow

1. Push feature branch to remote
2. Generate compare URL for review
3. Report completion to issue (NO URL) and URL in chat
4. **If `pr_strategy != none` AND `halt_at >= pr_created`:** Proceed to PR creation per `pr_strategy`
5. **If `halt_at < pr_created`:** HALT at scope boundary — do NOT create PR
6. **If `pr_strategy == none`:** HALT — do NOT create PR without explicit instruction
7. WAIT for "create a PR" instruction when scope does not include PR creation

## Sub-Agent Tasks

### Sub-Agent Tasks

| Task | Words |
|------|-------|
| `verify-authorization` | ≈400 |
| `verify-authorization/scope-auto-resolve` | ≈200 |
| `verify-authorization/item-decomposition-check` | ≈250 |
| `verify-authorization/sc-traceability-check` | ≈350 |
| `verify-authorization/sub-issue-verification` | ≈600 |
| `verify-authorization/spec-to-plan-cascade` | ≈400 |
| `verify-authorization/gap-fill-cascade` | ≈500 |
| `verify-authorization/auto-dispatch` | ≈500 |
| `verify-qa-mode` | 2,188 |
| `verify-already-implemented` | 1,902 |
| `verify-closed-issue` | 1,763 |
| `verify-sub-issues` | 1,449 |
| `post-implementation` | 1,183 |
| `screen-issue` | 3,037 |
| `pre-implementation-analysis` | ≈3,100 |
| `verify-fix-spec` | 1,017 |
| `verify-blockers` | 722 |
| `verify-codebase` | 726 |
| `verify-open-questions` | 531 |
| `reconcile-issue-graph` | ≈600 |
| `completion` | 769 |
| `search-prompt-fail` | ≈300 |
| `verify-schema-api-knowledge` | ≈350 |

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
cascade_type: plan_cascade | output_lineage_cascade | none
cascade_parent: <issue_number | null>
authorization_scope: standard | for_spec | for_plan | for_implementation | for_code_review | for_pr | pr_only | review_only
scope_source: parsed | default
halt_at: <pipeline_stage>
pr_strategy: stacked | individual | none
gap_fill_actions: [<action_list>]
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
work_state_file: <path>
authorization_scope: <scope_value>
halt_at: <pipeline_stage>
pr_strategy: stacked | individual | none
per_issue_gap_fill: [{issue: <N>, gap_fill: [<action>]}]
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
work_peers: [<N>]  # screen-issue only
authorization_scope: <scope_value>
halt_at: <pipeline_stage>
pr_strategy: stacked | individual | none
session_vars:
  github.owner: <from-session>
  github.repo: <from-session>
  dev.name: <from-session>
  dev.email: <from-session>
  worktree.path: <from-session>
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
| Work screening dispatch | Verify `screen-issue` sub-agents were dispatched for EVERY approved issue — no count threshold | Check for `task(subagent_type="general")` dispatch calls per issue | STRUCTURE-VIOLATION |

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
- Superseded: `issue-operations` `link-sub-issue` verification gate is superseded by `approval-gate --task verify-authorization` Step 5
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