# Plan: Fix Revert Dialog Record Count

## Status: ✔️ Completed

## Problem

The `confirm_revert_dialog` displays `session_data['record_count']` which is the rollback-specific
`"reversible/total"` string from `get_recent_sessions()` — i.e., records where the session is still
the latest leaf node. This is the wrong metric for the revert action.

For revert, the meaningful count is: **how many records in this session have post-import edits that
would actually be reverted** (later history entries exist AND record is not locked). The current
display misleads the user about what will happen.

## Fix

### 1. ✔️ Add `get_revert_preview_count(session_id)` to `UploadService`

- File: `src/services/upload_service.py`
- New static method that queries: for each distinct `record_id` in `edit_history` for the session,
  count those where (a) the record exists, (b) is not locked, and (c) has at least one history entry
  with `id > earliest_session_entry.id`.
- Returns `{'will_revert': N, 'skipped_locked': M, 'already_current': K, 'total': T}`.

### 2. ✔️ Pass revert preview counts into `confirm_revert_dialog`

- File: `src/frontend/pages/batch_rollback.py`
- In the `↩️` button handler, call `UploadService.get_revert_preview_count(session_id)` and merge
  the result into the `session_data` dict passed to `confirm_revert_dialog`.
- In `confirm_revert_dialog`, replace the `record_count` line with a breakdown using the new fields:
  `will_revert`, `skipped_locked`, `already_current`, `total`.

### 3. ✔️ Update plan and archive

---

## Notes

- No new tests required: the service method is a read-only preview query; the existing revert tests
  already cover the actual revert logic. A smoke-check lint pass suffices.
