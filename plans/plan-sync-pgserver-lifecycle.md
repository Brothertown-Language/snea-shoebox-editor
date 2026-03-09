# Plan: sync_prod_to_local — pgserver lifecycle (stop-only-if-started)

**Status:** 🔄 Pending
**File:** `scripts/sync_prod_to_local.py`, `src/database/connection.py`

---

## Problem

The sync script currently always starts pgserver via `_start_pgserver_core()`, which registers
`atexit._stop_local_db` unconditionally. This means if pgserver was already running (e.g., the
Streamlit app is live), the sync script will stop it on exit — disrupting the running app.

The correct behaviour:
- If pgserver was **already running** before the script ran → **do not stop it** on exit.
- If pgserver was **not running** and the script started it → **stop it** on exit (current atexit behaviour).

---

## Root Cause

`_start_pgserver_core()` always calls `atexit.register(_stop_local_db)` regardless of whether
pgserver was already running. There is no pre-flight check for an already-running instance.

---

## Fix Strategy

### In `src/database/connection.py` — `_start_pgserver_core()`

1. Before calling `pgserver.get_server()`, detect whether pgserver is already running by checking
   if `postmaster.pid` exists **and** the process in it is alive.
2. Return a boolean `was_already_running` alongside the URI — or expose it via a module-level flag.
3. Only register `atexit._stop_local_db` if pgserver was **not** already running.

Preferred approach: add a module-level `_pg_server_was_preexisting: bool = False` flag.
Set it to `True` in `_start_pgserver_core()` when a live instance is detected. The atexit handler
`_stop_local_db` checks this flag and skips cleanup if `True`.

### In `scripts/sync_prod_to_local.py` — `_ensure_pgserver()`

No changes needed if the flag approach is used — the atexit handler in `connection.py` handles it.

---

## Steps

### 1. 🔄 Add `_pg_server_was_preexisting` flag to `connection.py`

- Add module-level `_pg_server_was_preexisting: bool = False` near the other globals.
- In `_start_pgserver_core()`: before the `pgserver.get_server()` call, check if `postmaster.pid`
  exists and the PID in it is alive (`os.kill(pid, 0)` succeeds). If yes, set
  `_pg_server_was_preexisting = True`.
- In `_stop_local_db()`: if `_pg_server_was_preexisting` is `True`, log and skip cleanup.

### 2. 🔄 Verify

- `uv run python -m py_compile src/database/connection.py` — no errors.
- `uv run python -m py_compile scripts/sync_prod_to_local.py` — no errors.

---

## Checklist

- [ ] No Streamlit imports added to `_start_pgserver_core()`
- [ ] `_stop_local_db()` respects the preexisting flag
- [ ] Both files compile clean
- [ ] No scope crossing into `src/` beyond `connection.py`
