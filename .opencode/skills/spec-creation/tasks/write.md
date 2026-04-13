# Task: write

## Purpose

Assemble the final spec with acceptance criteria, ambiguity elimination, and deliverable structure. Includes self-review and user-review steps adapted from brainstorming Steps 7-9, extended with principles #4, #6, #10.

## Entry Criteria

- Requirements extraction completed (mandatory)
- Other prerequisite tasks completed or explicitly skipped via simplicity heuristic

## Exit Criteria

- GitHub Issue created with `[SPEC]` prefix and `needs-approval` label
- Self-review completed (placeholder scan, consistency, scope, ambiguity)
- Chat output is ONLY: `<exec summary>` + `<issue URL>` + `<byline>` (no full spec dump)
- User reviews spec ON THE ISSUE (not in chat)
- Ready for spec-auditor and approval-gate

## Procedure

### Step 1: Assemble Spec

Combine outputs from prerequisite tasks into a structured spec:
- Overview and goals (from requirements)
- Non-goals (from non-requirements)
- Architecture and interfaces (from decompose)
- Success criteria (acceptance criteria with binary pass/fail)
- Edge cases and error handling (from risk)
- Traceability references (from traceability)

### Step 2: Eliminate Ambiguity (Principle #4)

Review every requirement statement:
- Replace vague terms with measurable, testable statements
- Replace "should" with "MUST", "SHALL", or "MAY"
- Replace "fast" with specific thresholds
- Replace "user-friendly" with specific UX criteria
- Every "etc." must become an explicit list

### Step 3: Define Acceptance Criteria (Principle #6)

For each feature/requirement:
- Binary pass/fail criteria (NOT subjective)
- Edge case coverage
- Negative test cases (what must NOT happen)
- Integration test expectations

### Step 4: Structure the Deliverable (Principle #10)

Spec sections (adapt to spec complexity):

1. **Overview** — Problem statement and context
2. **Goals** — What this spec achieves
3. **Non-Goals** — What is explicitly out of scope
4. **Success Criteria** — Testable, binary pass/fail
5. **Architecture** — Components, interfaces, data flow
6. **Interfaces** — API contracts, data schemas, boundaries
7. **Data Models** — Schemas, migrations, constraints
8. **Edge Cases** — Error handling, failure modes, limits
9. **Acceptance Criteria** — Per-feature binary tests
10. **Risk Assessment** — High-risk areas, mitigation
11. **Operational Requirements** — Logging, metrics, deployment
12. **Rollout Plan** — Deployment strategy, rollback

Skip sections that don't apply (e.g., no data models for a guideline-only change).

### Step 5: Self-Review

After writing the spec, review with fresh eyes:

1. **Placeholder scan:** Any "TBD", "TODO", incomplete sections, or vague requirements? Fix them.
2. **Internal consistency:** Do any sections contradict each other? Does the architecture match the feature descriptions?
3. **Scope check:** Is this focused enough for a single implementation plan, or does it need decomposition?
4. **Ambiguity check:** Could any requirement be interpreted two different ways? If so, pick one and make it explicit.

Fix any issues inline. No need to re-review — just fix and move on.

### Step 6: Create GitHub Issue

Invoke `github-issue-creation` skill to persist the spec as a GitHub Issue:

1. Invoke `github-issue-creation --task pre-creation` to validate (check for conflicts, superseded issues, missing sections)
2. If validation fails → HALT and report. Fix issues and re-validate.
3. If validation passes → invoke `github-issue-creation --task single-task-check` to determine sub-issue needs
4. Invoke `github-issue-creation --task creation` to create the GitHub Issue
5. Record the issue number and URL

**Chat output is ONLY:**

```
<exec summary>

<issue URL>

🤖 <AgentName> (<ModelID>) ✨
```

**🚫 NEVER:**
- Dump full spec content to chat as the "review" step
- Claim spec is "written" without a GitHub Issue URL
- Ask the user to review the spec in chat

### Step 7: User Review on Issue

The user reviews the spec ON THE GITHUB ISSUE, not in chat.

- If user requests revisions via issue comments: update the issue body, then post update summary + URL + byline to chat
- If user approves the spec on the issue: proceed to Step 8
- Do NOT re-dump the spec to chat for any reason

### Step 8: Transition

After user approval of the spec on the GitHub Issue:
- Invoke `spec-auditor` for quality audit
- Then proceed to `approval-gate` for authorization
- Then `writing-plans` for implementation planning

## Context Required

- Preceded by: `requirements` (mandatory), `decompose`, `traceability`, `risk` (or explicitly skipped)
- Extends: brainstorming Steps 7-9 (adapted, not verbatim move)
- Calls: `github-issue-creation` (pre-creation → single-task-check → creation)
- Followed by: `spec-auditor`, then `approval-gate`