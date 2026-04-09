---
name: using-git-worktrees
description: Use when starting feature work that needs isolation from current workspace, before executing implementation plans, or when working with multiple agents in parallel. Triggers on: worktree, isolated workspace, parallel agent, worktree setup, branch isolation, concurrent work, set up worktree.
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

Follow this priority order:

### 1. Check Existing Directories

```bash
ls -d .worktrees 2>/dev/null     # Preferred (hidden)
ls -d worktrees 2>/dev/null      # Alternative
```

**If found:** Use that directory. If both exist, `.worktrees` wins.

### 2. Check AGENTS.md / Project Config

```bash
# Check for worktree directory preference in project files
grep -i "worktree" AGENTS.md .opencode/AGENTS.md 2>/dev/null
```

**If preference specified:** Use it without asking.

### 3. Default to Project-Local

If no directory exists and no preference found, default to `.worktrees/` (project-local, hidden).

## Safety Verification

### For Project-Local Directories (.worktrees or worktrees)

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

### 4. Create Worktree

```bash
# Determine branch name (spec/<name> or feature/<name>)
BRANCH_NAME="spec/554-git-worktrees-skill"

# Create worktree with new branch from dev
git worktree add .worktrees/$BRANCH_NAME -b $BRANCH_NAME dev
```

### 5. Verify Worktree Creation

```bash
git worktree list
# Should show both main worktree and .worktrees/$BRANCH_NAME
```

### 6. Run Project Setup

Auto-detect and run appropriate setup for this Python project:

```bash
cd .worktrees/$BRANCH_NAME

# This project uses uv
if [ -f pyproject.toml ]; then uv sync; fi
```

### 7. Verify Clean Baseline with Tests

```bash
cd .worktrees/$BRANCH_NAME
uv run pytest test/ -x
```

**If tests fail:** Report failures, ask whether to proceed or investigate.

**If tests pass:** Report ready.

### 8. Report Location

```
Worktree ready at .worktrees/spec/554-git-worktrees-skill
Tests passing (<N> tests, 0 failures)
Branch: spec/554-git-worktrees-skill (from dev)
Ready to implement <feature-name>
```

## Quick Reference

| Situation | Action |
|-----------|--------|
| `.worktrees/` exists | Use it (verify ignored) |
| `worktrees/` exists | Use it (verify ignored) |
| Both exist | Use `.worktrees/` |
| Neither exists | Create `.worktrees/` and add to `.gitignore` |
| Directory not ignored | Add to `.gitignore` + commit |
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
- Follow directory priority: existing > AGENTS.md > default `.worktrees/`
- Verify directory is ignored for project-local
- Auto-detect and run `uv sync` for project setup
- Announce worktree creation at start
- Create branch from `dev` (not `main`)
- Verify clean test baseline