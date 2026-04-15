# Task: start

Dispatch to divide-and-conquer/assemble-batch for implementation.

## Purpose

This task dispatches plan execution to `divide-and-conquer --task assemble-batch`, which handles all implementation through the unified batch workflow.

## Dispatch Procedure

1. **Verify plan approval** — confirm the plan issue has explicit approval in comments
2. **Verify prerequisites** — feature branch exists, working tree clean, dependencies ready
3. **Read Plan STATUS to compose initial phase progress** — before dispatching, read the plan issue body to determine which phases (if any) are already marked complete. Compose the initial `phase_progress` for the dispatch context:
   - If no phases are complete yet: `completed_phases: "No phases completed yet. This is the first phase."`, `concern_boundaries_crossed: ""`, `verification_evidence: ""`
   - If prior phases are complete: list them by concern name using the concern boundary annotations in the plan body, note any transitions between concerns, and summarize verification outcomes from the plan STATUS markers
4. **Dispatch to divide-and-conquer:**

```
/skill divide-and-conquer --task assemble-batch
```

When dispatching, the `executing-plans` skill passes `phase_progress` alongside `plan_issue`, `spec_issue`, `GIT_OWNER`, `GIT_REPO`, and `WORKTREE_PATH`. The `assemble-batch` task then maintains and extends phase progress as each sub-agent completes, feeding it forward into subsequent dispatch contexts.

The phase progress information comes from two sources:
- The Plan STATUS marker (which phases are marked complete with ☑)
- Concern boundary annotations in the plan body (prose descriptions of architectural concern transitions)

Phase progress is prose-driven — the orchestrating agent describes progress in natural prose. The requirement is that the information travels, not that it follows a rigid schema.

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