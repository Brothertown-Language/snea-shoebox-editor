# Task: bump

## Purpose

Apply version bump to all detected version files.

## Operating Protocol

1. **After analyze task**: Run after `analyze.md` determines bump type
2. **Atomic updates**: Update all version files in single operation
3. **Semantic versioning**: Apply semver rules correctly
4. **Commit integration**: Changes included in implementation commit (squashed)

## Entry Criteria

- Bump type determined (major/minor/patch)
- Version files identified
- Current version parsed from files

## Exit Criteria

- All version files updated
- Changes staged for commit
- Ready for PR creation

## Procedure

### Step 1: Parse Current Version

From each version file, extract current version:

**Python (pyproject.toml)**:
```python
# Pattern: version = "X.Y.Z"
match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
version = match.group(1)  # e.g., "1.2.3"
```

**Python (setup.py)**:
```python
# Pattern: version="X.Y.Z"
match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
version = match.group(1)  # e.g., "1.2.3"
```

**Node.js (package.json)**:
```json
{
  "version": "1.2.3"
}
```

**Rust (Cargo.toml)**:
```toml
[package]
version = "1.2.3"
```

**Generic (VERSION file)**:
```
1.2.3
```

### Step 2: Calculate New Version

**Semantic Versioning**: MAJOR.MINOR.PATCH

**Bump rules**:
```python
def bump_version(current: str, bump_type: str) -> str:
    major, minor, patch = map(int, current.split('.'))
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        return current  # No change for skip
```

**Examples**:
- Current: `1.2.3`, bump: `major` → New: `2.0.0`
- Current: `1.2.3`, bump: `minor` → New: `1.3.0`
- Current: `1.2.3`, bump: `patch` → New: `1.3.0`
- Wait no, current: `1.2.3`, bump: `patch` → New: `1.2.4`

My mistake: let me correct:

```python
# Correct rules:
# Major: X.Y.Z → (X+1).0.0
# Minor: X.Y.Z → X.(Y+1).0
# Patch: X.Y.Z → X.Y.(Z+1)
```

**Examples**:
- Current: `2.3.4`, bump: `major` → New: `3.0.0`
- Current: `2.3.4`, bump: `minor` → New: `2.4.0`
- Current: `2.3.4`, bump: `patch` → New: `2.3.5`

### Step 3: Preserve Pre-release Suffixes

**If version has pre-release suffix**:
- `1.2.3-alpha` → `1.2.4-alpha` (patch bump)
- `1.2.3-alpha` → `1.3.0-alpha` (minor bump)
- `1.2.3-alpha` → `2.0.0` (major bump, remove pre-release)

**Preservation logic**:
```python
def parse_version_with_prerelease(version: str):
    # Match: X.Y.Z[-suffix]
    match = re.match(r'(\d+\.\d+\.\d+)(?:-(.+))?', version)
    if match:
        version_part = match.group(1)
        prerelease = match.group(2)
        return version_part, prerelease
    return version, None

def bump_with_prerelease(current: str, bump_type: str) -> str:
    version_part, prerelease = parse_version_with_prerelease(current)
    new_version = bump_version(version_part, bump_type)
    
    # Remove pre-release for major bumps
    if bump_type == "major":
        return new_version
    
    # Preserve pre-release for minor/patch
    if prerelease:
        return f"{new_version}-{prerelease}"
    return new_version
```

### Step 4: Update Each Version File

**Python (pyproject.toml)**:

**Before**:
```toml
[project]
name = "my-package"
version = "1.2.3"
```

**After**:
```toml
[project]
name = "my-package"
version = "1.2.4"
```

**Update operation**:
```python
pycharm_replace_text_in_file(
    pathInProject="pyproject.toml",
    projectPath=<project-root>,
    oldText='version = "1.2.3"',
    newText='version = "1.2.4"'
)
```

**Python (setup.py)**:

**Before**:
```python
setup(
    name="my-package",
    version="1.2.3",
    ...
)
```

**After**:
```python
setup(
    name="my-package",
    version="1.2.4",
    ...
)
```

**Update operation**:
```python
pycharm_replace_text_in_file(
    pathInProject="setup.py",
    projectPath=<project-root>,
    oldText='version="1.2.3"',
    newText='version="1.2.4"'
)
```

**Node.js (package.json)**:

**Before**:
```json
{
  "name": "my-package",
  "version": "1.2.3"
}
```

**After**:
```json
{
  "name": "my-package",
  "version": "1.2.4"
}
```

**Update operation**:
```python
pycharm_replace_text_in_file(
    pathInProject="package.json",
    projectPath=<project-root>,
    oldText='"version": "1.2.3"',
    newText='"version": "1.2.4"'
)
```

**Rust (Cargo.toml)**:

**Before**:
```toml
[package]
name = "my-package"
version = "1.2.3"
```

**After**:
```toml
[package]
name = "my-package"
version = "1.2.4"
```

**Update operation**:
```python
pycharm_replace_text_in_file(
    pathInProject="Cargo.toml",
    projectPath=<project-root>,
    oldText='version = "1.2.3"',
    newText='version = "1.2.4"'
)
```

**Generic (VERSION file)**:

**Before**:
```
1.2.3
```

**After**:
```
1.2.4
```

**Update operation**:
```python
pycharm_replace_text_in_file(
    pathInProject="VERSION",
    projectPath=<project-root>,
    oldText="1.2.3",
    newText="1.2.4"
)
```

### Step 5: Verify Updates

Read back each updated file to verify:
1. Version string updated correctly
2. No unintended changes to surrounding content
3. Format preserved (quotes, spacing, etc.)

### Step 6: Stage Changes for Commit

Stage all updated version files:

```bash
git add pyproject.toml package.json Cargo.toml VERSION
```

**Important**: Do NOT commit separately. Version bump will be included in implementation commit (squashed).

## Atomic Update Guarantee

**All version files must be updated in a single operation**:

**Before update**:
- Read all version files
- Parse all versions
- Verify all versions match (or identify inconsistencies)

**During update**:
- Calculate new version once
- Apply to all files
- Verify all updates succeeded

**If any update fails**:
- Rollback all changes
- Report error
- Do not proceed with PR

## Version Consistency Check

**Before bumping**, verify all version files have same version:

```python
versions = {}
for file in version_files:
    versions[file] = parse_version(file)

unique_versions = set(versions.values())
if len(unique_versions) > 1:
    # Inconsistent versions detected
    report_error(f"Version files have different versions: {versions}")
    # Decide: use highest version or fail
```

**If versions are inconsistent**:
- Use highest version as base
- Document inconsistency in bump commit
- OR fail and request manual resolution

## Squash Integration

**Version bump commits are NOT separate commits**.

**They are squashed with implementation**:

```
Implementation commit (squashed):
- All implementation changes
- Version bump changes
- Single commit for PR

NOT:
- Implementation commit
- Version bump commit  ← WRONG
- Separate commits
```

**Git workflow**:
```bash
# After implementing feature
git add <implementation files>
git add <version files>  # Version bump staged
git commit -m "[Phase N] Implement feature X"  # Squashed commit
```

## Return Format (For Subtask Invocation)

When invoked as a subtask, return a JSON object:

```json
{
  "old_version": "1.2.3",
  "new_version": "1.2.4",
  "bump_type": "patch",
  "files_updated": ["pyproject.toml", "package.json"],
  "success": true
}
```

If the subtask fails:

```json
{
  "success": false,
  "error": "Description of what went wrong",
  "files_attempted": ["pyproject.toml"],
  "files_failed": ["package.json"]
}
```

## Common Issues

| Issue | Resolution |
|-------|------------|
| Version mismatch across files | Use highest version, warn user, proceed |
| Pre-release version detected | Preserve suffix for minor/patch, remove for major |
| No version files found | Create VERSION file or update project config |
| Version not found in file | Parse file-specific format, report error if missing |
| Update failed for one file | Rollback all changes, fail task, report error |

## Integration with Git-Workflow

**Integration point**: After `analyze.md`, before PR creation

**Workflow**:
1. `analyze.md` determines bump type
2. `bump.md` applies version updates
3. Changes staged for commit
4. Implementation continued
5. All changes committed together (squashed)
6. PR created with combined changes

## Tips

- Pre-release suffixes preserved for minor/patch bumps
- Major bumps remove pre-release suffixes (stable release)
- All version files must be consistent before bump
- Atomic operations: all succeed or all fail
- No separate commit for version bump (squashed with implementation)