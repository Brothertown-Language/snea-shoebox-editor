# Task: collect-screening-results

## Purpose

Dispatch `screen-issue` sub-agents for every approved issue, collect their result contracts, enforce the no-questions rule, resolve classifications autonomously, and assemble the Gate Evidence Audit Table. This is the **first** atomic task in the pre-implementation-analysis chain.

## Entry Criteria

- One or more issues approved (e.g., `Approved: #660`, `Approved: #660, #662, #621`)
- Each issue has been verified by `verify-authorization`
- User has explicitly authorized implementation
- Session vars available: `github.owner`, `github.repo`, `dev.name`, `dev.email`, `worktree.path`

## Exit Criteria

- All approved issues dispatched to `screen-issue` sub-agents (no inline screening)
- All screening result contracts collected
- No-questions rule verified (zero `question` tool invocations during this task)
- Autonomous classification resolution applied to all screening classifications
- Gate Evidence Audit Table assembled from screening results
- Downgrades applied for any row with failed gate evidence

## Procedure

### Step -1: Mandatory Sub-Agent Dispatch (MANDATORY FIRST)

Before reading ANY issue body:

1. Dispatch `screen-issue` sub-agents for EVERY approved issue — no count check, no inline path
2. Do NOT read any issue body into orchestrator context

**CRITICAL VIOLATION:** Reading issue bodies into orchestrator context before sub-agent dispatch is a CRITICAL GUIDELINE VIOLATION per `000-critical-rules.md` §Inline Screening of Authorization Sets. The orchestrator's context window must stay clean for cross-issue merge and dependency graph building — not consumed by raw issue bodies.

**There is no inline screening path.** Every approved issue — whether 1, 2, or 20 — MUST be screened by a `screen-issue` sub-agent dispatched via `task(subagent_type="general")`. The count threshold was removed because inline screening creates a forked code path that agents exploit to skip sub-agents. See `000-critical-rules.md` §"Common Misconception: Small approval sets can be screened inline" for the rationale.

**DO NOT re-introduce a count threshold.** This is a structural invariant, not a performance optimization.

### Step 0: Collect Screening Results

Collect per-issue screening results from `screen-issue` sub-agents (mandatory parallel dispatch).

All approved issues have been dispatched to `screen-issue` sub-agents in Step -1. Collect the result contracts:

```
For each approved issue:
  Collect result contract from dispatched screen-issue sub-agent
  Assemble into screening results
```

**If screening results are NOT available** (e.g., sub-agent dispatch failed), HALT and report the failure — do NOT fall back to inline screening.

**Dispatch context per sub-agent:**

```yaml
issue_number: <N>
work_peers: [<list of all approved issue numbers except this one>]
authorization_scope: <scope_value>
halt_at: <pipeline_stage>
pr_strategy: stacked | individual | none
session_vars:
  github.owner: <from-session>
  github.repo: <from-session>
  dev.name: <from-session>
  dev.email: <from-session>
  worktree.path: <from-session>
```

**After all sub-agents return**, assemble screening results.

### Step 0.1: No Questions During Analysis (ZERO TOLERANCE)

**CRITICAL: The `question` tool MUST NOT be invoked at ANY point during the pre-implementation-analysis flow — not just after plan presentation.**

Structural classification decisions (authorization scope, plan structure, sub-issue creation, execution order) are agent intelligence concerns per `000-critical-rules.md` §"Pushing Agent Intelligence Decisions to the User." The agent resolves these autonomously.

If the agent encounters a scenario not covered by existing rules:
1. Apply the closest applicable rule by analogy
2. If no analogy exists, resolve with best judgment and document the reasoning in the execution plan
3. Do NOT escalate to the developer unless the scenario matches one of the five `requires_developer: true` conditions from `screen-issue`

### Step 0.15: Autonomous Classification Resolution (MANDATORY)

When screening results return classifications, the orchestrator MUST resolve them autonomously using the decision table below. These are deterministic mappings — not judgment calls requiring developer input.

#### Classification Decision Table

| Screening Classification | Autonomous Action | Rationale |
|---|---|---|
| `already-implemented` | Exclude from work set; add to auto-close list via `verify-already-implemented` | All success criteria met; no work remaining |
| `partially-implemented` | Scope-reduce to remaining phases; continue with gap work only | Completed phases require no action; remaining gaps are the scope |
| `scope-reduced` | Continue with remaining phases only | Same as partially-implemented — the completed phases are done |
| `null` (fresh spec) | Include fully in work set | No prior implementation exists |
| `superseded` | Exclude from work set; flag in execution plan report | Another spec fully encompasses this one |
| `moot` | Exclude from work set; flag in execution plan report | Problem no longer exists or references restructured/removed code |

#### Re-Planning Decision

When the authorization text contains phrases like "re-plan as needed" or "revise as needed":

| Authorization Phrase | Autonomous Action |
|---|---|
| "re-plan as needed" | Re-plan the spec against the current codebase before implementing |
| "revise as needed" | Re-plan the spec against the current codebase before implementing |
| "update the spec" | Re-plan the spec against the current codebase before implementing |
| No re-planning phrase | Implement the spec as written, even if partially implemented |

#### Already-Implemented Closure Decision

| Scenario | Autonomous Action |
|---|---|
| Already-implemented issue referenced by another spec-fix | Close via the spec-fix's procedure (e.g., #1037 Phase 2 closes #1025) |
| Already-implemented with no referencing spec-fix | Close via `verify-already-implemented` auto-close procedure |
| Partially-implemented issue | Scope-reduce, do NOT close |

#### `requires_developer: true` Escalation Criteria

The ONLY conditions where screening results warrant developer escalation:

1. **Multiple valid structures with genuinely ambiguous trade-offs** (3+ subsystems with unclear boundaries — not a preference between two equivalent approaches)
2. **Legal/compliance concerns** requiring human judgment
3. **Developer must choose between mutually exclusive approaches** (not a choice between equivalent options)
4. **Unresolvable conflicts** between issues in the authorization set (contradictory success criteria)
5. **Different-intent stale assumptions** (Issue A references code that Issue B deletes, and their intents conflict)

All other scenarios — including classification decisions, re-planning, scope-reducing, and closure — are resolved autonomously per this decision table.

### Step 0.5: Assemble Gate Evidence Audit Table

From the collected screening results, assemble the full Gate Evidence Audit Table:

```markdown
## Gate Evidence Audit Table

| Issue # | Sub-issues Enumerated? (Gate 1) | All Sub-issues Verified? | Closure Legitimacy Verified? | Success Criteria Extracted? (Gate 2) | All Criteria Verified vs Codebase? | Final Classification |
|---------|----------------------------------|--------------------------|-------------------------------|--------------------------------------|-----------------------------------|---------------------|
| #N | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | <classification> |
```

Each row comes from the `gate_evidence` field of the corresponding `screen-issue` result contract.

**If ANY row has ❌ in columns 2-5:** That issue's classification is INVALID. It MUST be DOWNGRADED:
- ❌ in Gate 1 columns → DOWNGRADE to "partially-implemented" (sub-issues not verified)
- ❌ in Gate 2 columns → DOWNGRADE to "partially-implemented" or "not-implemented-despite-closure" (success criteria not verified)

**After downgrades:** Remove downgraded issues from "already-implemented" list. Add them to the "partially-implemented" list in the execution plan. Re-classify per screening results.

**If the table is incomplete:** HALT and complete it before proceeding.

## Enforcement References

- Evidence format + finding classification: see `enforcement/adversarial-verification.md`
- Scope parsing: see `enforcement/scope-parsing.md`
- Auto-dispatch routing: see `enforcement/auto-dispatch-table.md`
- Closed-issue verification: see `enforcement/closed-issue-verification.md`
- Sub-issue graph traversal: see `enforcement/sub-issue-graph-traversal.md`