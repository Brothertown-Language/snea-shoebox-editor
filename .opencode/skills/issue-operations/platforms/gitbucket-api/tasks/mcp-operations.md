# GitBucket CLI Operations

## Overview

GitBucket operations use the `gitbucket-api` CLI tool located at `.opencode/tools/gitbucket-api`. This replaces both MCP tools and the Python client for all operations.

## CLI Tool Availability

| Operation | CLI Command | Status |
|-----------|------------|--------|
| Get issue | `gitbucket-api issue <owner> <repo> <number>` | ✅ |
| Create issue | `gitbucket-api create-issue <owner> <repo> <title> [--body ...] [--labels ...]` | ✅ |
| Add comment | `gitbucket-api add-comment <owner> <repo> <number> <body>` | ✅ |
| List issues | `gitbucket-api issues <owner> <repo> [--state open\|closed\|all]` | ✅ |
| Get repository | `gitbucket-api repo <owner> <repo>` | ✅ |
| List branches | `gitbucket-api branches <owner> <repo>` | ✅ |
| List PRs | `gitbucket-api prs <owner> <repo> [--state ...] [--head ...]` | ✅ |
| Create PR | `gitbucket-api create-pr <owner> <repo> <title> <head> <base> [--body ...]` | ✅ |
| List labels | `gitbucket-api labels <owner> <repo>` | ✅ |
| Get current user | `gitbucket-api me` | ✅ |
| Validate auth | `gitbucket-api check-auth` | ✅ |
| Init config | `gitbucket-api init-config [--path ...]` | ✅ |

## CLI-First Workflow

**For all operations:**

```bash
# Create issue
./.opencode/tools/gitbucket-api create-issue org project "Bug fix" --body "Description" --labels bug,enhancement

# Get issue
./.opencode/tools/gitbucket-api issue org project 14

# List issues
./.opencode/tools/gitbucket-api issues org project --state open
```

## Tool Selection Decision Tree

```
Is operation in CLI command table?
    ├─ YES → Use CLI command
    │         ├─ Success → Return result
    │         └─ Failure → Log error, check credentials with check-auth
    └─ NO → Report missing command, HALT — do NOT fall back to inline scripts
```

## Error Classification

### CLI Error (Retry or Check Credentials)

```bash
./.opencode/tools/gitbucket-api check-auth
# If auth fails, check .env for GITBUCKET_TOKEN and GITBUCKET_HTML_URL
```

### API Error (Classified)

The CLI tool outputs structured error information:

```bash
./.opencode/tools/gitbucket-api create-issue org nonexistent "Test"
# Error: 404 Not Found - Check owner/repo names

./.opencode/tools/gitbucket-api create-issue org project "Test"
# Error: 401 Unauthorized - Check GITBUCKET_TOKEN

./.opencode/tools/gitbucket-api create-issue org project "Test"
# Error: 422 Unprocessable Entity - Check request body format
```

## Label Operations (Labels Can ONLY Be Set During Creation)

GitBucket does **not** support adding labels after issue creation. Use `--labels` during creation:

```bash
# ✅ WORKS: Set labels during issue creation
./.opencode/tools/gitbucket-api create-issue org project "Bug report" --body "Description" --labels bug,enhancement

# ❌ BROKEN: Cannot change labels after creation
# No CLI command for post-creation label operations — they return empty arrays
```

## Admin Operations (Basic Auth Required)

Admin operations require Basic authentication, not token:

```bash
# Admin operations are not available via CLI
# Uses Python API client directly for admin tasks
```

## Source Code

- `.opencode/tools/gitbucket-api` - CLI tool (entry point)
- `.opencode/skills/issue-operations/platforms/gitbucket-api/tools/impl/` - Python implementation
