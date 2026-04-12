---
name: finishing-a-development-branch
description: Use when implementation is complete and branch needs final checks before PR. Triggers on: done, finished, ready for PR, implementation complete, branch ready, push changes, final check.
type: technique
license: MIT
compatibility: opencode
---

# Skill: finishing-a-development-branch

## Overview

Branch completion workflow that ensures a feature branch is fully ready for PR creation. This skill verifies all changes are committed, tested, pushed, and reviewed before the developer creates a PR. It is adapted from the <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow.

**Source Attribution:** This skill is adapted from <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow (branch: newsrx).

## Persona

You are a Branch Finalizer. Your focus is ensuring no uncommitted changes, all verifications pass, and the branch is ready for review.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `prepare` | Prepare branch for PR creation | ~800 |
| `checklist` | Run completion checklist | ~500 |

## Invocation

- `/skill finishing-a-development-branch` - Overview only
- `/skill finishing-a-development-branch --task prepare` - Prepare branch for PR
- `/skill finishing-a-development-branch --task checklist` - Run completion checklist

## Operating Protocol

1. **Automatic invocation (strongly recommended):** This skill is auto-invoked by dispatch-table.yaml when:
   - Implementation completes on a feature branch
   - User says "done" or "finished" or "ready for PR"
   - Before review-prep task in git-workflow
   - DO NOT proceed to PR creation until checklist passes

2. **Verification-first approach:**
   - All changes must be committed
   - All tests must pass
   - All lint/typecheck must pass
   - Branch must be pushed to remote

3. **Exit conditions:** Branch is READY when:
   - All checklist items pass
   - Compare URL is generated
   - HALT and report readiness

## Prepare Branch Workflow

### Worktree Mode (MANDATORY — NO EXCEPTIONS)

All feature branches operate in worktrees. There is no alternative — worktree is the only method.

If `WORKTREE_PATH` is not set or empty: **FATAL ERROR → FLAG DEV → HALT.** Do not proceed without a valid worktree path.

1. All `bash` tool calls MUST use `workdir="{{WORKTREE_PATH}}"`
2. All `read`/`edit`/`write`/`glob`/`grep` tool calls MUST prefix `filePath`/`path` with `{{WORKTREE_PATH}}/` — these tools have NO `workdir` parameter and resolve relative paths against the main repo
3. Before any push/squash/rebase operation, verify:
   ```bash
   git branch --show-current
   # MUST match BRANCH_NAME
   ```
3. `git rev-parse --show-toplevel` MUST return the worktree path
4. NEVER operate in the main working directory during implementation

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

## Completion Checklist

```markdown
## Branch Completion Checklist

### Changes
- [ ] All changes committed
- [ ] No untracked files remaining
- [ ] Commit messages are descriptive
- [ ] Co-authored-by trailers present

### Code Quality
- [ ] `ruff check` passes (zero errors)
- [ ] `ruff format` applied
- [ ] `pyright` passes (zero errors)
- [ ] No dead code detected

### Tests
- [ ] All tests pass
- [ ] No skipped tests without reason
- [ ] New code has test coverage

### Branch
- [ ] Branch pushed to remote
- [ ] Upstream tracking set
- [ ] Compare URL generated
- [ ] Compare URL accessible

### Documentation
- [ ] AI co-authored attribution in new files
- [ ] Module docstrings present
- [ ] No narration print statements

### Ready for PR?
- [ ] All checklist items pass
- [ ] Compare URL verified
```

## Enforcement Mechanism

**⚠️ CRITICAL: Branch must be complete before PR creation.**

### Enforcement Matrix

| Situation | Action |
|-----------|--------|
| Uncommitted changes | COMMIT before proceeding |
| Lint errors | FIX before proceeding |
| Test failures | FIX before proceeding |
| Branch not pushed | PUSH before proceeding |
| Compare URL broken | FIX before proceeding |

### What Skills MUST Check

1. **Before reporting readiness:**
   - Is working tree clean?
   - Do all quality checks pass?
   - Is branch pushed?
   - Is compare URL accessible?

2. **During preparation:**
   - Are there leftover debug prints?
   - Are there TODO/FIXME comments?
   - Are there unrelated changes?

## Integration with Existing Workflow

### Dispatch Order

```
executing-plans → verification-before-completion → finishing-a-development-branch → review-prep → (PR creation by user)
```

### GitBucket Platform Adaptations

- Use GitBucket compare URL format
- Post completion summary to plan issue
- Generate compare URL for GitBucket instance

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

## Source Attribution

This skill is adapted from the <UPSTREAM_ORG>/<UPSTREAM_REPO> repository (branch: newsrx). The original workflow ensures branches are fully verified before PR creation.

**Key adaptations for OpenCode:**
- Integration with existing git-workflow skill
- GitBucket platform support with compare URL format
- Dispatch table integration for automatic invocation
- Quality checklist enforcement