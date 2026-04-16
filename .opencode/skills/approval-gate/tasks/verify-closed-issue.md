# Task: verify-closed-issue

## Purpose

Verify that a closed issue was legitimately closed — checking that a merged PR exists and that no premature closure occurred. This task enforces the rule that "closed" does NOT mean "verified" without evidence.

## Pre-Conditions

- **Load guideline:** `.opencode/guidelines/065-verification-honesty.md` before proceeding — verification claims must be backed by actual tool calls, not memory

## Entry Criteria

- An issue's closed state needs verification (before skipping, autoclosing parent, or classifying as "already implemented")
- The issue number is known

## Exit Criteria

- Closed state is verified as legitimate (merged PR exists) OR
- Closed state is flagged as a VERIFICATION-GAP (no merged PR evidence) with clear reason

## Procedure

### Step 1: Retrieve Issue State

```python
issue = github_issue_read(method="get", issue_number=N)

if issue["state"] != "closed":
    # Issue is still open — closed verification does not apply
    REPORT: "Issue #N is open, not closed. No closed-state verification needed."
    EXIT with result: NOT_CLOSED
```

**Evidence artifact:** `github_issue_read(method=get)` response showing `state: "closed"`.

### Step 2: Determine Closure Reason

```python
state_reason = issue.get("state_reason", "")
```

| `state_reason` | Interpretation | Next Step |
|----------------|---------------|-----------|
| `"completed"` | Issue was marked as done | Step 3 (verify merged PR) |
| `"not_planned"` | Issue was intentionally not implemented | Step 4 (handle not_planned) |
| `"duplicate"` | Issue was closed as a duplicate | Step 5 (verify duplicate target) |
| `None` or empty | No reason recorded | Step 3 (assume completed, verify) |

### Step 3: Verify Merged PR Exists (for "completed" or unknown reason)

**🚫 CRITICAL: A closed issue with `state_reason: "completed"` does NOT guarantee implementation.** Verify via GitHub API.

```python
# Search for PRs that reference this issue
prs = github_search_pull_requests(
    query=f"Fixes #{N} repo:{GIT_OWNER}/{GIT_REPO}"
)

merged_pr_found = False
merged_prs = []

for pr in prs:
    pr_detail = github_pull_request_read(
        method="get", owner=GIT_OWNER, repo=GIT_REPO, pullNumber=pr["number"]
    )
    if pr_detail.get("merged_at") is not None:
        merged_pr_found = True
        merged_prs.append({
            "number": pr_detail["number"],
            "merged_at": pr_detail["merged_at"],
            "merged_by": pr_detail.get("merged_by", {})
        })

if merged_pr_found:
    REPORT: f"Issue #{N} closed as completed with merged PR evidence: {', '.join(f'#{p['number']}' for p in merged_prs)}"
    EXIT with result: VERIFIED_CLOSED
else:
    # No merged PR found — suspicious closure
    REPORT: f"Issue #{N} closed as completed but NO merged PR found via 'Fixes #{N}' search"
    EXIT with result: VERIFICATION_GAP
```

**Evidence artifact:** `github_search_pull_requests` response + `github_pull_request_read` response showing `merged_at` field for each PR found.

### Step 4: Handle "not_planned" Closure

```python
# Issue was intentionally not implemented
REPORT: f"Issue #{N} closed as not_planned — work was intentionally deferred or rejected"
REPORT: "This issue may need reopening or a new fix spec if the underlying problem persists"
EXIT with result: NOT_PLANNED_CLOSURE
```

**Action for callers:**

| Caller Context | Action |
|---------------|--------|
| `verify-authorization` auto-dispatch | Do NOT autoclose; flag for review |
| `verify-already-implemented` | Do NOT classify as "already implemented" |
| `pre-implementation-analysis` screening | Do NOT exclude from implementation; may need scope reduction |
| `cleanup` pre-closure gate | Allow parent closure only if remaining scope is verified |

### Step 5: Verify Duplicate Target (for "duplicate" closure)

```python
# Extract duplicate target from issue body or comments
# GitHub typically adds "Duplicate of #M" automatically
# Also check comments for duplicate reference

body = issue.get("body", "")
comments = github_issue_read(method="get_comments", issue_number=N)

duplicate_target = None

# Search body for duplicate reference
for line in body.split("\n"):
    if "duplicate" in line.lower() and "#" in line:
        # Extract issue number reference
        import re
        match = re.search(r'#(\d+)', line)
        if match:
            duplicate_target = int(match.group(1))
            break

# Search comments for duplicate reference
if not duplicate_target:
    for comment in comments:
        if "duplicate" in comment.get("body", "").lower():
            match = re.search(r'#(\d+)', comment.get("body", ""))
            if match:
                duplicate_target = int(match.group(1))
                break

if duplicate_target:
    # Verify the duplicate target exists and is not also prematurely closed
    target = github_issue_read(method="get", issue_number=duplicate_target)
    REPORT: f"Issue #{N} closed as duplicate of #{duplicate_target} (state: {target['state']})"
    # Recursively verify the duplicate target if it's also closed
    # (Call verify-closed-issue recursively for the target, with depth limit)
    EXIT with result: DUPLICATE_OF, target=duplicate_target
else:
    REPORT: f"Issue #{N} closed as duplicate but no duplicate target found"
    EXIT with result: VERIFICATION_GAP
```

### Step 6: Check Sub-Issues (After Verifying Parent Closure)

If the issue is a parent with sub-issues, verify EACH sub-issue's closure is legitimate before closing the parent:

```python
sub_issues = github_issue_read(method="get_sub_issues", issue_number=N)

if sub_issues:
    for sub_issue in sub_issues:
        # Recursively verify each sub-issue
        sub_result = verify_closed_issue(sub_issue["number"])

        if sub_result == VERIFICATION_GAP:
            REPORT: f"Sub-issue #{sub_issue['number']} closure is a verification gap"
            # Parent CANNOT be closed until sub-issue is resolved
            EXIT with result: BLOCKED_BY_SUB_ISSUE

        elif sub_result == NOT_PLANNED_CLOSURE:
            REPORT: f"Sub-issue #{sub_issue['number']} was closed as not_planned"
            # Parent MAY be closed for remaining scope only
            NOTE sub_issue["number"] as "intentionally skipped"
```

### Step 7: Cross-Reference with Success Criteria

For legitimately closed issues (VERIFIED_CLOSED), optionally verify that the success criteria in the spec were actually met:

```python
# This step is informational — it does NOT block closure
# It provides additional confidence that the closed state is accurate

body = issue.get("body", "")
# Extract success criteria from spec body (if present)
# Compare against changes in the merged PR
# Report any discrepancies as informational findings
```

**This step is optional and does NOT block the verification result.** It provides additional evidence for downstream callers.

## Verification Result Types

| Result | Meaning | Action for Callers |
|--------|---------|-------------------|
| `NOT_CLOSED` | Issue is still open | Not applicable — caller should treat as open issue |
| `VERIFIED_CLOSED` | Closed with merged PR evidence | Safe to treat as legitimately closed |
| `VERIFICATION_GAP` | Closed without merged PR evidence | Do NOT trust closed state — flag for review |
| `NOT_PLANNED_CLOSURE` | Closed as "not_planned" | Work was intentionally skipped — may need reopening |
| `DUPLICATE_OF` | Closed as duplicate of another issue | Verify target issue covers the scope |
| `BLOCKED_BY_SUB_ISSUE` | Parent cannot close because a sub-issue has a verification gap | Resolve sub-issue verification first |

## Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Closed + merged PR | VERIFIED | auto-proceed | Trust closed state |
| Closed "completed" + no merged PR | VERIFICATION-GAP | flag-for-review | Do NOT trust — investigate closure |
| Closed "not_planned" | VERIFIED | auto-proceed | Work intentionally skipped |
| Closed "duplicate" + target verified | VERIFIED | auto-proceed | Trust duplicate closure |
| Closed "duplicate" + target not found | MISSING-TRACEABILITY | flag-for-review | Cannot verify duplicate chain |
| Closed + no reason recorded | VERIFICATION-GAP | flag-for-review | Investigate closure reason |
| Parent closed + sub-issue verification gap | VERIFICATION-GAP | flag-for-review | Resolve sub-issue first |

## Integration Points

This task is invoked by:

1. **`verify-authorization` Step 5.4** — Before skipping closed issues in auto-dispatch
2. **`verify-already-implemented`** — Before autoclosing as "already implemented"
3. **`pre-implementation-analysis` Step 0** — Before excluding "already implemented" issues from batch
4. **`cleanup` pre-closure gate** — Before closing parent issues in post-merge workflow
5. **`verify-fix-spec`** — Before skipping closed bug reports

## Context Required

- Issue number to verify
- `GIT_OWNER` and `GIT_REPO` from session
- Downstream callers should handle the result type to make appropriate decisions

## Cross-References

- `000-critical-rules.md`: Closed issues skip sub-issue and cross-reference verification — critical violation
- `065-verification-honesty.md`: Verification claims must be backed by tool call evidence
- `approval-gate/tasks/verify-authorization.md` Step 5.4: Closed-issue verification gate
- `approval-gate/tasks/verify-already-implemented.md`: Pre-autoclose sub-issue verification
- `git-workflow/tasks/cleanup.md`: Pre-closure sub-issue verification gate