# Task: content-quality

## Purpose

Check architectural reasoning, ambiguity, conflicts, and scope creep in a spec.

## Checks

| Check | Problem Class | Description |
|-------|---------------|-------------|
| Architectural reasoning | ARCHITECTURAL-REASONING-GAP | Are design decisions explained (why, alternatives, constraints)? |
| Ambiguity | AMBIGUOUS | Can any language be interpreted multiple ways by an LLM? |
| Conflicts | CONFLICTING | Do any parts of the spec contradict each other? |
| Scope discipline | SCOPE-CREEP-RISK | Do changes align with the stated objective? |
| Success criteria | VERIFICATION-GAP | Are success criteria testable with acceptance criteria? |
| Dependencies | DEPENDENCY-INCOMPLETE | Are integration points specific? |
| Comment format | COMMENT-FORMAT-VIOLATION | Does the spec use executive summary format? |
| Superseded closure | SUPERSEDED-CLOSURE-VIOLATION | Does closing language claim future action without execution? |

## Procedure

1. Read the spec issue via GitHub MCP
2. Check that architectural decisions explain WHY, alternatives considered, and constraints
3. Identify ambiguous language that an LLM might implement inconsistently
4. Find internal contradictions between spec sections
5. Verify all changes align with the stated objective
6. Check that success criteria are testable and measurable
7. Verify dependencies have specific integration points
8. Check comment format uses executive summary with byline at bottom

## Nine Core Areas (Reference)

Every spec should cover these areas (but the agent decides which are relevant):

1. **Commands** — Executable commands with flags
2. **Testing** — How to test, framework, test locations
3. **Project Structure** — Where code lives, tests go, docs belong
4. **Code Style** — Naming conventions, formatting, examples
5. **Git Workflow** — Branch naming, commit format, PR requirements
6. **Boundaries** — Three-tier (always/ask-first/never)

These are NOT mandatory sections — they're areas the agent should consider. A simple bug fix may not need all nine.

## Report Format

```
Subtask: content-quality
Finding: [ARCHITECTURAL-REASONING-GAP|AMBIGUOUS|CONFLICTING|SCOPE-CREEP-RISK|VERIFICATION-GAP|DEPENDENCY-INCOMPLETE|COMMENT-FORMAT-VIOLATION|SUPERSEDED-CLOSURE-VIOLATION] - [summary]
Location: [section of spec]
Context: [why this matters for implementability]
Recommendation: [suggested fix]
Severity: [HIGH|MEDIUM|LOW]
```

Co-authored with AI: OpenCode (ollama-cloud/glm-5)