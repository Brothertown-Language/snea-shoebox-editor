# Task: operational

## Purpose

Check for completeness of operational requirements: logging, metrics, alerts, deployment constraints, and data migration. New in v2. Auto-fix eligible findings are applied directly.

**Delegated from:** N/A (new in v2, indigenous to spec-auditor).

## Checks

| Check | Problem Class | Description |
|-------|---------------|-------------|
| Logging | OPERATIONAL-REQUIREMENTS-INCOMPLETE | Are logging requirements specified for the feature? |
| Metrics | OPERATIONAL-REQUIREMENTS-INCOMPLETE | Are measurable metrics defined? |
| Alerts | OPERATIONAL-REQUIREMENTS-INCOMPLETE | Are failure notification paths specified? |
| Deployment constraints | OPERATIONAL-REQUIREMENTS-INCOMPLETE | Are deployment strategy and rollback specified? |
| Data migration | OPERATIONAL-REQUIREMENTS-INCOMPLETE | For schema changes, are migration plans specified? |

## Procedure

1. Read the spec issue via GitHub MCP
2. Determine if the spec involves non-trivial system changes (new endpoints, schema changes, infrastructure)
3. If trivial (simple bug fix, text change), report as N/A and skip
4. For non-trivial specs, check for:
   - Logging: What events to log, at what level, with what context
   - Metrics: What to measure, alert thresholds
   - Alerts: Failure notifications, escalation paths
   - Deployment: Strategy (blue/green, canary, rollback)
   - Data migration: Schema changes, backfills, zero-downtime requirements
5. Flag any missing operational requirements as findings

## When to Run

- Infrastructure-heavy specs (database changes, API changes)
- Specs that affect deployment (new services, configuration changes)
- Specs with schema changes (requiring migration plans)
- Multi-phase specs where deployment order matters

## When to Skip

- Simple bug fixes with no deployment implications
- Text/content changes
- Refactoring that doesn't change behavior

## Report Format

```
Subtask: operational
Finding: OPERATIONAL-REQUIREMENTS-INCOMPLETE - [what's missing]
Location: [section of spec or "absent from spec"]
Context: [why operational readiness matters for this spec]
Classification: [auto-fix|conditional|flag-for-review]
Fix Action: [what was done OR "flagged for review — [reason]"]
Severity: [HIGH|MEDIUM|LOW]
```

## Auto-Fix Classification

| Problem Class | Classification | Fix Action |
|---------------|---------------|------------|
| OPERATIONAL-REQUIREMENTS-INCOMPLETE | auto-fix | Add operational requirements section stub (developer fills in details) |

## Cross-Reference

Creation-time operational requirements are enforced by the `spec-creation` skill's `risk` task. This subtask verifies completeness as a second pass — checking that operational concerns were addressed during spec creation and that nothing was missed.

**Finding pattern:** `MISSING-OPERATIONAL` — Spec lacks creation-time operational requirements. Was `spec-creation --task risk` used?

Co-authored with AI: <AI-Name> (<model-id>)