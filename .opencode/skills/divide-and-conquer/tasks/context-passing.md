# Task: context-passing

Migrated from `implementation-workflow` task context-passing.

## Purpose

Reference document for yield-back context patterns between subtasks in the divide-and-conquer orchestration chain, including phase progress information that must travel across phase boundaries.

## Entry Criteria

- Orchestration is in progress
- A subtask is about to be invoked and needs context

## Exit Criteria

- Correct context shape is passed to the next subtask

## Procedure

### What Pre-Work Needs FROM Authorization

```yaml
authorization: confirmed (bool)
issue_number: int
```

### What Implementation Needs FROM Pre-Work

```yaml
branch: string
working_tree_clean: bool
```

### What Review-Prep Needs FROM Implementation

```yaml
files_changed: list
commit_summary: string
implementation_status: success | failure
```

### What Verification Gate Needs FROM Implementation

```yaml
issue_number: int
phase: string
success_criteria: list
files_changed: list
```

### What Finishing Checklist Needs FROM Verification

```yaml
branch: string
verification_passed: true
implementation_complete: true
```

### What Chat Needs FROM Review-Prep

```yaml
compare_url: string (actionable link)
exec_summary: string (markdown, human-readable)
```

### Phase Progress — What Travels at Phase Boundaries

When the orchestrator dispatches a sub-agent for a phase that follows a prior phase, the dispatch context MUST carry phase progress information composed from prior sub-agent results and the Plan STATUS marker. This information ensures each phase knows what has already been accomplished and can act accordingly.

**Phase progress is prose-driven.** The requirement is that the information travels — the agent composing the context decides how to encode it. The following information must be present:

- **Completed phases by concern name.** Each completed phase should be identified by the concern it addresses, not just a phase number. For example: "dispatch context schema" rather than "Phase 1", "assemble-batch phase progress" rather than "Phase 3". The concern name makes the progress meaningful to the receiving sub-agent.

- **Concern boundaries crossed.** When the current phase's work transitions from one architectural concern to another (e.g., from data layer to UI, from orchestration to enforcement, from schema definition to runtime behavior), this transition must be documented. The boundary description should explain what concern the previous phase addressed and what concern the current phase enters.

- **Verification evidence.** What was verified in prior phases and the outcome. This is not a test log — it is a prose summary of what the sub-agent confirmed and the result. For example: "verified that the dispatch context contract includes the new phase_progress field and all invariants hold" rather than "3/3 tests passed".

**How it is composed:**

The orchestrator builds phase_progress incrementally. Before each sub-agent dispatch:
1. Read the Plan STATUS marker to identify which phases are already complete
2. Accumulate `completed_phases`, `concern_boundaries_crossed`, and `verification_evidence` from each prior sub-agent's result
3. If this sub-agent's work crosses a concern boundary, note the transition in `concern_boundaries_crossed`

**How it is NOT composed:**

There is no fixed template, no rigid YAML schema, no mandatory section headers. The orchestrator describes progress in natural prose that communicates what the next sub-agent needs to know. The information requirement is the rule; the encoding is up to the agent.

### Decision Log for Full Context History

`prior_context` in the dispatch context carries the most recent intent summary — it is designed for immediate consumption by the next sub-agent. For the full history of design decisions across ALL phases, the orchestrator and sub-agents should reference the **Decision Log** persisted on the Plan issue.

The Decision Log is an append-only sequence of GitHub Issue comments on the Plan issue. Each comment captures one sub-agent's `decision_log_entry` — the design decisions made during that phase. It survives session restarts because it lives on the GitHub Issue, not in transient agent context.

When `prior_context` references a decision that may need fuller explanation, the orchestrator should note "see Decision Log on Plan #N" so the sub-agent can retrieve the full context history if needed.

## Edge Cases

### Context Lost Between Steps

If a yield-back produces empty or missing fields:

1. HALT orchestration
2. Report which context field is missing
3. Wait for manual intervention

### Phase Progress with No Prior Phases

For the first sub-agent dispatched (no prior phases completed), `phase_progress` should still be present but note that no prior phases exist. For example: "No phases completed yet. This is the first phase." This ensures the field is never absent — it is either populated with prior progress or explicitly states that no progress has been made.

### Pre-Work Asks for Auth Again

Pre-work receives context from orchestrator — no re-authorization check needed. If pre-work prompts for auth, it received stale context. Re-invoke with fresh context from approval-gate.

Co-authored with AI: <AI-Name> (<model-id>)
## Live Verification: Context Accuracy (MANDATORY)

**Verify dispatch context accuracy before sending to sub-agents.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "WORKTREE_PATH correct" | Verify path exists | `ls -d <path>` | STRUCTURE-VIOLATION |
| "Session vars current" | Verify vars match session init | Check against session values | VERIFICATION-GAP |
| "Prior results accurate" | Verify result contracts from prior sub-agents | Read batch state file | VERIFICATION-GAP |

**Evidence artifact:** Path verification and session var check results.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| WORKTREE_PATH invalid | STRUCTURE-VIOLATION | auto-fix | HALT — cannot safely dispatch |
| Stale session vars | VERIFICATION-GAP | conditional | Refresh from session init |
| Prior results contradicted | VERIFICATION-GAP | conditional | Re-verify prior sub-agent output |
