# Task: verify-merge

## Purpose

Verify that a PR has actually been merged before closing associated issues. Prevents closing issues for unmerged or rejected PRs.

## Entry Criteria

- PR number identified
- Need to verify merge status before issue closure

## Exit Criteria

- Merge status confirmed or denied
- PR data available for closure decision

## Procedure

### Step 1: Get PR Status (Platform Routing)

**GitHub platform:**
```python
pr = github_pull_request_read(
    method="get",
    owner=GIT_OWNER,
    repo=GIT_REPO,
    pullNumber=N
)
merged = pr.get("merged", False)
state = pr.get("state", "unknown")
```

**GitBucket platform:**
```python
from skills.gitbucket_api.tools import GitBucketAPI
api = GitBucketAPI()
pr = api.get_pull_request(owner=GIT_OWNER, repo=GIT_REPO, pull_number=N)
merged = pr.get("merged", False)
state = pr.get("state", "unknown")
```

### Step 2: Verify Merge

| PR State | Merged | Action |
|----------|--------|--------|
| `closed` | `true` | ✅ Proceed with issue closure |
| `closed` | `false` | ❌ PR was closed without merge — do NOT close issue |
| `open` | `false` | ❌ PR still open — do NOT close issue |

### Step 3: Search Fallback (GitBucket)

When searching for a PR that fixes a specific issue on GitBucket (no search API):

1. List PRs with `direction=desc&sort=created&per_page=30`
2. Scan each PR body for reference pattern (`Fixes #N`, `#N`)
3. Stop on first match
4. Paginate only if no match found on first page

```python
from skills.gitbucket_api.tools import GitBucketAPI
api = GitBucketAPI()
prs = api.list_pull_requests(owner=GIT_OWNER, repo=GIT_REPO, state="closed")
matching_pr = None
for pr in prs:
    if f"#{issue_number}" in pr.get("body", "") or f"Fixes #{issue_number}" in pr.get("body", ""):
        matching_pr = pr
        break
```

## Common Issues

| Issue | Resolution |
|-------|------------|
| PR not found | Use search fallback (iterative listing) |
| PR closed without merge | Do NOT close issue — report status |
| GitBucket lacks search API | Use iterative listing with client-side filtering |
| PR state ambiguous | Check both `state` and `merged` fields |

## Context Required

- Session values: GIT_OWNER, GIT_REPO, GIT_PLATFORM
- Related tasks: `close` (uses merge verification before closing)