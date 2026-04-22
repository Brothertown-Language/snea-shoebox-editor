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

### ⚠️ CRITICAL: File Operation Tool Paths in Worktree

When `worktree.path` is set, ALL file operation tool calls (`read`, `edit`, `write`, `glob`, `grep`) MUST prefix paths with the worktree path. These tools have NO `workdir` parameter — relative paths resolve to the main repo, causing silent errors.

| Tool | Wrong (operates on main repo) | Correct (targets worktree) |
| -- | -- | -- |
| `read` | `read(filePath="src/main.py")` | `read(filePath=f"{worktree.path}/src/main.py")` |
| `edit` | `edit(filePath="src/main.py", ...)` | `edit(filePath=f"{worktree.path}/src/main.py", ...)` |
| `write` | `write(filePath="src/new.py", ...)` | `write(filePath=f"{worktree.path}/src/new.py", ...)` |
| `glob` | `glob(pattern="src/**/*.py")` | `glob(pattern="src/**/*.py", path=worktree.path)` |
| `grep` | `grep(pattern="TODO", path="src/")` | `grep(pattern="TODO", path=f"{worktree.path}/src/")` |

**For `bash` tool:** Continue using `workdir` parameter as documented in `using-git-worktrees` skill.

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
| -- | -- | -- | -- |
| Implementation commit | During work | `WIP: description` | None |
| Squash commit | PR creation | Descriptive | Full co-author trailers |

## Important Rules

- **DO NOT squash during implementation** - Multiple implementation commits on feature branches are normal and acceptable
- **Squashing is ONLY at PR creation time** - The `squash` in "squash-merge to main via PR" refers to PR merge, not feature branch development
- **DO NOT create PR without explicit instruction** - PR requires explicit "create a PR"
- **ALWAYS push after committing** - Push ensures GitHub compare works correctly

## Context Required

- Related skills: `approval-gate` (authorization scope)
- Related tasks: `pr-creation` (push and PR)

## Live Verification (MANDATORY)

**🚫 CRITICAL: Verify git state via tool calls before each commit during implementation. Assertions without tool-call artifacts are VERIFICATION-GAP findings.**

### Pre-Commit Verification

| Check | Tool Call | Expected Result | On Failure |
| -- | -- | -- | -- |
| On correct branch | `git branch --show-current` | Feature branch (not `main`/`dev`) | STRUCTURE-VIOLATION → HALT |
| Worktree location | `git rev-parse --show-toplevel` | Worktree path | STRUCTURE-VIOLATION → HALT |
| Changes to commit | `git status --porcelain` | Expected modified files listed | MISSING-ELEMENT → no changes found |
| Staged state matches intent | `git diff --staged` | Intended changes visible | VERIFICATION-GAP → re-stage |

### Verification Procedure

**Before each implementation commit, run:**

```
1. git branch --show-current → EVIDENCE: <feature-branch-name>
2. git rev-parse --show-toplevel → EVIDENCE: <worktree-path>
3. git status --porcelain → EVIDENCE: <modified files or "(empty)">
4. git diff --staged → EVIDENCE: <staged changes or "(empty)">
```

**After each implementation commit, verify:**

```
1. git log --oneline -1 → EVIDENCE: commit hash and message visible
2. git status --porcelain → EVIDENCE: "(empty)" if all committed
```

### Finding Classification

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| On `main` or `dev` | CONFLICTING | flag-for-review | HALT — must be in worktree on feature branch |
| Wrong toplevel path | STRUCTURE-VIOLATION | auto-fix | HALT — not in worktree, re-invoke pre-work |
| No changes to commit | MISSING-ELEMENT | conditional | Verify changes were saved — may need `git add` |
| Staged changes don't match intent | VERIFICATION-GAP | conditional | Review diff, adjust staging |

**These verifications are MANDATORY before each commit. Skipping them is a CRITICAL GUIDELINE VIOLATION.**

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
