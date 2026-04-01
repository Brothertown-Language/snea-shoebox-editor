---
name: sync-guidelines
description: Intelligently synchronize guidelines, skills, and tools between repositories through GitHub issues. Classifies files by semantic analysis and creates sync issues for human review.
license: MIT
compatibility: opencode
---

# Skill: sync-guidelines

## When to Invoke

This skill is triggered when:
- User runs `/skill sync-guidelines`
- Automated workflow detects changes in `.opencode/guidelines/`, `.opencode/skills/`, or `ai_bin/`

## Role

You are a Guidelines Sync Manager. Your purpose is to intelligently synchronize guidelines, skills, and tools between repositories through GitHub issues. You classify files by **reading and understanding content**, not by pattern matching.

## Operating Protocol

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
- `## Operating Protocol` - workflow definition
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
- `pubmed_data_3/` - project database path
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
- Issue URL created

## Issue Content Format

```markdown
# [SYNC] {direction}: {count} files from {source_repo}

**Source:** {source_owner}/{source_repo}
**Commit:** [{short_sha}](commit_url)
**Direction:** Push | Pull
**Sync Method:** Issue-based (intelligent inspection, no patterns)

## Classification Analysis

### File: {filepath}

**Content Read:** Yes (full file analyzed)

**Analysis:**
- {finding_1}
- {finding_2}
- {finding_3}

**Project-Specific Content Found:**
- {specific content or "None"}

**Classification:** ✅ Core / 🚫 Project-Specific / ⚠️ Uncertain

---

{Repeat for each file}

## Files to Sync (Core Only)

| File | Classification | Key Reason |
|------|---------------|------------|
| {path} | Core | {reason} |

## Files Not Synced

| File | Classification | Key Reason |
|------|---------------|------------|
| {path} | Project-Specific | {reason} |

## File Contents

### {filename}

```{language}
{full file content}
```

## Verification

- Source commit: [{sha[:8]}](url)
- All files read and analyzed: Yes
- Pattern-based classification used: No

---
*Created by sync-guidelines skill*
*Classification via intelligent content inspection*
```

## Configuration

**Project-Local Config**: This config file should NOT be synced from other repositories. Create it per-project:

```yaml
# .opencode/sync-config.yml
source:
  owner: <owner>   # From session_init.py output
  repo: <repo>     # From session_init.py output
  
target:
  owner: <owner>   # Target GitHub org/username
  repo: <repo>     # Target repo name

# Files that are explicitly project-local (never sync)
local_only:
  - ".opencode/AGENTS.md"
  - ".opencode/sync-config.yml"
  - ".opencode/sync-state.yml"
```

**NOTE**: Create this file only if syncing guidelines between repositories. The file is project-specific and should not be copied from other projects.

## Sync State Tracking

Use `.opencode/sync-state.yml` to track sync state:

```yaml
last_sync:
  push:
    commit: abc123def
    timestamp: 2026-03-30T10:30:00Z
    files:
      - .opencode/guidelines/080-code-standards.md
      
  pull:
    commit: def456ghi
    timestamp: 2026-03-29T14:20:00Z
    files:
      - guidelines/core/README.md
```

## Conflict Detection

### Push Conflicts

Before creating push issue:
1. Check if file exists in target repo (`github_get_file_contents`)
2. If both modified, note conflict in issue
3. Recommend manual merge in issue body

### Pull Conflicts

Before creating pull issue:
1. Read local file content
2. Analyze for project-specific modifications
3. If project-specific content found:
   - SKIP this file
   - Note as "protected" in issue
   - Recommend manual review if needed
4. If safe, proceed with pull proposal

## Tools Required

- **File reading:** Use available file reading tools
- **GitHub operations:**
  - `github_get_me` - Identify authenticated user
  - `github_get_file_contents` - Read remote files
  - `github_issue_write` - Create issues
  - `github_list_commits` - Detect changes since last sync

## Integration with git-workflow

1. Execute AFTER changes are committed to feature branch
2. Create sync issue as proposal (not auto-merge)
3. Human reviews and merges in target repository
4. Update sync state after successful sync

## Example Usage

### Manual Sync

```
User: /skill sync-guidelines

Agent:
1. Discovers changed files
2. Reads each file's content
3. Analyzes and classifies intelligently
4. Creates issue with analysis
5. Posts comment to spec issue
```

### Classification Example

```
File: .opencode/guidelines/080-code-standards.md

Analysis:
- Defines PEP 8 standards (generic)
- Defines typing rules (generic)
- Defines code quality rules (generic)
- No project name references
- No project-specific paths
- No database references

Classification: ✅ Core (sync bidirectionally)

---

File: .opencode/guidelines/070-environment.md

Analysis:
- Contains "pubmed_data_3" (project-specific database)
- Contains "project_root" handling (project-specific)
- Contains project-specific configuration
- Would break in another project

Classification: 🚫 Project-Specific (never sync)
```

## Prohibitions

### 🚫 NEVER DO

- Use pattern-based classification (filename, number ranges)
- Guess classification without reading content
- Directly modify files in target repository
- Overwrite project-specific files
- Auto-merge without human review
- Skip intelligent analysis phase

### ✅ ALWAYS DO

- Read entire file content for each file
- Analyze content semantically
- Explain classification reasoning in issue
- Create issues only (never direct edits)
- Let human reviewer make final decision on uncertain cases