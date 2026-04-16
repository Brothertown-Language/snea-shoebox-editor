# GitBucket MCP Operations

## Overview

GitBucket MCP tools are available for most operations. When MCP tools are unavailable, use Python tooling from `tools/` directory.

## MCP Tool Availability

| Operation | MCP Tool | Fallback |
|-----------|----------|----------|
| Get issue | `gitbucket_get_issue` ✅ | Python API |
| Create issue | `gitbucket_create_issue` ✅ | Python API |
| Update issue | `gitbucket_update_issue` ✅ | Python API |
| Add comment | `gitbucket_add_issue_comment` ✅ | Python API |
| List issues | `gitbucket_list_issues` ✅ | Python API |
| Get repository | `gitbucket_get_repository` ✅ | Python API |
| List branches | `gitbucket_list_branches` ✅ | Python API |
| Add labels | ❌ No MCP tool | **Python API only** |
| Replace labels | ❌ No MCP tool | **Python API only** |
| Remove labels | ❌ No MCP tool | **Python API only** |
| Admin operations | ❌ No MCP tool | **Python API only** |

## MCP-First Workflow

**When MCP tools available:**

```python
# Prefer MCP tool
from tools import gitbucket_get_issue, gitbucket_create_issue

# Create issue
issue = gitbucket_create_issue(
    owner="org",
    repo="project",
    title="Bug fix",
    body="Description",
    labels=["bug", "enhancement"]
)
```

**When MCP tools unavailable:**

```python
# Use Python tooling
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()

# Create issue
issue = api.create_issue(
    owner="org",
    repo="project",
    title="Bug fix",
    body="Description",
    labels=["bug", "enhancement"]
)
```

## Tool Selection Decision Tree

```
Is operation in MCP table?
    ├─ YES → Use MCP tool
    │         ├─ Success → Return result
    │         └─ Failure → Log MCPToolError, fallback to Python API
    └─ NO → Use Python API directly
```

## Error Classification

### MCP Tool Error (Retry or Fallback)

```python
from skills.gitbucket_api.tools import MCPToolError

try:
    issue = gitbucket_get_issue(owner, repo, issue_number)
except MCPToolError as e:
    # MCP tool failed - can retry or fallback
    logger.warning(f"MCP tool {e.tool} failed: {e.message}")
    # Fallback to Python API
    api = GitBucketAPI()
    issue = api.get_issue(owner, repo, issue_number)
```

### API Error (Classified)

```python
from skills.gitbucket_api.tools import AuthenticationError, NotFoundError, ValidationError

try:
    api = GitBucketAPI()
    issue = api.create_issue(...)
except AuthenticationError as e:
    # 401 - Check credentials
    logger.error(f"Auth failed: {e.message}")
    raise
except NotFoundError as e:
    # 404 - Check URL format
    logger.error(f"Not found: {e.endpoint}")
    raise
except ValidationError as e:
    # 422 - Check request body
    logger.error(f"Validation error: {e.message}")
    raise
```

## Label Operations (Python API Only)

GitBucket MCP does **not** provide label tools. Use Python API:

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()

# Add labels (auto-creates missing labels)
api.add_labels_to_issue(
    owner="org",
    repo="project",
    issue_number=14,
    labels=["bug", "enhancement"]
)

# Replace all labels
api.replace_issue_labels(
    owner="org",
    repo="project",
    issue_number=14,
    labels=["priority", "review"]
)

# Remove specific label
api.remove_label_from_issue(
    owner="org",
    repo="project",
    issue_number=14,
    label_name="bug"
)

# Remove all labels
api.remove_all_labels_from_issue(
    owner="org",
    repo="project",
    issue_number=14
)
```

## Admin Operations (Basic Auth Required)

Admin operations require Basic authentication, not token:

```python
from skills.gitbucket_api.tools import GitBucketAPI

# Initialize with Basic auth
api = GitBucketAPI(
    url="https://gitbucket.example.com/gitbucket/",
    username="admin",
    password="admin_password"
)

# Create user (admin only)
user = api.create_user(
    username="developer1",
    password="secure_password",
    email="developer1@example.com",
    is_admin=False
)

# Create organization (admin only)
org = api.create_organization(
    name="my-team",
    description="Development team"
)
```

## Source Code

- `tools/gitbucket_api.py` - Core client with all endpoints
