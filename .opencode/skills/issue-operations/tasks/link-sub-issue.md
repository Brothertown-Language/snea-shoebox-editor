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
    owner=GIT_OWNER,
    repo=GIT_REPO,
    title=f"[Task: #{M}] {phase_description}",
    body=f"**Parent Plan:** #{M}\n\n{phase_prose}",
    labels=["task"]
)
```

**GitBucket platform:**
```python
from skills.gitbucket_api.tools import GitBucketAPI
api = GitBucketAPI()
sub_issue = api.create_issue(
    owner=GIT_OWNER,
    repo=GIT_REPO,
    title=f"[Task: #{M}] {phase_description}",
    body=f"**Parent Plan:** #{M}\n\n{phase_prose}",
    labels=["task"]
)
```

### Step 5: Link Sub-Issue to Parent

**GitHub platform (formal link):**
```python
github_sub_issue_write(
    method="add",
    owner=GIT_OWNER,
    repo=GIT_REPO,
    issue_number=M,
    sub_issue_id=sub_issue["id"]
)
```

CRITICAL: Use database ID (`.id`), not issue number.

**GitBucket platform (comment-based fallback):**
```python
api.add_issue_comment(
    owner=GIT_OWNER,
    repo=GIT_REPO,
    issue_number=M,
    body=f"**Sub-issue linked:** #{sub_issue['number']} — {phase_description}"
)
```

The dispatcher records which method was used (formal link vs comment) for later closure operations.

## Single-Task Exemption

Single-task plans do NOT require sub-issues. If plan has exactly ONE implementation phase with no decomposition needed, skip sub-issue creation.

## Phase-Level vs Step-Level

Sub-issues = PHASES, not steps. Phases are approval units; steps are implementation details within phases.

Title format: `[Task: #<plan-number>] <descriptive-title>`

## Context Required

- Session values: GIT_OWNER, GIT_REPO, GIT_PLATFORM
- Related tasks: `close` (verifies sub-issue state), `track-hierarchy` (verifies structure)
- Sub-issue closure queries parent comments when comment-based linking was used