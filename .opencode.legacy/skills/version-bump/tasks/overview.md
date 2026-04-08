# Task: overview

Version bump skill that automatically determines and applies semantic version updates based on implementation impact analysis.

## When to Invoke

Use when:
- Creating a PR with code changes (version bump before PR)
- Preparing a release (version bump + tag + changelog)
- User manually requests version update
- Git-workflow skill needs version bump as part of PR creation workflow

## Prerequisites

- **Git**: Required for analyzing commit history and changes
- **Repository access**: Must be run from a git repository root
- **Version files**: At least one of `pyproject.toml`, `setup.py`, `package.json`, or `Cargo.toml`

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
- Changes to command-line interface that break existing usage

### Minor Bump (0.X.0)
- New features without breaking changes
- New public methods/classes
- New optional parameters
- Backward-compatible enhancements

### Patch Bump (0.0.X)
- Bug fixes
- Performance improvements
- Documentation updates (if code changes are present)
- Internal refactoring that doesn't change public API
- Test additions/modifications

### Skip Bump
- Documentation-only changes (no code changes)
- Chore PRs (build config, CI changes)
- Refactoring PRs without public API changes

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

## Conflict Resolution Strategy

When multiple PRs have version bumps (accumulation scenario):

**Strategy**: AI intelligently resolves conflicts by:
- Analyzing each PR's impact
- Applying the highest priority bump type
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

## Integration Points

### Git-Workflow Skill

**Phase**: Pre-work → Implementation → Review-prep → PR-creation → Cleanup

**Integration Point**: After implementation, before PR creation

**Workflow**:
1. Implementation completes
2. `git-workflow` invokes `version-bump` task
3. Version bump applied and committed
4. PR created with implementation + version bump

### Release Workflow Skill

**Phase**: Release preparation

**Integration Point**: After all PRs merged for release

**Workflow**:
1. All PRs merged into release branch
2. `release-workflow` invokes `version-bump --task release`
3. Tag created for version
4. Changelog generated from commits

## Procedure

### Step 1: Analyze Implementation

Invoke the `analyze.md` task to examine code changes and determine bump type.

### Step 2: Check Version Files

Identify all version files in repository:
- `pyproject.toml` (Python projects)
- `setup.py` (legacy Python projects)
- `package.json` (Node.js projects)
- `Cargo.toml` (Rust projects)
- `VERSION` file (generic version tracking)

### Step 3: Determine Bump Type

Using analysis results, determine appropriate bump type:
- **Major**: Breaking changes detected
- **Minor**: New features without breaking changes
- **Patch**: Bug fixes, improvements
- **Skip**: No code changes (docs/chore PRs)

### Step 4: Apply Version Bump

Invoke the `bump.md` task to update all version files atomically.

### Step 5: Commit Changes

Version bump commits are **squashed with implementation**:
- Single commit for PR: implementation + version bump
- No separate version-bump commits
- Clean git history

## Version File Detection

**Python Projects** (`pyproject.toml`):
```toml
[project]
version = "1.2.3"
```

**Legacy Python** (`setup.py`):
```python
setup(
    version="1.2.3",
    ...
)
```

**Node.js Projects** (`package.json`):
```json
{
  "version": "1.2.3"
}
```

**Rust Projects** (`Cargo.toml`):
```toml
[package]
version = "1.2.3"
```

**Generic** (`VERSION` file):
```
1.2.3
```

## Tips

- Version bumps only for PRs with **code changes** (docs/chore/refactor PRs skip)
- Version bump commits are **squashed with implementation**
- Major bumps **proceed automatically** with AI reasoning (no user blocking)
- Tags created **only during release preparation** (not after PR merge)
- Version bumps **accumulate across PRs**, AI resolves conflicts
- Use `bump.md` task for direct version updates when needed

## Manual Override

Users can explicitly specify bump type:

```
Create PR for feature/authentication with minor version bump
```

```
Bump version with patch (urgent bug fix)
```

```
Bump version with major (breaking API change)
```

If user specifies bump type, use that type directly (no AI analysis needed).

## Related Use Cases

- Pre-PR version management
- Release preparation workflow
- Hotfix versioning
- Breaking change management
- Automated changelog generation

## Cross-References

- Related: `git-workflow` skill (PR creation workflow)
- Related: `pr-creation-workflow` skill (PR timing)
- Related: AGENTS.md (git protocol, commit workflow)
- Enforces: Semantic Versioning (SemVer 2.0.0)