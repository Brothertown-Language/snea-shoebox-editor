# Task: retroactive

## Purpose

Create a plan for an existing spec that does not yet have one.

## Procedure

1. **Query existing spec:**

    - Get spec from GitHub Issue
    - Search for linked plans (GitHub Issues with `plan` label and body text matching `Spec: #N`)

2. **If no plan exists:**

    - Create `[PLAN]` GitHub Issue with `plan` + `needs-approval` labels
    - Include spec reference as prose in body (e.g., `Spec: #N`)
    - Plan content uses hybrid approach (phases + TDD steps)
    - Include header, file structure, self-review
    - Create sub-issues under the plan (not the spec)
    - HALT and wait for plan approval

3. **If plan exists:**

    - Validate plan (check for placeholders, TDD structure)
    - If invalid → Report issues
    - If valid → Proceed to implementation

## Live Verification: Retroactive Plan Evidence (MANDATORY)

**Each factual claim about existing specs and plans MUST be verified via tool call. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Spec #N exists" | Verify issue exists and has spec label | `github_issue_read(method="get", issue_number=N)` | MISSING-ELEMENT |
| "No plan exists for spec #N" | Query for linked plans | `github_search_issues(query="label:plan Spec: #N")` or iterate recent issues | VERIFICATION-GAP |
| "Plan is valid" | Run `validate` task checks | `validate` task inline | VERIFICATION-GAP |
| "Plan has sub-issues" | Check sub-issue state | `github_issue_read(method="get_sub_issues", issue_number=plan_number)` | MISSING-ELEMENT |

**Evidence artifact:** Tool call results confirming spec exists, plan state, and validation outcome.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Spec not found | MISSING-ELEMENT | flag-for-review | HALT — cannot create plan for missing spec |
| Plan actually exists (missed) | VERIFICATION-GAP | auto-fix | Use existing plan instead of creating duplicate |
| Plan invalid | VERIFICATION-GAP | flag-for-review | Report issues, do not proceed to implementation |
| Spec not approved | CONFLICTING | flag-for-review | HALT — plan requires approved spec |
