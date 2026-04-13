# Task: check-pr

## Purpose

List all PRs (open and merged) for the repository. If merged PRs with uncleaned branches are detected, activate the `cleanup` task. If only open PRs exist, report and HALT.

## Entry Triggers

- "check pr"
- "check prs"
- "check pull request"
- "check pull requests"

## Procedure

### Step 1: Query All PRs

```python
# List open PRs
open_prs = github_list_pull_requests(
    owner=GIT_OWNER, repo=GIT_REPO, state="open", perPage=50
)

# List merged PRs
merged_prs = github_list_pull_requests(
    owner=GIT_OWNER, repo=GIT_REPO, state="closed", perPage=50
)
# Note: GitHub "closed" includes both merged and unmerged; filter by merged_at
merged_prs = [pr for pr in merged_prs if pr.get("merged_at") is not None]
```

### Step 2: Report PR Status

Report all PRs found:

```
**Open PRs:** <count>
<list of PR #, title, branch>

**Merged PRs:** <count>
<list of PR #, title, branch, merged_at>
```

### Step 3: Decision

| Condition | Action |
| -- | -- |
| Merged PRs exist with local branches | Activate `--task cleanup` |
| Merged PRs exist, no local branches | Report "already cleaned up" |
| Only open PRs exist | Report PRs and HALT |
| No PRs exist | Report "No PRs found" and HALT |

### Step 4: If Cleanup Needed

Delegates to `cleanup` task — do NOT duplicate cleanup logic here.

```python
# If any merged PR has an uncleaned local branch:
# Invoke cleanup task
invoke("--task cleanup")
```

## Exit Criteria

- All PRs listed (open and merged)
- If merged PRs with branches → cleanup activated
- If only open PRs → reported and HALT