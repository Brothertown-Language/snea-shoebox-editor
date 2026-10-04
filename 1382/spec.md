# SPEC-FIX: Remediate ∞ (U+221E) → ꝏ (U+A74F) via Table Maintenance tool

## Intent / Executive Summary

- **Problem Statement:** The database stores ∞ (U+221E, INFINITY) in raw data columns (`records.lx`, `records.mdf_data`, `*.term` in `search_entries`, `headword_search_entries`, `gloss_search_entries`) as a mis-encoding of the original typographic oo-ligature ꝏ (U+A74F, LATIN SMALL LETTER OO). Raw columns carry the wrong character and must be correctable by an admin-gated database maintenance operation.
- **Root Cause / Motivation:** Eliot's Bible and Trumbull's dictionary use ꝏ — a ligature of two ⟨o⟩ letters cast as a single piece of type. The digitization process misidentified it as ∞. Confirmed in `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md` (∞ is a valid letter, maps to `oozzz`). The defect must be correctable now because every new record ingested from legacy sources perpetuates the mis-encoding, and raw column text is what admins and linguists read.
- **Approach Chosen:** Add a maintenance section inside the existing Data Reprocessing view under Admin → Table Maintenance (`src/frontend/pages/table_maintenance.py`, `render_data_reprocessing_maintenance()`), following the established Embedding Backfill section structure. The tool queries and displays the number of records detected with the defect — the remediable count and the locked defective-record count reported separately — then offers a single **Apply All** path as a plain primary button following the established maintenance-op pattern (`render_data_reprocessing_maintenance()` uses a plain `st.button("Start Full Reprocessing", type="primary")` with no confirm checkbox, and the Embedding Backfill section likewise). The operation is a DB maintenance and remediation task, NOT a record edit: it writes no `EditHistory` entries and performs no `current_version` bumps. On completion it reports the outcome (e.g., "N records remediated; M locked records remain unremediated"). The dependent-column rebuild follows the existing `upload_service.py` search-entry/FTS rebuild pattern.
- **Alternatives Considered & Why Discarded:**
  - **One-shot automatic batch migration at startup** — discarded: remediation of production linguistic data must be an explicit, reviewable admin action, not an implicit side effect of application startup (v1 of this spec used this design and was re-specified per developer direction).
  - **Direct SQL UPDATE script run by a developer** — discarded: bypasses application logic (cannot re-normalize dependent columns through the ingestion-consistent rebuild), and requires developer access to production data rather than admin self-service.
  - **Review One-by-One with per-record Apply/Skip controls** — discarded per stakeholder direction: the remediation is a uniform mechanical maintenance operation; per-record review adds UI complexity with no corrective value (v2–v6 of this spec used this design).
  - **`EditHistory` audit entry per remediated record** — discarded per stakeholder direction: the operation is DB maintenance, not an editorial edit; writing history entries and bumping `current_version` would misrepresent maintenance as record editing (v2–v6 of this spec used this design).
- **Key Design Decisions:**
  - **DB maintenance framing — no `EditHistory` writes, no version bumps** — tradeoff: remediated records carry no per-change history entry, in exchange for treating the operation as data hygiene consistent with its mechanical, deterministic nature (∞→ꝏ global replace on raw columns with ingestion-consistent dependent-column rebuild).
  - **Apply All as the only remediation path — a plain primary button following the established maintenance-op pattern** — tradeoff: no per-record cherry-picking and no confirm gate (consistent with Start Full Reprocessing and Start Embedding Backfill, which carry none), in exchange for a single deterministic bulk operation with a scan-first count display and an outcome report.
  - **Locked records are strictly immutable — never altered, counted and reported** — tradeoff: some defective records remain defective (reported post-remediation as remaining unremediated), in exchange for never violating the record-lock immutability invariant. No lock overrides, no forced unlocking.
  - **Reuse the ingestion search-entry/FTS rebuild pattern** (`src/services/upload_service.py`) rather than inventing a parallel rebuild — tradeoff: constrains the remediation code to mirror ingestion logic, in exchange for eliminating drift between remediation and ingestion rebuild behavior.
  - **Both ∞ and ꝏ map to `oozzz` in `generate_sort_lx()`** — tradeoff: an extra `symbol_map` entry, in exchange for byte-identical normalized columns before and after remediation.
  - **Seed files edited directly** — tradeoff: fixture churn in version control, in exchange for seed data matching real linguistic data; seed files are fixtures, not production data; production remediation is performed by the admin via the tool, never automatically.
- **User Intent / Original Prompt:** Stakeholder feedback from Dr. Keith Cunningham (relayed by the developer): the remediation must be treated as a DB maintenance and remediation task, NOT a record edit — no `EditHistory` entries and no version bumps; the only remediation path is Apply All (no per-record review UI); locked records are never altered but are counted and reported post-remediation. Supersedes the v2 direction for an interactive tool with Review One-by-One and per-record `EditHistory` writes. v8 developer feedback on the running app refines the v7 direction: the Apply All button carries no confirm gate (matching the existing maintenance ops) and the remediation lives inside the Data Reprocessing view rather than a separate sidebar option.

## Problem / Root Cause

Eliot's Bible and Trumbull's dictionary use ꝏ — a ligature of two ⟨o⟩ letters cast as a single piece of type. The digitization process misidentified it as ∞. Confirmed in repo paper citations (now migrated to snea-phonetics) and `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md` (∞ is a valid letter, maps to `oozzz`). Raw columns must carry the correct character while normalized columns remain unchanged (both ∞ and ꝏ normalize to `oozzz` via `generate_sort_lx()`).

## Affected Data

### Raw data columns (replace ∞ → ꝏ per record)

| Table | Column |
|-------|--------|
| `records` | `lx`, `mdf_data` |
| `search_entries` | `term` |
| `headword_search_entries` | `term` |
| `gloss_search_entries` | `term` |

### Normalized columns (re-normalize after change; result value unchanged)

| Table | Column | Mechanism |
|-------|--------|-----------|
| `records` | `sort_lx` | `generate_sort_lx()` |
| `search_entries` | `normalized_term` | `generate_sort_lx()` |
| `headword_search_entries` | `normalized_term` | `generate_sort_lx()` |
| `gloss_search_entries` | `normalized_term` | `generate_sort_lx()` |
| `fts_entries` | `fts_vector` | re-populate |

### Seed data files

| File | Action |
|------|--------|
| `src/seed_data/natick_sample_100.txt` | Replace all ∞ with ꝏ |
| `src/seed_data/natick_sample_100_no_diacritics.txt` | Replace all ∞ with ꝏ |

### Code changes

| File | Change |
|------|--------|
| `src/services/linguistic_service.py` | Add `"\ua74f": "oozzz"` to `symbol_map` in `generate_sort_lx()`; keep existing `"\u221e": "oozzz"` fallback |
| `src/services/linguistic_service.py` | New maintenance methods: defect scan (count + list, locked defective records counted separately) and apply-all batch remediation — no `EditHistory` writes, no `current_version` bumps |
| `src/frontend/pages/table_maintenance.py` | New "∞→ꝏ Remediation" section inside `render_data_reprocessing_maintenance()` with scan/count display and a plain primary Apply All button (no confirm gate); the sidebar radio list reverts to its original three options (Sources, Soft Deleted Records, Data Reprocessing) |

## Approach

1. **Service layer** — add maintenance service methods (following existing `LinguisticService` method conventions):
   - `count_infinity_records()` — counts non-deleted records where `lx` or `mdf_data` contains ∞ (U+221E). Locked defective records (`is_locked == True`) are counted separately as unremediable (reported, never altered) — they are NOT included in the remediable count.
   - `list_infinity_records()` — returns affected records (id, lx, preview of mdf_data, `is_locked` flag) for display; locked defective records are reported as unremediable.
   - `remediate_all_records(progress_callback)` — the maintenance batch operation: iterates the scan results and, for each non-locked, non-deleted defective record, replaces ∞→ꝏ in `lx` and `mdf_data`, updates `sort_lx`, and updates/re-normalizes the record's `search_entries`/`headword_search_entries`/`gloss_search_entries` `term`/`normalized_term` rows and `fts_entries.fts_vector`. Locked defective records are never touched — they are counted and reported as remaining unremediated. The per-record search-entry/FTS rebuild SHALL follow the existing pattern in `src/services/upload_service.py` (`SearchEntry`/`HeadwordSearchEntry`/`GlossSearchEntry` creation with `term` + `normalized_term = generate_sort_lx(term)`, and `FTSEntry` with `fts_vector = func.to_tsvector("simple", norm_mdf)`) to prevent drift from the ingestion logic. The operation writes no `EditHistory` entries and performs no `current_version` bumps — it is DB maintenance, not an editorial edit. Produces an outcome report stating the remediated count and the locked (unremediated) count.
2. **UI layer** — in `table_maintenance.py`, add a new "∞→ꝏ Remediation" section inside the existing `render_data_reprocessing_maintenance()` view, following the established Embedding Backfill section structure (the admin role guard is already enforced by `main()`, which gates the whole Table Maintenance page; the sidebar radio list keeps its original three options — Sources, Soft Deleted Records, Data Reprocessing):
   - `st.divider()`, `st.subheader("∞→ꝏ Remediation")`, and an `st.info` explanation box noting that the operation mutates RAW columns (`lx`, `mdf_data`) — unlike reprocessing, which rebuilds derived columns.
   - **Scan**: on view render, query and display "N records detected with the ∞ defect" (remediable count), with the locked defective-record count displayed separately (plus a Rescan button).
   - **Apply All**: a plain primary button following the established maintenance-op pattern (`st.button("Apply All", type="primary")` with no confirm checkbox — matching Start Full Reprocessing and Start Embedding Backfill); the only remediation path; applies to all detected non-locked defective records with progress indication following the existing section's progress pattern. On completion, displays the outcome report stating the remediated count and the locked (unremediated) count.
   - If no defective records found, display informational message with no action buttons.
   - Errors wrapped with `handle_ui_error` (logger `snea.pages.table_maintenance`), matching the surrounding sections.
3. **Normalization** — add ꝏ to `symbol_map`; both characters map to `oozzz`, so normalized values are byte-identical before and after remediation.
4. **Seed data** — replace ∞ with ꝏ in both seed files (permitted: seed files are fixtures, not production data; production remediation is performed by the admin via the tool, never automatically).

## Not Included

- **Automatic migration at startup** — remediation SHALL be an explicit admin action via the UI tool; an implicit startup migration would mutate production data without admin review.
- **Per-record review UI (Review One-by-One)** — removed per stakeholder direction; Apply All as a plain primary button is the only remediation path.
- **Separate "∞→ꝏ Remediation" sidebar option** — removed per developer feedback on the running app (v8); the remediation is a section inside the Data Reprocessing view, consistent with the Embedding Backfill section, and the sidebar radio list keeps its original three options.
- **`EditHistory` entries and `current_version` bumps for remediated records** — removed per stakeholder direction; the operation is DB maintenance, not an editorial edit, so record history and version state are untouched.
- **FTS search query normalization path changes** — already routes through `generate_sort_lx()`; changing it adds risk with no benefit.
- **Changes to `docs/lessons-learned/`** — they document the current state accurately.
- **Full pipeline re-ingestion** — targeted remediation per record is sufficient; re-ingestion would be disproportionate and risk unrelated data changes.
- **Soft-deleted records** — excluded from scan and remediation; they are not user-visible data.
- **Locked record remediation (lock overrides, forced unlocking)** — locked records (`is_locked == True`) are never altered by the maintenance operation; they are counted and reported as remaining unremediated. Strict immutability is preserved.

## Requirements

- R-1. `generate_sort_lx()` SHALL map both ∞ (U+221E) and ꝏ (U+A74F) to `oozzz`.
- R-2. `generate_sort_lx()` SHALL retain the existing ∞ → `oozzz` fallback entry in `symbol_map` after the ꝏ entry is added.
- R-3. The maintenance scan SHALL count and list exactly the non-deleted records whose `lx` or `mdf_data` contains ∞, excluding all other records.
- R-4. The maintenance scan SHALL report the locked defective-record count (`is_locked == True`) separately from the remediable count.
- R-5. Table Maintenance SHALL be the entry point via the existing `main()` admin guard, and the Data Reprocessing view SHALL contain the "∞→ꝏ Remediation" section.
- R-6. The remediation view SHALL display the detected defective-record counts — remediable and locked separately — before any remediation action is taken.
- R-7. Apply All SHALL remediate every non-locked, non-deleted defective record detected by the scan, replacing ∞ with ꝏ in `lx` and `mdf_data`.
- R-8. Apply All SHALL NOT alter locked records — each locked defective record SHALL retain ∞ and SHALL otherwise remain unchanged (no data change, no version bump, no history entry).
- R-9. Apply All SHALL produce a post-remediation outcome report stating the remediated count and the locked (unremediated) count.
- R-10. After remediation, normalized columns (`sort_lx`, `normalized_term`) SHALL be byte-identical to their pre-remediation values.
- R-11. After remediation, FTS search for terms containing ꝏ SHALL return the same results as pre-remediation search for the ∞ form.
- R-12. Seed data files SHALL contain ꝏ and SHALL NOT contain ∞.
- R-13. The per-record search-entry/FTS rebuild SHALL follow the existing ingestion pattern in `src/services/upload_service.py` to prevent drift from ingestion logic.

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method | Documentation Sources |
|----|-----------|---------------|---------------------|----------------------|
| SC-1 | `generate_sort_lx()` maps both ∞ and ꝏ to `oozzz` | `behavioral` | Unit test: `generate_sort_lx("k∞")` → `"koozzz"`, `generate_sort_lx("kꝏ")` → `"koozzz"` | `src/services/linguistic_service.py` (`generate_sort_lx()`); `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md` |
| SC-2 | Maintenance scan counts and lists exactly the records with ∞ in `lx` or `mdf_data` | `behavioral` | Unit test against fixture DB: seeded count matches `count_infinity_records()`; non-defective records excluded | `src/services/linguistic_service.py` (service method pattern); fixture DB tests |
| SC-3 | The Data Reprocessing maintenance view includes the ∞→ꝏ remediation section (admin-gated by the existing `main()` guard) | `behavioral` | Render page as admin — the remediation section is present in the Data Reprocessing view; render as editor/viewer — page blocked by existing admin guard; sidebar radio list has exactly the original three options | `src/frontend/pages/table_maintenance.py` (`main()` admin guard; `render_data_reprocessing_maintenance()`) |
| SC-4 | View displays the detected record counts — remediable and locked separately — before any action, with the outcome report rendered on completion | `behavioral` | Unit/UI test: with N defective fixture records (including locked), the section shows the remediable count and the locked count, and no changes are applied until the plain primary Apply All button is clicked; zero-state shows informational message with no action button; outcome report states remediated and locked counts | `src/frontend/pages/table_maintenance.py` (existing scan/count render patterns; `render_data_reprocessing_maintenance()`) |
| SC-5 | Apply All remediates every non-locked, non-deleted defective record: all remediable records' raw columns (`lx`, `mdf_data`) contain ꝏ not ∞ after Apply All | `behavioral` | Run Apply All on fixture DB; assert every non-locked defective record's raw columns contain ꝏ not ∞ | `src/services/linguistic_service.py` (maintenance service methods) |
| SC-6 | After remediation, normalized columns are byte-identical to pre-remediation values | `behavioral` | Compare `sort_lx`/`normalized_term` pre/post — identical (∞ and ꝏ both map to `oozzz`) | `src/services/linguistic_service.py` (`generate_sort_lx()` symbol_map) |
| SC-7 | FTS search for terms with ꝏ returns the same results as pre-remediation ∞ search | `behavioral` | Search `kꝏ` post-remediation; results match pre-remediation search for `k∞` | the search-entry/FTS rebuild block in `src/services/upload_service.py` (FTS rebuild pattern); fixture DB tests |
| SC-8 | Seed data files contain ꝏ, not ∞ | `string` | `grep -c $'\u221e'` on both seed files returns 0 | `src/seed_data/natick_sample_100.txt`; `src/seed_data/natick_sample_100_no_diacritics.txt` |
| SC-9 | Existing ∞ → `oozzz` fallback preserved in `generate_sort_lx()` (retained as a distinct regression guard against accidental fallback removal) | `string` | `"\u221e": "oozzz"` remains in `symbol_map` | `src/services/linguistic_service.py` (`generate_sort_lx()` symbol_map) |
| SC-10 | Maintenance scan reports the remediable count and the locked defective-record count separately | `behavioral` | Fixture DB with locked defective record: `count_infinity_records()` reports the remediable count excluding the locked record and a separate locked count ≥ 1; locked record not in the remediable set | `is_locked` on `records`; strict-immutability enforcement in `update_record()` in `src/services/linguistic_service.py` (provenance of the lock invariant) |
| SC-11 | Locked defective records are never altered by Apply All: each locked defective record retains ∞ and remains otherwise unchanged (no data change, no version bump, no history entry) | `behavioral` | Run Apply All on fixture DB containing locked defective record: locked record retains ∞; `lx`/`mdf_data`/`sort_lx`/`current_version` identical to pre-run values; no `edit_history` rows for it | `is_locked` on `records`; strict-immutability enforcement in `update_record()` in `src/services/linguistic_service.py` (provenance of the lock invariant) |
| SC-12 | Apply All produces an outcome report stating the remediated count and the locked (unremediated) count | `behavioral` | Run Apply All on fixture DB containing locked defective record: outcome report states the remediated count and the locked count (e.g., "N records remediated; M locked records remain unremediated") | `src/frontend/pages/table_maintenance.py` (outcome-report render); `src/services/linguistic_service.py` (batch outcome report) |
| SC-13 | Apply All remediates all non-locked defective records even when locked defective records are present (locked presence does not block remediable remediation) | `behavioral` | Fixture DB with mixed locked + unlocked defective records: after Apply All, every unlocked defective record is remediated per SC-5 | `src/services/linguistic_service.py` (maintenance service methods) |

## Items

### Item 1 (SC-1): ꝏ normalization entry in `generate_sort_lx()`

- RED: Unit test asserting `generate_sort_lx("kꝏ")` → `"koozzz"` fails (no ꝏ entry in `symbol_map`)
- GREEN: Add `"\ua74f": "oozzz"` to `symbol_map` in `generate_sort_lx()`
- verify: Both `generate_sort_lx("k∞")` → `"koozzz"` and `generate_sort_lx("kꝏ")` → `"koozzz"` pass
- commit: `src/services/linguistic_service.py` + test

### Item 2 (SC-2): Maintenance scan counts and lists defective records

- RED: Unit test asserting `count_infinity_records()` / `list_infinity_records()` match a seeded fixture count fails (methods absent)
- GREEN: Implement scan methods against the fixture DB
- verify: Seeded count matches; non-defective records excluded
- commit: scan methods + test

### Item 3 (SC-3): Remediation section inside Data Reprocessing view (admin-gated)

- RED: UI test asserting the "∞→ꝏ Remediation" section is present in the Data Reprocessing view for admin fails (section absent)
- GREEN: Add the section inside `render_data_reprocessing_maintenance()` with admin gating inherited from `main()`; sidebar radio list keeps exactly the original three options
- verify: Admin renders the Data Reprocessing view and sees the section; editor/viewer blocked by existing admin guard; radio list has exactly the original three options
- commit: `src/frontend/pages/table_maintenance.py` + UI test

### Item 4 (SC-4): Scan-count display before action (remediable + locked counts, plain Apply All, outcome report)

- RED: UI test asserting the remediable and locked counts render before any button click fails
- GREEN: Render scan counts (remediable and locked separately, plus Rescan button) on view render, with a plain primary Apply All button (no confirm gate) and the outcome report on completion
- verify: With N defective fixture records (including locked), the section shows both counts; no changes applied until the Apply All button is clicked; zero-state shows informational message with no action button; outcome report states remediated and locked counts
- commit: section render + UI test

### Item 5 (SC-5): Apply All remediates every non-locked, non-deleted defective record

- RED: Test running Apply All on fixture DB asserts raw columns contain ꝏ — fails (Apply All absent)
- GREEN: Implement `remediate_all_records()` applying ∞→ꝏ to every non-locked, non-deleted defective record
- verify: All remediable raw columns contain ꝏ not ∞
- commit: batch maintenance + test

### Item 6 (SC-6): Normalized columns byte-identical after remediation

- RED: Test comparing pre/post `sort_lx`/`normalized_term` fails if remediation alters normalized values
- GREEN: Re-normalize via `generate_sort_lx()` after raw change (both characters map to `oozzz`)
- verify: Pre/post normalized values byte-identical
- commit: re-normalization wiring + test

### Item 7 (SC-7): FTS search equivalence after remediation

- RED: Test searching `kꝏ` post-remediation vs `k∞` pre-remediation fails on mismatch
- GREEN: Rebuild `fts_entries.fts_vector` following the `upload_service.py` ingestion pattern
- verify: Result sets identical
- commit: FTS rebuild + test

### Item 8 (SC-8): Seed data cleaned

- RED: `grep -c $'\u221e'` on both seed files returns > 0 (fails the zero expectation)
- GREEN: Replace all ∞ with ꝏ in both seed files
- verify: `grep -c $'\u221e'` returns 0 on both files
- commit: both seed files

### Item 9 (SC-9): ∞ fallback preserved

- RED: String check asserting `"\u221e": "oozzz"` remains in `symbol_map` fails if the entry is removed during Item 1
- GREEN: Preserve the fallback entry while adding the ꝏ entry
- verify: `"\u221e": "oozzz"` present in `symbol_map`
- commit: `src/services/linguistic_service.py`

### Item 10 (SC-10): Locked-record separate count in scan reporting

- RED: Fixture test with a locked defective record asserts a separate locked count — fails (no exclusion logic)
- GREEN: Exclude locked records from the remediable count; report the locked count separately
- verify: Remediable count excludes locked record; locked count ≥ 1
- commit: scan methods + test

### Item 11 (SC-11): Apply All never alters locked records

- RED: Fixture test asserting a locked defective record is untouched by Apply All fails (no exclusion logic)
- GREEN: Apply All never touches locked records — no data change, no version bump, no history entry
- verify: Locked record retains ∞; `lx`/`mdf_data`/`sort_lx`/`current_version` unchanged; no `edit_history` rows for it
- commit: batch maintenance + test

### Item 12 (SC-12): Post-remediation outcome report (remediated + locked unremediated counts)

- RED: Test asserting the outcome report states the remediated count and the locked count fails (no report)
- GREEN: Produce the outcome report from the batch and render it on completion
- verify: Report states remediated count and locked (unremediated) count for the mixed fixture
- commit: outcome report + test

### Item 13 (SC-13): Locked presence does not block remediable remediation

- RED: Fixture test with mixed locked + unlocked defective records asserts all unlocked records remediated — fails
- GREEN: Ensure Apply All continues past locked records and remediates every non-locked defective record
- verify: Every unlocked defective record remediated in mixed fixture
- commit: batch maintenance + test

## Dependencies

| Reference | Relationship | Status |
|-----------|--------------|--------|
| `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md` | Must be read before implementation — documents that ∞ is a valid letter mapping to `oozzz` | Satisfied (exists in repo) |
| `docs/lessons-learned/2026-06-13-simple-vs-english-tsconfig.md` | Must be read before implementation — FTS rebuild must preserve the `'simple'` tsconfig | Satisfied (exists in repo) |
| Record lock invariant (`is_locked` on `records`; strict-immutability enforcement in `update_record()` in `src/services/linguistic_service.py`) | Provenance of the locked-record immutability invariant the maintenance operation preserves — locked records are never altered | Satisfied (exists in code) |
| `src/services/upload_service.py` search-entry/FTS rebuild pattern | Must be followed for per-record search-entry/FTS rebuild | Satisfied (exists in code) |
| `src/frontend/pages/table_maintenance.py` admin role guard in `main()` | Must be inherited by the new view; no separate guard written | Satisfied (exists in code) |

## Traceability

| Requirement | SC(s) | Approach Step |
|-------------|-------|---------------|
| R-1 | SC-1 | Step 3 (Normalization) |
| R-2 | SC-9 | Step 3 (Normalization) |
| R-3 | SC-2 | Step 1 (Service layer) |
| R-4 | SC-10 | Step 1 (Service layer) |
| R-5 | SC-3 | Step 2 (UI layer) |
| R-6 | SC-4 | Step 2 (UI layer) |
| R-7 | SC-5, SC-13 | Step 1 (Service layer) |
| R-8 | SC-11 | Step 1 (Service layer) |
| R-9 | SC-12 | Step 2 (UI layer) |
| R-10 | SC-6 | Step 3 (Normalization) |
| R-11 | SC-7 | Step 1 (Service layer) |
| R-12 | SC-8 | Step 4 (Seed data) |
| R-13 | SC-6, SC-7 | Step 1 (Service layer) |

## Documentation Sources

| Source | Type | Location | Verification |
|--------|------|----------|-------------|
| ∞ symbol normalization lesson | doc | `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md` | Read during codebase re-evaluation |
| simple vs english tsconfig lesson | doc | `docs/lessons-learned/2026-06-13-simple-vs-english-tsconfig.md` | Read during codebase re-evaluation |
| Record lock immutability invariant | code | `src/services/linguistic_service.py` (`update_record()` strict-immutability enforcement); `is_locked` on `records` | Read during codebase re-evaluation |
| Search-entry/FTS rebuild pattern | code | `src/services/upload_service.py` (search-entry/FTS rebuild block) | Read during codebase re-evaluation |
| Admin role guard | code | `src/frontend/pages/table_maintenance.py` (`main()`) | Read during codebase re-evaluation |
| Seed data fixtures | data | `src/seed_data/natick_sample_100.txt`, `src/seed_data/natick_sample_100_no_diacritics.txt` | Read during codebase re-evaluation |

## Enforcement Gate

> **Enforcement gate:** All success criteria MUST pass before this spec is considered complete. Partial implementation is not permitted.

## Cost Frame

Cost is measured in defect-discovery-latency, not tool calls. Correctness is the only metric.

- **SC-1:** Running the two-assertion normalization unit test costs minutes — it proves both characters converge on `oozzz`. Skipping costs a silent normalization divergence — a mis-keyed glyph corrupts every downstream sort and search for affected terms.
- **SC-2:** Running the fixture-DB scan test costs minutes — it proves the count is exact, not approximate. Skipping costs over- or under-remediation — an inexact scan either mutates clean records or leaves defects undetected.
- **SC-3:** Running the admin-guard render test costs minutes — it proves role gating. Skipping costs unauthorized remediation — a non-admin mutates linguistic data with no review.
- **SC-4:** Running the count-display test costs minutes — it proves the admin sees the blast radius before acting. Skipping costs blind bulk mutation — an admin applies changes without knowing how many records are affected.
- **SC-5:** Running the Apply All raw-column test costs minutes — it proves every non-locked defective record was actually transformed. Skipping costs partial remediation that looks complete — remaining ∞ records surface later as search and sort anomalies.
- **SC-6:** Running the pre/post normalized-column comparison costs minutes — it proves normalized data is stable. Skipping costs silent drift in sort and search columns — divergence discovered only after users report wrong ordering.
- **SC-7:** Running the FTS equivalence test costs minutes — it proves search behavior is unchanged. Skipping costs a search regression — terms become unfindable or duplicated post-remediation.
- **SC-8:** Running the seed-file grep costs seconds — it proves fixtures are clean. Skipping costs re-seeding contamination — every fresh fixture database reintroduces the defect.
- **SC-9:** Running the fallback string check costs seconds — it proves legacy ∞ handling survives. Skipping costs a regression for un-remediated legacy data — previously searchable records vanish from results.
- **SC-10:** Running the locked-count scan test costs minutes — it proves locked records are never counted as remediable and are reported separately. Skipping costs a lock-invariant violation surfacing mid-batch — the worst possible place to discover immutability was never enforced.
- **SC-11:** Running the locked-record untouched test costs minutes — it proves locked records survive the maintenance batch completely unchanged. Skipping costs silent mutation of locked records — a data-integrity defect invisible until audit.
- **SC-12:** Running the outcome-report test costs minutes — it proves the admin learns exactly how many records were remediated and how many locked records remain unremediated. Skipping costs an incomplete batch that reports success — unremediated locked defects silently forgotten.
- **SC-13:** Running the mixed-fixture test costs minutes — it proves locked records do not block the batch. Skipping costs a stalled remediation — one locked record silently halts remediation of all clean records.

## Edge Cases

- **Condition:** Record contains ∞ in `lx` but not `mdf_data` (or vice versa). **Expected behavior:** Both columns are scanned; the record is detected and both columns remediated. **Resolution:** Scan predicate is OR across `lx` and `mdf_data`; remediation replaces ∞ in both columns.
- **Condition:** Zero defective records detected at scan time. **Expected behavior:** View displays an informational message with no action buttons; Apply All is unavailable. **Resolution:** Guard clause in the render function; no-op service calls prevented.
- **Condition:** All defective records are locked. **Expected behavior:** Remediable count is 0; locked count equals total detected; Apply All completes with an outcome report stating 0 records remediated and M locked records remain unremediated, with no changes applied. **Resolution:** Never-alter-plus-report semantics; the outcome report distinguishes remediated (0) from locked (unremediated).
- **Condition:** Record contains multiple ∞ occurrences within one column. **Expected behavior:** All occurrences in that column are replaced in a single remediation pass. **Resolution:** Global replace per column within the batch operation's per-record pass.
- **Condition:** Batch write fails mid-remediation after some records were remediated. **Expected behavior:** The failure surfaces immediately (fail-fast) and the outcome report reflects the records completed before the failure. **Resolution:** No silent swallow; admin sees the error; re-running Apply All remediates only the remaining defective records.
- **Condition:** Concurrent admin sessions running remediation simultaneously. **Expected behavior:** Per-record writes are transactional so the last committed state is consistent. **Resolution:** Concurrent remediation of the same record is idempotent (∞→ꝏ replacement of already-remediated data is a no-op).
- **Condition:** Soft-deleted record contains ∞. **Expected behavior:** Excluded from scan and remediation. **Resolution:** Scan predicate filters deleted records.
- **State transitions:** Scan (read-only) → plain primary Apply All (batch write) → outcome report. The scan result displayed SHALL be the basis for the applied batch; a Rescan refreshes the displayed counts before action.
- **Failure modes:** Database unavailability during scan displays an error state, not a zero count — a zero count is only displayed when the query succeeds and returns zero.
- **Recovery:** A partially applied batch is recoverable by re-running Apply All after the failure — the re-scan detects only remaining defective records (already-remediated records no longer match the scan), so remediation is idempotent.

## Change Control

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1 | 2026-07-18 | AI agent | Initial spec (batch migration design) |
| 2 | 2026-09-29 | AI agent | Re-spec per developer direction: replace one-shot migration with interactive Table Maintenance tool (scan/count display, Apply All, Review One-by-One with per-record apply) |
| 3 | 2026-10-03 | AI agent | Codebase re-evaluation: added locked-record exclusion policy (strict immutability per `update_record()`; scan reports excluded locked count separately; Apply All produces applied-vs-skipped outcome report; new SC-11/SC-12/SC-13); cited `upload_service.py:1798-1843` search-entry/FTS rebuild pattern to prevent drift; confirmed `update_record()` EditHistory snapshot pattern reference accurate |
| 4 | 2026-10-03 | AI agent | Structural revision per holistic validation findings (aggregate verdict FAIL — substance 9/11 PASS, failures structural): added required sections per spec-structure-standards.md (6-field preamble, Not Included, Requirements, Items, Dependencies, Traceability, Documentation Sources, Enforcement Gate, Cost Frame, Edge Cases); converted MUST to RFC 2119 SHALL language; added Cost Frame with per-SC cost-frame statements; added Documentation Sources column to SC table; decomposed compound SCs into atomic single-claim SCs (old SC-5 → SC-5/SC-6; old SC-6 → SC-7/SC-8; old SC-12 → SC-14/SC-15/SC-16) with all 13 original claims preserved and renumbered to SC-1..SC-17; noted artifact_cross_reference warning (artifacts directory absent) |
| 5 | 2026-10-03 | AI agent | Structural revision per validation iteration 2 findings (aggregate verdict FAIL — all 11 holistic dimensions strong, 3 structural FAILs): replaced Traceability Phase(s) column (referenced undefined phase structure, contradicted Approach ordering) with Approach Step references consistent with the Approach steps; made SC-13 verification deterministic by removing the '(or scan UI)' either/or alternative; replaced all file-path line-number references (e.g. `linguistic_service.py:727`, `upload_service.py:1798-1843`) with stable anchors per the cross-reference standard; resolved Code-changes table discretion point by selecting `src/services/linguistic_service.py` as the single remediation-service location; added one-line rationale to SC-12 (regression guard); all 17 SCs and all substantive content preserved |
| 6 | 2026-10-03 | AI agent | Warning-resolution revision per developer directive (validation returned aggregate PASS with two non-blocking warnings, both required resolved for a 100% clean PASS): (1) artifact_cross_reference WARNING — generated the full analytical artifact set (blast-radius, concern-map, code-path-inventory, cross-cutting-matrix, interface-compatibility, state-analysis, testability-assessment) at `.issues/1382/artifacts/`, grounded in spec v5 (SC-1..SC-17) and verified against the live codebase; (2) dark-prose-007-cost-frames WARNING — added the canonical computation-frame/identity-anchor header to the Cost Frame section per cost-model-standards.md Per-SC format ("Cost is measured in defect-discovery-latency, not tool calls. Correctness is the only metric."); no SC, requirement, or section removed or weakened; v5 stable anchors preserved |
| 7 | 2026-10-04 | AI agent | Stakeholder-directed intent change (Dr. Keith Cunningham feedback, relayed by the developer): the remediation is reclassified as a DB maintenance and remediation task, NOT a record edit — (1) removed `EditHistory` entirely (no history entries, no `current_version` bumps for remediated records; all EditHistory/audit-trail SCs, requirements, cost-frame entries, traceability rows, and edge cases removed; `update_record()` reference retained only as provenance of the lock invariant); (2) removed the Review One-by-One UI — Apply All with a confirm gate is the only remediation path; scan/count display before action retained; (3) replaced the v3–v6 locked-record refusal-path SCs with maintenance-framed equivalents — locked records are never altered but are counted and reported post-remediation (scan reports remediable and locked counts separately; outcome report states remediated and locked unremediated counts); (4) soft-deleted records remain excluded from scan; normalization design, byte-identical normalized columns, FTS equivalence, seed-file replacement, SHALL language, Cost Frame header, Documentation Sources column, and 6-field preamble preserved; SC set renumbered to SC-1..SC-13; analytical artifacts, linked plan, and dependency contract regenerated to match |
| 8 | 2026-10-04 | AI agent | Developer feedback on the running app (live UX review): (1) removed the confirm gate on Apply All — it is now a plain primary button following the established maintenance-op pattern (`render_data_reprocessing_maintenance()` uses a plain `st.button("Start Full Reprocessing", type="primary")` with no confirm checkbox, and the Embedding Backfill section likewise); all confirm-gate language removed from requirements, SCs, cost frames, edge cases, and Not Included; the scan-first count display and outcome report are retained; (2) relocated the UI — the separate "∞→ꝏ Remediation" sidebar radio option is removed entirely and the sidebar radio list reverts to its original three options (Sources, Soft Deleted Records, Data Reprocessing); the remediation becomes a section inside the Data Reprocessing view (`render_data_reprocessing_maintenance()`), following the established Embedding Backfill section structure (divider, subheader, st.info explanation noting it mutates RAW columns lx/mdf_data, scan-first counts with Rescan, plain primary Apply All, existing progress pattern, outcome report, handle_ui_error wrapping); admin-only access inherited from the main() admin guard; R-5 and SC-3/SC-4 reworded accordingly; all analytical artifacts, linked plan, dependency contract, and SC summary regenerated to match |

---

🤖 Co-authored with AI: OpenCode (ollama-cloud/glm-5.3)
🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
