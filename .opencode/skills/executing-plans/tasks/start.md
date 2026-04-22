# Task: start

Dispatch to divide-and-conquer/assemble-work for implementation.

## Purpose

This task dispatches plan execution to `divide-and-conquer --task assemble-work`, which handles all implementation through the unified work workflow.

## Dispatch Procedure

1. **Verify plan approval** — confirm the plan issue has explicit approval in comments
2. **Verify prerequisites** — feature branch exists, working tree clean, dependencies ready
3. **Read Plan STATUS to compose initial phase progress** — before dispatching, read the plan issue body to determine which phases (if any) are already marked complete. Compose the initial `phase_progress` for the dispatch context:
   - If no phases are complete yet: `completed_phases: "No phases completed yet. This is the first phase."`, `concern_boundaries_crossed: ""`, `verification_evidence: ""`
   - If prior phases are complete: list them by concern name using the concern boundary annotations in the plan body, note any transitions between concerns, and summarize verification outcomes from the plan STATUS markers
4. **Check halt_at boundary** — if `halt_at == plan_created`, HALT. Do NOT dispatch to implementation. The authorization scope stops at plan creation.
5. **Step 5.5: RED Phase Verification Checkpoint** — Before dispatching to divide-and-conquer/assemble-work, the agent MUST verify that for each TDD-marked implementation item, a RED test artifact exists:

   - **5a.** For each item in the plan that requires implementation (not documentation-only), confirm that an enforcement test scenario exists in `.opencode/tests/test-enforcement.sh` that corresponds to that item's change.
   - **5b.** Confirm the enforcement test has been run and produced a FAILURE result (RED state) — the test must fail because the implementation change does not yet exist.
   - **5c.** If no RED test artifact exists for a TDD-marked item, the agent MUST HALT and require the RED phase to be completed before proceeding. The enforcement test must be written first, run, and confirmed to fail before implementation begins.
   - **5d.** Tool-call artifact REQUIRED: The agent must produce a tool-call artifact (e.g., `grep` or `bash` command output) proving that the RED test check was performed, showing the test exists and was verified to be in RED state.

   This checkpoint enforces the per-item TDD cycle mandated by `091-incremental-build.md`: enforcement tests must exist and be in RED state before implementation begins. Skipping this checkpoint is a critical violation per `000-critical-rules.md`.
6. **Dispatch to divide-and-conquer:**

```
/skill divide-and-conquer --task assemble-work
```

When dispatching, pass `authorization_scope`, `halt_at`, and `pr_strategy` alongside `plan_issue`, `spec_issue`, `<github.owner>`, `<github.repo>`, and `<worktree.path>`. The `assemble-work` task uses these fields for scope-aware dispatch boundary enforcement.

The phase progress information comes from two sources:
- The Plan STATUS marker (which phases are marked complete with ☑)
- Concern boundary annotations in the plan body (prose descriptions of architectural concern transitions)

Phase progress is prose-driven — the orchestrating agent describes progress in natural prose. The requirement is that the information travels, not that it follows a rigid schema.

The `assemble-work` task handles:

- Creating feature branches and worktrees
- Sub-agent dispatch for each implementation item
- Squash-merging feature branches into work branch
- Verification gates (verification-before-completion, finishing-a-development-branch)

**There is no single-issue bypass.** Single issue = work of one = one sub-agent.

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