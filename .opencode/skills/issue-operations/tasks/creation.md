# Task: creation

## Purpose

Create issue with proper title format, labels, and byline after validation passes. Routes to appropriate platform sub-skill.

## Operating Protocol

1. **Run after `pre-creation` validation passes.**
2. **DO NOT skip validation.**

## Entry Criteria

- Pre-creation validation passed
- Single-task vs multi-task determination complete
- User has authorized creation

## Exit Criteria

- Issue created via platform sub-skill
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

### Step 2: Create Issue (Platform Routing)

**GitHub platform:**
```python
github_issue_write(
    method="create",
    owner=owner,
    repo=repo,
    title=title,
    body=body,
    labels=["needs-approval"]
)
```

**GitBucket platform:**
```python
from skills.gitbucket_api.tools import GitBucketAPI
api = GitBucketAPI()
api.create_issue(
    owner=owner,
    repo=repo,
    title=title,
    body=body,
    labels=["needs-approval"]
)
```

**Note (GitBucket):** Labels can ONLY be set during creation. Post-creation label changes do not work.

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
2. Invoke `issue-operations --task link-sub-issue`
3. Create phase-level sub-issues
4. Link each via platform sub-skill (GitHub: `github_sub_issue_write(method="add")`; GitBucket: comment-based linking)

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

- Related tasks: `pre-creation` (runs first), `post-creation` (runs next), `link-sub-issue` (sub-issue creation)
- Platform routing: `../platforms/github-mcp/` or `../platforms/gitbucket-api/`
- Label state machine: `141-planning-status-tracking.md §10` (add `needs-approval` on creation; GitHub `labels` parameter replaces all labels)

## Live Verification: Creation Evidence (MANDATORY)

**Each creation precondition MUST be verified via tool call. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Pre-creation validation passed" | Verify validation result exists | Check pre-creation output in session | MISSING-ELEMENT |
| "No conflicting spec exists" | Search for overlapping issues | `github_search_issues(query="label:spec <keyword>")` | CONFLICTING |
| "Title follows format" | Verify title prefix | Check `[SPEC]`, `[SPEC-FIX]`, `[SPEC-ENHANCEMENT]`, `[Task:` prefix | STRUCTURE-VIOLATION |
| "Issue was created" | Verify API response | Check `number` field in creation response | MISSING-ELEMENT |
| "`needs-approval` label applied" | Verify label on created issue | `github_issue_read(method="get_labels", issue_number=N)` | MISSING-ELEMENT |
| "Byline in body" | Verify byline present | Check issue body for `🤖` marker | STRUCTURE-VIOLATION |

**Evidence artifact:** Pre-creation result, creation API response, post-creation label check.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Pre-creation not run | MISSING-ELEMENT | flag-for-review | HALT — run pre-creation first |
| Conflicting spec found | CONFLICTING | flag-for-review | HALT — report conflict |
| Wrong title format | STRUCTURE-VIOLATION | auto-fix | Correct title before creation |
| Creation API failed | MISSING-ELEMENT | flag-for-review | HALT — retry or report error |
| Label missing post-creation | MISSING-ELEMENT | auto-fix | Add label immediately |
| Byline missing | STRUCTURE-VIOLATION | auto-fix | Add byline to body |