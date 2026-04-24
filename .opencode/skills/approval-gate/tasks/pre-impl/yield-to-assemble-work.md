# Task: yield-to-assemble-work

## Purpose

Present the execution plan (informative only, no confirmation), verify the no-questions checkpoint, and execute immediately to `assemble-work`. Contains post-analysis dispatch rules, prohibited actions, and developer involvement triggers.

## Entry Criteria

- Work state file written (from `write-work-state`)
- Dependency graph and execution order determined
- Agent has completed all analysis without invoking `question` tool

## Exit Criteria

- Execution plan presented in chat (informative, not a decision prompt)
- No-questions checkpoint verified
- Agent proceeds immediately to `divide-and-conquer --task assemble-work`
- No HALT between plan presentation and `assemble-work`

## Procedure

### Step 6: Present Execution Plan (Informative Only)

**MANDATORY: The dependency analysis MUST be visible in chat (not hidden in agent reasoning).**

**The plan is presented for informational purposes. Agent proceeds immediately to execution. No confirmation is requested or awaited.**

Format:

```markdown
## Authorization Set — Dependency Analysis

**Approved Issues:** #660, #662, #621, #614, #630

### Pre-Analysis Screening

| Issue | Screening Result | Reason |
|-------|-----------------|--------|
| #660 | Excluded — meta/non-code | No code changes required |
| #670 | Excluded — already-implemented | PR #719 merged, all criteria met |
| #671 | Scope-reduced — partially-implemented | Phase 1 done by PR #719; phases 2, 3 remaining |

### Classification

| Issue | Category | Files | Dependencies |
|-------|----------|-------|-------------|
| #662 | Independent | `.opencode/skills/` | None |
| #621 | Conflict-risk | `.opencode/guidelines/000-*.md` | Conflicts with #630 |
| #614 | Independent | `src/` | None |
| #630 | Must-precede #621 | `.opencode/guidelines/` | Must complete before #621 |
| #671 | Independent | `.opencode/skills/` | None (scope: phases 2, 3 only) |

### Execution Plan

**Phase 1 (Serial):**
1. #630 — must precede #621

**Phase 2 (Parallel-safe):**

Each parallel issue includes dispatch context:
- #662 (`.opencode/skills/`) → `worktree_path: .worktrees/spec-662`
- #614 (`src/`) → `worktree_path: .worktrees/spec-614`
- #671 (`.opencode/skills/` — phases 2, 3 only) → `worktree_path: .worktrees/spec-671`

**Phase 3 (After #630):**
- #621 (`.opencode/guidelines/`)

**Merge-time ordering:**
- #662 and #621 may conflict at merge — #621 will rebase onto `dev` after #662 merges before creating its PR.

**Excluded:**
- #660 — meta/behavioral issue, no code changes required
- #670 — already-implemented (PR #719)

**Scope-reduced:**
- #671 — partially-implemented (phase 1 done by PR #719; phases 2, 3 remaining)

Proceeding with execution plan.
```

**Checkpoint (MANDATORY):** Before proceeding to `assemble-work`, verify NO `question` tool calls have been made at ANY point during the pre-implementation-analysis flow (not just since plan presentation). If any were made, remove them and proceed autonomously. The execution plan is presented for informational purposes — no confirmation is requested or awaited. If any were made, the answers are irrelevant — the agent should have resolved the questions autonomously.

### Step 10: Execute Immediately

After presenting the plan, proceed immediately to `assemble-work`. Do not HALT. Do not ask for confirmation. Do not wait.

Yield control to `divide-and-conquer --task assemble-work`:

```text
/skill divide-and-conquer --task assemble-work
```

**assemble-work** reads the work state file and handles:

- Creating worktrees for the work set
- Dispatching sub-agents for each issue
- Collecting results and updating work state
- Running review-prep after all issues complete

This handoff ensures:

- No HALTs between issues in the work set
- Each sub-agent gets isolated context
- The orchestrator stays clean — no implementation pollution
- Work state survives context turnover

### Post-Analysis Dispatch (MANDATORY)

After producing the execution plan and dependency graph, the agent MUST proceed directly to the next step in the dispatch chain (typically `assemble-work`). The analysis result IS the decision — no separate user confirmation is required. Key rules:

1. **Presentation is a status report, not a decision prompt.** The execution plan presentation (Step 6) is informational. It does NOT create a decision point.
2. **No HALT after analysis unless `requires_developer: true`.** The only valid halt after pre-implementation-analysis is when screening sub-agents returned `requires_developer: true` per the exhaustive 5-condition list in `screen-issue.md`. When `requires_developer: false`, proceed without halting.
3. **"Yield" means "produce output and continue," NOT "present output and wait."** The dispatch chain from pre-implementation-analysis to assemble-work is automatic. No user interaction is expected or allowed between them.
4. **Halting to "present" results as a decision point is functionally identical to asking a question** — both violate `000-critical-rules.md` §"Pushing Agent Intelligence Decisions to the User" and `020-go-prohibitions.md` §1.

### Prohibited Actions

- **No `question` tool invocation** after plan presentation
- **No HALT** between plan presentation and `assemble-work`
- **No "Proceed?" / "Shall I?" / any confirmation solicitation**
- **No "awaiting approval" / "waiting for GO" / any pending-state marker**

### Developer Involvement Triggers

The ONLY conditions requiring developer input during authorization set analysis:

- **Unresolvable conflicts**: Contradictory success criteria between issues in the authorization set
- **Stale spec assumptions (different intent)**: Issue A references code that Issue B deletes, and A's intent differs from B's
- **Ambiguous supersession**: Two issues partially overlap, unclear which supersedes which
- **Uncertain reconciliation findings**: `reconcile-issue-graph` produced `requires_dev_action` entries with conflicting signals that prevent confident classification
- **screen-issue returned `requires_developer: true` AFTER reconciliation**: Any screening sub-agent flagged for developer review for reasons OTHER than status inconsistencies (which `reconcile-status` handles)

**Status inconsistencies are NOT a developer involvement trigger.** `reconcile-issue-graph` resolves them deterministically (auto-close for verified-complete, reopen for verified-incomplete). Only `uncertain` findings with conflicting evidence that prevent classification are escalated.

When any of these triggers fire, HALT and present the conflict to the developer with a clear question. Do NOT attempt to auto-resolve.

## Enforcement References

- Auto-dispatch routing: see `enforcement/auto-dispatch-table.md`
- Scope parsing: see `enforcement/scope-parsing.md`

## Work State I/O

- **Reads from:** `## write-work-state`
- **Writes to:** `## yield-to-assemble-work`

After completing this task, write results to the work state file under section `## yield-to-assemble-work` using the YAML format defined in `enforcement/work-state-schema.md`.