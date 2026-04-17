# Task: reconcile-issue-graph

Act on findings from the issue graph traversal performed by `verify-authorization` §5.5. This task takes the traversal findings and resolves them — auto-closing verified-complete tickets, reopening verified-incomplete tickets, and flagging uncertain tickets for developer action.

## Pre-Conditions

- Graph traversal complete via `verify-authorization` §5.5
- Findings list available from traversal output
- `<GitOwner>` and `<GitRepo>` from session context

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

### Step 1.5: Cross-Reference Plan Scope Check

For each sub-issue finding in the traversal list:

1. **Identify the parent plan** — call `github_issue_read(method=get_sub_issues, owner=<GitOwner>, repo=<GitRepo>, issue_number=<N>)` on each finding's parent to confirm the plan relationship. Record the parent plan issue number.
2. **Read the parent plan body** — call `github_issue_read(method=get, owner=<GitOwner>, repo=<GitRepo>, issue_number=<plan_N>)` and extract the spec reference using the pattern `Spec: #N`.
3. **Search for other plans referencing the same spec** — call `github_search_issues(query="label:plan \"Spec: #<spec_N>\" in:body repo:<GitOwner>/<GitRepo>", owner=<GitOwner>, repo=<GitRepo>)`. Collect all plan issue numbers returned.
4. **Compare plan scopes for overlap** — for each additional plan found, call `github_issue_read(method=get)` to read its body. Extract phase titles and compare with the current plan's phases. Record overlapping phase titles.
5. **If overlap exists**: Add a finding to the `uncertain` classification with reason `"duplicate plan track — requires dev action to determine which plan owns deliverables"`. Record: spec number, all plan numbers referencing that spec, and the overlapping phase titles.

### Step 2: Verify Auto-Close Candidates

For each auto-close candidate:

1. **Merged PR path**: Call `github_pull_request_read(method=get)` on any associated PR. Confirm `merged_at` is not null. Record PR number and `merged_at` timestamp as evidence.
2. **Code-in-repo path**: Use `read`, `grep`, or `srclight_get_symbol` to confirm success criteria are met in the live codebase. Record specific file paths and symbol names as evidence.
3. **If evidence is ambiguous**: Reclassify as `uncertain` and move to `requires_dev_action`.

### Step 2.5: Evidence Gate

For each `auto-close` candidate, produce at least one live evidence artifact using `read`, `grep`, or `srclight_get_symbol` before the candidate can proceed to Step 6. The evidence artifact must reference specific file paths, symbol names, or grep patterns that verify the success criteria are met. Record each artifact with a unique identifier (e.g., `evidence-<issue_number>-1`).

- **Merged PR path**: The `github_pull_request_read` result from Step 2 is sufficient evidence. Record as `evidence-<N>-1: github_pull_request_read(PullRequest=<P>) → merged_at=<timestamp>`.
- **Code-in-repo path**: Require at least one `read`, `grep`, or `srclight_get_symbol` tool call confirming the specific code or symbol that satisfies the success criteria. Record as `evidence-<N>-1: <tool>(<target>) → <result_summary>`.

Candidates without evidence artifacts are reclassified as `uncertain` with reason "no evidence artifact produced for auto-close candidate".

### Step 2.7: Comment Conflict Detection

For each `auto-close` candidate, scan all comments on the issue for conflicting signals that would prevent confident auto-closure.

1. Call `github_issue_read(method=get_comments, owner=<GitOwner>, repo=<GitRepo>, issue_number=<N>)` for each candidate.
2. For each comment, check for conflict phrases within 24 hours of the reconciliation run timestamp: `"needs work"`, `"verification gap"`, `"not complete"`, `"partial"`, `"⚠️"`.
3. If any comment posted within the 24-hour window contains a conflict phrase, reclassify the candidate from `auto-close` to `uncertain` with reason `"comment-content conflict: issue comments flag incomplete work"`. Record the conflicting comment ID and phrase.
4. If no conflicting comments are found within the 24-hour window, the candidate passes this gate.

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
2. Call `github_add_issue_comment` with evidence (including Step 2.5 artifact reference):
   - Merged PR: "Auto-closing: merged PR #N confirmed (merged_at: TIMESTAMP) (evidence: merged_at via github_pull_request_read). Issue graph reconciliation via `reconcile-issue-graph`."
   - Code verified: "Auto-closing: success criteria verified against live code (files: [...], symbols: [...]) (evidence: <artifact description from Step 2.5>). Issue graph reconciliation via `reconcile-issue-graph`."
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
  Duplicate Plan Tracks:
    - Spec #S: plans #P1, #P2 — overlapping phases: [phase title, phase title]
  Nodes visited: <count>

🤖 <AgentName> (<ModelId>) ⚠️ needs-dev-action
```

If no duplicate plan tracks were found, omit the `Duplicate Plan Tracks` section entirely.

## Evidence Requirements

Every action MUST produce a live tool-call artifact:

| Action | Required Evidence |
|--------|-------------------|
| Auto-close (merged PR) | `github_pull_request_read` response showing `merged_at` |
| Auto-close (code verified) | `read`/`grep`/`srclight` output confirming code in repo |
| Reopen | `github_search_pull_requests` showing no merged PR + codebase read showing code NOT present |
| No-action (not_planned/duplicate) | `github_issue_read` response showing `state_reason` |
| Uncertain | Conflicting tool-call results that prevent confident classification |
| Evidence gate | `read`/`grep`/`srclight_get_symbol` output for auto-close candidates (mandatory — candidates without artifacts reclassified as `uncertain`) |
| Comment conflict scan | `github_issue_read(method=get_comments)` output confirming no contradicting comments within 24-hour window |
| Cross-reference check | `github_search_issues` output showing plans referencing the same spec + `github_issue_read` output confirming scope overlap |

## Context Required

```yaml
root_issue_number: <N>
findings: [{issue: <N>, state: <str>, classification: <str>, evidence_summary: <str>}]
session_vars:
  GitOwner: <from-session>
  GitRepo: <from-session>
  DevName: <from-session>
  DevEmail: <from-session>
  WorktreePath: <from-session>
```