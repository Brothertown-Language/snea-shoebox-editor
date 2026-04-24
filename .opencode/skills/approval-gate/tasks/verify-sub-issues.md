# Task: verify-sub-issues

> **Note:** Sub-issue verification is consolidated into `verify-authorization` Step 5 as the single authoritative readiness check. This task remains available for standalone invocation when detailed sub-issue inspection is needed, but the pre-implementation gate is `verify-authorization` Step 5.

## Purpose

Verify sub-issue structure and STATUS gate for multi-task plans before implementation. Sub-issues are verified under the plan issue, not the spec issue.

## Entry Criteria

- Plan exists as GitHub Issue (with `plan` label or `[PLAN]` prefix)
- Authorization received for specific subtask (e.g., "approved: 1.2")
- Subtask number provided or extracted from authorization
- Authorization received for plan (covers sub-issue creation)

## Exit Criteria

- Sub-issues verified present under plan (multi-task) OR exemption confirmed (work-of-1)
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

1. Extract subtask from authorization:
    - "approved: 1.2" → subtask 1.2 (numeric format, backward-compatible)
    - "approved: X.Y" → subtask X.Y (numeric format, backward-compatible)
    - "approved: {concern}" → find phase matching concern name (prose format)
    - "approved" (no number) → check STATUS for current phase

2. Get plan issue STATUS:
    ```python
    plan = github_issue_read(method="get", issue_number=plan_issue)
    # Parse STATUS from body
    # Prose-driven formats (recommended):
    #   "STATUS: in progress — {concern}, Step {N}"
    #   "STATUS: completed — {concern}"
    #   "STATUS: {concern} — {task description}"
    #   "STATUS: in progress — {concern} (REVISED - NEEDS APPROVAL)"
    # Numeric formats (backward-compatible):
    #   "STATUS: X.Y" or "STATUS: completed"
    # If STATUS not found, default to first concern's first step
    ```

3. Determine which subtask to implement:
    - If authorized for concern name or X.Y → use that subtask (explicit override)
    - If "approved" (no number) AND STATUS found → use STATUS value
    - If "approved" (no number) AND STATUS missing → use first concern, first step
    - POST COMMENT explaining which subtask is being implemented

4. Verify subtask exists:
   - If subtask X.Y or concern name exists in sub-issues → PROCEED
   - If subtask X.Y or concern name NOT in sub-issues → HALT and report: "Subtask not found. Available subtasks: [list]"

5. Report to user (MANDATORY - no silent halts):
```markdown
Proceeding to implement subtask for {concern} (or X.Y).

Authorization: "approved" (no phase specified)
STATUS: {concern}, Step {N} (or "not found, defaulting to first concern")
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

**⚠️ Body-Preservation Safeguard:** This task only creates new issues (`method="create"`) and does not modify existing issue bodies. If any task in this skill were to use `github_issue_write(method=update, body=...)`, it MUST verify that the new body preserves all original content (len(new_body) >= 0.8 * len(original_body)). See `000-critical-rules.md` → "Critical Violation: Issue Body Erasure" for the project-wide rule.

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
| STATUS matches authorized subtask (prose or numeric) | ✅ PROCEED - report which subtask and concern |
| STATUS mismatch | ⛔ HALT - report mismatch clearly |
| STATUS is "completed" | ⛔ HALT - spec already complete |
| STATUS not found + "approved" | ✅ PROCEED - default to first concern's first step, report decision |
| STATUS not found + "approved: X.Y" | ✅ PROCEED - use specified X.Y, report decision |
| STATUS not found + "approved: {concern}" | ✅ PROCEED - find phase matching concern name, report decision |
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
- STATUS field: Not found → Defaulting to first concern's first step
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
| STATUS mismatch | POST report: "STATUS mismatch: authorized for {concern}/{X.Y} but STATUS is {actual}. Please update STATUS or authorize correct subtask." |
| STATUS not found | Default to first concern's first step, POST report: "STATUS not found. Defaulting to first concern. Add 'STATUS: in progress — {concern}, Step 1' to plan issue for tracking." |
| Sub-issue not linked | Auto-create and link, POST report: "Created N sub-issues for phase tracking." |
| Single-phase plan with STATUS | Ignore STATUS, proceed, POST report: "Single-phase plan, ignoring STATUS field." |
| Subtask not in list | HALT, POST report: "Subtask {X.Y}/{concern} not found. Available subtasks: [list]. Please authorize a valid subtask." |
| Plan issue missing STATUS field | Default to first concern's first step, proceed, report to chat |

## Adversarial Verification: Sub-Issue State

Adversarial verification model (evidence format, classification tiers, tier actions): see `enforcement/adversarial-verification.md`

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

### Task-Specific Findings

See `enforcement/adversarial-verification.md` for the three-tier classification model (auto-fix, conditional, flag-for-review) and evidence artifact format.

## Context Required

- Related tasks: `verify-authorization`, `verify-codebase`
- Label state machine: `141-planning-status-tracking.md §10` (label transitions when creating sub-issues under plan)

## Enforcement References

- Evidence format + finding classification: see `enforcement/adversarial-verification.md`
- Scope parsing: see `enforcement/scope-parsing.md`
- Sub-issue graph traversal: see `enforcement/sub-issue-graph-traversal.md`
