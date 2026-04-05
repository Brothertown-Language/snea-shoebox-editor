---
name: changelog-generator
description: Automatically creates user-facing changelogs from git commits by analyzing commit history, categorizing changes, and transforming technical commits into clear, customer-friendly release notes.
license: MIT
compatibility: opencode
---

# Skill: changelog-generator

Automatically creates user-facing changelogs from git commits by analyzing commit history, categorizing changes, and transforming technical commits into clear, customer-friendly release notes.

## When to Use This Skill

**See `AGENTS.md` → "Skill Invocation Guidance" for the complete trigger table.**

This skill is invoked at these workflow triggers:

| Workflow Trigger | Invocation | Purpose |
|------------------|------------|---------|
| Generating changelog | `/skill changelog-generator` | Create changelog from commits |
| Updating CHANGELOG.md | `/skill changelog-generator --task write` | Write entries to changelog file |
| PR creation workflow | Invoked as subtask by `git-workflow` | Generate commit messages for PR |

## This Skill's Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `overview` | Full skill content for changelog generation | ~400 |
| `write` | Write generated entries to CHANGELOG.md | ~300 |

## Dual Changelog Workflow

This project maintains TWO changelogs:

1. **Project Changelog** (`CHANGELOG.md`): User-facing project changes
   - Features, fixes, improvements visible to end users
   - References version numbers from `pyproject.toml`
   - Follows Keep a Changelog format

2. **AI Agent Changelog** (`.opencode/CHANGELOG.md`): AI infrastructure changes
   - Guidelines, skills, workflow updates
   - Internal AI agent tooling changes
   - Also references version numbers from `pyproject.toml`

### Determining Target Changelog

| Change Type | Target Changelog |
|-------------|------------------|
| `.opencode/` directory changes | `.opencode/CHANGELOG.md` |
| Skills (`skills/`) changes | `.opencode/CHANGELOG.md` |
| Guidelines (`guidelines/`) changes | `.opencode/CHANGELOG.md` |
| AGENTS.md changes | `.opencode/CHANGELOG.md` |
| Project source code changes | `CHANGELOG.md` |
| Documentation (README, docs/) changes | `CHANGELOG.md` |
| Dependencies (`pyproject.toml`, `requirements.txt`) | `CHANGELOG.md` |
| Test changes | `CHANGELOG.md` |
| CI/CD changes (`.github/`) | `CHANGELOG.md` |

**Default:** If uncertain, use `.opencode/CHANGELOG.md` for AI-focused changes.

### Version Reference

Both changelogs reference version numbers from `pyproject.toml`:

```bash
# Extract current version
grep '^version = ' pyproject.toml | head -1 | cut -d'"' -f2

# Example output: 0.2.0
```

**Changelog Entry Format:**

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- Description of new feature

### Changed
- Description of change

### Fixed
- Description of fix
```

**Unreleased Changes:**

```markdown
## [X.Y.Z] - Unreleased

### Added
- Changes for next release
```

### Writing Dual Changelogs

When generating a changelog that affects both:

```bash
# Example: A new skill that also changes project behavior
# Write to both changelogs:
# 1. .opencode/CHANGELOG.md (skill added)
# 2. CHANGELOG.md (project behavior change)
```

Use the `write` task for each changelog separately:

```
/skill changelog-generator --task write --target .opencode/CHANGELOG.md
/skill changelog-generator --task write --target CHANGELOG.md
```
- Maintaining a public changelog/product updates page

## What This Skill Does

1. **Scans Git History**: Analyzes commits from a specific time period or between versions
2. **Categorizes Changes**: Groups commits into logical categories (features, improvements, bug fixes, breaking changes, security)
3. **Translates Technical → User-Friendly**: Converts developer commits into customer language
4. **Formats Professionally**: Creates clean, structured changelog entries
5. **Filters Noise**: Excludes internal commits (refactoring, tests, etc.)
6. **Follows Best Practices**: Applies changelog guidelines and your brand voice

## How to Use

### Basic Usage

From your project repository:

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

## Example

**User**: "Create a changelog for commits from the past 7 days"

**Output**:
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

**Inspired by:** Manik Aggarwal's use case from Lenny's Newsletter

## Available Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `overview` | Full skill content for changelog generation | ~400 |
| `write` | Write generated entries to CHANGELOG.md | ~300 |

## When Invoked as Subtask (e.g., from git-workflow)

For PR creation workflow, this skill should be invoked as a subtask to prevent context pollution:

```
task tool with:
- subagent_type: "general"
- description: "Generate changelog for PR"
- prompt: "Use the changelog-generator skill... write to CHANGELOG.md... return JSON"
```

**Expected Return Format:**

```json
{
  "summary": "Brief executive summary (1-2 sentences)",
  "changelog": "Full markdown changelog content",
  "success": true
}
```

The subtask will:
1. Load this skill in isolated context (~400 lines)
2. Generate changelog from commits
3. Write to CHANGELOG.md
4. Return JSON result
5. Discard context (no pollution to caller)

## Tips

- Run from your git repository root
- Specify date ranges for focused changelogs
- Use your CHANGELOG_STYLE.md for consistent formatting
- **Write to CHANGELOG.md before creating PRs** - Use `write` task to update the file
- Follow Keep a Changelog format for industry-standard changelogs

## Related Use Cases

- Creating GitHub release notes
- Writing app store update descriptions
- Generating email updates for users
- Creating social media announcement posts