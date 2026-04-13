---
name: sync-guidelines
description: Use when synchronizing guidelines, skills, or tools between repositories. Triggers on: sync guidelines, cross-repo sync, guideline update, skill update, multi-repo, consistency between repos.
type: technique
license: MIT
compatibility: opencode
---

# Skill: sync-guidelines

## Overview

Intelligently synchronizes guidelines, skills, and tools between repositories through GitHub/GitBucket issues. Files are classified by reading and understanding content — not by pattern matching — to determine what is core (syncable) versus project-specific (protected).

## Tasks

| Task | Purpose | Words |
| -- | -- | -- |
| `classify` | Classify files as core or project-specific | ~250 |
| `sync-push` | Push core changes to target repository | ~300 |
| `sync-pull` | Pull core changes into local repository | ~300 |
| `issue-format` | Template for sync issue content | ~350 |

## Invocation

- `/skill sync-guidelines` — Overview only
- `/skill sync-guidelines --task classify` — Classify files as core or project-specific
- `/skill sync-guidelines --task sync-push` — Push changes to target repo
- `/skill sync-guidelines --task sync-pull` — Pull changes from source repo
- `/skill sync-guidelines --task issue-format` — Get issue template

## Operating Protocol

1. **Issue-based sync:** All sync operations create GitHub/GitBucket issues as proposals. Direct file modification in target repositories is PROHIBITED.
2. **Intelligent classification:** Every file MUST be read and analyzed before classification. Pattern-based classification (filename, number ranges) is FORBIDDEN.
3. **Core vs project-specific:** Core content (generic workflows, universal standards) syncs bidirectionally. Project-specific content (database paths, project names, config) is NEVER synced.
4. **Human review required:** No auto-merge. Sync issues are proposals for human reviewers to approve and apply.
5. **Conflict detection:** Before creating sync issues, check whether files exist in target repo and note any conflicts for manual merge resolution.

## Configuration

**Project-Local Config**: This config file should NOT be synced from other repositories. Create it per-project:

```yaml
# .opencode/sync-config.yml
source:
  owner: <owner>
  repo: <repo>
target:
  owner: <owner>
  repo: <repo>
local_only:
  - .opencode/AGENTS.md
  - .opencode/sync-config.yml
  - .opencode/sync-state.yml
```

## Sync State Tracking

Use `.opencode/sync-state.yml` to track sync state:

```yaml
last_sync:
  push:
    commit: abc123def
    timestamp: 2026-03-30T10:30:00Z
    files:
  pull:
    commit: def456ghi
    timestamp: 2026-03-29T14:20:00Z
    files:
      - guidelines/core/README.md
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

## Tools Required

- **File reading:** Use available file reading tools
- **GitHub operations:**
  - `github_get_file_contents` — Read remote files
  - `github_issue_write` — Create issues
  - `github_list_commits` — Detect changes since last sync

## Integration with git-workflow

1. Execute AFTER changes are committed to feature branch
2. Create sync issue as proposal (not auto-merge)
3. Human reviews and merges in target repository
4. Update sync state after successful sync

## Cross-References

- Related skills: `git-workflow` (branch management, commit workflow)
- Related guidelines: `000-critical-rules.md` (no vibe coding, scope autonomy)
