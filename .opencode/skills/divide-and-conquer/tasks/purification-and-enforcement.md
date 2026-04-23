# Task: purification-and-enforcement

Migrated from `implementation-workflow` task purification-and-enforcement.

## Purpose

Reference document defining what git-workflow tasks DO and DO NOT do, and the enforcement rules for the divide-and-conquer orchestration layer.

## Entry Criteria

- Referencing this task when clarifying git-workflow boundaries or enforcement rules

## Exit Criteria

- Clear understanding of git-workflow scope and enforcement mechanisms

## Procedure

### Git Workflow Task Purification

**This skill CALLS git-workflow tasks. Git-workflow does NOT contain implementation logic.**

#### What Git-Workflow Tasks DO (Pure Git Ops)

| Task | Purpose | Implements? |
| -- | -- | -- |
| `pre-work` | Stash changes, create branch | NO - git ops only |
| `commit-prep` | Stage and commit changes | NO - git ops only |
| `review-prep` | Push branch, gen URL | NO - git ops only |
| `pr-creation` | Squash, create PR | NO - git ops only |
| `cleanup` | Delete merged branches | NO - git ops only |

#### What Git-Workflow Tasks DO NOT Do

| ❌ NOT in git-workflow | Moved Where? |
| -- | -- |
| Implementation logic | `divide-and-conquer` orchestrator |
| File editing | Implementation subagent |
| Spec reading | Implementation subagent |
| Progress tracking | Implementation subagent |

### Enforcement Mechanisms

#### ⚠️ CRITICAL: Verification Gate (Step 5)

**This gate is MANDATORY and has NO decision point.** It cannot be skipped, bypassed, or manually executed.

| Step | Skill | Required? | Decision Point? |
| -- | -- | -- | -- |
| 5a | verification-before-completion --task verify | YES | NO |
| 5b | finishing-a-development-branch --task checklist | YES | NO |
| 6 | git-workflow --task review-prep | YES | NO |

**Skipping any step in this sequence is a CRITICAL GUIDELINE VIOLATION.**

See `000-critical-rules.md` → "Skipping Post-Implementation Verification Skills" for the enforcement rule.

#### ⚠️ CRITICAL: No Implementation Logic in Git-Workflow

Git-workflow skills MUST remain pure git operations:

- ✅ Git commands (worktree, branch, commit, push)
- ✅ Git status checks
- ✅ Git cleanup
- ❌ File editing
- ❌ Spec reading
- ❌ Implementation decisions

#### ⚠️ CRITICAL: Yield-Back Before HALT

Each subtask MUST yield structured context before HALT:

- pre-work must yield branch info
- implementation must yield files changed
- review-prep must yield URL + summary

#### ⚠️ CRITICAL: HALT After Review-Prep

NEVER proceed to PR creation without explicit "create a PR" — UNLESS pipeline scope authorizes it:

- review-prep yields URL for CHAT
- HALT and wait
- Only "create a PR" triggers pr-creation
- **Exception:** When `authorization_scope >= for_pr` or scope is `pr_only`, pipeline scope authorizes PR creation. Proceed if `pr_strategy != none` AND `halt_at >= pr_created`.
- **When `halt_at < pr_created` or `pr_strategy == none`:** Do NOT create PR regardless of explicit instruction — the scope boundary is a hard wall.

#### ⚠️ CRITICAL: Scope Boundary Enforcement

The `halt_at` field from verify-authorization Step 2.0 defines a hard boundary. The dispatch chain MUST NOT proceed past this stage:

- `halt_at == spec_created` → HALT after spec creation
- `halt_at == plan_created` → HALT after plan creation
- `halt_at == implementation_complete` → HALT after implementation, no PR
- `halt_at == pr_created` → PR creation is authorized
- `halt_at == review_prep` → Standard flow, PR requires explicit instruction

## Edge Cases

### Common Issues

| Issue | Resolution |
| -- | -- |
| Authorization context lost | approval-gate passes context to divide-and-conquer |
| Pre-work asks for auth again | Pre-work receives context from orchestrator, no re-check |
| Implementation doesn't commit | Implementation calls git-workflow commit-prep directly |
| Verification fails | HALT and report missing evidence; do NOT proceed to review-prep |
| Finishing checklist fails | HALT and report issues (lint, tests, uncommitted); do NOT proceed to review-prep |
| Review-prep HALTs prematurely | Correct behavior - wait for "create a PR" |

Co-authored with AI: <AgentName> (<ModelId>)

## Live Verification: Enforcement Claims (MANDATORY)

**Verify enforcement checkpoint claims against actual state per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Authorization context preserved" | Verify work state contains auth | Read work state file for auth section | STRUCTURE-VIOLATION |
| "All commits made" | Verify clean working tree | `git status --porcelain` | VERIFICATION-GAP |
| "Verification passed" | Verify evidence artifacts exist | `glob(pattern="./tmp/verification-*")` | MISSING-ELEMENT |
| "Checklist completed" | Verify branch readiness | `git status --porcelain` and test execution | VERIFICATION-GAP |

**Evidence artifact:** Git state and file existence checks confirming enforcement accuracy.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Auth context lost | STRUCTURE-VIOLATION | conditional | Re-read from approval-gate |
| Uncommitted changes | VERIFICATION-GAP | conditional | Commit before proceeding |
| No verification evidence | MISSING-ELEMENT | conditional | Run verification before review-prep |
| Checklist not completed | VERIFICATION-GAP | conditional | Run checklist before review-prep |## Enforcement References
-  Completion checkpoint protocol: see `enforcement/completion-checkpoint.md`
-  Work state verification: see `enforcement/work-state-verification.md`
