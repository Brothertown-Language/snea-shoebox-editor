# Task: operational-flow

## Purpose

Check process flow and runbook documents for operational completeness: error recovery paths, input/output contracts, idempotency, sequential correctness, pause/resume capability, and rollback paths.

**Applicable document types:** Process Flow, Runbook/SOP

## Checks

| Check | Problem Class | Description |
|-------|---------------|-------------|
| Error recovery | OPERATIONAL-FLOW-GAP | Every step has a "what if this fails" path |
| Input/output contracts | OPERATIONAL-FLOW-GAP | Each step's outputs feed the next step's inputs |
| Idempotency | OPERATIONAL-FLOW-GAP | Can any step be safely re-run? |
| Sequential correctness | OPERATIONAL-FLOW-GAP | Are steps in dependency order? |
| Pause/resume | OPERATIONAL-FLOW-GAP | Can the operator stop and resume between steps? |
| Rollback | OPERATIONAL-FLOW-GAP | Is there a rollback path from any step? |

## Procedure

1. Read the document from issue, file, or URL source
2. Confirm document type is Process Flow or Runbook/SOP (skip otherwise)
3. For each step in the document:
   - Verify an error recovery path exists (what to do if this step fails)
   - Verify inputs and outputs are explicitly stated
   - Check if the step can be safely re-run if interrupted
4. Verify global properties:
   - Steps are in correct dependency order (no forward dependencies)
   - Pause/resume points are identifiable
   - Rollback paths exist from any step to a known-good state
5. For each missing element, create a finding

## Report Format

```
Subtask: operational-flow
Finding: OPERATIONAL-FLOW-GAP - [summary]
Location: [step or section]
Context: [why this matters for operational correctness]
Classification: [auto-fix|conditional|flag-for-review]
Fix Action: [what was done OR "flagged for review — [reason]"]
Severity: [HIGH|MEDIUM|LOW]
```

## Auto-Fix Classification

| Problem Class | Classification | Fix Action |
|---------------|---------------|------------|
| OPERATIONAL-FLOW-GAP (missing error recovery) | auto-fix | Add placeholder "If this step fails: [describe recovery]" |
| OPERATIONAL-FLOW-GAP (missing I/O contract) | auto-fix | Add placeholder "Inputs: [list] / Outputs: [list]" |
| OPERATIONAL-FLOW-GAP (wrong order) | flag-for-review | Reordering steps requires understanding intent |
| OPERATIONAL-FLOW-GAP (no rollback) | flag-for-review | Rollback design requires domain expertise |

Co-authored with AI: <AI-Name> (<model-id>)