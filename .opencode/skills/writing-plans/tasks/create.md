# Task: create

## Purpose

Create an implementation plan from an approved spec.

## Prerequisites

1. Approved spec (verified by approval-gate)
2. Spec stored as GitHub Issue
3. Spec has explicit approval (`approved` or `go`)

## Creation Steps

1. **Read approved spec:**

   - Query GitHub Issue for spec content
   - Extract objectives, constraints, success criteria
   - Identify affected files and dependencies

2. **Map file structure:**

   - List all files that will be created or modified
   - Define each file's responsibility
   - Ensure decomposition has clear boundaries

3. **Plan phase structure by judgment:**

   - Determine which phases the plan needs
   - Organize by concern flow, not template order
   - Write prose for phase descriptions

4. **Define tasks within each phase:**

   - Each task uses the TDD step structure
   - Each step is one action (2-5 minutes)
   - Exact code, exact commands, exact file paths

5. **Write plan document header:**

   - Goal, Architecture, Tech Stack

6. **Create plan issue:**

    - Title: `[PLAN] <Feature Name>`
    - Labels: `plan` + `needs-approval`
    - Body: Spec reference as prose (e.g., `Spec: #784`), then plan with header, file structure, phases with TDD tasks
    - Do NOT link plan as sub-issue of spec — the plan references the spec via body text only

    After plan issue is created, create sub-issues under the plan (not the spec) for each phase via `github-sub-issues --task create-sub-issue`.

7. **Self-review:**

   - Spec coverage check
   - Placeholder scan
   - Type consistency check
   - Fix any issues found

8. **Validate plan:**

   - Check for TBD/TODO placeholders
   - Verify all steps are actionable
   - Verify success criteria are testable

9. **Report plan creation in chat (MANDATORY):**

   Produce chat output in the mandatory format per `000-critical-rules.md`:

    1. **Executive summary**: 1-2 sentences describing what plan was created and for which spec
    2. **URL**: The plan issue URL (e.g., `https://github.com/<GIT_OWNER>/<GIT_REPO>/issues/<N>`)
    3. **AI byline**: `🤖 <AgentName> (<ModelID>)` — ALWAYS LAST

    Example:

    Created implementation plan for #771 (branch stacking prerequisite). 7 tasks across 6 files (3 skills + 3 guidelines).
    https://github.com/<GIT_OWNER>/<GIT_REPO>/issues/772
    🤖 <AgentName> (<ModelID>)

    Sub-issues are linked under the plan issue, NOT under the spec.
