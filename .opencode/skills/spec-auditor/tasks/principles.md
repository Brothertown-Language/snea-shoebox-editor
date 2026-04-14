# Task: principles

## Purpose

Check document content against applicable engineering principles from the `programming-principles` skill. Identifies violations of SRP, SoC, YAGNI, KISS, Coupling, Blast Radius, Testability, and other principles where spec design decisions conflict with established design judgment.

## Checks

| Check | Problem Class | Description |
|-------|---------------|-------------|
| Single Responsibility | SRP_VIOLATION | Phase, step, or module with multiple reasons to change |
| Separation of Concerns | SOC_VIOLATION | Mixed concerns in a single phase or step |
| YAGNI | YAGNI_VIOLATION | Features, abstractions, or configuration without current requirement |
| KISS | KISS_VIOLATION | Unnecessarily complex approach when simpler solution exists |
| Coupling | COUPLING_VIOLATION | Tight coupling between phases or steps that should be independent |
| Blast Radius | BLAST_RADIUS_VIOLATION | Change scope wider than necessary; failure isolation absent |
| Testability | TESTABILITY_VIOLATION | Design that makes testing difficult without explicit tradeoff note |
| General principle violation | PRINCIPLE_VIOLATION | Any of the 20 principles violated without documented tradeoff note (fallback) |

## Procedure

1. Read the document from issue, file, or URL source
2. Determine which of the 20 principles from `programming-principles` skill apply to this document type and content
3. Load `/skill programming-principles --task principles` for full reference definitions
4. For each applicable principle, check whether the spec's design decisions align or conflict:
   - SRP: Does any phase/step have multiple responsibilities? Does any module description handle more than one concern?
   - SoC: Are concerns properly isolated across phases? Does any phase mix UI, business logic, and data access?
   - YAGNI: Are there phases/steps for features not in the requirements? Are there abstractions with only one current implementation?
   - KISS: Is there an unnecessarily complex approach where a simpler one suffices? Are there over-engineered solutions?
   - Coupling: Are phase dependencies minimal? Do phases reference internals of other phases?
   - Blast Radius: Are failure domains isolated? Can changes/deployments be made independently?
   - Testability: Can the described design be tested? Does it require extensive mocking or setup?
   - Other principles: Apply when relevant to the specific domain
5. For each violation found, check whether a tradeoff note documenting the relaxation exists
6. Create findings for violations without documented tradeoff notes

## Auto-Fix Classification

| Problem Class | Classification | Fix Action |
|---------------|---------------|------------|
| SRP_VIOLATION (phase rename) | auto-fix | Rename phase/step to describe the single specific responsibility |
| SOC_VIOLATION (phase split) | auto-fix | Split mixed-concern phase into separate phases per concern |
| YAGNI_VIOLATION | conditional | Remove unrequired features/abstractions after verifying no dependencies |
| KISS_VIOLATION | flag-for-review | Simplicity vs. design intent requires domain judgment |
| COUPLING_VIOLATION | flag-for-review | Decoupling strategy depends on architecture context |
| BLAST_RADIUS_VIOLATION | flag-for-review | Isolation scope depends on deployment architecture |
| TESTABILITY_VIOLATION | flag-for-review | Testability tradeoffs require understanding of project constraints |
| PRINCIPLE_VIOLATION | flag-for-review | Generic principle violation requires domain judgment |

## Report Format

```
Subtask: principles
Finding: [problem-class] - [summary]
Location: [phase/step/section where violation found]
Context: [which principle applies and why the violation matters for this spec]
Classification: [auto-fix|conditional|flag-for-review]
Fix Action: [what was done OR "flagged for review — [reason]"]
Severity: [HIGH|MEDIUM|LOW]
```

## When to Run

- All document types (baseline subtask)
- Especially relevant for specs with multiple phases, complex designs, or architecture decisions

## When to Skip

- Empty or unparseable content (None confidence)

Co-authored with AI: <AI-Name> (<model-id>)