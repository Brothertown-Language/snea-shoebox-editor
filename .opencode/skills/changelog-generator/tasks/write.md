# Task: write

## Purpose

Write generated changelog entries to CHANGELOG.md file.

## Operating Protocol

1. **After generate task:** Run after `overview` task generates entries
2. **Prepend entries:** Add new entries to `[Unreleased]` section
3. **Create if missing:** Initialize CHANGELOG.md if it doesn't exist
4. **Atomic write:** Use file operations, not shell redirects

## Entry Criteria

- Changelog entries generated from `overview` task
- Repository has git history to analyze
- Working directory is clean or changes are acceptable to include

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

### Step 2: Locate CHANGELOG.md

Check if CHANGELOG.md exists at repository root.

**Path:** `<repo-root>/CHANGELOG.md`

**If file doesn't exist:**
- Create with standard Keep a Changelog header
- Include `[Unreleased]` section
- Include format reference links

### Step 3: Read Existing Content

Read current CHANGELOG.md content:

```python
content = pycharm_get_file_text_by_path(
    pathInProject="CHANGELOG.md",
    projectPath=<project-root>
)
```

### Step 4: Parse Sections

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

### Step 5: Merge New Entries

For each category in generated entries:
1. Find matching section in `[Unreleased]`
2. Prepend new entries to that section
3. Preserve existing entries below

**Category Mapping:**
- `New Features` → `### Added`
- `Improvements` → `### Changed`
- `Bug Fixes` → `### Fixed`
- `Breaking Changes` → `### Changed` (with breaking note)
- `Security` → `### Security` (or `### Fixed` with security note)

### Step 6: Write Updated Content

Write merged content back to CHANGELOG.md:

```python
pycharm_replace_text_in_file(
    pathInProject="CHANGELOG.md",
    projectPath=<project-root>,
    oldText=<existing-content>,
    newText=<merged-content>
)
```

### Step 7: Verify Write

Read back content to verify:
- Entries are in correct sections
- Formatting is preserved
- No duplicate entries

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