---
plan_schema_version: "1.1"
issue: 1382
title: "Remediate ∞ (U+221E) → ꝏ (U+A74F) via Table Maintenance tool"
authorization_scope: for_plan
pr_strategy: stacked
phase_count: 5
dispatch: [test-driven-development:red, test-driven-development:green, test-driven-development:post-regression, verification-before-completion:verify, (orchestrator):commit-inline, audit:verification-audit, (orchestrator):z3-check, finishing-a-development-branch:checklist, git-workflow-pr:review-prep, git-workflow-pr:create, completion-core:completion]
---

# Implementation Plan — #1382 — ∞ (U+221E) → ꝏ (U+A74F) Remediation via Table Maintenance Tool

- **Issue:** .issues/1382/spec.md
- **URL:** https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1382

**Goal:** Eliminate the ∞ (U+221E) mis-encoding of the Eliot/Trumbull oo-ligature ꝏ (U+A74F) from the database via an admin-controlled DB maintenance tool under Table Maintenance — scan and display the defective-record counts (remediable and locked separately), then a single confirm-gated Apply All — with NO `EditHistory` entries and NO version bumps (DB maintenance, not an editorial edit), locked records never altered but counted and reported post-remediation, normalized columns provably stable, seed data cleaned, and ꝏ added to `generate_sort_lx()` normalization alongside the preserved ∞ fallback.

**Architecture:** Three-layer additive change. Service layer (`LinguisticService`) gains 3 new methods: `count_infinity_records()`, `list_infinity_records()` (read-only scan; locked defective records counted/reported separately as unremediable), `remediate_all_records()` (maintenance batch write path; remediates only non-locked, non-deleted defective records; locked records are never touched and are reported in the outcome report `{remediated, locked}`; no `EditHistory` writes, no `current_version` bumps). The write path reuses `UploadService.populate_search_entries()` unmodified for search-entry/FTS rebuild — no new `to_tsvector` calls, `'simple'` tsconfig preserved. UI layer (`table_maintenance.py`) gains one sidebar radio option and one render function; admin guard inherited from `main()`; counts displayed before action; single confirm-gated Apply All; outcome report rendered on completion. Data layer: byte-substitution in 2 seed files. Success defined at suite level: full test suite green plus per-SC behavioral/string evidence. 13 SCs across 5 phases (4 implementation + 1 terminal gate); one item per SC, per-item RED/GREEN/post-regression/verify/commit cycle.

**Files:**
- `src/services/linguistic_service.py` (symbol_map entry + 3 new methods)
- `src/frontend/pages/table_maintenance.py` (radio option + render function)
- `src/seed_data/natick_sample_100.txt`
- `src/seed_data/natick_sample_100_no_diacritics.txt`
- `test/test_infinity_remediation_red.py` (new)
- `test/ui/test_table_maintenance_infinity.py` (new)

**Out of scope (unchanged):** `src/services/upload_service.py` (consumed, not modified); `src/database/models/**`; FTS query path; `docs/lessons-learned/**`; paper files (migrated to snea-phonetics); any automatic startup migration; per-record review UI (removed per stakeholder direction); `EditHistory` writes and `current_version` bumps (removed per stakeholder direction — DB maintenance, not an editorial edit).

---

## Pre-Flight Guard (Mandatory)

Check your tool list for a tool named `task`.

- Present ⇒ orchestrator — proceed.
- Absent ⇒ sub-agent — do NOT execute any instruction below. Return `BLOCKED` with `ORCHESTRATOR_ONLY_SKILL_CARD` (cards) or `ORCHESTRATOR_ONLY_PLAN` (plans) and halt.

---

## Phase Table

| Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch |
|-------|------|---------|-----|------------|------------|----------|
| 1 | Foundation | Seed data clean + ꝏ normalization (with ∞ fallback pin) | SC-8, SC-1, SC-9 | — | 5-14 | task-card (5-8, 10-13) + direct (9, 14) |
| 2 | Scan service | Read-only ∞ defect scan with fixture coverage; locked-record count reported separately | SC-2, SC-10 | 1 | 15-19 | task-card (15-18) + direct (19) |
| 3 | Maintenance write path | Batch remediation of non-locked defective records; locked records never altered; outcome report; normalized/FTS proof items | SC-5, SC-11, SC-12, SC-13, SC-6, SC-7 | 2 | 20-34 | task-card (20-23, 25-28, 30-33) + direct (24, 29, 34) |
| 4 | Admin UI | Sidebar exposure + remediable/locked count display + confirm-gated Apply All + outcome report render | SC-3, SC-4 | 2, 3 | 35-44 | task-card (35-38, 40-43) + direct (39, 44) |
| 5 | Suite-health gate + completion | Full-suite regression gate + post-implementation pipeline | SC-1..SC-13 | 1, 2, 3, 4 | 45-55 | task-card (45-48, 50-55) + direct (49) |

---

## Pre-Implementation

- [ ] 1. **Coherence gate (direct).** Re-read `.issues/1382/spec.md` and the analytical artifacts under `.issues/1382/artifacts/` (concern-map.yaml, blast-radius.yaml, state-analysis.yaml); confirm 13 SCs map to phases with no structural drift (phase-1: SC-8/SC-1/SC-9; phase-2: SC-2/SC-10; phase-3: SC-5/SC-11/SC-12/SC-13/SC-6/SC-7; phase-4: SC-3/SC-4; phase-5: all) before any implementation. **→ all SCs**
- [ ] 2. **Baseline check (direct).** Verify working tree is on the issue feature branch, trunk tip aligned (per git-workflow pre-work); record baseline evidence under `tmp/issue-1382/artifacts/`. **→ all SCs**
- [ ] 3. **Pre-regression (task-card).** Run regression test patterns before the RED phase per test-driven-development phase-0 task: `task(..., prompt: "execute phase-0 task from test-driven-development")`. Regression Test Protocol (AGENTS.md): run `bash scripts/sync_prod_to_local.sh` first — the sync script from the feature branch under test. Clean `tmp/issue-1382/artifacts/pipeline-pre-regression-*` first. **→ all SCs**
- [ ] 4. **Pre-regression verify (task-card).** Verify pre-regression results per verification-before-completion: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-pre-regression-verify-*` first. **→ all SCs**

---

## Admonishments

> **Compliance:** All SCs must pass before completion. Partial implementation is not permitted. Each item is daisy-chained — item N's commit is precondition for item N+1's RED.

> **One step at a time.** Execute exactly one step. Report progress. Wait for instruction before the next step.

> **Step status:** Report `[item N] [PASS|FAIL]` after each step. If FAIL, report blocker and halt.

> **Self-Remediation Protocol:** If a step FAILs: diagnose root cause, fix the deliverable, re-verify. If the fix requires spec revision, update the spec and re-enter the plan. Escalate only after remediation failure.

> **Enforcement gate:** All SCs (SC-1 through SC-13) must pass before this plan is complete. Behavioral SCs demand behavioral evidence — prose or structural substitutes are EVIDENCE_TYPE_MISMATCH (FAIL).

> **Data integrity:** No synthetic linguistic data. All test fixtures use real characters ∞ (U+221E) and ꝏ (U+A74F) as direct Unicode literals. No ASCII regex on linguistic data. No `to_tsvector('english')`. No automatic production mutation — remediation is admin-triggered only. DB maintenance framing: no `EditHistory` writes and no `current_version` bumps anywhere in the remediation path (stakeholder-directed — do not reintroduce editorial side effects).

---

### Phase 1 — Foundation

**Concern:** Clean the seed fixture data and extend normalization so both oo-ligature encodings map to `oozzz` — the substrate every later phase builds on.

**Code Path Coverage:** `src/seed_data/natick_sample_100*.txt` (byte substitution) and `src/services/linguistic_service.py` `generate_sort_lx()` `symbol_map` (additive dict entry + comment). No consumer of `generate_sort_lx()` is modified.

**Cross-Cutting SCs:** SC-1 and SC-9 co-locate in item 2 (the pin and the addition target the same function); SC-8 is independent data cleanup.

**Interface Boundaries:** `symbol_map` is internal to `generate_sort_lx()`; the addition must not alter any existing key's mapping. All existing callers (populate_search_entries, search normalization, reprocessing) see identical behavior for existing inputs.

**State Transitions:** Seed files: 364 U+221E → 0 U+221E, 364 U+A74F per file. Normalization: ꝏ input falls through to bare lowercase → now maps to `oozzz`; ∞ mapping unchanged.

**Steps:**

- [ ] 5. **RED (task-card).** Write the seed-evidence check: a test asserting 0 U+221E occurrences in both seed files (reads files, counts `\u221e`) — fails now (364 found per file). Place in `test/test_infinity_remediation_red.py` (new file, pgserver fixture setUpClass per `test/test_upload_search_entries.py` pattern even though this item needs no DB — later items share the fixture). **→ SC-8** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-red-*` first.
- [ ] 6. **GREEN (task-card).** Replace every ∞ (U+221E) with ꝏ (U+A74F) in both seed files via a `./tmp/` transform script (`uv run python`); verify counts (0 U+221E, 364 U+A74F per file), UTF-8 intact, file diffs show only the intended byte substitutions. Seed test passes. **→ SC-8** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 7. **Post-regression (task-card).** Run regression test patterns after GREEN per test-driven-development phase-4 task: `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-post-regression-*` first. **→ SC-8**
- [ ] 8. **Verify (task-card).** Verify per verification-before-completion: seed-file counts asserted by the committed test; full new test file run; `git status` shows only the two seed files + new test file staged. **→ SC-8** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 9. **Commit (direct).** `git add src/seed_data/ test/test_infinity_remediation_red.py && git commit -m "fix(1382): replace ∞ (U+221E) with ꝏ (U+A74F) in seed data"`. Test + change committed as one atomic slice. **→ SC-8**
- [ ] 10. **RED (task-card).** Add `TestGenerateSortLxLigature` assertions to the test file: `generate_sort_lx("k∞") == "koozzz"` (regression pin, SC-9 behavioral half) and `generate_sort_lx("kꝏ") == "koozzz"` (SC-1, fails — ꝏ currently falls through). Run the file: pin passes, ꝏ assertion fails. **→ SC-1, SC-9** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`.
- [ ] 11. **GREEN (task-card).** Add `"\ua74f": "oozzz"` to `symbol_map` in `generate_sort_lx()`; update the adjacent comment to document both ∞ and ꝏ as Algonquian oo-ligature forms mapping to `oozzz`. Re-run: both assertions pass. **→ SC-1, SC-9** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 12. **Post-regression (task-card).** Run regression patterns after GREEN (full suite — symbol_map is consumed by search/reprocessing paths): `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-post-regression-*` first. **→ SC-1, SC-9**
- [ ] 13. **Verify (task-card).** Verify: both unit assertions pass; string evidence — `"\u221e": "oozzz"` entry present in source (SC-9 string half); ruff/pyright clean on modified files. **→ SC-1, SC-9** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 14. **Commit (direct).** `git add src/services/linguistic_service.py test/test_infinity_remediation_red.py && git commit -m "feat(1382): map ꝏ (U+A74F) to oozzz in generate_sort_lx, pin ∞ fallback"`. **→ SC-1, SC-9**

**Cost frame:** Verifying the normalization change via the full suite costs minutes — `generate_sort_lx()` is consumed by search indexing and reprocessing, so a wrong edit breaks search invisibly at suite level. Skipping costs silent search corruption for every future upload — discovered only when a linguist's query misses a real headword.

**Phase 1 completion (VbC assertions):**
- [ ] Seed files: 0 U+221E, 364 U+A74F each; UTF-8 intact.
- [ ] `generate_sort_lx("kꝏ") == "koozzz"` and `generate_sort_lx("k∞") == "koozzz"` both pass; source retains the ∞ mapping.
- [ ] `git status` clean; no files outside the declared set modified.

**Concern transition:** Leaving foundation → entering scan service. Phase 2 queries records through the now-correct normalization substrate (ꝏ-bearing clean records must not be mis-scanned).

---

### Phase 2 — Scan service

**Concern:** Read-only defect scan — count and list exactly the non-deleted records carrying ∞ in `lx` or `mdf_data`, with the locked defective-record count reported separately.

**Code Path Coverage:** `src/services/linguistic_service.py` — two new static methods, session-injectable per `populate_search_entries` signature convention. No UI, no writes.

**Cross-Cutting SCs:** SC-2 is the primary gate; SC-10 (locked-record separate count reporting) lands in the same chain. The fixture (seeded User/Source/Records incl. soft-deleted defective record and locked defective record) is reused by every Phase 3 item.

**Interface Boundaries:** `count_infinity_records(session=None) -> int` (remediable count, locked records excluded) plus a separate locked defective-record count (e.g., returned alongside or via a companion query — remediable and locked counts reported separately per SC-10); `list_infinity_records(session=None) -> list[dict]` with `{id, lx, preview, is_locked}` — preview is a context window of `mdf_data` around the first ∞ match; locked defective records are reported (`is_locked` flag / separate count), never treated as remediable. Direct Unicode literal in the query — no ASCII regex (lessons-learned mandate).

**State Transitions:** DB unchanged (read-only). Fixture state: 5 seeded records → scan reports exactly 2 remediable defective (A: ∞ in lx+mdf_data; B: ∞ in mdf_data only), excluding clean C, soft-deleted defective D, and locked defective E (E counted separately in the locked count).

**Steps:**

- [ ] 15. **RED (task-card).** Extend the pgserver fixture: seed User (test@example.com), Source, and Records A (∞ in lx+mdf_data), B (∞ in mdf_data only), C (clean), D (defective, `is_deleted=True`), E (defective, `is_locked=True`). Assert remediable count == 2; `list_infinity_records()` returns ids [A, B] with non-empty previews; locked defective record E is reported separately (locked count ≥ 1 / `is_locked` flag), not in the remediable set. Fails — methods absent. **→ SC-2, SC-10** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-red-*` first.
- [ ] 16. **GREEN (task-card).** Implement both methods: filter `is_deleted == False`, match U+221E in `lx` OR `mdf_data` (direct Unicode literal, no ASCII regex); preview = bounded window around first match; locked defective records (`is_locked == True`) excluded from the remediable count and reported separately (locked count reported distinctly — never altered, per the record-lock immutability invariant). Re-run: assertions pass. **→ SC-2, SC-10** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 17. **Post-regression (task-card).** Run regression patterns after GREEN: `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-post-regression-*` first. **→ SC-2, SC-10**
- [ ] 18. **Verify (task-card).** Verify: fixture assertions pass; soft-deleted exclusion confirmed; locked defective record excluded from remediable count and reported separately; ruff/pyright clean; no write path introduced (read-only methods — session never commits mutations). **→ SC-2, SC-10** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 19. **Commit (direct).** `git add src/services/linguistic_service.py test/test_infinity_remediation_red.py && git commit -m "feat(1382): add ∞ defect scan service (count/list, soft-deleted excluded, locked count reported separately)"`. **→ SC-2, SC-10**

**Cost frame:** Verifying scan precision via the 4-record fixture costs seconds and catches the two costly error classes — over-match (remediating clean records: data corruption) and under-match (missing defective records: the defect persists invisibly). Skipping costs a miscount displayed to the admin on every tool open, eroding trust in the whole feature.

**Phase 2 completion (VbC assertions):**
- [ ] Scan count/list matches fixture truth exactly; soft-deleted defective record excluded; locked defective record excluded from the remediable count and reported separately.
- [ ] `git status` clean.

**Concern transition:** Leaving scan service → entering the maintenance write path. Phase 3 remediates exactly the records the scan returns as remediable.

---

### Phase 3 — Maintenance write path

**Concern:** Batch maintenance remediation of non-locked defective records — locked records never altered, outcome report stating remediated and locked unremediated counts — then the two proof items (normalized-identity, FTS equivalence) as separate assertion items. NO `EditHistory` writes, NO `current_version` bumps anywhere in this path (DB maintenance, not an editorial edit).

**Code Path Coverage:** `src/services/linguistic_service.py` — `remediate_all_records(progress_callback=None, session=None) -> dict`. Reuses `UploadService.populate_search_entries([rid], session=session)` unmodified for search-entry/FTS rebuild. No new `to_tsvector` calls.

**Cross-Cutting SCs:** SC-5 (write-path gate: Apply All remediates every non-locked, non-deleted defective record) and SC-13 (locked presence does not block remediable remediation) ride this chain; SC-11 (locked records never altered) and SC-12 (outcome report stating remediated and locked unremediated counts) land in the same items; SC-6/SC-7 are proof assertions against that path's invariants, each its own item and commit. SC-6/SC-7 encode the spec's protected invariants (normalized stability, FTS equivalence) enforced again at gate level via the dependency contract.

**Interface Boundaries:** Locked records: never touched — no data change, no version bump, no history entry (record-lock immutability invariant; the maintenance path writes no `EditHistory` rows and does not modify `current_version` for any record). Missing/clean/soft-deleted records: excluded by the scan predicate. Batch returns `{remediated, locked}` — remediated = count of non-locked defective records transformed; locked = count of locked defective records left unremediated (reported, never altered).

**State Transitions:** Record: defective → remediated (lx/mdf_data carry ꝏ; sort_lx recomputed to the identical value; search entries + fts_vector rebuilt; `current_version` unchanged; no `edit_history` row). Locked record E: unchanged in every column, reported in the outcome report. Normalized columns: byte-identical pre/post (∞ and ꝏ both → oozzz).

**Steps:**

- [ ] 20. **RED (task-card).** Assert against the fixture: run `remediate_all_records(...)` → A and B remediated: `lx`/`mdf_data` contain ꝏ not ∞; `sort_lx` recomputed; A's and B's search_entries/headword/gloss terms remediated; `current_version` unchanged for both; no `edit_history` rows created for any record. Also assert locked non-interference: E's `lx`/`mdf_data`/`sort_lx`/`current_version` identical to pre-run values, no `edit_history` row for E; outcome report `{remediated: 2, locked: 1}` (fails — method absent). Fails — method absent. **→ SC-5, SC-11, SC-12, SC-13** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-red-*` first.
- [ ] 21. **GREEN (task-card).** Implement `remediate_all_records`: iterate the scan's remediable set (non-locked, non-deleted defective records only); per record: replace ∞→ꝏ in `lx` and `mdf_data`, `record.sort_lx = generate_sort_lx(record.lx)`, call `UploadService.populate_search_entries([record_id], session=session)`, commit — NO `EditHistory` writes, NO `current_version` bumps; locked records are never touched; progress_callback per item; return outcome report `{remediated, locked}` (remediated = applied count; locked = unremediated locked defective count). Re-run: assertions pass. **→ SC-5, SC-11, SC-12, SC-13** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 22. **Post-regression (task-card).** Run regression patterns after GREEN (full suite — write path touches records, search entries): `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-post-regression-*` first. **→ SC-5, SC-11, SC-12, SC-13**
- [ ] 23. **Verify (task-card).** Verify: Apply All on the fixture remediates every non-locked defective record; locked record E unchanged in every column with no history row; outcome report `{remediated, locked}` correct; zero `edit_history` rows written by the batch and no `current_version` changes (maintenance framing verified). **→ SC-5, SC-11, SC-12, SC-13** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 24. **Commit (direct).** `git add src/services/linguistic_service.py test/test_infinity_remediation_red.py && git commit -m "feat(1382): add remediate_all_records maintenance batch (locked records untouched, outcome report, no EditHistory writes)"`. **→ SC-5, SC-11, SC-12, SC-13**
- [ ] 25. **RED (task-card).** Normalized-identity: assert sort_lx and all normalized_term values for A and B are byte-identical pre/post remediation (capture before, remediate, compare). Fails — assertion absent. **→ SC-6** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-red-*` first.
- [ ] 26. **GREEN (task-card).** Land the normalized-identity assertion set; re-run: passes (both ligature encodings map to oozzz — the property holds; if it FAILs here, a write-path defect surfaced and is fixed under SC-5's service code, not by weakening the assertion). **→ SC-6** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 27. **Post-regression (task-card).** Run regression patterns after GREEN: `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-post-regression-*` first. **→ SC-6**
- [ ] 28. **Verify (task-card).** Verify: byte-identity holds for every normalized column touched by remediation. **→ SC-6** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 29. **Commit (direct).** `git add test/test_infinity_remediation_red.py && git commit -m "test(1382): normalized-identity — sort_lx/normalized_term stable across remediation"`. **→ SC-6**
- [ ] 30. **RED (task-card).** FTS equivalence: pre-remediation, query `fts_entries` with `to_tsvector('simple', generate_sort_lx("k∞"))`, record result ids; post-remediation query with `to_tsvector('simple', generate_sort_lx("kꝏ"))`; assert identical result set. Fails — assertion absent. **→ SC-7** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-red-*` first.
- [ ] 31. **GREEN (task-card).** Land the FTS-equivalence assertion set; re-run: passes. **→ SC-7** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 32. **Post-regression (task-card).** Run regression patterns after GREEN: `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-post-regression-*` first. **→ SC-7**
- [ ] 33. **Verify (task-card).** Verify: result-set identity holds; `'simple'` tsconfig used (no `'english'` anywhere in the new path). **→ SC-7** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 34. **Commit (direct).** `git add test/test_infinity_remediation_red.py && git commit -m "test(1382): FTS equivalence — ꝏ query matches ∞ results"`. **→ SC-7**

**Cost frame:** Verifying the write path per-item costs minutes of pgserver fixture time. Skipping costs the two catastrophic failure modes — a locked-record mutation (violating the record-lock immutability invariant) and a normalized-column drift (breaks search sort order silently for every future query). The proof items exist because these invariants are the spec's entire reason for the maintenance design.

**Phase 3 completion (VbC assertions):**
- [ ] Apply-all fixture run: every non-locked defective record remediated; locked record E unchanged in every column and listed in the outcome report; zero `edit_history` rows written; no `current_version` changes.
- [ ] Normalized columns byte-identical pre/post; FTS result sets identical.
- [ ] `git status` clean; `upload_service.py` unmodified.

**Concern transition:** Leaving the maintenance write path → entering the admin UI. Phase 4 wires the button to the completed, proven service surface.

---

### Phase 4 — Admin UI

**Concern:** Expose the tool in Table Maintenance and implement the count-display → confirm-gated Apply All flow with the locked-count display and outcome report render.

**Code Path Coverage:** `src/frontend/pages/table_maintenance.py` — one radio option in `main()`'s sidebar list, one `elif` dispatch, one new `render_infinity_remediation()` function; `test/ui/test_table_maintenance_infinity.py` (new, StreamlitAppTest pattern from `test/ui/test_records_*.py`).

**Cross-Cutting SCs:** SC-3 (admin-only exposure) and SC-4 (remediable + locked count display before action, confirm gate, outcome report render) land in this phase as two items.

**Interface Boundaries:** Consumes `count_infinity_records`, `list_infinity_records`, `remediate_all_records` (and the scan's separate locked count). Admin guard inherited from `main()` — no new auth logic. Errors via `handle_ui_error(..., logger_name="snea.pages.table_maintenance")`. Progress via the `render_data_reprocessing_maintenance()` pattern (progress bar + status container).

**State Transitions:** UI states: zero-state (count 0 → info only, no buttons) → detected-state (remediable count N + locked count M displayed + confirm-gated Apply All) → apply-all-state (progress bar) → outcome report (remediated count; locked records remain unremediated). No DB mutation until the confirm-gated button is clicked.

**Steps:**

- [ ] 35. **RED (task-card).** UI test (new `test/ui/test_table_maintenance_infinity.py`): admin session (`user_role="admin"` in session_state) → sidebar radio includes "∞→ꝏ Remediation"; non-admin session → page blocked by the existing guard. Fails — option absent. **→ SC-3** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-red-*` first.
- [ ] 36. **GREEN (task-card).** Add `"∞→ꝏ Remediation"` to the radio options list in `main()`; add the `elif` dispatch to `render_infinity_remediation()`. Re-run: exposure test passes. **→ SC-3** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 37. **Post-regression (task-card).** Run regression patterns after GREEN: `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-post-regression-*` first. **→ SC-3**
- [ ] 38. **Verify (task-card).** Verify: admin sees the option; non-admin blocked; existing three options unaffected. **→ SC-3** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 39. **Commit (direct).** `git add src/frontend/pages/table_maintenance.py test/ui/test_table_maintenance_infinity.py && git commit -m "feat(1382): expose ∞→ꝏ remediation in Table Maintenance (admin-only)"`. **→ SC-3**
- [ ] 40. **RED (task-card).** UI flow test: with N defective fixture records (including locked), the view displays the remediable count and the locked count separately and applies nothing until the confirm-gated Apply All is clicked; zero-state (0 defective) shows info, no action buttons; Apply All requires confirm; after Apply All the outcome report states the remediated count and the locked (unremediated) count. Fails — view incomplete. **→ SC-4, SC-12** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-red-*` first.
- [ ] 41. **GREEN (task-card).** Implement `render_infinity_remediation()`: header + explanation; scan on render (remediable count via `count_infinity_records()`, locked defective count reported separately); Rescan button; zero-state info; Apply All behind confirm checkbox with progress (pattern from `render_data_reprocessing_maintenance()`) and post-run outcome report display (remediated count + locked unremediated count from the batch dict); `handle_ui_error` wrapping. Re-run: flow test passes. **→ SC-4, SC-12** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 42. **Post-regression (task-card).** Run regression patterns after GREEN: `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-post-regression-*` first. **→ SC-4**
- [ ] 43. **Verify (task-card).** Verify: remediable + locked count display before action; zero-state; confirm-gate on Apply All; no mutation without click; outcome report renders remediated and locked counts. **→ SC-4** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 44. **Commit (direct).** `git add src/frontend/pages/table_maintenance.py test/ui/test_table_maintenance_infinity.py && git commit -m "feat(1382): count display, confirm-gated apply-all, outcome report"`. **→ SC-4**

**Cost frame:** Verifying the UI flow costs minutes of StreamlitAppTest runtime. Skipping costs the defect class this spec exists to prevent — an unconfirmed bulk mutation or a count display that lies about what will change. The confirm gate and scan-first display are the stakeholder-facing safety properties; a broken render discovered post-merge burns stakeholder trust in the tool.

**Phase 4 completion (VbC assertions):**
- [ ] Admin-only exposure verified; non-admin blocked.
- [ ] Remediable and locked counts display precede any action; zero-state informational; Apply All confirm-gated; outcome report states remediated and locked counts.
- [ ] `git status` clean.

**Concern transition:** Leaving the admin UI → entering the suite-health gate and post-implementation pipeline. All 13 SCs' code and tests are committed; the gate proves them at suite level.

---

### Phase 5 — Suite-health gate + completion

**Concern:** Prove the full suite green after DB re-sync per the Regression Test Protocol and run the post-implementation pipeline (audit → z3-check → structural checks → pre-PR gate → regression check → review-prep → PR → completion summary).

**Code Path Coverage:** No new code — verification-only plus pipeline gates. File coverage re-asserted: the 4 modified/added files plus 2 new test files; nothing outside the declared set.

**Cross-Cutting SCs:** The gate aggregates all 13 SCs at suite level, plus the dependency contract's invariants (normalized_columns_stable, simple_tsconfig_only, no_auto_migration, locked_records_untouched, no_edit_history_writes).

**Interface Boundaries:** PR creation requires `for_pr` authorization scope — the plan halts before review-prep if implementation authorization did not extend to PR. Human-only merge applies.

**State Transitions:** Intermediate suite states converge to the final contract: full suite green, all per-SC evidence artifacts recorded under `tmp/issue-1382/artifacts/`, tests-run.yaml recorded. DB re-synced immediately before the gate.

**Steps:**

- [ ] 45. **RED — gate precondition (task-card).** Run `bash scripts/sync_prod_to_local.sh` (Regression Test Protocol — sync script from the feature branch under test) then the full-suite `uv run pytest test/` pre-gate; assert the target is unmet while implementation is incomplete OR record the passing state if all items landed — either way the run is recorded as the gate baseline. **→ all SCs** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-red-*` first.
- [ ] 46. **GREEN — full-suite gate (task-card).** Full-suite `uv run pytest test/` after DB re-sync; assert all tests pass (existing suite + new infinity remediation tests); record tests-run.yaml per the tests-run mandate (`tests_run > 0`, `all_passed == true`, enumerated tests + exit codes). **→ all SCs** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 47. **Verify — suite gate (task-card).** Verify per verification-before-completion: full-suite exit code 0, per-SC evidence artifacts present (SC-1..SC-13), behavioral evidence for behavioral SCs (no structural substitutes). **→ all SCs** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 48. **Audit (task-card).** Adversarial audit of the deliverable: `task(..., prompt: "execute verification-audit DiMo investigator from audit. Read 'audit/tasks/verification-audit-investigator.md' first")` — followed by validator, evaluator, arbiter in sequence. Clean `tmp/issue-1382/artifacts/pipeline-audit-*` first. **→ all SCs**
- [ ] 49. **Z3 check (direct).** Run `./.opencode/tools/solve check --state-path .issues/1382/artifacts/state.yaml --contract-path .issues/1382/dependency-contract.yaml` directly (no sub-agent dispatch). Clean `tmp/issue-1382/artifacts/pipeline-z3-check-*` first. **→ all SCs**
- [ ] 50. **Structural checks (task-card).** Run the finishing checklist (lint, typecheck, branch readiness): `task(..., prompt: "execute checklist task from finishing-a-development-branch")`. Clean `tmp/issue-1382/artifacts/pipeline-structural-checks-*` first. **→ all SCs**
- [ ] 51. **Pre-PR gate (task-card).** Verify all SC verdicts — BLOCK if any FAIL: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-pre-pr-gate-*` first. **→ all SCs**
- [ ] 52. **Regression check (task-card).** Final regression check before PR: `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-regression-check-*` first. **→ all SCs**
- [ ] 53. **Review-prep (task-card).** Prepare PR review context: `task(..., prompt: "execute review-prep from git-workflow-pr. Read 'git-workflow-pr/tasks/review-prep.md' first")`. **→ all SCs**
- [ ] 54. **Create PR (task-card).** Create the pull request (stacked strategy — one branch, N commits, one PR): `task(..., prompt: "execute create task from git-workflow-pr")`. Human-only merge — the agent does not merge. **→ all SCs**
- [ ] 55. **Completion summary (task-card).** Generate the completion executive summary: `task(..., prompt: "execute completion task from completion-core")`. **→ all SCs**

**Cost frame:** Verifying the full-suite gate costs minutes of execution time plus a DB re-sync. Skipping costs an unverifiable completion claim — the AGENTS.md tests-run mandate makes behavioral evidence with `tests_run > 0` and `all_passed == true` a hard gate; a suite claimed green without the recorded artifact is a fabricated pass.

**Phase 5 completion (VbC assertions):**
- [ ] Full-suite run: all tests pass; DB pre-synced via `bash scripts/sync_prod_to_local.sh`; tests-run.yaml recorded.
- [ ] Audit, z3-check, structural checks, pre-PR gate, regression check, review-prep, PR creation, completion summary — all gates PASS.
- [ ] `git status` clean; files outside the declared set untouched.

**Concern transition:** Leaving the suite-health gate and post-implementation pipeline — all 13 SCs covered, phase DAG complete with no cycles. Plan execution ends here; human-only merge applies.

---

## Exit Criteria

- [ ] C1. SC-1 passes: `generate_sort_lx("kꝏ") == "koozzz"` (unit assertion, committed).
- [ ] C2. SC-2 passes: scan count/list matches fixture truth exactly; soft-deleted defective record excluded.
- [ ] C3. SC-3 passes: sidebar option visible to admin, blocked for non-admin (StreamlitAppTest).
- [ ] C4. SC-4 passes: remediable and locked counts displayed before action; zero-state informational; no mutation until the confirm-gated button click.
- [ ] C5. SC-5 passes: Apply All remediates every non-locked, non-deleted defective record (raw columns ꝏ not ∞).
- [ ] C6. SC-6 passes: sort_lx and normalized_term byte-identical pre/post remediation.
- [ ] C7. SC-7 passes: FTS ꝏ post-remediation result set identical to ∞ pre-remediation result set.
- [ ] C8. SC-8 passes: both seed files contain 0 U+221E and 364 U+A74F.
- [ ] C9. SC-9 passes: ∞ → oozzz mapping present in symbol_map source; ∞ unit pin passes.
- [ ] C10. SC-10 passes: scan reports the locked defective-record count separately from the remediable count.
- [ ] C11. SC-11 passes: locked defective records retain ∞ and are otherwise unchanged after Apply All (no data change, no version bump, no history entry).
- [ ] C12. SC-12 passes: outcome report states the remediated count and the locked (unremediated) count.
- [ ] C13. SC-13 passes: locked presence does not block remediable remediation (mixed fixture: all unlocked defective records remediated).
- [ ] C14. Post-implementation pipeline gates all pass (audit, z3-check, structural checks, pre-PR gate, regression check) and the PR is created for the stacked branch.

---

## lifecycle_events

- timestamp: 2026-09-29T22:40:00Z
  event: plan_created
  plan_path: .issues/1382/plan.md
  phase_count: 5

- timestamp: 2026-10-03T04:00:00Z
  event: plan_revised
  plan_path: .issues/1382/plan.md
  reason: "Spec v3 — locked-record exclusion policy (old SC-11/SC-12/SC-13), upload_service.py:1798-1843 pattern citation; plan SC coverage regenerated to match"

- timestamp: 2026-10-03T00:00:00Z
  event: plan_revised
  plan_path: .issues/1382/plan.md
  reason: "Spec v5 — 17-SC renumbering (v4 decomposition of compound SCs); plan SC coverage remapped to SC-1..SC-17 with line-number references replaced by stable anchors"

- timestamp: 2026-10-04T04:45:00Z
  event: plan_revised
  plan_path: .issues/1382/plan.md
  reason: "Spec v7 — stakeholder-directed intent change (Dr. Keith Cunningham, relayed by developer): DB maintenance framing (no EditHistory writes, no current_version bumps), Apply All-only remediation path (Review One-by-One removed), locked-record maintenance-framed SCs (never altered, counted and reported); SC set renumbered SC-1..SC-13; plan SC coverage and dependency contract regenerated to match"

---

<!-- Pre-Flight Guard section above is canonical per plan-artifact-format §3.5 — reason code ORCHESTRATOR_ONLY_PLAN -->
<!-- Plan rebuilt for spec v7 (stakeholder-directed DB-maintenance framing): 13 SCs, 5 phases, full pre-regression + per-item red/green/post-regression/verify/commit chains as checkbox lists, phase table, admonishments, cost frames, VbC assertions, exit criteria -->

🤖 Co-authored with AI: OpenCode (ollama-cloud/glm-5.3)
🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
