# Task: principles

## Purpose

Check document content against applicable engineering principles from the `programming-principles` skill. Determines which of the 20 principles apply to the document and reports violations using principle-specific problem classes.

**Delegated from:** spec-auditor orchestrator. Runs as a baseline subtask for ALL document types.

## Checks

| Check | Problem Class | Description |
|-------|---------------|-------------|
| SRP violations | SRP_VIOLATION | Phases, steps, or sections handling multiple responsibilities |
| SoC violations | SOC_VIOLATION | Concerns mixed within a single phase or section |
| YAGNI violations | YAGNI_VIOLATION | Scope includes features, abstractions, or configurations not required by the objective |
| KISS violations | KISS_VIOLATION | Overly complex approach when simpler alternatives exist |
| Cohesion/coupling issues | COUPLING_VIOLATION | Phases/steps have high coupling or low cohesion |
| Blast radius concerns | BLAST_RADIUS_VIOLATION | Changes with unnecessarily wide impact scope |
| Testability concerns | TESTABILITY_VIOLATION | Design that makes testing unnecessarily difficult |
| Generic fallback | PRINCIPLE_VIOLATION | Principle violation not mapping to a specific class |

## Procedure

1. Read the document from issue, file, or URL source
2. Load `programming-principles --task principles` for full principle definitions
3. Load `programming-principles --task application-guide` for context-prioritization guidance
4. Determine which of the 20 principles apply to the document:
   - Default: all 20 principles
   - Narrow when content clearly doesn't warrant some (e.g., pure data model spec doesn't need concurrency principle checks)
5. For each applicable principle, check the document for violations:
   - SRP: Look for phases/steps/sections handling multiple responsibilities
   - SoC: Look for mixed concerns within a single phase or section
   - YAGNI: Look for features, abstractions, or configurations beyond the stated objective
   - KISS: Look for overly complex approaches when simpler alternatives exist
   - Cohesion/Coupling: Look for phases/steps with high coupling or low cohesion
   - Blast Radius: Look for changes with unnecessarily wide impact scope
   - Testability: Look for designs that make testing unnecessarily difficult
   - Other principles: Apply per their definitions in `programming-principles --task principles`
6. Report each violation as a separate finding with principle-specific problem class
7. If a violation doesn't map to a specific principle, use `PRINCIPLE_VIOLATION` as fallback
8. If `programming-principles` skill is unavailable, skip this subtask and note in executive summary

## Report Format

```
Subtask: principles
Finding: [SRP_VIOLATION|SOC_VIOLATION|YAGNI_VIOLATION|KISS_VIOLATION|COUPLING_VIOLATION|BLAST_RADIUS_VIOLATION|TESTABILITY_VIOLATION|PRINCIPLE_VIOLATION] - [summary]
Location: [section of document]
Context: [which principle is violated and why it matters for this document]
Classification: [auto-fix|conditional|flag-for-review]
Fix Action: [what was done OR "flagged for review — [reason]"]
Severity: [HIGH|MEDIUM|LOW]
```

## Auto-Fix Classification

| Problem Class | Classification | Fix Action |
|---------------|---------------|------------|
| YAGNI_VIOLATION | conditional | Remove out-of-scope features/abstractions after verifying no dependencies break |
| SRP_VIOLATION (phase rename) | auto-fix | Rename generic phase names to describe specific single concerns |
| SOC_VIOLATION (phase split) | auto-fix | Flag mixed-concern phases for splitting where concern boundaries are clear |
| KISS_VIOLATION | flag-for-review | Simpler alternative exists but requires understanding intent |
| COUPLING_VIOLATION | flag-for-review | Coupling tradeoffs require domain judgment |
| BLAST_RADIUS_VIOLATION | flag-for-review | Impact analysis requires domain context |
| TESTABILITY_VIOLATION | flag-for-review | Testability concerns require design intent understanding |
| PRINCIPLE_VIOLATION | flag-for-review | Generic violations need human judgment |

## When to Run

- ALL document types (baseline subtask)
- Even simple documents benefit from surface-level principle checks

## When to Skip

- `programming-principles` skill is unavailable (note in executive summary)

## Overlap with `concerns` Subtask

The `concerns` subtask and `principles` subtask may produce overlapping findings (e.g., both flag a mixed-concern phase). This is intentional:
- `concerns` provides structural context (deployment independence, risk profile, blast radius)
- `principles` provides principle-specific context (which principle is violated, design tradeoff)

Both findings should be reported. An agent can correlate findings from two separate reports.

Co-authored with AI: <AgentName> (<ModelId>)