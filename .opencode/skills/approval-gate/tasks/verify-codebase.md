# Task: verify-codebase

## Purpose

Re-evaluate codebase state before implementation to detect staleness or superseding issues.

## Entry Criteria

- Authorization verified
- Sub-issues verified

## Exit Criteria

- Files mentioned in spec still exist
- Referenced code is still valid
- No changes since spec written (or changes documented)

## Procedure

### Step 1: Check File Existence

For each file mentioned in spec:
- Verify file still exists at specified path
- Document any missing files

### Step 2: Check Code Validity

For each code reference:
- Verify function/class still exists
- Verify signature matches spec
- Document any changes

### Step 3: Check for Superseding Issues

```python
# Query for later issues that may supersede
issues = github_list_issues(owner=GIT_OWNER, repo=GIT_REPO, state="open")
for issue in issues:
    if "[SPEC]" in issue["title"] and issue["number"] > current_spec:
        # Check if superseding
        if issue_supersedes_current(issue, current_spec):
            HALT("Superseding issue found: #{}".format(issue["number"]))
```

### Step 4: Handle Staleness

If staleness detected:
- REVISE the spec to reflect current reality
- HALT and wait for fresh approval
- NEVER implement stale spec as-is

## Staleness Indicators

| Indicator | Action |
|-----------|--------|
| File moved/renamed | Update spec with new location |
| Function signature changed | Update spec with new signature |
| Dependency updated | Update spec with new dependency |
| Related spec implemented | Check if still needed |

## Context Required

- Guidelines: `130-authority-source.md` (code is authoritative)
- Related tasks: `verify-authorization`, `verify-blockers`