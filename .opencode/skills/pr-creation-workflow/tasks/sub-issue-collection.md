# Task: sub-issue-collection

## Purpose

Fetch sub-issues for a parent issue and build the autoclose list for the PR body.

## Procedure

### Single-Task Spec

If the spec has no sub-issues (single-task), include only the parent issue in the PR body:

```
Fixes #<parent>
```

### Multi-Task Spec with Sub-Issues

1. **Fetch sub-issues:**
   ```python
   sub_issues = github_issue_read(method="get_sub_issues", issue_number=<parent>)
   ```

2. **Build autoclose list:** parent + all sub-issues
   ```python
   autoclose_issues = [<parent>] + [sub["number"] for sub in sub_issues]
   ```

3. **Include ALL issues in PR body:**
   ```markdown
   ## Summary
   <description of what changed>

   Fixes #<parent>
   Fixes #<child1>
   Fixes #<child2>
   ```

### Multi-Task Spec WITHOUT Sub-Issues

If `get_sub_issues` returns empty for a multi-task spec, this is a CRITICAL VIOLATION — sub-issues should have been created before implementation. Halt and create sub-issues first.

## Example PR Bodies

**Single-task:**
```markdown
## Summary
Add OAuth2 authentication to the API layer.

Fixes #42
```

**Multi-task:**
```markdown
## Summary
Implement user authentication feature: database schema, API endpoints, and UI components.

Fixes #100
Fixes #101
Fixes #102
Fixes #103
```

## After PR Creation

- Report URL in chat ONLY (never to GitHub Issues)
- HALT — wait for human to merge
- Never merge PRs — HUMAN-ONLY operation