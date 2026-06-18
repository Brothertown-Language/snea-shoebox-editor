STATUS: DRAFT
CREATED: 2026-06-17

---

## Executive Summary

Add persistent system event logging to a SQL table for offline analysis of exceptions, migration lifecycle events, application lifecycle events, and infrastructure notifications. A single `system_event_log` table with an `event_type` discriminator captures all non-user-activity system events with structured context (severity, source, JSONB details). This replaces the narrower exception-only scope of the prior spec and provides a unified foundation for observability.

---

## Context

### Current State

The application has two logging paths:

1. **stderr logging** via `get_logger()` — used throughout the codebase (e.g., `src/database/migrations.py` `log_migration_start()`, `log_migration_error()`; `src/frontend/ui_utils.py` `handle_ui_error()`). Logs are ephemeral — they disappear after rotation and are inaccessible in Streamlit Cloud production.

2. **User activity logging** via `UserActivityLog` model (`src/database/models/identity.py:68`) and `AuditService.log_activity()` (`src/services/audit_service.py:21`). This tracks user-initiated actions (login, sync, edits) and is intentionally separate from system events.

### Existing Patterns

- **Model pattern**: `UserActivityLog` in `src/database/models/identity.py` — `TIMESTAMP(timezone=True)`, `__table_args__ = {"extend_existing": True}`, `autoincrement=True` primary key
- **Service pattern**: `AuditService.log_activity()` in `src/services/audit_service.py` — static method, optional session injection, error-safe commit with rollback on failure, never suppresses the caller's exception
- **Migration pattern**: `MigrationManager._MIGRATIONS` list in `src/database/migrations.py` — timestamp-based version format `YYYYMMDDHHMMSS`, each entry is `(version, method_name, description)`
- **Model file pattern**: Separate files per concern in `src/database/models/` (e.g., `identity.py`, `core.py`, `meta.py`, `search.py`)
- **Import convention**: `src/database/models/__init__.py` is docstring-only — no re-exports, no `__all__`
- **Base**: `declarative_base()` from `src/database/base.py`

---

## Problem Statement

System events that are critical for post-mortem analysis and operational awareness are currently written only to stderr logs, which:

- Disappear after log rotation
- Cannot be queried or aggregated for pattern analysis
- Are inaccessible in Streamlit Cloud production
- Lack structured context (severity, event type, JSONB details) for programmatic analysis
- Require manual grep-based correlation across disparate log lines

**Use Cases:**

1. A developer MUST be able to review all exceptions that occurred overnight, grouped by exception type and frequency
2. Migration failures MUST be persisted so that deployment issues can be diagnosed without access to ephemeral build logs
3. Application startup and shutdown events MUST be recorded to establish a timeline of service availability
4. Infrastructure events (DB connectivity loss, DNS resolution failures) MUST be logged to correlate application errors with underlying infrastructure problems
5. A user reporting "the app crashed yesterday" MUST be supportable by querying persisted events for that time window

---

## Requirements

The system MUST:

1. **REQ-1: Unified event table** — A single `system_event_log` table with an `event_type` string discriminator, shared across all event categories. No separate tables per event type.

2. **REQ-2: Event type support** — The following event types MUST be supported:
   - `exception` — exceptions caught by error handlers
   - `migration_start`, `migration_skip`, `migration_complete`, `migration_error` — migration lifecycle
   - `system_startup`, `system_shutdown` — application lifecycle
   - `infrastructure` — DB connectivity, DNS, other infra events

3. **REQ-3: Common fields** — Every event MUST include: `id` (auto-increment PK), `event_type` (string discriminator), `severity` (e.g., `info`, `warning`, `error`, `critical`), `message` (human-readable summary), `source` (module or component name), `details` (JSONB for structured context), `created_at` (TIMESTAMP with timezone).

4. **REQ-4: Unified logging entry point** — A single `EventLogService.log_event()` method that accepts event type, severity, message, source, and optional details dict. This MUST follow the `AuditService.log_activity()` pattern: static method, optional session injection, error-safe commit, never suppresses the caller's exception.

5. **REQ-5: Exception-specific helper** — A convenience method `EventLogService.log_exception()` that extracts exception type, message, and stack trace from an `Exception` object and calls `log_event()` with `event_type="exception"`.

6. **REQ-6: Migration integration** — The existing `log_migration_start()`, `log_migration_skip()`, `log_migration_complete()`, and `log_migration_error()` functions in `src/database/migrations.py` MUST also call `EventLogService.log_event()` in addition to their current stderr logging. The stderr logging MUST NOT be removed.

7. **REQ-7: `handle_ui_error()` integration** — The existing `handle_ui_error()` in `src/frontend/ui_utils.py` MUST call `EventLogService.log_exception()` in addition to its current stderr logging. The stderr logging MUST NOT be removed. The function signature MUST remain backward-compatible.

8. **REQ-8: DB write resilience** — A failure to write to the `system_event_log` table MUST NOT suppress the original event or exception. The service MUST catch DB exceptions, log them to stderr, and allow the caller to proceed.

9. **REQ-9: Log from now on** — No backfill of existing migration history or past exceptions. Only events occurring after deployment of this feature are recorded.

10. **REQ-10: Separation from user activity** — System events MUST use the `system_event_log` table, NOT the `user_activity_log` table. These are different concerns with different retention and query patterns.

---

## Non-Goals

- **User activity logging** — Already handled by `UserActivityLog` + `AuditService`. System events are a separate concern.
- **Real-time alerting or notification** — This spec addresses persistent storage only, not push notifications.
- **Log rotation or purging** — Retention policy is a follow-up concern.
- **Admin UI for viewing events** — A query API (`get_events()`) is in scope; a Streamlit admin page is not.
- **Third-party monitoring integration** — Sentry, Datadog, etc. are not addressed here.
- **Backfill of existing events** — Only events after deployment are recorded.

---

## Key Decisions

| DEC-ID | Decision | Rationale |
|--------|----------|-----------|
| DEC-A | Single `system_event_log` table with `event_type` discriminator | Avoids schema proliferation (one table per event type would create 8+ nearly identical tables). The discriminator pattern is well-suited to events that share most fields and differ only in `details` content. |
| DEC-B | Keep separate from `UserActivityLog` | User actions and system events have different retention requirements, query patterns, and consumers. Mixing them would complicate both. |
| DEC-C | Log from now on only; no backfill | Backfilling migration history from stderr logs is unreliable (logs may have rotated) and adds complexity with no user-facing benefit. |
| DEC-D | New model file `src/database/models/event_log.py` | Follows the existing convention of one file per concern (`identity.py`, `core.py`, `meta.py`, `search.py`). Keeps the model discoverable. |
| DEC-E | `EventLogService.log_event()` as unified entry point | Follows the `AuditService.log_activity()` pattern established in `src/services/audit_service.py`. A single entry point ensures consistent field population and error handling. |
| DEC-F | Replace prior exception-only spec entirely | The exception-only scope was too narrow. A unified system event table covers more use cases with less total complexity than multiple single-purpose tables. |

---

## Success Criteria

| ID | Criterion | Evidence Type |
|----|-----------|---------------|
| SC-1 | `system_event_log` table exists with all common fields (id, event_type, severity, message, source, details JSONB, created_at TIMESTAMP with timezone) after migration | behavioral |
| SC-2 | `EventLogService.log_event()` writes a record to `system_event_log` with correct field values | behavioral |
| SC-3 | `EventLogService.log_exception()` extracts exception type, message, and stack trace and writes an `exception`-type event | behavioral |
| SC-4 | Migration lifecycle events (`migration_start`, `migration_skip`, `migration_complete`, `migration_error`) are written to `system_event_log` when migrations run | behavioral |
| SC-5 | `handle_ui_error()` calls `EventLogService.log_exception()` and an `exception`-type event appears in `system_event_log` | behavioral |
| SC-6 | Existing stderr logging in `handle_ui_error()` and migration log functions is preserved (DB logging is additive) | behavioral |
| SC-7 | When DB write fails during `log_event()`, the original exception or event is not suppressed — the caller proceeds normally | behavioral |
| SC-8 | `handle_ui_error()` signature remains backward-compatible — callers passing only `(e, user_message)` continue to work | behavioral |
| SC-9 | `EventLogService.get_events()` returns events ordered by `created_at` descending, with optional filters for event_type, severity, and date range | behavioral |
| SC-10 | The `__init__.py` in `src/database/models/` remains docstring-only — no re-exports added | structural |

---

## Files Affected

| File | Change |
|------|--------|
| `src/database/models/event_log.py` | **New file** — `SystemEventLog` model |
| `src/database/migrations.py` | Add migration entry + `_migrate_create_system_event_log()` method; update `log_migration_*()` functions to call `EventLogService.log_event()` |
| `src/services/event_log_service.py` | **New file** — `EventLogService` with `log_event()`, `log_exception()`, `get_events()` |
| `src/frontend/ui_utils.py` | Update `handle_ui_error()` to call `EventLogService.log_exception()` |

---

## Risk Traceability

| RISK-ID | Risk Description | Likelihood | Impact | Mitigation | Verifying SC |
|---------|-----------------|------------|--------|------------|--------------|
| RISK-1 | DB write failure during event logging suppresses the original event | Low | High | Catch DB exceptions in `log_event()`, log to stderr, never suppress caller's exception | SC-7 |
| RISK-2 | JSONB `details` column grows unboundedly | Medium | Low | Details are caller-provided; no automatic expansion. Retention policy is a follow-up concern. | — |
| RISK-3 | Migration integration breaks existing migration behavior | Low | High | Stderr logging is preserved (SC-6); DB logging is additive. Migration functions continue to work if DB is unavailable. | SC-4, SC-6 |
| RISK-4 | `handle_ui_error()` signature change breaks callers | Low | High | Signature MUST remain backward-compatible (SC-8). New parameter is optional with default. | SC-8 |

---

## Security Considerations

| Concern | Mitigation |
|---------|------------|
| Sensitive data in exception details | `log_exception()` SHOULD NOT include local variables or request context by default. If added in the future, sensitive value filtering (per prior spec's `_filter_locals()` pattern) MUST be applied. |
| JSONB injection | The `details` field is populated programmatically, not from user input. No injection vector. |
| Information disclosure via event log | Event messages and details MUST NOT contain secrets, tokens, or PII. Callers are responsible for sanitizing their own event data. |

---

## Dependencies

This spec replaces and supersedes issue #51. No other dependencies.

🤖 Co-authored with AI: OpenCode (ollama-cloud/deepseek-v4-flash)