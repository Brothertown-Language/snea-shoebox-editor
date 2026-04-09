# Task: post-completion

## Purpose

Post completion comment to GitHub Issue when task is finished.

## Entry Criteria

- Task completed successfully
- All sub-tasks finished
- Issue number identified

## Exit Criteria

- Completion comment posted to GitHub Issue
- Summary and outcome documented
- Completed status indicator included

## Procedure

### Step 1: Gather Completion Information

What was accomplished?
What changed for stakeholders?
Were there any blockers resolved?

### Step 2: Format Completion Comment

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

### Step 4: Note Completion

If all tasks complete from this spec, include "All tasks complete from this specification."

## Common Issues

| Issue | Resolution |
|-------|------------|
| Missing summary | Add 1-2 sentence impact |
| No outcome | State what changed |
| Premature completion | Verify all sub-tasks done |

## Context Required

- Session values: GIT_OWNER, GIT_REPO
- Related tasks: `format-comment`, `post-progress`
