# Task: implementation

## Purpose

Handle work-in-progress commits during implementation. Multiple commits during implementation are acceptable for checkpointing.

## Operating Protocol

1. **User-driven work:** The agent performs approved implementation tasks
2. **Checkpoint commits allowed:** Commits during implementation serve to stage changes and prevent accidental loss
3. **Squashing is deferred:** Squashing to single commit happens during PR creation, not during implementation

## Entry Criteria

- Feature branch exists and is checked out
- Implementation authorized for this phase/task
- Working tree clean (or stashed)

## Exit Criteria

- All implementation work complete for authorized phase/task
- Changes committed (implementation commits acceptable)
- Ready for review and PR preparation

## Procedure

### Making Implementation Commits

Commits during implementation are checkpoint commits to prevent data loss. They do NOT need to be polished.

```bash
git add <files>
git commit -m "WIP: <descriptive message>"
```

**No co-author trailers required** during implementation commits - those are added during squash at PR time.

### ⚠️ CRITICAL: Commit Before Push

**The most common workflow failure is pushing without committing.**

**Correct sequence:**
```
1. Make file changes (edit tool, etc.)
2. git status (verify changes exist)
3. git add -A (stage changes)
4. git commit (commit changes)
5. git push (push committed branch)
```

**Incorrect sequence (CRITICAL VIOLATION):**
```
1. Make file changes
2. git push (WRONG - uncommitted changes)
   Result: Empty branch on remote
   Result: GitHub compare shows "nothing to compare"
```

**Verification before push:**
- `git status` MUST show "nothing to commit, working tree clean"
- Local branch MUST have at least one commit ahead of remote
- If `git status` shows uncommitted changes → COMMIT FIRST

## Multiple Commits Are Acceptable

| Commit Type | When | Message | Trailers |
|-------------|------|---------|----------|
| Implementation commit | During work | `WIP: description` | None |
| Squash commit | PR creation | Descriptive | Full co-author trailers |

## Important Rules

- **DO NOT squash until PR creation** - Multiple implementation commits are expected
- **DO NOT create PR without explicit instruction** - PR requires explicit "create a PR"
- **ALWAYS push after committing** - Push ensures GitHub compare works correctly

## Context Required

- Guidelines: `111-git-commit-workflow.md`
- Related skills: `approval-gate` (authorization scope)
- Related tasks: `commit-prep` (squash for PR), `pr-creation` (push and PR)

## When to Commit During Implementation

Commit when:
- Completing a discrete logical unit of work
- Reaching a checkpoint that might need rollback
- Before attempting something risky
- At natural break points in the work

## After Implementation Completes

1. **Commit all changes** (`git add -A && git commit`)
2. **Push to remote** (`git push -u origin <branch-name>`)
3. **Report completion** (executive summary to issue AND chat)
4. **HALT** — do NOT create PR
5. **WAIT** for explicit "create a PR" instruction

**See:** `pr-creation-workflow` skill for complete PR workflow.