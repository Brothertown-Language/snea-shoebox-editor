# Plan: Fix sync_prod_to_local.py pgserver startup & connection

**Status:** ✔️ Completed
**File:** `scripts/sync_prod_to_local.py`, `src/database/connection.py`

---

## Problem

`sync_prod_to_local.py` contains a private `_ensure_pgserver()` reimplementation that:
1. Has a broken guard — if `local_url` contains `@` and doesn't match the hardcoded localhost prefix, it returns early without starting pgserver at all.
2. Returns the raw socket URI from `pgserver.get_uri()`, which causes psycopg2 to attempt a socket connection that fails.

The root cause of the divergence: `_auto_start_pgserver()` in `connection.py` depends on `st.session_state` (Streamlit), so it cannot be called from a CLI script. A standalone reimplementation was written instead, but incorrectly.

## Fix Strategy

Extract a **Streamlit-free** pgserver start helper into `connection.py`, then call it from both `_auto_start_pgserver()` and `sync_prod_to_local.py`. This eliminates the divergence.

---

## Steps

### 1. ✔️ Extract `_start_pgserver_core()` in `src/database/connection.py`

- Add a new private function `_start_pgserver_core(db_path) -> str` that:
  - Calls `pgserver.get_server(str(db_path))` (with retry/force-stop logic already in `_auto_start_pgserver`)
  - For non-Junie context: calls `_enable_tcp_listening()` and returns `postgresql://postgres:@localhost:5432/postgres`
  - For Junie context (`JUNIE_PRIVATE_DB` set): returns `_pg_server.get_uri()` (socket)
  - Contains no Streamlit imports or `st.*` calls
- Refactor `_auto_start_pgserver()` to delegate the core start logic to `_start_pgserver_core()`

### 2. ✔️ Replace `_ensure_pgserver()` in `scripts/sync_prod_to_local.py`

- Remove the broken `_ensure_pgserver()` function entirely
- Import and call `_start_pgserver_core()` from `src.database.connection`
- The sync script always operates on the local dev DB (never Junie private DB), so `JUNIE_PRIVATE_DB` will not be set during normal sync runs — TCP URI will be returned

### 3. ✔️ Verify

- Run `uv run python scripts/sync_prod_to_local.py` (requires prod secrets) — confirm pgserver starts and TCP connection is used
- Confirm no regression in `_auto_start_pgserver()` by checking that the Streamlit app still starts correctly (log inspection via `tmp/streamlit.log`)
