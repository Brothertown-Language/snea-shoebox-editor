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

### Verify File Existence Against Live Filesystem

```
For each file mentioned in the spec:
  - Use glob or read tool to verify the file actually exists at the specified path
  - If file path includes worktree.path prefix → verify in worktree
  - If file does not exist → VERIFICATION-GAP (flag-for-review: may be planned but not created, or path may have changed)
  - If file path has changed since spec was written → MISSING-TRACEABILITY (conditional: update spec with correct path)
```

**Evidence artifact:** `glob` or `read` tool output confirming each referenced file exists or is absent.

### Verify Code References Against Live Symbols

```
For each function name, class name, or symbol mentioned in the spec:
  - Use srclight_get_signature or srclight_search_symbols to verify the symbol exists
  - If symbol does not exist → VERIFICATION-GAP (flag-for-review: planned but not implemented, or renamed)
  - If signature differs from spec claim → CONFLICTING (flag-for-review: spec may be stale)
```

**Evidence artifact:** `srclight_get_signature` or `srclight_search_symbols` results for each referenced symbol.

### Verify Superseding Issues Against Live GitHub State

```
For each potentially superseding issue:
  - Read the issue via github_issue_read(method=get, issue_number=N)
  - Verify it is still open (not closed without implementation)
  - Verify its body actually covers the current spec's scope
  - If superseding issue is closed as not_planned → NOT superseding (current spec is still valid)
  - If superseding issue scope is narrower than current spec → NOT superseding (partial overlap only)
```

**Evidence artifact:** `github_issue_read` responses for each candidate superseding issue.

### Verify Staleness Claims Against Recent Changes

```
If spec claims "no changes since spec written":
  - Use srclight_recent_changes to check if referenced files have been modified since spec creation date
  - Use git log --since="<spec-date>" -- <file-paths> to verify no modifications occurred
  - If files changed since spec → VERIFICATION-GAP (re-verify code validity)
```

**Evidence artifact:** Recent changes output or git log results confirming whether referenced files are unchanged.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Referenced file does not exist | VERIFICATION-GAP | flag-for-review | Developer must confirm: planned or typo |
| File path changed since spec | MISSING-TRACEABILITY | conditional | Update spec with correct path |
| Referenced symbol does not exist | VERIFICATION-GAP | flag-for-review | Developer must confirm: planned or renamed |
| Symbol signature differs from spec | CONFLICTING | flag-for-review | Spec may be stale; developer must judge |
| Superseding issue closed as not_planned | VERIFICATION-GAP | auto-fix | Remove superseded flag, proceed |
| Files changed since spec creation | VERIFICATION-GAP | conditional | Re-verify all code references |

## Context Required

- Related tasks: `verify-authorization`, `verify-blockers`
- `065-verification-honesty.md`: Verification claims must be backed by tool call evidence
- `spec-auditor --task ground-truth`: Adversarial verification model for metadata claims