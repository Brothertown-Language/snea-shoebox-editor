# Plan: Fix Pre-Existing Test Failures

**File:** `plans/fix-preexisting-failures.md`
**Status:** ✔️ Completed

---

## Root Cause Analysis

All 4 failures are **stale tests** — source code changed and tests were not updated. None should be removed.

---

### Failure 1 — `test_production_detection` (`tests/database/test_production_safety.py:8`)

`is_production()` checks `st.secrets` first (line 64 of `connection.py`). In the test environment, `st.secrets` access raises an exception (no secrets file), so it falls through to `getpass.getuser()`. The mock `src.database.connection.getpass.getuser` should work — but the test is actually failing because `st.secrets` is not raising; it's returning something that evaluates as not having `"runtime"` key, so it falls through correctly. 

**Actual root cause**: Running the test in isolation confirms `is_production()` returns `False` even when `getuser` is mocked to `"appuser"`. The `st.secrets` block at line 63–68 catches all exceptions, but in the test environment `st.secrets` is a real Streamlit object that does NOT raise — it just returns an empty dict-like object. So `"runtime" in st.secrets` evaluates to `False`, falls through to `getpass.getuser()`. The mock path is correct.

Re-checking: the test **does** mock `src.database.connection.getpass.getuser` but `is_production()` imports `getpass` locally at line 74 (`import getpass`). The local import re-binds the name, bypassing the module-level mock. The fix is to mock `getpass.getuser` at the point of use: `builtins` or patch the module-level `getpass` in `src.database.connection`.

**Fix:** Change mock target from `src.database.connection.getpass.getuser` to `src.database.connection.getpass` with a mock that has `.getuser` set, OR add `also patch st.secrets` to ensure the first branch is skipped. Simplest: also patch `st.secrets` to raise, so the fallback runs, and keep the existing `getpass.getuser` mock. Actually simplest: patch `src.database.connection.is_production` directly in `test_pgserver_safety`, and fix `test_production_detection` by also patching `streamlit.secrets` to raise an exception so the `st.secrets` branch is bypassed.

**Fix (concrete):**
- `test_production_detection`: Add `@patch("streamlit.secrets", new_callable=lambda: type('S', (), {'__contains__': lambda s,k: False})())` — or simpler: patch `src.database.connection.st.secrets` to raise `FileNotFoundError`. Actually simplest: patch `src.database.connection.getpass` (the module) so `.getuser` is the mock.
- `test_pgserver_safety`: Also patch `src.database.connection._pg_server` to `None` (so the early-return at line 483 is skipped) AND patch `src.database.connection.is_production` to return `True`.

---

### Failure 2 — `test_pgserver_safety` (`tests/database/test_production_safety.py:25`)

`_auto_start_pgserver()` returns a cached URI at line 486 because `_pg_server` is already running in the test environment — it never reaches the `is_production()` check at line 472.

**Fix:** Patch `src.database.connection._pg_server` to `None` so the cache-hit branch is skipped, AND patch `src.database.connection.is_production` to return `True` (avoids needing to fight the `getpass` mock issue).

---

### Failure 3 — `test_rehydration_failure_clears_state` (`tests/frontend/test_token_rehydration.py`)

Test expects `st.error("Session expired or invalid. Please log in again.")` but `sync_identity` in `identity_service.py:111` now calls `st.error("Failed to fetch user information from GitHub: ...")` itself before returning `False`. The app-level message no longer exists.

**Fix:** Update the assertion to match the actual error message emitted by `sync_identity`: `st.error.assert_called_with("Failed to fetch user information from GitHub: ")` — but since the exception message is dynamic, use `assert_called()` and check `call_args[0][0]` contains `"Failed to fetch user information"`.

---

### Failure 4 — `test_handle_ui_error_development` (`tests/frontend/test_ui_utils_errors.py:41`)

Test expects `handle_ui_error` to call `st.expander(user_message, expanded=True)` and `st.error` with exception details. Current `handle_ui_error` (line 17–30 of `ui_utils.py`) no longer uses `st.expander` — it calls `st.error(user_message)`, `st.warning(str(e))`, and `st.info(...)`.

**Fix:** Update test assertions to match current behavior:
- Remove `mock_st_expander.assert_called_once_with(...)` 
- Change `mock_st_error.assert_called()` + `assertIn("ValueError", ...)` to `mock_st_error.assert_called_once_with(user_message)`
- Add `mock_st_warning = patch("streamlit.warning")` and assert `mock_st_warning.assert_called_once_with("Internal dev error")`
- Keep `mock_st_info.assert_called()` (still valid — `st.info` is still called in dev mode)

---

## Steps

**Step 1:** ✔️ Fix `test_production_safety.py` — both tests
- `test_production_detection`: patch `src.database.connection.st` secrets to raise, keeping `getpass.getuser` mock
- `test_pgserver_safety`: patch `_pg_server=None` and `is_production` to return `True`

**Step 2:** ✔️ Fix `test_token_rehydration.py` — update expected error message assertion

**Step 3:** ✔️ Fix `test_ui_utils_errors.py` — update dev-mode assertions to match current `handle_ui_error` behavior (no expander; uses `st.warning` for exception detail)

**Step 4:** ✔️ Run all 4 previously-failing tests and confirm green — 5 passed in 0.92s

**Step 5:** ✔️ Verify that all tests pass

**Step 6:** ✔️ Updated plan — all steps complete.
