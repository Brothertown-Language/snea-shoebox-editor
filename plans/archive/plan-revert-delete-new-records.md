# Plan: Revert — Also Delete Records Added After Import

## Status: ✔️ Completed

## Background

The existing `↩️` "Revert post-import changes" action restores records to their post-import state
by discarding later edits. It does **not** touch records that were created as *new* records after
the import — those records have no entry in the session's `edit_history`, so they are invisible to
the revert logic.

The user wants an additional option on the Batch Rollback page to **also delete records that were
added as new after the batch was imported**, with correct counts in the confirmation dialog.

## Answer to the User's Question

No — the current `↩️` revert does **not** un-add records created after the import. Those records
have no `edit_history` entry for the session, so the revert logic never sees them.

## Scope

A new, separate action button `🗑️+` (or similar) per row on the Batch Rollback page:
- Deletes records created (via `edit_history` with `prev_data IS NULL`) after the batch's import
  timestamp, scoped to the same source as the session.
- Skips locked records.
- Shows a preview count in the confirmation dialog (will_delete, skipped_locked, total).

**Out of scope**: modifying the existing `↩️` revert behavior.

## Steps

### 1. ✔️ Completed — `UploadService.get_post_import_new_records_preview(session_id)`

- File: `src/services/upload_service.py`
- New static read-only method.
- Finds the session's import timestamp (earliest `edit_history.timestamp` for `session_id`).
- Finds the session's source (via `records.source_id` for any record in the session).
- Counts records in that source where the earliest `edit_history` entry has `prev_data IS NULL`
  and `timestamp > session_import_timestamp` (i.e., created after the import).
- Returns `{'will_delete': N, 'skipped_locked': M, 'total': T}`.

### 2. ✔️ Completed — `UploadService.delete_post_import_new_records(session_id, user_email, progress_callback)`

- File: `src/services/upload_service.py`
- New static method.
- Same discovery logic as the preview method.
- For each qualifying record: skip if locked, otherwise delete search entries, history, and record.
- Audit-logs as `batch_delete_new_records`.
- Returns `{'deleted_count': N, 'skipped_locked': M}`.

### 3. ✔️ Completed — `confirm_delete_new_dialog()` + new button in `batch_rollback.py`

- File: `src/frontend/pages/batch_rollback.py`
- New `@st.dialog("Delete Records Added After Import")` — same pattern as `confirm_revert_dialog`.
- Shows preview counts: will_delete, skipped_locked, total.
- Per-row action buttons expand from 3 to 4 columns; new `🗑️` button (key `delnew_<session_id>`,
  help "Delete records added after this batch was imported").

### 4. ✔️ Completed — Tests

- File: `tests/services/test_rollback.py`
- Three cases:
  1. No new records after import → `deleted_count=0`.
  2. New records present, unlocked → deleted.
  3. New records present, locked → skipped.

### 5. ✔️ Completed — Update plan and archive
