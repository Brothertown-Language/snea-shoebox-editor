---
name: finishing-a-development-branch
description: Use when implementation is complete and branch needs final checks before PR. Triggers on: done, finished, ready for PR, implementation complete, branch ready, push changes, final check.
type: technique
license: MIT
compatibility: opencode
---

# Skill: finishing-a-development-branch

## Overview

Branch completion workflow that ensures a feature branch is fully ready for PR creation. Verifies all changes are committed, tested, pushed, and reviewed before the developer creates a PR. Adapted from the \<UPSTREAM_ORG>/\<UPSTREAM_REPO> workflow.

**Source Attribution:** This skill is adapted from \<UPSTREAM_ORG>/\<UPSTREAM_REPO> workflow (branch: newsrx).

## Tasks

| Task | Purpose | Words |
| -- | -- | -- |
| `prepare` | Prepare branch for PR creation | ~450 |
| `checklist` | Run completion checklist | ~350 |
| `completion` | Ensure mandatory completion steps run regardless of workflow outcome | ~200 |

## Invocation

- `/skill finishing-a-development-branch` — Overview only
- `/skill finishing-a-development-branch --task prepare` — Prepare branch for PR
- `/skill finishing-a-development-branch --task checklist` — Run completion checklist
- `/skill finishing-a-development-branch --task completion` — Invoke when workflow halts at any point

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps (push, compare URL, status report) are never skipped. It is idempotent and safe to invoke multiple times.

## Operating Protocol

1. **Automatic invocation (strongly recommended):** This skill is auto-invoked when implementation completes on a feature branch, user says "done" or "finished" or "ready for PR", or before review-prep task in git-workflow.
2. **Verification-first approach:** All changes must be committed. All tests must pass. All lint/typecheck must pass. Branch must be pushed to remote.
3. **Exit conditions:** Branch is READY when all checklist items pass, compare URL is generated, and agent HALTs to report readiness.
4. **Worktree mandatory:** All feature branches operate in worktrees. If `WORKTREE_PATH` is not set: FATAL ERROR → FLAG DEV → HALT.

## Worktree Mode (MANDATORY)

If `WORKTREE_PATH` is not set or empty: **FATAL ERROR → FLAG DEV → HALT.** Do not proceed without a valid worktree path.

- All `bash` tool calls use `workdir="{{WORKTREE_PATH}}"`
- All `read`/`edit`/`write`/`glob`/`grep` tool calls prefix paths with `{{WORKTREE_PATH}}/`
- NEVER operate in the main working directory during implementation

## Lazy-Loaded Guidelines

When invoked, this skill requires the following guidelines to be loaded on-demand (they are not permanently loaded):

- **Load guideline:** `.opencode/guidelines/065-verification-honesty.md` — Required before branch completion verification claims

## Integration with Existing Workflow

### Dispatch Order

```
executing-plans → verification-before-completion → finishing-a-development-branch → review-prep → (PR creation by user)
```

### Git-Workflow Integration

- This skill runs BEFORE review-prep
- review-prep handles squash and push
- finishing-a-development-branch handles quality verification

### PR Creation

- This skill does NOT create PRs
- PR creation requires explicit "create a PR" instruction
- After checklist passes, report readiness and HALT

## Cross-References

- Related skills: `git-workflow` (branch management), `verification-before-completion` (evidence), `pr-creation-workflow` (PR timing)
- Related guidelines: `000-critical-rules.md` (review-prep required), `060-tool-usage.md` (build/lint commands)

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Fully supported — uses GitBucket compare URL format
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable
