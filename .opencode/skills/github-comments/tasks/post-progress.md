# Task: post-progress

## Purpose

Post work-in-progress comment to GitHub Issue with proper formatting.

## Entry Criteria

- Work started on task
- Progress to report
- Issue number identified

## Exit Criteria

- Progress comment posted to GitHub Issue
- Summary and outcome documented
- Working status indicator included

## Procedure

### Step 1: Gather Progress Information

What work is in progress?
What has been completed so far?
What remains to be done?

### Step 2: Format Progress Comment

See `format-comment` task for template.

### Step 3: Post Comment

```python
github_add_issue_comment(
    owner=GIT_OWNER,
    repo=GIT_REPO,
    issue_number=N,
    body=formatted_comment
)
```

### Step 4: Log Progress

Record progress in local context if needed for follow-up tasks.

## Common Issues

| Issue | Resolution |
|-------|------------|
| Comment too long | Summarize key points, reference details |
| Missing outcome | Add what is expected to change |
| Duplicate posting | Check existing comments before posting |

## Context Required

- Session values: GIT_OWNER, GIT_REPO
- Related tasks: `format-comment`, `post-completion`
