# Task: link-sub-issue

## Purpose

Create and link sub-issues to parent plan issues. Uses platform sub-issue API when available, falls back to comment-based linking on platforms without sub-issue support.

## Entry Criteria

- Plan issue number identified
- Phase name/description provided
- Plan has multiple phases (not single-task)

## Exit Criteria

- Sub-issue created with proper title format
- Sub-issue linked (formal link via API or comment-based fallback)

## Procedure

### Step 1: Verify Plan is Multi-Task

```python
plan = github_issue_read(method="get", issue_number=M)
phases = extract_phases(plan["body"])
if len(phases) == 1:
    # Single-task exemption - no sub-issue needed
    return
```

### Step 2: Check Existing Sub-Issues

**GitHub platform:**
```python
sub_issues = github_issue_read(method="get_sub_issues", issue_number=M)
```

**GitBucket platform:**
Check parent issue comments for structured sub-issue list comments.

### Step 3: Extract Phase Prose from Plan Body

Read the full plan issue body and locate the section for the target phase. Extract all prose that a sub-agent needs to implement this phase independently.

### Step 4: Create Sub-Issue (Platform Routing)

**GitHub platform:**
```python
sub_issue = github_issue_write(
    method="create",
    owner=<github.owner>,
    repo=<github.repo>,
    title=f"[Task: #{M}] {phase_description}",
    body=f"**Parent Plan:** #{M}\n\n{phase_prose}",
    labels=["task"]
)
```

**GitBucket platform:**
```bash
./.opencode/tools/gitbucket-api create-issue <github.owner> <github.repo> "[Task: #<M>] <phase_description>" --body "**Parent Plan:** #<M>\n\n<phase_prose>" --labels task
```

### Step 4.5: EXTRACT URL FROM API RESPONSE

1. The sub-issue URL MUST be copied verbatim from the `github_issue_write` API response's `html_url` field.
2. Do NOT retype, reconstruct, or assemble the URL from known values (org, repo, number).
3. Paste the URL exactly as returned. If the API response is `{ "html_url": "https://github.com/Org/Repo/issues/42" }`, the output URL is `https://github.com/Org/Repo/issues/42` — character for character.
4. Verification checkpoint: Compare the pasted URL character-by-character against the `html_url` field in the API response before sending.

### Step 5: Link Sub-Issue to Parent

**GitHub platform (formal link):**
```python
github_sub_issue_write(
    method="add",
    owner=<github.owner>,
    repo=<github.repo>,
    issue_number=M,
    sub_issue_id=sub_issue["id"]
)
```

CRITICAL: Use database ID (`.id`), not issue number.

**GitBucket platform (comment-based fallback):**
```bash
./.opencode/tools/gitbucket-api add-comment <github.owner> <github.repo> <M> "**Sub-issue linked:** #<sub_issue_number> — <phase_description>"
```

The dispatcher records which method was used (formal link vs comment) for later closure operations.

## Single-Task Exemption

Single-task plans do NOT require sub-issues. If plan has exactly ONE implementation phase with no decomposition needed, skip sub-issue creation.

## Phase-Level vs Step-Level

Sub-issues = PHASES, not steps. Phases are approval units; steps are implementation details within phases.

Title format: `[Task: #<plan-number>] <descriptive-title>`

## Context Required

- Session values: github.owner, github.repo, github.platform
- Related tasks: `close` (verifies sub-issue state), `track-hierarchy` (verifies structure)
- Sub-issue closure queries parent comments when comment-based linking was used

## Live Verification: Sub-Issue Linking Evidence (MANDATORY)

**Each sub-issue operation MUST be verified via tool call. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Plan #M is multi-task" | Verify plan has multiple phases | `github_issue_read(method="get", issue_number=M)` → parse body | VERIFICATION-GAP |
| "Sub-issue created" | Verify sub-issue exists | `github_issue_read(method="get", issue_number=sub_number)` | MISSING-ELEMENT |
| "Sub-issue linked to plan" | Verify sub-issue parent | `github_issue_read(method="get_sub_issues", issue_number=M)` | STRUCTURE-VIOLATION |
| "Database ID used (not issue number)" | Verify `sub_issue_id` is numeric DB ID | Check `id` field from creation response | STRUCTURE-VIOLATION |
| "Platform supports sub-issue API" | Probe capabilities | `issue-operations --task capabilities` | CONFLICTING |

**Evidence artifact:** Creation response, sub-issue link verification result.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Plan is single-task | VERIFICATION-GAP | auto-fix | Skip sub-issue creation per exemption |
| Sub-issue creation failed | MISSING-ELEMENT | flag-for-review | HALT — retry |
| Sub-issue under wrong parent | STRUCTURE-VIOLATION | auto-fix | Re-link under plan |
| Used issue number instead of DB ID | STRUCTURE-VIOLATION | auto-fix | Re-link with correct DB ID |
| Platform lacks sub-issue API | CONFLICTING | auto-fix | Use comment-based fallback |