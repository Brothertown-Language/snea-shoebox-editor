# GitBucket Label Operations

## Overview

GitBucket label operations using the `gitbucket-api` CLI tool at `.opencode/tools/gitbucket-api`.

## Add Labels to Issue

**⚠️ BROKEN: Returns empty array `[]`, labels are NOT added**

The GitBucket API endpoint `POST /repos/{owner}/{repo}/issues/{number}/labels` returns HTTP 200 with an empty array but does NOT add labels to the issue.

**Workaround:** Add labels during issue creation with `create-issue --labels`.

### CLI (Only Option)

```bash
# ❌ BROKEN: No CLI command for post-creation label addition

# ✅ WORKAROUND: Add labels during issue creation
./.opencode/tools/gitbucket-api create-issue org project "Bug report" --body "Description" --labels bug,enhancement
```

## Replace All Labels

**⚠️ BROKEN: Returns empty array `[]`, labels are NOT set**

The GitBucket API endpoint `PUT /repos/{owner}/{repo}/issues/{number}/labels` returns HTTP 200 with an empty array but does NOT set labels on the issue.

**Workaround:** Add labels during issue creation with `create-issue --labels`.

### CLI (Only Option)

```bash
# ❌ BROKEN: No CLI command for label replacement

# ✅ WORKAROUND: Add labels during issue creation
./.opencode/tools/gitbucket-api create-issue org project "Bug report" --body "Description" --labels priority,review
```

## Remove Specific Label

### Python API (Only Option — not available via CLI)

Post-creation label removal is available via the Python API but not exposed as a CLI command.

## Remove All Labels

### Python API (Only Option — not available via CLI)

All-labels removal is available via the Python API but not exposed as a CLI command.

## Repository Labels

### List Labels

```bash
./.opencode/tools/gitbucket-api labels org project
```

### Create Label

Label creation happens automatically when labels are specified during `create-issue`. For explicit label creation, use the Python API directly.

## Tool Selection

| Operation | CLI Command | Status |
|-----------|------------|--------|
| Add labels | N/A | ⚠️ BROKEN (returns `[]`) |
| Replace labels | N/A | ⚠️ BROKEN (returns `[]`) |
| Remove label | N/A | Python API only |
| Remove all labels | N/A | Python API only |
| List labels | `gitbucket-api labels <owner> <repo>` | ✅ |
| Create label | N/A | Auto-created via create-issue |

**Note:** The `gitbucket-api` CLI tool is the primary tool for label operations that work. Broken operations are not exposed via CLI.

## Error Handling

```bash
# 422 - Invalid label name or format
./.opencode/tools/gitbucket-api create-issue org project "Test" --labels "invalid label!"
# Error output will indicate validation failure
```

## Source Code

- `.opencode/tools/gitbucket-api` - CLI entry point
- `.opencode/skills/issue-operations/platforms/gitbucket-api/tools/impl/` - Python implementation