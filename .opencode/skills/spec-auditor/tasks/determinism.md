# Task: determinism

## Purpose

Check process flow, runbook, and SOP documents for deterministic behavior: same inputs produce same outputs, no hidden non-determinism, environment assumptions are explicit, and state dependencies are documented.

**Applicable document types:** Process Flow, Runbook/SOP

## Checks

| Check | Problem Class | Description |
|-------|---------------|-------------|
| Input/output determinism | DETERMINISM-VIOLATION | Same inputs → same outputs for every step |
| Hidden non-determinism | DETERMINISM-VIOLATION | No timestamps, random values, or external state used as decision inputs |
| Environment assumptions | DETERMINISM-VIOLATION | Environment requirements stated explicitly (OS, versions, configs) |
| State dependencies | DETERMINISM-VIOLATION | State dependencies between steps are documented |

## Procedure

1. Read the document from issue, file, or URL source
2. Confirm document type is Process Flow or Runbook/SOP (skip otherwise)
3. For each step:
   - Verify that given the same inputs, the step produces the same outputs
   - Check for use of `Date.now()`, `Math.random()`, external API responses, or current timestamps as decision inputs
   - Verify environment requirements are stated (e.g., Python 3.12, Docker 24.x)
4. For cross-step dependencies:
   - Verify state that carries between steps is explicitly documented
   - Verify no implicit state assumptions (e.g., "the file from step 2" must name the file)
5. Create findings for each violation

## Report Format

```
Subtask: determinism
Finding: DETERMINISM-VIOLATION - [summary]
Location: [step or section]
Context: [why determinism matters for this document type]
Classification: [auto-fix|conditional|flag-for-review]
Fix Action: [what was done OR "flagged for review — [reason]"]
Severity: [HIGH|MEDIUM|LOW]
```

## Auto-Fix Classification

| Problem Class | Classification | Fix Action |
|---------------|---------------|------------|
| DETERMINISM-VIOLATION (missing environment assumptions) | auto-fix | Add placeholder "Environment: [specify required versions/configs]" |
| DETERMINISM-VIOLATION (undocumented state dependency) | auto-fix | Add explicit state dependency note between steps |
| DETERMINISM-VIOLATION (non-deterministic step) | flag-for-review | Non-determinism may be intentional; requires domain judgment |

Co-authored with AI: <AgentName> (<ModelId>)