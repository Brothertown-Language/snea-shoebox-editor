# Task: traceability

## Purpose

Map every requirement to spec section, test, and implementation step. Ensure nothing is lost between requirements and implementation.

## Entry Criteria

- Requirements extraction completed
- (Optional) Decomposition completed

## Exit Criteria

- Every requirement maps to at least one spec section
- Every spec section maps to at least one requirement
- Test scenarios identified for each requirement
- Implementation steps traceable to requirements

## Procedure

### Step 1: Build Traceability Matrix

Map each requirement ID to:

| Requirement | Spec Section | Test Scenario | Implementation Step |
|-------------|-------------|---------------|---------------------|
| [R1] | Section X | Test case Y | Step Z |

### Step 2: Verify Bidirectional Coverage

- **Forward:** Every requirement → spec section (nothing lost)
- **Backward:** Every spec section → requirement (no scope creep)
- **Test coverage:** Every requirement → at least one test scenario
- **Implementation coverage:** Every requirement → at least one implementation step

### Step 3: Identify Gaps

- Requirements without spec sections (lost requirements)
- Spec sections without requirements (scope creep)
- Requirements without test scenarios (untestable)
- Requirements without implementation steps (orphan)

## Output Format

```
## Traceability Matrix

| Req ID | Spec Section | Test | Implementation |
|--------|-------------|------|----------------|
| [R1]   | §2.1        | T1   | Step 3         |
| [R2]   | §2.2        | T2   | Step 4         |

### Gaps
- <any missing mappings>
```

## Context Required

- Preceded by: `requirements`, optionally `decompose`
- Feeds into: `write`
- Note: Creation-time traceability is enforced here. `spec-auditor` verifies traceability as a second pass.