# Task: assess

## Purpose

Pre-flight context-fit assessment. Determine whether a task can be implemented directly by the current agent or must be decomposed into sub-tasks dispatched to sub-agents.

## Entry Criteria

- A non-trivial task is about to begin
- The agent has NOT yet started implementation

## Exit Criteria

- Assessment outcome is documented: IMPLEMENT_DIRECTLY or DECOMPOSE
- Assessment reasoning is captured for traceability

## Procedure

### Step 1: Evaluate Context Fitness

The agent holistically evaluates whether it can hold all needed context in working memory. Consider:

- **Scope of work**: How many spec requirements must be satisfied?
- **Number of files**: How many source files need modification or creation?
- **Complexity of changes**: Are the changes localized or cross-cutting? Do they involve deep call chains, type hierarchies, or multi-module coordination?
- **Context dependencies**: Does the work require holding large API surfaces, complex data structures, or extensive cross-references in mind simultaneously?
- **Spec density**: Is the spec concise or does it contain extensive detail, edge cases, and multi-phase requirements?

**No hardcoded thresholds.** A 5-file change may be trivial if all edits are obvious and independent. A 2-file change may require decomposition if the logic is deeply interleaved and requires holding complex state transitions in mind.

### Step 2: Determine Outcome

| Signal | IMPLEMENT_DIRECTLY | DECOMPOSE |
| -- | -- | -- |
| Files affected | 1-2, localized | 3+, cross-cutting |
| Spec requirements | 1-2, simple | 3+, with dependencies |
| Change complexity | Obvious, pattern-following | Novel, requires design reasoning |
| Context load | All needed context fits comfortably | Agent feels "dense" or risks losing track |
| Dependencies | None or shallow | Deep call chains, type hierarchies |

### Step 3: Document Assessment

Produce a structured assessment:

```yaml
assessment:
  task: "<task description>"
  outcome: IMPLEMENT_DIRECTLY | DECOMPOSE
  reasoning: "<1-3 sentences explaining the judgment>"
  files_estimated: <N>
  spec_requirements: <N>
  complexity: trivial | moderate | complex
  depth: 0
```

### Trivial Exception

Single-file, obvious fixes skip assessment entirely:
- Typo fixes
- One-line config edits
- Obvious single-function corrections
- Comment-only changes

When in doubt, assess. The cost of a false DECOMPOSE is low (minor overhead). The cost of a false IMPLEMENT_DIRECTLY can be context overflow and incomplete work.

## Edge Cases

### Assessment Says IMPLEMENT_DIRECTLY but Work Grows

If during implementation the scope expands beyond what was assessed:
1. STOP
2. Re-assess with the new scope information
3. If DECOMPOSE: discard in-progress direct work, switch to decomposition
4. If still IMPLEMENT_DIRECTLY: continue but re-evaluate at next scope expansion

### Assessment Says DECOMPOSE for a Simple Task

A conservative assessment (DECOMPOSE for work that could be done directly) is acceptable. The decomposition overhead is small compared to the risk of overflow. Do not second-guess a DECOMPOSE decision.