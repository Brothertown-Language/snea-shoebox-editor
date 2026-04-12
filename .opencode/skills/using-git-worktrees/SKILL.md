---
name: using-git-worktrees
description: Use when creating any feature branch. Always invoke before git-workflow pre-work. Triggers on: branch, feature branch, pre-work, worktree, new branch, checkout.
type: technique
license: MIT
compatibility: opencode
---

# Skill: using-git-worktrees

## Overview

Git worktrees create isolated workspaces sharing the same repository, allowing work on multiple branches simultaneously without switching. This skill adapts the [obra/superpowers using-git-worktrees](https://github.com/obra/superpowers/blob/main/skills/using-git-worktrees/SKILL.md) pattern for the `feature→dev→main` three-branch workflow used in this project.

**Core principle:** Systematic directory selection + safety verification = reliable isolation for parallel agent work.

**Announce at start:** "Using the using-git-worktrees skill to set up an isolated workspace."

**Source attribution:** This skill is adapted from [obra/superpowers `using-git-worktrees`](https://github.com/obra/superpowers/tree/main/skills/using-git-worktrees). Original concepts and structure are used with attribution.

## Persona

You are a Worktree Setup Specialist. Your focus is creating safe, isolated git worktrees so agents can work in parallel without conflict.

## Integration with Project Workflow

### Three-Branch Model Adaptation

The original obra/superpowers skill assumes a direct-to-main branch model. This adaptation changes:

| Original (superpowers) | This Project |
|------------------------|-------------|
| Worktrees from `main` | Worktrees from `dev` |
| Feature branches target `main` | Feature branches target `dev` |
| No project setup step | Auto-detect and run `uv sync` |
| No cleanup integration | Integrates with `finishing-a-development-branch` |

### Branch Naming

Feature branches in worktrees follow existing project conventions:
- `spec/<short-name>` for spec-driven work
- `feature/<description>` for general feature work

### Cleanup Integration

After work is complete and PR is merged, the worktree cleanup is handled by the `finishing-a-development-branch` skill's cleanup workflow. This skill does NOT handle cleanup.

## Directory Selection Process

Worktrees are ALWAYS created in `.worktrees/`. There is no alternative method. Stash+checkout is FORBIDDEN.

**If `WORKTREE_FATAL=1` appears in session init output:** HALT immediately and report the fatal error to the developer. Do NOT proceed with any implementation.

### Directory: `.worktrees/`

The project uses `.worktrees/` as the worktree directory. The `session_init.py` script bootstraps `.worktrees/main/` automatically. All feature worktrees are created under `.worktrees/`.

## Safety Verification

### For `.worktrees/` Directory

**MUST verify directory is ignored before creating worktree:**

```bash
git check-ignore -q .worktrees 2>/dev/null
```

**If NOT ignored:**

1. Add `.worktrees/` to `.gitignore`
2. Commit the change with message: "chore: add .worktrees/ to gitignore for worktree isolation"
3. Proceed with worktree creation

**Why critical:** Prevents accidentally committing worktree contents to repository.

## Creation Steps

### 1. Announce Intent

State clearly: "Using the using-git-worktrees skill to set up an isolated workspace."

### 2. Sync with Dev

```bash
git checkout dev
git pull origin dev
```

Always create worktrees from an up-to-date `dev` branch.

### 3. Detect Project Name

```bash
project=$(basename "$(git rev-parse --show-toplevel)")
```

### 3.5. Check for Worktree Name Collisions

Before creating a new worktree, check if a worktree for this branch already exists:

```bash
# Sanitize branch name for worktree directory (replace / with -)
BRANCH_NAME_SANITIZED=$(echo "$BRANCH_NAME" | tr '/' '-')
WT_PATH=".worktrees/$BRANCH_NAME_SANITIZED"

if git worktree list | grep -q "$WT_PATH"; then
    echo "Worktree $WT_PATH already exists. Checking branch match..."
    CURRENT_BRANCH=$(git -C "$WT_PATH" branch --show-current 2>/dev/null)
    if [ "$CURRENT_BRANCH" != "$BRANCH_NAME" ]; then
        echo "HALT: Worktree collision: $WT_PATH exists for branch $CURRENT_BRANCH, expected $BRANCH_NAME"
        # Report to developer — do not proceed
    else
        echo "Worktree $WT_PATH exists for correct branch. Reusing existing worktree."
        # Skip to Step 6 (Project Setup)
    fi
fi
```

If a collision is detected with a different branch name, HALT and report to the developer. Do not proceed with worktree creation.

### 3.6. Capture Dev Base Hash (Parallel Dispatch)

When multiple worktrees will be created for parallel dispatch (from `batch-approval-analysis`), capture the dev branch hash BEFORE creating any worktrees:

```bash
DEV_BASE_HASH=$(git rev-parse --short 7 origin/dev)
```

Pass this hash in the dispatch context so all parallel worktrees start from the same base commit.

### 4. Create Worktree

```bash
# Determine branch name (spec/<name> or feature/<name>)
BRANCH_NAME="spec/<short-name>"

# Create worktree with new branch from dev
git worktree add .worktrees/$BRANCH_NAME -b $BRANCH_NAME dev
```

### 5. Verify Worktree Creation

```bash
git worktree list
# Should show both main worktree and .worktrees/$BRANCH_NAME
```

### 6. Run Project Setup

Auto-detect and run appropriate setup for this Python project. Use `workdir` parameter on tool calls — NEVER `cd`:

```bash
# Use workdir parameter on Bash tool call:
# workdir=".worktrees/$BRANCH_NAME"
if [ -f pyproject.toml ]; then uv sync; fi
```

### 7. Verify Clean Baseline with Tests

Use `workdir` parameter on tool calls — NEVER `cd`:

```bash
# Use workdir parameter on Bash tool call:
# workdir=".worktrees/$BRANCH_NAME"
uv run pytest test/ -x
```

**If tests fail:** Report failures, ask whether to proceed or investigate.

**If tests pass:** Report ready.

### 8. Report Location

```
Worktree ready at .worktrees/spec-<short-name>
Tests passing (<N> tests, 0 failures)
Branch: spec/<short-name> (from dev)
Ready to implement <feature-name>
All commands use workdir=".worktrees/$BRANCH_NAME" — never cd
```

### 9. Export Worktree Environment Variables (MANDATORY)

After worktree creation, export environment variables that ALL downstream skills and sub-agents require. These are NOT optional — every skill that operates in a worktree MUST read these variables.

```bash
export WORKTREE_PATH=".worktrees/$BRANCH_NAME_SANITIZED"
export BRANCH_NAME="$BRANCH_NAME"
export DEV_BASE_HASH=$(git rev-parse --short 7 origin/dev)
```

**If `WORKTREE_PATH` is not set or empty after this step: FATAL ERROR → FLAG DEV → HALT.** There is no alternative — worktree is the only method for feature branches.

These environment variables are consumed by:
- `git-workflow` tasks (review-prep, pr-creation, cleanup)
- `finishing-a-development-branch` skill
- `subagent-driven-development` dispatch context
- `batch-approval-analysis` execution plan

## Tool Usage Compliance

**⚠️ CRITICAL: All commands in worktrees MUST use `workdir` parameter or relative paths from project root. NEVER use `cd` commands.**

Per AGENTS.md and `060-tool-usage.md`, `cd` commands are a zero-tolerance violation. When executing commands inside a worktree:

### Bash Tool (workdir parameter)

| Method | Example | Compliant? |
|--------|---------|------------|
| `workdir` parameter on Bash tool | `workdir=".worktrees/$BRANCH_NAME"` | ✅ YES |
| Relative path from project root | `uv run --directory .worktrees/$BRANCH_NAME pytest` | ✅ YES |
| `cd .worktrees/$BRANCH_NAME && ...` | `cd .worktrees/xyz && uv sync` | 🚫 NO — zero tolerance |

### File Operation Tools (filePath parameter) — CRITICAL

**The `read`, `edit`, `write`, `glob`, and `grep` tools do NOT have a `workdir` parameter.** When `WORKTREE_PATH` is set, relative paths resolve to the **main repo**, causing silent errors — edits go to the wrong file.

| Tool | ❌ WRONG (main repo) | ✅ CORRECT (worktree) |
|------|----------------------|---------------------|
| `read` | `read(filePath="src/main.py")` | `read(filePath=f"{WORKTREE_PATH}/src/main.py")` |
| `edit` | `edit(filePath="src/main.py", ...)` | `edit(filePath=f"{WORKTREE_PATH}/src/main.py", ...)` |
| `write` | `write(filePath="src/new.py", ...)` | `write(filePath=f"{WORKTREE_PATH}/src/new.py", ...)` |
| `glob` | `glob(pattern="src/**/*.py")` | `glob(pattern="src/**/*.py", path=WORKTREE_PATH)` |
| `grep` | `grep(pattern="TODO", path="src/")` | `grep(pattern="TODO", path=f"{WORKTREE_PATH}/src/")` |

**Rule:** When `WORKTREE_PATH` is set, every file operation tool call MUST prefix paths with the worktree path. No exceptions.

When **NOT** in a worktree (working in main repo), relative paths function correctly as-is.

## Verification Step

After worktree creation (step 5), verify the worktree actually exists before proceeding:

```bash
git worktree list
# MUST show the new worktree entry
# If missing → HALT and report — do NOT proceed without a valid worktree
```

**If verification fails:** The worktree was not created successfully. HALT and report the failure — do not proceed without a valid worktree.

## Quick Reference

| Situation | Action |
|-----------|--------|
| `.worktrees/` exists | Use it |
| `.worktrees/` not ignored | Add to `.gitignore` |
| `.worktrees/` missing | Create it and add to `.gitignore` |
| `WORKTREE_FATAL=1` in session init | HALT and report to developer |
| Tests fail during baseline | Report failures + ask |
| No `pyproject.toml` | Skip dependency install |

## Common Mistakes

### Skipping Ignore Verification

- **Problem:** Worktree contents get tracked, pollute git status
- **Fix:** Always use `git check-ignore` before creating project-local worktree

### Creating Worktree from Wrong Branch

- **Problem:** Worktree based on stale or wrong branch
- **Fix:** Always `git checkout dev && git pull origin dev` before creating worktree

### Proceeding with Failing Tests

- **Problem:** Can't distinguish new bugs from pre-existing issues
- **Fix:** Report failures, get explicit permission to proceed

### Not Announcing Worktree Creation

- **Problem:** Other agents unaware of parallel workspace
- **Fix:** Always announce "Using the using-git-worktrees skill to set up an isolated workspace" at start

## Fatal Error Protocol

**If `WORKTREE_FATAL=1` appears in session init output or worktree creation fails:**

1. HALT immediately — do NOT proceed with any implementation
2. Report the fatal error to the developer
3. Worktrees are the ONLY method for feature branches — stash+checkout is FORBIDDEN
4. The developer must fix the worktree infrastructure before any work can proceed

**Worktree setup failure means the repository infrastructure is broken.** Proceeding without worktrees risks:
- Parallel agent conflicts
- Dirty working trees
- Lost changes
- Branch contamination

Fix the worktree infrastructure, then proceed. Stash+checkout is FORBIDDEN

## Integration

### Called By

- **brainstorming** (Phase 4) - REQUIRED when design is approved and implementation follows
- **subagent-driven-development** (#555) - REQUIRED before executing any tasks
- **executing-plans** - REQUIRED before executing any tasks
- Any skill needing isolated workspace

### Pairs With

- **finishing-a-development-branch** - REQUIRED for cleanup after work complete
- **git-workflow** - Branch management and PR creation

### Cleanup After Merge

After the PR is merged, the worktree cleanup is handled by `finishing-a-development-branch` skill:

```bash
# Remove worktree
git worktree remove .worktrees/$BRANCH_NAME

# Prune stale worktree references
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
- HALT immediately if `WORKTREE_FATAL=1` appears in session init