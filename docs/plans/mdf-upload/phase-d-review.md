<!-- Copyright (c) 2026 Brothertown Language -->
<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
# Phase D — Review & Confirm Page (frontend) 🔄

**Status:** In Progress (2026-02-09) — D-1 block and D-2 complete; D-3
effectively superseded by immediate-apply pattern (see below); D-3a
through D-5 pending.

### D-1. Display match review table ✅
Show each staged entry with columns: `lx`, suggested match (existing
`lx` + `ge`), match type badge (`exact` / `base_form`), and a status
selector (`matched` / `create_new` / `create_homonym` / `discard` /
`ignored`).  If `cross_source_matches`
is non-empty, display an informational note (e.g. ℹ️ "Also found in:
Source X, Source Y") so the user is aware of entries in other sources
without those being selectable as match targets.

**Default status logic** — the status selector should pre-select a
sensible default for each entry based on its match results:
- If `record_id_conflict` is true → default to **`create new`**.
- Else if `suggested_record_id` is set with `match_type = 'exact'` →
  default to **`match`**.
- Else if `suggested_record_id` is set with `match_type = 'base_form'`
  → default to **`match`** (but the `base_form` badge alerts the user
  to review).
- Else (no suggestion) → default to **`create new`**.

If `record_id_conflict` is true, display a ⚠️ warning (e.g.
"Record #42 belongs to Source Y — mark as 'create new' to avoid
cross-source conflict") prompting the user to create a new record
instead of reusing the conflicting record number.  The default status
is already set to `create new` for these entries so the user can
simply confirm without extra clicks.

### D-1b. Implement responsive record comparison view ✅
When the user expands or selects a staged entry for review, display the
**new (uploaded) MDF data** alongside the **existing (database) MDF data**
so the user can compare before choosing a status.

- **Wide screens** (e.g. ≥ 768 px or Streamlit's default two-column
  threshold): use `st.columns([1, 1])` to show the comparison
  **side-by-side** — existing data on the **left**, new (uploaded) data
  on the **right**.
- **Narrow screens** (below the threshold): stack the panels
  **over-under** — existing data on **top**, new (uploaded) data on
  **bottom**.

Each panel should display:
- A clear heading: "Existing record (#<id>)" / "New (uploaded)".
- The full MDF text in a read-only `st.code` or `st.text_area` block
  with MDF syntax context (monospaced font).
- If there is no existing match (entry will be a new record), the
  left/top panel shows a placeholder such as "No existing record".

This comparison view is the primary tool the user relies on to decide
whether a pending record should be updated, added as new, or discarded.

### D-1a. Add bulk approval action buttons ✅
Above the review table, display contextual bulk-action buttons:

- **New source** (source has no existing records): show an
  "Approve All as New Records" button that calls
  `approve_all_new_source` (B-6a) and refreshes the table.
- **Existing source**: show two buttons:
  1. "Approve All Matched" — calls `approve_all_by_record_match`
     (B-6b) which **immediately applies** matched entries to the
     live `records` table (updates records, writes `edit_history`,
     populates search entries, and removes queue rows).
  2. "Approve Non-Matches as New" — calls
     `approve_non_matches_as_new` (B-6c) which **immediately creates**
     new records from unmatched entries (writes `edit_history`,
     populates search entries, and removes queue rows).
- **All sources**: show a "Discard All Marked" button that calls
  `discard_marked` (B-7d) to delete all entries with `'discard'`
  status from the batch.

All buttons refresh the review table after execution.  Because the
bulk buttons now apply immediately (rather than just changing status),
the separate D-3 commit buttons are no longer needed for most
workflows.

### D-1c. Add per-record "Apply Now" button ✅
For each entry in the review table, display an **"Apply Now"** button
next to the status selector.  The button is **enabled** only when the
entry has an actionable status (`matched`, `create_new`,
`create_homonym`, or `discard`) and **disabled** when the status is
`pending` or `ignored`.  On click, call `apply_single(queue_id, …)`
(B-7b) to immediately commit that single record to the live `records`
table and `edit_history` (or discard it if status is `'discard'`).
The row is then removed from the review table.  Display a brief inline
confirmation (e.g. ✅ "Applied: ēsh → record #42" or
✅ "Discarded: ēsh").

This lets the user process records one at a time without waiting to
use the batch-level bulk buttons (D-1a).

### D-1 Implementation Summary

**Status:** Complete (2026-02-08)

**Source files changed:**
- `src/frontend/pages/upload_mdf.py` — Added `_render_review_table()` function
  implementing D-1 (review table with status selectors including `discard`
  option and default status logic),
  D-1a (bulk action buttons: "Approve All as New Records" for new sources,
  "Approve All Matched" and "Approve Non-Matches as New" for existing sources,
  and "Discard All Marked" for all sources),
  D-1b (side-by-side MDF comparison view using `st.columns([1,1])`),
  D-1c (per-record "Apply Now" button, enabled for `matched`/`create_new`/
  `create_homonym`/`discard`, disabled for `pending`/`ignored`).
  Added `_set_queue_status()` helper for direct status updates.
  Stage & Match button is now disabled after use (via `upload_staged_file`
  session state key) until a new file is uploaded.  After staging, the view
  immediately reruns to show the review display.

  **Sidebar layout refactor (2026-02-08):** All review controls (back
  button, Re-Match, pagination, bulk actions) moved to `st.sidebar`.
  The main panel is now reserved exclusively for record comparison
  content.  This follows the project-wide UI layout pattern documented
  in `.junie/project-architecture.md` § "UI LAYOUT PATTERN — SIDEBAR
  CONTROLS".

**Test files added:**
- `tests/frontend/test_upload_review_d1.py` — 12 unit tests (16 total after D-2):
  - 1 test for empty batch info message.
  - 1 test for review table rendering (sidebar pagination).
  - 1 test for exact match defaulting to 'matched' status.
  - 1 test for new source showing "Approve All as New Records" button.
  - 1 test for existing source showing two bulk buttons.
  - 1 test for comparison view with existing record.
  - 1 test for no-match placeholder text.
  - 1 test for Apply Now disabled when status is 'ignore'.
  - 1 test for Apply Now enabled when status is 'create_new'.
  - 1 test for pagination page size selector.
  - 1 test for pagination page count display.
  - 1 test for Stage & Match button disabled after staging.

**Test results:** All 143 tests pass (12 new + 131 existing) with zero
regressions.

### D-2. Allow manual match override ✅
Provide a search/select widget so the user can pick a different existing
record instead of the auto-suggested one.

### D-2 Implementation Summary

**Status:** Complete (2026-02-09)

**Source files changed:**
- `src/services/upload_service.py` — Added `search_records_for_override(source_id, query, limit)`
  static method that searches existing records by `lx` or `ge` using case-insensitive
  `ILIKE` matching, scoped to the given source.
- `src/frontend/pages/upload_mdf.py` — Added manual match override widget inside
  `_render_review_table()` as a collapsible `st.expander("🔍 Change match")` per row.
  Contains a search text input, candidate selectbox, and "Confirm Override" button
  that calls `UploadService.confirm_match(queue_id, record_id)`.

**Test files updated:**
- `tests/frontend/test_upload_review_d1.py` — 4 new tests (class `TestManualMatchOverride`):
  - 1 test for override expander rendering.
  - 1 test for search returning candidates and displaying selectbox.
  - 1 test for Confirm Override calling `confirm_match` with chosen record_id.
  - 1 test for empty search results showing info message.

**Test results:** All 147 tests pass (4 new + 143 existing) with zero regressions.

### D-3. Apply action buttons — superseded by immediate-apply pattern ✅

**Note:** The original plan called for four separate commit buttons
("Apply Updates", "Add New Records", "Add & Apply All", "Discard All").
During implementation, the architecture evolved so that bulk actions
(D-1a) and per-record "Apply Now" (D-1c) apply changes **immediately**
to the live `records` table rather than staging status changes for a
separate commit step.  This eliminates the need for D-3's four buttons.

The current apply workflow is:
- **Per-record**: the "Apply Now" button (D-1c) calls `apply_single`
  which writes to `records`, `edit_history`, populates search entries,
  and deletes the queue row in one step.
- **Bulk matched**: "Approve All Matched" (D-1a) calls
  `approve_all_by_record_match` which iterates matched rows and calls
  `apply_single` for each.
- **Bulk new**: "Approve Non-Matches as New" (D-1a) calls
  `approve_non_matches_as_new` which iterates unmatched rows and calls
  `apply_single` for each.
- **Bulk discard**: "Discard All Marked" (D-1a) calls `discard_marked`
  to delete all `'discard'`-status rows.
- **Full batch discard**: `discard_all` (B-7a) remains available
  programmatically but is not currently exposed as a UI button.

The `commit_matched`, `commit_homonyms`, and `commit_new` batch methods
(B-8, B-8a, B-9) still exist in the backend and are tested, but are not
currently called by the frontend — all frontend paths use `apply_single`
instead.

### D-3a. Add "Download Pending Changes" button ⏳
Add a **"Download Pending Changes"** button to the review page that
exports only the pending `matchup_queue` entries for the selected batch
as an MDF-formatted text file.  The download includes **only** staged
entries that have not yet been applied — it does not include committed
records or discarded rows.

- Retrieve all `matchup_queue` rows for the current `batch_id` that
  still have a pending status (not yet committed or discarded).
- Render each row's `new_data` as MDF text using the existing MDF
  formatter.
- Offer the result as a Streamlit download button (`st.download_button`)
  with a filename derived from the batch source name and batch id
  (e.g. `pending_<source>_<batch_id_short>.txt`).
- The button is only visible when the batch has at least one pending
  entry.

This allows linguists to export staged entries, edit them offline in a
text editor, and re-upload corrected MDF files.

### D-4. Display apply results summary ⏳
Show counts of updated records, new records, new homonyms, ignored
entries, discarded entries, and any errors.  Provide a link back to the
source view page.

### D-5. Write integration tests for the upload flow ⏳
End-to-end test using the private Junie database and
`src/seed_data/natick_sample_100.txt` as the upload input:
- Upload the sample MDF file.
- Verify staging, matching, committing, and search_entries population.
- Verify edit_history rows and session_id grouping.

### D-6. Write UI mock tests for the upload page (Phase C) ✅
Add tests in `tests/frontend/test_upload_mdf_page.py` that mock Streamlit
widgets and `UploadService` calls to verify upload page logic without a
running browser.  Each test patches `streamlit` functions (`st.selectbox`,
`st.file_uploader`, `st.button`, `st.session_state`, etc.) and asserts
the correct service calls are made.  Cover:
- **C-1 / C-2**: page renders only for `editor` / `admin` roles; blocked
  for `viewer`.
- **C-3**: `st.file_uploader` accepts `.txt` / `.mdf`; `parse_upload` is
  called with the file content on upload.
- **C-4**: source selectbox is populated from the `sources` table.
- **C-4a**: selecting `"+ Add new source…"` displays inline inputs; on
  confirmation a new source row is inserted and auto-selected.
- **C-5**: after upload, entry count and `lx` / `ps` / `ge` summary
  table are displayed.
- **C-6**: "Stage & Match" button calls `stage_entries` then
  `suggest_matches`; `batch_id` is stored in `st.session_state`.
- **C-6a**: batch selector lists pending batches with source name,
  filename, count, and upload date/time; selecting a batch loads its
  rows.
- **C-6b**: "Re-Match" button calls `rematch_batch` and refreshes the
  review table.

**Implementation note:** Tests are in `tests/frontend/test_upload_mdf_page.py`
(15 tests) rather than the originally planned `tests/ui/` path.

### D-7. Write UI mock tests for the review & confirm page (Phase D) ⏳
Add tests in `tests/frontend/test_upload_review_d1.py` that mock Streamlit
widgets and `UploadService` calls to verify review page logic.  Cover:
- **D-1**: review table renders columns (`lx`, suggested match, match
  type badge, status selector); cross-source info note displays when
  `cross_source_matches` is non-empty; `record_id_conflict` ⚠️ warning
  displays; `hm_mismatch` ⚠️ error warning displays. ✅
- **D-1 default status**: status selector pre-selects correct default
  (`create new` for conflicts, `match` for exact/base_form suggestions,
  `create new` for no suggestion). ✅
- **D-1b**: comparison view shows existing data left/top and new data
  right/bottom; "No existing record" placeholder when no match. ✅
- **D-1a**: bulk approval buttons render contextually — "Approve All as
  New Records" for new sources; "Approve All Matched" and "Approve
  Non-Matches as New" for existing sources; each calls the correct
  backend method. ✅
- **D-1c**: per-record "Apply Now" button is enabled for actionable
  statuses (`matched`, `create_new`, `create_homonym`, `discard`) and
  disabled for `pending` / `ignored`; clicking calls `apply_single` and
  removes the row. ✅
- **D-2**: manual match override widget calls `confirm_match` with the
  user-selected `record_id`.
- **D-3**: (superseded) verify that the immediate-apply pattern works
  correctly: bulk buttons ("Approve All Matched", "Approve Non-Matches
  as New", "Discard All Marked") each call the correct backend methods
  and immediately apply changes; review table refreshes after each
  action; per-record "Apply Now" handles individual entries.
- **D-3a**: "Download Pending Changes" button renders only when pending
  entries exist; downloaded file contains only pending `matchup_queue`
  entries as MDF text; button is hidden when no pending entries remain.
- **Discard workflow**: `mark_as_discard` sets status; `discard_marked`
  bulk-deletes; `apply_single` with `'discard'` status removes row
  without record writes.
- **D-4**: results summary displays correct counts for updated, new,
  homonym, ignored, and discarded entries.

**Implementation note:** D-1 block tests are in
`tests/frontend/test_upload_review_d1.py` (16 tests: 12 from D-1 + 4
from D-2) rather than the originally planned `tests/ui/` path.  Tests
for D-3 through D-4 will be added as those features are implemented.
