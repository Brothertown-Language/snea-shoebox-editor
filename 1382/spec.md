# SPEC-FIX: Remediate ∞ (U+221E) → ꝏ (U+A74F) via Table Maintenance tool

## Intent / Executive Summary

The database stores ∞ (U+221E, INFINITY) in raw data columns (`records.lx`, `records.mdf_data`, `*.term`) as a mis-encoding of the original typographic oo-ligature ꝏ (U+A74F, LATIN SMALL LETTER OO). Rather than a one-shot migration, this spec adds an interactive remediation tool as a new sidebar option under Admin → Table Maintenance (`src/frontend/pages/table_maintenance.py`). The tool queries and displays the number of records detected with the defect, then offers the admin two paths: **Apply All** (no review) or **Review One-by-One** with a per-record apply option. Every applied change writes a proper `EditHistory` entry.

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
| `src/services/linguistic_service.py` (or new remediation service module) | New methods: defect scan (count + list), apply-one, apply-all — each writing `EditHistory` entries |
| `src/frontend/pages/table_maintenance.py` | New sidebar radio option "∞→ꝏ Remediation" with scan/count display, Apply All, and Review One-by-One UI |

## Approach

1. **Service layer** — add remediation service methods (pattern follows existing `LinguisticService` methods and `EditHistory` audit-snapshot pattern from `update_record()`):
   - `count_infinity_records()` — counts non-deleted records where `lx` or `mdf_data` contains ∞ (U+221E).
   - `list_infinity_records()` — returns affected records (id, lx, preview of mdf_data) for review.
   - `remediate_record(record_id, user_email, session_id)` — for one record: snapshot `mdf_data` as `prev_data`, replace ∞→ꝏ in `lx` and `mdf_data`, write `EditHistory` (prev/current snapshots, `change_summary: "Remediate ∞ (U+221E) → ꝏ (U+A74F) oo-ligature"`, version = current+1, session UUID for the batch), update `sort_lx`, and update/re-normalize the record's `search_entries`/`headword_search_entries`/`gloss_search_entries` `term`/`normalized_term` rows and `fts_entries.fts_vector`.
   - `remediate_all_records(user_email, progress_callback)` — iterates `list_infinity_records()`, applies per record with a shared session UUID, progress callback for UI.
2. **UI layer** — in `table_maintenance.py` `main()` sidebar radio, add option `"∞→ꝏ Remediation"` rendering a new `render_infinity_remediation()` view (admin role guard already enforced by `main()`):
   - **Scan**: on page open, query and display "N records detected with the ∞ defect" (plus a Rescan button).
   - **Apply All**: single confirm-gated button; applies to all detected records with progress indication; no per-record review.
   - **Review One-by-One**: paginated/sequential display of each affected record (id, lx, before/after preview of affected text) with per-record **Apply** and **Skip** controls.
   - If no defective records found, display informational message with no action buttons.
3. **Normalization** — add ꝏ to `symbol_map`; both characters map to `oozzz`, so normalized values are byte-identical before and after remediation.
4. **Seed data** — replace ∞ with ꝏ in both seed files (permitted: seed files are fixtures, not production data; production remediation is performed by the admin via the tool, never automatically).

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method |
|----|-----------|---------------|---------------------|
| SC-1 | `generate_sort_lx()` maps both ∞ and ꝏ to `oozzz` | `behavioral` | Unit test: `generate_sort_lx("k∞")` → `"koozzz"`, `generate_sort_lx("kꝏ")` → `"koozzz"` |
| SC-2 | Remediation scan counts and lists exactly the records with ∞ in `lx` or `mdf_data` | `behavioral` | Unit test against fixture DB: seeded count matches `count_infinity_records()`; non-defective records excluded |
| SC-3 | Table Maintenance sidebar exposes "∞→ꝏ Remediation" for admin only | `behavioral` | Render page as admin — option visible and view renders; render as editor/viewer — page blocked by existing admin guard |
| SC-4 | View displays detected record count before any action | `behavioral` | Unit/UI test: with N defective fixture records, page shows N and no changes applied until a button is clicked |
| SC-5 | Apply All remediates every detected record and writes one `EditHistory` entry per record | `behavioral` | Run Apply All on fixture DB; all raw columns contain ꝏ not ∞; `edit_history` count matches detected count; `prev_data`/`current_data` snapshots correct |
| SC-6 | Review One-by-One allows per-record Apply, and Skip leaves the record unchanged | `behavioral` | Fixture test: apply record A, skip record B; A remediates with `EditHistory` entry, B retains ∞ with no history entry |
| SC-7 | After remediation, normalized columns are byte-identical to pre-remediation values | `behavioral` | Compare `sort_lx`/`normalized_term` pre/post — identical (∞ and ꝏ both map to `oozzz`) |
| SC-8 | FTS search for terms with ꝏ returns the same results as pre-remediation ∞ search | `behavioral` | Search `kꝏ` post-remediation; results match pre-remediation search for `k∞` |
| SC-9 | Seed data files contain ꝏ, not ∞ | `string` | `grep -c $'\u221e'` on both seed files returns 0 |
| SC-10 | Existing ∞ → `oozzz` fallback preserved in `generate_sort_lx()` | `string` | `"\u221e": "oozzz"` remains in `symbol_map` |

## Non-Goals

- No automatic migration at startup — remediation is an explicit admin action via the UI tool
- No changes to the FTS search query normalization path (already routes through `generate_sort_lx()`)
- No changes to `docs/lessons-learned/` (they document the current state accurately)
- No full pipeline re-ingestion — targeted remediation per record
- Soft-deleted records are excluded from scan and remediation

## Change Control

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1 | 2026-07-18 | AI agent | Initial spec (batch migration design) |
| 2 | 2026-09-29 | AI agent | Re-spec per developer direction: replace one-shot migration with interactive Table Maintenance tool (scan/count display, Apply All, Review One-by-One with per-record apply) |

---

🤖 Co-authored with AI: OpenCode (ollama-cloud/glm-5.3)