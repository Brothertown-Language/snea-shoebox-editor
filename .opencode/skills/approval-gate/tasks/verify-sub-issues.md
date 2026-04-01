# Task: verify-sub-issues

## Purpose

Verify sub-issue structure and STATUS gate for multi-task specs before implementation.

## Entry Criteria

- Spec exists as GitHub Issue
- Authorization received for specific subtask (e.g., "approved: 1.2")
- Subtask number provided or extracted from authorization

## Exit Criteria

- Sub-issues verified present (multi-task) OR exemption confirmed (single-task)
- STATUS in parent matches requested subtask number
- Auto-create performed if needed

## Procedure

### Step 1: Check for Sub-issues

```python
sub_issues = github_issue_read(method="get_sub_issues", issue_number=parent_issue)
```

### Step 2: Determine Spec Type

**Single-task spec (EXEMPT from sub-issues):**
- Exactly ONE implementation task
- No decomposition into phases needed
- Can be implemented as atomic unit

**Multi-task spec (REQUIRES sub-issues):**
- Multiple phases (Phase 1, Phase 2, ...)
- Multiple implementation tasks
- Requires sequential work streams

### Step 3: Verify STATUS Gate (CRITICAL)

**For multi-task specs with sub-issues:**

1. Extract subtask number from authorization:
   - "approved: 1.2" → subtask 1.2
   - "approved: X.Y" → subtask X.Y
   - "approved" (no number) → check STATUS for current phase

2. Get parent issue STATUS:
   ```python
   parent = github_issue_read(method="get", issue_number=parent_issue)
   # Parse STATUS from body
   # STATUS format: "STATUS: X.Y" or "STATUS: completed"
   ```

3. Verify STATUS matches requested subtask:
   - If authorized for X.Y and STATUS is X.Y → PROCEED
   - If authorized for X.Y and STATUS is different → HALT
   - Report mismatch: "STATUS mismatch: authorized for 1.2 but STATUS is 2.1"

4. **Why STATUS Gate Matters:**
   - Prevents parallel execution of subtasks
   - Ensures sequential workflow
   - Avoids git branch conflicts
   - Prevents file edit races

### Step 4: Auto-Create Sub-issues if Needed

If empty AND multi-task:

```python
# For each PHASE in spec:
issue = github_issue_write(
    method="create",
    title=f"[Task: #{parent}] {phase_description}",
    body=f"Parent: #{parent}\nSubtask: {phase_number}\n\n## Purpose\n\n{phase_objective}\n\n## Procedure\n\n{phase_steps}",
    labels=["enhancement", "architecture"]
)
github_sub_issue_write(
    method="add",
    issue_number=parent,
    sub_issue_id=issue["id"]
)
```

### Step 5: Post Comment

"Created N sub-issues for phase tracking."

## STATUS Gate Rules

| Scenario | Action |
|----------|--------|
| STATUS matches authorized subtask | ✅ PROCEED |
| STATUS mismatch | ⛔ HALT - report mismatch |
| STATUS is "completed" | ⛔ HALT - spec already complete |
| Single-task spec (no STATUS) | ✅ PROCEED - no gate needed |

## Forbidden Actions

- Implementing phase without verified sub-issue structure
- Proceeding when `get_sub_issues` returns empty for multi-task specs
- Creating step-level sub-issues (use PHASE level)
- Assuming markdown checkboxes = task tracking
- Implementing when STATUS doesn't match authorized subtask
- Parallel execution of subtasks (enforce single-subtask flow)

## Common Issues

| Issue | Resolution |
|-------|------------|
| STATUS mismatch | Report to user, wait for STATUS update |
| STATUS not found | Assume no STATUS gate (proceed with caution) |
| Sub-issue not linked | Auto-create and link |
| Single-task spec with STATUS | Ignore STATUS, proceed |

## Context Required

- Guidelines: `120-github-issue-first.md`, `github-sub-issues` skill
- Guidelines: `.opencode/skills/templates/PARENT-ISSUE-TEMPLATE.md`
- Guidelines: `.opencode/skills/templates/SUB-ISSUE-TEMPLATE.md`
- Related tasks: `verify-authorization`, `verify-codebase`