# Plan: Disable ↩️ and 🗑️ Buttons When No Records Qualify

## Status: 🔄 Pending

## Background

The `↩️` (revert post-import changes) and `🗑️` (delete records added after import) buttons on the
Batch Rollback page are always enabled. They should be disabled when there is nothing to act on:

- `↩️` disabled when `will_revert == 0` (no changed records for the batch).
- `🗑️` disabled when `will_delete == 0` (no new records added after the import timestamp).

Streamlit's `disabled=` parameter is evaluated at render time, so both previews must be fetched
during row rendering — not inside the click handler.

## Scope

`src/frontend/pages/batch_rollback.py` only. No service changes required.

## Steps

### 1. 🔄 Pending — Fetch previews at row render time

- In the `for s in page_sessions:` loop, before rendering buttons, call:
  - `UploadService.get_revert_preview_count(s['session_id'])` → `revert_preview`
  - `UploadService.get_post_import_new_records_preview(s['session_id'])` → `delete_new_preview`
- Move the `from src.services.upload_service import UploadService` import to the top of `main()`
  (or module level) to avoid repeated inline imports.

### 2. 🔄 Pending — Pass `disabled=` to buttons

- `↩️` button: `disabled=(revert_preview['will_revert'] == 0)`
- `🗑️` button: `disabled=(delete_new_preview['will_delete'] == 0)`
- Remove the now-redundant inline preview calls from inside the click handlers (previews already
  available from step 1); pass them directly into the dialogs.

### 3. 🔄 Pending — Verify and archive

- Lint both modified files.
- Run `JUNIE_PRIVATE_DB=true uv run python -m pytest tests/services/test_rollback.py -v`.
- Archive this plan.
