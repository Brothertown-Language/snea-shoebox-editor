# Task: pr-creation/squash-push

## Purpose

Squash implementation commits to a single commit (for single-issue branches) or verify existing commit structure (for work branches), rebase on current dev, and push to remote.

## Entry Criteria

- Enforcement gates passed (pr-creation/enforcement-gate)
- Implementation is complete and committed

## Exit Criteria

- Single clean commit on feature branch (single-issue) OR verified work branch structure
- Branch rebased on current dev
- Branch pushed to remote with force-with-lease
- Working tree clean

## Procedure

### Step 2: Changelog Generation (MANDATORY)

Check for `[skip changelog]` in last commit message or PR title. If present, skip.

If not present, execute: `/skill changelog-generator --since-last-release`

Then stage: `git add CHANGELOG.md`

**Enforcement gate:** Verify `git status --porcelain CHANGELOG.md` shows `M` or `A` before proceeding. If changelog not staged and no skip directive — HALT.

### Step 3: Squash to Single Commit

**Branch type determines strategy:**

| Branch Type | Squash Strategy |
| -- | -- |
| **Single-issue branch** | All commits squashed to ONE commit |
| **Work branch** | One commit per implementation item (N commits is correct) |

#### Single-Issue Branch (Default)

```bash
git reset --soft origin/dev
git commit -m "<descriptive message>" \
    --trailer "Co-authored-by: <AgentName> (<ModelId>) <noreply@example.com>" \
    --trailer "Co-authored-by: <dev.name> <dev.email>"
```

#### Work Branch

If `.opencode/tmp/work-*.md` exists, this is a work branch — skip squash. Verify commit structure instead.

### Step 3.5: Rebase on Current Dev (MANDATORY)

```bash
git fetch origin
git rebase origin/dev
```

**If conflicts occur:** HALT and report conflicts to the developer. List conflicting files.

**This step is MANDATORY even if review-prep just ran a rebase.** Dev may have been updated since.

### Step 4: Push to Remote

```bash
git push --force-with-lease origin <branch>
```

## Worktree Mode (MANDATORY — NO EXCEPTIONS)

All feature branches operate in worktrees. If `worktree.path` is not set: **FATAL ERROR → HALT.**

1. All `bash` tool calls MUST use `workdir="{{worktree.path}}"`
2. All `read`/`edit`/`write`/`glob`/`grep` tool calls MUST prefix with `{{worktree.path}}/`
3. Before any push/squash/rebase: verify `git branch --show-current` matches expected branch
4. `git rev-parse --show-toplevel` MUST return the worktree path
5. NEVER operate in the main working directory during implementation

## Live Verification (MANDATORY)

After squash and before push:

| Check | Command | Expected |
| -- | -- | -- |
| Working tree clean | `git status --porcelain` | Empty |
| Staged changes correct | `git diff --staged` | Only intended changes |
| No unstaged changes | `git diff` | Empty |
| Commits ahead of dev | `git log origin/dev..HEAD --oneline` | Expected commit(s) |
| Branch tracking | `git branch -vv` | `[origin/<branch>]` |
| Worktree path correct | `git rev-parse --show-toplevel` | Worktree path |

## Recovery from Accidental Protected Branch Commit

```bash
git branch feature/recovery HEAD
git checkout dev
git reset --hard origin/dev
git checkout feature/recovery
git push origin feature/recovery
```

## Context Required

- Related tasks: `pr-creation/enforcement-gate`, `pr-creation/create-pr`
- Related guidelines: `000-critical-rules.md` (co-author trailers)