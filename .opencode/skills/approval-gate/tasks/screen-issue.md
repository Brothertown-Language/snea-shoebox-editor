# Task: screen-issue (Routing Document)

## Purpose

Per-issue screening for pre-implementation analysis. Screen a single approved issue against screening categories (already-implemented, superseded, moot, stale assumptions, partial implementation, revision status, meta/non-code, cross-issue sub-issue handling). Produce a compact result contract for cross-issue merge.

## Gate Tasks

This task delegates to two atomic gate tasks executed sequentially:

| Gate Task | Concern | Steps |
|-----------|---------|-------|
| `screen/screen-issue-gate1` | Read issue, screening categories, Gate 1 (sub-issue enumeration), GA-1 | Steps 1-3 |
| `screen/screen-issue-gate2` | Gate 2 (success criteria verification), cross-references, evidence audit GA-2–GA-4, sub-issue expansion, cross-issue handling, file/symbol extraction, result contract | Steps 4-10 |

## Chain

```
gate1 → gate2
```

Gate 1 classifies the issue and executes sub-issue enumeration. If the issue is an "already-implemented" candidate, Gate 1 MUST pass before gate2 runs. Gate 2 verifies success criteria, completes the evidence audit, and produces the final result contract.

**Chain-of-responsibility note:** Each gate task uses the work state file for inter-task I/O. Gate tasks read inputs from predecessor sections and write results to their own section per `enforcement/work-state-schema.md`.

## Entry Criteria

- Single issue number to screen (passed via dispatch context)
- Issue has been verified by `verify-authorization`
- User has explicitly authorized implementation
- `<github.owner>` and `<github.repo>` available from dispatch context

## Exit Criteria

- Issue classified into one screening category
- Gate 1 (sub-issue enumeration) executed if applicable
- Gate 2 (success criteria verification) executed if applicable
- Compact result contract produced (≈100-500 words, YAML-structured)

## Enforcement References

- Evidence format + finding classification: see `enforcement/adversarial-verification.md`
- Scope parsing: see `enforcement/scope-parsing.md`
- Auto-dispatch routing: see `enforcement/auto-dispatch-table.md`
- Closed-issue verification: see `enforcement/closed-issue-verification.md`
- Sub-issue graph traversal: see `enforcement/sub-issue-graph-traversal.md`