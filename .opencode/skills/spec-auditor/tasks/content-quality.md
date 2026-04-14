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
| Plan bleed | PLAN-BLEED | Does the spec contain implementation details (code, DDL, algorithms) that belong in the plan? |

## Procedure

1. Read the spec issue via GitHub MCP
2. Check that architectural decisions explain WHY, alternatives considered, and constraints
3. Identify ambiguous language that an LLM might implement inconsistently
4. Find internal contradictions between spec sections
5. Verify all changes align with the stated objective
6. Check that success criteria are testable and measurable
7. Verify dependencies have specific integration points
8. Check comment format uses executive summary with byline at bottom
9. Check for plan-bleed: content that prescribes HOW instead of WHAT

**Plan-bleed detection signals:**

| Signal | Plan-Level Content | Replace With |
|--------|--------------------|--------------|
| Code blocks with `def`, `class`, or function bodies | Implementation code | Function names + responsibilities table |
| SQL DDL (`CREATE TABLE`, `ALTER TABLE`) | Database implementation | Table names + constraints table |
| Step-by-step algorithms with imperative logic | Implementation procedure | Input/output contract |
| File paths with "add", "modify", "create" language | File-level instructions | Affected files + anchors table |
| Architecture decisions without "MUST" constraints | Design choices | Architecture requirements table |

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
Finding: [ARCHITECTURAL-REASONING-GAP|AMBIGUOUS|CONFLICTING|SCOPE-CREEP-RISK|VERIFICATION-GAP|DEPENDENCY-INCOMPLETE|COMMENT-FORMAT-VIOLATION|SUPERSEDED-CLOSURE-VIOLATION|PLAN-BLEED] - [summary]
Location: [section of spec]
Context: [why this matters for implementability]
Classification: [auto-fix|conditional|flag-for-review]
Fix Action: [what was done OR "flagged for review — [reason]"]
Severity: [HIGH|MEDIUM|LOW]
```

## Auto-Fix Classification

| Problem Class | Classification | Fix Action |
|---------------|---------------|------------|
| DEPENDENCY-INCOMPLETE | auto-fix | Add specific integration points |
| SCOPE-CREEP-RISK | conditional | Remove scope-creep steps after verifying no orphan dependencies |
| AMBIGUOUS | flag-for-review | Ambiguity requires domain context to resolve |
| CONFLICTING | flag-for-review | Contradictions require understanding intent |
| VERIFICATION-GAP | flag-for-review | Success criteria require domain expertise |
| COMMENT-FORMAT-VIOLATION | flag-for-review | May be intentional formatting |
| SUPERSEDED-CLOSURE-VIOLATION | flag-for-review | May reference valid future work |
| ARCHITECTURAL-REASONING-GAP | flag-for-review | Requires understanding design tradeoffs |
| PLAN-BLEED | auto-fix | Replace code/DDL/algorithms with requirements tables; note moved content for plan |

Co-authored with AI: <AI-Name> (<model-id>)