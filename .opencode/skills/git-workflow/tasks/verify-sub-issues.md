# Subtask: verify-sub-issues

## Purpose

Verify parent/child issue structure before closing parent issues. Invoked by `cleanup` task after PR merge.

## Invocation

**Called by:** `cleanup` task after closing child issues

**Call pattern:**
```
/task subagent_type="general" description="Verify sub-issues" prompt="Use the git-workflow skill verify-sub-issues subtask to verify all child issues are closed before closing parent issue #PARENT_ISSUE."
```

## Parameters

None. Uses issue context from calling task.

## Return Value

Returns JSON object to calling task:

```json
{
  "can_close_parent": true,
  "parent_issue": 123,
  "child_count": 3,
  "closed_children": [101, 102, 103],
  "open_children": []
}
```

**Failure return (block parent closure):**
```json
{
  "can_close_parent": false,
  "parent_issue": 123,
  "child_count": 3,
  "closed_children": [101, 102],
  "open_children": [
    {
      "number": 103,
      "title": "Phase 3: UI Components",
      "state": "open",
      "analysis": "Incomplete - no PR, no superseded link"
    }
  ],
  "action": "POST_WARNING"
}
```

## Procedure

### Step 1: Query Sub-Issues

Use GitHub MCP to get all child issues:

```python
children = github_issue_read(method="get_sub_issues", issue_number=parent_issue)
```

**If empty result:**
- Parent has no sub-issues
- Return `can_close_parent: true`
- Parent can be closed directly

**If non-empty result:**
- Proceed to Step 2 to classify each child

### Step 2: Classify Each Sub-Issue

**Categorize each child issue:**

| State | Evidence | Classification |
|-------|----------|----------------|
| `state: "closed"` + `state_reason: "completed"` | Closed as done | ✅ DONE |
| `state: "closed"` + `state_reason: "not_planned"` | Intentionally not done | ✅ DONE |
| `state: "closed"` + comment "Superseded by #N" | Replacement exists | Check #N exists → ✅ DONE |
| `state: "open"` + comment "Superseded by #N" | Replacement exists | Check #N exists → ✅ DONE |
| `state: "open"` + PR link in body ("Fixes #N") | PR may be merged | Verify PR merged → ✅ DONE |
| `state: "open"` + no PR, no superseded, no completion | Incomplete work | 🚫 BLOCK |

**For each child, determine:**
1. Current state and state_reason
2. Comments for superseded references
3. Body for PR links
4. Whether work is actually done

### Step 3: Determine Action

**If ALL children classified as DONE:**
- Return `can_close_parent: true`
- Parent can be closed with summary

**If ANY child classified as BLOCK:**
- Return `can_close_parent: false`
- Include blocking children in response
- Set `action: "POST_WARNING"`

### Step 4: Return Result

Return structured JSON with classification for each child.

## ⚠️ Edge Case: Superseded Issues

When child has "Superseded by #N" comment:

1. Parse the replacement issue number from comment
2. Query the replacement issue
3. Verify replacement exists and is open or closed-completed
4. If replacement verified → Child is DONE
5. If replacement doesn't exist → Child is INCOMPLETE (block)

```python
# Extract issue number from "Superseded by #123" pattern
import re
match = re.search(r'Superseded by #(\d+)', comment)
if match:
    replacement_number = int(match.group(1))
    replacement = github_issue_read(method="get", issue_number=replacement_number)
    if replacement and replacement["state"] in ["open", "closed"]:
        # Verify replacement actually tracks the work
        return "DONE"
    else:
        # Replacement doesn't exist - child is incomplete
        return "INCOMPLETE"
```

## ⚠️ Edge Case: PR Links in Body

When child body contains "Fixes #N" or "Closes #N":

1. Extract PR number from body
2. Query PR status via GitHub API
3. If `merged_at` exists → Work is done
4. If PR closed without merge → Work may not be done

```python
# Extract PR number from "Fixes #123" pattern
match = re.search(r'Fixes #(\d+)', body)
if match:
    pr_number = int(match.group(1))
    pr = github_pull_request_read(method="get", pullNumber=pr_number)
    if pr.get("merged_at"):
        # PR was merged, work is done
        return "DONE"
    else:
        # PR not merged, needs investigation
        return "BLOCK"
```

## Safety Checks Before Closing Parent

Before returning `can_close_parent: true`, verify ALL:

- [ ] All children queried via `github_issue_read(method="get_sub_issues")`
- [ ] Each child classified correctly (DONE or BLOCK)
- [ ] No children left in BLOCK category
- [ ] Superseded references verified
- [ ] PR links verified

## Warning Comment Template

If parent cannot be closed, return structured data for warning comment:

```json
{
  "comment": "🤖 ⚠️ **Cannot Close Parent — Open Sub-Issues Detected**\n\nThis parent issue cannot be closed because the following sub-issue(s) remain incomplete:\n\n- #103: Phase 3: UI Components — Incomplete - no PR, no superseded link\n\n**Status Analysis:**\n- #103 is open with no work completed and no replacement issue.\n\n**To close this parent:**\n1. Complete the remaining sub-issue(s)\n2. Close each sub-issue when work is complete\n3. Or close as \"not planned\" with explanation if intentionally skipped\n\n---\n🤖 ⚠️ Blocking by <AgentName> (<ModelID>)"
}
```

Calling task posts this comment to parent issue.

## Context Required

- Guidelines: `124-github-archive-workflow.md` → "Parent Closure Pre-Check" section
- GitHub MCP: `github_issue_read` method="get_sub_issues"

## Integration Notes

- Called by `cleanup` task AFTER closing child issues addressed by PR
- Returns structured data (no side effects)
- Calling task posts warning comment if needed
- Calling task closes parent after verification