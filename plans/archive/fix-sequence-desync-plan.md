# Plan: Fix PostgreSQL Sequence Desync After Prod→Local Sync

## Status: IMPLEMENTED

## Problem
After `sync_prod_to_local.py` copies all rows with explicit `id` values, PostgreSQL sequences
are not advanced. This causes `UniqueViolation` on the next INSERT into any table.
Confirmed broken: `records`, `user_activity_log`. All 12 integer-PK tables are at risk.

## Solution
Add a `reset_all_sequences()` helper in two places:
1. `scripts/sync_prod_to_local.py` — runs once after all tables are synced (primary fix).
2. `src/services/identity_service.py` — runs on first login per session (safety net).

---

## Changes

### 1. `scripts/sync_prod_to_local.py`

- Add a `reset_all_sequences(local_engine)` function after the sync loop (after line 143).
- Uses `pg_get_serial_sequence` to avoid hardcoding sequence names.
- Iterates all tables in `Base.metadata.sorted_tables` that have an integer `id` column.
- Calls `setval(seq, COALESCE(MAX(id), 1))` for each.
- Log each reset with `log_message`.
- Call `reset_all_sequences(local_engine)` after the sync loop completes (after line 144).

### 2. `src/services/identity_service.py`

- Add a `_reset_sequences()` private static method to `IdentityService`.
- Uses `get_session()` and executes the same `pg_get_serial_sequence` / `setval` pattern.
- Wraps in try/except — logs warning on failure, never raises (must not block login).
- Call `IdentityService._reset_sequences()` inside `sync_identity()` when
  `is_identity_synchronized()` is False (i.e., first login only), after
  `fetch_github_user_info` returns successfully.

### 3. Pydoc and Code Comments (both locations)

- In `sync_prod_to_local.py`: add a docstring to `reset_all_sequences()` stating:
  - Purpose: resets all integer-PK sequences after a prod→local data copy.
  - **Maintenance note**: the table list is derived dynamically from `Base.metadata.sorted_tables`
    (integer `id` columns only), so it automatically covers new tables added to the ORM.
    If a table is removed from the ORM or its PK column is renamed away from `id`, verify
    the function still behaves correctly.
- In `identity_service.py`: add a docstring to `_reset_sequences()` stating:
  - Purpose: safety-net sequence reset on first login to self-heal after any prod→local sync
    that did not run `sync_prod_to_local.py` (or ran an older version without the reset).
  - **Maintenance note**: uses `pg_get_serial_sequence` dynamically — no hardcoded table list.
    When tables are added, removed, or their PK column renamed, re-verify this method still
    covers all affected sequences. If a new table is added that is NOT in `Base.metadata`
    (e.g., a raw SQL table), it must be added explicitly here.

---

## Sequence Reset SQL Pattern (both locations)

```sql
DO $$
DECLARE
    t text;
    seq text;
BEGIN
    FOR t IN VALUES
        ('matchup_queue'), ('edit_history'), ('schema_version'), ('search_entries'),
        ('users'), ('user_preferences'), ('user_activity_log'), ('permissions'),
        ('sources'), ('languages'), ('record_languages'), ('records')
    LOOP
        seq := pg_get_serial_sequence(t, 'id');
        IF seq IS NOT NULL THEN
            EXECUTE format('SELECT setval(%L, COALESCE((SELECT MAX(id) FROM %I), 1))', seq, t);
        END IF;
    END LOOP;
END $$;
```

---

## Checklist

- [x] `sync_prod_to_local.py`: add `reset_all_sequences()` function
- [x] `sync_prod_to_local.py`: call after sync loop
- [x] `identity_service.py`: add `_reset_sequences()` static method
- [x] `identity_service.py`: call from `sync_identity()` on first login
- [x] Verify no login is blocked if reset fails (exception is caught)
- [x] `sync_prod_to_local.py`: add maintenance docstring to `reset_all_sequences()`
- [x] `identity_service.py`: add maintenance docstring to `_reset_sequences()`
