# Task: verify-sub-issues

## Purpose

Verify sub-issue structure and STATUS gate for multi-task plans before implementation. Sub-issues are verified under the plan issue, not the spec issue.

## Entry Criteria

- Plan exists as GitHub Issue (with `plan` label or `[PLAN]` prefix)
- Authorization received for specific subtask (e.g., "approved: 1.2")
- Subtask number provided or extracted from authorization
- Authorization received for plan (covers sub-issue creation)

## Exit Criteria

- Sub-issues verified present under plan (multi-task) OR exemption confirmed (single-task/single-phase)
- STATUS in plan matches requested subtask number
- Auto-create performed if needed

## Procedure

### Step 1: Check for Sub-issues

```python
sub_issues = github_issue_read(method="get_sub_issues", issue_number=plan_issue)
```

### Step 2: Determine Plan Type

**Single-phase plan (EXEMPT from sub-issues):**
- Exactly ONE implementation phase
- No decomposition into phases needed
- Can be implemented as atomic unit

**Multi-task plan (REQUIRES sub-issues):**
- Multiple phases (Phase 1, Phase 2, ...)
- Multiple implementation tasks
- Requires sequential work streams

### Step 3: Verify STATUS Gate (CRITICAL)

**For multi-task plans with sub-issues:**

1. Extract subtask number from authorization:
   - "approved: 1.2" → subtask 1.2
   - "approved: X.Y" → subtask X.Y
   - "approved" (no number) → check STATUS for current phase

2. Get plan issue STATUS:
   ```python
   plan = github_issue_read(method="get", issue_number=plan_issue)
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

**No separate authorization required.** Plan approval covers sub-issue creation as a setup step.

```python
# For each PHASE in plan:
issue = github_issue_write(
    method="create",
    title=f"[Task: #{plan_issue}] {phase_description}",
    body=f"Plan: #{plan_issue}\nSubtask: {phase_number}\n\n## Purpose\n\n{phase_objective}\n\n## Procedure\n\n{phase_steps}",
    labels=["enhancement", "architecture"]
)
github_sub_issue_write(
    method="add",
    issue_number=plan_issue,
    sub_issue_id=issue["id"]
)
```

Auto-creating sub-issues for an approved multi-task plan does NOT require separate authorization. The plan's authorization covers this setup step.

### Step 5: Post Comment

"Created N sub-issues for phase tracking."

## Auto-Create Authorization

**Auto-creating sub-issues for an approved multi-task plan does NOT require separate authorization.** The plan's authorization covers this setup step.

| Action | Requires Separate Auth? | Why |
|--------|------------------------|-----|
| Auto-creating sub-issues | ❌ NO | Tracking/setup action, covered by plan authorization |
| Linking sub-issues to plan | ❌ NO | Part of sub-issue creation workflow |
| Proceeding to implementation after auto-creation | ❌ NO | Plan authorization continues to implementation |

## STATUS Gate Rules

| Scenario | Action |
|----------|--------|
| STATUS matches authorized subtask | ✅ PROCEED - report which subtask |
| STATUS mismatch | ⛔ HALT - report mismatch clearly |
| STATUS is "completed" | ⛔ HALT - spec already complete |
| STATUS not found + "approved" | ✅ PROCEED - default to first subtask (1.1), report decision |
| STATUS not found + "approved: X.Y" | ✅ PROCEED - use specified X.Y, report decision |
| Single-phase plan (no STATUS) | ✅ PROCEED - no gate needed |
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
- Proceeding **to implementation** when `get_sub_issues` returns empty for multi-task specs **without creating sub-issues first**
- Creating step-level sub-issues (use PHASE level)
- Assuming markdown checkboxes = task tracking
- Implementing when STATUS doesn't match authorized subtask
- Parallel execution of subtasks (enforce single-subtask flow)

## Common Issues

| Issue | Resolution |
|-------|------------|
| STATUS mismatch | POST report: "STATUS mismatch: authorized for X.Y but STATUS is Z.W. Please update STATUS or authorize correct subtask." |
| STATUS not found | Default to first subtask (1.1), POST report: "STATUS not found. Defaulting to first subtask (1.1). Add 'STATUS: X.Y' to plan issue for tracking." |
| Sub-issue not linked | Auto-create and link, POST report: "Created N sub-issues for phase tracking." |
| Single-phase plan with STATUS | Ignore STATUS, proceed, POST report: "Single-phase plan, ignoring STATUS field." |
| Subtask not in list | HALT, POST report: "Subtask X.Y not found. Available subtasks: [list]. Please authorize a valid subtask." |
| Plan issue missing STATUS field | Default to first subtask (1.1), proceed, report to chat |

## Adversarial Verification: Sub-Issue State

**Before trusting any sub-issue claim (existence, state, labels, STATUS), verify against actual GitHub API state.** Do NOT rely on cached sub-issue lists, previously-read state, or claimed closures.

### Verify Sub-Issue Existence and State

```
sub_issues = github_issue_read(method="get_sub_issues", issue_number=plan_issue)

For each sub-issue returned:
  child = github_issue_read(method="get", issue_number=sub_issue_number)
  
  - Verify child exists (404 = deleted sub-issue → MISSING-TRACEABILITY)
  - Verify child.state matches claimed state (do NOT trust cache)
  - If child.state == "closed" → verify merged PR exists before treating as complete
    - Search for PRs referencing the sub-issue
    - If closed but no merged PR → VERIFICATION-GAP (premature closure)
  - Verify child.title matches the phase description (not reassigned to different work)
```

**Evidence artifact:** `github_issue_read(method=get)` for each sub-issue showing actual state, title, and labels.

### Verify Sub-Issue Labels and STATUS

```
For each sub-issue:
  labels = github_issue_read(method=get_labels, issue_number=sub_issue_number)
  body = github_issue_read(method=get, issue_number=sub_issue_number)
  
  - If has "needs-approval" label but parent plan has explicit authorization → STRUCTURE-VIOLATION
    (auto-fix: authorization cascades from plan, label should be removed)
  - If STATUS marker in sub-issue body is mismatched to actual content maturity → STRUCTURE-VIOLATION
    (auto-fix: update STATUS per ground-truth maturity classification)
  - If STATUS says COMPLETE but sub-issue is open → CONFLICTING
    (flag-for-review: may indicate tracking mismatch)
```

**Evidence artifact:** Label list and body content for each sub-issue.

### Verify Sub-Issue Link Integrity

```
sub_issues = github_issue_read(method="get_sub_issues", issue_number=plan_issue)
parent_check = github_issue_read(method="get_sub_issues", issue_number=sub_issue_number)

- Verify sub-issues are linked under the correct parent (plan, not spec)
- If sub-issue is linked under spec instead of plan → STRUCTURE-VIOLATION
  (auto-fix: re-link under plan, remove from spec)
```

**Evidence artifact:** Sub-issue list from plan showing correct parent-child relationships.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Sub-issue 404 | MISSING-TRACEABILITY | flag-for-review | Developer must resolve deleted sub-issue |
| Sub-issue closed without merged PR | VERIFICATION-GAP | flag-for-review | Report — may be premature closure |
| Sub-issue needs-approval stale | STRUCTURE-VIOLATION | auto-fix | Remove label (auth cascades from plan) |
| STATUS maturity mismatch | STRUCTURE-VIOLATION | auto-fix | Update STATUS to match content |
| Sub-issue linked under spec (not plan) | STRUCTURE-VIOLATION | auto-fix | Re-link under correct parent |
| Title reassigned to different work | CONFLICTING | flag-for-review | Developer must verify scope |

## Context Required

- Related tasks: `verify-authorization`, `verify-codebase`
- Label state machine: `141-planning-status-tracking.md §10` (label transitions when creating sub-issues under plan)