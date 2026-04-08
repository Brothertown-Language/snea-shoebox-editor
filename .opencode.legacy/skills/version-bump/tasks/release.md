# Task: release

## Purpose

Create git tags and generate changelogs during release preparation workflow.

## Workflow

1. **Release preparation only**: Not used for regular PR workflow
2. **After PR accumulation**: All version bumps from PRs are already merged
3. **Creates git tag**: Tags version commit
4. **Generates changelog**: Creates release notes from commit history

## Preconditions

- All PRs for release merged
- Version already bumped via accumulated PRs
- Repository in clean state (no uncommitted changes)
- Ready to create git tag

## Postconditions

- Git tag created for version
- CHANGELOG.md generated/updated with release notes
- Tag points to correct commit

## Procedure

### Step 1: Verify Version State

**Check current version in all files**:

```python
versions = {}
for file in version_files:
    versions[file] = parse_version(file)

unique_versions = set(versions.values())
if len(unique_versions) != 1:
    report_error("Version files inconsistent")
    # Use highest version or fail

version = list(unique_versions)[0]
```

**Verify version has NOT been tagged yet**:

```bash
git tag -l "v{version}"
# Should return nothing if tag doesn't exist
```

**If tag exists**:
- Error: Version already has a tag
- Suggest incrementing version first
- OR report duplicate tag error

### Step 2: Create Git Tag

**Annotated tag (recommended)**:

```bash
git tag -a "v{version}" -m "Release {version}"
```

**Tag message format**:
```
Release {version}

- [Summary of changes]
- [Key features/fixes]

See CHANGELOG.md for details.
```

**Example**:
```bash
git tag -a "v1.2.0" -m "Release 1.2.0

- Added new validation module
- New /validate API endpoint
- Bug fixes in client error handling

See CHANGELOG.md for details."
```

### Step 3: Verify Tag Creation

**Check tag was created**:

```bash
git tag -l "v{version}"
# Should output: v1.2.0

git show "v{version}"
# Should show tag message and commit
```

**Verify tag points to correct commit**:

```bash
git rev-parse "v{version}"
# Should match expected commit SHA
```

### Step 4: Generate Changelog

**Invoke changelog-generator skill**:

```
Create changelog from commits since last release
```

**Changelog generation**:
1. Get previous version tag: `git describe --tags --abbrev=0 HEAD^`
2. Get commits between versions: `git log {prev_tag}..HEAD`
3. Categorize commits into sections:
   - Added (features)
   - Changed (improvements)
   - Fixed (bug fixes)
   - Breaking changes
   - Security
4. Format per Keep a Changelog standard

### Step 5: Update CHANGELOG.md

**Add new version section**:

```markdown
## [1.2.0] - 2026-04-03

### Added
- New validation module with input sanitization
- POST /validate API endpoint for client validation

### Changed
- Improved error handling performance

### Fixed
- Client error handling now preserves error context

### Breaking Changes
- None

### Security
- None
```

**Insert after `[Unreleased]` section**:

```markdown
## [Unreleased]

### Added
- [New uncommitted features]

## [1.2.0] - 2026-04-03
...
```

**Do NOT replace entire CHANGELOG.md**:
- Preserve previous versions
- Insert new version section at top
- Preserve `[Unreleased]` section

### Step 6: Write CHANGELOG.md

**Update file atomically**:

```python
pycharm_replace_text_in_file(
    pathInProject="CHANGELOG.md",
    projectPath=<project-root>,
    oldText="## [Unreleased]",
    newText=new_changelog_content
)
```

### Step 7: Commit Changelog Update

**Changelog updates are separate from version bumps**:

```bash
git add CHANGELOG.md
git commit -m "docs: Update CHANGELOG for v{version}"
```

**Rationale**: Changelog is documentation, can be separate commit.

### Step 8: Push Tag and Changelog

**Push tag to remote**:

```bash
git push origin "v{version}"
```

**Push changelog commit**:

```bash
git push origin HEAD
```

## Tag Naming Convention

**Standard format**: `v{MAJOR}.{MINOR}.{PATCH}`

**Examples**:
- `v1.0.0` - Major release
- `v0.5.0` - Minor release
- `v0.0.1` - Patch release

**Pre-release versions**:
- `v1.0.0-alpha.1` - Alpha release
- `v1.0.0-beta.2` - Beta release
- `v1.0.0-rc.1` - Release candidate

**Tag prefix**: Always use `v` prefix (e.g., `v1.2.0`, not `1.2.0`)

## Changelog Format

**Keep a Changelog standard**:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- [New uncommitted features]

## [1.2.0] - 2026-04-03

### Added
- New validation module
- POST /validate API endpoint

### Changed
- Improved error handling

### Fixed
- Client error context preservation

### Breaking Changes
- None

## [1.1.0] - 2026-03-20

...
```

**Categories**:
- **Added**: New features
- **Changed**: Improvements to existing features
- **Deprecated**: Features to be removed in future
- **Removed**: Breaking changes (removed features)
- **Fixed**: Bug fixes
- **Security**: Security improvements

## Integration with Workflow

**Release Workflow Sequence**:

1. **All PRs merged** via normal PR workflow
   - Each PR already has version bump (squashed with implementation)
   - Version accumulates across PRs
   - Final version ready for release

2. **Release preparation** (this task):
   - Verify version state
   - Create git tag
   - Generate changelog
   - Commit changelog update
   - Push tag and changelog

3. **Post-release**:
   - GitHub release created (manual or automated)
   - Release notes published
   - Artifacts published (if applicable)

**NOT in release workflow**:
- Version bump happens BEFORE release (during PR accumulation)
- Tag created DURING release (not post-merge)
- Changelog generated DURING release (not post-merge)

## Return Format (For Subtask Invocation)

When invoked as a subtask, return a JSON object:

```json
{
  "version": "1.2.0",
  "tag": "v1.2.0",
  "changelog_updated": true,
  "changelog_file": "CHANGELOG.md",
  "success": true
}
```

If the subtask fails:

```json
{
  "success": false,
  "error": "Description of what went wrong",
  "version": "1.2.0",
  "tag_created": false,
  "changelog_updated": false
}
```

## Common Issues

| Issue | Resolution |
|-------|------------|
| Version already tagged | Fail, suggest increment version first |
| Version files inconsistent | Use highest version, warn user |
| No previous tag found | Generate changelog from all commits |
| CHANGELOG.md missing | Create with standard header and new version |
| Git tag push fails | Verify tag exists locally, retry push |
| Remote rejects tag | Tag already exists on remote, suggest new version |

## Release vs PR Workflow

**Key Difference**: Version bump timing

| Workflow | When Version Bumps | When Tag Created | When Changelog Generated |
|----------|-------------------|------------------|-------------------------|
| PR | During PR (before creation) | Never | Never |
| Release | Already done via PRs | During release | During release |

**PR Workflow** (per PR):
```
Implementation → Analyze → Bump → Commit → PR → Merge
```

**Release Workflow** (after all PRs):
```
Verify Version → Tag → Changelog → Commit Changelog → Push
```

## Tips

- Tags created **only during release preparation**
- Changelog generated **during release**, not post-merge
- Version already bumped **via accumulated PRs**
- No separate version bump for releases
- Check for existing tags before creating
- Preserve CHANGELOG.md history
- Use annotated tags (not lightweight tags)