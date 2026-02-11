<!-- Copyright (c) 2026 Brothertown Language -->
<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
# Phase C — Upload Page (frontend) ✅

**Status:** Complete (2026-02-08)

### C-1. Register a new Streamlit page for uploads ✅
Add a page entry in `src/services/navigation_service.py` for
`"Upload MDF"` and create the file `src/frontend/pages/upload_mdf.py`
with a minimal placeholder.

### C-2. Add role guard to the upload page ✅
Only users with `editor` or `admin` role may access this page.  Use the
existing `SecurityManager` route-protection pattern.

### C-3. Implement file uploader widget ✅
Use `st.file_uploader` to accept `.txt` and `.mdf` files.  Display the
raw file preview in an expander.

### C-4. Implement source selector ✅
Add a `st.selectbox` populated from the `sources` table so the user can
choose which source collection the upload targets.

### C-4a. Add "Create New Source" option to source selector ✅
Add an option (e.g. `"+ Add new source…"`) at the end of the source
selectbox.  When selected, display inline text inputs for the new source's
`name` and optional `description`.  The `name` field should include a
placeholder hint (e.g. "Natick Dictionary — Trumbull") showing the
convention of combining the document/book title with the author/linguist
in a single value.  No schema change is needed — the existing `name`
column is sufficient (DRY).  On confirmation, insert the new row into the
`sources` table and auto-selected it as the active source for the upload.

### C-5. Parse and display upload summary ✅
On upload, call `UploadService.parse_upload()`, display the count of
entries found, and show a scrollable table of `lx` / `ps` / `ge` values.

### C-6. Implement "Stage & Match" button ✅
On click, call `stage_entries` (which returns a `batch_id`) then
`suggest_matches(batch_id)`.  Store the `batch_id` and results in
`st.session_state`.

### C-6a. Implement pending upload batch selector ✅
Above the review area, display a selectbox listing all pending upload
batches for the current user (from `list_pending_batches`).  Each option
shows the source name, original filename, entry count, and **upload
date/time** (formatted as e.g. `2026-02-08 14:52`).  The date/time is
essential for distinguishing between multiple uploads of the same file.
Selecting a batch loads its `matchup_queue` rows into the review table.
This allows the user to switch between multiple in-progress uploads.

### C-6b. Implement "Re-Match" button ✅
Display a "Re-Match" button next to the batch selector.  On click, call
`rematch_batch(batch_id)` (B-5a) to re-run match suggestions against
the current state of the `records` table.  This is useful when records
have been edited in another session (or by another user) since the
original upload was staged.  The review table refreshes with updated
suggestions.

### Phase C — Implementation Summary

**Source files changed:**
- `src/services/navigation_service.py` — Added `PAGE_UPLOAD` registration,
  nav tree entries (authenticated/unauthenticated), and page-to-path map.
- `src/frontend/pages/upload_mdf.py` — New file implementing all C steps:
  role guard (C-2), file uploader with preview (C-3), source selector with
  create-new option (C-4/C-4a), parse summary table (C-5), Stage & Match
  button (C-6), pending batch selector (C-6a), Re-Match button (C-6b).

**Test files added:**
- `tests/frontend/test_upload_mdf_page.py` — 15 unit tests:
  - 4 tests for role guard (viewer blocked, no role blocked, editor/admin allowed).
  - 2 tests for source selector (options include create-new, inline inputs).
  - 1 test for file uploader (accepts .txt/.mdf).
  - 3 tests for parse summary (display, error, 100-entry sample file).
  - 2 tests for Stage & Match (calls service, blocked without source).
  - 2 tests for pending batch selector (displayed with labels, empty info).
  - 1 test for Re-Match button (calls rematch_batch).

**Test results:** All 130 tests pass (15 new + 115 existing) with zero
regressions.
