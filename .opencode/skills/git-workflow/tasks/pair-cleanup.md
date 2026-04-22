# Pair-Mode Cleanup Task

Clean up pair-mode branches and stashes after PR merge.

## Steps

1. **Verify PR was merged:**
   ```bash
   # Use GitHub MCP to verify merge
   github_pull_request_read(method=get, owner=<owner>, repo=<repo>, pullNumber=<N>)
   ```
   Check that `merged_at` is not None.

2. **Switch to dev:**
   ```bash
   git checkout dev
   git pull origin dev
   ```

3. **Delete local pair branch:**
   ```bash
   git branch -d <pair-branch>
   ```

4. **Delete remote pair branch:**
   ```bash
   git push origin --delete <pair-branch>
   ```

5. **Clean up stale stashes (if any pair-related stashes exist):**
   ```bash
   git stash list | grep "pair-"
   ```
   For each matching stash, ask developer: "Resume or drop?"

6. **Clean up orphaned worktrees:**
   ```bash
   git worktree list --porcelain
   ```
   Remove any worktrees for the merged pair branch.

## Branch Deletion Discipline

- Delete merged pair branches IMMEDIATELY after merge confirmation
- Never keep merged pair branches around "just in case"
- Stashes from pair sessions: ask developer before dropping

## Result Contract

```yaml
status: DONE
task: pair-cleanup
branches_deleted: [<name>]
stashes_preserved: [<name>]
pr_merge_verified: bool
```