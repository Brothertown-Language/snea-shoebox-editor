# SQLAlchemy Autoflush PK Collision — Query.delete() Deferred Execution

Date: 2026-06-14

## Context

Migration `_migrate_reprocess_all_records` (v2026030207140) calls `reprocess_all_records()` which iterates over 7,606 records. Each iteration calls `populate_search_entries()` and `_update_record_languages()` per record. SQLAlchemy's autoflush fires on the next record's `session.get()` call, flushing pending INSERTs from the previous record before the DELETEs for the current record have executed.

## Findings

### Root Cause

SQLAlchemy's `Query.delete()` does not execute immediately — it's deferred until flush. When the next iteration's `session.get(Record, rid)` triggers an autoflush, SQLAlchemy flushes all pending operations in order: INSERTs first (from the previous record's `session.add()` calls), then DELETEs (from the current record's `Query.delete()` calls). The INSERTs collide with existing rows because the DELETEs haven't run yet.

### Fix: Two Approaches

**Approach 1 — `session.flush()` after ORM deletes (used in `populate_search_entries()`):**
Retained ORM `Query.delete()` for all four tables but added `session.flush()` after the deletes to force execution before the next iteration's INSERTs. The flush ensures DELETEs execute before the next record's `session.add()` calls accumulate.

**Approach 2 — Raw SQL DELETE (used in `_update_record_languages()`):**
Replaced `session.query(RecordLanguage).filter_by(record_id=record.id).delete()` with `session.execute(text("DELETE FROM record_languages WHERE record_id = :rid"), {"rid": record.id})`. Raw SQL DELETE executes immediately and is not deferred by autoflush.

**Safety net:** `session.commit()` after each record in `reprocess_all_records()` prevents accumulation of pending operations across the 7,606-record loop.

### Why `session.flush()` Works

The original collision sequence was:
1. Record N: `session.add()` → pending INSERTs
2. Record N+1: `session.get()` triggers autoflush → flushes INSERTs (record N) **before** DELETEs (record N+1) → collision

With `session.flush()` after the deletes:
1. Record N: `Query.delete()` → deferred
2. `session.flush()` → forces DELETE to execute **immediately**
3. `session.add()` → pending INSERTs for record N (safe — record N's rows were just deleted)
4. Record N+1: `session.get()` triggers autoflush → flushes only INSERTs (record N) — no collision because DELETEs already ran

### Test Evidence

- `test_populate_search_entries_replaces_existing` — explicitly tests the delete-then-insert path: pre-inserts an old `SearchEntry`, calls `populate_search_entries`, asserts the old entry was replaced with the correct new term. Passes.
- `test_populate_search_entries` — basic create case. Passes.

## Recommendation

For simple per-table deletes in a loop, `session.flush()` after ORM `Query.delete()` is sufficient and avoids raw SQL. For complex cases or when the ORM delete pattern is unreliable, use raw SQL `session.execute(text("DELETE FROM ... WHERE ..."))` which executes immediately and is not deferred by autoflush.

## Files Referenced

| File | Lines |
|------|-------|
| `src/services/upload_service.py` | 1767-1772 (populate_search_entries), 1203-1213 (_update_record_languages), 1878-1879 (reprocess_all_records per-record commit) |
| `tests/services/test_upload_service.py` | 1041-1063 (test_populate_search_entries, test_populate_search_entries_replaces_existing) |
