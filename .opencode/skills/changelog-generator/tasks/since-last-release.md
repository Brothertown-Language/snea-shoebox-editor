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

### Step 3: Extract Branch Headers and Categorize

Analyze **merge commits** to extract branch names and map branch prefixes to changelog sections.

**Branch Prefix → Category Mapping:**

| Branch Prefix | Changelog Section | Description |
| -- | -- | -- |
| `spec/` | Primary (own `### <branch-name>` header) | Spec-based feature work |
| `feature/` | Added | New features |
| `fix/` | Fixed | Bug fixes |
| `hotfix/` | Fixed | Urgent bug fixes |
| `chore/` | Changed | Maintenance tasks |
| `doc/` | Changed | Documentation updates |
| `skill/` | Changed | Skill updates |

**Merge Commit Parsing:**

From merge commit message:
```
Merge pull request #120 from <OWNER>/spec/example-branch-name
Fix cleanup task to use succinct confirmation output
```
Extract branch name: `spec/example-branch-name` → prefix `spec/` → category: primary → header: `### spec/example-branch-name`

**Fallback — Conventional Commit Prefix:**

When no merge commit is available (squash merge, direct commit, or non-PR workflow), fall back to conventional commit prefix matching:

| Convention Prefix | Category |
| -- | -- |
| `feat:` / `feat(scope):` | Added |
| `fix:` / `fix(scope):` | Fixed |
| `refactor:` / `refactor(scope):` | Changed |
| `chore:` | Changed |
| `docs:` | Changed |
| `perf:` | Changed |
| `security:` | Security |
| `deprecate:` | Deprecated |

### Step 4: Transform to User-Facing Language

Convert technical commits to customer-friendly descriptions:

**Technical → User-Facing Examples:**

| Technical Commit | User-Facing Entry |
| -- | -- |
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

### Step 5: Write Incremental Entries to CHANGELOG.md

**Incremental-only approach:** Append new `### <branch-name>` entries after existing ones in `[Unreleased]`. Never rewrite the entire `[Unreleased]` section.

**Procedure:**

1. Read current CHANGELOG.md
2. Identify the last entry in `[Unreleased]`
3. Append new `### <branch-name>` sections after existing content
4. Preserve all existing entries unchanged
5. Do not dedupe or reorganize existing entries

**Feature-Branch-Header Format:**

Entries are grouped under their branch name as a subsection header within `[Unreleased]`:

```markdown
## [Unreleased]

### spec/example-branch-name

- **Feature Name** (#123) - Brief description of what it does and why it matters.

### spec/another-branch

- **Another Feature** (#124) - What changed and the impact on users.
- **Bug Fix** (#124) - What was fixed and the problem it solves.
```

For non-spec branches (feature/, fix/, hotfix/, chore/, doc/, skill/), map to the appropriate `### Added`, `### Changed`, `### Fixed`, `### Security`, or `### Deprecated` section header and append entries there. If that section header already exists, append after existing entries within it.

**Fallback format** (when no branch information available):

```markdown
### Added

- **Feature Name** - Brief description of what it does and why it matters.

### Fixed

- **Feature Name** - What was fixed and the problem it solves.
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

## Commit Message Conventions (Fallback)

When branch headers are unavailable, fall back to conventional commit prefixes:

- `feat:` / `feat(scope):` → **Added**
- `fix:` / `fix(scope):` → **Fixed**
- `refactor:` / `refactor(scope):` → **Changed**
- `docs:` → Often excluded (internal)
- `test:` / `tests:` → Often excluded (internal)
- `chore:` → Often excluded (internal)
- `style:` → Often excluded (internal)
- `perf:` → **Changed** (performance improvement)
- `security:` → **Security**

## Branch Header Extraction

For merge commits, extract the branch name from the merge message:

```
Merge pull request #120 from <OWNER>/spec/example-branch-name
Fix cleanup task to use succinct confirmation output
```

- Branch name: `spec/example-branch-name`
- Prefix: `spec/` → Primary section (use branch name as header)
- Changelog header: `### spec/example-branch-name`

All commits in that PR are grouped under this branch header section.

**Fallback:** When no merge commit exists (squash merge, direct commit), use the conventional commit prefix on the individual commit message.

## Deduction Rules

1. **Skip internal commits**: Tests, CI config, internal refactoring
2. **Group related changes**: Multiple commits about same feature = one entry
3. **Preserve user impact**: Focus on user-visible changes
4. **Be concise**: One sentence per entry maximum

## Example Output

After analyzing merge commits since `ce6e5f1`:

```markdown
## [Unreleased]

### spec/734-divide-and-conquer

- **Divide-and-Conquer Skill** (#734) - New discipline-enforcing skill that mandates pre-flight context-fit assessment before implementation. Tasks that risk context window overflow are decomposed and dispatched to sub-agents.

### spec/698-fix-phase1-schema-gaps

- **FK Cascade on Record Deletion** (#698) - Fixed FK violation crash when deleting records. Added explicit deletes in hard_delete_record() and batch paths.
- **Hard-Delete Unit Tests** (#698) - Added 5 unit tests for hard_delete_record() covering search entry cleanup, EditHistory cleanup, and edge cases.

### Added

- **Environment Variable Rename** (from `spec/759-env-rename`) - Renamed JUNIE_PRIVATE_DB to OPENCODE across source, tests, scripts, and docs.

### Fixed

- **Sub-agent worktree dispatch** (from `spec/fix-subagent-worktree-741`) - Add worktree awareness to all sub-agent dispatch and skill creation.
```

## Context Required

- Git repository root
- CHANGELOG.md path
- Last changelog update commit hash
