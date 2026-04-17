---
name: using-git-worktrees
description: Use when creating a feature branch or worktree for implementation. Always invoke before git-workflow pre-work. Triggers on: branch, worktree, feature branch, create worktree, pre-work, WORKTREE_PATH.
type: discipline-enforcing
license: MIT
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
| `completion` | Ensure mandatory terminal-state dispatch occurred; remediate if not; report status | ~200 |

## Invocation

- `/skill using-git-worktrees` — Overview only (this document)
- `/skill using-git-worktrees --task create-worktree` — Create a new worktree
- `/skill using-git-worktrees --task tool-usage` — Tool usage compliance rules
- `/skill using-git-worktrees --task reference` — Quick reference and troubleshooting
- `/skill using-git-worktrees --task completion` — Invoke when workflow halts at any point

## Operating Protocol

1. **Announce intent** at start: "Using the using-git-worktrees skill to set up an isolated workspace."
1. **Default base branch is `dev`** — never from `main`. For batch workflows, `BASE_BRANCH` may be a prior feature branch or batch branch. Feature branches target `dev`.
1. **Always use `.worktrees/` directory** — stash+checkout is FORBIDDEN.
1. **Verify `.worktrees/` is gitignored** before creating worktree. If not, add it and commit.
1. **Check for name collisions** before creating — reuse existing worktree for same branch, HALT on mismatch.
1. **Export `WORKTREE_PATH`, `BRANCH_NAME`, `DEV_BASE_HASH`** after creation — downstream skills require these.
1. **If `WORKTREE_FATAL=1`** appears in session init: HALT immediately, report to developer, do NOT proceed.
1. **If `WORKTREE_PATH` is empty after creation**: FATAL ERROR → FLAG DEV → HALT.
1. **Verify clean test baseline** after setup — report failures, get explicit permission to proceed.
1. **Cleanup** is handled by `finishing-a-development-branch`, not by this skill.

## Three-Branch Model Adaptation

| Original (superpowers) | This Project |
|------------------------|-------------|
| Worktrees from `main` | Worktrees from `dev` |
| Feature branches target `main` | Feature branches target `dev` |
| No project setup step | Auto-detect and run `uv sync` |
| No cleanup integration | Integrates with `finishing-a-development-branch` |

Branch naming: `spec/<short-name>` for spec-driven work, `feature/<description>` for general feature work, `batch/<short-name>` for batch aggregation branches.

**BASE_BRANCH parameter:** The `create-worktree` task supports creating worktrees from branches other than `dev`. Defaults to `dev` for standalone branches. In batch workflows, set to a prior feature branch (for dependency merge) or the batch branch. Agent decides at creation time based on context.

## Cross-References

- **Called by:** `brainstorming` (Phase 4), `divide-and-conquer`, `executing-plans`
- **Pairs with:** `finishing-a-development-branch` (cleanup), `git-workflow` (branch/PR management)
- **Related guidelines:** `000-critical-rules.md` (worktree bypass violation), `060-tool-usage.md` (path rules)

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps are never skipped. It is idempotent and safe to invoke multiple times.
