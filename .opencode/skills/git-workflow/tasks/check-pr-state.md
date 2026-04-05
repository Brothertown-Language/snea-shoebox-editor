# Task: check-pr-state

## Purpose

Determine if branch has an existing PR (open, merged, or closed) before creating new PR.

## Workflow

This subtask is invoked by `pr-creation` task to check PR state.

## Returns

JSON result:
```json
{
  "branch": "<branch-name>",
  "pr_state": "<none|open|merged|closed>",
  "pr_number": <int|null>,
  "action": "<create_new_pr|update_existing|create_new_branch>"
}
```

## Procedure

### Step 1: Get Current Branch

```bash
CURRENT_BRANCH=$(git branch --show-current)
```

### Step 2: Query GitHub for Existing PRs

```python
prs = github_list_pull_requests(
    owner=GIT_OWNER,
    repo=GIT_REPO,
    head=CURRENT_BRANCH,
    state="all"
)

if not prs:
    return {"branch": CURRENT_BRANCH, "pr_state": "none", "pr_number": None, "action": "create_new_pr"}

for pr in prs:
    if pr["state"] == "open":
        return {
            "branch": CURRENT_BRANCH,
            "pr_state": "open",
            "pr_number": pr["number"],
            "action": "update_existing"
        }
    elif pr["state"] == "closed" and pr.get("merged_at"):
        return {
            "branch": CURRENT_BRANCH,
            "pr_state": "merged",
            "pr_number": pr["number"],
            "action": "create_new_branch"
        }
    elif pr["state"] == "closed":
        return {
            "branch": CURRENT_BRANCH,
            "pr_state": "closed",
            "pr_number": pr["number"],
            "action": "create_new_pr"
        }
```

### Step 3: Todo Tracking (Optional)

Use `todowrite` tool to track progress:

```json
[
  {"content": "Get current branch name", "status": "completed", "priority": "high"},
  {"content": "Query GitHub MCP for existing PRs", "status": "in_progress", "priority": "high"},
  {"content": "Determine PR state and action", "status": "pending", "priority": "high"}
]
```

### Step 4: Return Result

Return JSON result to calling task.

## Decision Tree

| PR State | Action | Next Step |
|----------|--------|-----------|
| None | `create_new_pr` | Continue with PR creation workflow |
| Open | `update_existing` | Update existing PR body |
| Merged | `create_new_branch` | Create new branch from current dev |
| Closed (not merged) | `create_new_pr` | Continue with PR creation workflow |

## Context Required

- Session init values: `GIT_OWNER`, `GIT_REPO`
- GitHub MCP tools available
