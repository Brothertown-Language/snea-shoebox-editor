# Subtask: verify-stash-branch

## Purpose

Verify clean branch state and preserve external changes BEFORE branch creation. Invoked by `pre-work` task.

## Invocation

**Called by:** `pre-work` task at Step 1-4 (before feature branch creation)

**Call pattern:**
```
/task subagent_type="general" description="Verify stash-branch" prompt="Use the git-workflow skill verify-stash-branch subtask to verify clean working tree and preserve external changes before branch creation."
```

## Parameters

None. Reads current git state directly.

## Return Value

Returns JSON object to calling task:

```json
{
  "success": true,
  "branch_state": {
    "current_branch": "feature/issue-123",
    "is_main": false,
    "is_dev": false,
    "is_feature": true
  },
  "working_tree_state": {
    "clean": true,
    "stashed": false,
    "stash_ref": null
  }
}
```

**Failure return:**
```json
{
  "success": false,
  "error": "Stash failed - working tree still dirty after stash attempt",
  "details": "Files remaining: file1.py, file2.py"
}
```

## Procedure

### Step 1: Check Current Branch

```bash
git branch --show-current
```

Parse output:
- `main` → `is_main: true`, MUST create branch first
- `dev` → `is_dev: true`, MUST create branch first
- `feature/*` or `spec/*` → `is_feature: true`, may proceed
- Other → Report unexpected branch state

### Step 2: Check for Pending Changes

```bash
git status
```

If clean (no output or "nothing to commit, working tree clean"):
- Set `working_tree_state.clean: true`
- Set `working_tree_state.stashed: false`
- Return success

If dirty (modified/untracked files):
- Proceed to Step 3

### Step 3: Stash External Changes (If Needed)

If dirty working tree:

```bash
git stash push --include-untracked -m "WIP: external changes before <branch-name>"
git stash list  # VERIFY stash was created
git status      # VERIFY clean working tree
```

**CRITICAL VERIFICATION:**

After stash, run `git status` again:
- If CLEAN → Set `working_tree_state.stashed: true`, record stash ref
- If STILL DIRTY → STOP. Return failure with details.

```json
{
  "success": false,
  "error": "Stash failed - working tree still dirty after stash attempt",
  "details": "Files remaining after stash: <file list>"
}
```

**MANDATORY FAILURE:**

If `git status` STILL shows modifications after stash:
- DO NOT proceed
- Return failure immediately
- Report exact files remaining

### Step 4: Return Result

Return structured JSON to calling task with all state information.

## ⚠️ Edge Case: Already on Feature Branch

If already on a feature branch (`feature/*` or `spec/*`):

1. Verify working tree is clean (stash if needed)
2. Report ready for implementation
3. DO NOT create new branch (already have one)

Return:
```json
{
  "success": true,
  "branch_state": {
    "current_branch": "feature/existing-branch",
    "is_main": false,
    "is_dev": false,
    "is_feature": true,
    "already_exists": true
  },
  "working_tree_state": {
    "clean": true,
    "stashed": false
  }
}
```

## ⚠️ Edge Case: External Changes Stashed

If external changes were stashed:

Return:
```json
{
  "success": true,
  "branch_state": {
    "current_branch": "main",
    "is_main": true,
    "is_dev": false,
    "is_feature": false
  },
  "working_tree_state": {
    "clean": true,
    "stashed": true,
    "stash_ref": "stash@{0}",
    "stash_message": "WIP: external changes before feature/my-change"
  },
  "next_steps": ["Create feature branch from dev"]
}
```

Calling task must note the stash ref for later restoration.

## Safety Checks

Before returning success, verify ALL:

- [ ] `git status --porcelain` returns empty
- [ ] Current branch NOT `main` (unless feature branch will be created next)
- [ ] Stash ref recorded if stash was created

## Common Issues

| Issue | Resolution |
|-------|------------|
| Stash failed | Return failure. Let calling task report to user. |
| Already on feature branch | Return success with `already_exists: true` |
| Untracked files not stashed | Use `--include-untracked` flag |

## Context Required

- Guidelines: `110-git-branch-first.md` (Branch Before Edit)
- Guidelines: `114-git-branch-cleanup.md` (Branch Cleanup After Merge)

## Integration Notes

- Called by `pre-work` task before Step 5 (Create Feature Branch)
- Returns structured state for caller to proceed or halt
- Does NOT create branches (that's Step 5 in `pre-work`)
- Does NOT restore stashes (that's done post-implementation)
