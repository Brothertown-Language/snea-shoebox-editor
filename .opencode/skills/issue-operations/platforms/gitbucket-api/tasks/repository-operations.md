# GitBucket Repository Operations

## Overview

Repository management operations using the `gitbucket-api` CLI tool at `.opencode/tools/gitbucket-api`.

**Primary Tool: CLI tool at `.opencode/tools/gitbucket-api`**

**CRITICAL: The `gitbucket_*` MCP tools have been REMOVED. The Python import pattern has been REPLACED by the CLI tool. Use `./.opencode/tools/gitbucket-api <command>` for all operations.**

## Basic Operations

### Get Repository

```bash
./.opencode/tools/gitbucket-api repo org project
```

### List User's Repositories

```bash
# List own repositories
./.opencode/tools/gitbucket-api repos

# List repositories for a specific user
./.opencode/tools/gitbucket-api repos --user username
```

### List Branches

```bash
./.opencode/tools/gitbucket-api branches org project
```

### List Pull Requests

```bash
./.opencode/tools/gitbucket-api prs org project --state open
```

### Get Pull Request

```bash
# List PRs and filter by number
./.opencode/tools/gitbucket-api prs org project --state all | jq '.[] | select(.number == 42)'
```

## Chained Operations

### Workflow 1: Check Branch Status Before Creating PR

**Scenario:** Verify branch exists, check for open PRs, create PR if none exists.

```bash
# Step 1: Check if branch exists
./.opencode/tools/gitbucket-api branches org project

# Step 2: Check for existing PRs for this branch
./.opencode/tools/gitbucket-api prs org project --state open

# Step 3: Create new PR (if no existing PR found)
./.opencode/tools/gitbucket-api create-pr org project "Feature: feature/oauth2" feature/oauth2 dev --body "## Description\n\nImplements OAuth2 authentication."
```

### Workflow 2: Find Stale Branches

**Scenario:** Find branches that haven't been updated recently.

```bash
# List all branches
./.opencode/tools/gitbucket-api branches org project
# Then filter out protected branches (main, master, dev) and identify stale ones
```

### Workflow 3: Repository Health Check

**Scenario:** Check repository for CI compliance, labels, milestones.

```bash
# Check for required labels
./.opencode/tools/gitbucket-api labels org project

# Check for open PRs
./.opencode/tools/gitbucket-api prs org project --state open

# Get repository info
./.opencode/tools/gitbucket-api repo org project

# Check branches
./.opencode/tools/gitbucket-api branches org project
```

### Workflow 4: Sync Fork with Upstream

**Scenario:** Check if fork is behind upstream and needs sync.

```bash
# Get repository info
./.opencode/tools/gitbucket-api repo org fork-repo
# Check if it's a fork and get upstream info from response
```

### Workflow 5: Create Release from Milestone

**Scenario:** Create release when milestone is completed.

```bash
# Note: Release/milestone operations require direct Python API usage
# Contact maintainers for milestone/release CLI commands if needed
```

## Complete API Reference

| Operation | CLI Command | Returns |
|-----------|------------|---------|
| Get repository | `gitbucket-api repo <owner> <repo>` | JSON |
| List own repos | `gitbucket-api repos` | JSON array |
| List user repos | `gitbucket-api repos --user <user>` | JSON array |
| List branches | `gitbucket-api branches <owner> <repo>` | JSON array |
| List PRs | `gitbucket-api prs <owner> <repo> [--state ...] [--head ...]` | JSON array |
| Create PR | `gitbucket-api create-pr <owner> <repo> <title> <head> <base> [--body ...]` | JSON |

## Source Code

- `.opencode/tools/gitbucket-api` - CLI entry point
- `.opencode/skills/issue-operations/platforms/gitbucket-api/tools/impl/` - Python implementation