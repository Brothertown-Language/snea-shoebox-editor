<!-- Copyright (c) 2026 Brothertown Language -->
# MDF File Upload — Implementation Plan

This plan covers the end-to-end feature for uploading MDF files, staging
them in the `matchup_queue`, suggesting matches against existing records,
letting the user review/confirm, and committing accepted changes to the
`records` table with full audit history.

A user may have **multiple pending uploads** at the same time.  Each
upload is identified by a unique `batch_id` (UUID) assigned at staging
time.  All backend operations that read or write `matchup_queue` rows
are scoped by `batch_id` so uploads do not interfere with each other.

**Approval mandate** — no staged upload may modify the live `records`
table or insert `edit_history` rows without explicit user approval.  All
`matchup_queue` entries remain in a pending/approved state in the
database until the user deliberately triggers an apply or add action
(D-3).  There is no automatic or implicit upsert path.  This prevents
accidental writes and ensures every change is intentional.

Each step is a single, discrete semantic unit.  Steps are grouped into
phases for readability but must be implemented one at a time.

---

## Phase A — MDF Parser Enhancements ✅

**Status:** Complete (2026-02-08)

### A-1. Extract `\nt Record:` tag from MDF data ✅
Update `src/mdf/parser.py` so `parse_mdf()` extracts the `\nt Record: <id>`
tag from each entry and returns it as an optional `record_id` integer field
in the parsed dict (None when absent).

### A-2. Extract searchable sub-entry fields ✅
Update `src/mdf/parser.py` so `parse_mdf()` also extracts `\va` (variant),
`\se` (sub-entry), `\cf` (cross-reference), and `\ve` (English of sub-entry)
fields.  Return them as lists of strings in the parsed dict.

### A-3. Add `\nt Record:` deduplication / normalization helper ✅
Create a standalone function `normalize_nt_record(mdf_text: str, record_id: int) -> str`
in `src/mdf/parser.py` that:
- Removes all existing `\nt Record: …` lines from the text.
- Appends exactly one `\nt Record: <record_id>` line at the end.

### A-4. Write unit tests for parser enhancements ✅
Add tests in `tests/` covering:
- Parsing entries with and without `\nt Record:`.
- Parsing entries with `\va`, `\se`, `\cf`, `\ve`.
- `normalize_nt_record` adding, replacing, and deduplicating the tag.

Use `src/seed_data/natick_sample_100.txt` (100 randomly selected records
from the full Natick dictionary) as the test fixture for all parser tests.

### Phase A — Implementation Summary

**Source files changed:**
- `src/mdf/parser.py` — Rewrote parser using simple line-oriented parsing
  (no regex).  Added helper functions `_extract_tag()` and
  `_is_nt_record_line()`.  Added `normalize_nt_record()`.
- `src/seed_data/natick_sample_100.txt` — Regenerated with 100 randomly
  selected records (seed=42) from the full Natick dictionary.

**Test files added:**
- `tests/mdf/test_parser_phase_a.py` — 19 unit tests:
  - 6 tests for `record_id` extraction (present, absent, extra spaces,
    other `\nt` lines, sample file).
  - 7 tests for sub-entry field extraction (`\va`, `\se`, `\cf`, `\ve`,
    empty lists, sample file validation).
  - 6 tests for `normalize_nt_record` (add, replace, deduplicate, preserve
    other `\nt`, append position, content preservation).

**Test results:** All 53 tests pass (19 new + 34 existing) with zero
regressions.

---

## Phase B — Upload Service (backend)

### B-1. Add `batch_id`, `filename`, and `match_type` columns to `matchup_queue` ✅
Add the following columns to the `MatchupQueue` model in
`src/database/models/workflow.py`:
- `batch_id` (`String`, non-nullable) — UUID identifying the upload batch.
- `filename` (`String`, nullable) — original upload filename for display.
- `match_type` (`String`, nullable) — `'exact'` or `'base_form'`; set by
  `suggest_matches`.

Update the migration in `src/database/migrations.py` to add these
columns to existing tables.  All subsequent backend methods that query
or mutate `matchup_queue` rows are scoped by `batch_id` (not just
`user_email` + `source_id`).

### B-2. Create `UploadService` scaffold
Create `src/services/upload_service.py` with a class `UploadService`
containing stub methods for the operations listed in subsequent steps.

### B-3. Implement `parse_upload(file_content: str) -> list[dict]`
This method calls `parse_mdf()` and returns the list of parsed entries.
It should raise a clear `ValueError` if the file is empty or contains no
valid entries.

### B-3a. Implement `assign_homonym_numbers(entries: list[dict]) -> list[dict]`
After parsing, detect homonyms **within the uploaded batch** by comparing
`lx` values without diacritics (same `unicodedata.normalize('NFD')` +
remove `Mn` category logic used in B-5).  For each group of entries that
share the same diacritics-stripped base form:
- If none of the entries in the group already have an `\hm` tag, assign
  sequential `\hm` values starting from `1` (e.g. three entries with
  base form `esh` → `\hm 1`, `\hm 2`, `\hm 3`).
- If some entries already have `\hm` values, keep those and assign the
  next available ordinal to entries that lack one.
- If only one entry exists for a base form (no homonyms), do **not** add
  an `\hm` tag.
- Update both the parsed dict's `hm` field and the raw `mdf_data` text
  (insert `\hm <n>` on the line immediately after `\lx`).

This step runs on the parsed list **before** staging so that `\hm` tags
are present in the `matchup_queue` rows from the start, ensuring
accurate matching in B-5.

### B-4. Implement `stage_entries(user_email, source_id, entries, filename) -> str`
Generate a new `batch_id` (UUID).  Insert each parsed entry into the
`matchup_queue` table with status `'pending'`, the generated `batch_id`,
and the original `filename`.  Return the `batch_id` so the caller can
reference this specific upload.  Each row stores the raw `mdf_data` and
the extracted `lx`.

### B-4a. Implement `list_pending_batches(user_email) -> list[dict]`
Return a list of all distinct upload batches that still have rows in
`matchup_queue` for this user.  Each dict contains:
`{batch_id, source_id, source_name, filename, entry_count, uploaded_at}`.
`uploaded_at` is a timezone-aware datetime derived from the earliest
`created_at` among the batch's `matchup_queue` rows (i.e. the moment
the upload was staged).  Ordered by `uploaded_at` descending (newest
first).  This powers the batch selector in the UI (C-6a).

### B-5. Implement `suggest_matches(batch_id) -> list[dict]`
For every `pending` row in `matchup_queue` belonging to this `batch_id`:

**Matching is restricted to the same `source_id`** to prevent cross-source
matchups.  Only records belonging to the selected source are considered as
candidates.

1. **Exact match**: query the `records` table for existing entries with the
   same `lx` (and optionally same `hm`) **within the same `source_id`**.
2. **Diacritics-stripped fallback**: if no exact match is found, strip
   Unicode diacritics / combining characters from both the queued `lx` and
   each candidate record's `lx` (using `unicodedata.normalize('NFD')` +
   removal of category `Mn` characters) and compare the base forms.  This
   catches common mismatches such as `ēsh` vs `esh` or `nâne` vs `nane`.
   **This fallback also only searches within the same `source_id`.**
3. **Cross-source indicator**: after the same-source search, run a
   separate lightweight query across **other** sources to check whether
   any records with a matching `lx` (exact or base-form) exist elsewhere.
   Store the count (or list of source names) in a
   `cross_source_matches` field so the review UI can display an
   informational note (e.g. "Also found in: Source X, Source Y").
   **Cross-source matches are never used as suggested matches.**
4. **Cross-source record number conflict**: if the uploaded entry has a
   parsed `\nt Record: <id>` and a record with that same `id` exists in
   a **different** source, set a `record_id_conflict` flag (boolean) and
   populate `record_id_conflict_sources` (list of source names where the
   conflicting record lives).  This warns the user that reusing the
   record number would point at a record from another source — they
   should mark the entry as **"create new"** so it receives its own
   unique record id.  **This check is informational only and does not
   block any action.**

Write the best same-source candidate's `record_id` into
`suggested_record_id`.  When the match came from the fallback path, also
set a `match_type` indicator (e.g. `'exact'` or `'base_form'`) so the
review UI can flag approximate matches for the user.

Return a summary list of
`{queue_id, lx, suggested_record_id, suggested_lx, match_type, cross_source_matches, record_id_conflict, record_id_conflict_sources}`.

### B-5b. Implement `auto_remove_exact_duplicates(batch_id) -> dict`
After `suggest_matches` runs, automatically compare each matched
uploaded entry against its suggested existing record **excluding the
`\nt Record:` identifier line**.  If the remaining MDF content is
identical (byte-for-byte after stripping `\nt Record: …` lines from
both sides), the uploaded entry is an exact duplicate and adds no new
information.

For every exact duplicate found, **delete** the `matchup_queue` row
from the batch (it requires no user action).

Return a summary dict:
`{removed_count: int, headwords: list[str]}` where `headwords` is the
list of `lx` values for the removed entries.  The caller (C-6 / C-6b)
should display this summary to the user so they are aware of what was
auto-removed (e.g. "12 exact duplicates removed: ahtâs, kees, mâhks,
…").

This step runs automatically after `suggest_matches` (B-5) and after
`rematch_batch` (B-5a) so that duplicates are always pruned before the
user sees the review table.

### B-5c. Flag `\hm`-only mismatches as errors
After `auto_remove_exact_duplicates` (B-5b) runs, scan the remaining
matched entries in the batch.  For each entry that has a
`suggested_record_id`, compare the uploaded MDF against the existing
record's MDF **excluding both `\nt Record:` and `\hm` lines**.  If the
remaining content is identical but the `\hm` values differ, this is a
data-integrity error — two records with the same content should not have
different homonym numbers.

Set an `hm_mismatch` flag (boolean) and `hm_mismatch_detail` string
(e.g. `"uploaded \hm 2, existing \hm 1"`) on the `matchup_queue` row
(or in the returned summary dict).  These entries are **not**
auto-removed — they require explicit user review.

The review UI (D-1) should display a ⚠️ error-level warning for flagged
entries (e.g. "Data identical except \hm number — possible numbering
error") so the user can decide whether to update the existing record,
create a new homonym, or ignore the entry.

This step runs automatically after `auto_remove_exact_duplicates` (B-5b)
and after `rematch_batch` (B-5a).  Add `hm_mismatch` detection to the
**B-11** test coverage list.

### B-5d. Flag headword edit-distance mismatches on record-number matches
After B-5c runs, scan remaining matched entries where the match was made
via `\nt Record:` id (i.e. the uploaded entry's record number matched an
existing record in the same source).  For each such entry, compute the
edit distance (Levenshtein) between the uploaded `lx` and the existing
record's `lx`.  **Compare using NFD-normalized forms (diacritics
preserved)** — `unicodedata.normalize('NFD')` on both sides — so that
diacritic differences (e.g. `ēsh` vs `ésh`) are counted as character
edits rather than being stripped away.

If the edit distance exceeds a configurable threshold (default: **3**),
the mismatch is considered suspicious.  Set a `headword_distance` integer field
and a `headword_distance_detail` string (e.g.
`"uploaded 'kētan', existing 'kēton' — edit distance 2"`) on the
`matchup_queue` row.  These entries are **not** auto-removed — they
require explicit user review.

The review UI (D-1) should display a ⚠️ warning for flagged entries
(e.g. "Headword mismatch on record #42 — possible data error") so the
user can decide whether the uploaded entry is a correction, a different
word, or an error.

This step runs automatically after B-5c and after `rematch_batch`
(B-5a).  Add `headword_distance` detection to the **B-11** test
coverage list.

### B-5a. Implement `rematch_batch(batch_id) -> list[dict]`
Re-run match suggestions for an existing batch.  For every row in
`matchup_queue` with this `batch_id` that has status `'pending'`
(or optionally all non-committed statuses — reset them to `'pending'`
first), clear `suggested_record_id` and `match_type`, then re-execute
the same matching logic as `suggest_matches` (B-5).  This is used when
records have been edited in another session and the user wants updated
match suggestions.  Return the same summary list as `suggest_matches`.

### B-6. Implement `confirm_match(queue_id, record_id=None) -> None`
Mark a single `matchup_queue` row as `'matched'`.  If `record_id` is
provided, override the suggestion.  Validate that the target record exists.

### B-6a. Implement `approve_all_new_source(batch_id) -> int`
Bulk-approve shortcut for **new source** uploads (the source has zero
existing records).  Mark every `'pending'` row in `matchup_queue` for
this `batch_id` as `'create_new'` — there is nothing to compare against,
so all entries will be committed as new records.  Return the count of
rows updated.

### B-6b. Implement `approve_all_by_record_match(batch_id) -> int`
Bulk-approve shortcut for **existing source** uploads.  For every
`'pending'` row in this `batch_id` that already has a
`suggested_record_id` with `match_type = 'exact'` (i.e. matched by
`\nt Record:` id or exact `lx`), automatically mark it as `'matched'`.
Rows without a suggestion are left as `'pending'` for manual review.
Return the count of rows auto-approved.

### B-6c. Implement `approve_non_matches_as_new(batch_id) -> int`
Bulk-approve shortcut for **existing source** uploads.  For every
`'pending'` row in this `batch_id` that has **no**
`suggested_record_id` (no match found), mark it as `'create_new'` so
it will be committed as a new record.  Rows that do have a suggestion
are left untouched for manual review.  Return the count of rows marked.

### B-6d. Implement `mark_as_homonym(queue_id) -> None`
Mark a single `matchup_queue` row as `'create_homonym'`.  This is used
when the uploaded entry shares the same `lx` as an existing record but
is a distinct word (different meaning / part of speech).  At commit time
the entry will be inserted as a **new record** with the next available
`\hm` (homonym number) for that `lx` within the source.  For example,
if `lx = "ēsh"` already exists with `\hm 1`, the new homonym record
will be created with `\hm 2`.

### B-7. Implement `ignore_entry(queue_id) -> None`
Mark a single `matchup_queue` row as `'ignored'` so it is skipped during
commit.

### B-7b. Implement `apply_single(queue_id, user_email, language_id, session_id) -> dict`
Apply a single `matchup_queue` row immediately, regardless of batch-level
actions.  Inspect the row's current status to determine the operation:
- `'matched'` → execute the same logic as `commit_matched` for this one row.
- `'create_homonym'` → execute the same logic as `commit_homonyms` for this
  one row.
- `'create_new'` → execute the same logic as `commit_new` for this one row.
- `'pending'` or `'ignored'` → raise an error (the user must first set a
  valid actionable status).

After the record is written and `edit_history` is inserted, **delete** the
`matchup_queue` row and call `populate_search_entries` for the affected
record id.  Return a dict with `{action, record_id, lx}` summarising what
was done.  This method is only called after explicit user approval via the
per-record "Apply Now" button (D-1c).

### B-7a. Implement `discard_all(batch_id) -> int`
Permanently delete all `matchup_queue` rows for this `batch_id`
regardless of status (`'pending'`, `'matched'`, `'create_new'`,
`'create_homonym'`, `'ignored'`).  No records or `edit_history` rows are
written — the staged upload is simply discarded.  Return the count of
deleted rows.

### B-8. Implement `commit_matched(batch_id, user_email, session_id) -> int`
**This method is only called after explicit user approval via
"Apply Updates" or "Add & Apply All" (D-3).  No records or
edit_history rows are written until the user triggers an apply action.**

For every `'matched'` row belonging to this `batch_id`:
1. Snapshot the existing record's `mdf_data` as `prev_data`.
2. Normalize the uploaded `mdf_data` with `normalize_nt_record`.
3. Update the `records` row (`mdf_data`, `lx`, `hm`, `ps`, `ge`).
   **`normalize_nt_record` in step 2 guarantees the `\nt Record:` tag
   is present and accurate in the stored `mdf_data`.**
4. Insert an `edit_history` row with **all required fields**:
   - `record_id` — the updated record's id.
   - `user_email` — the uploading user.
   - `session_id` — the batch UUID passed in.
   - `version` — increment from the record's latest version (or 1 if first).
   - `change_summary` — e.g. `"MDF upload: updated from matchup_queue"`.
   - `prev_data` — the snapshot taken in step 1.
   - `current_data` — the normalized MDF written in step 3.
5. **Delete** the `matchup_queue` row (not just status update) so it
   no longer appears in the review table.  This lets the user see
   remaining work at a glance when processing in small batches.
6. Return the count of committed records.

### B-8a. Implement `commit_homonyms(batch_id, user_email, language_id, session_id) -> int`
**This method is only called after explicit user approval via
"Apply Updates" or "Add & Apply All" (D-3).**

For every `'create_homonym'` row belonging to this `batch_id`:
1. Query the highest existing `\hm` value for this `lx` within the
   same `source_id`.  If no `\hm` exists on the existing record(s),
   treat the existing record as `\hm 1` (update it to add `\hm 1`
   if not already present).
2. Assign the next sequential `\hm` number to the new entry
   (e.g. existing max is 1 → new entry gets `\hm 2`).
3. Insert a new `records` row with `source_id`, `language_id`, the
   assigned `hm`, and fields extracted from the queued MDF.
4. Run `normalize_nt_record` with the new record's id.
5. Insert an `edit_history` row:
   - `record_id` — the newly created homonym record's id.
   - `user_email` — the uploading user.
   - `session_id` — the batch UUID.
   - `version` — `1`.
   - `change_summary` — e.g. `"MDF upload: new homonym created (hm 2)"`.
   - `prev_data` — `NULL`.
   - `current_data` — the normalized MDF.
6. **Delete** the `matchup_queue` row so it no longer appears in the
   review table.
7. Return the count of new homonym records.

### B-9. Implement `commit_new(batch_id, user_email, language_id, session_id) -> int`
**This method is only called after explicit user approval via
"Add New Records" or "Add & Apply All" (D-3).  No records or
edit_history rows are written until the user triggers an add action.**

For every `'pending'` row (no match) that the user explicitly marks as
"create new":
1. Insert a new `records` row with `source_id`, `language_id`, and
   fields extracted from the queued MDF (`lx`, `hm`, `ps`, `ge`, `mdf_data`).
2. Run `normalize_nt_record` with the new record's id to stamp the
   `\nt Record:` tag into the stored `mdf_data`.  **This ensures every
   new record has an accurate `\nt Record:` tag from the moment it is
   created.**
3. Insert an `edit_history` row with **all required fields**:
   - `record_id` — the newly created record's id.
   - `user_email` — the uploading user.
   - `session_id` — the batch UUID passed in.
   - `version` — `1` (first version).
   - `change_summary` — e.g. `"MDF upload: new record created"`.
   - `prev_data` — `NULL` (no prior version).
   - `current_data` — the normalized MDF from step 2.
4. **Delete** the `matchup_queue` row so it no longer appears in the
   review table.
5. Return the count of new records.

### B-10. Implement `populate_search_entries(record_ids: list[int]) -> int`
For each record id, delete existing `search_entries` rows and re-insert
entries for `lx`, `va`, `se`, `cf`, `ve` extracted from the current
`mdf_data`.  Return the total count of search entries created.

### B-11. Write unit tests for `UploadService`
Use `src/seed_data/natick_sample_100.txt` as the test fixture for all
upload service tests.  Add tests covering:
- `parse_upload` with valid and empty content.
- `assign_homonym_numbers` detecting and tagging intra-batch homonyms.
- `stage_entries` row creation and `batch_id` generation.
- `list_pending_batches` returns correct batches per user.
- `suggest_matches` with and without existing records.
- `auto_remove_exact_duplicates` detection and removal of unchanged records.
- `hm_mismatch` detection for records identical except `\hm` number.
- `rematch_batch` clears and re-runs suggestions.
- `confirm_match`, `mark_as_homonym`, and `ignore_entry` status transitions.
- `commit_matched` record update + edit_history creation.
- `commit_homonyms` homonym record creation + `\hm` assignment.
- `commit_new` record creation + edit_history creation.
- `apply_single` per-record commit for each status type.
- `discard_all` row deletion with no side effects.
- `populate_search_entries` correct extraction.

---

## Phase C — Upload Page (frontend)

### C-1. Register a new Streamlit page for uploads
Add a page entry in `src/services/navigation_service.py` for
`"Upload MDF"` and create the file `src/frontend/pages/upload_mdf.py`
with a minimal placeholder.

### C-2. Add role guard to the upload page
Only users with `editor` or `admin` role may access this page.  Use the
existing `SecurityManager` route-protection pattern.

### C-3. Implement file uploader widget
Use `st.file_uploader` to accept `.txt` and `.mdf` files.  Display the
raw file preview in an expander.

### C-4. Implement source selector
Add a `st.selectbox` populated from the `sources` table so the user can
choose which source collection the upload targets.

### C-4a. Add "Create New Source" option to source selector
Add an option (e.g. `"+ Add new source…"`) at the end of the source
selectbox.  When selected, display inline text inputs for the new source's
`name` and optional `description`.  The `name` field should include a
placeholder hint (e.g. "Natick Dictionary — Trumbull") showing the
convention of combining the document/book title with the author/linguist
in a single value.  No schema change is needed — the existing `name`
column is sufficient (DRY).  On confirmation, insert the new row into the
`sources` table and auto-select it as the active source for the upload.

### C-5. Parse and display upload summary
On upload, call `UploadService.parse_upload()`, display the count of
entries found, and show a scrollable table of `lx` / `ps` / `ge` values.

### C-6. Implement "Stage & Match" button
On click, call `stage_entries` (which returns a `batch_id`) then
`suggest_matches(batch_id)`.  Store the `batch_id` and results in
`st.session_state`.

### C-6a. Implement pending upload batch selector
Above the review area, display a selectbox listing all pending upload
batches for the current user (from `list_pending_batches`).  Each option
shows the source name, original filename, entry count, and **upload
date/time** (formatted as e.g. `2026-02-08 14:52`).  The date/time is
essential for distinguishing between multiple uploads of the same file.
Selecting a batch loads its `matchup_queue` rows into the review table.
This allows the user to switch between multiple in-progress uploads.

### C-6b. Implement "Re-Match" button
Display a "Re-Match" button next to the batch selector.  On click, call
`rematch_batch(batch_id)` (B-5a) to re-run match suggestions against
the current state of the `records` table.  This is useful when records
have been edited in another session (or by another user) since the
original upload was staged.  The review table refreshes with updated
suggestions.

---

## Phase D — Review & Confirm Page (frontend)

### D-1. Display match review table
Show each staged entry with columns: `lx`, suggested match (existing
`lx` + `ge`), match type badge (`exact` / `base_form`), and a status
selector (`match` / `create new` / `new homonym` / `ignore`).  If `cross_source_matches`
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

### D-1b. Implement responsive record comparison view
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

### D-1a. Add bulk approval action buttons
Above the review table, display contextual bulk-action buttons:

- **New source** (source has no existing records): show an
  "Approve All as New Records" button that calls
  `approve_all_new_source` (B-6a) and refreshes the table.
- **Existing source**: show two buttons:
  1. "Approve All Matched" — calls `approve_all_by_record_match`
     (B-6b) to auto-approve entries that matched by record#.
  2. "Approve Non-Matches as New" — calls
     `approve_non_matches_as_new` (B-6c) to mark unmatched entries
     as new records.

All buttons update `st.session_state` and refresh the review table so
the user can still override individual entries before committing.

### D-1c. Add per-record "Apply Now" button
For each entry in the review table, display an **"Apply Now"** button
next to the status selector.  The button is **enabled** only when the
entry has an actionable status (`match`, `create new`, or
`new homonym`) and **disabled** when the status is `pending` or
`ignore`.  On click, call `apply_single(queue_id, …)` (B-7b) to
immediately commit that single record to the live `records` table and
`edit_history`.  The row is then removed from the review table.  Display
a brief inline confirmation (e.g. ✅ "Applied: ēsh → record #42").

This lets the user process records one at a time without waiting to
use the batch-level apply buttons (D-3).

### D-2. Allow manual match override
Provide a search/select widget so the user can pick a different existing
record instead of the auto-suggested one.

### D-3. Implement apply action buttons
Replace the single "Commit" button with four distinct actions.  **Nothing
touches the live `records` table or `edit_history` until one of the
apply/add actions is performed.**  All operations generate a
`session_id` (UUID) and log the session via `AuditService`.

1. **"Apply Updates"** — calls `commit_matched` and `commit_homonyms`
   only.  Applies changes to existing records (matched updates and new
   homonyms) but does **not** create new records.  Entries marked
   `'create_new'` remain staged for a separate action.
2. **"Add New Records"** — calls `commit_new` only.  Creates new
   records from entries marked `'create_new'` but does **not** touch
   existing records.  Entries marked `'matched'` or `'create_homonym'`
   remain staged for a separate action.
3. **"Add & Apply All"** — calls `commit_matched`, `commit_homonyms`,
   and `commit_new` in sequence.  Applies all approved changes in one
   step.
4. **"Discard All"** — calls `discard_all(batch_id)` (B-7a).
   Permanently removes all `matchup_queue` rows for the selected
   batch without writing anything to the live tables or edit history.
   After discard, the batch selector refreshes and the discarded
   batch is no longer listed.

After any apply/add action, call `populate_search_entries` for the
affected record ids.  The review table automatically refreshes to show
only the remaining staged entries — committed rows have been deleted
from `matchup_queue` by the backend, so the user can immediately see
what is left to process.

If a user has a mix of statuses not fully covered by a single button
(e.g. some matched, some new, some ignored), they can invoke
"Apply Updates" and "Add New Records" separately, or use
"Add & Apply All" to handle everything at once.

### D-4. Display apply results summary
Show counts of updated records, new records, new homonyms, ignored
entries, discarded entries, and any errors.  Provide a link back to the
source view page.

### D-5. Write integration tests for the upload flow
End-to-end test using the private Junie database and
`src/seed_data/natick_sample_100.txt` as the upload input:
- Upload the sample MDF file.
- Verify staging, matching, committing, and search_entries population.
- Verify edit_history rows and session_id grouping.

### D-6. Write UI mock tests for the upload page (Phase C)
Add tests in `tests/ui/test_upload_mdf_page.py` that mock Streamlit
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

### D-7. Write UI mock tests for the review & confirm page (Phase D)
Add tests in `tests/ui/test_upload_review_page.py` that mock Streamlit
widgets and `UploadService` calls to verify review page logic.  Cover:
- **D-1**: review table renders columns (`lx`, suggested match, match
  type badge, status selector); cross-source info note displays when
  `cross_source_matches` is non-empty; `record_id_conflict` ⚠️ warning
  displays; `hm_mismatch` ⚠️ error warning displays.
- **D-1 default status**: status selector pre-selects correct default
  (`create new` for conflicts, `match` for exact/base_form suggestions,
  `create new` for no suggestion).
- **D-1b**: comparison view shows existing data left/top and new data
  right/bottom; "No existing record" placeholder when no match.
- **D-1a**: bulk approval buttons render contextually — "Approve All as
  New Records" for new sources; "Approve All Matched" and "Approve
  Non-Matches as New" for existing sources; each calls the correct
  backend method.
- **D-1c**: per-record "Apply Now" button is enabled for actionable
  statuses (`match`, `create new`, `new homonym`) and disabled for
  `pending` / `ignore`; clicking calls `apply_single` and removes the
  row.
- **D-2**: manual match override widget calls `confirm_match` with the
  user-selected `record_id`.
- **D-3**: four apply action buttons ("Apply Updates", "Add New Records",
  "Add & Apply All", "Discard All") each call the correct backend
  methods; review table refreshes after each action; no live table
  writes occur until an apply button is clicked.
- **D-4**: results summary displays correct counts for updated, new,
  homonym, ignored, and discarded entries.

---

## Phase E — Cleanup & Polish

### E-1. Add activity logging for upload events
Log `upload_start`, `upload_staged`, `upload_committed` actions via
`AuditService` with the `session_id`.

### E-2. Add batch rollback support
Implement `UploadService.rollback_session(session_id)` that restores
`prev_data` from `edit_history` for all rows matching the session.

### E-3. Write unit tests for rollback
Test that rollback restores records and removes the corresponding
`search_entries`.

### E-4. Update roadmap documentation
Add the upload feature to the roadmap as a new phase entry once all
steps are done (user approval required).  Do **not** mark the phase as
completed until the user explicitly confirms it is finished.
