# Task: prepare

## Purpose

Prepare a feature branch for PR creation by ensuring all changes are committed, quality checks pass, and the branch is pushed to remote.

## Operating Protocol

1. Invoked by: `/skill finishing-a-development-branch --task prepare`
2. When to use: When implementation is complete and branch needs final preparation
3. Exit criteria: Working tree clean, all quality checks pass, branch pushed, compare URL generated

## Worktree Mode (MANDATORY — NO EXCEPTIONS)

All feature branches operate in worktrees. There is no alternative.

If `WORKTREE_PATH` is not set or empty: **FATAL ERROR → FLAG DEV → HALT.** Do not proceed without a valid worktree path.

1. All `bash` tool calls MUST use `workdir="{{WORKTREE_PATH}}"`
2. All `read`/`edit`/`write`/`glob`/`grep` tool calls MUST prefix `filePath`/`path` with `{{WORKTREE_PATH}}/`
3. Before any push/squash/rebase: `git branch --show-current` MUST match BRANCH_NAME
4. `git rev-parse --show-toplevel` MUST return the worktree path
5. NEVER operate in the main working directory during implementation

## Prepare Branch Workflow

### Step 1: Verify All Changes Committed

```bash
git status --porcelain
```

- If output is not empty → Stage and commit remaining changes
- Verify commit messages are descriptive
- Verify co-authored-by trailers are present

### Step 2: Run Code Quality Checks

```bash
# Lint
uv run ruff check --fix src/ test/

# Format
uv run ruff format src/ test/

# Type check
uv run pyright src/
```

- All checks must pass with zero errors
- Warnings should be addressed but don't block

### Step 3: Run Tests

```bash
uv run pytest test/ -x
```

- All tests must pass
- No skipped tests without documented reason

### Step 4: Verify Branch Pushed

```bash
git push -u origin <branch>
git branch -vv
```

- Branch must have upstream tracking
- Remote must have latest commits

### Step 5: Generate Compare URL

```
https://gitbucket.newsrx.com/gitbucket/<owner>/<repo>/compare/<base>...<branch>
```

- URL must be accessible
- Diff must show expected changes

## Enforcement Matrix

| Situation | Action |
|-----------|--------|
| Uncommitted changes | COMMIT before proceeding |
| Lint errors | FIX before proceeding |
| Test failures | FIX before proceeding |
| Branch not pushed | PUSH before proceeding |
| Compare URL broken | FIX before proceeding |

## Context Required

- Related skills: `finishing-a-development-branch` (parent skill), `verification-before-completion` (evidence)
- Related tasks: `checklist`