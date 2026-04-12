---
name: gitbucket-api
description: Use when working with a GitBucket repository for API operations, issue management, or label handling. Triggers on: GitBucket, gitbucket, API call, issue creation, label, token authentication, error recovery, non-GitHub platform.
type: reference
license: MIT
compatibility: opencode
---

# GitBucket API Skill

## Overview

GitBucket implements a GitHub-compatible API v3. This skill documents the Python client (primary tool), API limitations, and error recovery. The `gitbucket_*` MCP tool functions have been REMOVED — use the Python client at `.opencode/skills/gitbucket-api/tools/` exclusively.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `issue-operations` | Issue CRUD patterns, create/update/list workarounds | ~500 |
| `label-operations` | Label CRUD, auto-creation, post-creation limitations | ~400 |
| `error-recovery` | Error handling, retry logic, credential failures | ~320 |
| `mcp-operations` | MCP tool mapping, alternative API paths | ~250 |
| `repository-operations` | Repository CRUD, branch operations | ~300 |
| `session-integration` | Session init integration, env var detection | ~200 |

## Invocation

- `/skill gitbucket-api --task issue-operations` - Issue CRUD patterns
- `/skill gitbucket-api --task label-operations` - Label management patterns
- `/skill gitbucket-api --task error-recovery` - Error handling procedures
- `/skill gitbucket-api` - Overview only

## Key API Deficiencies (CRITICAL)

| Operation | Status | Workaround |
|-----------|--------|------------|
| `update_issue()` PATCH | ❌ Returns 404 | Use GitBucket web UI to update issues |
| `add_labels_to_issue()` | ❌ Returns empty array, labels NOT added | Add labels during `create_issue(labels=[...])` |
| `replace_issue_labels()` | ❌ Returns empty array, labels NOT set | Add labels during `create_issue(labels=[...])` |
| Basic auth | ❌ "Bad credentials" | Token authentication ONLY |

**Label auto-creation ONLY works during `create_issue()`.** No working API for label operations after issue creation.

## Authentication

Token authentication ONLY. Basic auth is broken in GitBucket (returns "Bad credentials" for all requests).

```python
from skills.gitbucket_api.tools import GitBucketAPI
api = GitBucketAPI()  # Reads GITBUCKET_HTML_URL and GITBUCKET_TOKEN from .env
```

## Python Client

**Use `from skills.gitbucket_api.tools import GitBucketAPI` for all operations.** The client handles both array and object responses correctly. See task files for endpoint-specific patterns.

## Response Schema

All `list_*` endpoints return arrays (`List[Dict]`), NOT objects. The Python client handles this automatically.

## Operating Protocol

1. Detect GitBucket platform from session init output
2. Use Python client for all API operations
3. Add labels ONLY during `create_issue()` creation
4. Use web UI for issue updates (PATCH endpoint broken)
5. Follow error recovery procedures in `tasks/error-recovery.md`

## Cross-References

| Guideline | Section |
|-----------|---------|
| Session init plugin | GitBucket detection and credentials |
| `.opencode/skills/gitbucket-api/reference/` | OpenAPI v4.42.1 specification |
| `.opencode/skills/gitbucket-api/tests/` | API verification test suite |