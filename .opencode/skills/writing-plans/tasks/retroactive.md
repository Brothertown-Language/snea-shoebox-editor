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
