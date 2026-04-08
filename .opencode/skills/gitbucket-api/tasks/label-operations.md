# GitBucket Label Operations

## Overview

GitBucket label operations using Python API tools.

## Add Labels to Issue

**⚠️ BROKEN: Returns empty array `[]`, labels are NOT added**

The GitBucket API endpoint `POST /repos/{owner}/{repo}/issues/{number}/labels` returns HTTP 200 with an empty array but does NOT add labels to the issue.

**Workaround:** Add labels during issue creation with `create_issue(labels=[...])`.

### Python API (Only Option)

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()

# ❌ BROKEN: Labels NOT added, returns empty array
labels = api.add_labels_to_issue(
    owner="org",
    repo="project",
    issue_number=14,
    labels=["bug", "enhancement"]
)
# Returns: [] — labels are NOT added to the issue

# ✅ WORKAROUND: Add labels during issue creation
issue = api.create_issue(
    owner="org",
    repo="project",
    title="Bug report",
    body="Description",
    labels=["bug", "enhancement"]  # ✅ Auto-creates and attaches labels
)
```

## Replace All Labels

**⚠️ BROKEN: Returns empty array `[]`, labels are NOT set**

The GitBucket API endpoint `PUT /repos/{owner}/{repo}/issues/{number}/labels` returns HTTP 200 with an empty array but does NOT set labels on the issue.

**Workaround:** Add labels during issue creation with `create_issue(labels=[...])`.

### Python API (Only Option)

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()

# ❌ BROKEN: Labels NOT set, returns empty array
labels = api.replace_issue_labels(
    owner="org",
    repo="project",
    issue_number=14,
    labels=["priority", "review"]
)
# Returns: [] — labels are NOT set on the issue

# ✅ WORKAROUND: Add labels during issue creation
issue = api.create_issue(
    owner="org",
    repo="project",
    title="Bug report",
    body="Description",
    labels=["priority", "review"]  # ✅ Works, auto-creates labels
)
```

## Remove Specific Label

### Python API (Only Option)

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()

# Remove one label
api.remove_label_from_issue(
    owner="org",
    repo="project",
    issue_number=14,
    label_name="bug"
)
```

## Remove All Labels

### Python API (Only Option)

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()

# Remove all labels
api.remove_all_labels_from_issue(
    owner="org",
    repo="project",
    issue_number=14
)
```

## Repository Labels

### List Labels

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()
labels = api.list_labels(owner="org", repo="project")
```

### Create Label

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()
label = api.create_label(
    owner="org",
    repo="project",
    name="bug",
    color="ff0000"
)
```

## Tool Selection

| Operation | Python API |
|-----------|------------|
| Add labels | `api.add_labels_to_issue()` | ⚠️ BROKEN (returns `[]`) |
| Replace labels | `api.replace_issue_labels()` | ⚠️ BROKEN (returns `[]`) |
| Remove label | `api.remove_label_from_issue()` |
| Remove all labels | `api.remove_all_labels_from_issue()` |
| List labels | `api.list_labels()` |
| Create label | `api.create_label()` |

**Note:** GitBucket Python API is the primary tool for all label operations.

## Error Handling

```python
from skills.gitbucket_api.tools import GitBucketAPI
from skills.gitbucket_api.tools.exceptions import ValidationError

api = GitBucketAPI()

try:
    api.add_labels_to_issue(...)
except ValidationError as e:
    # 422 - Invalid label name or format
    print(f"Validation error: {e.message}")
```

## Source Code

- `tools/gitbucket_api.py` - `add_labels_to_issue()`, `replace_issue_labels()`, `remove_label_from_issue()`, `remove_all_labels_from_issue()`, `list_labels()`, `create_label()`