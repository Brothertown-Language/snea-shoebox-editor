# Pair-Mode Pre-Work Task

Detect pair mode from branch prefix and set up WIP-commit switching instead of worktree creation.

## Detection

Check current branch name:
```bash
BRANCH=$(git branch --show-current)
```

If `$BRANCH` starts with `pair-`, pair mode is active.

## WIP-Commit Switching (instead of worktree creation)

When pair mode is active (branch name starts with `pair-`):

1. **Check for uncommitted changes:**
   ```bash
   git status --porcelain
   ```

2. **If changes exist, create WIP commit:**
   ```bash
   git add -A
   git commit -m "WIP: $(git branch --show-current) [pair-mode]

   Co-authored-by: $DEV_NAME <$DEV_EMAIL>
   Co-authored-by: AI: $AGENT_NAME ($MODEL_ID) [pair-mode]"
   ```

3. **If no changes but on protected branch (`dev`/`main`):**
   - Prompt developer: "You're on `$BRANCH`. Which issue should we work on?"
   - Create pair branch: `git checkout -b pair-feature/<issue>-<desc>`
   - No worktree needed — working directly in main directory

4. **If switching to existing pair branch:**
   ```bash
   git checkout <pair-branch>
   ```

## Pair Mode vs Autonomous Mode

| Aspect | Autonomous Mode | Pair Mode |
|--------|----------------|-----------|
| Branch prefix | `feature/`, `spec/` | `pair-` |
| Working directory | `.worktrees/` | Main project dir |
| Branch switching | Worktree per branch | WIP commit + checkout |
| Worktree safety | Tier 1 mandate | Tier 2 — developer present |
| Commit trailers | Standard co-author | `[pair-mode]` tag |

## Result Contract

```yaml
status: DONE | BLOCKED
task: pair-pre-work
pair_mode: bool
branch_name: <str>
wip_commit_created: bool
working_directory: <path>
```