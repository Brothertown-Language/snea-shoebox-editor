# Task: verify-authorization

## Purpose

Check for explicit authorization and needs-approval label status before implementation.

## Entry Criteria

- User says "approved", "go", or similar authorization
- Spec exists as GitHub Issue

## Exit Criteria

- Authorization verified as explicit and for correct issue
- needs-approval label status checked
- Git state verified clean (stash if needed)
- Authorization recorded for scope tracking

## Procedure

### Step 1: Verify Git State (MANDATORY FIRST)

**🚫 CRITICAL: This check MUST happen BEFORE any other work.**

```bash
git branch --show-current
git status
```

**If on `main` with ANY pending changes (modified, deleted, untracked):**

```bash
git stash push -u -m "WIP: before <branch-name>"
git stash list   # VERIFY stash created
git status       # VERIFY clean working tree
```

**Verification Requirements:**

| Check | Command | Expected Result |
|-------|---------|------------------|
| Stash created | `git stash list` | Shows stash entry |
| Working tree clean | `git status --porcelain` | Empty output |

**If EITHER check fails ⇒ STOP. Report failure. Let user resolve.**

**Then proceed:**

```bash
git checkout main && git pull origin main
git checkout -b spec/<short-name>
```

### Step 2: Verify Authorization Is Explicit

Check that authorization is:
- From user (not agent)
- Explicit ("approved", "go", "approved: N.M")
- For the CURRENT issue (not old session)

### Step 3: Check needs-approval Label

```python
# Get issue labels
issue = github_issue_read(method="get", issue_number=N)
has_label = "needs-approval" in [l["name"] for l in issue["labels"]]

if has_label and explicit_authorization:
    # Label is informational, NOT blocking
    # Proceed with implementation
    # Optionally note: "needs-approval label can be removed"
```

### Step 4: Record Authorization Scope

Authorization applies to:
- Specific issue only
- Current phase/task only
- This session only (no carryover)

## Critical: Explicit Authorization Priority

When user provides explicit authorization, it **OVERRIDES** the needs-approval label.

| Scenario | Action |
|----------|--------|
| "approved" AND label present | PROCEED - explicit auth wins |
| "approved" AND no label | PROCEED |
| NO auth AND label present | HALT - wait for authorization |
| NO auth AND no label | Check other blockers |

## Context Required

- Related tasks: `verify-sub-issues`, `verify-codebase`