STATUS: 1.3 (REVISED - NEEDS APPROVAL)
CREATED: 2026-03-29
REVISED: 2026-04-23 — Added per-phase TDD RED/GREEN cycle structure; every SC mapped to test function with # SC-N markers; reversed step order (tests before implementation) per incremental-build discipline
REVISED: 2026-05-22 — SC evidence type column added; SC-11/SC-12/SC-13 appended; Phase 4 TDD clarification; per-phase TDD cycle tables standardized
REVISED: 2026-06-13 — Added Decision Ledger, Risk Traceability, Out of Scope, Constraints, expanded Executive Summary; removed non-spec sections per modern spec standards

---

## Executive Summary

**Intent:** Add persistent exception logging to a SQL table for offline analysis, enabling post-mortem debugging of production issues without relying on ephemeral log files.

**Problem:** Current exception handling logs to stderr (Streamlit logs) which disappear after rotation, cannot be queried for patterns, lack structured context, and are inaccessible in production (Streamlit Cloud).

**Approach Chosen:** Dedicated ExceptionLog model with sanitized local variable capture, stack trace logging, and request context storage. Logged via `log_exception()` service function, integrated into existing `handle_ui_error()` handler.

**Key Design Decisions:** Separate audit model file, secret redaction in local variables, DB-failure resilience (never suppress original exception), configurable truncation limits.

**Alternatives Considered:**
- Structured file logging (JSON logs): Rejected — files also rotate; no query capability
- External logging service (Sentry/DataDog): Rejected — adds external dependency; offline-first requirement
- Extra stderr verbosity: Rejected — does not address persistence or queryability

---

## Decision Ledger

| DEC-ID | Decision | Rationale | Requirement Key | Affected SCs |
|--------|----------|-----------|-----------------|--------------|
| DEC-1 | Dedicated ExceptionLog model in new `audit.py` file | Separate concern from core/meta models; follows existing pattern of one model file per domain | MUST | SC-1, SC-2 |
| DEC-2 | Log exceptions to a SQL table instead of only stderr | Enables querying, aggregation, and retention beyond log rotation | MUST | SC-6, SC-9 |
| DEC-3 | Sanitize local variables before storage (redact secrets) | Prevents sensitive data (passwords, tokens, secrets) from persisting in DB | MUST | SC-4, SC-5 |
| DEC-4 | DB write failure must not suppress original exception | Exception logging is secondary — the original exception must always propagate | MUST | SC-11 |
| DEC-5 | Truncate large values (locals, stack traces) | Prevents unbounded storage growth; configurable MAX_VAR_LENGTH and MAX_STACK_LENGTH | MUST | SC-10, SC-12 |
| DEC-6 | Concurrent-safe DB writes via session-level isolation | Multiple simultaneous exceptions must not cause data loss or interleaving | SHOULD | SC-13 |

---

## Risk Traceability

| RISK-ID | Risk | Likelihood | Impact | Mitigation | Verifying SC |
|---------|------|------------|--------|------------|--------------|
| RISK-1 | Sensitive data leaked into exception logs | Medium | High | _filter_locals() redacts secrets; sanitization has depth limit for circular refs | SC-5 |
| RISK-2 | Exception logging DB write fails | Low | Medium | Catch and log to stderr; original exception never suppressed | SC-11 |
| RISK-3 | Exception log table grows unbounded | Medium | Low | Truncation limits row size; admin UI (Phase 4) can include retention policy | SC-10, SC-12 |
| RISK-4 | Circular reference in locals causes infinite loop | Low | High | Depth-limited sanitization (max 3 levels) catches circular refs | SC-7 |
| RISK-5 | Concurrent exception handling loses data | Low | Medium | Session-level locking or queued writes ensure atomicity | SC-13 |

---

## Context

### Project Structure

- **Database models**: Located in `src/database/models/` with separate files for core, meta, iso639, search, identity, workflow
- **Model imports**: Exported through `src/database/models/__init__.py`
- **Migrations**: Versioned migrations in `src/database/migrations.py` using `MigrationManager._MIGRATIONS` list with format `YYYYMMDDHHMMSS` (timestamp-based, NOT incremental)

### Existing Error Handling

Current implementation in `src/frontend/ui_utils.py`:

```python
def handle_ui_error(
    e: Exception, user_message: str = "An unexpected error occurred.", logger_name: str | None = None
):
    """Logs to server stderr and shows sanitized message to user."""
    log = get_logger(logger_name or "ui_error_handler")
    log.error(f"{user_message} Detail: {str(e)}", exc_info=True)
    st.error(user_message)
    if str(e):
        st.warning(str(e))
```

**Limitation**: Logs disappear after rotation, no database persistence, no structured context.

### Migration System

1. Add migration to `_MIGRATIONS` list: `(timestamp, method_name, description)`
2. Add corresponding `def _migrate_xxx(self, conn):` method
3. Schema version tracked in `schema_version` table automatically

---

## Problem Statement

Current exception handling logs to stderr (Streamlit logs) which:
- Disappear after log rotation
- Cannot be queried for patterns
- Lack structured context for analysis
- Are inaccessible in production (Streamlit Cloud)

**Use Cases:**
1. Developer needs to analyze exceptions that occurred overnight
2. Patterns of similar exceptions need aggregation
3. User reports "it crashed yesterday" — need to find the exception
4. Performance analysis of exception frequency

---

## Project Structure

- **Source code**: `src/database/models/` (models), `src/services/` (business logic), `src/frontend/` (UI)
- **Tests**: `tests/services/` (service tests), `tests/frontend/` (UI tests)
- **Migrations**: `src/database/migrations.py` (versioned schema changes)

---

## Boundaries

| Action | Permission |
|--------|------------|
| Add new model file | ✅ Always |
| Add new service file | ✅ Always |
| Modify migration system | ⚠️ Ask first |
| Update `handle_ui_error()` | ⚠️ Ask first |
| Add admin UI page | ⚠️ Ask first |

---

## Success Criteria

| SC | Test | Expected Result | Evidence Type |
|-----|------|-----------------|---------------|
| SC-1 | `test_exception_log_model_created` # SC-1 | ExceptionLog model maps to `exception_logs` table with all columns | `structural` |
| SC-2 | `test_exception_logs_table_exists` # SC-2 | `\d exception_logs` in psql shows all columns and indexes | `structural` |
| SC-3 | `test_exception_logs_empty_query` # SC-3 | `SELECT * FROM exception_logs LIMIT 1` returns no errors (empty table) | `structural` |
| SC-4 | `test_sanitize_value_depth_limit` # SC-4 | `_sanitize_value({"password": "secret"}, 0)` returns `{"password": ""}` | `behavioral` |
| SC-5 | `test_filter_locals_removes_secrets` # SC-5 | `_filter_locals({"password": "x", "name": "y"})` returns `{"password": "", "name": "y"}` | `behavioral` |
| SC-6 | `test_log_exception_writes_to_db` # SC-6 | `log_exception(exc, session)` creates a record in `exception_logs` with stack trace | `behavioral` |
| SC-7 | `test_sanitize_circular_refs` # SC-7 | `_sanitize_value()` with circular reference returns `"[circular]"` without infinite loop | `behavioral` |
| SC-8 | `test_handle_ui_error_logs_to_db` # SC-8 | `handle_ui_error()` calls `log_exception()` and record appears in `exception_logs` | `behavioral` |
| SC-9 | `test_get_exceptions_query` # SC-9 | `get_exceptions()` returns list of ExceptionLog objects ordered by created_at desc | `behavioral` |
| SC-10 | `test_exception_log_large_locals_truncated` # SC-10 | Locals exceeding MAX_VAR_LENGTH (1000 chars) are truncated | `behavioral` |
| SC-11 | `test_db_failure_does_not_suppress_original_exception` # SC-11 | When DB write fails during `log_exception()`, the original exception is still raised/loged, not suppressed | `behavioral` |
| SC-12 | `test_large_stack_trace_truncated` # SC-12 | Stack traces exceeding configurable MAX_STACK_LENGTH are truncated with a truncation marker appended | `behavioral` |
| SC-13 | `test_concurrent_logging_no_data_loss` # SC-13 | Multiple concurrent `log_exception()` calls from different threads/requests produce no data loss or interleaving | `behavioral` |

---

## Out of Scope

| Concern | Rationale |
|---------|-----------|
| Alerting or notification on new exceptions | This spec covers storage and querying only; alert integration (Slack, email) would be a separate feature |
| Automatic log retention/deletion policy | Phase 4 admin UI may include retention controls; Phase 1-3 store all exceptions indefinitely |
| Non-Python exception capture | Covers only Python exceptions within the Streamlit application; infrastructure-level errors handled separately |
| Performance monitoring integration | Exception logging is passive storage, not active monitoring or APM |

---

## Constraints

| Constraint | Detail |
|------------|--------|
| No suppression of original exceptions | Exception logging must never swallow or suppress the triggering exception |
| Sensitive data redaction | Local variables matching secret patterns (password, token, secret, key) must be sanitized before storage |
| Storage bounding | Local variables truncated to MAX_VAR_LENGTH (1000 chars); stack traces to MAX_STACK_LENGTH |
| Circular reference safety | Sanitization must handle circular/self-referential objects without infinite loops |
| Concurrent safety | Multiple simultaneous exception writes must not interleave or lose data |
| Existing error handler compatibility | `handle_ui_error()` signature and behavior preserved; logging added as side effect |

---

## Security Considerations

| Concern | Mitigation |
|---------|------------|
| Sensitive data in locals | Filter out variables with names containing `password`, `secret`, `token`, etc. |
| Large objects in locals | Truncate to MAX_VAR_LENGTH (1000 chars) |
| Circular references | Depth limit of 3 in _sanitize_value |
| Database connection failure | Catch and log to server stderr |

---

## Files Affected

| File | Change |
|------|--------|
| `src/database/models/audit.py` | New file — `ExceptionLog` model |
| `src/database/models/__init__.py` | Import `ExceptionLog` |
| `src/services/exception_service.py` | New file — `log_exception()`, `get_exceptions()` |
| `src/frontend/ui_utils.py` | Update `handle_ui_error()` to call `log_exception()` |
| `src/database/migrations.py` | Add migration for `exception_logs` table |
| `tests/services/test_exception_service.py` | New file — tests for exception service |
| `tests/frontend/test_ui_utils_errors.py` | New file — integration tests for `handle_ui_error()` |

---

## Dependencies

### None Currently

This spec has no dependencies on other issues. Exception logging is a standalone feature that can be implemented independently.

---

## Phase 1: Database Schema Setup (Gated)

### TDD Cycle

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|-------|-------------------|-------------------|----------|--------|
| Phase 1 | `test_exception_log_model_created` # SC-1, `test_exception_logs_table_exists` # SC-2, `test_exception_logs_empty_query` # SC-3 | `ExceptionLog` model, `__init__.py` import, migration `_migrate_create_exception_logs()` | Clean up model imports, verify migration registry order | Phase 1 commit with phase reference |

### Steps

| Phase | Step | Action |
|------|------|--------|
| **RED** | 1.1 | Add `test_exception_log_model_created` # SC-1 to `tests/database/test_crud.py` — assert ExceptionLog model has `__tablename__ = 'exception_logs'` with columns: id, exception_type, message, stack_trace, local_vars, request_context, created_at |
| **RED** | 1.2 | Add `test_exception_logs_table_exists` # SC-2 to `tests/database/test_migration_manager.py` — assert `exception_logs` table exists with all columns and indexes after migration |
| **RED** | 1.3 | Add `test_exception_logs_empty_query` # SC-3 to `tests/database/test_crud.py` — assert `SELECT * FROM exception_logs LIMIT 1` returns no errors |
| **RED** | 1.4 | Verify all RED tests FAIL: `uv run pytest tests/database/test_crud.py tests/database/test_migration_manager.py -k "exception_log" -v` |
| **GREEN** | 1.5 | Create `ExceptionLog` model in `src/database/models/audit.py` |
| **GREEN** | 1.6 | Add model import to `src/database/models/__init__.py` |
| **GREEN** | 1.7 | Add migration to `_MIGRATIONS` list: `(20260401HHMMSS, "_migrate_create_exception_logs", "Create exception_logs table")` |
| **GREEN** | 1.8 | Implement `_migrate_create_exception_logs()` with CREATE TABLE and indexes |
| **GREEN** | 1.9 | Run migrations, verify all Phase 1 tests PASS: `uv run pytest tests/database/test_crud.py tests/database/test_migration_manager.py -k "exception_log" -v` |
| **REFACTOR** | 1.10 | Clean up model imports, verify migration registry order |
| **COMMIT** | 1.11 | Commit Phase 1 with reference to phase number |

---

## Phase 2: Exception Service Implementation (Gated)

### TDD Cycle

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|-------|-------------------|-------------------|----------|--------|
| Phase 2 | `test_sanitize_value_depth_limit` # SC-4, `test_filter_locals_removes_secrets` # SC-5, `test_log_exception_writes_to_db` # SC-6, `test_sanitize_circular_refs` # SC-7, `test_get_exceptions_query` # SC-9, `test_exception_log_large_locals_truncated` # SC-10, `test_db_failure_does_not_suppress_original_exception` # SC-11, `test_large_stack_trace_truncated` # SC-12, `test_concurrent_logging_no_data_loss` # SC-13 | `log_exception()`, `_sanitize_value()`, `_filter_locals()`, `_get_request_context()`, `get_exceptions()` | Clean up service code, verify error handling for DB connection failures | Phase 2 commit with phase reference |

### Steps

| Phase | Step | Action |
|------|------|--------|
| **RED** | 2.1 | Add `test_sanitize_value_depth_limit` # SC-4 to `tests/services/test_exception_service.py` — assert `_sanitize_value({"password": "secret"}, 0)` returns `{"password": ""}` |
| **RED** | 2.2 | Add `test_filter_locals_removes_secrets` # SC-5 to `tests/services/test_exception_service.py` — assert `_filter_locals({"password": "x", "name": "y"})` returns `{"password": "", "name": "y"}` |
| **RED** | 2.3 | Add `test_log_exception_writes_to_db` # SC-6 to `tests/services/test_exception_service.py` — assert `log_exception(exc, session)` creates a record in `exception_logs` |
| **RED** | 2.4 | Add `test_sanitize_circular_refs` # SC-7 to `tests/services/test_exception_service.py` — assert `_sanitize_value()` with circular reference returns `"[circular]"` without infinite loop |
| **RED** | 2.5 | Add `test_get_exceptions_query` # SC-9 to `tests/services/test_exception_service.py` — assert `get_exceptions()` returns list of ExceptionLog objects ordered by created_at desc |
| **RED** | 2.6 | Add `test_exception_log_large_locals_truncated` # SC-10 to `tests/services/test_exception_service.py` — assert locals exceeding MAX_VAR_LENGTH (1000 chars) are truncated |
| **RED** | 2.7 | Add `test_db_failure_does_not_suppress_original_exception` # SC-11 to `tests/services/test_exception_service.py` — assert when DB write fails during `log_exception()`, original exception is still raised/logged |
| **RED** | 2.8 | Add `test_large_stack_trace_truncated` # SC-12 to `tests/services/test_exception_service.py` — assert stack traces exceeding configurable MAX_STACK_LENGTH are truncated with truncation marker |
| **RED** | 2.9 | Add `test_concurrent_logging_no_data_loss` # SC-13 to `tests/services/test_exception_service.py` — assert multiple concurrent `log_exception()` calls produce no data loss or interleaving |
| **RED** | 2.10 | Verify all RED tests FAIL: `uv run pytest tests/services/test_exception_service.py -v` |
| **GREEN** | 2.11 | Create `src/services/exception_service.py` with `log_exception()` function |
| **GREEN** | 2.12 | Implement `_sanitize_value()` with depth limiting (max 3) |
| **GREEN** | 2.13 | Implement `_filter_locals()` with sensitive var filtering (`password`, `secret`, `token`, etc.) |
| **GREEN** | 2.14 | Implement `_get_request_context()` for Streamlit state capture |
| **GREEN** | 2.15 | Implement `get_exceptions()` query function |
| **GREEN** | 2.16 | Implement DB-failure resilience: catch all DB exceptions in `log_exception()`, log to stderr, never suppress the original exception |
| **GREEN** | 2.17 | Implement stack trace truncation: truncate to `MAX_STACK_LENGTH` with truncation marker appended |
| **GREEN** | 2.18 | Verify concurrent-safety: use session-level locking or queued writes for thread-safe DB access |
| **GREEN** | 2.19 | Verify all Phase 2 tests PASS: `uv run pytest tests/services/test_exception_service.py -v` |
| **REFACTOR** | 2.20 | Clean up service code, verify error handling for DB connection failures |
| **COMMIT** | 2.21 | Commit Phase 2 with reference to phase number |

---

## Phase 3: Integration Points (Gated)

### TDD Cycle

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|-------|-------------------|-------------------|----------|--------|
| Phase 3 | `test_handle_ui_error_logs_to_db` # SC-8 | Update `handle_ui_error()` to call `log_exception()`, add `session_id` parameter | Review integration, verify stack trace, local vars, context captured correctly | Phase 3 commit with phase reference |

### Steps

| Phase | Step | Action |
|------|------|--------|
| **RED** | 3.1 | Add `test_handle_ui_error_logs_to_db` # SC-8 to `tests/frontend/test_ui_utils_errors.py` — assert `handle_ui_error()` calls `log_exception()` and record appears in `exception_logs` |
| **RED** | 3.2 | Verify RED test FAILS: `uv run pytest tests/frontend/test_ui_utils_errors.py -k "exception" -v` |
| **GREEN** | 3.3 | Update `handle_ui_error()` in `src/frontend/ui_utils.py` to call `log_exception()` |
| **GREEN** | 3.4 | Add `session_id` parameter to `handle_ui_error()` signature |
| **GREEN** | 3.5 | Import `log_exception` from `src.services.exception_service` |
| **GREEN** | 3.6 | Verify Phase 3 test PASSES: `uv run pytest tests/frontend/test_ui_utils_errors.py -k "exception" -v` |
| **REFACTOR** | 3.7 | Review integration, verify stack trace, local vars, context captured correctly |
| **COMMIT** | 3.8 | Commit Phase 3 with reference to phase number |

---

## Phase 4: Admin UI (Optional) (Gated)

**Phase 4 is OPTIONAL to implement.** However, if Phase 4 IS implemented, a full TDD cycle (RED→GREEN→REFACTOR→COMMIT) is mandatory — not optional. There is no partial TDD for optional phases.

### TDD Cycle

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|-------|-------------------|-------------------|----------|--------|
| Phase 4 | `test_exception_admin_page_renders` — assert admin page renders with filter controls | Admin Streamlit page with filters, resolution workflow, CSV export | Review UI layout, verify filter performance | Phase 4 commit with phase reference |

### Steps

| Phase | Step | Action |
|------|------|--------|
| **RED** | 4.1 | Add `test_exception_admin_page_renders` to `tests/frontend/test_exception_admin.py` — assert admin page renders with filter controls |
| **RED** | 4.2 | Verify RED test FAILS: `uv run pytest tests/frontend/test_exception_admin.py -v` |
| **GREEN** | 4.3 | Create `src/frontend/pages/exception_admin.py` Streamlit page |
| **GREEN** | 4.4 | Add filters: date range, user, exception type, resolution status |
| **GREEN** | 4.5 | Display stack trace and context in expandable sections |
| **GREEN** | 4.6 | Add resolution workflow: mark as resolved with notes |
| **GREEN** | 4.7 | Add export to CSV functionality |
| **GREEN** | 4.8 | Add page to Streamlit navigation |
| **GREEN** | 4.9 | Verify Phase 4 tests PASS: `uv run pytest tests/frontend/test_exception_admin.py -v` |
| **REFACTOR** | 4.10 | Review UI layout, verify filter performance |
| **COMMIT** | 4.11 | Commit Phase 4 with reference to phase number |

---

## Documentation Sources

| Source | Description | Version/Date | URL |
|--------|-------------|--------------|-----|
| Python `logging` Module | Standard library logging patterns for exception capture | 3.12 | https://docs.python.org/3/library/logging.html |
| Python `traceback` Module | Stack trace extraction and formatting | 3.12 | https://docs.python.org/3/library/traceback.html |
| SQLAlchemy ORM Session Management | Async session patterns and error-safe commits | ^2.0 | https://docs.sqlalchemy.org/ |
| Existing UI Error Handler | Current `handle_ui_error()` in `src/frontend/utils/errors.py` | Current | `src/frontend/utils/errors.py` |
| Streamlit Pages Pattern | Admin page structure for Phase 4 | Current | `src/frontend/pages/*.py` |

---

> **Approval Tracking**: Approvals are tracked via GitHub Issue comments (e.g., `AI:  ✅ Approved: Phase 1`), NOT in the issue body. Issue body edits destroy history.

🤖 ✨ Created by OpenCode (glm-5): Issue #51

---

REVISED 2026-04-23: Added per-phase TDD RED/GREEN cycle structure. Every Success Criterion (SC-1 through SC-10) is now mapped to a specific test function with `# SC-N:` comment markers. Phase steps are reordered so RED test writing (steps 1.x) precedes GREEN implementation (steps 2.x), per incremental-build discipline. Each phase concludes with REFACTOR and COMMIT steps.

REVISED 2026-05-22: Added Evidence Type column to all SC rows. Appended SC-11 (DB failure resilience), SC-12 (stack trace truncation), SC-13 (concurrent logging safety). Added per-phase TDD cycle summary tables with RED/GREEN/REFACTOR/COMMIT columns. Clarified Phase 4 optional TDD requirement: optional to implement, mandatory TDD if implemented. Mapped new SCs to Phase 2 RED/GREEN steps.
