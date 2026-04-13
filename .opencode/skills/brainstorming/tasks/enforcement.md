# Task: enforcement

Enforcement rules and messages for the brainstorming skill. Ensures brainstorming is not skipped before spec creation.

## What Skills MUST Check

1. **Before spec creation:**

   - Has exploration been invoked?
   - Is exploration output present?
   - Has problem understanding been explored?

2. **Enforcement matrix:**

   - Exploration NOT invoked → INVOKE brainstorming
   - Exploration invoked but incomplete (missing problem understanding) → COMPLETE exploration
   - Exploration complete → PROCEED to spec creation

3. **What does NOT bypass exploration:**

   - "skip brainstorming" → NOT allowed
   - "I already know what I want" → Still require brief exploration (problem understanding at minimum)
   - User impatience → Document partial exploration, ask to proceed

## Enforcement Messages

**Missing exploration:**

```
Exploration required before spec creation.

This ensures thorough requirements investigation before planning.

To invoke: Say '/skill brainstorming' or describe your feature to start exploration.
```

**Incomplete exploration:**

```
Exploration incomplete. Problem understanding must be explored at minimum.

Please complete exploration before proceeding to spec creation.
```

## Investigation Completion Criteria

Before creating a spec, investigation MUST be complete. This is a hard gate, not optional.

| Requirement | Evidence |
| -- | -- |
| Problem understood | Clearly stated problem, context, stakeholders |
| Codebase explored | Existing patterns, reusable components identified |
| Alternatives considered | At least 2 approaches for significant decisions |
| Risks identified | Risk assessment with mitigation strategies |
| Success criteria defined | Testable, measurable completion criteria |

### Permissible Investigation Activities

| Activity | Allowed? | Notes |
| -- | -- | -- |
| Read production code | YES | Read-only exploration |
| Read production data | YES | Read-only analysis |
| Create test scripts in `./tmp/` | YES | Isolated from production |
| Run test scripts in `./tmp/` | YES | No production impact |
| Run static analysis | YES | Code verification |
| Modify production code | NO | Requires approved spec |
| Modify production data | NO | Requires approved spec |
| Run code against production DB | NO | Requires explicit user authorization |
