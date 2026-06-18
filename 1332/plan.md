# Implementation Plan — #1332: System Event Logging

## Goal

Add persistent system event logging to a SQL `system_event_log` table for offline analysis of exceptions, migration lifecycle events, application lifecycle events, and infrastructure notifications.

## Architecture

The feature adds a new model `SystemEventLog` (SQLAlchemy ORM) in `src/database/models/event_log.py`, a new service `EventLogService` in `src/services/event_log_service.py`, a migration entry to create the table, and integration hooks in `src/database/migrations.py` (log functions) and `src/frontend/ui_utils.py` (`handle_ui_error()`).

## Tech Stack

- SQLAlchemy ORM on PostgreSQL
- JSONB column for flexible structured details
- `TIMESTAMP(timezone=True)` for event timestamps
- `extend_existing=True` table args (Streamlit hot-reload compatibility)
- Auto-increment integer primary key

---

> **Compliance Requirement:** All steps and sub-steps in this document MUST be followed in order. Failure to comply with any step — including but not limited to verification gates, test phases, audit checkpoints, and review steps — will result in the feature branch being rejected and discarded, requiring a full rework from scratch and loss of all prior work. There is no valid reason to skip, compress, reorder, or omit any step. If a step appears redundant or unnecessary, follow it anyway — the cost of following an extra step is negligible compared to the cost of rework from a skipped step.

---

## Phase 1: Model + Migration

**Concern:** Data layer — `SystemEventLog` ORM model and database migration to create the `system_event_log` table. Entering first architectural concern (persistence). Leaves zero state — this is the foundation layer.

**Files:** `src/database/models/event_log.py` (new), `src/database/migrations.py` (edit: add migration entry + `_migrate_create_system_event_log()` method)

**SCs covered:** SC-1, SC-10

### Dispatch Table

| Gate | Dispatch Type | Blind? | Sub-Agent Type | Receives Context | SCs |
|------|--------------|--------|----------------|-----------------|-----|
| G1: sc-coherence-gate | sub-task | yes (blind) | general | `{"task": "Verify spec/plan coherence for Phase 1 model+migration scope. Issue 1332. Phase 1 covers SystemEventLog model + migration entry. SC-1, SC-10."}` | SC-1, SC-10 |
| G2: pre-red-baseline | sub-task | yes (blind) | general | `{"task": "Document source currency and SC-ID traceability for Phase 1. Issue 1332. Model + migration scope."}` | SC-1, SC-10 |
| G3: red-phase | sub-task | yes (blind) | general | `{"task": "Write failing test for Phase 1: verify system_event_log table exists with correct schema after migration (SC-1). Issue 1332."}` | SC-1 |
| G4: red-doublecheck | sub-task | yes (blind) | general | `{"task": "Verify RED-side SC evidence: test correctly fails because model/migration don't exist yet. Issue 1332 Phase 1."}` | SC-1 |
| G5: post-red-enforcement | sub-task | yes (blind) | general | `{"task": "Enforce RED gate: git diff --name-only -- src/ | wc -l must be zero. Issue 1332 Phase 1."}` | SC-1 |
| G6: green-phase | sub-task | yes (blind) | general | `{"task": "Implement SystemEventLog model in src/database/models/event_log.py and migration entry in src/database/migrations.py. Issue 1332."}` | SC-1, SC-10 |
| G7: post-green-enforcement | sub-task | yes (blind) | general | `{"task": "Enforce GREEN gate: git diff --name-only -- test/ | wc -l must be non-zero. Issue 1332 Phase 1."}` | SC-1 |
| G8: checkpoint-commit | inline | N/A | N/A | — | SC-1, SC-10 |
| G9: structural-checks | sub-task | yes (blind) | general | `{"task": "Run lint/typecheck/format checks on Phase 1 changes. Issue 1332."}` | SC-1, SC-10 |
| G10: green-doublecheck | sub-task | yes (blind) | general | `{"task": "Semantic-intent verification of Phase 1 GREEN implementation. Verify model matches spec. Issue 1332."}` | SC-1, SC-10 |
| G11: green-vbc | sub-task | yes (blind) | general | `{"task": "Verification before completion for Phase 1. Issue 1332."}` | SC-1, SC-10 |
| G12: adversarial-audit | sub-task | yes (blind) | general | `{"task": "Audit Phase 1 implementation for verifiability and correctness. Issue 1332."}` | SC-1, SC-10 |
| G13: cross-validate | sub-task | yes (blind) | general | `{"task": "Cross-validate Phase 1 auditors' findings. Issue 1332."}` | SC-1, SC-10 |
| G14: regression-check | sub-task | yes (blind) | general | `{"task": "Run regression tests for Phase 1. Issue 1332."}` | SC-1, SC-10 |
| G15: review-prep | sub-task | yes (blind) | general | `{"task": "Prepare Phase 1 for review. Issue 1332."}` | SC-1, SC-10 |
| G16: exec-summary | sub-task | yes (blind) | general | `{"task": "Phase 1 completion summary. Issue 1332."}` | SC-1, SC-10 |

### Concern Boundary Annotation

**Leaving:** Data layer foundation (model + migration). At this point the `system_event_log` table exists but nothing writes to it.

**Entering:** Service layer — `EventLogService` will use the model created in Phase 1.

**Handoff info needed by Phase 2:** The `SystemEventLog` model class name, import path (`src.database.models.event_log`), and the `get_session()` connection function from `src.database.connection`.

### Inter-Phase Handoff

1. Update Z3 state file with Phase 1 gate states
2. Run `solve check` — confirm Phase 1 dependency contract SAT
3. Verify checkpoint tag exists for Phase 1
4. Append lifecycle manifest event for Phase 1 completion

---

## Phase 2: EventLogService

**Concern:** Service layer — `EventLogService` with `log_event()`, `log_exception()`, and `get_events()`. Entering the service concern, leaving the data layer. Follows the `AuditService.log_activity()` pattern.

**Files:** `src/services/event_log_service.py` (new)

**SCs covered:** SC-2, SC-3, SC-7, SC-9

### Dispatch Table

| Gate | Dispatch Type | Blind? | Sub-Agent Type | Receives Context | SCs |
|------|--------------|--------|----------------|-----------------|-----|
| G1: sc-coherence-gate | sub-task | yes (blind) | general | `{"task": "Verify spec/plan coherence for Phase 2 service scope. Issue 1332. Phase 2 covers EventLogService. SC-2, SC-3, SC-7, SC-9."}` | SC-2, SC-3, SC-7, SC-9 |
| G2: pre-red-baseline | sub-task | yes (blind) | general | `{"task": "Document source currency and SC-ID traceability for Phase 2. Issue 1332. Service layer."}` | SC-2, SC-3, SC-7, SC-9 |
| G3: red-phase | sub-task | yes (blind) | general | `{"task": "Write failing tests for Phase 2: log_event() writes record (SC-2), log_exception() extracts exception data (SC-3), DB write resilience (SC-7), get_events() query API (SC-9). Issue 1332."}` | SC-2, SC-3, SC-7, SC-9 |
| G4: red-doublecheck | sub-task | yes (blind) | general | `{"task": "Verify RED-side SC evidence: tests correctly fail because EventLogService doesn't exist yet. Issue 1332 Phase 2."}` | SC-2, SC-3, SC-7, SC-9 |
| G5: post-red-enforcement | sub-task | yes (blind) | general | `{"task": "Enforce RED gate: git diff --name-only -- src/ | wc -l must be zero. Issue 1332 Phase 2."}` | SC-2, SC-3, SC-7, SC-9 |
| G6: green-phase | sub-task | yes (blind) | general | `{"task": "Implement EventLogService with log_event(), log_exception(), get_events() in src/services/event_log_service.py. Follow AuditService.log_activity() pattern. Issue 1332."}` | SC-2, SC-3, SC-7, SC-9 |
| G7: post-green-enforcement | sub-task | yes (blind) | general | `{"task": "Enforce GREEN gate: git diff --name-only -- test/ | wc -l must be non-zero. Issue 1332 Phase 2."}` | SC-2, SC-3, SC-7, SC-9 |
| G8: checkpoint-commit | inline | N/A | N/A | — | SC-2, SC-3, SC-7, SC-9 |
| G9: structural-checks | sub-task | yes (blind) | general | `{"task": "Run lint/typecheck/format checks on Phase 2 changes. Issue 1332."}` | SC-2, SC-3, SC-7, SC-9 |
| G10: green-doublecheck | sub-task | yes (blind) | general | `{"task": "Semantic-intent verification of Phase 2 GREEN implementation. Verify service matches spec. Issue 1332."}` | SC-2, SC-3, SC-7, SC-9 |
| G11: green-vbc | sub-task | yes (blind) | general | `{"task": "Verification before completion for Phase 2. Issue 1332."}` | SC-2, SC-3, SC-7, SC-9 |
| G12: adversarial-audit | sub-task | yes (blind) | general | `{"task": "Audit Phase 2 implementation for verifiability and correctness. Issue 1332."}` | SC-2, SC-3, SC-7, SC-9 |
| G13: cross-validate | sub-task | yes (blind) | general | `{"task": "Cross-validate Phase 2 auditors' findings. Issue 1332."}` | SC-2, SC-3, SC-7, SC-9 |
| G14: regression-check | sub-task | yes (blind) | general | `{"task": "Run regression tests for Phase 2. Issue 1332."}` | SC-2, SC-3, SC-7, SC-9 |
| G15: review-prep | sub-task | yes (blind) | general | `{"task": "Prepare Phase 2 for review. Issue 1332."}` | SC-2, SC-3, SC-7, SC-9 |
| G16: exec-summary | sub-task | yes (blind) | general | `{"task": "Phase 2 completion summary. Issue 1332."}` | SC-2, SC-3, SC-7, SC-9 |

### Concern Boundary Annotation

**Leaving:** Service layer — `EventLogService` is implemented and tested. It can write events to the DB and query them back.

**Entering:** Integration layer — existing code paths (migration log functions, `handle_ui_error()`) need to call the new service.

**Handoff info needed by Phase 3:** The `EventLogService.log_event()` and `EventLogService.log_exception()` function signatures, import path (`src.services.event_log_service`).

### Inter-Phase Handoff

1. Update Z3 state file with Phase 2 gate states
2. Run `solve check` — confirm Phase 2 dependency contract SAT
3. Verify checkpoint tag exists for Phase 2
4. Append lifecycle manifest event for Phase 2 completion

---

## Phase 3: Integration Hooks

**Concern:** Integration — wiring existing code paths into the new event logging service. Entering the integration concern. Leaving the new-code concern (no new files — only edits to existing files).

**Files:** `src/database/migrations.py` (edit: `log_migration_start()`, `log_migration_skip()`, `log_migration_complete()`, `log_migration_error()`), `src/frontend/ui_utils.py` (edit: `handle_ui_error()`)

**SCs covered:** SC-4, SC-5, SC-6, SC-8

### Dispatch Table

| Gate | Dispatch Type | Blind? | Sub-Agent Type | Receives Context | SCs |
|------|--------------|--------|----------------|-----------------|-----|
| G1: sc-coherence-gate | sub-task | yes (blind) | general | `{"task": "Verify spec/plan coherence for Phase 3 integration scope. Issue 1332. Integration hooks: migration log functions + handle_ui_error(). SC-4, SC-5, SC-6, SC-8."}` | SC-4, SC-5, SC-6, SC-8 |
| G2: pre-red-baseline | sub-task | yes (blind) | general | `{"task": "Document source currency and SC-ID traceability for Phase 3. Issue 1332. Integration hooks."}` | SC-4, SC-5, SC-6, SC-8 |
| G3: red-phase | sub-task | yes (blind) | general | `{"task": "Write failing tests for Phase 3: migration events logged (SC-4), handle_ui_error calls log_exception (SC-5), stderr preserved (SC-6), backward-compatible signature (SC-8). Issue 1332."}` | SC-4, SC-5, SC-6, SC-8 |
| G4: red-doublecheck | sub-task | yes (blind) | general | `{"task": "Verify RED-side SC evidence: tests correctly fail because hooks not wired yet. Issue 1332 Phase 3."}` | SC-4, SC-5, SC-6, SC-8 |
| G5: post-red-enforcement | sub-task | yes (blind) | general | `{"task": "Enforce RED gate: git diff --name-only -- src/ | wc -l must be zero. Issue 1332 Phase 3."}` | SC-4, SC-5, SC-6, SC-8 |
| G6: green-phase | sub-task | yes (blind) | general | `{"task": "Implement integration hooks: update log_migration_*() functions in src/database/migrations.py and handle_ui_error() in src/frontend/ui_utils.py. Issue 1332."}` | SC-4, SC-5, SC-6, SC-8 |
| G7: post-green-enforcement | sub-task | yes (blind) | general | `{"task": "Enforce GREEN gate: git diff --name-only -- test/ | wc -l must be non-zero. Issue 1332 Phase 3."}` | SC-4, SC-5, SC-6, SC-8 |
| G8: checkpoint-commit | inline | N/A | N/A | — | SC-4, SC-5, SC-6, SC-8 |
| G9: structural-checks | sub-task | yes (blind) | general | `{"task": "Run lint/typecheck/format checks on Phase 3 changes. Issue 1332."}` | SC-4, SC-5, SC-6, SC-8 |
| G10: green-doublecheck | sub-task | yes (blind) | general | `{"task": "Semantic-intent verification of Phase 3 GREEN implementation. Verify hooks match spec. Issue 1332."}` | SC-4, SC-5, SC-6, SC-8 |
| G11: green-vbc | sub-task | yes (blind) | general | `{"task": "Verification before completion for Phase 3. Issue 1332."}` | SC-4, SC-5, SC-6, SC-8 |
| G12: adversarial-audit | sub-task | yes (blind) | general | `{"task": "Audit Phase 3 implementation for verifiability and correctness. Issue 1332."}` | SC-4, SC-5, SC-6, SC-8 |
| G13: cross-validate | sub-task | yes (blind) | general | `{"task": "Cross-validate Phase 3 auditors' findings. Issue 1332."}` | SC-4, SC-5, SC-6, SC-8 |
| G14: regression-check | sub-task | yes (blind) | general | `{"task": "Run regression tests for Phase 3. Issue 1332."}` | SC-4, SC-5, SC-6, SC-8 |
| G15: review-prep | sub-task | yes (blind) | general | `{"task": "Prepare Phase 3 for review. Issue 1332."}` | SC-4, SC-5, SC-6, SC-8 |
| G16: exec-summary | sub-task | yes (blind) | general | `{"task": "Phase 3 completion summary. Issue 1332."}` | SC-4, SC-5, SC-6, SC-8 |

### Concern Boundary Annotation

**Leaving:** Integration concern — all existing code paths now write to the `system_event_log` table.

**Entering:** Completion — all SCs implemented. Verify against spec, run finishing checklist.

**Handoff info needed by post-all-phases sweep:** Git status, lint results, test results for the full feature.

---

> **Compliance Requirement:** All steps and sub-steps in this document MUST be followed in order. Failure to comply with any step — including but not limited to verification gates, test phases, audit checkpoints, and review steps — will result in the feature branch being rejected and discarded, requiring a full rework from scratch and loss of all prior work. There is no valid reason to skip, compress, reorder, or omit any step. If a step appears redundant or unnecessary, follow it anyway — the cost of following an extra step is negligible compared to the cost of rework from a skipped step.

---

## Post-All-Phases Sweep

- [ ] FINISHING CHECKLIST — route to finishing sub-agent: git status clean, lint/typecheck from scratch, coverage sweep
- [ ] PR CREATION — route to git-workflow pr-creation: via `github_create_pull_request`, extract `html_url` from response
- [ ] POST-MERGE CLEANUP — route to git-workflow cleanup: delete merged branches, close issues, sync dev

## Authorization Context

```
authorization_scope: for_plan
halt_at: plan_created
pr_strategy: none
pipeline_phase: plan_creation
authorization_source: "User approved #1332 via spec approval cascade"
```