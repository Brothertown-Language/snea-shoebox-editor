# Task: close

## Purpose

Close an issue after verifying PR merge. Handles parent/child verification and platform-specific closure.

## Entry Criteria

- PR has been merged (verified via platform API)
- Issue number identified
- Merge SHA available for verification

## Exit Criteria

- Issue closed via platform API (where supported) or closure comment posted (GitBucket PATCH fallback)
- Parent/child relationships verified before closure
- Closure comment posted if substantive

## Procedure

### Step 1: Verify PR Merge

Invoke `verify-merge` task to confirm PR is actually merged before closing any issue.

### Step 2: Verify Parent/Child Relationships

**CRITICAL: Only close the child corresponding to the merged PR. Parent stays open until ALL children are closed.**

1. If issue has sub-issues: check all sub-issues are closed before closing parent
2. If issue is a sub-issue: verify parent has no other open sub-issues before closing parent
3. Plan-bridge hierarchy: close sub-issues under the plan first, then the plan, then the spec

### Step 3: Close Issue (Platform Routing)

**GitHub platform:**
```python
github_issue_write(
    method="update",
    owner=<GitOwner>,
    repo=<GitRepo>,
    issue_number=N,
    state="closed",
    state_reason="completed"
)
```

**GitBucket platform (PATCH fallback):**
```python
# PATCH /issues/:number returns 404 on GitBucket
# Post closure comment instead
from skills.gitbucket_api.tools import GitBucketAPI
api = GitBucketAPI()
api.add_issue_comment(
    owner=<GitOwner>,
    repo=<GitRepo>,
    issue_number=N,
    body="Closing: PR merged and implementation verified."
)
```

### Step 4: Post Closure Comment (if substantive)

Only if the closure provides information stakeholders need:

```markdown
**Summary:**

<What was implemented and merged>

**Outcome:** <What changed for stakeholders>

All tasks complete from this specification.

---
🤖 <AgentName> (<ModelId>) ✅ completed
```

## Common Issues

| Issue | Resolution |
|-------|------------|
| PR not actually merged | HALT — do not close issue |
| Parent has open children | Do not close parent yet |
| GitBucket PATCH broken | Use closure comment fallback |
| Non-substantive closure | Skip comment, just close |

## Context Required

- Session values: GIT_OWNER, GIT_REPO, GIT_PLATFORM
- Related tasks: `verify-merge` (runs first), `comment` (format for closure comment)
- Parent/child closure order per `010-approval-gate.md`

## Live Verification: Closure Evidence (MANDATORY)

**Each closure precondition MUST be verified via tool call before closing. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "PR #N is merged" | Verify merge status via API | `github_pull_request_read(method="get", pullNumber=N)` → `merged` field | VERIFICATION-GAP |
| "All sub-issues are closed" | Verify each sub-issue state | `github_issue_read(method="get_sub_issues", issue_number=N)` → check each closed | VERIFICATION-GAP |
| "Issue #N has a merged PR" | Search for PR referencing issue | `github_search_pull_requests(query="fixes #N")` | MISSING-ELEMENT |
| "Platform supports PATCH close" | Probe platform capabilities | `issue-operations --task capabilities` | CONFLICTING |

**Evidence artifact:** Merge verification result, sub-issue state check results.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| PR not merged | VERIFICATION-GAP | flag-for-review | HALT — do not close issue |
| Sub-issues still open | VERIFICATION-GAP | flag-for-review | Do not close parent |
| No PR references issue | MISSING-ELEMENT | flag-for-review | HALT — cannot verify implementation |
| Platform lacks PATCH | CONFLICTING | auto-fix | Use closure comment fallback |