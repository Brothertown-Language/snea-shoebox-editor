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
issues = github_list_issues(owner=<github.owner>, repo=<github.repo>, state="open")
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

## Adversarial Verification: Codebase State Claims

**Before trusting that files exist or code is valid as claimed, verify against actual filesystem and codebase state — not spec text claims, not cached results from earlier sessions.**

### Verification Checklist

- **File existence:** Use `glob` or `read` to verify each file mentioned in the spec exists at its specified path. If missing → VERIFICATION-GAP (flag-for-review).
- **Code references:** Use `srclight_get_signature` or `srclight_search_symbols` to verify each symbol mentioned in the spec exists and signatures match. If mismatch → CONFLICTING (flag-for-review).
- **Superseding issues:** Use `github_issue_read` to verify each candidate superseding issue is still open and covers the current spec's scope. Closed as `not_planned` → NOT superseding.
- **Staleness:** Use `srclight_recent_changes` or `git log --since=<spec-date>` to verify referenced files are unchanged since spec creation. If changed → VERIFICATION-GAP (conditional: re-verify).

## Enforcement References

- Evidence format + finding classification: see `enforcement/adversarial-verification.md`
- Scope parsing: see `enforcement/scope-parsing.md`
- Closed-issue verification: see `enforcement/closed-issue-verification.md`

## Context Required

- Related tasks: `verify-authorization`, `verify-blockers`
- `065-verification-honesty.md`: Verification claims must be backed by tool call evidence
- `spec-auditor --task ground-truth`: Adversarial verification model for metadata claims
