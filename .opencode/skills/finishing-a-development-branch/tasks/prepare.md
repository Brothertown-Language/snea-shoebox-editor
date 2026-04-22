# Task: prepare

## Purpose

Prepare a feature branch for PR creation by ensuring all changes are committed, quality checks pass, and the branch is pushed to remote.

## Operating Protocol

1. Invoked by: `/skill finishing-a-development-branch --task prepare`
2. When to use: When implementation is complete and branch needs final preparation
3. Exit criteria: Working tree clean, all quality checks pass, branch pushed, compare URL generated

## Worktree Mode (MANDATORY — NO EXCEPTIONS)

All feature branches operate in worktrees. There is no alternative.

If `worktree.path` is not set or empty: **FATAL ERROR → FLAG DEV → HALT.** Do not proceed without a valid worktree path.

1. All `bash` tool calls MUST use `workdir="{{worktree.path}}"`
2. All `read`/`edit`/`write`/`glob`/`grep` tool calls MUST prefix `filePath`/`path` with `{{worktree.path}}/`
3. Before any push/squash/rebase: `git branch --show-current` MUST match branch
4. `git rev-parse --show-toplevel` MUST return the worktree path
5. NEVER operate in the main working directory during implementation

## Step 0: Sync Dev Branch (Fast-Forward Only)

**Before running quality checks, ensure local dev is current.** If dev has been updated by other merges since this branch was created, running checks on a stale base produces incorrect results.

```bash
git fetch origin dev
git pull origin dev --ff-only
```

**The `--ff-only` flag is MANDATORY.** A plain `git pull origin dev` can silently succeed with a merge commit, hiding divergence. The `--ff-only` flag ensures dev fast-forwards cleanly.

**If `--ff-only` pull fails (diverged history):**

```bash
# HALT and report. Suggest manual resolution:
echo "ERROR: local dev has diverged from origin/dev"
echo "Suggest: git pull --rebase origin dev"
echo "Or manual resolution required"
# HALT — do NOT proceed with stale codebase
# Do NOT create merge commits on dev
```

**If dev is already up to date:** The ff-only pull is a no-op and proceeds instantly.

**Worktree context:** If running from a worktree, `git pull` must target the main working tree's dev, not the worktree. Use `git -C /path/to/main/repo pull origin dev --ff-only` to ensure operations target the main tree.

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

1. Read `<github.owner>`, `<github.repo>`, `<gitbucket.html_url>` from session init
2. Construct the Compare URL using those exact values
3. **Character-match verification:** Confirm the constructed URL contains the exact `<github.owner>` and `<github.repo>` strings from session init (character-for-character match)
4. If any mismatch: HALT and report

## Enforcement Matrix

| Situation | Action |
| -- | -- |
| Uncommitted changes | COMMIT before proceeding |
| Lint errors | FIX before proceeding |
| Test failures | FIX before proceeding |
| Branch not pushed | PUSH before proceeding |
| Compare URL broken | FIX before proceeding |

## Context Required

- Related skills: `finishing-a-development-branch` (parent skill), `verification-before-completion` (evidence)
- Related tasks: `checklist`

## Live Verification: Preparation Claims (MANDATORY)

**Each preparation step MUST produce a tool-call artifact. Assertions without artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Working tree clean" | Verify no uncommitted changes | `git status --porcelain` | VERIFICATION-GAP |
| "Lint passes" | Run lint command and check result | `uvx ruff check src/ test/` | VERIFICATION-GAP |
| "Tests pass" | Run test command and check result | `uv run pytest test/` | VERIFICATION-GAP |
| "All changes relevant to spec" | Verify diff file list matches spec scope | `git diff dev --name-only` → compare with spec | CONFLICTING |

**Evidence artifact:** Tool call output for each verification step.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Uncommitted changes exist | VERIFICATION-GAP | conditional | Commit first |
| Lint failures | VERIFICATION-GAP | flag-for-review | HALT — fix before PR |
| Test failures | VERIFICATION-GAP | flag-for-review | HALT — fix before PR |
| Unrelated changes in diff | CONFLICTING | flag-for-review | Report — scope deviation |
