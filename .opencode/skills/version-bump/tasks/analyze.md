# Task: analyze

## Purpose

Analyze implementation changes to determine appropriate semantic version bump.

## Operating Protocol

1. **On-demand invocation**: Called by `overview` task or `git-workflow` skill
2. **Code change detection**: Scans for actual code changes (not docs/chore)
3. **Impact analysis**: Examines public API changes, new features, bug fixes
4. **Bump type recommendation**: Returns major/minor/patch/skip

## Entry Criteria

- Git repository with commits or staged changes to analyze
- OR explicit user request with bump type specified
- Version files present (pyproject.toml, setup.py, package.json, Cargo.toml, VERSION)

## Exit Criteria

- Bump type determined (major/minor/patch/skip)
- Reasoning documented for major bumps
- Version files to update identified

## Procedure

### Step 1: Check for Explicit Override

If user explicitly specifies bump type:
```
Create PR with minor version bump
```

**Action**: Use specified bump type directly, skip analysis.

**Return early with**: `{ "bump_type": "minor", "reason": "User-specified", "files": [...] }`

### Step 2: Gather Changes to Analyze

**For PRs in progress**:
```bash
# Changes on feature branch vs main
git diff main...HEAD
```

**For staged changes**:
```bash
# Staged changes ready to commit
git diff --cached
```

**For recent commits**:
```bash
# Commits since last version bump
git log --oneline --since="last tag or last bump commit"
```

### Step 3: Detect Code vs Non-Code Changes

**Code changes** (require version bump):
- `*.py` files (Python modules)
- `*.js`, `*.ts` files (JavaScript/TypeScript)
- `*.rs` files (Rust)
- Source code in any language
- Build configuration that affects runtime behavior

**Non-code changes** (skip version bump):
- `*.md` files (documentation only)
- `*.txt` files (README, LICENSE, etc.)
- `*.yml`, `*.yaml` for CI/CD (chore)
- `.gitignore`, `.editorconfig` (chore)
- Test files without production code changes

**Decision logic**:
```python
code_files = []
non_code_files = []

for file in changed_files:
    if is_code_file(file) or affects_runtime(file):
        code_files.append(file)
    else:
        non_code_files.append(file)

if not code_files:
    return { "bump_type": "skip", "reason": "No code changes detected", "files": non_code_files }
```

### Step 4: Analyze Impact Severity

**For code changes, examine**:

#### Breaking Changes → Major Bump

**Indicators**:
- Removed or renamed public methods/classes
- Changed function signatures (parameters removed or made required)
- Changed return types
- Moved classes to different modules
- Changed command-line interface that breaks existing usage
- Deprecated features finally removed
- Database schema changes that break backward compatibility

**Detection**:
```python
# Look for patterns in diffs:
- "def old_function" removed
- "class OldClass" removed
- Parameter removal: "def func(a, b)" → "def func(a)"
- Required parameters: "def func(a=None)" → "def func(a)"
```

**Examples**:
```python
# Breaking: removed parameter with default became required
# Before: def process(data, options=None)
# After:  def process(data, options)  # ← Breaking change

# Breaking: renamed public method
# Before: class Client:
#             def get_data(self):
# After:  class Client:
#             def fetch_data(self):  # ← Breaking change, old method removed
```

#### New Features → Minor Bump

**Indicators**:
- New public methods/classes
- New optional parameters
- New modules/packages
- New command-line options
- New API endpoints
- New configuration options

**Detection**:
```python
# Look for patterns:
+ "def new_function"
+ "class NewClass"
+ "export class"
+ "pub fn new_"  # Rust
```

**Examples**:
```python
# Minor: new public method added
+ def validate_input(self, data):
+     """New validation method."""
+     ...

# Minor: new optional parameter
# Before: def process(data)
# After:  def process(data, timeout=None)  # ← Minor change
```

#### Bug Fixes / Improvements → Patch Bump

**Indicators**:
- Fixed bugs or errors
- Performance improvements
- Internal refactoring (no public API changes)
- Code style changes
- Dependency updates (patch level)
- Test additions/modifications

**Detection**:
```python
# Look for patterns:
- "fix:" in commit messages
- "bug" in commit messages
- Error handling improvements
- Internal function changes (private methods)
```

**Examples**:
```python
# Patch: bug fix
# Before: def parse(data):
#             return data['value']
# After:  def parse(data):
#             return data.get('value', default)  # ← Patch: bug fix

# Patch: performance improvement
# Before: results = [x for x in items if condition(x)]
# After:  results = list(filter(condition, items))  # ← Patch: performance
```

### Step 5: Determine Bump Type

**Priority order**:
```
Major > Minor > Patch > Skip
```

**Decision logic**:
```python
def determine_bump_type(analysis):
    if any_breaking_changes(analysis.changes):
        return "major"
    elif any_new_features(analysis.changes):
        return "minor"
    elif any_bug_fixes_or_improvements(analysis.changes):
        return "patch"
    else:
        return "skip"
```

### Step 6: Document Major Bump Reasoning

**For major bumps only**, create reasoning document:

```markdown
# Major Bump Reasoning

**Version**: X.Y.Z → (X+1).0.0

**Breaking Changes Detected**:

1. **[Change Type]**: [Description]
   - File: `path/to/file.py`
   - Before: [description of old behavior]
   - After: [description of new behavior]
   - Impact: [who is affected and how]

2. **[Change Type]**: [Description]
   ...

**Migration Guide**:
[If possible, suggest how users can migrate]

**Proceeding**: AI proceeding with major bump without blocking user.
```

**Rationale**: Major bumps require clear documentation for users upgrading.

### Step 7: Identify Version Files

Scan repository for version files:

**Python**:
```bash
grep -l "version" pyproject.toml setup.py setup.cfg 2>/dev/null
```

**Node.js**:
```bash
test -f package.json && echo "package.json"
```

**Rust**:
```bash
test -f Cargo.toml && echo "Cargo.toml"
```

**Generic**:
```bash
test -f VERSION && echo "VERSION"
```

**Return list of files to update**.

## Analysis Example

**Input**:
```
Changes on feature/add-validation branch:
+ src/validators.py (new file)
+ src/api/endpoints.py (modified - new endpoint)
M src/core/client.py (modified - bug fix)
```

**Analysis**:
```
1. New file: src/validators.py
   - New module for input validation
   - Public API addition
   - → Minor bump candidate

2. Modified: src/api/endpoints.py
   - New endpoint: POST /validate
   - New public API
   - → Minor bump candidate

3. Modified: src/core/client.py
   - Bug fix in error handling
   - Internal change
   - → Patch bump candidate

Overall: Minor features detected → Minor bump
Files to update: pyproject.toml
```

**Output**:
```json
{
  "bump_type": "minor",
  "reason": "New public API: validators module, /validate endpoint",
  "files": ["pyproject.toml"],
  "analysis": {
    "new_features": 2,
    "bug_fixes": 1,
    "breaking_changes": 0
  }
}
```

## Return Format (For Subtask Invocation)

When invoked as a subtask, return a JSON object:

```json
{
  "bump_type": "major|minor|patch|skip",
  "reason": "Brief explanation of why this bump type was chosen",
  "files": ["pyproject.toml", "package.json"],
  "analysis": {
    "new_features": 0,
    "bug_fixes": 0,
    "breaking_changes": 0,
    "code_files_count": 0,
    "non_code_files_count": 0
  },
  "major_reasoning": null  // or markdown document if bump_type == "major"
}
```

## Conflict Resolution Strategy

**When multiple PRs have version bumps**:

**Scenario**:
- PR #1: Minor bump queued
- PR #2: Patch bump queued
- AI determines: Use highest priority bump type

**Resolution Rules**:
```
Major > Minor > Patch
```

**Example**:
- PR #1 adds new feature → Minor bump
- PR #2 fixes bug → Patch bump
- Combined impact: Minor bump (higher priority)
- Version: 0.1.0 → 0.2.0 (not 0.1.1)

**AI Resolution**: Automatically applies highest priority bump type from accumulated PRs.

## Common Issues

| Issue | Resolution |
|-------|------------|
| No version files found | Scan for alternative version locations or create VERSION file |
| Mixed changes (code + docs) | Analyze code changes only, ignore documentation |
| Unclear if breaking | Err on side of minor/patch, document in changelog |
| User override conflicts | User-specified bump type takes precedence |
| Multiple version files | Update all detected version files atomically |

## Integration with Git-Workflow

**Integration point**: Before PR creation

**Workflow**:
1. Implementation completes
2. `git-workflow` invokes `version-bump --task analyze`
3. Analysis returns bump type and files
4. If bump required, `git-workflow` invokes `version-bump --task bump`
5. Version bump committed with implementation
6. PR created with combined changes

## Tips

- Major bumps **proceed automatically** (no user blocking)
- If unsure about breaking vs minor, choose minor (safer default)
- Document all major bump reasoning clearly
- Skip version bump for docs/chore/refactor PRs
- User override always takes precedence