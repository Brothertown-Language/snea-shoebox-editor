# Plan: Fast EXISTS Check for Button Enable/Disable

## Status: 🔄 Pending

## Background

The current implementation fetches full count previews (`get_revert_preview_count`,
`get_post_import_new_records_preview`) at row render time to determine whether `↩️` and `🗑️`
buttons should be disabled. These are expensive queries — they iterate all records in the session
and run per-record sub-queries.

The correct approach:
- **Row render time**: cheap EXISTS query (boolean) — is there *any* qualifying record?
- **Dialog open time**: full count query — how many records will be affected?

## Scope

`src/services/upload_service.py` and `src/frontend/pages/batch_rollback.py` only.

## Steps

### 1. 🔄 Pending — Add two fast EXISTS methods to `UploadService`

- `has_revertible_changes(session_id: str) -> bool`
  - EXISTS: any `EditHistory` entry for the session whose `record_id` has a *later* history entry
    (id > earliest for that session), and the record is not locked and not deleted.
  - Single query with EXISTS subquery — no Python-side iteration.

- `has_post_import_new_records(session_id: str) -> bool`
  - EXISTS: any record in the same source, created (prev_data IS NULL in earliest history entry)
    after the session's import timestamp, not locked, not deleted.
  - Single query with EXISTS subquery — no Python-side iteration.

### 2. 🔄 Pending — Update `batch_rollback.py`

- At row render time: replace the two full preview calls with the two new EXISTS calls.
  - `↩️` disabled when `not has_revertible_changes(session_id)`
  - `🗑️` disabled when `not has_post_import_new_records(session_id)`
- In the `↩️` click handler: restore the `get_revert_preview_count()` call (moved back from render
  time) and pass result into `confirm_revert_dialog`.
- In the `🗑️` click handler: restore the `get_post_import_new_records_preview()` call (moved back
  from render time) and pass result into `confirm_delete_new_dialog`.

### 3. 🔄 Pending — Verify and archive

- Lint both modified files.
- Run `JUNIE_PRIVATE_DB=true uv run python -m pytest tests/services/test_rollback.py -v`.
- Archive this plan and the superseded `plan-disable-buttons-no-records.md`.
