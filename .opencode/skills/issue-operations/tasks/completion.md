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

### Step N: EXTRACT URL FROM API RESPONSE

1. The Issue URL MUST be copied verbatim from the `github_issue_write` API response's `html_url` field.
2. Do NOT retype, reconstruct, or assemble the URL from known values (org, repo, number).
3. Paste the URL exactly as returned. If the API response is `{ "html_url": "https://github.com/Org/Repo/issues/42" }`, the output URL is `https://github.com/Org/Repo/issues/42` — character for character.
4. Verification checkpoint: Compare the pasted URL character-by-character against the `html_url` field in the API response before sending.

Generate executive summary in chat:

```
**Summary:**

<What issue was created and its purpose>

**Outcome:** <What stakeholders get from the new issue>

Issue URL: <html_url from github_issue_write API response — NEVER construct from template>
```

URL is ALWAYS last per `000-critical-rules.md`.

## Live Verification: Completion Evidence (MANDATORY)

**Each completion state check MUST be verified via tool call, not just asserted. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Issue was created" | Verify issue exists | `github_issue_read(method="get", issue_number=N)` | MISSING-ELEMENT |
| "`needs-approval` label applied" | Verify label present | `github_issue_read(method="get_labels", issue_number=N)` | MISSING-ELEMENT |
| "Sub-issues created" | Verify sub-issues exist | `github_issue_read(method="get_sub_issues", issue_number=N)` | MISSING-ELEMENT |
| "Auditor was invoked" | Check for auditor results | Session records or `./tmp/` files | VERIFICATION-GAP |

**Evidence artifact:** Tool call results for each completion state check.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Issue not found | MISSING-ELEMENT | flag-for-review | HALT — creation may have failed |
| Label missing | MISSING-ELEMENT | auto-fix | Add label immediately |
| Sub-issues missing (multi-task) | MISSING-ELEMENT | conditional | Create sub-issues if multi-task spec |
| Auditor not invoked | VERIFICATION-GAP | conditional | Invoke spec-auditor |