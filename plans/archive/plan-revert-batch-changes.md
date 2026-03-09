# Plan: Add "Revert Changes to This Batch" to Batch Rollback

## Overview

Add a third per-row action button to the Batch Rollback page that reverts all non-locked
post-import edits on records belonging to a batch, restoring them to the state they were in
immediately after the batch was imported. This is distinct from the existing 🔙 rollback,
which undoes the import itself.

**Logic**: For each record touched by the session, find the `current_data` of the earliest
`edit_history` entry with that `session_id` — that is the post-import snapshot. If the record
has been edited since (i.e., there are later edit_history entries), and the record is not
locked (`is_locked = False`), restore `mdf_data` to that post-import snapshot and delete the
subsequent history entries. Locked records are skipped and counted.

---

## Steps

### 1. ✔️ Add `revert_batch_changes` to `UploadService`

- File: `src/services/upload_service.py`
- New static method after `rollback_session`.
- For each record in the session:
  - Find the earliest `edit_history` row with `session_id = <sid>` → its `current_data` is the post-import state.
  - Check if any later `edit_history` rows exist for that record (timestamp/id after the session entry).
  - If none → record is already at post-import state, skip (count as `already_current`).
  - If record is locked (`record.is_locked`) → skip (count as `skipped_locked`).
  - Otherwise → restore `record.mdf_data` to post-import snapshot, re-parse lx/hm/ps/ge, delete later history entries, repopulate search entries.
- Returns `{'reverted_count': N, 'skipped_locked': M, 'already_current': K}`.
- Audit log action: `"batch_revert_changes"`.

### 2. ✔️ Add `confirm_revert_dialog` to `batch_rollback.py`

- File: `src/frontend/pages/batch_rollback.py`
- New `@st.dialog("Revert Post-Import Changes")` function.
- Warning message explaining the action (restores to post-import state, skips locked records, cannot be undone).
- Progress bar + status widget (same pattern as `confirm_rollback_dialog`).
- On confirm: call `UploadService.revert_batch_changes(...)`, show success summary, `st.rerun()`.

### 3. ✔️ Add ↩️ action button per row

- File: `src/frontend/pages/batch_rollback.py`
- Expand the `btn_cols` from 2 to 3 columns in the per-row layout.
- Add `↩️` button (key `revert_<session_id>`, help `"Revert post-import changes to this batch"`).
- On click: call `confirm_revert_dialog(s)`.
- Update column widths to accommodate 3 buttons (adjust `c5` column ratio).

### 4. ✔️ Add tests

- File: `tests/` (appropriate test module for upload_service or batch rollback).
- Test: records with no post-import edits → `already_current` count correct, no changes made.
- Test: records with post-import edits, not locked → reverted to post-import snapshot.
- Test: locked records → skipped, `skipped_locked` count correct.

### 5. ✔️ Update plan to reflect completion and archive

---

## Status: ✔️ Complete
