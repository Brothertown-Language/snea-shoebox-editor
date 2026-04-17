# Task: verify-fix-spec

## Purpose

Verify that a bug report has a fix spec sub-issue before it can be considered complete. This enforces the critical rule that bugs must have fix specs before closure.

## Entry Criteria

- Issue has been identified as a bug report (via triage or `bug` label)
- Issue data gathered (body, comments, sub-issues)

## Exit Criteria

- Fix spec sub-issue existence verified OR missing fix spec reported
- If missing, `analyze-and-spec` task recommended

## Procedure

### Step 1: Determine if Issue Is a Bug Report

Check for bug indicators:

| Indicator | Present? |
|-----------|----------|
| `bug` label on issue | Check labels |
| Bug language in body ("crash", "error", "broken", "steps to reproduce") | Analyze content |
| Title contains bug keywords | Analyze title |

If NOT a bug report, this check does not apply. Report "N/A — not a bug report" and EXIT.

### Step 2: Check for Fix Spec Sub-Issues

```
github_issue_read(method="get_sub_issues", issue_number=N)
```

Examine sub-issues for:

| Signal | Indicates Fix Spec? |
|--------|---------------------|
| Sub-issue title starts with `[SPEC] Fix:` | Yes — fix spec exists |
| Sub-issue has `spec` label | Likely — verify content |
| Sub-issue has `needs-approval` label | Likely — pending fix spec |
| No sub-issues match above | No — fix spec missing |

### Step 3: Report Findings

**If fix spec exists:**
- Report the fix spec issue number
- Note its authorization status (has `needs-approval` or has been approved)
- Continue with normal workflow

**If fix spec is missing:**
- Report "fix spec sub-issue NOT found for bug report"
- Recommend invoking `issue-review --issue N --task analyze-and-spec`
- This is a **blocking condition** for bug report closure per `000-critical-rules.md`

## Edge Cases

| Case | Handling |
|------|----------|
| Bug report is already closed | **Do NOT skip — verify closure is legitimate via merged PR.** See "Closed Bug Report Verification" below |
| Bug report has multiple fix spec sub-issues | Report all; this is valid for multiple root causes |
| Sub-issue exists but is not a fix spec | Ignore for this check; still need a proper fix spec |
| Issue was misclassified as bug | Skip this check; not applicable |

### Closed Bug Report Verification

**🚫 CRITICAL: A closed bug report does NOT mean the fix is already resolved.** Before skipping verification for a closed bug report, verify that the closure is legitimate:

```
if bug_report.state == "closed":
    # Do NOT assume closed = resolved. Verify closure reason.

    # Step 1: Check closure reason
    state_reason = bug_report.get("state_reason", "")

    if state_reason == "not_planned":
        # Bug was intentionally not fixed — may still need a fix spec
        # Do NOT skip; the bug may need to be reopened or a new fix spec created
        REPORT: "Bug closed as not_planned — fix spec still needed if bug is valid"
        PROCEED to Step 2 (fix spec verification)

    elif state_reason == "completed":
        # Verify a merged PR exists that fixes this bug
        prs = github_search_pull_requests(query=f"Fixes #{bug_issue_number} repo:{<GitOwner>}/{<GitRepo>}")
        merged_pr_found = False
        for pr in prs:
            pr_detail = github_pull_request_read(method="get", owner=<GitOwner>, repo=<GitRepo>, pullNumber=pr["number"])
            if pr_detail.get("merged_at") is not None:
                merged_pr_found = True
                break

        if merged_pr_found:
            # Bug was closed via merged PR — legitimate closure
            # Still check for fix spec sub-issue (it may exist from before the fix)
            PROCEED to Step 2 (fix spec verification)
        else:
            # Closed as "completed" but no merged PR — suspicious closure
            REPORT: "Bug closed as completed but no merged PR found — verification gap"
            PROCEED to Step 2 (fix spec may still be needed)

    else:
        # State reason unclear
        REPORT: "Bug closed without clear reason — verification gap"
        PROCEED to Step 2 (fix spec verification)
```

## Cross-References

- `issue-review --task analyze-and-spec`: Creates fix spec for bug reports
- `000-critical-rules.md`: Bug reports must have fix spec before closure
- `065-verification-honesty.md`: Verification claims must be backed by tool call evidence
- `spec-auditor --task ground-truth`: Adversarial verification model for metadata claims

## Ground-Truth Verification

**Before trusting any fix spec claim, verify it against actual GitHub state.** Do NOT rely on cached sub-issue lists, assumed labels, or claimed STATUS values.

### Verify Fix Spec Exists (Not Just Claimed)

```
sub_issues = github_issue_read(method="get_sub_issues", issue_number=N)

For each sub-issue returned:
  - Verify it actually exists by reading it:
    child = github_issue_read(method="get", issue_number=sub_issue_number)
  - Verify it is a fix spec (not a related but non-fix issue):
    - Title starts with "[SPEC] Fix:" OR
    - Has "spec" label OR
    - Body contains fix spec content
  - If sub_issue_number returns 404 → MISSING-TRACEABILITY (flag-for-review)
```

**Evidence artifact:** `github_issue_read(method=get_sub_issues)` and `github_issue_read(method=get)` for each sub-issue.

### Verify Fix Spec Labels and STATUS Match Maturity

```
For each verified fix spec sub-issue:
  labels = github_issue_read(method=get_labels, issue_number=sub_issue_number)
  body = github_issue_read(method=get, issue_number=sub_issue_number)
  
  - If has "needs-approval" label but content is DETAILED or COMPLETE → STRUCTURE-VIOLATION
    (auto-fix: note label is stale, recommend removal after auth)
  - If STATUS says BRAINSTORM/DRAFT but content is DETAILED/COMPLETE → STRUCTURE-VIOLATION
    (auto-fix: update STATUS marker per ground-truth maturity classification)
  - If STATUS says COMPLETE but content is BRAINSTORM/DRAFT → CONFLICTING
    (flag-for-review: may indicate tracking intent, developer must judge)
```

**Evidence artifact:** Label list and body content for each fix spec sub-issue.

### Verify Fix Spec Is Not Closed Prematurely

```
For each fix spec sub-issue:
  child = github_issue_read(method=get, issue_number=sub_issue_number)
  
  - If child state is "closed" → verify a merged PR exists
  - Search for PRs referencing the sub-issue number
  - If closed with no merged PR → VERIFICATION-GAP (flag-for-review: premature closure)
```

**Evidence artifact:** Issue state response and PR search results.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Fix spec sub-issue 404 | MISSING-TRACEABILITY | flag-for-review | Developer must resolve missing issue |
| Fix spec labels stale | STRUCTURE-VIOLATION | auto-fix | Note stale label, recommend removal |
| STATUS mismatch (conservative) | STRUCTURE-VIOLATION | auto-fix | Update STATUS to match content |
| STATUS mismatch (overstated) | CONFLICTING | flag-for-review | Developer must judge intent |
| Premature closure | VERIFICATION-GAP | flag-for-review | Report — no merged PR found |