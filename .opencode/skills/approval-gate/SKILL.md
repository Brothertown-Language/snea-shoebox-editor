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
| `screen-issue` | Per-issue screening for pre-implementation analysis (routing document for gate1 + gate2); dispatched as parallel sub-agents | ≈250 |
| `screen-issue/gate1` | Gate 1: Read issue, screening categories, sub-issue enumeration | ≈1,900 |
| `screen-issue/gate2` | Gate 2: Success criteria verification, cross-reference traversal, evidence audit, result contract | ≈2,500 |
| `pre-implementation-analysis` | Cross-issue merge of screening results, dependency graph, execution plan for assemble-work (routing document) | ≈425 |
| `pre-impl/collect-screening-results` | Steps -1, 0, 0.1, 0.15, 0.5: mandatory dispatch, collect results, autonomous classification, gate evidence audit | ≈1,200 |
| `pre-impl/reconcile-status` | Step 0.7: reconcile issue status inconsistencies via reconcile-issue-graph | ≈600 |
| `pre-impl/build-dependency-graph` | Steps 1, 2, 3, 4: flat item list, cross-issue analysis, classify issues, dependency graph | ≈1,600 |
| `pre-impl/check-cross-spec-overlap` | Cross-spec overlap check against open specs/plans outside batch | ≈500 |
| `pre-impl/write-work-state` | Steps 5, 7, 8, 9: execution strategy, dev base hash, dispatch context, work state file | ≈720 |
| `pre-impl/yield-to-assemble-work` | Steps 6, 10: present execution plan, execute immediately to assemble-work | ≈920 |
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
- `/skill approval-gate --task screen-issue/gate1` - Gate 1: Read issue, screening categories, sub-issue enumeration
- `/skill approval-gate --task screen-issue/gate2` - Gate 2: Success criteria verification, cross-reference, result contract
- `/skill approval-gate --task pre-impl/collect-screening-results` - Collect screening results and assemble gate evidence audit
- `/skill approval-gate --task pre-impl/reconcile-status` - Reconcile issue status inconsistencies
- `/skill approval-gate --task pre-impl/build-dependency-graph` - Build dependency graph from cross-issue analysis
- `/skill approval-gate --task pre-impl/check-cross-spec-overlap` - Check overlap with open specs/plans outside batch
- `/skill approval-gate --task pre-impl/write-work-state` - Determine execution strategy and write work state file
- `/skill approval-gate --task pre-impl/yield-to-assemble-work` - Present execution plan and yield to assemble-work
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
   → verification-before-completion (VERIFY: SC results exist)
   → finishing-a-development-branch --task checklist (VERIFY: all items checked)
   → git-workflow --task review-prep (VERIFY: compare URL generated)

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

## Chain-of-Responsibility Paths

| Path | Criteria | Chain |
|------|----------|-------|
| fast-path | 1 issue, standard scope, 0 sub-issues, explicit auth | scope-auto-resolve → verify-explicit-authorization → route-to-next-skill |
| medium-path | 1 issue + sub-issues OR plan with phases | scope-auto-resolve → verify-explicit-authorization → item-decomposition → sc-traceability → sub-issue-structure → route-to-next-skill |
| full-path | Multi-issue auth set | scope-auto-resolve → verify-explicit-authorization → item-decomposition → sc-traceability → sub-issue-structure → spec-to-plan-cascade → gap-fill-cascade → screen-issue → pre-impl/* → auto-dispatch |

Tier 1 mandates never skipped. Work state file bridges hops. See `enforcement/auto-dispatch-table.md` §Path Routing.

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

See `010-approval-gate.md` §Authorization Scope Rules for the complete table. Key rules:

- **Issue-bound**: Authorization applies ONLY to the specific issue
- **Hard HALT at scope boundary**: Agent MUST NOT proceed past `halt_at` without re-authorization
- **Reference ≠ cascade**: Issue mentions do NOT cascade authorization
- **Pipeline authorization**: Scope horizon determines pipeline stage where work stops

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
| `screen-issue` | ≈250 |
| `screen-issue/gate1` | ≈1,900 |
| `screen-issue/gate2` | ≈2,500 |
| `pre-implementation-analysis` | ≈425 |
| `pre-impl/collect-screening-results` | ≈1,200 |
| `pre-impl/reconcile-status` | ≈600 |
| `pre-impl/build-dependency-graph` | ≈1,600 |
| `pre-impl/check-cross-spec-overlap` | ≈500 |
| `pre-impl/write-work-state` | ≈720 |
| `pre-impl/yield-to-assemble-work` | ≈920 |
| `verify-fix-spec` | 1,017 |
| `verify-blockers` | 722 |
| `verify-codebase` | 726 |
| `verify-open-questions` | 531 |
| `reconcile-issue-graph` | ≈600 |
| `completion` | 769 |
| `search-prompt-fail` | ≈300 |
| `verify-schema-api-knowledge` | ≈350 |

### Result Contracts (Sub-Agent Tasks)

Result contracts define the structured YAML output each sub-agent task must return. Full schemas are in the `enforcement/` directory when applicable; key fields are listed below for orchestration reference.

#### Key Result Contract Fields

| Task | Status Values | Key Fields |
|------|--------------|------------|
| `screen-issue` | DONE, DONE_WITH_CONCERNS, BLOCKED, OVERFLOW | classification, category, flat_items, gate_evidence, requires_developer |
| `verify-authorization` | DONE, BLOCKED | authorization_result, cascade_applied, sub_issues_verified, authorization_scope, halt_at, pr_strategy, gap_fill_actions |
| `verify-qa-mode` | DONE | mode, spec_found, spec_candidates, routing |
| `verify-already-implemented` | DONE | issue_number, classification, evidence_summary, auto_close_performed |
| `verify-closed-issue` | DONE | issue_number, legitimate, state_reason, merged_pr_evidence, action |
| `verify-sub-issues` | DONE | parent_issue, sub_issues_count, all_verified, missing_sub_issues, auto_created |
| `post-implementation` | DONE | branch_pushed, compare_url, issues_reported |
| `pre-implementation-analysis` | DONE, BLOCKED | included, excluded, scope_reduced, dependency_graph, requires_developer, work_state_file, authorization_scope, halt_at, pr_strategy |
| `verify-fix-spec` | DONE | bug_report, fix_spec_exists, fix_spec_issue, action |
| `reconcile-issue-graph` | DONE, DONE_WITH_UNCERTAIN | root_issue, auto_closed, reopened, no_action, requires_dev_action, nodes_visited |

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

Every task that reads a metadata claim (label, comment, STATUS marker, sub-issue state, authorization history) MUST verify that claim against actual GitHub state before trusting it for workflow decisions. This extends `065-verification-honesty.md` from code verification to metadata verification.

**Evidence format and finding classification:** See `enforcement/adversarial-verification.md` for the complete evidence format, three-tier finding classification (auto-fix, conditional, flag-for-review), and problem class taxonomy. Every verification check MUST produce an evidence artifact via tool call — assertions without tool call evidence are verification honesty violations.

Key verification checks: `needs-approval` label status, authorization comment author/scope/currency, STATUS marker maturity, sub-issue open/closed state, fix spec existence, and screen-issue dispatch completeness.

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