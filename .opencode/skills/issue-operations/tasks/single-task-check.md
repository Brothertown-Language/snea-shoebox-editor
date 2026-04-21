# Task: single-task-check

## Purpose

Determine if a spec is single-task (plan optional) or multi-task (requires plan issue with phase-level sub-issues).

## Operating Protocol

1. **Run after pre-creation validation passes.**
2. **Run BEFORE issue creation.**

## Entry Criteria

- Spec content parsed
- Pre-creation validation passed

## Exit Criteria

- Determination made: single-task or multi-task
- If multi-task: phase list identified for plan creation
- Plan need determination passed to post-creation
- `single_task_determination` value exported for `writing-plans` consumption

## Procedure

### Step 1: Parse Spec Structure

**Read spec body and identify:**

1. Concern boundaries — what distinct responsibilities does the spec address?
2. Whether steps mix implementation, verification, and review
3. Whether changes are localized or cross-cutting
4. Number of phases (`## Phase N:` sections) — as a signal, not the primary classifier

### Step 2: Apply Single-Task Criteria

**A spec is SINGLE-TASK if ALL of these are true:**

| Criterion | Description |
|-----------|-------------|
| **One cohesive concern** | All steps address ONE concern (not multiple distinct concerns) |
| **Implementation only** | Steps contain implementation, not verification/review |
| **Localized impact** | Changes are confined to a single area of responsibility |
| **No decomposition needed** | Task can be implemented as one atomic unit |

**A spec is MULTI-TASK if ANY of these are true:**

| Criterion | Description |
|-----------|-------------|
| **Multiple concerns** | Steps address different architectural concerns |
| **Mixed concern types** | Steps include implementation + verification + review |
| **Cross-cutting impact** | Changes span multiple areas of responsibility |
| **Deployment independence** | Parts can be deployed separately |

**Phase count is a signal, not a gate:** If the spec has multiple `## Phase N:` sections, that _suggests_ multi-task, but the agent evaluates semantic concerns to confirm. A multi-phase spec with one cohesive concern may still be single-task. A single-phase spec with mixed concerns is multi-task.

### Step 3: Determine Plan Strategy

**If SINGLE-TASK:**

```
Result: SINGLE-TASK
single_task_determination: single-task
Plan needed: Determined by writing-plans decision gate (combined or separate)
Sub-issues: None if combined; under plan if separate
Next: Pass single_task_determination to post-creation → writing-plans
```

**If MULTI-TASK:**

```
Result: MULTI-TASK
single_task_determination: multi-task
Plan needed: YES (always separate)
Phases:
  - Phase 1: [Title]
  - Phase 2: [Title]
  - ...
Sub-issues under plan: YES
Next: Pass single_task_determination to post-creation → writing-plans
```

### Step 4: Report Determination

**Output:**

```markdown
**Spec Analysis:**

- Type: {single-task|multi-task}
- Phases: {count}
- Plan needed: {yes|optional}

{If multi-task, list phase titles for plan creation}
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
- Single phase
- BUT: includes review steps → Mixed concern types (implementation + verification)

**Determination:** MULTI-TASK (verification concern separate from implementation)

### Edge Case 2: Two Phases, Same Concern

**Spec:**
```
## Phase 1: Database Schema (Gated)
## Phase 2: Database Schema Tests (Auto-progress)
```

**Analysis:**
- Two phases (signal suggests multi-task)
- Same concern (database schema)
- Second is verification of first → Mixed concern types

**Determination:** MULTI-TASK (verification is separate concern) → plan needed

### Edge Case 3: Single Cohesive Concern

**Spec:**
```
## Phase 1: Add Rate Limiting (Gated)
1. Implement rate limiter
2. Add configuration
3. Test rate limiting
```

**Analysis:**
- Single phase
- All steps for ONE feature (one cohesive concern)
- Testing is integrated, not a separate verification concern

**Determination:** SINGLE-TASK (plan optional)

### Edge Case 4: Cross-Cutting Single Phase

**Plan:**
```
## Phase 1: Update Skills (Gated)
- Update approval-gate
- Update divide-and-conquer
```

**Analysis:**
- Single phase
- Multiple files but single concern (skill update)

**Determination:** Single-phase plan — no sub-issues needed under the plan

## Safety Checks

Before proceeding, verify ALL:

- Spec structure correctly parsed
- Concern boundaries identified

**If ambiguous → Default to MULTI-TASK (safer).**

## Context Required

- Related tasks: `pre-creation` (runs first), `creation` (uses determination), `post-creation` (triggers writing-plans if multi-task)

## Live Verification: Single-Task Check Evidence (MANDATORY)

**Each determination claim MUST be verified via tool call against the actual spec body. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Spec has N phases" | Count `## Phase N:` sections in spec body | `github_issue_read(method="get", issue_number=N)` → parse body | VERIFICATION-GAP |
| "All steps address one concern" | Verify concern consistency | Manual parse — flag mixed concerns | CONFLICTING |
| "No decomposition needed" | Verify single atomic unit | Manual parse — flag decomposition needs | VERIFICATION-GAP |
| "Spec structure parsed correctly" | Verify parsing produces valid phase list | Re-parse and compare | STRUCTURE-VIOLATION |

**Evidence artifact:** Spec body parse result, phase count, concern analysis.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Phase count wrong | VERIFICATION-GAP | auto-fix | Re-parse spec body |
| Mixed concerns in single phase | CONFLICTING | flag-for-review | Classify as multi-task |
| Decomposition needed | VERIFICATION-GAP | flag-for-review | Classify as multi-task |
| Parse error | STRUCTURE-VIOLATION | conditional | Re-parse or flag ambiguous |