STATUS: 3 (COMPLETE)
CREATED: 2026-06-14
CLOSED: 2026-06-14

> **Full spec: [Issue #1300](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1300)**

## Problem

Migration `_migrate_reprocess_all_records` (v2026030207140) calls `reprocess_all_records()` which iterates over 7,606 records and calls `populate_search_entries()` and `_update_record_languages()` per record. SQLAlchemy's autoflush fires on the next record's `session.get()` call, flushing pending INSERTs from the previous record before the DELETEs for the current record have executed. This causes `UniqueViolation` on `search_entries_pkey` and `record_languages_pkey` because the INSERTs collide with existing rows that the DELETEs haven't removed yet.

Additionally, `reprocess_all_records()` used `get_session()` to obtain its own database session, which could connect to a different pgserver instance than the migration's engine — causing the migration to run against the wrong database.

## Root Cause

SQLAlchemy's `Query.delete()` does not execute immediately — it's deferred until flush. When the next iteration's `session.get(Record, rid)` triggers an autoflush, SQLAlchemy flushes all pending operations in order: INSERTs first (from the previous record's `session.add()` calls), then DELETEs (from the current record's `Query.delete()` calls). The INSERTs collide with existing rows because the DELETEs haven't run yet.

## Fix Applied

Four changes:

1. **`populate_search_entries()`**: Retained ORM `Query.delete()` but added `session.flush()` after deletes to force execution before next iteration's INSERTs.
2. **`_update_record_languages()`**: Replaced ORM delete with raw SQL `session.execute(text("DELETE FROM ..."))` which executes immediately.
3. **`reprocess_all_records()`**: Added per-record `session.commit()` and optional `session` parameter.
4. **`_migrate_reprocess_all_records()`**: Passes migration's own engine session instead of using `get_session()`.

## Files Changed

| File | Change |
|------|--------|
| `src/services/upload_service.py` | flush after deletes, raw SQL in _update_record_languages, per-record commit, optional session param |
| `src/database/migrations.py` | Pass migration's own engine session to reprocess_all_records |

## Verification

- All 41 tests in `tests/services/test_linguistic_service.py` pass
- All 60 tests in `tests/services/test_upload_service.py` pass

🤖 Co-authored with AI: OpenCode (deepseek-v4-flash-free)