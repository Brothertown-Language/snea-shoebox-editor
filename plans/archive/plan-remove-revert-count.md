# Plan: Remove count from revert post-import dialog

**Status:** completed completed  
**Created:** 2026-03-11  
**Scope:** `src/frontend/pages/batch_rollback.py`

## Problem

The "Revert Post-Import Changes" dialog is slow to open because clicking ↩️ calls
`UploadService.get_revert_preview_count(session_id)` before opening the dialog. This is an
expensive DB query that counts records to be reverted. The user just wants a confirmation
prompt — the counts are not needed.

## Fix

**Step 1** — In `batch_rollback.py` line 351–352: remove the `get_revert_preview_count` call
and pass `s` directly (without `revert_preview`) to `confirm_revert_dialog`.

**Step 2** — In `confirm_revert_dialog` (lines 122–128): remove the `preview` block that
displays will_revert, skipped_locked, already_current, and total counts.

**Step 3** — Archive plan.

## Steps

1. 🔄 Pending — Remove `get_revert_preview_count` call and simplify `confirm_revert_dialog` call in button handler.
2. 🔄 Pending — Remove count display lines from `confirm_revert_dialog`.
3. 🔄 Pending — Archive plan.
