# Task: reconcile-status

## Purpose

Identify and reconcile issue status inconsistencies from the Gate Evidence Audit Table. Invoke `reconcile-issue-graph` for deterministic corrections before the flat item list is assembled. This prevents the pipeline from escalating deterministic status corrections to the developer.

## Entry Criteria

- Gate Evidence Audit Table assembled (from `collect-screening-results`)
- Screening result contracts available for all approved issues
- Issues with status inconsistencies identified

## Exit Criteria

- All deterministic status inconsistencies resolved (auto-close or reopen)
- Only `uncertain` findings (conflicting signals) remain for developer escalation
- Affected issues re-read from GitHub API with updated state
- Screening result classifications updated for any state changes
- Reconciliation report output to chat

## Procedure

### Step 0.7: Reconcile Issue Status Inconsistencies (MANDATORY)

After the Gate Evidence Audit Table is assembled, identify all issues with status inconsistencies and invoke `reconcile-issue-graph` to auto-correct them before assembling the flat item list. This step prevents the pipeline from escalating deterministic status corrections to the developer.

**Status inconsistency indicators from screening results:**

| Indicator | Example | Reconciliation Action |
|-----------|---------|----------------------|
| Issue reopened after PR merge | `state: open` + merged PR exists with `Fixes #N` | Auto-close (merged PR path) |
| Issue open but all success criteria verified in codebase | `state: open` + Gate 1 + Gate 2 pass | Auto-close (code verified path) |
| Sub-issue closed without merged PR | Sub-issue `state: closed` + `state_reason` not `not_planned`/`duplicate` + no merged PR | Reopen |
| Issue closed as completed but success criteria fail Gate 2 | `state: closed` + Gate 2 FAIL | Reopen (not-implemented-despite-closure) |
| Sub-issue open but parent PR merged with `Fixes` on parent | Sub-issue `state: open` + parent has merged PR | Evaluate: auto-close if criteria met, or include remaining work |

**Procedure:**

1. **Collect inconsistencies:** From the screening results, collect all issues where the current GitHub state contradicts the verified implementation state:
   - `category: already-implemented` + `gate_evidence.gate1_closure_legitimacy: false` → status inconsistency
   - `category: partially-implemented` + issue/sub-issues closed prematurely → status inconsistency
   - `requires_developer: true` due to status confusion (not genuine conflict) → route to reconciliation

2. **Build findings list:** For each inconsistent issue, create a finding with:
   - `issue_number`: the issue with wrong state
   - `state`: current state from GitHub API
   - `classification`: one of `auto-close (merged PR)`, `auto-close (code verified)`, `reopen`, `no-action (not_planned)`, `no-action (duplicate)`, `uncertain`
   - `evidence_summary`: brief description of why the state is wrong

3. **Invoke `reconcile-issue-graph`:** Pass the findings list to the reconciliation task. Follow the `reconcile-issue-graph` procedure exactly:
   - Step 1: Categorize findings (reuse classifications from above)
   - Step 2: Verify auto-close candidates (merged PR or code verification)
   - Step 3: Verify reopen candidates (no merged PR, code not in repo)
   - Step 4: Process no-action findings
   - Step 5: Collect uncertain findings (only these escalate to developer)
   - Step 6: Execute auto-close actions (update issue state + comment with evidence)
   - Step 7: Execute reopen actions (update issue state + comment with evidence)
   - Step 8: Output reconciliation report to chat

4. **Re-screen after reconciliation:** After `reconcile-issue-graph` completes, re-read the affected issues' state from GitHub API. Update screening result classifications if state changed. Proceed to `build-dependency-graph`.

**Key principle:** The developer is NEVER asked to determine whether an issue's state is correct. `reconcile-issue-graph` resolves all deterministic cases (merged PR = auto-close, no merged PR = reopen). Only `uncertain` findings (conflicting signals) are escalated.

## Enforcement References

- Closed-issue verification: see `enforcement/closed-issue-verification.md`
- Sub-issue graph traversal: see `enforcement/sub-issue-graph-traversal.md`
- Auto-dispatch routing: see `enforcement/auto-dispatch-table.md`

## Work State I/O

- **Reads from:** `## collect-screening-results`
- **Writes to:** `## reconcile-status`

After completing this task, write results to the work state file under section `## reconcile-status` using the YAML format defined in `enforcement/work-state-schema.md`.