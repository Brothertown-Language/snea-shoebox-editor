# Plan: Fix Sequence Reset Ordering — Move to init_db()

## Status: IMPLEMENTED

## Problem

The sequence reset fires **after** the first audit INSERT, not before it.

Timeline from `streamlit.log` (all at 21:40:44):
1. `fetch_github_user_info()` is called
2. Inside it: `AuditService.log_activity(... "login" ...)` → **UniqueViolation** ❌
3. `fetch_github_user_info()` returns `True`
4. `sync_identity()` calls `_reset_sequences()` → "Sequence reset complete" ✅ (too late)

The reset must happen **before** any INSERT — ideally at app startup, not in the login path.

## Root Cause

`_reset_sequences()` is called in `sync_identity()` after `fetch_github_user_info()` returns.
But `fetch_github_user_info()` calls `sync_user_to_db()` and `AuditService.log_activity()`
internally — both of which do INSERTs — before returning.

## Solution

Move `_reset_sequences()` into `init_db()` in `src/database/connection.py`.

`init_db()` is the correct hook because:
- It is called once at app startup (before any user interaction or INSERTs).
- `get_engine()` is `@st.cache_resource` — singleton — so `init_db()` effectively runs once per app lifecycle.
- It already runs migrations; sequence reset is a natural companion to schema initialization.

The `_reset_sequences()` method stays in `IdentityService` (or moves to a shared utility — see Change #2).
`sync_identity()` is restored to its original one-liner (no reset call).

## Changes

### 1. `src/database/connection.py` — `init_db()`

- After `MigrationManager(engine).run_all()`, call the sequence reset function.
- Import and call `IdentityService._reset_sequences()` — OR extract the logic into a
  standalone function in `connection.py` to avoid a circular import (see note below).

**Circular import note**: `identity_service.py` imports from `src.database` (which includes
`connection.py`). Calling `IdentityService._reset_sequences()` from `connection.py` would
create a circular import. Therefore, the sequence reset logic must be extracted into a
standalone function `_reset_sequences(engine)` directly in `connection.py`, and
`IdentityService._reset_sequences()` updated to delegate to it (or be removed).

### 2. `src/database/connection.py` — new `_reset_sequences(engine)` function

- Standalone module-level function (not a class method).
- Same dynamic ORM iteration logic as the existing `IdentityService._reset_sequences()`.
- Called from `init_db()` after migrations.
- Logs via the module logger (`_logger`).
- Wrapped in try/except — logs warning on failure, never raises (must not block startup).
- Full maintenance docstring (same obligations as existing docstring).

### 3. `src/services/identity_service.py` — remove login-path reset

- Remove the `if result: IdentityService._reset_sequences()` block from `sync_identity()`.
- Restore the original one-liner: `return IdentityService.fetch_github_user_info(access_token)`.
- `IdentityService._reset_sequences()` method: remove entirely (logic now lives in `connection.py`).
- Remove the now-unused `from src.database.base import Base` and `from sqlalchemy import Integer, text`
  imports if they were added solely for `_reset_sequences()`.

## Checklist

- [x] `connection.py`: add standalone `_reset_sequences(engine)` function with maintenance docstring
- [x] `connection.py`: call `_reset_sequences(engine)` at end of `init_db()`
- [x] `identity_service.py`: remove `IdentityService._reset_sequences()` method
- [x] `identity_service.py`: restore `sync_identity()` to original one-liner
- [x] `identity_service.py`: remove imports added solely for `_reset_sequences()` if now unused
- [x] Verify ordering: `init_db()` → sequences reset → app ready → login → INSERTs
- [x] Verify no startup is blocked if reset fails (exception is caught)
