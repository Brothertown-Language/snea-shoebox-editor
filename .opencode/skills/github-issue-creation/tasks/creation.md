# Task: creation

## Purpose

Create GitHub Issue with proper title format, labels, and byline after validation passes.

## Operating Protocol

1. **Run after `pre-creation` validation passes.**
2. **DO NOT skip validation.**

## Entry Criteria

- Pre-creation validation passed
- Single-task vs multi-task determination complete
- User has authorized creation

## Exit Criteria

- Issue created in GitHub
- `needs-approval` label applied
- Creation byline included in issue body footer
- Issue number available for sub-issue linking

## Procedure

### Step 1: Determine Title Format

| Issue Type | Title Format | Example |
|------------|--------------|---------|
| Primary spec | `[SPEC] <Feature Name>` | `[SPEC] PubMed API Rate Limiting` |
| Bug fix | `[SPEC-FIX] <Bug Description>` | `[SPEC-FIX] Token Refresh Failure` |
| Enhancement | `[SPEC-ENHANCEMENT] <Enhancement>` | `[SPEC-ENHANCEMENT] Add Rate Limiting` |
| Task | `[Task: #<parent>] <Task Description>` | `[Task: #100] Create user tables` |

### Step 2: Create Issue

```python
github_issue_write(
    method="create",
    owner=owner,
    repo=repo,
    title=title,  # Format: [SPEC] <Description>
    body=body,    # Full spec content
    labels=["needs-approval"]
)
```

**Response includes:**
- `number`: Issue number (database ID)
- `id`: Database ID for sub-issue linking
- `html_url`: Issue URL

### Step 3: Verify Byline in Issue Body

**The issue body must already include a byline footer** (added during spec drafting):

```
🤖 <AgentName> (<ModelID>) created
```

**No separate comment needed.** The byline is part of the issue body content, not a standalone comment.

### Step 4: Report Issue Created

Report: "Created issue #<number>. Next step: Invoke auditors before approval."

## Multi-Task Spec Handling

**If spec has multiple phases:**

1. After creating parent issue
2. Invoke `github-sub-issues` skill
3. Create phase-level sub-issues
4. Link each via `github_sub_issue_write(method="add")`

**Single-task exemption:**
- If spec has ONE task, skip sub-issue creation
- Apply `needs-approval` label
- Proceed to `post-creation` task

## Safety Checks

Before proceeding, verify ALL:

- Pre-creation validation passed
- Title follows proper format
- `needs-approval` label applied
- Creation byline in body footer

**If ANY check fails → HALT and report.**

## Context Required

- Related tasks: `pre-creation` (runs first), `post-creation` (runs next)
- Related skills: `github-comments` (byline format), `github-sub-issues` (sub-issue creation)
- Label state machine: `141-planning-status-tracking.md §10` (add `needs-approval` on creation; GitHub `labels` parameter replaces all labels)