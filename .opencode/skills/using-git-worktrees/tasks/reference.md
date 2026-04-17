# Task: reference

Quick reference, common mistakes, fatal error protocol, and integration details.

## Safety Verification

MUST verify `.worktrees/` is ignored before creating worktree:

```bash
git check-ignore -q .worktrees 2>/dev/null
```

If NOT ignored:
1. Add `.worktrees/` to `.gitignore`
2. Commit the change with message: "chore: add .worktrees/ to gitignore for worktree isolation"
3. Proceed with worktree creation

## Quick Reference

| Situation | Action |
|-----------|--------|
| `.worktrees/` exists | Use it |
| `.worktrees/` not ignored | Add to `.gitignore` |
| `.worktrees/` missing | Create it and add to `.gitignore` |
| `worktree.fatal=1` in session init | HALT and report to developer |
| Tests fail during baseline | Report failures + ask |
| No `pyproject.toml` | Skip dependency install |

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Skipping ignore verification | Worktree contents tracked, pollute git status | Always use `git check-ignore` before creating |
| Creating worktree from `main` | Based on wrong branch | Always `git checkout dev && git pull origin dev` first |
| Proceeding with failing tests | Can't distinguish new bugs from pre-existing | Report failures, get explicit permission |
| Not announcing worktree creation | Other agents unaware of parallel workspace | Always announce at start |

## Fatal Error Protocol

If `worktree.fatal=1` appears in session init output or worktree creation fails:

1. HALT immediately — do NOT proceed with any implementation
2. Report the fatal error to the developer
3. Worktrees are the ONLY method for feature branches — stash+checkout is FORBIDDEN
4. The developer must fix the worktree infrastructure before any work can proceed

Worktree setup failure means the repository infrastructure is broken. Proceeding without worktrees risks:
- Parallel agent conflicts
- Dirty working trees
- Lost changes
- Branch contamination

Fix the worktree infrastructure, then proceed. Stash+checkout is FORBIDDEN.

## Integration

### Called By

- **brainstorming** (Phase 4) — REQUIRED when design is approved and implementation follows
- **divide-and-conquer** — REQUIRED before executing any tasks
- **executing-plans** — REQUIRED before executing any tasks
- Any skill needing isolated workspace

### Pairs With

- **finishing-a-development-branch** — REQUIRED for cleanup after work complete
- **git-workflow** — Branch management and PR creation

### Cleanup After Merge

After PR merge, worktree cleanup is handled by `finishing-a-development-branch`:

```bash
git worktree remove .worktrees/$BRANCH_NAME
git worktree prune
```

This cleanup happens as part of the standard `git-workflow --task cleanup` sequence.

## Red Flags

**Never:**
- Create worktree without verifying it's ignored (project-local)
- Create worktree from `main` (always branch from `dev`)
- Skip baseline test verification
- Proceed with failing tests without asking
- Assume directory location when ambiguous
- Handle worktree cleanup in this skill (delegated to `finishing-a-development-branch`)

**Always:**
- Use `.worktrees/` directory (the only method)
- Verify directory is ignored for project-local
- Auto-detect and run `uv sync` for project setup
- Announce worktree creation at start
- Create branch from `dev` (not `main`)
- Verify clean test baseline
- HALT immediately if `worktree.fatal=1` appears in session init