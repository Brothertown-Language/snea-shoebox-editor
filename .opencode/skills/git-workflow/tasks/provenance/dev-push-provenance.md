# Task: provenance/dev-push-provenance

## Purpose

After pushing a submodule to its remote dev branch, create provenance tracking (issue + optionally PR) in the submodule repository with three-tier fallback model.

## Entry Criteria

- Submodule has been pushed to remote dev
- Platform detection completed and cached (provenance/platform-detection)
- Parent repo, branch, and issue number are known

## Exit Criteria

- Provenance tracked in submodule repo (Tier 1, 2, or 3)
- Cross-reference comment posted on parent issue (Tier 1 or 2 only)
- Operation logged with timestamp and tier
- Git workflow continues regardless of outcome

## Procedure

### Step 5: Detect Platform

Call `provenance/platform-detection` functions if not cached:
1. `detect_submodule_platform(submodule_remote_url)` → {platform, owner, repo}
2. Use cached result if available
3. `test_platform_api_availability(platform, owner, repo)` → {platform, access_level, reason}
4. Cache result

### Step 6: Attempt Tier 1 — Issue + PR

When `access_level` is `full`:

**Create issue in submodule repo:**
- Title: `Sync from <parent-repo>/<parent-branch>: <change-description>`
- Body includes parent repo, branch, issue, submodule path, and what changed

**Create PR in submodule repo (targeting dev branch):**
- Title: Same as issue
- Body: `Fixes #<submodule-issue-number>` + parent references

**If PR creation succeeds:**
- Record: `{timestamp, submodule, operation: "dev-push", tier: 1, issue_number, pr_number}`
- Cross-reference parent issue
- DONE

**If PR creation fails:**
- Log failure, downgrade to Tier 2

### Step 7: Attempt Tier 2 — Issue Only

When Tier 1 failed or `access_level` is `issue-only`:

**Create issue in submodule repo** (if not already created):
- Title: Same as Tier 1
- Body: Same format + `⚠️ PR creation unavailable`

**If issue creation succeeds:**
- Record: `{timestamp, ..., tier: 2, issue_number, pr_number: null}`
- Cross-reference parent issue
- DONE

**If issue creation fails:**
- Log failure, downgrade to Tier 3

### Step 8: Tier 3 — Commit Message Provenance

When Tier 2 failed or no API access:

1. No API calls attempted
2. Structured commit message already in submodule serves as provenance:
   ```
   Sync <submodule-path> from <parent-repo>/<parent-branch>
   
   Triggered-by: <parent-repo>#<parent-issue>
   Change: <description>
   [skip-ci]
   ```
3. Record: `{timestamp, ..., tier: 3, issue_number: null, pr_number: null}`

### Step 9: Cross-Reference Parent Issue

When Tier 1 or Tier 2 succeeds:

Post comment on parent issue:
```
Submodule provenance tracked in <sub-owner>/<sub-repo>#<submodule-issue-number> (Tier <tier>)
[If PR exists: PR #<pr-number>]

Operation: dev-push | Submodule: <submodule-path>

---
<AgentName> (<ModelId>)
```

**Non-blocking:** Permission denied, rate limit, or network errors → log warning and continue.

### Step 10: Log Provenance Result

Always log regardless of tier:
```json
{
  "timestamp": "<ISO 8601>",
  "submodule": "<owner>/<repo>",
  "submodule_path": "<path-in-parent>",
  "operation": "dev-push",
  "tier": 1,
  "issue_number": 123,
  "pr_number": 45,
  "failure_reasons": []
}
```

For downgrade scenarios, `failure_reasons` accumulates reasons at each tier.

## Acceptance Criteria

| ID | Criterion |
| -- | -- |
| P1 | Creates provenance issue in submodule repo (or commit message fallback) |
| P2 | Silent fallback to Tier 3 when no API access |
| P3 | Issue body includes parent repo, branch, issue, and change description |
| P4 | Parent issue receives cross-reference comment (Tier 1/2 only) |
| P12 | All fallbacks silent — no HALT, no blocking |
| P13 | Log entry includes timestamp, submodule, operation, tier |

## Context Required

- Related tasks: `provenance/platform-detection`, `provenance/promotion-provenance`
- Related skills: `gitbucket-api`