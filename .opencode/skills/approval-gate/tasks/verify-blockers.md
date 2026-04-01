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
issues = github_list_issues(owner=GIT_OWNER, repo=GIT_REPO, state="open")
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

## Context Required

- Guidelines: `010-approval-gate.md`
- Related tasks: `verify-authorization`, `verify-open-questions`