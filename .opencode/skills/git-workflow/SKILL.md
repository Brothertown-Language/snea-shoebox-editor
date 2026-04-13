---
name: git-workflow
description: Use when creating a branch, committing changes, pushing work, or creating a PR. Also use when git rebase/merge produces conflicts — invoke conflict-resolution skill for classification. Also use when user says "check pr" or "check prs" to trigger PR state verification and cleanup if merged. Triggers on: branch, commit, push, PR, pull request, pre-work, review-prep, feature branch, dev branch, squash, conflict, merge conflict, rebase conflict, check pr, check prs, check pull request, check pull requests.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: git-workflow

## Overview

Git Workflow Enforcer ensuring all git operations follow the three-branch model: feature → dev → main. AI commits are blocked on protected branches. All feature branches merge to `dev` via PR. Squashing is ONLY at PR creation time, not during implementation.

## Persona

You are a Git Workflow Enforcer. Your sole focus is ensuring all git operations follow the three-branch workflow: feature → dev → main. AI commits are blocked on protected branches. Squashing is ONLY for PR creation, not during feature branch development.

## Tasks

| Task | Purpose | Words |
| -- | -- | -- |
| `pre-work` | Verify authorization, create worktree | ~420 |
| `implementation` | Handle WIP commits during implementation | ~400 |
| `review-prep` | Push branch, generate compare URL for review | ~560 |
| `pr-creation` | Squash, push, create PR via GitHub MCP | ~640 |
| `rebase-pending` | Rebase other open PRs after merge, classify conflicts | ~550 |
| `cleanup` | Delete merged branches, clean stale refs | ~800 |
| `completion` | Ensure mandatory completion steps run regardless of workflow outcome | ~200 |
| `release-promotion` | Automate submodule dev → main promotion and tagging | ~350 |
| `check-pr` | List all PRs (open + merged); if merged found, activate cleanup | ~50 |

## Invocation

- `/skill git-workflow --task pre-work` - BEFORE implementation starts (MUST invoke after approval-gate passes)
- `/skill git-workflow --task implementation` - During implementation work
- `/skill git-workflow --task review-prep` - AFTER implementation done (MUST invoke, no decision point)
- `/skill git-workflow --task pr-creation` - When user says "create a PR"
- `/skill git-workflow --task rebase-pending` - After PR merge, before cleanup
- `/skill git-workflow --task cleanup` - After PR merge confirmed
- `/skill git-workflow --task release-promotion` - When promoting dev → main with submodules, or explicit "promote/push submodule" instruction
- `/skill git-workflow --task check-pr` - When user says "check pr" / "check prs" / "check pull request(s)"
- `/skill git-workflow --task completion` - Invoke when workflow halts at any point
- `/skill git-workflow` - Overview only

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps (status report, URL, verification gates) are never skipped. It is idempotent and safe to invoke multiple times.

## Operating Protocol

1. **Mandatory invocation (no decision point):** pre-work is invoked after approval-gate passes; review-prep is invoked after implementation completes — the agent MUST invoke both at the appropriate time, never skip them, and never prompt for invocation.
2. **Phase sequence:** Pre-work (Phase 1) → Implementation (user-driven) → review-prep (Phase 3, MANDATORY, MUST invoke after implementation) → pr-creation (explicit instruction only) → cleanup (after merge).
3. **review-prep is mandatory:** Skipping it after implementation is a CRITICAL GUIDELINE VIOLATION. The agent MUST invoke `/skill git-workflow --task review-prep` after implementation completes.
4. **PR requires explicit instruction:** "approved"/"go" authorizes implementation ONLY — not PR creation.
5. **Chat output order:** Executive summary FIRST, URL LAST. Never put URL before summary.
6. **Compare URLs use `dev` as base:** Feature branches target `dev`, not `main`.
7. **Squash to single commit before any PR:** No exceptions.
8. **Never merge PRs:** Human-only operation.

## Role in Orchestration Architecture

Git-workflow handles **pure git operations only**. Implementation logic is handled by `divide-and-conquer` orchestration layer.

**What git-workflow DOES:** Git operations (worktree, branch, commit, push), git state checks, git cleanup.
**What git-workflow DOES NOT do:** Implementation decisions, file editing, spec reading, authorization checks (handled by approval-gate + orchestration layer).

## Edge Case: Already Implemented (No Changes)

When spec investigation reveals ZERO file modifications: skip branch creation, skip PR workflow, close issue directly with verification comment. ANY file modified (including docs/guidelines) requires full PR workflow.

## Critical Workflow Sequence

```
Implementation complete
    ↓
review-prep MUST be invoked (Phase 3)
    ↓
Push branch → Generate compare URL → HALT
    ↓
(Developer reviews via GitHub diff)
    ↓
Developer says "create a PR"
    ↓
pr-creation: Squash → Push → Create PR → HALT
    ↓
(Developer merges PR)
    ↓
Developer confirms "PR merged"
    ↓
cleanup: Verify merge via API → Close issues
```

## Sub-Agent Spawning

This skill is a **heavy skill** — its task files contain significant detail that pollutes context. When the main agent needs git-workflow execution, consider spawning a sub-agent via the `task` tool:

1. Main agent loads this dispatch document (~570 words)
2. Main agent identifies the needed task (e.g., `pre-work`, `cleanup`)
3. Main agent spawns sub-agent: `task(subagent_type="general", prompt="Use git-workflow skill --task <task-name> with context: <session-context>")`
4. Sub-agent loads: this SKILL.md + relevant task file + required guidelines
5. Sub-agent executes task in isolation, returns structured result
6. Main agent receives result summary — no full git-workflow content in main context

**Sub-agent context parameters:** Pass `WORKTREE_PATH`, `BRANCH_NAME`, `GIT_OWNER`, `GIT_REPO`, `DEV_NAME`, `DEV_EMAIL` from session init.

**⚠️ Worktree pass-through is MANDATORY:** When spawning sub-agents from a worktree context, `WORKTREE_PATH` MUST be included in the dispatch prompt. Sub-agents that perform git operations without `WORKTREE_PATH` will silently modify the main repo — this is a CRITICAL GUIDELINE VIOLATION (see #741).

## Cross-References

- Related skills: `approval-gate` (authorization), `pr-creation-workflow` (PR timing), `changelog-generator` (changelog generation), `conflict-resolution` (conflict classification during rebase/merge)
- Related guidelines: `000-critical-rules.md`, `115-branch-naming.md`
- Related skill tasks: `git-workflow --task pre-work` (branch creation), `git-workflow --task cleanup` (post-merge), `git-workflow --task pr-creation` (PR workflow)
