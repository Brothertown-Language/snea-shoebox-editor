# Task: overview

Guidelines synchronization manager that intelligently syncs guidelines, skills, and tools between repositories through GitHub issues.

## Role

Guidelines Sync Manager that intelligently synchronizes between repositories through GitHub issues. Classifies files by **reading and understanding content**, not by pattern matching.

## When to Invoke

- User runs `/skill sync-guidelines`
- Automated workflow detects changes in `.opencode/guidelines/`, `.opencode/skills/`, or `ai_bin/`

## Workflow

### Phase 0: Pre-Work Verification

1. Verify on feature branch (not `main`)
2. Check for uncommitted changes (`git status`)
3. Stash if needed

### Phase 1: Discover Files to Sync

1. Detect changed files since last sync
2. For each file in `.opencode/guidelines/`, `.opencode/skills/`, `ai_bin/`:
   - Read the **entire file content**
   - Analyze semantically what the file does
   - Determine classification: core or project-specific

### Phase 2: Intelligent Classification

**READ each file and ANALYZE:**

#### Core Indicators (Sync Bidirectionally)

A file is **core** if it:
- Defines generic workflows (git operations, github MCP usage)
- Contains universal engineering standards
- Describes cross-project concepts (approval gates, spec creation, error handling)
- Has NO project-specific imports, paths, or configuration
- Can be dropped into ANY project and work without modification

Examples of core content:
- `## Workflow` - workflow definition
- `git checkout`, `github_issue_write` - generic operations
- `## Critical Requirements` - universal standards
- Generic error handling, data integrity rules

#### Project-Specific Indicators (Never Sync)

A file is **project-specific** if it:
- References project name in imports or code
- Contains project-specific database paths
- Has project-specific API endpoints
- Contains project-specific configuration
- Would break if copied to another project

Examples of project-specific content:
- `<project-db>/` - project database path
- `<repo>` - project name (from session_init.py)
- `project_root /` - project-specific path handling
- Project-specific table names or schemas

#### Uncertain Classification

If classification is unclear:
- Note the uncertainty in the issue
- Provide analysis of what was found
- Let human reviewer decide

### Phase 3: Create GitHub Issue

Use `github_issue_write` to create an issue in target (push) or source (pull) repository:

```
github_issue_write(
    method="create",
    owner=<target_owner>,
    repo=<target_repo>,
    title="[SYNC] {direction}: {count} files from {source_repo}",
    body=<structured issue with inspection analysis>,
    labels=["sync", "needs-review"]
)
```

### Phase 4: Report Completion

Post comment to spec issue documenting:
- Files analyzed
- Classification decisions with reasoning
- GitHub issue URL created

## Classification Logic Example

```python
# Core file: Defines generic workflow
"## Workflow" → core (workflow definition)
"git checkout" → core (generic operation)
"github_issue_write" → core (generic MCP usage)

# Project-specific: Contains project paths
"<project-db>/" → project-specific (project path)
"project_root /" → project-specific (project handling)
"<repo>" → project-specific (project reference)
```

## Cross-References

- Related: `git-workflow` skill (for git operations)
- Related: `github-comments` skill (for issue creation)
- Guidelines: `000-session-init.md` (for project-specific values)