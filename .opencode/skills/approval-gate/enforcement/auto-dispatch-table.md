# Auto-Dispatch Table Module

## Context Differentiation

When a spec is approved, the auto-dispatch chain determines which downstream actions are required based on authorization scope and issue state.

| Context | Dispatch Target |
|---------|----------------|
| Spec approved, no plan exists | `writing-plans --task create` |
| Spec approved, faithful plan exists | Auto-approve plan (cascade) |
| Plan approved, no sub-issues | `issue-operations --task link-sub-issue` |
| Plan approved, sub-issues linked | `divide-and-conquer --task assemble-work` |
| Implementation complete | `verification-before-completion` |
| Verification passed | `finishing-a-development-branch --task checklist` |
| Checklist passed | `git-workflow --task review-prep` |

## Scope-Dependent Routing

| Authorization Scope | Auto-Dispatch Behavior |
|---------------------|----------------------|
| `standard` | Each gate requires explicit approval; no auto-bypass |
| `for_spec` | HALT after spec_created; no auto-dispatch beyond spec creation |
| `for_plan` | Auto-create spec (gap-fill), HALT after plan_created |
| `for_implementation` | Auto-create spec+plan (gap-fill), auto-approve, proceed through implementation |
| `for_code_review` | Auto-create spec+plan, auto-approve, proceed through implementation + code review |
| `for_pr` | Auto-create spec+plan, auto-approve, proceed through PR creation, stacked PR |
| `pr_only` | Skip to PR creation, stacked PR |
| `review_only` | Skip to code review readiness |

## Dispatch Order (Mandatory)

After plan approval, the dispatch order is:

1. `git-workflow --task pre-work` — worktree creation
2. `divide-and-conquer --task assemble-work` — sub-agent dispatch
3. `verification-before-completion` — success criteria verification
4. `finishing-a-development-branch --task checklist` — branch readiness
5. `git-workflow --task review-prep` — push, compare URL

Each step produces an evidence artifact before proceeding to the next.

## Path Routing

Three chain-of-responsibility paths route through verify-authorization sub-tasks. Path selection is determined by issue count, scope, and sub-issue presence.

| Path | Criteria | Skips |
|------|----------|-------|
| fast-path | 1 issue, `standard` scope, 0 sub-issues, explicit auth | needs-approval-label check, item-decomposition, sc-traceability, sub-issue-verification, spec-to-plan-cascade, gap-fill-cascade, screen-issue, pre-implementation-analysis |
| medium-path | 1 issue + sub-issues OR plan with phases | screen-issue (single issue), pre-implementation-analysis (no dependency graph needed) |
| full-path | Multi-issue authorization set | None — all steps executed |

**Tier 1 mandates (worktree, branch protection) are never skipped regardless of path.** Work state file is the durable context bridge between hops across all paths.