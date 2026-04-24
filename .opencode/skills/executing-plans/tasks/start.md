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
5. **Step 5.5: RED Phase Verification Checkpoint — Content and Behavioral (MANDATORY)** — Before dispatching to divide-and-conquer/assemble-work, the agent MUST verify that for each TDD-marked implementation item, a RED test artifact exists. The type of RED test depends on whether the item is a rule change or a code change:

   - **For rule/guideline items** (changes to `.opencode/guidelines/*.md`, `.opencode/skills/*/SKILL.md`, `.opencode/skills/*/tasks/*.md`, critical violation text, agent behavior rules): The RED test artifact MUST be a **behavioral enforcement test** — one that sends the agent a prompt and verifies the agent does NOT follow the new rule yet (test FAILS because the rule change hasn't been made). Content-verification (grep for text presence) is SECONDARY and does NOT satisfy the behavioral RED gate for rule items. See `080-code-standards.md` → Behavioral Enforcement Tests (PRIMARY) and `091-incremental-build.md` → Behavioral Variant for Rule Items.
   - **For code items** (changes to `src/`, `test/`, Python files, notebook cells): The RED test artifact MUST be a **unit or integration test** that verifies the implementation behavior before the change exists. Standard TDD RED phase applies.

   - **5a.** For each item in the plan that requires implementation (not documentation-only), confirm that an enforcement test exists in `.opencode/tests/test-enforcement.sh` or `.opencode/tests/behaviors/` that corresponds to that item's change.
   - **5b.** For rule/guideline items: confirm the enforcement test is a **behavioral test** (uses `.opencode/tests/behaviors/helpers.sh` assertion helpers like `assert_tool_calls_made`, `assert_forbidden_pattern_absent`, `assert_required_pattern_present`). For code items: confirm the test is a unit/integration test that exercises the changed functionality.
   - **5c.** Confirm the enforcement test has been run and produced a FAILURE result (RED state) — the test must fail because the implementation change does not yet exist.
   - **5d.** If no RED test artifact exists for a TDD-marked item, or if a rule item only has a content-verification test (grep pattern) without a behavioral test, the agent MUST HALT and require the behavioral RED phase to be completed before proceeding. Content-verification alone does NOT satisfy the RED gate for rule changes per `080-code-standards.md` → Behavioral Enforcement Tests (PRIMARY).
   - **5e.** Tool-call artifact REQUIRED: The agent must produce a tool-call artifact (e.g., `grep` or `bash` command output) proving that the RED test check was performed, showing the test exists and was verified to be in RED state.

   This checkpoint enforces the per-item TDD cycle mandated by `091-incremental-build.md`. For rule items, it enforces the behavioral TDD variant — behavioral tests must exist and be in RED state before implementation begins. Content-verification tests are secondary for rule changes. Skipping this checkpoint is a critical violation per `000-critical-rules.md`.

#### Step 5.5a — Verify Behavioral Enforcement Test Files Exist (Missing-Test Recovery)

**5.5a.** Before dispatching, verify behavioral enforcement test files exist for each TDD-marked item. If absent, create them from the spec's Success Criteria test mandate. If present, run them and confirm they fail (RED). If they pass, HALT.

This makes the implementation phase resilient to branch switching, worktree recreation, and developer context-switching.

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