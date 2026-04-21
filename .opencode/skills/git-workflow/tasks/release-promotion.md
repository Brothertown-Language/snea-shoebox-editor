# Task: release-promotion

## ⚠️ TIER 1 MANDATE: Human-Only Merge

Agents MUST NOT execute `git merge` into `main`, `master`, or any protected branch.
All promotions MUST go through PR-based merge. The agent prepares the release;
a human reviews and merges the PR. Direct merge to a protected branch is a
CRITICAL GUIDELINE VIOLATION per `000-critical-rules.md`.

## Purpose

Prepare dev → main promotion, semver tagging, and release creation via PR-based workflow. Supports both submodule-based repos (promote each submodule in lockstep) and non-submodule repos. The agent creates the release PR; a human must merge it. Tags and releases are created post-merge.

## Operating Protocol

1. **Submodule repos:** When parent repo promotes dev → main, all submodules must be promoted in lockstep via PR
2. **Non-submodule repos:** Create release PR from dev targeting main, HALT for human merge, then tag and release
3. **Explicit trigger:** Developer can instruct promotion of individual submodules
4. **Tag validation:** All semver tags must pass `validate-release-tags.sh --semver` before parent promotion proceeds

## Entry Criteria

- Repository is promoting dev → main (automatic or explicit), OR
- Developer has explicitly instructed "promote submodule <X>" or "push submodule <Y>"
- Post-merge: Human has merged the release PR and developer wants tagging + release creation

## Exit Criteria

### Submodule Path

- All promoted submodules have a release PR created targeting main
- Agent has HALTed for human merge of each submodule PR
- After human merge: each promoted submodule has an annotated semver tag on main (auto-incremented patch or developer-specified)
- After human merge: each promoted submodule has a GitHub/GitBucket release created
- After human merge: parent submodule refs updated to tagged SHAs
- `validate-release-tags.sh --semver` exits 0

### Non-Submodule Path

- Release PR created targeting main from release branch
- Agent has HALTed for human merge
- After human merge: Annotated semver tag created on main (auto-incremented patch or developer-specified)
- After human merge: Tags pushed to origin
- After human merge: GitHub/GitBucket release created

## Procedure

### Step 0: Route to Release Path

```bash
test -f .gitmodules
```

- If `.gitmodules` EXISTS: Proceed to **Submodule Path** (Step 1)
- If `.gitmodules` does NOT exist: Proceed to **Non-Submodule Path** (Step N1)

---

## Submodule Path

### Step 0.5: Detect Issue System Availability

Before iterating submodules, detect each submodule's host platform and test API access. Results are cached for the session so that provenance tracking (Step 2h) can use them without redundant API calls.

For each submodule listed in `.gitmodules`:

```bash
git config --file .gitmodules --get-regexp path | awk '{print $2}'
```

For each submodule `<path>`:

**a. Determine platform from remote URL:**

```bash
cd <path>
REMOTE_URL=$(git remote get-url origin)
cd ..
```

Parse `REMOTE_URL` to identify the hosting platform:

| URL Pattern | Platform |
| -- | -- |
| Contains `github.com` | `github` |
| Matches known GitBucket host pattern | `gitbucket` |
| No match | `unknown` |

**b. Test API availability:**

| Platform | Test | Result Mapping |
| -- | -- | -- |
| `github` | `github_get_file_contents(owner, repo, path="")` | Success → `full`; 403 → `no-access`; 404 → `no-repo`; Auth error → `auth-failed` |
| `gitbucket` | `GET /api/v3/repos/<owner>/<repo>` per `gitbucket-api` skill | Success → `full`; 403 → `no-access`; 404 → `no-repo`; Auth error → `auth-failed` |
| `unknown` | No API available | `no-access` |

**c. Cache result:**

Session-scoped cache keyed by `<owner>/<repo>`. Value: `{platform, access_level, reason}`.

| `access_level` | Tier Used by Provenance |
| -- | -- |
| `full` | Tier 1 (issue + PR) |
| `issue-only` | Tier 2 (issue only) |
| `no-access`, `auth-failed`, `no-repo` | Tier 3 (commit message) |

**This step is non-blocking.** Detection failures default to Tier 3 silently.

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

#### 2a: Determine Next Semver Tag

**Auto-increment patch version:**

```bash
cd <path>
LATEST_TAG=$(git tag --sort=-v:refname | head -1)
cd ..

if [ -z "$LATEST_TAG" ]; then
    NEXT_TAG="v0.1.0"
else
    VERSION=${LATEST_TAG#v}
    MAJOR=$(echo "$VERSION" | cut -d. -f1)
    MINOR=$(echo "$VERSION" | cut -d. -f2)
    PATCH=$(echo "$VERSION" | cut -d. -f3)
    NEXT_TAG="v${MAJOR}.${MINOR}.$((PATCH + 1))"
fi
```

**Developer-specified version:** If developer provided an explicit version (e.g., "promote submodule X as v2.0.0"), use that version instead of auto-increment.

#### 2b: Create Release Branch from Dev

```bash
cd <path>
RELEASE_BRANCH="release/dev-to-main-v${NEXT_TAG#v}"
git checkout dev
git checkout -b "$RELEASE_BRANCH"
cd ..
```

#### 2c: Push Release Branch

```bash
cd <path>
git push origin "$RELEASE_BRANCH"
cd ..
```

#### 2d: Create PR Targeting Main

Create a release PR in the submodule repo targeting `main` (or `master`):

**For GitHub:**

```
github_create_pull_request(
    owner=<sub-owner>,
    repo=<sub-repo>,
    title="Release $NEXT_TAG: promote dev → main",
    head="$RELEASE_BRANCH",
    base="main",
    body="Release $NEXT_TAG\n\nAutomated submodule promotion from dev → main.\n\n⚠️ This PR was prepared by an AI agent. Human review required before merge."
)
```

**For GitBucket:** Use GitBucket API per `gitbucket-api` skill.

#### 2e: HALT — Wait for Human Merge

Report the PR URL to chat. HALT and wait for the human to merge the PR.

After human merges the PR, proceed to post-merge steps (2f-2h). These may be invoked in a subsequent session using `--task release-promotion --post-merge`.

#### 2f: (Post-merge) Tag Main with Semver Tag

```bash
cd <path>
git checkout main
git pull origin main
git tag -a "$NEXT_TAG" -m "Release $NEXT_TAG: promoted from dev #<parent-issue>"
cd ..
```

#### 2g: (Post-merge) Push Tags and Create Platform Release

```bash
cd <path>
git push origin main --tags
cd ..
```

**For GitHub:**

Use GitHub MCP to create release:

```
github_get_latest_release(owner=<sub-owner>, repo=<sub-repo>)
```

**Release body template:**

```markdown
Release $NEXT_TAG

Automated submodule promotion from dev → main.
```

**For GitBucket:** Use GitBucket API per `gitbucket-api` skill.

#### 2h: Return to Parent and Update Ref

```bash
cd <parent-repo-root>
git add <path>
```

#### 2i: Create Provenance Tracking

After promoting a submodule, invoke provenance tracking with inline fallback:

```
Invoke: /skill git-workflow --task provenance --mode=promotion
```

**Context parameters to pass:**

| Parameter | Value |
| -- | -- |
| parent_repo | `<github.owner>/<github.repo>` from session init |
| parent_branch | The branch being released (commonly `main` or `dev`) |
| parent_issue | Issue number from the release spec |
| submodule_path | Path of the promoted submodule |
| tag_name | The semver tag created in Step 2f |
| source_branch | The branch promoted (typically `dev`) |
| change_description | Brief description of changes in this submodule |
| parent_release_ref | Parent release tag or issue reference |

**Inline fallback (P12) — provenance attempts each tier and falls back automatically:**

1. Detect submodule platform and API availability (provenance.md Step 0-1)
2. Attempt Tier 1 (issue + PR):
   - Create issue: `Release <submodule-path> promoted from <source-branch>`
   - Create PR targeting `main` with `Fixes #<submodule-issue-number>` (P8)
   - If PR creation fails → downgrade to Tier 2, log reason
3. Attempt Tier 2 (issue only):
   - If issue creation fails → downgrade to Tier 3, log reason
4. Tier 3 (commit message):
   - No API calls; provenance in tag message: `Release <path>: promoted from <branch> #[parent-issue]` (P9)
5. All fallbacks are SILENT — no HALT, no blocking of the promotion workflow

**Tier logging (P13):** Each provenance operation logs:
```
{timestamp, submodule, operation: "promotion", tier: <1|2|3>, issue_number?, pr_number?, tag_name}
```

**Cross-reference (P14/P15):** When Tier 1 or 2 succeeds, post comment on parent issue:
```
Submodule provenance tracked in <sub-owner>/<sub-repo>#<submodule-issue-number> (Tier <tier>)
[If PR exists: PR #<pr-number>]
Operation: promotion | Submodule: <submodule-path> | Tag: <tag-name>
```

**Provenance is non-blocking:** The promotion workflow continues regardless of provenance outcome. Failures at any tier result in silent downgrade, never HALT.

#### Cross-Reference Step: Add Parent Issue Comment for Promotion

After promotion provenance issue creation succeeds (Tier 1 or Tier 2 only):

1. Add a parent issue comment referencing the submodule provenance issue
2. Comment format includes: submodule repo, issue number, PR number (if applicable), tier used
3. Example: `Submodule provenance: <sub-owner>/<sub-repo>#<issue-number> (Tier 1: Issue + PR)`
4. If tier used is Tier 2 (issue only): `Submodule provenance: <sub-owner>/<sub-repo>#<issue-number> (Tier 2: Issue only)`
5. If parent issue comment creation fails: log the failure and continue — cross-reference comments are non-blocking
6. Cross-reference comments provide bidirectional traceability between parent release and submodule promotion

**See `provenance.md` → promotion-provenance section for complete procedure.**

### Step 3: Validate Tags

After all submodules are promoted and tagged (post-merge):

```bash
./.opencode/scripts/validate-release-tags.sh --semver
```

**MUST exit 0.** If it exits non-zero:

1. Report which submodule failed validation
2. HALT — do not proceed with parent promotion
3. Developer must resolve the tag issue before retrying

### Step 4: Proceed with Parent Promotion

After Step 3 passes, the parent repository may proceed with its own dev → main promotion via the Non-Submodule Path below.

---

## Non-Submodule Path

### Step N1: Determine Next Semver Tag

**Auto-increment patch version:**

```bash
LATEST_TAG=$(git tag --sort=-v:refname | head -1)

if [ -z "$LATEST_TAG" ]; then
    NEXT_TAG="v0.1.0"
else
    VERSION=${LATEST_TAG#v}
    MAJOR=$(echo "$VERSION" | cut -d. -f1)
    MINOR=$(echo "$VERSION" | cut -d. -f2)
    PATCH=$(echo "$VERSION" | cut -d. -f3)
    NEXT_TAG="v${MAJOR}.${MINOR}.$((PATCH + 1))"
fi
```

**Developer-specified version:** If developer provided an explicit version (e.g., "promote as v2.0.0"), use that version instead of auto-increment.

### Step N2: Create Release Branch from Dev

```bash
RELEASE_BRANCH="release/dev-to-master-v${NEXT_TAG#v}"
git checkout dev
git checkout -b "$RELEASE_BRANCH"
```

### Step N3: Push Release Branch

```bash
git push origin "$RELEASE_BRANCH"
```

### Step N4: Create PR Targeting Master

Create a release PR targeting `master` (or `main`):

**For GitHub:**

```
github_create_pull_request(
    owner=<github.owner>,
    repo=<github.repo>,
    title="Release $NEXT_TAG: promote dev → main",
    head="$RELEASE_BRANCH",
    base="master",
    body="Release $NEXT_TAG\n\nAutomated dev → main promotion.\n\n⚠️ This PR was prepared by an AI agent. Human review required before merge."
)
```

**For GitBucket:** Use GitBucket API per `gitbucket-api` skill.

### Step N5: HALT — Wait for Human Merge

Report the PR URL to chat. HALT and wait for the human to merge the PR.

After human merges the PR, proceed to post-merge steps (N6-N8). These may be invoked in a subsequent session using `--task release-promotion --post-merge`.

### Step N6: (Post-merge) Tag Master with Semver Tag

```bash
git checkout master
git pull origin master
git tag -a "$NEXT_TAG" -m "Release $NEXT_TAG"
```

### Step N7: (Post-merge) Push Tags

```bash
git push origin master --tags
```

### Step N8: (Post-merge) Create Platform Release

**For GitHub:**

Use GitHub MCP to create release:

```
github_get_latest_release(owner=<github.owner>, repo=<github.repo>)
```

Then create release via GitHub API with:

```markdown
Release $NEXT_TAG

Automated dev → main promotion.
```

**For GitBucket:** Use GitBucket API per `gitbucket-api` skill.

**Release body template:**

```markdown
Release $NEXT_TAG

Automated dev → main promotion.
```

---

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
| T19 | Submodule dev → main PR is created; human merges |
| T20 | Semver tag is auto-incremented (patch version) when no developer-specified version |
| T21 | GitHub/GitBucket release is created post-merge for each promoted submodule |
| T22 | Parent submodule refs are updated to tagged SHAs after human merge |
| T23 | `validate-release-tags.sh --semver` passes after automated promotion |
| T24 | Developer can explicitly instruct push or promotion of individual submodules |
| T25 | Submodule SHAs are locked (no `--remote` flag) during release promotion |
| T26 | Non-submodule repos: agent creates release PR; human merges |
| T27 | Non-submodule repos: semver tag is created post-merge and pushed |
| T28 | Non-submodule repos: platform release is created post-merge |

## Common Issues

| Issue | Resolution |
| -- | -- |
| PR has merge conflicts | Classify per conflict-resolution skill; Tier 3 → HALT for developer |
| Tag already exists | Report error; developer must specify a different version |
| `validate-release-tags.sh` fails | HALT; report which submodule failed and why |
| No previous tag exists | Default to `v0.1.0` as first release tag |
| Submodule has no dev branch | HALT; report that dev branch must exist before promotion |
| Human merges but forgets to tag | Re-invoke `--task release-promotion --post-merge` for tagging + release |
| Release branch name collision | Append timestamp or short SHA to branch name |
| Pre-merge hook blocks direct merge | N/A — PR-based approach avoids this; skill never directs direct merge |

## Context Required

- Related skills: `conflict-resolution` (merge conflict classification), `gitbucket-api` (GitBucket release creation)
- Related tasks: `pre-work` (submodule initialization), `cleanup` (post-merge cleanup)
- Related scripts: `validate-release-tags.sh` (tag validation)