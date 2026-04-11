# Task: verify-authorization

## Purpose

Check for explicit authorization and needs-approval label status before implementation.

## Entry Criteria

- User says "approved", "go", or similar authorization
- Spec exists as GitHub Issue

## Exit Criteria

- Authorization verified as explicit and for correct issue
- needs-approval label status checked
- Git state verified (worktree environment ready)
- Authorization recorded for scope tracking

## Procedure

### Step 1: Verify Git State (MANDATORY FIRST)

**🚫 CRITICAL: This check MUST happen BEFORE any other work.**

```bash
git branch --show-current
git status
```

**If on `main` or `dev`:** This is expected — feature branches are created in worktrees, not by switching branches in the main tree. Proceed to Step 2.

**If on a feature branch already:** Verify you're in the correct worktree. Check `WORKTREE_PATH` environment variable.

**🚫 CRITICAL: Do NOT create branches directly in verify-authorization.**

Branch creation is DELEGATED to `git-workflow --task pre-work`, which creates worktrees via the `using-git-worktrees` skill. Creating branches here bypasses worktree isolation — a CRITICAL VIOLATION.

**After git state verification:**
1. Record that git state is verified
2. Proceed to Step 2 (authorization verification)
3. After ALL verification steps, invoke `git-workflow --task pre-work` for worktree creation
4. `pre-work` will handle: sync with `dev`, worktree creation, and environment variable setup

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