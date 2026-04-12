# Task: create-sub-issue

## Purpose

Create a sub-issue for a parent spec issue at the phase level.

## Entry Criteria

- Parent issue number identified
- Phase name/description provided
- Spec has multiple phases (not single-task)

## Exit Criteria

- Sub-issue created with proper title format
- Sub-issue linked to parent via database ID

## Procedure

### Step 1: Verify Parent is Multi-Task

```python
parent = github_issue_read(method="get", issue_number=N)
# Check if spec has multiple phases
phases = extract_phases(parent["body"])
if len(phases) == 1:
    # Single-task exemption - no sub-issue needed
    return
```

### Step 2: Check Existing Sub-Issues

```python
sub_issues = github_issue_read(method="get_sub_issues", issue_number=N)
# If sub-issues exist for this phase, skip
```

### Step 3: Create Sub-Issue

```python
sub_issue = github_issue_write(
    method="create",
    owner=GIT_OWNER,
    repo=GIT_REPO,
    title=f"[Task: #{N}] {phase_description}",
    body=f"**Parent Issue:** #{N}\n\n{phase_content}",
    labels=["task"]
)
```

**Title format:** `[Task: #PARENT] Phase Description`

### Step 4: Link to Parent

**CRITICAL: Use database ID, not issue number.**

```python
github_sub_issue_write(
    method="add",
    owner=GIT_OWNER,
    repo=GIT_REPO,
    issue_number=N,           # Parent issue NUMBER
    sub_issue_id=sub_issue["id"]  # Sub-issue DATABASE ID
)
```

### Step 5: Confirm Creation

## Common Issues

| Issue | Resolution |
|-------|------------|
| Parent is single-task | Skip - no sub-issue needed |
| Sub-issue already exists | Skip creation |
| Database ID not found | Use response["id"] not response["number"] |
| Link fails | Verify parent issue exists |

## Context Required

- Session values: GIT_OWNER, GIT_REPO
- Related tasks: `link-sub-issue`, `track-hierarchy`