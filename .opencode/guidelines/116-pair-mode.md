# Pair Mode Branch Discipline

## Overview

Pair mode (`pair-` prefix branches) allows the AI agent to work directly in the main project directory alongside the developer, using WIP-commit branch switching instead of worktrees. This is a Tier 2 waiver of the worktree mandate — the developer is present and accepting branch hygiene responsibility.

## Branch Naming

| Branch Pattern | Mode | Working Directory |
|---|---|---|
| `pair-feature/123-xyz` | Dev-pair | Main project dir |
| `pair-spec/456-abc` | Dev-pair | Main project dir |
| `feature/789-xyz` | Autonomous | `.worktrees/` |
| `spec/789-abc` | Autonomous | `.worktrees/` |
| `dev` or `main` | None | Prompt to create/switch |

The `pair-` prefix IS the mode signal. No state files needed — branch name carries everything.

## Mandatory Rules

### 1. Always Use `pair-` Prefix

No exceptions. If the developer is present and driving, use `pair-` prefix. If the AI is autonomous, use `feature/` or `spec/` with worktrees.

### 2. Never Operate in `.worktrees/` When Pair Mode Active

Pair mode branches work in the main project directory. Worktrees must not be created for pair mode branches.

### 3. WIP Commits Before Branch Switches

Before any branch switch in pair mode, the AI MUST:

1. Check `git status --porcelain`
2. If changes exist: `git add -A && git commit -m "WIP: <description>"` with co-author trailers
3. `git checkout <target-branch>`
4. On return, optionally `git reset HEAD~1` to uncommit the WIP

### 4. Commit Trailers Include `[pair-mode]`

Pair mode commits include:

```
Co-authored-by: Human Name <human@email> [pair-mode]
Co-authored-by: AI: <AgentName> (<ModelId>) [pair-mode]
```

The `[pair-mode]` tag distinguishes these from autonomous mode commits.

### 5. PR Body Uses `Implements #N`

Never `Fixes` or `Closes` — avoids premature issue closure. Use `Implements #N` to link without auto-closing.

## Session Detection

The `session_context.py` plugin detects pair mode at session start when the current branch starts with `pair-`. It emits:

- Identity section (always): `github.owner`, `github.repo`, `github.platform`, credential status
- Pair mode resume context: branch name, related issue, diff summary
- Trigger warnings: `on_main_branch`, `protected_branch_with_changes`, `uncommitted_work`

## Task Sequence

```
Session start → pair-mode-resume detects pair-* branch
    ↓
pair-pre-work: WIP-commit switch (no worktree)
    ↓
(pair commits as needed during work)
    ↓
pair-pr-creation: Squash → Push → Create PR
    ↓
(Developer merges PR)
    ↓
pair-cleanup: Delete branch, clean stashes
```

## Tier 2 Worktree Waiver

Pair mode is a Tier 2 waiver of the Tier 1 worktree mandate (per `000-critical-rules.md` Mandate Tiering). The developer is present and accepts responsibility for:

- Branch hygiene (no accidental commits to `dev`/`main`)
- WIP commit cleanup after branch switches
- Merge conflict awareness

The `pair-` prefix IS the waiver signal. No additional configuration or state files are required.

## Issue Association

When on a `pair-` branch:

- Infer issue number from branch name: `pair-feature/123-xyz` → issue #123
- Ask: "Commit for issue #123?" before committing
- If branch has no issue number, ask: "Which issue is this for?"

## Prohibited Actions in Pair Mode

- Creating worktrees for pair mode branches
- Committing directly to `dev` or `main` (hooks enforce this)
- Using `Fixes` or `Closes` in PR body (use `Implements`)
- Skipping WIP commit before branch switches
- Omitting `[pair-mode]` tag from commit trailers