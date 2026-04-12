# Task: classify

## Purpose

Intelligently classify files as core (sync bidirectionally) or project-specific (never sync) by reading and understanding file content.

## Operating Protocol

1. Invoked by: `/skill sync-guidelines --task classify`
2. When to use: When discovering files that need classification during a sync operation
3. Exit criteria: All discovered files classified with reasoning documented

## Classification Framework

### Core Indicators (Sync Bidirectionally)

A file is **core** if it:
- Defines generic workflows (git operations, github MCP usage)
- Contains universal engineering standards
- Describes cross-project concepts (approval gates, spec creation, error handling)
- Has NO project-specific imports, paths, or configuration
- Can be dropped into ANY project and work without modification

Examples of core content:
- `## Operating Protocol` — workflow definition
- `git checkout`, `github_issue_write` — generic operations
- `## Critical Requirements` — universal standards
- Generic error handling, data integrity rules

### Project-Specific Indicators (Never Sync)

A file is **project-specific** if it:
- References project name in imports or code
- Contains project-specific database paths
- Has project-specific API endpoints
- Contains project-specific configuration
- Would break if copied to another project

Examples of project-specific content:
- `pubmed_data_3/` — project database path
- `<repo>` — project name (from session_init.py)
- `project_root /` — project-specific path handling
- Project-specific table names or schemas

### Uncertain Classification

If classification is unclear:
- Note the uncertainty in the issue
- Provide analysis of what was found
- Let human reviewer decide

## Classification Rule

**When in doubt, classify as project-specific.** Syncing project-specific content is destructive; missing core content is recoverable.

## Context Required

- Related skills: `sync-guidelines` (parent skill)
- Related tasks: `sync-push`, `sync-pull`