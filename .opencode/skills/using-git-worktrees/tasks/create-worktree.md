# Task: create-worktree

Create a git worktree for a feature branch, following the full creation workflow from sync through verification.

## Prerequisites

- Session init has been run
- `WORKTREE_FATAL` is NOT `1` (if it is, HALT immediately)
- Authorization received for the feature branch

## Steps

### 1. Announce Intent

State clearly: "Using the using-git-worktrees skill to set up an isolated workspace."

### 2. Sync with Base Branch

Create worktrees from an up-to-date base branch. The default base is `dev`, but for batch workflows where a batch branch already exists, the base can be the batch branch or another feature branch:

```bash
git checkout $BASE_BRANCH
git pull origin $BASE_BRANCH
```

**BASE_BRANCH defaults to `dev`** for standalone branches. In batch workflows, `BASE_BRANCH` may be set to a prior feature branch (for dependency merge) or the batch branch.

### 3. Detect Project Name

```bash
project=$(basename "$(git rev-parse --show-toplevel)")
```

### 3.5. Check for Worktree Name Collisions

Before creating a new worktree, check if a worktree for this branch already exists:

```bash
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

If a collision is detected with a different branch name, HALT and report to the developer.

### 3.6. Capture Dev Base Hash (Parallel Dispatch)

When multiple worktrees will be created for parallel dispatch (from `pre-implementation-analysis`), capture the dev branch hash BEFORE creating any worktrees:

```bash
DEV_BASE_HASH=$(git rev-parse --short 7 origin/dev)
```

Pass this hash in the dispatch context so all parallel worktrees start from the same base commit.

### 4. Create Worktree

```bash
# Determine branch name (spec/<name> or feature/<name>)
BRANCH_NAME="spec/<short-name>"

# Create worktree with new branch from BASE_BRANCH (defaults to dev)
git worktree add .worktrees/$BRANCH_NAME -b $BRANCH_NAME $BASE_BRANCH
```

**BASE_BRANCH** determines the starting point for the new branch:

- Default: `dev` (for standalone feature branches)
- Batch workflow: may be `dev`, a prior issue's feature branch (dependency chain), or the batch branch
- Agent decides the base branch at creation time based on context

Branch naming conventions:

- `spec/<short-name>` for spec-driven work
- `feature/<description>` for general feature work
- `batch/<short-name>` for batch aggregation branches

### 5. Verify Worktree Creation

After creation, verify the worktree exists:

```bash
git worktree list
# MUST show both main worktree and .worktrees/$BRANCH_NAME
```

If verification fails (worktree missing), HALT and report. Do NOT proceed without a valid worktree.

### 6. Run Project Setup

Auto-detect and run setup for this Python project. Use `workdir` parameter on tool calls — NEVER `cd`:

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

- **If tests fail:** Report failures, ask whether to proceed or investigate.
- **If tests pass:** Report ready.

### 8. Report Location

```
Worktree ready at .worktrees/spec-<short-name>
Tests passing (<N> tests, 0 failures)
Branch: spec/<short-name> (from dev)
Ready to implement <feature-name>
All commands use workdir=".worktrees/$BRANCH_NAME" — never cd
```

### 9. Export Worktree Environment Variables (MANDATORY)

After worktree creation, export environment variables that ALL downstream skills and sub-agents require:

```bash
export WORKTREE_PATH=".worktrees/$BRANCH_NAME_SANITIZED"
export BRANCH_NAME="$BRANCH_NAME"
export BASE_BRANCH="${BASE_BRANCH:-dev}"
export DEV_BASE_HASH=$(git rev-parse --short 7 origin/dev)
```

**If `WORKTREE_PATH` is not set or empty after this step: FATAL ERROR → FLAG DEV → HALT.** There is no alternative — worktree is the only method for feature branches.

These environment variables are consumed by:

- `git-workflow` tasks (review-prep, pr-creation, cleanup)
- `finishing-a-development-branch` skill
- `subagent-driven-development` dispatch context
- `divide-and-conquer` assemble-batch task
- `pre-implementation-analysis` execution plan
