# Task: verify-blockers

## Purpose

Check for blocking issues or dependencies that prevent implementation.

## Entry Criteria

- Authorization verified
- Sub-issues verified
- Codebase verified

## Exit Criteria

- No `needs-approval` label present (or explicit authorization received)
- No blocking issues superseding spec
- No unresolved dependencies

## Procedure

### Step 1: Check needs-approval Label

```python
issue = github_issue_read(method="get", issue_number=N)
has_label = "needs-approval" in [l["name"] for l in issue["labels"]]

if has_label and explicit_authorization:
    # Label is informational, proceed
elif has_label and not explicit_authorization:
    HALT("needs-approval label present, awaiting authorization")
```

### Step 2: Check for Superseding Issues

```python
# Query for issues that may supersede current spec
issues = github_list_issues(owner=<github.owner>, repo=<github.repo>, state="open")
for issue in issues:
    if issue_supersedes_current(issue, current_spec):
        HALT("Superseding issue: #{}".format(issue["number"]))
```

### Step 3: Check Dependencies

For each dependency listed in spec:
- Verify availability
- Check for dependency conflicts
- Document any issues

## Blockers

| Blocker | Action |
|---------|--------|
| needs-approval label (no auth) | HALT and wait |
| Superseding issue | HALT and report |
| Conflicting spec | HALT and identify conflict |
| Missing dependency | HALT and ask about alternatives |

## Adversarial Verification: Blocker State

**Before trusting any blocker claim (issue exists, issue is open, issue is blocking), verify against actual GitHub API state.** Do NOT rely on cached issue state, comment claims, or assumed blocker relationships.

### Verify Blocker Issues Exist and Are Actually Blocking

```
For each identified blocker issue:
  blocker = github_issue_read(method="get", issue_number=blocker_number)
  
  - Verify issue exists (404 → MISSING-TRACEABILITY: blocker reference is stale)
  - Verify issue state matches claimed state:
    - If claimed "open" but actually "closed" → VERIFICATION-GAP (blocker resolved)
    - If claimed "closed" but actually "open" → CONFLICTING (blocker still active)
  - Verify issue is genuinely blocking:
    - If blocker has a merged PR that resolves it → blocker is resolved
    - If blocker title/content doesn't relate to current issue → VERIFICATION-GAP
```

**Evidence artifact:** `github_issue_read(method=get)` for each blocker showing actual state, title, and labels.

### Verify Superseding Issues Against Actual State

```
For each potential superseding issue:
  issue = github_issue_read(method="get", issue_number=N)
  comments = github_issue_read(method="get_comments", issue_number=N)
  
  - Verify issue is still open and active (closed → not superseding)
  - Verify issue scope actually covers current spec (read body, compare scope)
  - Do NOT trust "supercedes" label or claim without body verification
  - If claimed superseding but scope is narrower than current spec → CONFLICTING
```

**Evidence artifact:** Issue body comparison between claimed superseder and current spec.

### Verify Dependency Availability

```
For each dependency listed in spec:
  - If dependency is a package/library → verify with srclight or import check
  - If dependency is another issue → verify via github_issue_read(method=get)
    - Is it open? Closed? Does it have a merged PR?
  - If dependency is a code symbol → verify with srclight_get_signature
    - Does the symbol exist? Is it in the expected module?
```

**Evidence artifact:** Tool call results confirming dependency existence and availability.

### Verify needs-approval Label Against Actual Auth State

```
issue = github_issue_read(method="get", issue_number=N)
comments = github_issue_read(method="get_comments", issue_number=N)

has_label = "needs-approval" in [l["name"] for l in issue["labels"]]
has_auth = any comment from developer (MEMBER/OWNER/COLLABORATOR) saying "approved"/"go"

- has_label AND has_auth → STRUCTURE-VIOLATION (auto-fix: label is stale, remove it)
- no label AND no auth → VERIFICATION-GAP (may need label added)
- has_label AND no auth → Correct state, proceed to HALT
- no label AND has_auth → Correct state, proceed with implementation
```

**Evidence artifact:** Label list and comment search results showing actual auth state.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Blocker issue 404 | MISSING-TRACEABILITY | flag-for-review | Developer must resolve stale reference |
| Blocker claimed open but actually closed | VERIFICATION-GAP | auto-fix | Remove blocker, proceed |
| Blocker claimed closed but actually open | CONFLICTING | flag-for-review | Developer must confirm blocker status |
| Superseding issue scope narrower than claimed | CONFLICTING | flag-for-review | Developer must judge supersession |
| Dependency symbol/file does not exist | VERIFICATION-GAP | flag-for-review | Developer must confirm: planned or typo |
| needs-approval label stale | STRUCTURE-VIOLATION | auto-fix | Remove label (explicit auth overrides) |

## Context Required

- Related tasks: `verify-authorization`, `verify-open-questions`
- Label state machine: `141-planning-status-tracking.md §10` (remove `needs-approval` on explicit auth, add `needs-revision` on revision required)