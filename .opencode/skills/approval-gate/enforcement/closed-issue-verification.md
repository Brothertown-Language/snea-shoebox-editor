# Closed-Issue Verification Module

## Closed State Verification Procedure

Before treating a closed issue as resolved (skipping implementation, auto-closing parents, removing from work sets), verify the closed state against live GitHub data.

### Verification Steps

1. Read issue via `github_issue_read(method=get, issue_number=N)`
2. Check `state` field — must be `"closed"`
3. Check `state_reason` field:
   - `"completed"` — requires merged PR evidence
   - `"not_planned"` — intentionally skipped; verify this is acceptable for current context
   - `"duplicate"` — verify the duplicate target issue exists and is resolved
4. For `"completed"` issues: verify merged PR exists
   - Search PRs referencing issue: `github_search_pull_requests(query="#N")`
   - Check at least one PR is merged: `github_pull_request_read(method=get, pullNumber=P)` → `merged == true`
5. If no merged PR found for a `"completed"` issue: classify as VERIFICATION-GAP

## State Reason Classification

| state_reason | Evidence Required | Trust Level |
|---------------|------------------|-------------|
| `completed` | Merged PR confirming implementation | Low — verify PR exists and is merged |
| `not_planned` | Developer intent to skip | Medium — check comments for skip rationale |
| `duplicate` | Target issue exists and is resolved | Low — verify target issue state |
| (null/missing) | Treat as unknown | None — re-verify from scratch |

## Auto-Close Rules

- NEVER auto-close parents while children are still open
- NEVER auto-close based solely on `state: "closed"` without merged PR evidence
- Use `approval-gate --task verify-closed-issue` for verification before any autoclose
- Use `approval-gate --task reconcile-issue-graph` for batch graph reconciliation