# Task: write

## Purpose

Write generated changelog entries to CHANGELOG.md file.

## Operating Protocol

1. **After generate task:** Run after `overview` task generates entries
2. **Prepend entries:** Add new entries to `[Unreleased]` section
3. **Create if missing:** Initialize CHANGELOG.md if it doesn't exist
4. **Atomic write:** Use file operations, not shell redirects

## Dual Changelog Support

This repository maintains TWO changelogs:

1. **Project Changelog** (`CHANGELOG.md`): User-facing project changes
2. **AI Agent Changelog** (`.opencode/CHANGELOG.md`): AI infrastructure changes

### Determining Target Changelog

| Change Type | Target Changelog |
|-------------|------------------|
| `.opencode/` directory | `.opencode/CHANGELOG.md` |
| Skills (`skills/`) | `.opencode/CHANGELOG.md` |
| Guidelines (`guidelines/`) | `.opencode/CHANGELOG.md` |
| AGENTS.md | `.opencode/CHANGELOG.md` |
| Project source code | `CHANGELOG.md` |
| Documentation | `CHANGELOG.md` |
| Dependencies | `CHANGELOG.md` |
| Tests | `CHANGELOG.md` |
| CI/CD (`.github/`) | `CHANGELOG.md` |

**Default:** If uncertain, default to `.opencode/CHANGELOG.md` for AI-focused changes.

## Entry Criteria

- Changelog entries generated from `overview` task
- Repository has git history to analyze
- Working directory is clean or changes are acceptable to include
- Target changelog path determined (project or AI agent)

## Exit Criteria

- CHANGELOG.md updated with new entries
- File formatted per Keep a Changelog standard
- Entries in correct `[Unreleased]` section

## Procedure

### Step 1: Generate Changelog Entries

Invoke the `overview` task to generate changelog entries from commits:

```
Create a changelog from commits since branching from main
```

### Step 2: Extract Version from pyproject.toml

**CRITICAL:** Both changelogs MUST reference version numbers from `pyproject.toml`, not use `[Unreleased]` indefinitely.

```bash
# Extract current version from pyproject.toml
version=$(grep '^version = ' pyproject.toml | head -1 | cut -d'"' -f2)
```

**Example:** If `pyproject.toml` has `version = "0.2.0"`, the changelog section header should be:

```markdown
## [0.2.0] - Unreleased
```

**Version Header Format:**

```markdown
## [X.Y.Z] - Unreleased
```

For released versions, use the release date:

```markdown
## [X.Y.Z] - YYYY-MM-DD
```

**Why Version Numbers Matter:**

- Users can track which version introduced a change
- Developers can correlate changelog entries with releases
- Aligns project and AI changelogs under consistent versioning
- Enables future automation (release notes, version history)

### Step 3: Locate Target Changelog

Determine which changelog to update:

**Decision Tree:**

```
Changes in .opencode/? → Use .opencode/CHANGELOG.md
Changes in skills/? → Use .opencode/CHANGELOG.md  
Changes in guidelines/? → Use .opencode/CHANGELOG.md
Changes in AGENTS.md → Use .opencode/CHANGELOG.md
Project source code? → Use CHANGELOG.md
Documentation? → Use CHANGELOG.md
Dependencies? → Use CHANGELOG.md
Tests? → Use CHANGELOG.md
CI/CD (.github/)? → Use CHANGELOG.md
Uncertain? → Default to .opencode/CHANGELOG.md for AI-focused changes
```

**Paths:**

| Changelog | Path |
|-----------|------|
| Project | `<repo-root>/CHANGELOG.md` |
| AI Agent | `<repo-root>/.opencode/CHANGELOG.md` |

### Step 4: Read Target Changelog

Check if CHANGELOG.md exists at repository root.

**Path:** `<repo-root>/CHANGELOG.md`

**If file doesn't exist:**
- Create with standard Keep a Changelog header
- Include `[X.Y.Z] - Unreleased` section with version from pyproject.toml
- Include format reference links
- Include cross-reference link (project changelogs reference AI changelog, vice versa)

### Step 5: Read Existing Content

Read current changelog content from target file:

```python
content = pycharm_get_file_text_by_path(
    pathInProject="<target-changelog>",
    projectPath=<project-root>
)
```

### Step 6: Parse Sections

Parse existing changelog into sections:

```
## [Unreleased]
### Added
### Changed
### Fixed
...

## [1.0.0] - YYYY-MM-DD
...
```

### Step 7: Merge New Entries

For each category in generated entries:
1. Find matching version section (current version from pyproject.toml)
2. Find matching subsection (`### Added`, `### Changed`, `### Fixed`, etc.)
3. Prepend new entries to that subsection
4. Preserve existing entries below

**Section Structure:**

```markdown
## [X.Y.Z] - Unreleased    ← Current version from pyproject.toml

### Added
- <new-entry-1>           ← Generated entries prepended here
- <new-entry-2>
- <existing-entry-1>      ← Existing entries preserved below

### Changed
- <new-entry>
- <existing-entry>

### Fixed
- <new-entry>
```

**Category Mapping:**
- `New Features` → `### Added`
- `Improvements` → `### Changed`
- `Bug Fixes` → `### Fixed`
- `Breaking Changes` → `### Changed` (with breaking note)
- `Security` → `### Security` (or `### Fixed` with security note)

### Step 8: Write Updated Content

Write merged content back to target changelog:

```python
pycharm_replace_text_in_file(
    pathInProject="<target-changelog>",
    projectPath=<project-root>,
    oldText=<existing-content>,
    newText=<merged-content>
)
```

### Step 9: Verify Write

Read back content to verify:
- Entries are in correct sections
- Formatting is preserved
- No duplicate entries
- Version section matches pyproject.toml version

## File Format Template

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- <entry-1>
- <entry-2>

### Changed
- <entry-1>

### Fixed
- <entry-1>

## [0.1.0] - 2026-04-03

### Added
- Initial release
```

## Entry Insertion Example

**Generated entries:**
```
### Added
- New feature A
- New feature B

### Fixed
- Bug fix for X
```

**Existing CHANGELOG.md:**
```
## [Unreleased]

### Added
- Previous feature

### Fixed
```

**Merged result:**
```
## [Unreleased]

### Added
- New feature A
- New feature B
- Previous feature

### Fixed
- Bug fix for X
```

## Context Required

- Repository root path
- Git history (commits since last release or branch point)
- Keep a Changelog format specification

## Return Format (For Subtask Invocation)

When invoked as a subtask (e.g., from git-workflow pr-creation), return a JSON object:

```json
{
  "summary": "Brief executive summary (1-2 sentences describing stakeholder value)",
  "changelog": "Full markdown changelog content\n\n## Changes\n\n### Added\n- Feature A\n\n### Fixed\n- Bug B\n\n...",
  "success": true
}
```

**Summary:** User-facing description focusing on value, not technical details.

**Changelog:** Complete markdown content with categorized sections.

**Success:** Boolean indicating if the changelog was written to CHANGELOG.md.

If the subtask fails, return:

```json
{
  "summary": "",
  "changelog": "",
  "success": false,
  "error": "Description of what went wrong"
}
```

## Common Issues

| Issue | Resolution |
|-------|------------|
| File doesn't exist | Create with standard header and `[Unreleased]` section |
| No `[Unreleased]` section | Add section after header, before versioned sections |
| Duplicate entries | Skip entries that already exist in file |
| Wrong category | Map to closest matching category in Keep a Changelog |