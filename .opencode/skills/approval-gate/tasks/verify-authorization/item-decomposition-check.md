# Task: verify-authorization — Step 4.5: Verify Item Decomposition

## Purpose

Before implementation proceeds, verify that the plan includes item-level decomposition as required by `091-incremental-build.md`. This gate applies to ALL scopes (GREENFIELD, NEW_FEATURE, FIX, ENHANCEMENT) and ALL authorization types.

## Verification Checks

1. **Item enumeration exists** — The plan lists every implementation unit as a discrete item with name, scope, and deliverable
2. **Dependency ordering exists** — Items are ordered so that each item's dependencies are satisfied by preceding items
3. **Acceptance criteria per item** — Each item has testable acceptance criteria that can be verified independently

## Procedure

```
plan_issue = github_issue_read(method="get", issue_number=plan_number)
plan_body = plan_issue["body"]

# Check for item enumeration
has_items = "Item" in plan_body and ("Dependencies" in plan_body or "Acceptance Criteria" in plan_body)

# Check for TDD step structure
has_tdd_steps = "RED" in plan_body and "GREEN" in plan_body and "COMMIT" in plan_body

if not has_items:
    # STRUCTURE-VIOLATION: No item decomposition found
    finding = "Plan lacks item decomposition — no item enumeration found"
    action = "BLOCK implementation; require plan revision with top-down item decomposition"
    severity = "STRUCTURE-VIOLATION"

if not has_tdd_steps:
    # STRUCTURE-VIOLATION: No TDD cycle defined
    finding = "Plan lacks TDD cycle definition — no RED/GREEN/COMMIT steps found"
    action = "BLOCK implementation; require plan revision with per-item TDD steps"
    severity = "STRUCTURE-VIOLATION"

# If both checks pass, proceed to Step 5
```

## Exemption

Single-task plans (0 or 1 phases) are exempt from the item decomposition check. The check applies ONLY to multi-task plans with more than one phase.

## Cross-Reference

See `091-incremental-build.md` for the complete discipline rules, scope classification, and per-item TDD cycle. See `091-incremental-build.md` → "Enforcement Mechanism" section for RED phase verification requirements, execution checkpoint references, and plan template checkpoint references.