# Task: since-last-release

## Purpose

Generate changelog entries for all commits since the last changelog update.

## Operating Protocol

1. **Identify last changelog commit**: Find the most recent commit that modified CHANGELOG.md
2. **Analyze commits**: Scan all commits since that point
3. **Categorize changes**: Group into Added/Changed/Fixed/Security/Deprecated
4. **Write entries**: Update CHANGELOG.md in [Unreleased] section
5. **Stage changes**: `git add CHANGELOG.md`

## Procedure

### Step 1: Find Last Changelog Update

```bash
git log --oneline --max-count=1 CHANGELOG.md
```

Use this commit hash as the start point for analyzing changes.

### Step 2: Collect Commits

```bash
git log <last-changelog-hash>..HEAD --pretty=format:"%h|%ad|%an|%s%n%b" --date=short
```

For merge commits, include the PR number and description from the merge message.

### Step 3: Categorize Changes

Analyze commits and categorize into:

| Category | Prefixes | Description |
|----------|----------|-------------|
| **Added** | `feat:`, `feat(`, `add` | New features, capabilities |
| **Changed** | `refactor:`, `change`, `update`, `improve` | Modifications to existing features |
| **Fixed** | `fix:`, `fix(`, `bug` | Bug fixes |
| **Security** | `security:`, `cve-`, `vuln` | Security improvements |
| **Deprecated** | `deprecate:`, `remove` | Features being phased out |

### Step 4: Transform to User-Facing Language

Convert technical commits to customer-friendly descriptions:

**Technical → User-Facing Examples:**

| Technical Commit | User-Facing Entry |
|------------------|-------------------|
| `fix(approval-gate): prevent silent halt when STATUS field missing` | `**Approval Gate Silent Halt** - Fixed silent halt when STATUS field is missing from sub-issues. Added default behavior and mandatory status reporting.` |
| `feat(skills): import skill-creator` | `**Skill Creator Import** - Imported skill-creator skill. Create new skills with templates and guided workflows.` |
| `git-workflow: enforce PR timing` | `**Git Workflow Enforcement** - Added enforcement gates for PR timing. PRs now require explicit instruction to create.` |

**Transformation Rules:**
1. Start with feature name (bold)
2. Describe WHAT changed (user perspective)
3. Explain WHY it matters (benefit/impact)
4. Keep to single paragraph
5. Use active voice
6. Avoid technical jargon

### Step 5: Write to CHANGELOG.md

Read current CHANGELOG.md, insert entries in [Unreleased] section:

1. Read existing entries in [Unreleased]
2. Merge new entries with existing (dedupe, consolidate)
3. Maintain alphabetical order within each category
4. Preserve existing formatting

**Format:**
```markdown
## [Unreleased]

### Added

- **Feature Name** - Brief description of what it does and why it matters.

### Changed

- **Feature Name** - What changed and the impact on users.

### Fixed

- **Feature Name** - What was fixed and the problem it solves.

### Security

- **Feature Name** - Security improvement and protection provided.

### Deprecated

- **Feature Name** - What is being phased out and timeline.
```

### Step 6: Stage Changes

```bash
git add CHANGELOG.md
```

### Step 7: Report Result

Report to calling context:
- Number of commits analyzed
- Number of entries added (by category)
- File updated: CHANGELOG.md

## Commit Message Conventions

Look for conventional commit prefixes:
- `feat:` / `feat(scope):` → **Added**
- `fix:` / `fix(scope):` → **Fixed**
- `refactor:` / `refactor(scope):` → **Changed**
- `docs:` → Often excluded (internal)
- `test:` / `tests:` → Often excluded (internal)
- `chore:` → Often excluded (internal)
- `style:` → Often excluded (internal)
- `perf:` → **Changed** (performance improvement)
- `security:` → **Security**

## Merge Commit Handling

For merge commits like:
```
Merge pull request #120 from NewsRx/spec/cleanup-succinct-output
Fix cleanup task to use succinct confirmation output
```

Use the PR number and description, not the merge itself. The actual changes are in the merged commits.

## Deduction Rules

1. **Skip internal commits**: Tests, CI config, internal refactoring
2. **Group related changes**: Multiple commits about same feature = one entry
3. **Preserve user impact**: Focus on user-visible changes
4. **Be concise**: One sentence per entry maximum

## Example Output

After analyzing commits since `ce6e5f1`:

```markdown
## [Unreleased]

### Added

- **Skill Creator Import** - Imported skill-creator from awesome-opencode-skills. Create new skills with templates and guided workflows.
- **Changelog Generator Integration** - Automated changelog updates during PR creation. Runs as sub-task for context isolation.

### Changed

- **Git Workflow Enforcement** - Added enforcement gates for PR timing. PRs require explicit "create a PR" instruction.
- **PR Workflow** - Changelog generator invoked automatically during PR creation.
- **Cleanup Task Output** - Streamlined to one-line confirmation.

### Fixed

- **Approval Gate Silent Halt** - Fixed silent halt when STATUS field missing. Added default behavior and status reporting.
- **Changelog Invocation** - Fixed PR workflow that referenced skill but never invoked it.
- **Changelog Verification** - Added checkpoint to verify changelog staged before squash.
```

## Context Required

- Git repository root
- CHANGELOG.md path
- Last changelog update commit hash