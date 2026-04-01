# Planning: Spec Structure Requirements

## Spec File Format

**All specs use GitHub Issues as the authoritative source.**

For archive and closure workflow, see `124-github-archive-workflow.md`.

---

## 6. Spec Structure Requirements

### Two Workflow Stages

**Stage 1: Investigation & Planning (CRITICAL CHECKPOINT)**
- Investigation phases: **MANDATORY** research, analysis, exploration — MUST complete before spec creation
- Planning phases: design, architecture, breakdown — MUST complete before spec creation
- **These are HARD GATES — not automatic, not optional**
- **A spec cannot be finalized without completed investigation and planning**
- **NOT included in the spec file — but VERIFIED before proceeding**

#### Investigation Tools and Methods

During investigation, the agent MAY:

| Activity | Allowed? | Notes |
|----------|----------|-------|
| Read production code | ✅ YES | Read-only exploration |
| Read production data | ✅ YES | Read-only analysis |
| Create test scripts in `./tmp/` | ✅ YES | Isolated from production |
| Run test scripts in `./tmp/` | ✅ YES | No production impact |
| Create isolated test fixtures | ✅ YES | Dedicated test databases/schemas |
| Run static analysis (lint, typecheck) | ✅ YES | Code verification |
| Modify production code | 🚫 NO | Requires approved spec |
| Modify production data | 🚫 NO | Requires approved spec |
| Run code against production DB | 🚫 NO | Requires explicit user authorization |

**Test Scripts for Investigation:**

Test code created during investigation MUST:
- Be placed in `./tmp/` directory only
- Use isolated test fixtures (dedicated test DB, test schemas)
- NOT modify production code, data, or systems
- Be deleted after investigation completes (temp artifacts)

**Example Permissible Investigation:**

```python
# ✅ ALLOWED: Create test script to validate hypothesis
# File: ./tmp/test_mesh_lookup.py

from commons.mesh.validator import MeshValidator

# Use test fixture, NOT production
validator = MeshValidator(test_mode=True)
result = validator.lookup_term("coronary artery disease")
print(f"Validation result: {result}")
```

#### Investigation Completion Criteria

Before creating a spec, the agent MUST verify:

| Requirement | Evidence |
|-------------|----------|
| Problem understood | Clearly stated problem, context, stakeholders |
| Codebase explored | Existing patterns, reusable components identified |
| Hypotheses tested | Test scripts run, results documented |
| Alternatives considered | At least 2 approaches documented with tradeoffs |
| Risks identified | Risk assessment with mitigation strategies |
| Success criteria defined | Testable, measurable completion criteria |

#### 🚫 CRITICAL VIOLATION: Spec Without Investigation

Creating a spec without completed investigation is a CRITICAL GUIDELINE VIOLATION:

- **PROHIBITED**: Creating specs from vague requirements without exploration
- **PROHIBITED**: Skipping codebase analysis before planning
- **PROHIBITED**: Finalizing specs before investigating edge cases
- **PROHIBITED**: Proceeding without success criteria defined
- **PROHIBITED**: Running test code against production systems

#### ✅ ALLOWED During Investigation

- **ALLOWED**: Creating `./tmp/` test scripts to validate hypotheses
- **ALLOWED**: Running isolated test fixtures
- **ALLOWED**: Static analysis (lint, typecheck) on production code
- **ALLOWED**: Read-only exploration of production code and data
- **ALLOWED**: Documenting findings for the spec

**Stage 2: Requires Approval (In Spec)**
- Implementation phases: build, code, integrate
- Verification phases: test, review, validate
- Completion phases: ship, deploy
- **These appear in the spec with numbered phases/steps**

### Spec Template

```markdown
# Spec: [Title]

STATUS: 1.1
CREATED: YYYY-MM-DD

---

## Phase 1: [Concern Name] (Gated)

### Steps
1. ☐ [first task for this concern]
2. ☐ [second task for this concern]
3. ☐ [third task for this concern]

### Content
[Implementation details from planning phase]

---

## Phase 2: [Next Concern] (auto-progress)

### Steps
1. ☐ [first task for this concern]
2. ☐ [second task for this concern]

---

## Phase 3: [Verification Concern] (requires approval)

### Steps
1. ☐ [first review task]
2. ☐ [second review task]

---

> **Approval Tracking**: Approvals are tracked via GitHub Issue comments (e.g., `AI: <Agent> ✅ Approved: Phase 1`), NOT in the issue body. Issue body edits destroy history.

**⚠️ CRITICAL: Phase names MUST describe specific concerns, NOT generic activities.**
- ✅ Good: "Database Schema Setup", "API Endpoint Integration", "Error Handling Layer"
- ❌ Bad: "Implementation", "Testing", "Development", "Build"
```

### What NOT to Include in Specs

**DO NOT include:**
- Investigation phases (already done)
- Planning phases (already done)
- Research notes (that was investigation)
- Architecture decisions (that was planning)

The spec starts **AFTER** investigation and planning are complete.

---

## 7. Required Elements

Every spec file MUST include:

1. **Title**: `# Spec: [Feature Name]`
2. **STATUS Header**: `STATUS: phase.step` (e.g., `STATUS: 1.2`)
3. **CREATED Date**: `CREATED: YYYY-MM-DD`
4. **Numbered Phases**: Phase 1, Phase 2, Phase 3...
5. **Numbered Steps**: 1, 2, 3 within each phase
6. **Status Markers**: `☐`/`↻`/`☑`/`☒` for each step
7. **Approval Tracking Note**: A footer note directing approvals to comments (not a table in the body)

## 8. Phase Naming Quality (MANDATORY)

**Phase names MUST represent actual separation of concerns, not generic activities.**

### Boilerplate Phase Names (PROHIBITED)

Phase names that describe generic activities without specifying the concern:

- "Implementation" — activity, not concern boundary
- "Testing" — activity, not concern boundary
- "Build" / "Create" / "Develop" — activities, not concerns
- "Verify" / "Validate" / "Check" — activities, not concerns
- "Deploy" / "Ship" / "Release" — activities, not concerns

### Meaningful Phase Names (REQUIRED)

Phase names that describe specific concern boundaries:

- "Database Schema Setup" — specific concern boundary
- "API Endpoint Integration" — specific concern boundary
- "Error Handling Layer" — specific concern boundary
- "Configuration Migration" — specific concern boundary
- "Unit Testing Infrastructure" — specific concern (infrastructure for testing)
- "Integration Testing Suite" — specific concern (integration test setup)

### Validation Rules

| Pattern | Status | Reason |
|---------|--------|--------|
| Single-word activity name | BOILERPLATE-TITLE | No concern boundary specified |
| "Testing" alone | BOILERPLATE-TITLE | Generic activity |
| "Testing Infrastructure" | ACCEPTABLE | Specific concern (infrastructure) |
| "Unit Testing" | ACCEPTABLE | Specific testing type |
| "Implementation" with specific steps | REVIEW | May be acceptable if steps define concern |

### Examples

**❌ BOILERPLATE (Wrong):**
```markdown
## Phase 1: Implementation (Gated)
### Steps
1. ☐ Write the code
2. ☐ Make it work
3. ☐ Fix bugs
```

**✅ MEANINGFUL (Correct):**
```markdown
## Phase 1: Database Schema Setup (Gated)
### Steps
1. ☐ Create user table with authentication fields
2. ☐ Add indexes for login queries
3. ☐ Write migration script
```

---

*Source: Content migrated from `040-plan-delivery.md`*