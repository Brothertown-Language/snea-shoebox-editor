# Task: traceability

## Purpose

Check for orphan requirements (requirements with no implementation steps) and orphan features (implementation steps with no stated requirement). New in v2.

## Checks

| Check | Problem Class | Description |
|-------|---------------|-------------|
| Orphan requirements | MISSING-TRACEABILITY | Requirements/spec objectives that have no corresponding implementation steps |
| Orphan features | MISSING-TRACEABILITY | Implementation steps that don't trace back to any stated requirement or objective |
| Missing success criteria | VERIFICATION-GAP | Objectives without measurable success criteria |

## Procedure

1. Read the spec issue via GitHub MCP
2. Extract all stated requirements and objectives from the Objective, Problem Statement, and Success Criteria sections
3. Extract all implementation steps from the phases
4. For each requirement, verify it has at least one implementation step addressing it
5. For each implementation step, verify it traces back to at least one stated requirement
6. Flag any orphan requirements (no steps address them) or orphan features (no requirement justifies them)
7. Check that success criteria are measurable and testable

## Why This Matters

Orphan requirements mean something was promised but not planned for implementation. Orphan features mean something is being implemented that wasn't asked for — either scope creep or missing context. Both indicate a gap in the spec's internal consistency.

## Report Format

```
Subtask: traceability
Finding: MISSING-TRACEABILITY - [orphan requirement/orphan feature description]
Location: [section of spec]
Context: [what requirement is unaddressed OR what feature is unjustified]
Recommendation: [add implementation steps OR add requirement justification]
Severity: [HIGH|MEDIUM|LOW]
```

## When to Run

- Feature specs with multiple requirements
- Specs with multiple phases or steps
- Complex specs where traceability gaps are likely

## When to Skip

- Simple bug fix specs with one requirement and one step
- Specs with obvious 1:1 requirement-to-step mapping

Co-authored with AI: OpenCode (ollama-cloud/glm-5)