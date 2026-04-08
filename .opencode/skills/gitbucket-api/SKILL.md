---
name: gitbucket-api
description: GitBucket API patterns and capabilities using OpenAPI specification and Python client. Documents actual API responses, authentication patterns, and error recovery.
license: MIT
compatibility: opencode
---

# GitBucket API Skill

## Role

You are a GitBucket API specialist focused on correct API usage patterns using the OpenAPI specification and Python client.

## Overview

GitBucket implements a GitHub-compatible API v3. This skill documents:
- Official OpenAPI v4.42.1 specification with 32 endpoints
- Actual API response schemas from testing
- Python client usage (primary tool)
- Error recovery patterns

**CRITICAL: The `gitbucket_*` MCP tool functions (gitbucket_get_issue, gitbucket_create_issue, etc.) have been REMOVED from opencode. The Python client at `.opencode/skills/gitbucket-api/tools/` is the ONLY way to use the GitBucket API. The Rust-based `gitbucket-mcp-server` had a bug causing all `list_*` tools to fail with "expected record, received array" — it has been removed from the opencode config. Use the Python client exclusively.**

## OpenAPI Specification

Official OpenAPI spec: `.opencode/skills/gitbucket-api/reference/openapi-v4.42.1.json`

**API Coverage:**
- 32 documented endpoints
- Authentication: Token auth (`Authorization: token YOUR_TOKEN`)
- Base URL: `{scheme}://{host}/api/v3`
- Schemas: User, Repository, Issue, PullRequest, Branch, Commit, Release, Label, Milestone, Webhook, etc.

## When to Use

Invoke this skill when:
- Working with GitBucket repositories (detected from remote URL)
- Creating/updating GitBucket issues
- Managing labels on GitBucket issues
- Debugging GitBucket API failures ("Bad credentials")

## Response Schemas (Actual API Behavior)

**CRITICAL: All `list_*` endpoints return arrays, NOT objects.**

| Endpoint | Returns | Type | Verified |
|----------|---------|------|----------|
| `list_issues` | Array of Issue objects | `List[Dict]` | ✅ Tested |
| `list_pull_requests` | Array of PR objects | `List[Dict]` | ✅ Tested |
| `list_branches` | Array of Branch objects | `List[Dict]` | ✅ Tested |
| `list_releases` | Array of Release objects | `List[Dict]` | ✅ Tested |
| `list_labels` | Array of Label objects | `List[Dict]` | ✅ Tested |
| `list_milestones` | Array of Milestone objects | `List[Dict]` | ✅ Tested |
| `list_user_repositories` | Array of Repo objects | `List[Dict]` | ✅ Tested |
| `list_users` | Array of User objects | `List[Dict]` | ✅ Tested |
| `get_issue` | Single Issue object | `Dict` | ✅ Tested |
| `get_repository` | Single Repo object | `Dict` | ✅ Tested |

**Testing performed on:** `NewSRX-Tech-LLC/Documentation` repository

## API Compatibility Matrix

| Operation | GitHub API | GitBucket API | Status |
|-----------|------------|---------------|--------|
| Token auth GET/POST | ✅ Works | ✅ Works | Use token for all operations |
| Token auth PATCH/PUT/DELETE | ✅ Works | ⚠️ Partial | PATCH/PUT work, but some endpoints return empty responses |
| Basic auth | ✅ Works | ❌ "Bad credentials" | Token only |
| Create issue with labels | ✅ Works | ✅ Works | Labels in create call, auto-creates labels |
| Add labels to issue | ✅ Works | ❌ BROKEN | Returns empty array, labels NOT added |
| Replace all labels | ✅ Works | ❌ BROKEN | Returns empty array, labels NOT set |
| Remove label from issue | ✅ Works | ❓ Not tested | May have same issue as add/replace |
| Remove all labels | ✅ Works | ❓ Not tested | May have same issue as add/replace |
| Update issue (PATCH) | ✅ Works | ❌ 404 | GitBucket doesn't implement this endpoint |
| Auto-create missing labels | ❌ Fails | ✅ Works | GitBucket creates labels automatically |

**⚠️ DEFICIENCIES:** See `API-DEFICIENCIES.md` for detailed test results and workarounds.

**POST-UPGRADE TEST (2026-04-06):**
- All 14 core endpoints working: ✅
- `update_issue()` PATCH: ❌ Returns 404
- `add_labels_to_issue()` POST: ❌ Returns 200 with empty array, labels NOT added
- `replace_issue_labels()` PUT: ❌ Returns 200 with empty array, labels NOT set

**WORKAROUND FOR LABELS:** Use `create_issue(labels=[...])` to add labels during issue creation. Label management operations do NOT work after issue creation.

## Endpoint Categories

| Category | Endpoints | Description |
|----------|-----------|-------------|
| **Users & Auth** | `/user`, `/users`, `/users/{username}` | Authenticated user, list/get users |
| **Repositories** | `/user/repos`, `/orgs/{org}/repos`, `/repos/{owner}/{repo}` | List/create repos |
| **Issues** | `/repos/{owner}/{repo}/issues{/:number}` | List/create/get issues |
| **Pull Requests** | `/repos/{owner}/{repo}/pulls{/:number}` | List/create/get PRs |
| **Branches** | `/repos/{owner}/{repo}/branches` | List branches |
| **Git Data** | `/repos/{owner}/{repo}/git/refs/{ref}`, `/contents/{path}`, `/statuses/{sha}` | Refs, contents, commit statuses |
| **Releases** | `/repos/{owner}/{repo}/releases` | List/create releases |
| **Labels** | `/repos/{owner}/{repo}/labels` | List/create labels |
| **Milestones** | `/repos/{owner}/{repo}/milestones` | List/create milestones |
| **Webhooks** | `/repos/{owner}/{repo}/hooks` | List/create webhooks |
| **Admin** | `/admin/users`, `/admin/organizations` | Create user/org (admin only) |

## Authentication

### ✅ CORRECT: Token Authentication (ONLY working method)

GitBucket requires token authentication. Basic auth does NOT work.

```python
# Session init provides these values:
GITBUCKET_HTML_URL = os.environ.get("GITBUCKET_HTML_URL") or os.environ.get("GITBUCKET_URL")
GITBUCKET_TOKEN = os.environ.get("GITBUCKET_TOKEN")

# Use token in Authorization header:
headers = {
    "Authorization": f"token {GITBUCKET_TOKEN}",
    "Content-Type": "application/json",
}
```

### 🚫 NON-FUNCTIONAL: Basic Authentication

**Basic auth is broken in GitBucket** — it returns "Bad credentials" for all requests.
Username and password parameters are retained in the API client for forward-compatibility
only. Do NOT attempt to use basic auth.

```python
# WRONG: Basic auth always fails with "Bad credentials"
import base64
credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
headers = {"Authorization": f"Basic {credentials}"}  # ❌ WILL FAIL
```

**This means:** GITBUCKET_USERNAME and GITBUCKET_PASSWORD in .env are non-functional.
Only GITBUCKET_HTML_URL and GITBUCKET_TOKEN are required.

## Python Client (Primary Tool)

**Use the Python client from `.opencode/skills/gitbucket-api/tools/` for all GitBucket API operations.**

### Tool Structure

```
.opencode/skills/gitbucket-api/tools/
├── __init__.py            # Public API exports
├── auth.py                # Token auth (basic auth non-functional)
├── gitbucket_api.py       # Core client (all 32 endpoints)
├── exceptions.py          # Exception hierarchy
└── session.py             # Session init integration
```

### Import Pattern

```python
from skills.gitbucket_api.tools import GitBucketAPI

# Initialize from environment (reads GITBUCKET_HTML_URL (or GITBUCKET_URL) and GITBUCKET_TOKEN from .env)
api = GitBucketAPI()

# Or with explicit credentials
api = GitBucketAPI(
    url="https://gitbucket.example.com/gitbucket/",
    token="your-token"
)
```

### All 32 Endpoints

| Category | Methods |
|----------|---------|
| **Users & Auth** | `get_current_user()`, `list_users()`, `get_user()`, `list_user_repositories()`, `list_own_repositories()` |
| **Repositories** | `create_repository()`, `create_org_repository()`, `get_repository()` |
| **Issues** | `list_issues()`, `create_issue()`, `get_issue()`, `update_issue()` ⚠️ BROKEN (404), `add_issue_comment()` |
| **Labels** | `add_labels_to_issue()` ⚠️ BROKEN, `replace_issue_labels()` ⚠️ BROKEN, `remove_label_from_issue()`, `remove_all_labels_from_issue()`, `list_labels()`, `create_label()` |
| **Pull Requests** | `list_pull_requests()`, `create_pull_request()`, `get_pull_request()` |
| **Branches** | `list_branches()` |
| **Contents** | `get_contents()` |
| **Git Data** | `get_ref()`, `create_status()` |
| **Releases** | `list_releases()`, `create_release()` |
| **Milestones** | `list_milestones()`, `create_milestone()` |
| **Webhooks** | `list_webhooks()`, `create_webhook()` |
| **Admin** | `create_user()`, `create_organization()` (requires Basic auth) |

### Return Types

**IMPORTANT: The Python client correctly handles both array and object responses.**

```python
# List endpoints return arrays
issues = api.list_issues(owner="org", repo="project", state="open")
# type: list[dict]

# Get endpoints return objects
issue = api.get_issue(owner="org", repo="project", issue_number=14)
# type: dict
```

## Issue Operations

### Create Issue

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()

issue = api.create_issue(
    owner="org",
    repo="project",
    title="Issue title",
    body="Issue body",
    labels=["enhancement", "bug"],  # ✅ Auto-creates missing labels
    assignees=["username"],
    milestone=5
)
# Returns: {"number": 123, "id": 456789, ...}
```

### Get Issue

```python
issue = api.get_issue(
    owner="org",
    repo="project",
    issue_number=14
)
# Returns: single Issue object (dict)
```

### Update Issue

**⚠️ BROKEN: Returns 404 Not Found**

GitBucket does NOT implement `PATCH /repos/{owner}/{repo}/issues/{issue_number}`.

```python
# ❌ THIS DOES NOT WORK - Returns 404
issue = api.update_issue(
    owner="org",
    repo="project",
    issue_number=14,
    title="New title",
    body="New body"
)
# Returns: 404 Not Found
```

**Workaround:** Use GitBucket web UI to update issue title, body, or state.

**Tested:** 2026-04-06 - Still returns 404 after GitBucket upgrade.

---

### List Issues

```python
issues = api.list_issues(
    owner="org",
    repo="project",
    state="open"
)
# Returns: array of Issue objects (list[dict])
```

## Label Operations

**⚠️ CRITICAL: Label management operations are BROKEN in GitBucket v4.42.1**

The following operations return HTTP 200 with empty arrays but do NOT update issues:
- `add_labels_to_issue()` - Returns `[]`, labels NOT added
- `replace_issue_labels()` - Returns `[]`, labels NOT set
- `remove_label_from_issue()` - Not tested, may have same issue
- `remove_all_labels_from_issue()` - Not tested, may have same issue

**WORKAROUND:** Add labels during issue creation:

```python
# ✅ CORRECT: Add labels during creation
issue = api.create_issue(
    owner="org",
    repo="project",
    title="Issue title",
    body="Issue body",
    labels=["enhancement", "bug"]  # ✅ Works, auto-creates labels
)

# ❌ WRONG: Trying to add labels after creation
labels = api.add_labels_to_issue(
    owner="org",
    repo="project",
    issue_number=14,
    labels=["enhancement", "bug"]
)
# Returns: [] (empty array, labels NOT added)
```

**Tested:** 2026-04-06 - Both `add_labels_to_issue()` and `replace_issue_labels()` still broken after upgrade.

---

### Add Labels to Existing Issue

**⚠️ BROKEN: Returns empty array, labels NOT added**

```python
# ❌ THIS DOES NOT WORK - Returns empty array
labels = api.add_labels_to_issue(
    owner="org",
    repo="project",
    issue_number=14,
    labels=["enhancement", "bug"]
)
# Returns: [] (empty array)
# Issue labels remain unchanged
```

**Workaround:** Use `create_issue(labels=[...])` during issue creation.

**Tested:** 2026-04-06 - Verified NOT working.

---

### Replace All Labels on Issue

**⚠️ BROKEN: Returns empty array, labels NOT set**

```python
# ❌ THIS DOES NOT WORK - Returns empty array
labels = api.replace_issue_labels(
    owner="org",
    repo="project",
    issue_number=14,
    labels=["enhancement", "priority"]
)
# Returns: [] (empty array)
# Issue labels remain unchanged
```

**Workaround:** Use `create_issue(labels=[...])` during issue creation.

**Tested:** 2026-04-06 - Verified NOT working.

---

### Remove Specific Label from Issue

**⚠️ NOT TESTED - May have same issue as add/replace**

```python
# ⚠️ Not tested - exercise caution
api.remove_label_from_issue(
    owner="org",
    repo="project",
    issue_number=14,
    label_name="bug"
)
```

---

### Remove All Labels from Issue

```python
api.remove_all_labels_from_issue(
    owner="org",
    repo="project",
    issue_number=14
)
```

## Label Auto-Creation Behavior

**⚠️ CRITICAL: Label auto-creation ONLY works during `create_issue()`**

GitBucket auto-creates labels when specified in `create_issue(labels=[...])`:

```python
# ✅ WORKS: Labels auto-created during issue creation
issue = api.create_issue(
    owner="org",
    repo="project",
    title="New Issue",
    body="Description",
    labels=["new-label-1", "new-label-2"]
)
# GitBucket will:
# 1. Create "new-label-1" and "new-label-2" if they don't exist
# 2. Add both labels to the new issue
# 3. Return the created issue with labels attached
```

**Label auto-creation does NOT work for subsequent operations:**

```python
# ❌ DOES NOT WORK: Labels NOT created and NOT added
api.add_labels_to_issue(owner="org", repo="repo", issue_number=14, labels=["new-label"])
# Returns: []
# Issue labels remain unchanged
# Labels are NOT created
```

This is different from GitHub's API which requires labels to exist first.

**Recommendation:** Always use `create_issue(labels=[...])` for label management. There is no working API for label operations after issue creation.

## Error Recovery

See `tasks/error-recovery.md` for detailed procedures.

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Bad credentials" | Basic auth attempted | Use token authentication only |
| "Not Found" | Wrong endpoint URL | Verify URL format: `/api/v3/repos/{owner}/{repo}/...` |
| "Unauthorized" | Token missing or invalid | Check `GITBUCKET_TOKEN` value |
| 422 Unprocessable Entity | Label already exists | GitBucket returns validation error for duplicate labels |

## Session Init Integration

Session init (`ai_bin/session_init.py`) detects GitBucket and outputs:

```
GIT_PLATFORM=gitbucket
GITBUCKET_HTML_URL=https://gitbucket.example.com/gitbucket/
GITBUCKET_HAS_CREDENTIALS=true
```

## Testing

### Verify API After Upgrades

Run the test suite after GitBucket version changes:

```bash
# Test core endpoints (14 tests)
uv run python .opencode/skills/gitbucket-api/tests/verify_api.py

# Test documented deficiencies (3 tests)
uv run python .opencode/skills/gitbucket-api/tests/test_api_deficiencies.py
```

Update `API-DEFICIENCIES.md` if test results change.

## Source Code Reference

This skill is based on analysis of GitBucket source code:
- `ApiIssueControllerBase.scala` - Issue endpoints
- `ApiIssueLabelControllerBase.scala` - Label endpoints
- `CreateAnIssue.scala` - Create issue model
- `AddLabelsToAnIssue.scala` - Add labels model

## Sub-Tasks

- `tasks/issue-operations.md` - Issue CRUD patterns
- `tasks/label-operations.md` - Label CRUD patterns
- `tasks/error-recovery.md` - Error handling

## Guidelines Reference

| Guideline | Section |
|-----------|---------|
| `000-session-init.md` | GitBucket detection and credentials |