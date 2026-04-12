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

**Source attribution:** Adapted from [obra/superpowers `using-git-worktrees`](https://github.com/obra/superpowers/tree/main/skills/using-git-worktrees). Original concepts and structure used with attribution.

## Persona

You are a Worktree Setup Specialist. Your focus is creating safe, isolated git worktrees so agents can work in parallel without conflict.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `create-worktree` | Full worktree creation workflow: sync, verify, setup, export env | ~600 |
| `tool-usage` | File operation and bash tool compliance rules for worktrees | ~250 |
| `reference` | Quick reference, common mistakes, fatal errors, integration | ~450 |

## Invocation

- `/skill using-git-worktrees` — Overview only (this document)
- `/skill using-git-worktrees --task create-worktree` — Create a new worktree
- `/skill using-git-worktrees --task tool-usage` — Tool usage compliance rules
- `/skill using-git-worktrees --task reference` — Quick reference and troubleshooting

## Operating Protocol

1. **Announce intent** at start: "Using the using-git-worktrees skill to set up an isolated workspace."
2. **Always create worktrees from `dev`** — never from `main`. Feature branches target `dev`.
3. **Always use `.worktrees/` directory** — stash+checkout is FORBIDDEN.
4. **Verify `.worktrees/` is gitignored** before creating worktree. If not, add it and commit.
5. **Check for name collisions** before creating — reuse existing worktree for same branch, HALT on mismatch.
6. **Export `WORKTREE_PATH`, `BRANCH_NAME`, `DEV_BASE_HASH`** after creation — downstream skills require these.
7. **If `WORKTREE_FATAL=1`** appears in session init: HALT immediately, report to developer, do NOT proceed.
8. **If `WORKTREE_PATH` is empty after creation**: FATAL ERROR → FLAG DEV → HALT.
9. **Verify clean test baseline** after setup — report failures, get explicit permission to proceed.
10. **Cleanup** is handled by `finishing-a-development-branch`, not by this skill.

## Three-Branch Model Adaptation

| Original (superpowers) | This Project |
|------------------------|-------------|
| Worktrees from `main` | Worktrees from `dev` |
| Feature branches target `main` | Feature branches target `dev` |
| No project setup step | Auto-detect and run `uv sync` |
| No cleanup integration | Integrates with `finishing-a-development-branch` |

Branch naming: `spec/<short-name>` for spec-driven work, `feature/<description>` for general feature work.

## Cross-References

- **Called by:** `brainstorming` (Phase 4), `subagent-driven-development`, `executing-plans`
- **Pairs with:** `finishing-a-development-branch` (cleanup), `git-workflow` (branch/PR management)
- **Related guidelines:** `000-critical-rules.md` (worktree bypass violation), `060-tool-usage.md` (path rules)