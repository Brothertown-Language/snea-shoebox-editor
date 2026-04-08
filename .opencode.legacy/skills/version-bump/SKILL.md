---
name: version-bump
description: Automatically determines and applies semantic version updates based on implementation impact analysis. Updates version files before PR creation, handles version conflicts, and creates tags/changelogs during release workflow.
license: MIT
compatibility: opencode
---

# Version Bump

Automatically determines and applies semantic version updates based on implementation impact analysis. Follows semantic versioning (SemVer 2.0.0) rules and integrates with git-workflow skill for PR creation.

## When to Use

- Creating a PR with code changes (version bump before PR)
- Preparing a release (version bump + tag + changelog)
- User manually requests version update
- git-workflow skill needs version bump as part of PR creation

## Prerequisites

- **Git**: Required for analyzing commit history and changes
- **Repository access**: Must be run from a git repository root
- **Version files**: At least one of pyproject.toml, setup.py, package.json, Cargo.toml, or VERSION file

## What This Skill Does

1. **Analyzes Implementation Impact**: Examines code changes to determine appropriate version bump type
2. **Applies Semantic Versioning**: Follows SemVer rules (MAJOR.MINOR.PATCH)
3. **Updates Version Files**: Modifies all relevant version files atomically
4. **Handles Conflicts**: When multiple PRs have version bumps, applies intelligent conflict resolution
5. **Integrates with Git-Workflow**: Coordinates with PR creation workflow
6. **Supports Release Workflow**: Creates git tags and generates changelogs during release preparation

## How to Use

### Basic Usage (PR Workflow)

```
Create PR for feature/authentication
```

The skill will automatically:
1. Analyze implementation changes
2. Determine bump type (major/minor/patch)
3. Update version files
4. Include version bump in PR commits

### Manual Version Bump

```
Bump version to prepare for release
```

### Specific Bump Type

```
Bump version with minor bump
```

### During Release Preparation

```
Create release for version 1.5.0
```

## Semantic Versioning Rules

### Major Bump (X.0.0)
- Breaking changes to public API
- Incompatible API changes
- Removal of public methods/classes
- Changes to CLI that break existing usage

### Minor Bump (0.X.0)
- New features without breaking changes
- New public methods/classes
- New optional parameters
- Backward-compatible enhancements

### Patch Bump (0.0.X)
- Bug fixes
- Performance improvements
- Internal refactoring (no public API changes)
- Test additions/modifications

### Skip Bump
- Documentation-only changes (no code changes)
- Chore PRs (build config, CI changes)
- Refactoring PRs without public API changes

## Example

**User**: "Create PR for new validation module"

**Skill Behavior**:
1. Analyzes code changes
2. Detects new public API (validators)
3. Determines bump type: **minor** (new features)
4. Updates version: 1.2.3 → 1.3.0
5. Commits with implementation (squashed)
6. Creates PR with combined changes

## Version Bump Workflow

### PR Workflow (Default)

**When**: Creating any PR with code changes

**Steps**:
1. Analyze PR implementation changes
2. Determine appropriate bump type
3. Apply version bump to files
4. Include version bump in PR commit (squashed with implementation)

**Decision Point**: If major bump detected, AI proceeds with reasoning (no user blocking)

### Release Workflow

**When**: Preparing for release (NOT post-merge)

**Steps**:
1. Verify version has been bumped via accumulated PRs
2. Create git tag for version
3. Generate changelog automatically

**Decision Point**: Tags created only during release preparation, not after PR merge

## Available Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `overview` | Full skill content for version bump workflow | ~370 |
| `analyze` | Analyze code changes to determine bump type | ~410 |
| `bump` | Apply version bump to all version files | ~340 |
| `release` | Create git tag and generate changelog during release | ~260 |

## When Invoked as Subtask (e.g., from git-workflow)

For PR creation workflow, this skill should be invoked as a subtask to prevent context pollution:

```
task tool with:
- subagent_type: "general"
- description: "Version bump for PR"
- prompt: "Use the version-bump skill... analyze changes... update version files... return JSON"
```

**Expected Return Format:**

```json
{
  "bump_type": "minor",
  "old_version": "1.2.3",
  "new_version": "1.3.0",
  "files_updated": ["pyproject.toml"],
  "success": true
}
```

The subtask will:
1. Load this skill in isolated context (~370 lines)
2. Analyze implementation changes
3. Determine bump type
4. Update all version files atomically
5. Return JSON result
6. Discard context (no pollution to caller)

## Conflict Resolution

When multiple PRs have version bumps (accumulation scenario):

**Strategy**: AI intelligently resolves conflicts by:
- Analyzing each PR's impact
- Applying highest priority bump type
- Preserving intent of all accumulated changes

**Example**:
- PR #1: Minor bump (0.1.0 → 0.2.0)
- PR #2: Patch bump (0.2.0 → 0.2.1)
- AI resolves to: Minor bump (0.1.0 → 0.2.0) - preserving higher impact

**Resolution Rules**:
- Major > Minor > Patch
- If any PR has major bump, use major
- If no major but any has minor, use minor
- Otherwise, use patch

## Tips

- Version bumps only for PRs with **code changes** (docs/chore/refactor PRs skip)
- Version bump commits are **squashed with implementation**
- Major bumps **proceed automatically** with AI reasoning (no user blocking)
- Tags created **only during release preparation** (not after PR merge)
- Version bumps **accumulate across PRs**, AI resolves conflicts
- Use specific bump type (`bump version with minor`) to override AI analysis

## Related Use Cases

- Pre-PR version management
- Release preparation workflow
- Hotfix versioning
- Breaking change management
- Automated version maintenance

## Cross-References

- Related: `git-workflow` skill (PR creation workflow)
- Related: `changelog-generator` skill (changelog creation)
- Related: `pr-creation-workflow` skill (PR timing)
- Enforces: Semantic Versioning (SemVer 2.0.0)