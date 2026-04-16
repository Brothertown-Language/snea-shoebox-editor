# Task: reconcile-issue-graph

Act on findings from the issue graph traversal performed by `verify-authorization` §5.5. This task takes the traversal findings and resolves them — auto-closing verified-complete tickets, reopening verified-incomplete tickets, and flagging uncertain tickets for developer action.

## Pre-Conditions

- Graph traversal complete via `verify-authorization` §5.5
- Findings list available from traversal output
- `GIT_OWNER` and `GIT_REPO` from session context

## Entry Criteria

- Graph traversal has produced a findings list
- Each finding includes: issue number, current state, and traversal classification

## Exit Criteria

- All actionable findings resolved (auto-closed or reopened)
- Uncertain findings collected in `requires_dev_action` list
- Reconciliation report output to chat

## Procedure

### Step 1: Categorize Findings

For each finding from the traversal list, classify into one of six categories:

| Category | Condition | Action Class |
|----------|-----------|-------------|
| auto-close (merged PR) | Open + merged PR exists (`merged_at` confirmed via GitHub API) | auto-close |
| auto-close (code verified) | Open + success criteria verified against live code in repo | auto-close |
| reopen | Closed + no merged PR + code NOT in repo + `state_reason` not `not_planned` or `duplicate` | reopen |
| no-action (not_planned) | Closed + `state_reason: "not_planned"` | skip |
| no-action (duplicate) | Closed + `state_reason: "duplicate"` + target verified as covering scope | skip |
| uncertain | Conflicting or ambiguous signals that prevent confident classification | flag-for-dev |

### Step 2: Verify Auto-Close Candidates

For each auto-close candidate:

1. **Merged PR path**: Call `github_pull_request_read(method=get)` on any associated PR. Confirm `merged_at` is not null. Record PR number and `merged_at` timestamp as evidence.
2. **Code-in-repo path**: Use `read`, `grep`, or `srclight_get_symbol` to confirm success criteria are met in the live codebase. Record specific file paths and symbol names as evidence.
3. **If evidence is ambiguous**: Reclassify as `uncertain` and move to `requires_dev_action`.

### Step 3: Verify Reopen Candidates

For each reopen candidate:

1. Call `github_search_pull_requests` for the issue number — confirm no merged PR exists.
2. Use `read`/`grep`/`srclight_get_symbol` to confirm the code is NOT present in the repo.
3. Call `github_issue_read(method=get)` to confirm `state_reason` is not `not_planned` or `duplicate`.
4. **If a merged PR is found**: Reclassify as `no-action` — the closure may have been legitimate via a PR the traversal missed.
5. **If code IS found in repo**: Reclassify as `uncertain` — conflicting signals require dev judgment.

### Step 4: Process No-Action Findings

For `not_planned` findings: Record issue number and `state_reason`. No further action.

For `duplicate` findings: Verify the target issue exists and covers the scope. If the target is also problematic (closed without merged PR), reclassify the target as a separate finding. If the target is verified, record as no-action.

### Step 5: Collect Uncertain Findings

For each uncertain finding, collect:

- Issue number
- Current state
- Needed state (best assessment)
- Reason determination cannot be made

Add to `requires_dev_action` list in the result contract.

### Step 6: Execute Auto-Close Actions

For each verified auto-close candidate:

1. Call `github_issue_write(method=update, state=closed, state_reason=completed)` on the issue.
2. Call `github_add_issue_comment` with evidence:
   - Merged PR: "Auto-closing: merged PR #N confirmed (merged_at: TIMESTAMP). Issue graph reconciliation via `reconcile-issue-graph`."
   - Code verified: "Auto-closing: success criteria verified against live code (files: [...], symbols: [...]). Issue graph reconciliation via `reconcile-issue-graph`."
3. Remove `needs-approval` label if present.

### Step 7: Execute Reopen Actions

For each verified reopen candidate:

1. Call `github_issue_write(method=update, state=open)` on the issue.
2. Call `github_add_issue_comment`: "Reopening: no merged PR found and code not present in repo. Previous closure may have been premature. Issue graph reconciliation via `reconcile-issue-graph`."

### Step 8: Output Reconciliation Report

**When all findings resolved:**

```
Issue Graph Reconciliation for #<root>:
  Auto-closed: #N (merged PR #P), #M (code verified)
  Reopened: #O (no merged PR, code not in repo)
  No action: #Q (not_planned), #R (duplicate of #S)
  Nodes visited: <count>
```

**When uncertain findings remain:**

```
Issue Graph Reconciliation for #<root>:
  Auto-closed: #N (merged PR #P)
  Reopened: #O (no merged PR, code not in repo)
  Requires dev action:
    - #X: current=closed, needed=open — cannot verify implementation status (conflicting signals: PR exists but not merged, code may exist in another branch)
    - #Y: current=open, needed=closed — code appears present but success criteria partially unmet
  Nodes visited: <count>

🤖 <AI-Name> (<model-id>) ⚠️ needs-dev-action
```

## Evidence Requirements

Every action MUST produce a live tool-call artifact:

| Action | Required Evidence |
|--------|-------------------|
| Auto-close (merged PR) | `github_pull_request_read` response showing `merged_at` |
| Auto-close (code verified) | `read`/`grep`/`srclight` output confirming code in repo |
| Reopen | `github_search_pull_requests` showing no merged PR + codebase read showing code NOT present |
| No-action (not_planned/duplicate) | `github_issue_read` response showing `state_reason` |
| Uncertain | Conflicting tool-call results that prevent confident classification |

## Context Required

```yaml
root_issue_number: <N>
findings: [{issue: <N>, state: <str>, classification: <str>, evidence_summary: <str>}]
session_vars:
  GIT_OWNER: <from-session>
  GIT_REPO: <from-session>
  DEV_NAME: <from-session>
  DEV_EMAIL: <from-session>
  WORKTREE_PATH: <from-session>
```