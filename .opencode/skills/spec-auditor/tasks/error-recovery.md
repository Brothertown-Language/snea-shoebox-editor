# Task: error-recovery

## Purpose

Check runbook and SOP documents for error recovery and rollback completeness: prerequisites, scope, contact/escalation, version/date, and validation gates.

**Applicable document types:** Runbook/SOP

## Checks

| Check | Problem Class | Description |
|-------|---------------|-------------|
| Prerequisites | ERROR-RECOVERY-GAP | Tools, access, and credentials needed before starting are listed |
| Scope | ERROR-RECOVERY-GAP | What this runbook covers and what it doesn't is stated |
| Contact/escalation | ERROR-RECOVERY-GAP | Who to call when things go wrong is documented |
| Version/date | ERROR-RECOVERY-GAP | When this was last validated is recorded |
| Validation gate | ERROR-RECOVERY-GAP | How to confirm the procedure succeeded is specified |

## Procedure

1. Read the document from issue, file, or URL source
2. Confirm document type is Runbook/SOP (skip otherwise)
3. Check for prerequisites section:
   - Required tools and their versions
   - Required access levels or credentials
   - Required environment state (e.g., "database must be backed up")
4. Check for scope definition:
   - What this runbook covers
   - What it does NOT cover (out of scope)
5. Check for contact/escalation:
   - Primary contact for questions
   - Escalation path for failures outside runbook scope
6. Check for version/date:
   - Last validation date
   - Version number if applicable
7. Check for validation gate at end:
   - How to verify the procedure succeeded
   - What "success" looks like (specific, measurable criteria)
8. Create findings for each missing element

## Report Format

```
Subtask: error-recovery
Finding: ERROR-RECOVERY-GAP - [summary]
Location: [section or "absent from document"]
Context: [why this matters for runbook reliability]
Classification: [auto-fix|conditional|flag-for-review]
Fix Action: [what was done OR "flagged for review — [reason]"]
Severity: [HIGH|MEDIUM|LOW]
```

## Auto-Fix Classification

| Problem Class | Classification | Fix Action |
|---------------|---------------|------------|
| ERROR-RECOVERY-GAP (missing prerequisites) | auto-fix | Add "## Prerequisites" stub with checklist template |
| ERROR-RECOVERY-GAP (missing scope) | auto-fix | Add "## Scope" stub with "In scope" / "Out of scope" template |
| ERROR-RECOVERY-GAP (missing escalation) | auto-fix | Add "## Escalation" stub with contact template |
| ERROR-RECOVERY-GAP (missing version/date) | auto-fix | Add `Last Validated: [date]` header |
| ERROR-RECOVERY-GAP (missing validation gate) | auto-fix | Add "## Validation" stub with success criteria template |

Co-authored with AI: <AgentName> (<ModelId>)