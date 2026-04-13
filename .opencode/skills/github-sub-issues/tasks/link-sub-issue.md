# Task: link-sub-issue

## Purpose

Link a sub-issue to its parent plan issue using database ID (not issue number).

## Entry Criteria

- Sub-issue created
- Sub-issue database ID available
- Plan issue number identified

## Exit Criteria

- Sub-issue linked to plan via GitHub's sub-issue feature
- Link visible in plan issue's task list

## Procedure

### Step 1: Get Sub-Issue Database ID

**CRITICAL: Must use database ID, not issue number.**

```python
# When creating sub-issue, database ID is in response
sub_issue = github_issue_write(method="create", ...)
db_id = sub_issue["id"]  # This is the database ID
```

**If sub-issue already exists:**
```python
sub_issue = github_issue_read(method="get", issue_number=M)
db_id = sub_issue["id"]
```

### Step 2: Link to Plan

```python
github_sub_issue_write(
    method="add",
    owner=GIT_OWNER,
    repo=GIT_REPO,
    issue_number=M,           # Plan issue NUMBER (not ID)
    sub_issue_id=db_id        # Sub-issue DATABASE ID (not number)
)
```

### Step 3: Verify Link

```python
sub_issues = github_issue_read(method="get_sub_issues", issue_number=M)
# Verify sub_issue is now in the list
```

## Common Issues

| Issue | Resolution |
|-------|------------|
| Used issue number instead of ID | Get .id field from issue response |
| Link returns error | Verify plan and sub-issue both exist |
| Sub-issue not appearing | Call get_sub_issues to verify link |

## Context Required

- Session values: GIT_OWNER, GIT_REPO
- Related tasks: `create-sub-issue`, `track-hierarchy`