# Task: pre-implementation-analysis (Routing Document)

## Purpose

Analyze interdependencies and determine execution order for all approved issues — whether one or many — producing a flat item list for `assemble-work` dispatch. Every approval follows this unified path: sub-issue expansion → flat item list → assemble-work → work branch → pr-creation → one PR.

This task is a **routing document** that delegates to 6 atomic tasks in `pre-impl/`.

## Entry Criteria

- One or more issues approved
- Each issue verified by `verify-authorization`
- User explicitly authorized implementation

## Exit Criteria

- Execution plan presented in chat (informative only)
- Agent proceeds immediately to `assemble-work`

## Atomic Task Chain

```
collect-screening-results → reconcile-status → build-dependency-graph
→ check-cross-spec-overlap → write-work-state → yield-to-assemble-work
```

| Atomic Task | Concern | Original Steps |
|------------|---------|----------------|
| `pre-impl/collect-screening-results` | Mandatory sub-agent dispatch, screening collection, no-questions rule, autonomous classification resolution, gate evidence audit table | Steps -1, 0, 0.1, 0.15, 0.5 |
| `pre-impl/reconcile-status` | Issue status inconsistency reconciliation via `reconcile-issue-graph` | Step 0.7 |
| `pre-impl/build-dependency-graph` | Flat item list, cross-issue analysis, issue classification, dependency graph construction | Steps 1, 2, 3, 4 |
| `pre-impl/check-cross-spec-overlap` | Overlap check against open specs/plans outside the batch (four-tier classification) | Step 2 (Cross-Spec Overlap subsection) |
| `pre-impl/write-work-state` | Execution strategy, dev base hash, dispatch context, work state file persistence | Steps 5, 7, 8, 9 |
| `pre-impl/yield-to-assemble-work` | Present execution plan, verify no-questions checkpoint, dispatch to assemble-work | Steps 6, 10 |

**Chain-of-responsibility note:** Each atomic task uses the work state file for inter-task I/O. Tasks read inputs from predecessor sections and write results to their own section per `enforcement/work-state-schema.md`.

## Red Flags

- Never skip dependency analysis when multiple issues are approved together
- Never dispatch parallel subagents for conflict-risk issues without serialization
- Never include meta/non-code, already-implemented, superseded, or moot issues in the implementation plan
- Never present dependency analysis only in agent reasoning (MUST be in chat)
- Never assume all issues are independent without analysis
- Never execute must-precede issues out of order
- Never use `question` tool after presenting the execution plan
- Never HALT between plan presentation and `assemble-work`
- Never escalate status inconsistencies to the developer (use `reconcile-issue-graph`)

## Cross-References

- `000-critical-rules.md` §"Pushing Agent Intelligence Decisions to the User" — structural decisions are agent intelligence concerns
- `020-go-prohibitions.md` §1 — no prompts for authorization; "approved to PR" covers the full pipeline
- `screen-issue.md` — exhaustive `requires_developer: true` conditions
- `approval-gate/SKILL.md` §"Dispatch Order" — "MUST auto-dispatch" after analysis completes

## Enforcement References

- Evidence format + finding classification: see `enforcement/adversarial-verification.md`
- Scope parsing: see `enforcement/scope-parsing.md`
- Auto-dispatch routing: see `enforcement/auto-dispatch-table.md`
- Closed-issue verification: see `enforcement/closed-issue-verification.md`
- Sub-issue graph traversal: see `enforcement/sub-issue-graph-traversal.md`