<!-- Copyright (c) 2026 Brothertown Language -->
<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
# Phase B — Upload Service (backend) ✅

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

### B-2. Create `UploadService` scaffold ✅
Create `src/services/upload_service.py` with a class `UploadService`
containing stub methods for the operations listed in subsequent steps.

### B-3. Implement `parse_upload(file_content: str) -> list[dict]` ✅
This method calls `parse_mdf()` and returns the list of parsed entries.
It should raise a clear `ValueError` if the file is empty or contains no
valid entries.

### B-3a. Implement `assign_homonym_numbers(entries: list[dict]) -> list[dict]` ✅
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

### B-4. Implement `stage_entries(user_email, source_id, entries, filename) -> str` ✅
Generate a new `batch_id` (UUID).  Insert each parsed entry into the
`matchup_queue` table with status `'pending'`, the generated `batch_id`,
and the original `filename`.  Return the `batch_id` so the caller can
reference this specific upload.  Each row stores the raw `mdf_data` and
the extracted `lx`.

### B-4a. Implement `list_pending_batches(user_email) -> list[dict]` ✅
Return a list of all distinct upload batches that still have rows in
`matchup_queue` for this user.  Each dict contains:
`{batch_id, source_id, source_name, filename, entry_count, uploaded_at}`.
`uploaded_at` is a timezone-aware datetime derived from the earliest
`created_at` among the batch's `matchup_queue` rows (i.e. the moment
the upload was staged).  Ordered by `uploaded_at` descending (newest
first).  This powers the batch selector in the UI (C-6a).

### B-5. Implement `suggest_matches(batch_id) -> list[dict]` ✅
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

### B-5b. Implement `auto_remove_exact_duplicates(batch_id) -> dict` ✅
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

### B-5c. Flag `\hm`-only mismatches as errors ✅
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

### B-5d. Flag headword edit-distance mismatches on record-number matches ✅
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

### B-5a. Implement `rematch_batch(batch_id) -> list[dict]` ✅
Re-run match suggestions for an existing batch.  For every row in
`matchup_queue` with this `batch_id` that has status `'pending'`
(or optionally all non-committed statuses — reset them to `'pending'`
first), clear `suggested_record_id` and `match_type`, then re-execute
the same matching logic as `suggest_matches` (B-5).  This is used when
records have been edited in another session and the user wants updated
match suggestions.  Return the same summary list as `suggest_matches`.

### B-6. Implement `confirm_match(queue_id, record_id=None) -> None` ✅
Mark a single `matchup_queue` row as `'matched'`.  If `record_id` is
provided, override the suggestion.  Validate that the target record exists.

### B-6a. Implement `approve_all_new_source(batch_id) -> int` ✅
Bulk-approve shortcut for **new source** uploads (the source has zero
existing records).  Mark every `'pending'` row in `matchup_queue` for
this `batch_id` as `'create_new'` — there is nothing to compare against,
so all entries will be committed as new records.  Return the count of
rows updated.

### B-6b. Implement `approve_all_by_record_match(batch_id, user_email, language_id, session_id) -> int` ✅
Bulk-apply shortcut for **existing source** uploads.  For every
`'pending'` or `'matched'` row in this `batch_id` that has a
`suggested_record_id` with `match_type` of `'exact'` or `'base_form'`,
set the status to `'matched'` and then immediately apply via
`apply_single` (updates the existing record, writes `edit_history`,
populates search entries, and removes the queue row).  Rows without a
suggestion are left untouched for manual review.  Return the count of
rows actually applied.

### B-6c. Implement `approve_non_matches_as_new(batch_id, user_email, language_id, session_id) -> int` ✅
Bulk-apply shortcut for **existing source** uploads.  For every
`'pending'` or `'create_new'` row in this `batch_id` that has **no**
`suggested_record_id` (no match found), set the status to `'create_new'`
and then immediately apply via `apply_single` (creates a new record,
writes `edit_history`, populates search entries, and removes the queue
row).  Rows that do have a suggestion are left untouched for manual
review.  Return the count of rows actually applied.

### B-6d. Implement `mark_as_homonym(queue_id) -> None` ✅
Mark a single `matchup_queue` row as `'create_homonym'`.  This is used
when the uploaded entry shares the same `lx` as an existing record but
is a distinct word (different meaning / part of speech).  At commit time
the entry will be inserted as a **new record** with the next available
`\hm` (homonym number) for that `lx` within the source.  For example,
if `lx = "ēsh"` already exists with `\hm 1`, the new homonym record
will be created with `\hm 2`.

### B-7. Implement `ignore_entry(queue_id) -> None` ✅
Mark a single `matchup_queue` row as `'ignored'` so it is skipped during
commit.

### B-7b. Implement `apply_single(queue_id, user_email, language_id, session_id) -> dict` ✅
Apply a single `matchup_queue` row immediately, regardless of batch-level
actions.  Inspect the row's current status to determine the operation:
- `'matched'` → execute the same logic as `commit_matched` for this one row.
- `'create_homonym'` → execute the same logic as `commit_homonyms` for this
  one row.
- `'create_new'` → execute the same logic as `commit_new` for this one row.
- `'discard'` → delete the `matchup_queue` row without creating or updating
  any record.  Return `{action: 'discarded', record_id: None, lx: …}`.
- `'pending'` or `'ignored'` → raise an error (the user must first set a
  valid actionable status).

After the record is written and `edit_history` is inserted, **delete** the
`matchup_queue` row and call `populate_search_entries` for the affected
record id.  Return a dict with `{action, record_id, lx}` summarising what
was done.  This method is only called after explicit user approval via the
per-record "Apply Now" button (D-1c).

### B-7c. Implement `mark_as_discard(queue_id) -> None` ✅
Mark a single `matchup_queue` row as `'discard'`.  This status indicates
the entry should be removed from the batch without creating or updating
any record.  The entry remains in the queue until explicitly applied
(via "Apply Now" or "Discard All Marked").

### B-7d. Implement `discard_marked(batch_id) -> int` ✅
Delete all `matchup_queue` rows for this `batch_id` that have status
`'discard'`.  No records or `edit_history` rows are written.  Return
the count of deleted rows.  This is the bulk counterpart to per-record
discard via `apply_single`.

### B-7a. Implement `discard_all(batch_id) -> int` ✅
Permanently delete all `matchup_queue` rows for this `batch_id`
regardless of status (`'pending'`, `'matched'`, `'create_new'`,
`'create_homonym'`, `'ignored'`).  No records or `edit_history` rows are
written — the staged upload is simply discarded.  Return the count of
deleted rows.

### B-8. Implement `commit_matched(batch_id, user_email, session_id) -> int` ✅
**This method is only called after explicit user approval via
"Apply Updates" or "Add & Apply All" (D-3).  No records or
edit_history rows are written until the user triggers an apply action.**

For every `'matched'` row belonging to this `batch_id`:
1. Snapshot the existing record's `mdf_data` as `prev_data`.
2. Format the uploaded `mdf_data` with `format_mdf_record`, then
   normalize with `normalize_nt_record`.
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

### B-8a. Implement `commit_homonyms(batch_id, user_email, language_id, session_id) -> int` ✅
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
4. Run `format_mdf_record` then `normalize_nt_record` with the new
   record's id.
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

### B-9. Implement `commit_new(batch_id, user_email, language_id, session_id) -> int` ✅
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

### B-10. Implement `populate_search_entries(record_ids: list[int]) -> int` ✅
For each record id, delete existing `search_entries` rows and re-insert
entries for `lx`, `va`, `se`, `cf`, `ve` extracted from the current
`mdf_data`.  Return the total count of search entries created.

### B-11. Write unit tests for `UploadService` ✅
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
- `apply_single` per-record commit for each status type (including `discard`).
- `discard_all` row deletion with no side effects.
- `discard_marked` deletion of `'discard'`-status rows only.
- `populate_search_entries` correct extraction.

### Phase B — Implementation Summary

**Status:** Complete (2026-02-08)

**Source files changed:**
- `src/services/upload_service.py` — New file. `UploadService` class with
  24 static methods covering the full upload workflow: parse, assign
  homonyms, stage, list batches, suggest matches (exact + base-form +
  record-id), auto-remove duplicates, flag hm mismatches, flag headword
  distance, rematch, search records for override,
  confirm/approve/ignore/discard status transitions, apply single,
  discard all, discard marked, commit matched/homonyms/new, and populate
  search entries.  Includes helper functions `_strip_diacritics`,
  `_strip_nt_record_lines`, `_strip_nt_record_and_hm_lines`,
  `_extract_hm_from_mdf`, and `_levenshtein`.
- `tests/database/test_crud.py` — Fixed pre-existing test failure:
  `test_user_deletion_restriction` was creating `MatchupQueue` without
  the now-required `batch_id` column (added in B-1).

**Test files added:**
- `tests/services/test_upload_service.py` — 53 unit tests:
  - 3 tests for `_strip_diacritics` helper.
  - 6 tests for `parse_upload` (valid, empty, whitespace, no entries,
    multiple entries, sample file).
  - 7 tests for `assign_homonym_numbers` (no homonyms, two/three
    homonyms, diacritics grouping, preserves existing hm, insertion
    position, single entry).
  - 5 tests for `stage_entries` and `list_pending_batches` (row
    creation, UUID format, batch listing, user isolation, ordering).
  - 6 tests for `suggest_matches` (exact lx, base-form fallback, no
    match, record-id match, cross-source indicator, record-id conflict).
  - 2 tests for `auto_remove_exact_duplicates` (removal + retention).
  - 2 tests for `flag_hm_mismatches` (mismatch + no mismatch).
  - 2 tests for `flag_headword_distance` (exceeds + within threshold).
  - 1 test for `rematch_batch` (re-runs after new record added).
  - 2 tests for `confirm_match` (default + override).
  - 1 test for `approve_all_new_source`.
  - 1 test for `approve_all_by_record_match`.
  - 1 test for `approve_non_matches_as_new`.
  - 1 test for `mark_as_homonym`.
  - 1 test for `ignore_entry`.
  - 1 test for `discard_marked`.
  - 1 test for `apply_single_discard`.
  - 1 test for `discard_all`.
  - 4 tests for `apply_single` (create_new, matched, pending raises,
    create_homonym).
  - 1 test for `commit_matched` (update + history + row deletion).
  - 1 test for `commit_homonyms` (new record + hm assignment).
  - 1 test for `commit_new` (insert + nt Record tag + history).
  - 2 tests for `populate_search_entries` (extraction + replacement).

**Test results:** All 118 tests pass (53 new + 65 existing) with zero
regressions.
