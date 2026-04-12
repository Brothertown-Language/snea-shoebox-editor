# Task: purification-and-enforcement

## Purpose

Reference document defining what git-workflow tasks DO and DO NOT do, and the enforcement rules for the implementation-workflow orchestration layer.

## Entry Criteria

- Referencing this task when clarifying git-workflow boundaries or enforcement rules

## Exit Criteria

- Clear understanding of git-workflow scope and enforcement mechanisms

## Procedure

### Git Workflow Task Purification

**This skill CALLS git-workflow tasks. Git-workflow does NOT contain implementation logic.**

#### What Git-Workflow Tasks DO (Pure Git Ops)

| Task | Purpose | Implements? |
|------|---------|-------------|
| `pre-work` | Stash changes, create branch | NO - git ops only |
| `commit-prep` | Stage and commit changes | NO - git ops only |
| `review-prep` | Push branch, gen URL | NO - git ops only |
| `pr-creation` | Squash, create PR | NO - git ops only |
| `cleanup` | Delete merged branches | NO - git ops only |

#### What Git-Workflow Tasks DO NOT Do

| ❌ NOT in git-workflow | Moved Where? |
|------------------------|---------------|
| Implementation logic | `implementation-workflow` orchestrator |
| File editing | Implementation subagent |
| Spec reading | Implementation subagent |
| Progress tracking | Implementation subagent |

### Enforcement Mechanisms

#### ⚠️ CRITICAL: Verification Gate (Step 3.5)

**This gate is MANDATORY and has NO decision point.** It cannot be skipped, bypassed, or manually executed.

| Step | Skill | Required? | Decision Point? |
|------|-------|-----------|-----------------|
| 3.5a | verification-before-completion --task verify | YES | NO |
| 3.5b | finishing-a-development-branch --task checklist | YES | NO |
| 4 | git-workflow --task review-prep | YES | NO |

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

NEVER proceed to PR creation without explicit "create a PR":
- review-prep yields URL for CHAT
- HALT and wait
- Only "create a PR" triggers pr-creation

## Edge Cases

### Common Issues

| Issue | Resolution |
|-------|------------|
| Authorization context lost | approval-gate passes context to implementation-workflow |
| Pre-work asks for auth again | Pre-work receives context from orchestrator, no re-check |
| Implementation doesn't commit | Implementation calls git-workflow commit-prep directly |
| Verification fails | HALT and report missing evidence; do NOT proceed to review-prep |
| Finishing checklist fails | HALT and report issues (lint, tests, uncommitted); do NOT proceed to review-prep |
| Review-prep HALTs prematurely | Correct behavior - wait for "create a PR" |