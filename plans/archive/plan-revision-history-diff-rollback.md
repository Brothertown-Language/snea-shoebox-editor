# Plan: Revision History — Diff Display & Rollback

**Status:** ✅ Complete

## Overview
The revision history expander on the records view currently shows only version number, user, timestamp, and change summary. It does not render a diff against the current record, and in edit mode there is no rollback button. This plan fixes both gaps.

## What & Why
- **`get_edit_history` is missing `prev_data` / `current_data`** — the `EditHistory` model stores both MDF snapshots but the service method omits them from the returned dict. Without them the UI cannot compute a diff.
- **No diff rendering** — the expander needs to show the historical snapshot with diff highlights against the live record MDF, using the same `compute_mdf_line_diffs` + `render_mdf_block(diagnostics=...)` pattern already used in the upload match review view. The live record is already displayed above the expander, so only the historical snapshot needs to be rendered inside it.
- **No rollback button** — in edit mode, each history entry should offer a "↩ Rollback" button that loads `current_data` of that entry into `pending_edits` for the record (same mechanism as manual editing, no auto-save).

## Scope
- `src/services/linguistic_service.py` — `get_edit_history`: add `current_data` to returned dicts.
- `src/frontend/pages/records.py` — Revision History expander: render side-by-side diff + rollback button in edit mode.
- No schema changes. No new service methods needed.

## Steps

### Phase 1 — Service layer
1. ✔️ In `get_edit_history`, include `current_data` in each returned dict.

### Phase 2 — UI: diff display
1. ✔️ In the Revision History expander, for each history entry call `compute_mdf_line_diffs(entry['current_data'], mdf_data)` to get `(hist_diags, _live_diags)`. Render only the historical snapshot via `render_mdf_block(entry['current_data'], diagnostics=hist_diags)`. The live record is already displayed above the expander — no second column needed. Add `compute_mdf_line_diffs` to the import from `ui_utils`.

### Phase 3 — UI: rollback button (edit mode only)
1. ✔️ When `is_editing` is True (global edit mode or local edit), show a "↩ Rollback" button per history entry. On click, set `st.session_state.pending_edits[record_id] = entry['current_data']` and `st.rerun()`. No auto-save — user must still press Update/Save All.

### Phase 4 — Completion
1. ✔️ Update this plan to reflect actual progress and declare completion if all steps are done.

## Out of Scope
- No changes to batch_rollback.py.
- No new tests unless explicitly requested.
