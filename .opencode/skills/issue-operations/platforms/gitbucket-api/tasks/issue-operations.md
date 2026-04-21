# GitBucket Issue Operations

## Overview

Issue CRUD operations using the `gitbucket-api` CLI tool at `.opencode/tools/gitbucket-api`.

**Primary Tool: CLI tool at `.opencode/tools/gitbucket-api`**

**CRITICAL: The `gitbucket_*` MCP tools have been REMOVED. The Python import pattern has been REPLACED by the CLI tool. Use `./.opencode/tools/gitbucket-api <command>` for all operations.**

## Response Types

**ALL `list` commands return JSON arrays:**
- `issues` → JSON array
- `issue` → JSON object

**Always check type before iterating:**
```bash
# List returns JSON array
./.opencode/tools/gitbucket-api issues org project --state open

# Get single issue returns JSON object
./.opencode/tools/gitbucket-api issue org project 14
```

## Basic Operations

### Create Issue

```bash
./.opencode/tools/gitbucket-api create-issue org project "Issue title" --body "Issue body" --labels enhancement,bug
```

**Fields supported:**
- `<title>` (required positional) - Issue title
- `--body` (optional) - Issue description
- `--labels` (optional, comma-separated) - Label names (auto-created)

### Get Issue

```bash
./.opencode/tools/gitbucket-api issue org project 14
```

### Update Issue

**⚠️ BROKEN: Returns 404 Not Found**

GitBucket does NOT implement `PATCH /repos/{owner}/{repo}/issues/{issue_number}`.

```bash
# ❌ THIS DOES NOT WORK - Returns 404
# No update-issue CLI command available
```

**Workaround:** Use GitBucket web UI to update issue title, body, or state. There is no API for updating existing issues.

### List Issues

```bash
./.opencode/tools/gitbucket-api issues org project --state open
```

### Add Comment

```bash
./.opencode/tools/gitbucket-api add-comment org project 14 "Comment text"
```

## Chained Operations

### Workflow 1: Create Issue with Labels and Comments

**Scenario:** Create issue, add welcome comment.

```bash
# Step 1: Create issue with labels
./.opencode/tools/gitbucket-api create-issue org project "Bug: Login fails on mobile" --body "## Description\n\nLogin fails on mobile devices." --labels bug,priority:high

# Step 2: Add welcome comment
./.opencode/tools/gitbucket-api add-comment org project <issue-number> "**Status:** Issue created and under investigation.\n\nWe'll look into this shortly."
```

### Workflow 2: Parent/Child Issue Management

**Scenario:** Create parent spec issue and child task issues, link via comments.

```bash
# Step 1: Create parent spec issue
./.opencode/tools/gitbucket-api create-issue org project "[SPEC] Add OAuth2 Authentication" --body "## Objective\n\nImplement OAuth2 authentication." --labels enhancement,spec

# Step 2: Create child task issues (repeat for each phase)
./.opencode/tools/gitbucket-api create-issue org project "[Task: #<parent>] Phase 1: OAuth2 Client Setup" --body "Parent Issue: #<parent>\n\nImplement OAuth2 client setup." --labels task

# Step 3: Add comment to parent listing children
./.opencode/tools/gitbucket-api add-comment org project <parent-number> "**Sub-issues created:**\n\n- #<child1>: OAuth2 Client Setup\n- #<child2>: Token Management"
```

### Workflow 3: Close Issue with Summary Comment

**Scenario:** Close issue after completion, add summary comment.

```bash
# Step 1: Add completion comment
./.opencode/tools/gitbucket-api add-comment org project 14 "🤖 <AgentName> (<ModelId>) ✅ completed\n\n**Summary:**\n\nImplemented OAuth2 authentication with automatic token refresh.\n\n**Outcome:**\n\nUsers can now authenticate via OAuth2, and tokens refresh automatically without user intervention."

# Step 2: Close issue (requires web UI — PATCH is broken on GitBucket)
# Use GitBucket web UI to close the issue
```

### Workflow 4: Batch Label Operations

**⚠️ CRITICAL: `update_issue()` and post-creation label APIs are BROKEN in GitBucket.**

- `update_issue()` returns 404
- `add_labels_to_issue()` returns `[]`, labels NOT added
- `replace_issue_labels()` returns `[]`, labels NOT set

**Labels can ONLY be set during `create_issue()`.** There is no working API for changing labels after issue creation.

```bash
# ✅ WORKS: Set labels during issue creation
./.opencode/tools/gitbucket-api create-issue org project "Bug report" --body "Description" --labels bug,priority:high,needs-review

# ❌ BROKEN: Cannot change labels after creation
# No CLI command available — post-creation label operations are broken
```

**Workaround:** Delete and recreate the issue if labels need to change.

### Workflow 5: Find and Close Duplicate Issues

**Scenario:** Find duplicate issues and close them with reference to original.

```bash
# Step 1: Get the canonical issue
./.opencode/tools/gitbucket-api issue org project 14

# Step 2: List all open issues
./.opencode/tools/gitbucket-api issues org project --state open

# Step 3: Identify duplicates from the list

# Step 4: Close each duplicate with comment (requires web UI for closing)
./.opencode/tools/gitbucket-api add-comment org project <dup-number> "**Closing as duplicate of #14**\n\nThis issue is a duplicate and is being closed. Please continue discussion on #14."
```

### Workflow 6: Title Dedup Search (GitBucket Fallback)

**Scenario:** Pre-creation Step 0.5 title dedup gate when search API is unavailable (GitBucket search is BROKEN).

When the platform lacks a search API, use iterative listing with client-side keyword filtering:

```bash
# Step 1: List open issues (most recent first)
./.opencode/tools/gitbucket-api issues org project --state open

# Step 2: List closed issues (most recent first)
./.opencode/tools/gitbucket-api issues org project --state closed

# Step 3: Client-side keyword filter — extract significant keywords from proposed title
# Remove stop words and prefixes like [SPEC], [SPEC-FIX], [Task:]
# Match issues whose titles share ≥2 significant keywords with proposed title

# Step 4: For each candidate match, read the full body
./.opencode/tools/gitbucket-api issue org project <candidate-number>

# Step 5: Classify match (EXACT-DUPLICATE, NEAR-DUPLICATE, CLOSED-IN-ERROR, RELATED-BUT-DISTINCT, FALSE-POSITIVE)
# Follow Phase 2 and Phase 3 of pre-creation Step 0.5
```

**Key difference from GitHub:** GitHub uses `github_search_issues` with a keyword query for server-side filtering. GitBucket requires fetching all issues and filtering client-side by keyword match and recency. Paginate only if no match found on first page.

## Error Handling

The CLI tool outputs structured error information:

```bash
# 401 - Authentication error
./.opencode/tools/gitbucket-api check-auth

# 404 - Repo doesn't exist
./.opencode/tools/gitbucket-api create-issue org nonexistent "Test"
# Error: 404 Not Found

# 422 - Invalid input
./.opencode/tools/gitbucket-api create-issue org project "Test" --labels "invalid label!"
# Error: 422 Unprocessable Entity
```

## Complete API Reference

| Operation | CLI Command | Status |
|-----------|------------|--------|
| Create issue | `create-issue <owner> <repo> <title> [--body ...] [--labels ...]` | ✅ |
| Get issue | `issue <owner> <repo> <number>` | ✅ |
| Update issue | N/A | ❌ BROKEN (404) |
| List issues | `issues <owner> <repo> [--state ...]` | ✅ |
| Add comment | `add-comment <owner> <repo> <number> <body>` | ✅ |
| Add labels | N/A | ❌ BROKEN (returns `[]`) |
| Replace labels | N/A | ❌ BROKEN (returns `[]`) |
| Remove label | N/A | Available via Python API |
| Remove all labels | N/A | Available via Python API |

## Source Code

- `.opencode/tools/gitbucket-api` - CLI entry point
- `.opencode/skills/issue-operations/platforms/gitbucket-api/tools/impl/` - Python implementation