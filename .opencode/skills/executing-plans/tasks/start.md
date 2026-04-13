# Task: start

Dispatch to divide-and-conquer/assemble-batch for implementation.

## Purpose

This task dispatches plan execution to `divide-and-conquer --task assemble-batch`, which handles all implementation through the unified batch workflow.

## Dispatch Procedure

1. **Verify plan approval** — confirm the plan issue has explicit approval in comments
2. **Verify prerequisites** — feature branch exists, working tree clean, dependencies ready
3. **Dispatch to divide-and-conquer:**

```
/skill divide-and-conquer --task assemble-batch
```

The `assemble-batch` task handles:

- Creating feature branches and worktrees
- Sub-agent dispatch for each implementation item
- Squash-merging feature branches into batch branch
- Verification gates (verification-before-completion, finishing-a-development-branch)

**There is no single-issue bypass.** Single issue = batch of one = one sub-agent.

## Legacy Task Redirects

| Legacy Task | Redirect Target |
|------------|----------------|
| `step` | `divide-and-conquer --task orchestrate` |
| `progress` | `divide-and-conquer --task orchestrate` |
| `verify` | `verification-before-completion --task verify` |

## Enforcement

- No approval → HALT (approval-gate blocks)
- Placeholders in plan → HALT (writing-plans blocks)
- No feature branch → HALT (git-workflow creates)