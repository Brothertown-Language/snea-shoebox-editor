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
   # If STATUS not found, default to first subtask (1.1)
   ```

3. Determine which subtask to implement:
   - If authorized for X.Y → use X.Y (explicit override)
   - If "approved" (no number) AND STATUS found → use STATUS value
   - If "approved" (no number) AND STATUS missing → use first subtask (1.1)
   - POST COMMENT explaining which subtask is being implemented

4. Verify subtask exists:
   - If subtask X.Y exists in sub-issues → PROCEED
   - If subtask X.Y NOT in sub-issues → HALT and report: "Subtask X.Y not found. Available subtasks: [list]"

5. Report to user (MANDATORY - no silent halts):
   ```markdown
   Proceeding to implement subtask X.Y.
   
   Authorization: "approved" (no phase specified)
   STATUS: X.Y (or "not found, defaulting to first subtask")
   Sub-issue: #NNN
   
   Starting implementation now.
   ```

6. **Why STATUS Gate Matters:**
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
| STATUS matches authorized subtask | ✅ PROCEED - report which subtask |
| STATUS mismatch | ⛔ HALT - report mismatch clearly |
| STATUS is "completed" | ⛔ HALT - spec already complete |
| STATUS not found + "approved" | ✅ PROCEED - default to first subtask (1.1), report decision |
| STATUS not found + "approved: X.Y" | ✅ PROCEED - use specified X.Y, report decision |
| Single-task spec (no STATUS) | ✅ PROCEED - no gate needed |
| Subtask not in sub-issues list | ⛔ HALT - report available subtasks |

## Mandatory Reporting (No Silent Halts)

**Every STATUS gate check MUST report status to user:**

1. Which subtask is being implemented
2. Why that subtask was selected (STATUS value or default)
3. Link to the sub-issue

**Example report:**
```markdown
**STATUS Gate Verification:**
- Authorization: "approved" (no phase specified)
- STATUS field: Not found → Defaulting to first subtask (1.1)
- Sub-issue: #473
- Proceeding with implementation
```

**Never HALT silently.** Always explain what was checked and what the outcome is.

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
| STATUS mismatch | POST report: "STATUS mismatch: authorized for X.Y but STATUS is Z.W. Please update STATUS or authorize correct subtask." |
| STATUS not found | Default to first subtask (1.1), POST report: "STATUS not found. Defaulting to first subtask (1.1). Add 'STATUS: X.Y' to parent issue for tracking." |
| Sub-issue not linked | Auto-create and link, POST report: "Created N sub-issues for phase tracking." |
| Single-task spec with STATUS | Ignore STATUS, proceed, POST report: "Single-task spec, ignoring STATUS field." |
| Subtask not in list | HALT, POST report: "Subtask X.Y not found. Available subtasks: [list]. Please authorize a valid subtask." |
| Parent issue missing STATUS field | Default to first subtask (1.1), proceed, POST explanatory comment |

## Context Required

- Related tasks: `verify-authorization`, `verify-codebase`