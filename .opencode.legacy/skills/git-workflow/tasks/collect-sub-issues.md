# Task: collect-sub-issues

## Purpose

Collect sub-issues for multi-task specs to build autoclose list for PR body.

## Workflow

This subtask is invoked by `pr-creation` task to get sub-issues.

## Returns

JSON result:
```json
{
  "parent_issue": <int>,
  "sub_issues": [<int>, ...],
  "autoclose_list": [<int>, ...],
  "is_single_task": <bool>
}
```

## Procedure

### Step 1: Determine Parent Issue

Parent issue is the spec that authorized this work.

For feature branches named `feature/issue-NNN-...`: parent = NNN

### Step 2: Query Sub-Issues

```python
sub_issues = github_issue_read(
    method="get_sub_issues",
    issue_number=parent_issue,
    owner=GIT_OWNER,
    repo=GIT_REPO
)
```

### Step 3: Build Result

```python
if not sub_issues:
    # Single-task spec
    return {
        "parent_issue": parent_issue,
        "sub_issues": [],
        "autoclose_list": [parent_issue],
        "is_single_task": True
    }

# Multi-task spec
sub_issue_numbers = [sub["number"] for sub in sub_issues]
autoclose_list = [parent_issue] + sub_issue_numbers

return {
    "parent_issue": parent_issue,
    "sub_issues": sub_issue_numbers,
    "autoclose_list": autoclose_list,
    "is_single_task": False
}
```

### Step 4: Todo Tracking (Optional)

Use `todowrite` tool to track progress:

```json
[
  {"content": "Determine parent issue from branch", "status": "completed", "priority": "high"},
  {"content": "Query GitHub MCP for sub-issues", "status": "in_progress", "priority": "high"},
  {"content": "Build autoclose list", "status": "pending", "priority": "high"}
]
```

## PR Body Format

| Spec Type | Fixes Format |
|-----------|-------------|
| Single-task | `Fixes #<parent>` |
| Multi-task | `Fixes #<parent>` AND `Fixes #<child>` for each sub-issue |

### Multi-Task Example

```markdown
## Summary

Implemented subtask architecture for git-workflow skill.

## Changes

### Features
- Added check-pr-state subtask
- Added collect-sub-issues subtask

Fixes #371
Fixes #373
Fixes #374
Fixes #375
Fixes #376
```

## Context Required

- Session init values: `GIT_OWNER`, `GIT_REPO`
- GitHub MCP tools available
- Parent issue number (from feature branch name or spec)

## Edge Cases

| Case | Result |
|------|--------|
| Parent issue not found | HALT with error |
| Sub-issues query fails | HALT with error |
| Empty sub-issues list | Return single-task format |
