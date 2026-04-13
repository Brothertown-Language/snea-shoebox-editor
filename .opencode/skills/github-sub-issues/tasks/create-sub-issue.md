# Task: create-sub-issue

## Purpose

Create a sub-issue for a parent plan issue at the phase level.

## Entry Criteria

- Plan issue number identified
- Phase name/description provided
- Plan has multiple phases (not single-task)

## Exit Criteria

- Sub-issue created with proper title format
- Sub-issue linked to plan via database ID

## Procedure

### Step 1: Verify Plan is Multi-Task

```python
plan = github_issue_read(method="get", issue_number=M)
# Check if plan has multiple phases
phases = extract_phases(plan["body"])
if len(phases) == 1:
    # Single-task exemption - no sub-issue needed
    return
```

### Step 2: Check Existing Sub-Issues

```python
sub_issues = github_issue_read(method="get_sub_issues", issue_number=M)
# If sub-issues exist for this phase, skip
```

### Step 3: Create Sub-Issue

```python
sub_issue = github_issue_write(
    method="create",
    owner=GIT_OWNER,
    repo=GIT_REPO,
    title=f"[Task: #{M}] {phase_description}",
    body=f"**Parent Plan:** #{M}\n\n{phase_content}",
    labels=["task"]
)
```

**Title format:** `[Task: #PLAN] Phase Description`

### Step 4: Link to Plan

**CRITICAL: Use database ID, not issue number.**

```python
github_sub_issue_write(
    method="add",
    owner=GIT_OWNER,
    repo=GIT_REPO,
    issue_number=M,               # Plan issue NUMBER
    sub_issue_id=sub_issue["id"]   # Sub-issue DATABASE ID
)
```

### Step 5: Confirm Creation

## Common Issues

| Issue | Resolution |
|-------|------------|
| Plan is single-task | Skip - no sub-issue needed |
| Sub-issue already exists | Skip creation |
| Database ID not found | Use response["id"] not response["number"] |
| Link fails | Verify parent issue exists |

## Context Required

- Session values: GIT_OWNER, GIT_REPO
- Parent context comes from the plan issue, not the spec
- Related tasks: `link-sub-issue`, `track-hierarchy`