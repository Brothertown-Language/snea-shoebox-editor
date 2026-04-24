# Task: provenance/promotion-provenance

## Purpose

After promoting a submodule from dev → main (release), create provenance tracking (issue + optionally PR) in the submodule repository with three-tier fallback model.

## Entry Criteria

- Submodule has been promoted (dev → main merge completed)
- Release tag has been created in the submodule
- Platform detection completed (provenance/platform-detection)
- Parent repo, branch, issue, and tag name are known

## Exit Criteria

- Provenance tracked in submodule repo (Tier 1, 2, or 3)
- Cross-reference comment posted on parent issue (Tier 1 or 2 only)
- Operation logged with timestamp, tier, and tag name
- Release promotion continues regardless of outcome

## Procedure

### Step 11: Detect Platform

Call `provenance/platform-detection` functions if not cached:
1. `detect_submodule_platform()` → {platform, owner, repo}
2. Use cached result if available
3. `test_platform_api_availability()` → {platform, access_level, reason}
4. Cache result

### Step 12: Attempt Tier 1 — Issue + PR

When `access_level` is `full`:

**Create issue in submodule repo:**
- Title: `Release <submodule-path> promoted from <source-branch>`
- Body includes parent repo, branch, release ref, submodule path, tag, what changed, and why

**Create PR in submodule repo (targeting main branch):**
- Title: `Release <tag>: <source-branch> → main`
- Body: `Fixes #<submodule-issue-number>` + parent references

**If PR creation succeeds:**
- Record with tier: 1
- Cross-reference parent issue
- DONE

**If PR creation fails:**
- Log failure, downgrade to Tier 2

### Step 13: Attempt Tier 2 — Issue Only

When Tier 1 failed or `access_level` is `issue-only`:

**Create issue in submodule repo** (if not already created):
- Title: Same as Tier 1
- Body: Same format + `⚠️ PR creation unavailable`

**If issue creation succeeds:**
- Record with tier: 2
- Cross-reference parent issue
- DONE

**If issue creation fails:**
- Log failure, downgrade to Tier 3

### Step 14: Tier 3 — Commit Message Provenance

When Tier 2 failed or no API access:

1. No API calls attempted
2. Tag commit message serves as provenance:
   ```
   Release <submodule-path>: promoted from <source-branch> #[parent-issue]
   
   Tag: <tag-name>
   Parent: <parent-repo>#<parent-issue>
   Branch: <parent-branch>
   ```
3. Record: `{..., tier: 3, issue_number: null, pr_number: null, tag_name: ...}`

### Step 15: Cross-Reference Parent Issue

When Tier 1 or Tier 2 succeeds:

Post comment on parent issue:
```
Submodule provenance tracked in <sub-owner>/<sub-repo>#<submodule-issue-number> (Tier <tier>)
[If PR exists: PR #<pr-number>]

Operation: promotion | Submodule: <submodule-path> | Tag: <tag-name>

---
<AgentName> (<ModelId>)
```

### Step 16: Log Provenance Result

Always log regardless of tier:
```json
{
  "timestamp": "<ISO 8601>",
  "submodule": "<owner>/<repo>",
  "submodule_path": "<path-in-parent>",
  "operation": "promotion",
  "tier": 1,
  "issue_number": 123,
  "pr_number": 45,
  "tag_name": "<tag>",
  "failure_reasons": []
}
```

## Acceptance Criteria

| ID | Criterion |
| -- | -- |
| P5 | Creates provenance issue (and optionally PR) in submodule repo |
| P6 | Silent fallback to issue-only (Tier 2) when PR creation fails |
| P7 | Silent fallback to commit message (Tier 3) when no API access |
| P8 | PR body includes `Fixes #<submodule-issue-number>` |
| P9 | Tag commit message includes parent provenance |
| P12 | All fallbacks silent — no HALT, no blocking |
| P13 | Log entry includes timestamp, submodule, operation, tier |

## Differences from dev-push-provenance

| Aspect | dev-push-provenance | promotion-provenance |
| -- | -- | -- |
| Target branch | `dev` | `main` |
| Creates release tag | No | Yes (prior to provenance) |
| Issue title | `Sync from <parent>/<branch>: <description>` | `Release <path> promoted from <branch>` |
| Context | Repo, branch, issue | Repo, branch, issue, release tag |

## Context Required

- Related tasks: `provenance/platform-detection`, `provenance/dev-push-provenance`
- Related skill: `git-workflow --task release-promotion`