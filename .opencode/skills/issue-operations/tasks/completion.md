# Task: completion

Idempotent completion subtask for issue-operations. Ensures mandatory steps run regardless of where the workflow halted.

## State Check Phase

1. **Issue created:** Check if the issue already exists
   - Search by title or check recent issue list (via platform sub-skill)
2. **Labels applied:** Check if `needs-approval` label is present
3. **Sub-issues created:** Check if multi-task spec has sub-issues (via platform sub-skill `get_sub_issues` or comment-based tracking)
4. **Auditor invoked:** Check if spec-auditor has been run on the issue (via session records or `./tmp/` files)

## Skill-Specific Completion

1. **Apply `needs-approval` label** (if not already present):
    ```python
    labels = github_issue_read(method="get_labels", issue_number=N)
    if "needs-approval" not in [l["name"] for l in labels]:
        # Add label
    ```
2. **Invoke spec-auditor** (if not already run):
    - Check session records or `./tmp/` files for auditor results
    - If missing: invoke spec-auditor
3. **Create sub-issues** (if multi-task and not already created):
    - Check `get_sub_issues` result
    - If empty and spec is multi-task: invoke `issue-operations --task link-sub-issue`

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Issue URL as the action URL (ALWAYS last)

## Label State Machine

Before adding or removing labels in completion, consult `141-planning-status-tracking.md §10` for the complete label transition matrix and the GitHub `labels` parameter warning (replaces all labels, not additive).

## Report Phase

Generate executive summary in chat:

```
**Summary:**

<What issue was created and its purpose>

**Outcome:** <What stakeholders get from the new issue>

Issue URL: ${BASE_URL}${GIT_OWNER}/${GIT_REPO}/issues/<number>
```

URL is ALWAYS last per `000-critical-rules.md`.