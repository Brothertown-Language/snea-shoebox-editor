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

### Step 3: Extract Phase Prose from Plan Body

Read the full plan issue body and locate the section for the target phase. Extract all prose that a sub-agent needs to implement this phase independently — without re-reading the plan. This includes:

- **Why this phase exists**: The concern it addresses and its place in the overall design
- **What it must accomplish**: Tasks, deliverables, and behavioral requirements
- **How to verify completion**: Success criteria and testable outcomes
- **What could go wrong**: Edge cases, known risks, and failure modes
- **What must be done first**: Dependencies on prior phases or external prerequisites

The agent decides how to structure this content within the sub-issue body. There is no prescribed section format, no fill-in-the-blanks template, and no required headers. The prose from the plan body should flow naturally, preserving the author's intent and context.

### Step 4: Create Sub-Issue

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

**Title format:** `[Task: #PLAN] Phase Description`

**Body requirement:** The sub-issue body MUST contain enough phase context for a sub-agent to implement the phase independently. A body that contains only `**Parent Plan:** #M` is insufficient — the phase prose extracted in Step 3 must be included.

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