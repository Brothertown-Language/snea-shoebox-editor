# Task: overview

Changelog generator that transforms technical git commits into polished, user-friendly changelogs.

## When to Invoke

Use when:
- Preparing release notes for a new version
- Creating product update summaries
- Documenting changes for customers
- Writing changelog entries for app store submissions
- Generating update notifications

## Prerequisites

- **Git**: Required for reading commit history
- **Repository access**: Must be run from a git repository root
- **Optional**: Custom changelog style guide (CHANGELOG_STYLE.md)

## What This Skill Does

1. **Scans Git History**: Analyzes commits from a specific time period or between versions
2. **Categorizes Changes**: Groups commits into logical categories (features, improvements, bug fixes, breaking changes, security)
3. **Translates Technical → User-Friendly**: Converts developer commits into customer language
4. **Formats Professionally**: Creates clean, structured changelog entries
5. **Filters Noise**: Excludes internal commits (refactoring, tests, etc.)
6. **Follows Best Practices**: Applies changelog guidelines and your brand voice

## How to Use

### Basic Usage

```
Create a changelog from commits since last release
```

```
Generate changelog for all commits from the past week
```

```
Create release notes for version 2.5.0
```

### With Specific Date Range

```
Create a changelog for all commits between March 1 and March 15
```

### With Custom Guidelines

```
Create a changelog for commits since v2.4.0, using my changelog 
guidelines from CHANGELOG_STYLE.md
```

## Example Output

```markdown
# Updates - Week of March 10, 2024

## ✨ New Features

- **Team Workspaces**: Create separate workspaces for different 
  projects. Invite team members and keep everything organized.

- **Keyboard Shortcuts**: Press ? to see all available shortcuts. 
  Navigate faster without touching your mouse.

## 🔧 Improvements

- **Faster Sync**: Files now sync 2x faster across devices
- **Better Search**: Search now includes file contents, not just titles

## 🐛 Fixes

- Fixed issue where large images wouldn't upload
- Resolved timezone confusion in scheduled posts
- Corrected notification badge count
```

## Procedure

1. **Scan commits** from specified time period or version range
2. **Categorize** each commit into: features, improvements, fixes, breaking, security
3. **Translate** technical language to user-friendly descriptions
4. **Format** into structured markdown with appropriate sections
5. **Filter** out internal-only commits (refactoring, tests, infrastructure)
6. **Apply** custom style guide if provided (CHANGELOG_STYLE.md)

## Tips

- Run from your git repository root
- Specify date ranges for focused changelogs
- Review and adjust the generated changelog before publishing
- Use your CHANGELOG_STYLE.md for consistent formatting

## Related Use Cases

- Creating GitHub release notes
- Writing app store update descriptions
- Generating email updates for users
- Creating social media announcement posts

## Cross-References

- Related: `git-workflow` skill (for commit access)
- Related: AGENTS.md (git workflow guidelines)