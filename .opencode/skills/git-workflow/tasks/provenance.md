# Task: provenance

## Purpose

Create provenance tracking issues and PRs in submodule repositories after push or promotion operations. Detects the submodule's host platform (GitHub, GitBucket, or unknown), tests API availability, and falls back gracefully through a three-tier model when access is limited.

## Operating Protocol

1. **Triggered after push or promotion** — when a submodule is pushed/merged, provenance tracking should be attempted
2. **Three-tier fallback** — if full API access is unavailable, fall back silently to the next tier; never HALT or block the git workflow
3. **Platform detection** — determine the submodule's issue system from its remote URL before attempting any API calls

## Entry Criteria

- A submodule has been pushed or promoted (commit merged to dev/main)
- `.gitmodules` exists in the worktree
- Submodule remote URL is available via `git remote get-url origin` inside the submodule

## Exit Criteria

- Platform detection result is cached for the session
- If API access is available (Tier 1 or 2), a provenance issue (and optionally PR) is created in the submodule repo
- If no API access (Tier 3), a commit message with provenance metadata is documented
- All detection results are logged

## Procedure

### Step 0: Platform Detection

For each submodule that has been pushed or promoted, determine the host platform from its remote URL.

#### `detect_submodule_platform(submodule_remote_url)`

Parse the remote URL to identify the hosting platform:

| URL Pattern | Platform | Example |
| -- | -- | -- |
| Contains `github.com` | `github` | `https://github.com/owner/repo.git`, `git@github.com:owner/repo.git` |
| Matches known GitBucket host pattern | `gitbucket` | `https://gitbucket.example.com/owner/repo.git`, `git@gitbucket.example.com:owner/repo.git`, port-based patterns like `:8080/owner/repo` |
| No match | `unknown` | Any URL that doesn't match the above patterns |

**Parsing logic:**

```
1. Extract the hostname from the remote URL
   - SSH: git@<hostname>:<owner>/<repo>.git → hostname is between @ and :
   - HTTPS: https://<hostname>/<owner>/<repo>.git → hostname is the authority component
2. If hostname is "github.com" → platform = "github"
3. If hostname matches known GitBucket patterns (non-github.com hostname with /owner/repo path, or port-based patterns like :8080) → platform = "gitbucket"
4. Otherwise → platform = "unknown"
```

**Owner and repo extraction:**

From any URL format, extract `owner` and `repo`:

```
SSH:   git@<host>:<owner>/<repo>.git  → owner=<owner>, repo=<repo>
HTTPS: https://<host>/<owner>/<repo>.git → owner=<owner>, repo=<repo>
```

Strip trailing `.git` from repo name if present.

### Step 1: Test API Availability

#### `test_platform_api_availability(platform, owner, repo)`

Test whether the issue system API is reachable and authenticated for the submodule repo.

**For GitHub:**

```
1. Call github_get_file_contents(owner=<owner>, repo=<repo>, path="") or equivalent lightweight read
2. If successful → {platform: "github", access_level: "full", reason: null}
3. Map error responses:
   - HTTP 403 → {platform: "github", access_level: "no-access", reason: "HTTP 403 Forbidden"}
   - HTTP 404 → {platform: "github", access_level: "no-repo", reason: "HTTP 404 Not Found"}
   - Authentication error → {platform: "github", access_level: "no-access", reason: "Authentication failed"}
```

**For GitBucket:**

```
1. Call GET /api/v3/repos/<owner>/<repo> (document the API call pattern per gitbucket-api skill)
2. If successful → {platform: "gitbucket", access_level: "full", reason: null}
3. Map error responses:
   - HTTP 403 → {platform: "gitbucket", access_level: "no-access", reason: "HTTP 403 Forbidden"}
   - HTTP 404 → {platform: "gitbucket", access_level: "no-repo", reason: "HTTP 404 Not Found"}
   - Authentication error → {platform: "gitbucket", access_level: "no-access", reason: "Authentication failed"}
```

**For unknown platform:**

```
→ {platform: "unknown", access_level: "no-access", reason: "Unknown platform — no API available"}
```

#### Access Level Semantics

| `access_level` | Meaning | Tier |
| -- | -- | -- |
| `full` | Issue + PR creation available | Tier 1 |
| `issue-only` | Issue creation works, PR creation fails | Tier 2 |
| `no-access` | No API access (403, 404, auth failure, unknown platform) | Tier 3 |

### Step 2: Cache Detection Result

#### `cache_detection_result(result)`

Cache the platform detection result for the session duration to avoid repeated API calls for the same submodule.

**Cache key:** `<owner>/<repo>` (derived from the submodule remote URL)

**Cache value:** The full detection result dictionary: `{platform, access_level, reason}`

**Session-scoped:** Cache exists only for the current session. A new session re-detects from scratch.

**Implementation:** Use a simple in-memory dictionary. No persistent storage — the cache resets when the session ends.

### Step 3: Three-Tier Fallback Model

After platform detection and API availability testing, select the appropriate provenance tracking tier:

**Tier 1: Issue + PR in Submodule Repo**

When `access_level` is `full`:

```
1. Create a provenance issue in the submodule repo
   - Title: "Provenance: <parent-repo> <operation> <ref>"
   - Body: Links parent repo, issue, PR, and commit SHA
2. Create a PR in the submodule repo (if applicable)
3. Record: {timestamp, submodule, operation: "issue+pr", tier: 1, issue_number, pr_number}
```

**Tier 2: Issue Only in Submodule Repo**

When `access_level` is `issue-only`:

```
1. Create a provenance issue in the submodule repo
   - Title: "Provenance: <parent-repo> <operation> <ref>"
   - Body: Links parent repo, issue, and commit SHA; notes PR creation unavailable
2. Record: {timestamp, submodule, operation: "issue-only", tier: 2, issue_number}
```

**Tier 3: Commit Message Provenance**

When `access_level` is `no-access`:

```
1. No API calls attempted — provenance is recorded via commit message metadata
2. The commit message in the submodule already contains the SHA and operation info
3. Record: {timestamp, submodule, operation: "commit-message", tier: 3}
```

**All fallbacks are silent — no HALT, no blocking of git workflow.** If Tier 1 fails, fall back to Tier 2. If Tier 2 fails, fall back to Tier 3. The git workflow continues regardless of provenance tracking outcome.

### Step 4: Log Detection Results

Every detection result is logged for audit purposes:

```json
{
  "timestamp": "<ISO 8601>",
  "submodule": "<owner>/<repo>",
  "operation": "<push|promote>",
  "tier": 1,
  "issue_number": null,
  "pr_number": null
}
```

Logging is informational only — it does not affect the git workflow.

## Acceptance Criteria

| ID | Criterion |
| -- | -- |
| P10 | Platform detection parses remote URL: github.com → github, known GitBucket host → gitbucket, unknown → unknown |
| P11 | Error handling maps: 403 → no-access, 404 → no-repo, auth error → auth-failed; all fallback to Tier 3 |
| P12 | Detection results are cached for session duration (no repeated API calls) |
| P13 | Three-tier fallback model: full → issue+pr, issue-only → issue, no-access → commit message |
| P14 | All fallbacks are silent — no HALT, no blocking of git workflow |
| P15 | All detection results are logged with timestamp, submodule, operation, tier, and optional issue/pr numbers |

## Common Issues

| Issue | Resolution |
| -- | -- |
| Remote URL uses non-standard format | Attempt best-effort parsing; if unrecoverable, classify as `unknown` platform |
| GitHub API rate limited | Treat as `no-access` with reason "API rate limited"; fall back to Tier 3 |
| GitBucket API unreachable | Treat as `no-access` with reason "API unreachable"; fall back to Tier 3 |
| Submodule has no remote | Classify as `unknown` platform; fall back to Tier 3 |
| Platform detected but repo not found (404) | Return `{platform, "no-repo", "HTTP 404 Not Found"}`; fall back to Tier 3 |

## Context Required

- Related skills: `gitbucket-api` (GitBucket API calls), `conflict-resolution` (if provenance PR has conflicts)
- Related tasks: `release-promotion` (submodule promotion), `review-prep` (submodule push)
- Related guidelines: `000-critical-rules.md` (fallback is silent, never HALT)

## dev-push-provenance

### Purpose

After pushing a submodule to its remote dev branch during the parent repo's review-prep workflow, create a provenance issue (and optionally PR) in the submodule repository to track the cross-repo relationship. Falls back silently through three tiers when API access is limited.

### Entry Criteria

- Submodule has been pushed to its remote branch (dev or main)
- Platform detection has completed (Step 0 above) and result is cached
- Parent repo, parent branch, and parent issue number are known

### Procedure

#### Step 5: Detect Platform and Issue System Availability

For each submodule that was pushed, call the Phase 1 detection functions:

```
1. detect_submodule_platform(submodule_remote_url) → {platform, owner, repo}
2. Check cache for <owner>/<repo>
   - If cached → use cached result
   - If not cached → test_platform_api_availability(platform, owner, repo) → {platform, access_level, reason}
3. cache_detection_result(result)
```

#### Step 6: Attempt Tier 1 — Create Issue + PR

When `access_level` is `full`:

```
1. Create issue in submodule repo:
   - Title: "Sync from <parent-repo>/<parent-branch>: <change-description>"
   - Body template:

     **Triggered by:** <parent-repo>#<parent-issue>
     **Parent branch:** <parent-branch>
     **Submodule path:** <submodule-path>
     **Change:** <description of what changed in the submodule>

     This submodule update was pushed as part of <parent-repo>/<parent-branch> work on #<parent-issue>.

     ---

     <AI-Name> (<ModelID>)

   - For GitHub: github_issue_write(method="create", owner=<sub-owner>, repo=<sub-repo>, title=..., body=...)
   - For GitBucket: POST /api/v3/repos/<owner>/<repo>/issues (per gitbucket-api skill)

2. Create PR in submodule repo (targeting submodule's dev branch):
   - Title: same as issue title
   - Body:

     Fixes #<submodule-issue-number>

     **Triggered by:** <parent-repo>#<parent-issue>
     **Parent branch:** <parent-branch>

     ---

     <AI-Name> (<ModelID>)

   - For GitHub: github_create_pull_request(owner=<sub-owner>, repo=<sub-repo>, title=..., body=..., head="<pushed-branch>", base="dev")
   - For GitBucket: POST /api/v3/repos/<owner>/<repo>/pulls (per gitbucket-api skill)

3. If PR creation succeeds:
   - Record: {timestamp, submodule, operation: "dev-push", tier: 1, issue_number, pr_number}
   - Post parent issue comment cross-referencing submodule provenance (see Step 9)
   - DONE for this submodule

4. If PR creation fails:
   - Log failure reason: {tier: 1, step: "pr-creation", reason: <error message>}
   - Downgrade to Tier 2
```

#### Step 7: Attempt Tier 2 — Issue Only

When Tier 1 PR creation failed, or `access_level` is `issue-only`:

```
1. If issue was NOT already created in Tier 1 attempt:
   Create issue in submodule repo:
   - Title: "Sync from <parent-repo>/<parent-branch>: <change-description>"
   - Body:

     **Triggered by:** <parent-repo>#<parent-issue>
     **Parent branch:** <parent-branch>
     **Submodule path:** <submodule-path>
     **Change:** <description>

     ⚠️ PR creation unavailable — this issue serves as the sole provenance record.

     ---

     <AI-Name> (<ModelID>)

   - For GitHub: github_issue_write(method="create", ...)
   - For GitBucket: POST /api/v3/repos/<owner>/<repo>/issues

2. If issue creation succeeds:
   - Record: {timestamp, submodule, operation: "dev-push", tier: 2, issue_number, pr_number: null}
   - Post parent issue comment cross-referencing submodule provenance (see Step 9)
   - DONE for this submodule

3. If issue creation fails:
   - Log failure reason: {tier: 2, step: "issue-creation", reason: <error message>}
   - Downgrade to Tier 3
```

#### Step 8: Tier 3 — Commit Message Provenance

When Tier 2 issue creation failed, or `access_level` is `no-access`:

```
1. No API calls attempted
2. Structured commit message metadata is the provenance record:

   Sync <submodule-path> from <parent-repo>/<parent-branch>

   Triggered-by: <parent-repo>#<parent-issue>
   Change: <description>
   [skip-ci]

3. Record: {timestamp, submodule, operation: "dev-push", tier: 3, issue_number: null, pr_number: null}
```

**Note:** The commit in the submodule should already contain this structured message. If not, the agent amends the commit message or documents the provenance in the log only — never force-pushes or rewrites submodule history.

#### Step 9: Cross-Reference Parent Issue

When Tier 1 or Tier 2 succeeds (a submodule issue was created):

```
Post a comment on the parent issue (<parent-issue>) in the parent repo:

  Submodule provenance tracked in <sub-owner>/<sub-repo>#<submodule-issue-number>
  Tier: <1 or 2> | Operation: dev-push | Submodule: <submodule-path>

  ---

  <AI-Name> (<ModelID>)
```

- For GitHub: github_add_issue_comment(owner=GIT_OWNER, repo=GIT_REPO, issue_number=<parent-issue>, body=...)
- For GitBucket: POST /api/v3/repos/<owner>/<repo>/issues/<number>/comments

When Tier 3 is used, no parent issue comment is posted (no submodule issue exists to reference).

#### Step 10: Log Provenance Result

Every provenance attempt is logged regardless of tier:

```json
{
  "timestamp": "<ISO 8601>",
  "submodule": "<owner>/<repo>",
  "submodule_path": "<path-in-parent>",
  "operation": "dev-push",
  "tier": 1,
  "issue_number": null,
  "pr_number": null,
  "failure_reasons": []
}
```

For downgrade scenarios, `failure_reasons` accumulates the reason at each tier:

```json
{
  "timestamp": "<ISO 8601>",
  "submodule": "<owner>/<repo>",
  "submodule_path": "<path-in-parent>",
  "operation": "dev-push",
  "tier": 3,
  "issue_number": null,
  "pr_number": null,
  "failure_reasons": [
    {"tier": 1, "step": "pr-creation", "reason": "HTTP 403 Forbidden"},
    {"tier": 2, "step": "issue-creation", "reason": "Authentication failed"}
  ]
}
```

**All fallbacks are silent.** No HALT, no blocking of the git workflow. The parent repo push proceeds regardless of provenance outcome.

### Acceptance Criteria

| ID | Criterion |
| -- | -- |
| P1 | Dev-push provenance creates an issue in the submodule repo (or falls back to commit message) |
| P2 | When no API access is available, falls back to Tier 3 (commit message provenance) — silent, non-blocking |
| P3 | Issue body includes parent repo, parent branch, parent issue number, and what changed |
| P4 | Parent issue receives a comment cross-referencing the submodule provenance issue (Tier 1/2 only) |
| P12 | Automatic silent fallback — no HALT, no blocking, no developer intervention required |
| P13 | Log entry includes timestamp, submodule, operation, tier used, and optional issue/PR numbers |

### Context Parameters

When invoking provenance from review-prep, pass these parameters:

| Parameter | Source |
| -- | -- |
| parent_repo | `<GIT_OWNER>/<GIT_REPO>` from session init |
| parent_branch | Current feature branch name (BRANCH_NAME) |
| parent_issue | Issue number from the implementation spec |
| submodule_path | Path of the pushed submodule within parent repo |
| change_description | Brief description of what changed |

## promotion-provenance

### Purpose

After promoting a submodule from dev → main (release), create a provenance issue and PR (or fallback) in the submodule repository to track the release. Falls back silently through three tiers when API access is limited.

### Entry Criteria

- Submodule has been promoted (dev → main merge completed)
- Release tag has been created in the submodule
- Platform detection has completed (Step 0 above) and result is cached
- Parent repo, parent branch, parent issue number, and tag name are known

### Procedure

#### Step 11: Detect Platform and Issue System Availability

For each submodule that was promoted, call the Phase 1 detection functions:

```
1. detect_submodule_platform(submodule_remote_url) → {platform, owner, repo}
2. Check cache for <owner>/<repo>
   - If cached → use cached result
   - If not cached → test_platform_api_availability(platform, owner, repo) → {platform, access_level, reason}
3. cache_detection_result(result)
```

#### Step 12: Attempt Tier 1 — Create Issue + PR

When `access_level` is `full`:

```
1. Create issue in submodule repo:
   - Title: "Release <submodule-path> promoted from <source-branch>"
   - Body template:

     **Parent repo:** <parent-repo>
     **Parent branch:** <parent-branch>
     **Parent release:** <parent-release-issue-or-tag>
     **Submodule path:** <submodule-path>
     **Tag:** <tag-name>
     **What changed:** <description of what changed in the submodule>
     **Why:** <reason for the promotion>

     This submodule was promoted from <source-branch> to main as part of <parent-repo>/<parent-branch> release work.

     ---

     <AI-Name> (<ModelID>)

   - For GitHub: github_issue_write(method="create", owner=<sub-owner>, repo=<sub-repo>, title=..., body=...)
   - For GitBucket: POST /api/v3/repos/<owner>/<repo>/issues (per gitbucket-api skill)

2. Create PR in submodule repo (targeting submodule's main branch):
   - Title: "Release <tag>: <source-branch> → main"
   - Body:

     Fixes #<submodule-issue-number>

     **Parent repo:** <parent-repo>
     **Parent branch:** <parent-branch>

     ---

     <AI-Name> (<ModelID>)

   - For GitHub: github_create_pull_request(owner=<sub-owner>, repo=<sub-repo>, title=..., body=..., head="<source-branch>", base="main")
   - For GitBucket: POST /api/v3/repos/<owner>/<repo>/pulls (per gitbucket-api skill)

3. If PR creation succeeds:
   - Record: {timestamp, submodule, operation: "promotion", tier: 1, issue_number, pr_number}
   - Post parent issue comment cross-referencing submodule provenance (see Step 15)
   - DONE for this submodule

4. If PR creation fails:
   - Log failure reason: {tier: 1, step: "pr-creation", reason: <error message>}
   - Downgrade to Tier 2
```

#### Step 13: Attempt Tier 2 — Issue Only

When Tier 1 PR creation failed, or `access_level` is `issue-only`:

```
1. If issue was NOT already created in Tier 1 attempt:
   Create issue in submodule repo:
   - Title: "Release <submodule-path> promoted from <source-branch>"
   - Body:

     **Parent repo:** <parent-repo>
     **Parent branch:** <parent-branch>
     **Parent release:** <parent-release-issue-or-tag>
     **Submodule path:** <submodule-path>
     **Tag:** <tag-name>
     **What changed:** <description>
     **Why:** <reason>

     ⚠️ PR creation unavailable — this issue serves as the sole provenance record.

     ---

     <AI-Name> (<ModelID>)

   - For GitHub: github_issue_write(method="create", ...)
   - For GitBucket: POST /api/v3/repos/<owner>/<repo>/issues

2. If issue creation succeeds:
   - Record: {timestamp, submodule, operation: "promotion", tier: 2, issue_number, pr_number: null}
   - Post parent issue comment cross-referencing submodule provenance (see Step 15)
   - DONE for this submodule

3. If issue creation fails:
   - Log failure reason: {tier: 2, step: "issue-creation", reason: <error message>}
   - Downgrade to Tier 3
```

#### Step 14: Tier 3 — Commit Message Provenance

When Tier 2 issue creation failed, or `access_level` is `no-access`:

```
1. No API calls attempted
2. Structured commit message metadata is the provenance record:

   Release <submodule-path>: promoted from <source-branch> #[parent-issue]

   Tag: <tag-name>
   Parent: <parent-repo>#<parent-issue>
   Branch: <parent-branch>

3. Record: {timestamp, submodule, operation: "promotion", tier: 3, issue_number: null, pr_number: null}
```

**Note:** The tag commit in the submodule should already contain the structured message above. If not, the agent amends the tag message or documents the provenance in the log only — never force-pushes or rewrites submodule history.

#### Step 15: Cross-Reference Parent Issue

When Tier 1 or Tier 2 succeeds (a submodule issue was created):

```
Post a comment on the parent issue (<parent-issue>) in the parent repo:

  Submodule promotion provenance tracked in <sub-owner>/<sub-repo>#<submodule-issue-number>
  Tier: <1 or 2> | Operation: promotion | Submodule: <submodule-path> | Tag: <tag-name>

  ---

  <AI-Name> (<ModelID>)

- For GitHub: github_add_issue_comment(owner=GIT_OWNER, repo=GIT_REPO, issue_number=<parent-issue>, body=...)
- For GitBucket: POST /api/v3/repos/<owner>/<repo>/issues/<number>/comments
```

When Tier 3 is used, no parent issue comment is posted (no submodule issue exists to reference).

#### Step 16: Log Provenance Result

Every provenance attempt is logged regardless of tier:

```json
{
  "timestamp": "<ISO 8601>",
  "submodule": "<owner>/<repo>",
  "submodule_path": "<path-in-parent>",
  "operation": "promotion",
  "tier": 1,
  "issue_number": null,
  "pr_number": null,
  "tag_name": "<tag-name>",
  "failure_reasons": []
}
```

For downgrade scenarios, `failure_reasons` accumulates the reason at each tier:

```json
{
  "timestamp": "<ISO 8601>",
  "submodule": "<owner>/<repo>",
  "submodule_path": "<path-in-parent>",
  "operation": "promotion",
  "tier": 3,
  "issue_number": null,
  "pr_number": null,
  "tag_name": "<tag-name>",
  "failure_reasons": [
    {"tier": 1, "step": "pr-creation", "reason": "HTTP 403 Forbidden"},
    {"tier": 2, "step": "issue-creation", "reason": "Authentication failed"}
  ]
}
```

**All fallbacks are silent.** No HALT, no blocking of the git workflow. The parent release promotion proceeds regardless of provenance outcome.

### Acceptance Criteria

| ID | Criterion |
| -- | -- |
| P5 | Promotion provenance creates an issue (and optionally PR) in the submodule repo, or falls back through tiers |
| P6 | When PR creation fails, falls back to issue-only (Tier 2) — silent, non-blocking |
| P7 | When no API access is available, falls back to commit message (Tier 3) — silent, non-blocking |
| P8 | PR body includes `Fixes #<submodule-issue-number>` for automatic closure |
| P9 | Tag commit message includes parent provenance: `Release <path>: promoted from <branch> #[parent-issue]` |
| P12 | Automatic silent fallback — no HALT, no blocking, no developer intervention required |
| P13 | Log entry includes timestamp, submodule, operation, tier used, tag name, and optional issue/PR numbers |

### Context Parameters

When invoking provenance for promotion, pass these parameters:

| Parameter | Source |
| -- | -- |
| parent_repo | `<GIT_OWNER>/<GIT_REPO>` from session init |
| parent_branch | The branch being released (commonly `main` or `dev`) |
| parent_issue | Issue number from the release spec |
| submodule_path | Path of the promoted submodule within parent repo |
| tag_name | The semver tag created for this promotion |
| source_branch | The branch promoted (typically `dev`) |
| change_description | Brief description of what changed in the submodule |
| parent_release_ref | Parent release tag or issue reference |

### Differences from dev-push-provenance

| Aspect | dev-push-provenance | promotion-provenance |
| -- | -- | -- |
| Target branch | Submodule's `dev` branch | Submodule's `main` branch |
| Creates release tag | No | Yes (prior to provenance) |
| Issue title pattern | `Sync from <parent-repo>/<parent-branch>: <description>` | `Release <submodule-path> promoted from <source-branch>` |
| PR target | `base="dev"` | `base="main"` |
| Tag message | N/A | Includes `#[parent-issue]` reference |
| Context includes | Parent repo, branch, issue | Parent repo, branch, issue, release tag |

## cross-reference

### Purpose

After creating a submodule provenance issue (Tier 1 or Tier 2), post a cross-reference comment on the parent repo issue to document the submodule tracking location. This creates transparent bidirectional linking between parent work and submodule provenance.

### When to Apply

| Tier | Has Submodule Issue? | Parent Comment? |
| -- | -- | -- |
| Tier 1 (issue+PR) | Yes | ✅ Yes — post comment |
| Tier 2 (issue only) | Yes | ✅ Yes — post comment |
| Tier 3 (commit message) | No | ❌ No — nothing to reference |

### Procedure

#### For dev-push-provenance (after Step 8)

When Tier 1 or Tier 2 succeeds:

```
1. Post comment on parent issue (<parent-issue>) in parent repo:

   Submodule provenance tracked in <sub-owner>/<sub-repo>#<submodule-issue-number> (Tier <tier>)
   [If PR exists: Tier 1, PR #<pr-number>]

   Operation: dev-push | Submodule: <submodule-path>

   ---

   <AI-Name> (<ModelID>)

2. For GitHub: github_add_issue_comment(owner=GIT_OWNER, repo=GIT_REPO, issue_number=<parent-issue>, body=...)
3. For GitBucket: POST /api/v3/repos/<owner>/<repo>/issues/<number>/comments
```

#### For promotion-provenance (after Step 14)

When Tier 1 or Tier 2 succeeds:

```
1. Post comment on parent issue (<parent-issue>) in parent repo:

   Submodule provenance tracked in <sub-owner>/<sub-repo>#<submodule-issue-number> (Tier <tier>)
   [If PR exists: Tier 1, PR #<pr-number>]

   Operation: promotion | Submodule: <submodule-path> | Tag: <tag-name>

   ---

   <AI-Name> (<ModelID>)

2. For GitHub: github_add_issue_comment(owner=GIT_OWNER, repo=GIT_REPO, issue_number=<parent-issue>, body=...)
3. For GitBucket: POST /api/v3/repos/<owner>/<repo>/issues/<number>/comments
```

### Error Handling

Cross-reference comments are **non-blocking**:

| Error | Response |
| -- | -- |
| Permission denied on parent repo | Log warning, continue — provenance already recorded in submodule |
| API rate limited | Log warning, continue |
| Parent issue not found | Log warning, continue — parent may have been closed/deleted |
| Network error | Log warning, continue |

**Never HALT or block the git workflow for cross-reference comment failures.** The primary provenance record (issue/PR in submodule, or commit message) is the authoritative tracking. Cross-reference comments are supplementary documentation.

### Acceptance Criteria

| ID | Criterion |
| -- | -- |
| P14 | Parent issue receives cross-reference comment when Tier 1 or 2 succeeds |
| P15 | Cross-reference includes tier information for transparency |
| P16 | Cross-reference comments are non-blocking — failures logged, workflow continues |
| P17 | Tier 3 does NOT post parent comment (no submodule issue to reference) |