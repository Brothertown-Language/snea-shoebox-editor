# Task: single-task-check

## Purpose

Determine if a spec is single-task (no sub-issues needed) or multi-task (requires phase-level sub-issues).

## Operating Protocol

1. **Run after pre-creation validation passes.**
2. **Run BEFORE issue creation.**

## Entry Criteria

- Spec content parsed
- Pre-creation validation passed

## Exit Criteria

- Determination made: single-task or multi-task
- If multi-task: phase list identified for sub-issue creation

## Procedure

### Step 1: Parse Spec Structure

**Read spec body and identify:**

1. Number of phases (`## Phase N:` sections)
2. Number of tasks within each phase
3. Complexity of implementation

### Step 2: Apply Single-Task Criteria

**A spec is SINGLE-TASK if ALL of these are true:**

| Criterion | Description |
|-----------|-------------|
| **One phase** | Spec has exactly one `## Phase 1:` section |
| **Implementation only** | Phase contains implementation steps, not verification/review |
| **Single concern** | All steps address ONE concern (not multiple distinct concerns) |
| **No decomposition needed** | Task can be implemented as one atomic unit |

**A spec is MULTI-TASK if ANY of these are true:**

| Criterion | Description |
|-----------|-------------|
| **Multiple phases** | Spec has `## Phase 2:`, `## Phase 3:`, etc. |
| **Mixed concern types** | Phases include implementation + verification + review |
| **Distinct concerns** | Phases address different architectural concerns |
| **Deployment independence** | Phases can be deployed separately |

### Step 3: Determine Sub-Issue Strategy

**If SINGLE-TASK:**

```
Result: SINGLE-TASK
Sub-issues: None
Next: Proceed to issue creation
```

**If MULTI-TASK:**

```
Result: MULTI-TASK
Phases:
  - Phase 1: [Title]
  - Phase 2: [Title]
  - ...
Sub-issues needed: YES
Next: Create sub-issues in post-creation
```

### Step 4: Report Determination

**Output:**

```markdown
**Spec Analysis:**

- Type: {single-task|multi-task}
- Phases: {count}
- Sub-issues needed: {yes|no}

{If multi-task, list phase titles for sub-issue creation}
```

## Edge Cases

### Edge Case 1: One Phase with Review Steps

**Spec:**
```
## Phase 1: Implementation (Gated)
1. Implement feature
2. Write tests
3. Code review
```

**Analysis:**
- Single phase → Could be single-task
- BUT: includes review steps → Multiple concerns

**Determination:** MULTI-TASK (verification concern separate from implementation)

### Edge Case 2: Two Phases, Same Concern

**Spec:**
```
## Phase 1: Database Schema (Gated)
## Phase 2: Database Schema Tests (Auto-progress)
```

**Analysis:**
- Two phases
- Same concern (database schema)
- Second is verification of first

**Determination:** MULTI-TASK (verification is separate concern)

### Edge Case 3: Large Single Phase

**Spec:**
```
## Phase 1: Add Rate Limiting (Gated)
1. Implement rate limiter
2. Add configuration
3. Test rate limiting
```

**Analysis:**
- Single phase
- All steps for ONE feature
- No verification phase

**Determination:** SINGLE-TASK

## Safety Checks

Before proceeding, verify ALL:

- Spec structure correctly parsed
- Phase count accurate
- Concern boundaries identified

**If ambiguous → Default to MULTI-TASK (safer).**

## Context Required

- Related tasks: `pre-creation` (runs first), `creation` (uses determination)