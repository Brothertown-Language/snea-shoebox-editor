# Task: release-promotion

## Purpose

Automate submodule dev → main promotion, semver tagging, and release creation when the parent repository promotes dev → main. Also supports explicit developer instruction to promote or push individual submodules.

## Operating Protocol

1. **Automatic trigger:** When parent repo promotes dev → main, all submodules must be promoted in lockstep
2. **Explicit trigger:** Developer can instruct promotion of individual submodules
3. **Tag validation:** All semver tags must pass `validate-release-tags.sh --semver` before parent promotion proceeds

## Entry Criteria

- Parent repo is promoting dev → main (automatic), OR
- Developer has explicitly instructed "promote submodule <X>" or "push submodule <Y>"
- `.gitmodules` exists in the worktree

## Exit Criteria

- All promoted submodules have main merged from dev
- Each promoted submodule has an annotated semver tag (auto-incremented patch or developer-specified)
- Each promoted submodule has a GitHub/GitBucket release created
- Parent submodule refs updated to tagged SHAs
- `validate-release-tags.sh --semver` exits 0

## Procedure

### Step 0: Check for .gitmodules

```bash
test -f .gitmodules
```

If `.gitmodules` does NOT exist: Skip this entire task. No submodules to promote.

### Step 1: Lock Submodule SHAs

When promoting parent dev → main, submodule SHAs must be locked to their committed values (no `--remote`):

```bash
git submodule update --init
```

**CRITICAL:** Do NOT use `--remote` flag. During release promotion, submodules must be at their committed SHAs, not advanced to the tip of their dev branches. Using `--remote` would silently advance submodules beyond the tested state, violating release integrity.

### Step 2: Promote Each Submodule

For each submodule listed in `.gitmodules`:

```bash
# Extract submodule paths
git config --file .gitmodules --get-regexp path | awk '{print $2}'
```

For each submodule `<path>`:

#### 2a: Enter Submodule and Switch to Main

```bash
cd <path>
git checkout main
```

#### 2b: Merge Dev into Main

```bash
git merge dev
```

If merge conflicts occur, classify per `conflict-resolution` skill:
- Tier 1 (Trivial): whitespace/formatting → auto-resolve, silent
- Tier 2 (Textual but safe): same intent, different text → auto-resolve, note in chat
- Tier 3 (Intent conflict): different goals → HALT, flag for developer review

#### 2c: Determine Next Semver Tag

**Auto-increment patch version:**

```bash
# Get the highest existing tag
LATEST_TAG=$(git tag --sort=-v:refname | head -1)

if [ -z "$LATEST_TAG" ]; then
    NEXT_TAG="v0.1.0"
else
    # Strip v-prefix, increment patch
    VERSION=${LATEST_TAG#v}
    MAJOR=$(echo "$VERSION" | cut -d. -f1)
    MINOR=$(echo "$VERSION" | cut -d. -f2)
    PATCH=$(echo "$VERSION" | cut -d. -f3)
    NEXT_TAG="v${MAJOR}.${MINOR}.$((PATCH + 1))"
fi
```

**Developer-specified version:** If developer provided an explicit version (e.g., "promote submodule X as v2.0.0"), use that version instead of auto-increment.

#### 2d: Create Annotated Tag

```bash
git tag -a "$NEXT_TAG" -m "Release $NEXT_TAG"
```

#### 2e: Push Submodule Main and Tags

```bash
git push origin main --tags
```

#### 2f: Create Platform Release

**For GitHub:**

```python
github_create_or_update_file = None  # Not applicable
# Use GitHub API to create release:
github_get_latest_release(owner=..., repo=...)  # To check existing
# Then use GitHub release creation via MCP or API
```

**For GitBucket:** Use GitBucket API per `gitbucket-api` skill.

**Release body template:**

```markdown
Release $NEXT_TAG

Automated submodule promotion from dev → main.
```

#### 2g: Return to Parent and Update Ref

```bash
cd <parent-repo-root>
git add <path>
```

### Step 3: Validate Tags

After all submodules are promoted and tagged:

```bash
./.opencode/scripts/validate-release-tags.sh --semver
```

**MUST exit 0.** If it exits non-zero:

1. Report which submodule failed validation
2. HALT — do not proceed with parent promotion
3. Developer must resolve the tag issue before retrying

### Step 4: Proceed with Parent Promotion

After Step 3 passes, the parent repository may proceed with its own dev → main promotion.

## Explicit Developer Instruction

Developers can target individual submodules without promoting all:

| Instruction | Action |
| -- | -- |
| "promote submodule shared-skills" | Promote only the `shared-skills` submodule |
| "push submodule shared-templates" | Push only `shared-templates` to its dev branch |
| "promote submodule X as v2.0.0" | Promote X with developer-specified version |

**Explicit instructions do NOT require all submodules to be promoted.** Only the named submodule(s) are processed.

## Acceptance Criteria

| ID | Criterion |
| -- | -- |
| T19 | Submodule dev → main promotion is automated when parent promotes dev → main |
| T20 | Semver tag is auto-incremented (patch version) when no developer-specified version |
| T21 | GitHub release is created for each promoted submodule |
| T22 | Parent submodule refs are updated to tagged SHAs after promotion |
| T23 | `validate-release-tags.sh --semver` passes after automated promotion |
| T24 | Developer can explicitly instruct push or promotion of individual submodules |
| T25 | Submodule SHAs are locked (no `--remote` flag) during release promotion |

## Common Issues

| Issue | Resolution |
| -- | -- |
| Merge conflict during dev → main | Classify per conflict-resolution skill; Tier 3 → HALT |
| Tag already exists | Report error; developer must specify a different version |
| `validate-release-tags.sh` fails | HALT; report which submodule failed and why |
| No previous tag exists | Default to `v0.1.0` as first release tag |
| Submodule has no dev branch | HALT; report that dev branch must exist before promotion |

## Context Required

- Related skills: `conflict-resolution` (merge conflict classification), `gitbucket-api` (GitBucket release creation)
- Related tasks: `pre-work` (submodule initialization), `cleanup` (post-merge cleanup)
- Related scripts: `validate-release-tags.sh` (tag validation)