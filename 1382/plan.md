# Implementation Plan: Issue #1382 — ∞ (U+221E) → ꝏ (U+A74F) Remediation via Table Maintenance Tool

> Spec: `.issues/1382/spec.md` (v2) — GitHub issue Brothertown-Language/snea-shoebox-editor#1382
> Authorization: `approved-for-plan` (2026-09-29). Scope: plan creation. Implementation awaits separate authorization.

## Per-Task Implementation-Workflow Reference Card (applies to EVERY task below)

1. **RED** — write the enforcement test for this task's SC; run it with `uv run pytest`; it MUST fail for the right reason (method absent, assertion unmet)
2. **GREEN** — implement the minimum change that makes the test pass; run `uv run pytest test/<file>::<test>` until pass
3. **REFACTOR** — clean up; verify no cross-reference drift (stable anchors, no line-number refs); keep direct Unicode in data
4. **VERIFY** — run structural checks: `uvx ruff check src/ test/` (advisory), `uvx ruff format --check src/ test/` (advisory), `uvx pyright src/`
5. **COMMIT** — stage test + change together as one working slice; commit with descriptive message; `tests_run > 0` and `all_passed == true` recorded in `tmp/1382/tests-run-<task>.yaml`

Prohibitions (every task): no `pdflatex` (n/a), no ASCII regex on linguistic data, no `to_tsvector('english')`, no synthetic linguistic data, no bare `python`/`pytest` (always `uv run`), no edits to production DB, no `--no-verify`.

---

## Phase 1 — Foundation

### Task 1.1: Seed data remediation (SC-9)

- **Files:** `src/seed_data/natick_sample_100.txt`, `src/seed_data/natick_sample_100_no_diacritics.txt`
- **Change:** Replace every ∞ (U+221E) with ꝏ (U+A74F) — 364 occurrences per file (verified). Byte-level substitution only; no other characters touched; UTF-8 preserved.
- **Steps (reference card):**
  1. RED: `uv run pytest` a string-evidence check `tmp/1382/check_seed_red.py` asserting 0 U+221E occurrences — fails now (364 found)
  2. GREEN: apply substitution (`python` one-liner via `uv run python` is data transform, not inline mutation of API resources — permitted; or `sed`-free careful script writing to `./tmp` then move). Verify count 0 for U+221E, >0 for U+A74F
  3. REFACTOR: none (data files)
  4. VERIFY: `grep -c $'\u221e'` both files → 0; `grep -c $'\ua74f'` → 364 each; UTF-8 intact (`file` reports UTF-8)
  5. COMMIT: `Seed data: replace ∞ (U+221E) with ꝏ (U+A74F) oo-ligature (#1382)`
- **Evidence:** `string` — grep counts recorded in tests-run artifact.

### Task 1.2: Normalization for ꝏ (SC-1, SC-10)

- **Files:** `src/services/linguistic_service.py` (`generate_sort_lx()` symbol_map), `test/test_infinity_remediation_red.py` (new)
- **Change:** Add `"\ua74f": "oozzz"` to `symbol_map` (lines ~152-157). Keep `"\u221e": "oozzz"` and `"\u2714": ""` unchanged.
- **Steps:**
  1. RED: add `TestGenerateSortLxInfinity` with assertions: `generate_sort_lx("k∞") == "koozzz"` (already passes — regression pin) and `generate_sort_lx("kꝏ") == "koozzz"` (fails — ꝏ currently falls through). Run `uv run pytest test/test_infinity_remediation_red.py` — ꝏ test fails
  2. GREEN: add the dict entry; re-run — both pass
  3. REFACTOR: update the adjacent comment (line 150) to document both ∞ and ꝏ as Algonquian oo-ligature forms mapping to `oozzz`
  4. VERIFY: ruff + pyright clean on modified file; full `uv run pytest test/test_infinity_remediation_red.py` green
  5. COMMIT: `generate_sort_lx: map ꝏ (U+A74F) to oozzz alongside ∞ fallback (#1382)`
- **Evidence:** `behavioral` — unit tests SC-1; `string` — SC-10 (`"\u221e": "oozzz"` present).

---

## Phase 2 — Scan Service

### Task 2.1: Defect scan methods (SC-2)

- **Files:** `src/services/linguistic_service.py` (new methods), `test/test_infinity_remediation_red.py`
- **Change:** Add to `LinguisticService`:
  - `count_infinity_records(session=None) -> int` — count of records with `is_deleted=False` AND (`lx` contains U+221E OR `mdf_data` contains U+221E)
  - `list_infinity_records(session=None) -> list[dict]` — same filter, returns `[{id, lx, preview}]` where `preview` is a short context window of `mdf_data` around the first ∞ match
- **Reuse:** session pattern from `get_sources_with_counts()` (`with get_session()` / provided session); direct Unicode U+221E literal in query (no ASCII regex — per lessons-learned).
- **Steps:**
  1. RED: extend test file with pgserver fixture (pattern: `test/test_upload_search_entries.py` — `pgserver.get_server`, `Base.metadata.create_all`, seed User/Source/Record). Seed: rec A (∞ in lx+mdf_data), rec B (∞ in mdf_data only), rec C (clean), rec D (defective, `is_deleted=True`). Assert `count_infinity_records() == 2`, list ids == [A, B], previews non-empty. Fails — methods absent
  2. GREEN: implement both methods; re-run — pass
  3. REFACTOR: keep methods static, session-injectable (matches `populate_search_entries` signature convention)
  4. VERIFY: ruff + pyright; full new test file green
  5. COMMIT: `Add ∞ defect scan: count_infinity_records + list_infinity_records (#1382)`
- **Evidence:** `behavioral` — SC-2 fixture assertions including soft-deleted exclusion.

---

## Phase 3 — Remediation Write Path

### Task 3.1: Per-record + batch remediation (SC-5)

- **Files:** `src/services/linguistic_service.py`, `test/test_infinity_remediation_red.py`
- **Change:** Add:
  - `remediate_record(record_id, user_email, session_id, session=None) -> bool` — load record (skip if missing/`is_deleted`/no ∞); `prev_data = record.mdf_data` snapshot; replace ∞→ꝏ in `lx` and `mdf_data`; `record.sort_lx = generate_sort_lx(record.lx)`; add `EditHistory(record_id, user_email, session_id, version=record.current_version+1, change_summary="Remediate ∞ (U+221E) → ꝏ (U+A74F) oo-ligature", prev_data=prev_data, current_data=record.mdf_data)`; call `UploadService.populate_search_entries([record_id], session=session)` to rebuild search entries + FTS; commit; return True. Locked records: log warning, return False
  - `remediate_all_records(user_email, progress_callback=None, session=None) -> dict` — iterate `list_infinity_records()`; shared `uuid4` session_id; per-record remediation; return `{total, remediated, skipped}`
- **Reuse:** EditHistory snapshot pattern from `update_record()`; search rebuild from `populate_search_entries()` (unmodified).
- **Steps:**
  1. RED: fixture — remediate rec A; assert `lx`/`mdf_data` contain ꝏ not ∞; `edit_history` has exactly 1 new row with correct prev/current snapshots and `version == current+1`; search_entries/headword/gloss terms remediated. Fails — method absent
  2. GREEN: implement; re-run — pass
  3. REFACTOR: confirm no `to_tsvector` introduced (rebuild path owns FTS); confirm `is_deleted` guard
  4. VERIFY: ruff + pyright; test file green
  5. COMMIT: `Add remediate_record/remediate_all_records with EditHistory audit (#1382)`
- **Evidence:** `behavioral` — SC-5 assertions.

### Task 3.2: Review semantics + normalized-identity + FTS equivalence (SC-6, SC-7, SC-8)

- **Files:** `test/test_infinity_remediation_red.py` (assertions only; service code unchanged unless a defect surfaces — if a defect surfaces, fix under same SC)
- **Steps:**
  1. RED→GREEN cycle on three assertion groups:
     - SC-6: remediate A, do NOT remediate B (skip path is simply not calling remediate_record); assert A clean + history row, B still has ∞ + no history row for B
     - SC-7: before remediating, capture `sort_lx` of A and all `normalized_term` values for A's entries; remediate; assert byte-identical after
     - SC-8: pre-remediation, run FTS query against `fts_entries` using `to_tsvector('simple', generate_sort_lx("k∞"))` and record result ids; remediate; post-remediation query with `to_tsvector('simple', generate_sort_lx("kꝏ"))`; assert identical result set
  2. REFACTOR: none expected
  3. VERIFY: `uv run pytest test/test_infinity_remediation_red.py` all green
  4. COMMIT: `Tests: review semantics, normalized-identity, FTS equivalence for ∞ remediation (#1382)`
- **Evidence:** `behavioral` — SC-6/SC-7/SC-8 assertions.

---

## Phase 4 — Admin UI

### Task 4.1: Table Maintenance integration (SC-3, SC-4)

- **Files:** `src/frontend/pages/table_maintenance.py`, `test/ui/test_table_maintenance_infinity.py` (new)
- **Change:**
  - `main()` sidebar radio options list (line ~149): add `"∞→ꝏ Remediation"`; add `elif table_option == "∞→ꝏ Remediation": render_infinity_remediation()` to dispatch chain
  - New `render_infinity_remediation()`:
    - `st.header("∞ → ꝏ Remediation")` + explanatory info (∞ is a mis-encoding of the oo-ligature ꝏ; normalized search values unchanged)
    - Scan on render: `count = LinguisticService.count_infinity_records()`; display count via `st.metric` or `st.info`; Rescan button
    - If count == 0: info message only, no action buttons
    - If count > 0: two sections —
      - **Apply All**: warning about irreversibility-in-bulk, `st.button("Apply All", type="primary")` behind a `st.checkbox` confirm gate; on click, `remediate_all_records(user_email, progress_callback)` with progress bar + status container (pattern from `render_data_reprocessing_maintenance`, lines 176-192); success summary `f"Remediated {results['remediated']} of {results['total']} records."`
      - **Review One-by-One**: `records = list_infinity_records()`; display record i (id, lx, before/after preview — before = current text, after = same text with ∞→ꝏ applied for display); Apply button → `remediate_record(rid, user_email, session_id=uuid)` → advance to next; Skip button → advance without change; progress counter "i of N"
    - `handle_ui_error(e, ..., logger_name="snea.pages.table_maintenance")` on exceptions (existing pattern)
    - `user_email` from `st.session_state` (same source as other admin pages)
- **Steps:**
  1. RED: UI test (StreamlitAppTest, pattern from `test/ui/test_records_*.py`): admin session → radio includes "∞→ꝏ Remediation"; selecting it renders count display; non-admin session → existing guard blocks page. Fails — option absent
  2. GREEN: implement radio option + render function; re-run — pass
  3. REFACTOR: verify `main()` guard covers new branch; no duplicated scan logic in UI
  4. VERIFY: ruff + pyright; full new test file; full `uv run pytest test/` suite regression
  5. COMMIT: `Table Maintenance: add ∞→ꝏ remediation tool with scan/apply-all/review UI (#1382)`
- **Evidence:** `behavioral` — SC-3 (admin-only exposure), SC-4 (count display before action; zero-state informational).

---

## Post-Implementation (after all phases)

- Run full regression: `uv run pytest test/` (regression protocol: re-sync local DB first via `bash scripts/sync_prod_to_local.sh` — tests use pgserver fixtures, not the local DB, but the protocol is mandatory before any regression cycle)
- Record final `tmp/1382/tests-run-final.yaml` with enumerated tests, exit codes, pass/fail counts
- Structural: `uvx ruff check src/ test/`, `uvx ruff format --check src/ test/`, `uvx pyright src/`
- HALT for implementation authorization review — no PR without explicit `for_pr` scope

## SC → Task Traceability

| SC | Task | Evidence |
|----|------|----------|
| SC-1 | 1.2 | behavioral |
| SC-2 | 2.1 | behavioral |
| SC-3 | 4.1 | behavioral |
| SC-4 | 4.1 | behavioral |
| SC-5 | 3.1 | behavioral |
| SC-6 | 3.2 | behavioral |
| SC-7 | 3.2 | behavioral |
| SC-8 | 3.2 | behavioral |
| SC-9 | 1.1 | string |
| SC-10 | 1.2 | string |

All 10 SCs covered, one SC per item, per-SC RED/GREEN/REFACTOR/VERIFY/COMMIT cycle.

---

🤖 Co-authored with AI: OpenCode (ollama-cloud/glm-5.3)