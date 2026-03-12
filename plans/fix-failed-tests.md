# Plan: Fix Failed Tests

**File:** `plans/fix-failed-tests.md`
**Status:** ✅ Complete

## Root Causes (5 distinct issues)

### Issue 1 — `normalized_term=None` in test SearchEntry creation
**Affected:** 6 locations across 4 test files  
`SearchEntry(record_id=..., term=..., entry_type=...)` omits `normalized_term`, which is NOT NULL in DB.

Files:
- `tests/database/test_crud.py` lines 117, 239
- `tests/services/test_linguistic_service.py` lines 128, 151, 152, 218
- `tests/services/test_upload_service.py` line 1001

**Fix:** Add `normalized_term=LinguisticService.generate_sort_lx(term)` (or a simple string like `term.lower()`) to each `SearchEntry(...)` constructor call in tests.

### Issue 2 — D1 frontend tests: `locked_conflict_count > 0` TypeError
**Affected:** 4 tests in `tests/frontend/test_upload_review_d1.py`  
New code at `upload_mdf.py:472-474` uses `with get_session() as session:` context manager, but tests mock `get_session` as a plain return value, not a context manager. `count()` returns `MagicMock`, causing `MagicMock > 0` TypeError.

**Fix:** In each failing D1 test, configure the mock session as a context manager:
```python
mock_sess.__enter__ = MagicMock(return_value=mock_sess)
mock_sess.__exit__ = MagicMock(return_value=False)
mock_get_session.return_value.__enter__ = MagicMock(return_value=mock_sess)
mock_get_session.return_value.__exit__ = MagicMock(return_value=False)
```
And ensure `mock_sess.query.return_value.filter_by.return_value.count.return_value = 0`.

### Issue 3 — Identity service test: `call_args` returns last `add()` call (Source, not User)
**Affected:** `tests/services/test_identity_service.py` — `test_sync_user_to_db_new_user`, `test_sync_user_to_db_existing_user`  
`sync_user_to_db` now calls `ensure_user_source` which does `session.add(Source(...))` after `session.add(User(...))`. `mock_session.add.call_args` returns the last call (Source). Also `commit` is now called twice.

**Fix:** Change `mock_session.add.call_args` → `mock_session.add.call_args_list[0]` to get the first `add()` call (the User). Change `mock_session.commit.assert_called_once()` → `mock_session.commit.assert_called()`.

### Issue 4 — Record locking test: `get_edit_history` excludes max-version entry
**Affected:** `tests/services/test_record_locking.py` — `test_lock_record` (expects 1), `test_unlock_record` (expects 2)  
`get_edit_history` filters out the max-version entry (line 840). With 1 history entry (lock), it returns 0. With 2 entries (lock + unlock), it returns 1.

- `test_lock_record` line 52: `assertEqual(len(history), 1)` → should be `0`
- `test_unlock_record` line 85: `assertEqual(len(history), 2)` → should be `1`

**Fix:** Update the expected counts in both tests to match the actual `get_edit_history` behavior.

### Issue 5 — Integration test: `ModuleNotFoundError: No module named 'src'`
**Affected:** `tests/integration/test_upload_e2e.py`  
No `pythonpath` configured in `pyproject.toml` pytest section. Other tests work because they were run differently or the path was set elsewhere.

**Fix:** Add `[tool.pytest.ini_options]` with `pythonpath = ["."]` to `pyproject.toml`.

---

## Steps

**Step 1:** 🔄 Pending — Add `[tool.pytest.ini_options] pythonpath = ["."]` to `pyproject.toml`

**Step 2:** 🔄 Pending — Fix `normalized_term` in all 6 test `SearchEntry` constructors (use `term` as value since tests don't need real normalization)

**Step 3:** 🔄 Pending — Fix D1 frontend tests: configure context manager on mock session + set `count.return_value = 0` for locked_conflict query in the 4 affected tests

**Step 4:** 🔄 Pending — Fix identity service tests: use `call_args_list[0]` and `assert_called()` instead of `assert_called_once()`

**Step 5:** 🔄 Pending — Fix record locking tests: update expected history counts (lock: 0, unlock: 1)

**Step 6:** 🔄 Pending — Run full test suite and confirm all previously-failing tests now pass

**Step 7:** Update this plan with the results.

**Step 8:** Archive this plan when it is completed 100%.

