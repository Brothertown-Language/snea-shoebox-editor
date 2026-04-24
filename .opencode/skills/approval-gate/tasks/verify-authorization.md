# Task: verify-authorization

## Purpose

Check for explicit authorization and needs-approval label status before implementation. This task orchestrates the atomized sub-tasks in `verify-authorization/` for fine-grained, low-context verification.

## Entry Criteria

- User says "approved", "go", or similar authorization
- Spec exists as GitHub Issue

## Exit Criteria

- Authorization verified as explicit and for correct issue
- needs-approval label status checked
- Git state verified (worktree environment ready)
- Authorization recorded for scope tracking

## Sub-Task Dispatch Order

This task delegates to atomic sub-tasks. Each sub-task reads inputs from the work state file and writes results back. Invoke in sequence:

| Step | Sub-Task | Purpose |
|------|----------|---------|
| 0 | Inline fallback guard | If sub-agent returns empty, execute Steps 1-6 inline |
| 0.5 | `verify-authorization/scope-auto-resolve` | Parse authorization text, resolve scope/halt_at/pr_strategy/gap_fill |
| 1 | `verify-authorization/verify-explicit-authorization` | Check for "approved"/"go" + author identity + currency |
| 2 | Label check (inline) | Check needs-approval label status, handle explicit auth override |
| 3 | Authorization decision (inline) | Route based on authorization result |
| 4.5 | `verify-authorization/item-decomposition-check` | Verify item enumeration, dependency ordering, TDD steps |
| 4.6 | `verify-authorization/sc-traceability-check` | Verify SC-to-test traceability, RED-phase ordering |
| 5 | `verify-authorization/sub-issue-verification` | Sub-issue phase count, adversarial verification, closed-issue check |
| 5b | `verify-authorization/spec-to-plan-cascade` | Spec-to-plan approval cascade |
| 5b.5+5c | `verify-authorization/gap-fill-cascade` | Gap-fill precedence and cascade execution |
| 6 | `verify-authorization/auto-dispatch` | Scope-aware auto-dispatch + output lineage |

## Sub-Agent Result Guard

When `verify-authorization` is dispatched as a sub-agent and returns empty or whitespace-only:

1. Report: `"Sub-agent for verify-authorization returned empty result, performing inline"`
2. Execute Steps 0.5–6 inline using direct tool calls
3. Produce the same result contract format

**Double-failure protocol:** If inline verification also fails:
1. Report: `"Sub-agent and inline verification both failed for verify-authorization"`
2. Invoke `--task completion` on the `approval-gate` skill
3. HALT with status message + byline

## Enforcement References

- Evidence format + finding classification: see `enforcement/adversarial-verification.md`
- Scope parsing: see `enforcement/scope-parsing.md`
- Dispatch routing: see `enforcement/auto-dispatch-table.md`
- Closed-issue verification: see `enforcement/closed-issue-verification.md`
- Sub-issue graph traversal: see `enforcement/sub-issue-graph-traversal.md`

## Result Contract

```yaml
status: DONE | BLOCKED
task: verify-authorization
issue_number: <N>
authorization_result: authorized | unauthorized | needs_approval
cascade_applied: bool
sub_issues_verified: bool
gates_passed: [gate_name]
blocking_reason: <reason|null>
cascade_type: plan_cascade | output_lineage_cascade | none
cascade_parent: <issue_number | null>
authorization_scope: standard | for_spec | for_plan | for_implementation | for_code_review | for_pr | pr_only | review_only
scope_source: parsed | default
halt_at: <pipeline_stage>
pr_strategy: stacked | individual | none
gap_fill_actions: [<action_list>]
```