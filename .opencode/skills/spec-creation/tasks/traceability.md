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

### Step 1: Build Traceability

Map each requirement to:
- Which spec section covers it
- What test scenario validates it
- Which implementation step implements it

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

## Content Coverage

Can each requirement be traced to a spec section, test scenario, and implementation step? Does the traceability provide bidirectional coverage?

- **Forward traceability:** Every requirement → spec section and test
- **Backward traceability:** Every spec section → requirement

**Any format that provides this coverage is acceptable.** A formal traceability matrix table works well for complex specs. A prose list or inline references work well for simple specs. The agent chooses the format that best serves the spec.

## Context Required

- Preceded by: `requirements`, optionally `decompose`
- Feeds into: `write`
- Note: Creation-time traceability is enforced here. `spec-auditor` verifies traceability as a second pass.