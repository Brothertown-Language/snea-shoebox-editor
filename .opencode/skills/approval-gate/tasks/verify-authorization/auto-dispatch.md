# Task: verify-authorization — Step 6: Scope-Aware Auto-Dispatch

## Purpose

After all verification gates (Steps 1-5) pass, determine the approval context and auto-dispatch to the next skill in the chain. This step runs ONLY when ALL prior verification gates pass. If ANY gate fails, HALT — do NOT dispatch.

## 6.1 Pre-Implementation Worktree Setup (MANDATORY)

**Before any sub-agent dispatch or file modification, the agent MUST invoke `git-workflow --task pre-work` to:**

1. Create the feature branch in a worktree (`.worktrees/`)
2. Set the `worktree.path` environment variable
3. Verify branch state and working tree cleanliness

**This step is MANDATORY and CANNOT be skipped.** If the worktree already exists from a previous session, verify it and proceed. If worktree creation fails, HALT — do not proceed without a valid worktree.

**Evidence requirement:** `git worktree list` must show the feature branch worktree, and `worktree.path` must be set before any `divide-and-conquer` dispatch.

## Auto-Dispatch Context Differentiation

| Approval Context | How to Detect | Auto-Dispatch Target |
| -- | -- | -- |
| **Spec approval** | Issue title contains `[SPEC` or has `spec` label | `writing-plans --task create` (or `brainstorming --task explore` if gap-fill) |
| **Plan approval** | Issue has `plan` label or `[PLAN]` prefix in title | `executing-plans --task start` |
| **Already implemented** | `verify-already-implemented` returns positive (after closed-issue verification in Step 5.4 confirms legitimate closure) | No dispatch — auto-close instead |
| **Reconciled during verification** | reconcile-issue-graph returned auto-closed or reopened tickets | Include reconciled tickets in chat output; proceed with dispatch |
| **Closed but NOT verified** | Step 5.4 closed-issue verification finds closure without merged PR evidence | flag-for-review — do NOT autoclose |

## Scope-Aware Dispatch Targets

The dispatch target is modified by `authorization_scope` from Step 2.0. See `enforcement/auto-dispatch-table.md` for the complete scope-dependent routing.

**🚫 HARD HALT AT SCOPE BOUNDARY:** The agent MUST NOT proceed past the pipeline stage specified by `halt_at`. If the dispatch chain reaches the `halt_at` stage, the agent reports completion and STOPS. Proceeding past `halt_at` without re-authorization is a CRITICAL GUIDELINE VIOLATION.

## Auto-Dispatch Procedure

1. Determine approval context (spec vs plan) by checking:
   - Issue title format: `[SPEC` prefix = spec approval
   - Issue title format: `[PLAN]` prefix = plan approval
   - Labels: presence of `spec` or `plan` labels
   - Plan detection is via `plan` label or `[PLAN]` prefix in title (NOT via sub-issue relationship to spec)
2. Determine scope from Step 2.0 result (`authorization_scope`, `halt_at`, `pr_strategy`)
3. Execute gap-fill from Step 5c if scope >= `for_plan`
4. **If spec approval:** Invoke `writing-plans --task create` with context:
   - `spec_issue=#N` (the approved spec issue number)
   - `authorization_scope=<scope>` and `halt_at=<stage>`
   - `<github.owner>`, `<github.repo>`, `<worktree.path>` from session
5. **If plan approval:** Invoke `executing-plans --task start` with context:
   - `plan_issue=#N` (the approved plan issue number)
   - `spec_issue=#M` (extracted from plan body — the spec reference)
   - `authorization_scope=<scope>`, `halt_at=<stage>`, `pr_strategy=<strategy>`
   - `<github.owner>`, `<github.repo>`, `<worktree.path>` from session
6. **Chat output:** Clearly indicate the transition and scope:
   - Spec approval: "Verification passed → Creating implementation plan (scope: <scope>)"
   - Plan approval: "Verification passed → Starting implementation (scope: <scope>, halt_at: <stage>)"

## Spec Revision Revocation Detection

If a spec is revised (status contains `REVISED - NEEDS APPROVAL` — in either prose or numeric format):

Prose format: `STATUS: in progress — {concern} (REVISED - NEEDS APPROVAL)`
Numeric format: `STATUS: 1.1 (REVISED - NEEDS APPROVAL)`

1. Search for `[PLAN]` issues that reference the spec number in their body
2. Mark found plans for audit (their authorization is revoked by the spec revision)
3. Report affected plans in chat output

## Auto-Dispatch Edge Cases

- **Spec already has a plan:** `writing-plans --task create` handles this (skips or updates per its existing logic)
- **Multi-task plan with missing sub-issues:** Step 5 sub-issue verification gate fails → HALT, no dispatch
- **Authorization set dispatch:** Each plan in the work set gets its own dispatch cycle after work state is established
- **Scope requires gap-fill but artifact exists:** Skip gap-fill for that artifact (check before creating)
- **`pr_only` or `review_only` scope with no existing branch/PR:** HALT and report — these scopes assume existing work

## Authorization Cascade by Output Lineage (Step 2.1)

When user approves issue #P, and #P's body or comments explicitly state that it created issue #C (e.g., "Spec created: #966"), authorization cascades from #P to #C if ALL conditions are met:

1. #P is a meta/investigation/review issue (no implementation criteria of its own)
2. #P's sole or primary deliverable is the creation of #C
3. #C is a spec or plan with implementation criteria
4. No contradictory evidence (e.g., #P's body says "spec rejected, try again")

When cascade applies:

- #C is treated as if the user said "Approved: #C"
- Add comment to #C: "Authorization cascaded from #P (approvable output of approved issue)"
- Remove `needs-approval` label from #C

When cascade does NOT apply (conditions not met):

- HALT and inform user: "#P was approved but it is an investigation issue — its spec #C was not named. Please confirm: approve #C?"
- This is a genuine authorization gap where the developer's intent is ambiguous

**Evidence artifact:** `github_issue_read(method=get_comments)` showing lineage evidence in #P, and `github_issue_write` / `github_add_issue_comment` responses confirming cascade actions on #C.

## Context Budget Check Before Dispatch (MANDATORY for implementation scopes)

**When `authorization_scope` is `for_implementation`, `for_code_review`, or `for_pr`:**

Before dispatching to `divide-and-conquer --task assemble-work`, verify that sufficient context budget remains to complete at least one implementation item:

1. Estimate remaining context: if the agent has consumed >75% of its context window on process steps (verification, screening, worktree setup), the remaining budget may be insufficient for implementation
2. If context budget is critically low (<25% remaining): report budget exhaustion explicitly in chat output before halting — do NOT silently halt after process overhead
3. Budget exhaustion does NOT exempt the agent from the implementation-first gate — it is a REPORTING requirement, not a bypass

**Evidence artifact:** If halted due to budget exhaustion, the halt message MUST include: "Context budget exhausted during process steps. Deliverables produced: 0 file modifications. Process steps completed: [list]."

This check prevents the pattern documented in bugs #1232 and #1233 where the agent completes all process overhead but halts before implementation with no deliverables.

## Work State I/O

- **Reads from:** `## gap-fill-cascade`, `## scope-auto-resolve`
- **Writes to:** `## auto-dispatch`

After completing this task, write results to the work state file under section `## auto-dispatch` using the YAML format defined in `enforcement/work-state-schema.md`.