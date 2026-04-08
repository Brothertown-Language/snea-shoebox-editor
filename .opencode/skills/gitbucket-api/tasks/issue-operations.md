# GitBucket Issue Operations

## Overview

Issue CRUD operations using GitBucket Python API client.

**Primary Tool: Python client from `.opencode/skills/gitbucket-api/tools/gitbucket_api.py`**

**CRITICAL: The `gitbucket_*` MCP tools have been REMOVED. The Python client is the ONLY option. Use `from skills.gitbucket_api.tools import GitBucketAPI` for all operations.**

## Response Types

**ALL `list_*` methods return arrays:**
- `list_issues()` → `list[dict]`
- `get_issue()` → `dict`

**Always check type before iterating:**
```python
issues = api.list_issues(owner="org", repo="project")
# type: list[dict]

issue = api.get_issue(owner="org", repo="project", issue_number=14)
# type: dict
```

## Basic Operations

### Create Issue

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()
issue = api.create_issue(
    owner="org",
    repo="project",
    title="Issue title",
    body="Issue body",
    labels=["enhancement", "bug"],  # ✅ Auto-creates labels
    assignees=["username"],
    milestone=5
)
# Returns: single Issue object (dict)
print(f"Created issue #{issue['number']}")
```

**Fields supported:**
- `title` (required) - Issue title
- `body` (optional) - Issue description
- `labels` (optional) - Array of label names (auto-created)
- `assignees` (optional) - Array of usernames
- `milestone` (optional) - Milestone number

### Get Issue

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()
issue = api.get_issue(owner="org", repo="project", issue_number=14)
# Returns: single Issue object (dict)
print(f"Issue title: {issue['title']}")
print(f"State: {issue['state']}")
print(f"Labels: {[l['name'] for l in issue['labels']]}")
```

### Update Issue

**⚠️ BROKEN: Returns 404 Not Found**

GitBucket does NOT implement `PATCH /repos/{owner}/{repo}/issues/{issue_number}`.

```python
from skills.gitbucket_api.tools import GitBucketAPI

# ❌ THIS DOES NOT WORK - Returns 404
api = GitBucketAPI()
issue = api.update_issue(
    owner="org",
    repo="project",
    issue_number=14,
    title="New title",
    body="New body"
)
# Raises NotFoundError: 404 Not Found
```

**Workaround:** Use GitBucket web UI to update issue title, body, or state. There is no API for updating existing issues.

### List Issues

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()
issues = api.list_issues(
    owner="org",
    repo="project",
    state="open",      # "open", "closed", or "all"
    labels="bug,enhancement"  # Comma-separated label names
)
# Returns: array of Issue objects (list[dict])
for issue in issues:
    print(f"#{issue['number']}: {issue['title']}")
```

### Add Comment

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()
comment = api.add_issue_comment(
    owner="org",
    repo="project",
    issue_number=14,
    body="Comment text"
)
# Returns: Comment object (dict)
```

## Chained Operations

### Workflow 1: Create Issue with Labels and Comments

**Scenario:** Create issue, add labels, assign user, add welcome comment.

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()

# Step 1: Create issue with labels
issue = api.create_issue(
    owner="org",
    repo="project",
    title="Bug: Login fails on mobile",
    body="## Description\n\nLogin fails on mobile devices.\n\n## Steps to Reproduce\n\n1. Open mobile browser\n2. Navigate to login page\n3. Enter credentials\n4. Click login\n\n## Expected Behavior\n\nShould authenticate successfully.",
    labels=["bug", "priority:high"]
)
print(f"Created issue #{issue['number']}")

# Step 2: Add welcome comment
api.add_issue_comment(
    owner="org",
    repo="project",
    issue_number=issue['number'],
    body="**Status:** Issue created and under investigation.\n\nWe'll look into this shortly."
)

# Step 3: Update issue (add assignee)
api.update_issue(
    owner="org",
    repo="project",
    issue_number=issue['number'],
    assignees=["developer-name"]
)

print(f"Issue #{issue['number']} created with labels and assigned")
```

### Workflow 2: Parent/Child Issue Management

**Scenario:** Create parent spec issue and child task issues, link via comments.

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()

# Step 1: Create parent spec issue
parent_issue = api.create_issue(
    owner="org",
    repo="project",
    title="[SPEC] Add OAuth2 Authentication",
    body="#" Spec: OAuth2 Authentication\n\n## Objective\n\nImplement OAuth2 authentication for the application.\n\n## Phases\n\n1. OAuth2 Client Setup\n2. Token Management\n3. Session Handling\n4. UI Integration\n\n## Success Criteria\n\n- Users can authenticate via OAuth2\n- Tokens refresh automatically\n- Sessions persist across page reloads",
    labels=["enhancement", "spec"]
)
print(f"Parent issue #{parent_issue['number']} created")

# Step 2: Create child task issues
phases = [
    "OAuth2 Client Setup",
    "Token Management",
    "Session Handling",
    "UI Integration"
]

child_issues = []
for i, phase in enumerate(phases, 1):
    child = api.create_issue(
        owner="org",
        repo="project",
        title=f"[Task: #{parent_issue['number']}] Phase {i}: {phase}",
        body=f"Parent Issue: #{parent_issue['number']}\n\n**Scope:**\n\nImplement {phase.lower()} for OAuth2 authentication.\n\nSee parent issue for full details.",
        labels=["task"]
    )
    child_issues.append(child)
    print(f"Child issue #{child['number']} created")

# Step 3: Add comment to parent listing children
child_list = "\n".join([f"- #{c['number']}: {phases[i]}" for i, c in enumerate(child_issues)])
api.add_issue_comment(
    owner="org",
    repo="project",
    issue_number=parent_issue['number'],
    body=f"**Sub-issues created:**\n\n{child_list}"
)

print(f"Parent #{parent_issue['number']} with {len(child_issues)} child issues created")
```

### Workflow 3: Close Issue with Summary Comment

**Scenario:** Close issue after completion, add summary comment.

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()

# Step 1: Add completion comment
api.add_issue_comment(
    owner="org",
    repo="project",
    issue_number=14,
    body="""✅ Completed by OpenCode

**Summary:**

Implemented OAuth2 authentication with automatic token refresh.

**Outcome:**

Users can now authenticate via OAuth2, and tokens refresh automatically without user intervention.

**Verification:**

- OAuth2 client configured
- Token management implemented
- Session handling tested
- UI integration complete"""
)

# Step 2: Close issue
api.update_issue(
    owner="org",
    repo="project",
    issue_number=14,
    state="closed"
)

print("Issue #14 closed with summary comment")
```

### Workflow 4: Batch Label Operations

**⚠️ CRITICAL: `update_issue()` and post-creation label APIs are BROKEN in GitBucket.**

- `update_issue()` returns 404
- `add_labels_to_issue()` returns `[]`, labels NOT added
- `replace_issue_labels()` returns `[]`, labels NOT set

**Labels can ONLY be set during `create_issue()`.** There is no working API for changing labels after issue creation.

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()

# ✅ WORKS: Set labels during issue creation
issue = api.create_issue(
    owner="org",
    repo="project",
    title="Bug report",
    body="Description",
    labels=["bug", "priority:high", "needs-review"]
)

# ❌ BROKEN: Cannot change labels after creation
# api.add_labels_to_issue(...) → returns []
# api.replace_issue_labels(...) → returns []
# api.update_issue(labels=[...]) → returns 404
```

**Workaround:** Delete and recreate the issue if labels need to change.

### Workflow 5: Find and Close Duplicate Issues

**Scenario:** Find duplicate issues and close them with reference to original.

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()

# Step 1: Get the canonical issue
canonical_issue = api.get_issue(
    owner="org",
    repo="project",
    issue_number=14
)

# Step 2: List all open issues
all_issues = api.list_issues(
    owner="org",
    repo="project",
    state="open"
)

# Step 3: Find duplicates (same title)
duplicates = [
    issue for issue in all_issues
    if issue['title'] == canonical_issue['title'] and issue['number'] != canonical_issue['number']
]

print(f"Found {len(duplicates)} duplicates")

# Step 4: Close each duplicate with comment
for dup in duplicates:
    # Add comment
    api.add_issue_comment(
        owner="org",
        repo="project",
        issue_number=dup['number'],
        body=f"**Closing as duplicate of #{canonical_issue['number']}**\n\nThis issue is a duplicate and is being closed. Please continue discussion on #{canonical_issue['number']}."
    )
    
    # Close issue
    api.update_issue(
        owner="org",
        repo="project",
        issue_number=dup['number'],
        state="closed",
        labels=["duplicate"]
    )
    
    print(f"Closed duplicate #{dup['number']}")

print(f"All {len(duplicates)} duplicates closed")
```

## Error Handling

```python
from skills.gitbucket_api.tools import GitBucketAPI
from skills.gitbucket_api.tools.exceptions import (
    AuthenticationError,
    NotFoundError,
    ValidationError,
    GitBucketError
)

api = GitBucketAPI()

try:
    issue = api.create_issue(
        owner="org",
        repo="nonexistent",
        title="Test"
    )
except AuthenticationError as e:
    # 401 - Check GITBUCKET_TOKEN
    print(f"Auth failed: {e.message}")
except NotFoundError as e:
    # 404 - Repo doesn't exist
    print(f"Not found: {e.endpoint}")
except ValidationError as e:
    # 422 - Invalid input
    print(f"Validation error: {e.message}")
except GitBucketError as e:
    # Other HTTP errors
    print(f"API error: {e.status_code} - {e.message}")
```

## Complete API Reference

| Operation | Method | Returns |
|-----------|--------|---------|
| Create issue | `create_issue()` | `dict` |
| Get issue | `get_issue()` | `dict` |
| Update issue | `update_issue()` | `dict` ⚠️ BROKEN (404) |
| List issues | `list_issues()` | `list[dict]` |
| Add comment | `add_issue_comment()` | `dict` |
| Add labels | `add_labels_to_issue()` | `list[dict]` |
| Replace labels | `replace_issue_labels()` | `list[dict]` |
| Remove label | `remove_label_from_issue()` | `None` |
| Remove all labels | `remove_all_labels_from_issue()` | `None` |

## Source Code

- `tools/gitbucket_api.py` - All issue methods
- `tools/exceptions.py` - Exception classes