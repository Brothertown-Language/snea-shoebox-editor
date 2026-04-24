# Task: provenance/platform-detection

## Purpose

Detect submodule host platform from remote URL and test API availability to determine provenance tracking tier.

## Entry Criteria

- Submodule has been pushed (for dev-push) or promoted (for promotion)
- Submodule remote URL is available via `git remote get-url origin`

## Exit Criteria

- Platform detected (github / gitbucket / unknown)
- API availability tested and classified into access levels
- Detection result cached for session duration
- No HALT or blocking of git workflow on failure

## Procedure

### Step 0: Platform Detection

Parse the remote URL to identify the hosting platform:

```python
def detect_submodule_platform(remote_url):
    # Extract hostname: git@<hostname>:<owner>/<repo>.git or https://<hostname>/...
    hostname = extract_hostname(remote_url)
    
    if hostname == "github.com":
        return {"platform": "github", "owner": owner, "repo": repo}
    elif is_gitbucket_pattern(hostname):  # non-github with /owner/repo pattern
        return {"platform": "gitbucket", "owner": owner, "repo": repo}
    else:
        return {"platform": "unknown", "owner": owner, "repo": repo}
```

### Step 1: Test API Availability

**GitHub:**
```python
github_get_file_contents(owner=<owner>, repo=<repo>, path="")
# Map errors:
# HTTP 403 → access_level: "no-access"
# HTTP 404 → access_level: "no-repo"
# Auth error → access_level: "auth-failed"
```

**GitBucket:**
```python
./.opencode/tools/gitbucket-api get-repo <owner> <repo>
# Map errors similarly
```

**Unknown platform:**
```
→ {platform: "unknown", access_level: "no-access", reason: ...}
```

### Step 2: Cache Detection Result

Cache key: `<owner>/<repo>`
Cache value: `{platform, access_level, reason}`
Session-scoped — resets when session ends.

### Access Level Semantics

| Level | Meaning | Tier |
| -- | -- | -- |
| `full` | Issue + PR creation available | Tier 1 |
| `issue-only` | Issue creation works, PR fails | Tier 2 |
| `no-access` | No API access (HTTP 403) | Tier 3 |
| `auth-failed` | Authentication error | Tier 3 |
| `no-repo` | Repository not found | Tier 3 |

## Acceptance Criteria

| ID | Criterion |
| -- | -- |
| P10 | Platform detection parses URLs correctly (github.com, gitbucket, unknown) |
| P11 | Error handling maps errors to access levels correctly |
| P12 | Detection results cached for session duration |
| P13 | Three-tier classification accurate |

## Common Issues

| Issue | Resolution |
| -- | -- |
| Non-standard URL format | Best-effort parsing; classify as unknown if unrecoverable |
| API rate limited | Treat as no-access, fall back to Tier 3 |
| Submodule has no remote | Classify as unknown platform |

## Context Required

- Related tools: `github_*` MCP tools, `.opencode/tools/gitbucket-api`
- Related tasks: `provenance/dev-push-provenance`, `provenance/promotion-provenance`