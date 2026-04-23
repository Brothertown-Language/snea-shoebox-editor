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

## Success Criteria Verification (Step 7)

### SC Verification Is MANDATORY

Step 7 of `verify-closed-issue` is MANDATORY with ZERO TOLERANCE. Skipping SC verification after confirming a merged PR exists is a CRITICAL GUIDELINE VIOLATION.

A merged PR proves code was merged, NOT that success criteria are met. Every success criterion MUST be verified against the live codebase with a tool-call artifact as evidence.

### SC Verification Procedure

1. Extract success criteria from the issue body (parse `- [ ]` or `- [x]` checklist items under "Success Criteria" heading)
2. If no success criteria found: result remains `VERIFIED_CLOSED` with note `SC_VERIFICATION_NOT_PERFORMED`
3. If success criteria found: verify EACH criterion against the live codebase using `read`, `grep`, `srclight_get_symbol`, `github_pull_request_read`, or test execution
4. Produce a per-SC pass/fail table with columns: SC ID, criterion text, verification tool used, evidence detail, PASS/FAIL

### Downgrade Path

| SC Verification Result | Original Result | Downgraded Result |
|------------------------|-----------------|-------------------|
| All SCs pass | VERIFIED_CLOSED | VERIFIED_CLOSED (no change) |
| Some SCs pass | VERIFIED_CLOSED | PARTIALLY_IMPLEMENTED |
| No SCs pass | VERIFIED_CLOSED | NOT_IMPLEMENTED_DESPITE_CLOSURE |
| No SCs found | VERIFIED_CLOSED | VERIFIED_CLOSED (note: SC_VERIFICATION_NOT_PERFORMED) |

### ZERO TOLERANCE Enforcement

- Reporting a downgraded result as VERIFIED_CLOSED is a CRITICAL GUIDELINE VIOLATION
- Stating "I checked" without a tool-call artifact is a CRITICAL GUIDELINE VIOLATION per `065-verification-honesty.md`
- Each SC MUST produce a tool-call artifact as evidence
- The default comparison mode is `exact` — character-for-character match
- `semantic` comparison requires explicit per-field justification

## Auto-Close Rules

- NEVER auto-close parents while children are still open
- NEVER auto-close based solely on `state: "closed"` without merged PR evidence
- NEVER treat a closed issue as verified without confirming success criteria pass (Step 7)
- NEVER skip Step 7 SC verification and report VERIFIED_CLOSED
- Use `approval-gate --task verify-closed-issue` for verification before any autoclose
- Use `approval-gate --task reconcile-issue-graph` for batch graph reconciliation