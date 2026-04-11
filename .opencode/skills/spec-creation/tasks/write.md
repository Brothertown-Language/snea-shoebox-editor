# Task: write

## Purpose

Assemble the final spec with acceptance criteria, ambiguity elimination, and deliverable structure. Includes self-review and user-review steps adapted from brainstorming Steps 7-9, extended with principles #4, #6, #10.

## Entry Criteria

- Requirements extraction completed (mandatory)
- Other prerequisite tasks completed or explicitly skipped via simplicity heuristic

## Exit Criteria

- Spec written as GitHub Issue
- Self-review completed (placeholder scan, consistency, scope, ambiguity)
- User review requested
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

### Step 6: User Review

Ask the user to review the written spec:

> "Spec written. Please review it and let me know if you want to make any changes before we proceed to audit and approval."

Wait for the user's response. If they request changes, make them and re-run the self-review. Only proceed once the user approves.

### Step 7: Transition

After user approval of the spec:
- Invoke `spec-auditor` for quality audit
- Then proceed to `approval-gate` for authorization
- Then `writing-plans` for implementation planning

## Context Required

- Preceded by: `requirements` (mandatory), `decompose`, `traceability`, `risk` (or explicitly skipped)
- Extends: brainstorming Steps 7-9 (adapted, not verbatim move)
- Followed by: `spec-auditor`, then `approval-gate`