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

**Goal:** Eliminate the ∞ (U+221E) mis-encoding of the Eliot/Trumbull oo-ligature ꝏ (U+A74F) from the database via an admin-controlled interactive tool under Table Maintenance — scan and display the defective-record count, then Apply All or Review One-by-One — with an `EditHistory` audit entry per remediated record, normalized columns provably stable, seed data cleaned, and ꝏ added to `generate_sort_lx()` normalization alongside the preserved ∞ fallback.

**Architecture:** Three-layer additive change. Service layer (`LinguisticService`) gains 4 new methods: `count_infinity_records()`, `list_infinity_records()` (read-only scan), `remediate_record()`, `remediate_all_records()` (write path). The write path reuses `UploadService.populate_search_entries()` unmodified for search-entry/FTS rebuild — no new `to_tsvector` calls, `'simple'` tsconfig preserved. UI layer (`table_maintenance.py`) gains one sidebar radio option and one render function; admin guard inherited from `main()`. Data layer: byte-substitution in 2 seed files. Success defined at suite level: full test suite green plus per-SC behavioral/string evidence. 10 SCs across 5 phases (4 implementation + 1 terminal gate); one item per SC, per-item RED/GREEN/post-regression/verify/commit cycle.

**Files:**
- `src/services/linguistic_service.py` (symbol_map entry + 4 new methods)
- `src/frontend/pages/table_maintenance.py` (radio option + render function)
- `src/seed_data/natick_sample_100.txt`
- `src/seed_data/natick_sample_100_no_diacritics.txt`
- `test/test_infinity_remediation_red.py` (new)
- `test/ui/test_table_maintenance_infinity.py` (new)

**Out of scope (unchanged):** `src/services/upload_service.py` (consumed, not modified); `src/database/models/**`; FTS query path; `docs/lessons-learned/**`; paper files (migrated to snea-phonetics); any automatic startup migration.

---

## Pre-Flight Guard (Mandatory)

Check your tool list for a tool named `task`.

- Present ⇒ orchestrator — proceed.
- Absent ⇒ sub-agent — do NOT execute any instruction below. Return `BLOCKED` with `ORCHESTRATOR_ONLY_SKILL_CARD` (cards) or `ORCHESTRATOR_ONLY_PLAN` (plans) and halt.

---

## Phase Table

| Phase | Name | Concern | SCs | Depends On | Item Range | Dispatch |
|-------|------|---------|-----|------------|------------|----------|
| 1 | Foundation | Seed data clean + ꝏ normalization (with ∞ fallback pin) | SC-9, SC-1, SC-10 | — | items 1-2 | task-card + direct (commit) |
| 2 | Scan service | Read-only ∞ defect scan with fixture coverage | SC-2 | 1 | item 4 | task-card + direct (commit) |
| 3 | Remediation write path | Per-record + batch remediation with EditHistory audit; review/identity/FTS proof items | SC-5, SC-6, SC-7, SC-8 | 2 | items 5-8 | task-card + direct (commit) |
| 4 | Admin UI | Sidebar exposure + scan-count/apply-all/review flow | SC-3, SC-4 | 2, 3 | items 9-10 | task-card + direct (commit) |
| 5 | Suite-health gate + completion | Full-suite regression gate + post-implementation pipeline | SC-1..SC-10 | 1, 2, 3, 4 | item 11 | task-card + direct (z3-check) |

---

## Pre-Implementation

- [ ] 1. **Coherence gate (direct).** Re-read `.issues/1382/spec.md` and `.issues/1382/artifacts/structure.yaml`; confirm 10 SCs map to phases with no structural drift (phase-1: SC-9/SC-1/SC-10; phase-2: SC-2; phase-3: SC-5/SC-6/SC-7/SC-8; phase-4: SC-3/SC-4; phase-5: all) before any implementation. **→ all SCs**
- [ ] 2. **Baseline check (direct).** Verify working tree is on the issue feature branch, trunk tip aligned (per git-workflow pre-work); record baseline evidence under `tmp/issue-1382/artifacts/`. **→ all SCs**
- [ ] 3. **Pre-regression (task-card).** Run regression test patterns before the RED phase per test-driven-development phase-0 task: `task(..., prompt: "execute phase-0 task from test-driven-development")`. Regression Test Protocol (AGENTS.md): run `bash scripts/sync_prod_to_local.sh` first — the sync script from the feature branch under test. Clean `tmp/issue-1382/artifacts/pipeline-pre-regression-*` first. **→ all SCs**
- [ ] 4. **Pre-regression verify (task-card).** Verify pre-regression results per verification-before-completion: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-pre-regression-verify-*` first. **→ all SCs**

---

## Admonishments

> **Compliance:** All SCs must pass before completion. Partial implementation is not permitted. Each item is daisy-chained — item N's commit is precondition for item N+1's RED.

> **One step at a time.** Execute exactly one step. Report progress. Wait for instruction before the next step.

> **Step status:** Report `[item N] [PASS|FAIL]` after each step. If FAIL, report blocker and halt.

> **Self-Remediation Protocol:** If a step FAILs: diagnose root cause, fix the deliverable, re-verify. If the fix requires spec revision, update the spec and re-enter the plan. Escalate only after remediation failure.

> **Enforcement gate:** All SCs (SC-1 through SC-10) must pass before this plan is complete. Behavioral SCs demand behavioral evidence — prose or structural substitutes are EVIDENCE_TYPE_MISMATCH (FAIL).

> **Data integrity:** No synthetic linguistic data. All test fixtures use real characters ∞ (U+221E) and ꝏ (U+A74F) as direct Unicode literals. No ASCII regex on linguistic data. No `to_tsvector('english')`. No automatic production mutation — remediation is admin-triggered only.

---

### Phase 1 — Foundation

**Concern:** Clean the seed fixture data and extend normalization so both oo-ligature encodings map to `oozzz` — the substrate every later phase builds on.

**Code Path Coverage:** `src/seed_data/natick_sample_100*.txt` (byte substitution) and `src/services/linguistic_service.py` `generate_sort_lx()` `symbol_map` (additive dict entry + comment). No consumer of `generate_sort_lx()` is modified.

**Cross-Cutting SCs:** SC-1 and SC-10 co-locate in item 2 (the pin and the addition target the same function); SC-9 is independent data cleanup.

**Interface Boundaries:** `symbol_map` is internal to `generate_sort_lx()`; the addition must not alter any existing key's mapping. All existing callers (populate_search_entries, search normalization, reprocessing) see identical behavior for existing inputs.

**State Transitions:** Seed files: 364 U+221E → 0 U+221E, 364 U+A74F per file. Normalization: ꝏ input falls through to bare lowercase → now maps to `oozzz`; ∞ mapping unchanged.

**Steps:**

- [ ] 5. **RED (task-card).** Write the seed-evidence check: a test asserting 0 U+221E occurrences in both seed files (reads files, counts `\u221e`) — fails now (364 found per file). Place in `test/test_infinity_remediation_red.py` (new file, pgserver fixture setUpClass per `test/test_upload_search_entries.py` pattern even though this item needs no DB — later items share the fixture). **→ SC-9** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-red-*` first.
- [ ] 6. **GREEN (task-card).** Replace every ∞ (U+221E) with ꝏ (U+A74F) in both seed files via a `./tmp/` transform script (`uv run python`); verify counts (0 U+221E, 364 U+A74F per file), UTF-8 intact, file diffs show only the intended byte substitutions. Seed test passes. **→ SC-9** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 7. **Post-regression (task-card).** Run regression test patterns after GREEN per test-driven-development phase-4 task: `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-post-regression-*` first. **→ SC-9**
- [ ] 8. **Verify (task-card).** Verify per verification-before-completion: seed-file counts asserted by the committed test; full new test file run; `git status` shows only the two seed files + new test file staged. **→ SC-9** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 9. **Commit (direct).** `git add src/seed_data/ test/test_infinity_remediation_red.py && git commit -m "fix(1382): replace ∞ (U+221E) with ꝏ (U+A74F) in seed data"`. Test + change committed as one atomic slice. **→ SC-9**
- [ ] 10. **RED (task-card).** Add `TestGenerateSortLxLigature` assertions to the test file: `generate_sort_lx("k∞") == "koozzz"` (regression pin, SC-10 behavioral half) and `generate_sort_lx("kꝏ") == "koozzz"` (SC-1, fails — ꝏ currently falls through). Run the file: pin passes, ꝏ assertion fails. **→ SC-1, SC-10** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`.
- [ ] 11. **GREEN (task-card).** Add `"\ua74f": "oozzz"` to `symbol_map` in `generate_sort_lx()`; update the adjacent comment to document both ∞ and ꝏ as Algonquian oo-ligature forms mapping to `oozzz`. Re-run: both assertions pass. **→ SC-1, SC-10** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 12. **Post-regression (task-card).** Run regression patterns after GREEN (full suite — symbol_map is consumed by search/reprocessing paths): `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-post-regression-*` first. **→ SC-1, SC-10**
- [ ] 13. **Verify (task-card).** Verify: both unit assertions pass; string evidence — `"\u221e": "oozzz"` entry present in source (SC-10 string half); ruff/pyright clean on modified files. **→ SC-1, SC-10** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 14. **Commit (direct).** `git add src/services/linguistic_service.py test/test_infinity_remediation_red.py && git commit -m "feat(1382): map ꝏ (U+A74F) to oozzz in generate_sort_lx, pin ∞ fallback"`. **→ SC-1, SC-10**

**Cost frame:** Verifying the normalization change via the full suite costs minutes — `generate_sort_lx()` is consumed by search indexing and reprocessing, so a wrong edit breaks search invisibly at suite level. Skipping costs silent search corruption for every future upload — discovered only when a linguist's query misses a real headword.

**Phase 1 completion (VbC assertions):**
- [ ] Seed files: 0 U+221E, 364 U+A74F each; UTF-8 intact.
- [ ] `generate_sort_lx("kꝏ") == "koozzz"` and `generate_sort_lx("k∞") == "koozzz"` both pass; source retains the ∞ mapping.
- [ ] `git status` clean; no files outside the declared set modified.

**Concern transition:** Leaving foundation → entering scan service. Phase 2 queries records through the now-correct normalization substrate (ꝏ-bearing clean records must not be mis-scanned).

---

### Phase 2 — Scan service

**Concern:** Read-only defect scan — count and list exactly the non-deleted records carrying ∞ in `lx` or `mdf_data`.

**Code Path Coverage:** `src/services/linguistic_service.py` — two new static methods, session-injectable per `populate_search_entries` signature convention. No UI, no writes.

**Cross-Cutting SCs:** SC-2 is the sole gate; its fixture (seeded User/Source/Records incl. soft-deleted defective record) is reused by every Phase 3 item.

**Interface Boundaries:** `count_infinity_records(session=None) -> int`; `list_infinity_records(session=None) -> list[dict]` with `{id, lx, preview}` — preview is a context window of `mdf_data` around the first ∞ match. Direct Unicode literal in the query — no ASCII regex (lessons-learned mandate).

**State Transitions:** DB unchanged (read-only). Fixture state: 4 seeded records → scan reports exactly 2 defective (A: ∞ in lx+mdf_data; B: ∞ in mdf_data only), excluding clean C and soft-deleted defective D.

**Steps:**

- [ ] 15. **RED (task-card).** Extend the pgserver fixture: seed User (test@example.com), Source, and Records A (∞ in lx+mdf_data), B (∞ in mdf_data only), C (clean), D (defective, `is_deleted=True`). Assert `count_infinity_records() == 2`; `list_infinity_records()` returns ids [A, B] with non-empty previews. Fails — methods absent. **→ SC-2** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-red-*` first.
- [ ] 16. **GREEN (task-card).** Implement both methods: filter `is_deleted == False`, match U+221E in `lx` OR `mdf_data` (direct Unicode literal, no ASCII regex); preview = bounded window around first match. Re-run: assertions pass. **→ SC-2** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 17. **Post-regression (task-card).** Run regression patterns after GREEN: `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-post-regression-*` first. **→ SC-2**
- [ ] 18. **Verify (task-card).** Verify: fixture assertions pass; soft-deleted exclusion confirmed; ruff/pyright clean; no write path introduced (read-only methods — session never commits mutations). **→ SC-2** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 19. **Commit (direct).** `git add src/services/linguistic_service.py test/test_infinity_remediation_red.py && git commit -m "feat(1382): add ∞ defect scan service (count/list, soft-delete excluded)"`. **→ SC-2**

**Cost frame:** Verifying scan precision via the 4-record fixture costs seconds and catches the two costly error classes — over-match (remediating clean records: data corruption) and under-match (missing defective records: the defect persists invisibly). Skipping costs a miscount displayed to the admin on every tool open, eroding trust in the whole feature.

**Phase 2 completion (VbC assertions):**
- [ ] Scan count/list matches fixture truth exactly; soft-deleted defective record excluded.
- [ ] `git status` clean.

**Concern transition:** Leaving scan service → entering remediation write path. Phase 3 iterates exactly the records the scan returns.

---

### Phase 3 — Remediation write path

**Concern:** Per-record and batch remediation with full audit trail, then the three proof items (review semantics, normalized-identity, FTS equivalence) as separate assertion items.

**Code Path Coverage:** `src/services/linguistic_service.py` — `remediate_record(record_id, user_email, session_id, session=None) -> bool` and `remediate_all_records(user_email, progress_callback=None, session=None) -> dict`. Reuses `UploadService.populate_search_entries([rid], session=session)` unmodified for search-entry/FTS rebuild. No new `to_tsvector` calls.

**Cross-Cutting SCs:** SC-5 is the write-path gate; SC-6/SC-7/SC-8 are proof assertions against that path's semantics, each its own item and commit. SC-7/SC-8 encode the spec's protected invariants (normalized stability, FTS equivalence) enforced again at gate level via the dependency contract.

**Interface Boundaries:** Locked records: log warning, return False, counted as `skipped` in batch (mirrors `update_record()` guard). Missing/clean/soft-deleted record: return False without mutation. Success: exactly one `EditHistory` row (prev_data snapshot before mutation, current_data after, version = current+1, session_id = batch uuid4, fixed change_summary). Batch returns `{total, remediated, skipped}`.

**State Transitions:** Record: defective → remediated (lx/mdf_data carry ꝏ; sort_lx recomputed; search entries + fts_vector rebuilt). Normalized columns: byte-identical pre/post (∞ and ꝏ both → oozzz). `edit_history`: +1 row per remediated record. B (skipped): unchanged, no history row.

**Steps:**

- [ ] 20. **RED (task-card).** Assert against the fixture: `remediate_record(A.id, "test@example.com", session_id)` → True; `lx`/`mdf_data` contain ꝏ not ∞; exactly 1 new `EditHistory` row for A with correct prev/current snapshots and `version == A.current_version + 1`; A's search_entries/headword/gloss terms remediated. Fails — method absent. **→ SC-5** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-red-*` first.
- [ ] 21. **GREEN (task-card).** Implement `remediate_record`: load record; bail False if missing/`is_deleted`/no ∞/locked (log warning); snapshot `prev_data`; replace ∞→ꝏ in `lx` and `mdf_data`; `record.sort_lx = generate_sort_lx(record.lx)`; add `EditHistory(...)`; call `UploadService.populate_search_entries([record_id], session=session)`; commit; return True. Implement `remediate_all_records`: iterate `list_infinity_records()`, shared `uuid4` session_id, per-record remediation, progress_callback per item, return `{total, remediated, skipped}`. Re-run: assertions pass. **→ SC-5** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 22. **Post-regression (task-card).** Run regression patterns after GREEN (full suite — write path touches records, search entries, edit history): `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-post-regression-*` first. **→ SC-5**
- [ ] 23. **Verify (task-card).** Verify: apply-all on the fixture remediates every detected record; one history row each with correct snapshots; batch dict counts correct; locked-record skip path covered. **→ SC-5** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 24. **Commit (direct).** `git add src/services/linguistic_service.py test/test_infinity_remediation_red.py && git commit -m "feat(1382): add remediate_record/remediate_all_records with EditHistory audit"`. **→ SC-5**
- [ ] 25. **RED→GREEN (task-card).** Review semantics: remediate A via `remediate_record`, do not touch B; assert A clean + history row, B still carries ∞ + no history row for B. **→ SC-6** — dispatch red then green per test-driven-development as needed (skip is the absence of the call — the assertion set is the deliverable); post-regression + verify follow the same task-card chain; commit: `git commit -m "test(1382): review semantics — remediate A/skip B assertions"`. Clean `tmp/issue-1382/artifacts/pipeline-*` per step first.
- [ ] 26. **RED→GREEN (task-card).** Normalized-identity: capture A's `sort_lx` and all `normalized_term` values pre-remediation; remediate; assert byte-identical post. **→ SC-7** — same chain; commit: `git commit -m "test(1382): normalized-identity — sort_lx/normalized_term stable across remediation"`.
- [ ] 27. **RED→GREEN (task-card).** FTS equivalence: pre-remediation, query `fts_entries` with `to_tsvector('simple', generate_sort_lx("k∞"))`, record result ids; remediate; post-remediation query with `to_tsvector('simple', generate_sort_lx("kꝏ"))`; assert identical result set. **→ SC-8** — same chain; commit: `git commit -m "test(1382): FTS equivalence — ꝏ query matches ∞ results"`.

**Cost frame:** Verifying the write path per-item costs minutes of pgserver fixture time. Skipping costs the two catastrophic failure modes — a history-less mutation (unauditable data change, violating the data-integrity mandate) and a normalized-column drift (breaks search sort order silently for every future query). The proof items exist because these invariants are the spec's entire reason for the interactive design.

**Phase 3 completion (VbC assertions):**
- [ ] Apply-all fixture run: every detected record remediated; one EditHistory row each; snapshots correct.
- [ ] Review semantics: A clean+history, B unchanged+no history.
- [ ] Normalized columns byte-identical pre/post; FTS result sets identical.
- [ ] `git status` clean; `upload_service.py` unmodified.

**Concern transition:** Leaving the write path → entering the admin UI. Phase 4 wires buttons to the completed, proven service surface.

---

### Phase 4 — Admin UI

**Concern:** Expose the tool in Table Maintenance and implement the scan-count → apply-all/review flow with confirm gating and per-record Apply/Skip.

**Code Path Coverage:** `src/frontend/pages/table_maintenance.py` — one radio option in `main()`'s sidebar list, one `elif` dispatch, one new `render_infinity_remediation()` function; `test/ui/test_table_maintenance_infinity.py` (new, StreamlitAppTest pattern from `test/ui/test_records_*.py`).

**Cross-Cutting SCs:** SC-3 (admin-only exposure) and SC-4 (count-before-action flow) land in this phase as two items.

**Interface Boundaries:** Consumes `count_infinity_records`, `list_infinity_records`, `remediate_record`, `remediate_all_records`. Admin guard inherited from `main()` — no new auth logic. `user_email` from `st.session_state` per existing admin-page convention. Errors via `handle_ui_error(..., logger_name="snea.pages.table_maintenance")`. Progress via the `render_data_reprocessing_maintenance()` pattern (progress bar + status container).

**State Transitions:** UI states: zero-state (count 0 → info only, no buttons) → detected-state (count N + Apply All + Review One-by-One) → review-state (record i of N, Apply/Skip) → apply-all-state (progress bar). No DB mutation until a button is clicked.

**Steps:**

- [ ] 28. **RED (task-card).** UI test (new `test/ui/test_table_maintenance_infinity.py`): admin session (`user_role="admin"` in session_state) → sidebar radio includes "∞→ꝏ Remediation"; non-admin session → page blocked by the existing guard. Fails — option absent. **→ SC-3** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-red-*` first.
- [ ] 29. **GREEN (task-card).** Add `"∞→ꝏ Remediation"` to the radio options list in `main()`; add the `elif` dispatch to `render_infinity_remediation()`. Re-run: exposure test passes. **→ SC-3** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 30. **Post-regression (task-card).** Run regression patterns after GREEN: `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-post-regression-*` first. **→ SC-3**
- [ ] 31. **Verify (task-card).** Verify: admin sees the option; non-admin blocked; existing three options unaffected. **→ SC-3** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 32. **Commit (direct).** `git add src/frontend/pages/table_maintenance.py test/ui/test_table_maintenance_infinity.py && git commit -m "feat(1382): expose ∞→ꝏ remediation in Table Maintenance (admin-only)"`. **→ SC-3**
- [ ] 33. **RED (task-card).** UI flow test: with N defective fixture records, the view displays the count and applies nothing until a button is clicked; zero-state (0 defective) shows info, no action buttons; Apply All requires confirm; Review shows record i of N with Apply/Skip. Fails — view incomplete. **→ SC-4** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`.
- [ ] 34. **GREEN (task-card).** Implement `render_infinity_remediation()`: header + explanation; scan on render (count via `count_infinity_records()`); Rescan button; zero-state info; Apply All behind confirm checkbox with progress (pattern from `render_data_reprocessing_maintenance()`); Review One-by-One listing `list_infinity_records()` with before/after preview (after = same text with ∞→ꝏ applied for display), per-record Apply (`remediate_record` with fresh uuid session_id) / Skip advance, "i of N" counter; `handle_ui_error` wrapping. Re-run: flow test passes. **→ SC-4** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 35. **Post-regression (task-card).** Run regression patterns after GREEN: `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-post-regression-*` first. **→ SC-4**
- [ ] 36. **Verify (task-card).** Verify: count-before-action behavior; zero-state; confirm-gate on Apply All; per-record Apply/Skip; no mutation without click. **→ SC-4** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 37. **Commit (direct).** `git add src/frontend/pages/table_maintenance.py test/ui/test_table_maintenance_infinity.py && git commit -m "feat(1382): scan-count display, confirm-gated apply-all, review one-by-one flow"`. **→ SC-4**

**Cost frame:** Verifying the UI flow costs minutes of StreamlitAppTest runtime. Skipping costs the defect class this spec exists to prevent — an unconfirmed bulk mutation or a count display that lies about what will change. The confirm gate and scan-first display are the stakeholder-facing safety properties; a broken render discovered post-merge burns stakeholder trust in the tool.

**Phase 4 completion (VbC assertions):**
- [ ] Admin-only exposure verified; non-admin blocked.
- [ ] Count display precedes any action; zero-state informational; Apply All confirm-gated; per-record Apply/Skip works.
- [ ] `git status` clean.

**Concern transition:** Leaving the admin UI → entering the suite-health gate and post-implementation pipeline. All 10 SCs' code and tests are committed; the gate proves them at suite level.

---

### Phase 5 — Suite-health gate + completion

**Concern:** Prove the full suite green after DB re-sync per the Regression Test Protocol and run the post-implementation pipeline (audit → z3-check → structural checks → pre-PR gate → regression check → review-prep → PR → completion summary).

**Code Path Coverage:** No new code — verification-only plus pipeline gates. File coverage re-asserted: the 4 modified/added files plus 2 new test files; nothing outside the declared set.

**Cross-Cutting SCs:** The gate aggregates all 10 SCs at suite level, plus the dependency contract's invariants (normalized_columns_stable, simple_tsconfig_only, no_auto_migration).

**Interface Boundaries:** PR creation requires `for_pr` authorization scope — the plan halts before review-prep if implementation authorization did not extend to PR. Human-only merge applies.

**State Transitions:** Intermediate suite states converge to the final contract: full suite green, all per-SC evidence artifacts recorded under `tmp/issue-1382/artifacts/`, tests-run.yaml recorded. DB re-synced immediately before the gate.

**Steps:**

- [ ] 38. **RED — gate precondition (task-card).** Run `bash scripts/sync_prod_to_local.sh` (Regression Test Protocol — sync script from the feature branch under test) then the full-suite `uv run pytest test/` pre-gate; assert the target is unmet while implementation is incomplete OR record the passing state if all items landed — either way the run is recorded as the gate baseline. **→ all SCs** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-red-*` first.
- [ ] 39. **GREEN — full-suite gate (task-card).** Full-suite `uv run pytest test/` after DB re-sync; assert all tests pass (existing suite + new infinity remediation tests); record tests-run.yaml per the tests-run mandate (`tests_run > 0`, `all_passed == true`, enumerated tests + exit codes). **→ all SCs** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 40. **Verify — suite gate (task-card).** Verify per verification-before-completion: full-suite exit code 0, per-SC evidence artifacts present (SC-1..SC-10), behavioral evidence for behavioral SCs (no structural substitutes). **→ all SCs** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-verify-*` first.
- [ ] 41. **Audit (task-card).** Adversarial audit of the deliverable: `task(..., prompt: "execute verification-audit DiMo investigator from audit. Read 'audit/tasks/verification-audit-investigator.md' first")` — followed by validator, evaluator, arbiter in sequence. Clean `tmp/issue-1382/artifacts/pipeline-audit-*` first. **→ all SCs**
- [ ] 42. **Z3 check (direct).** Run `./.opencode/tools/solve check --state-path .issues/1382/artifacts/state.yaml --contract-path .issues/1382/dependency-contract.yaml` directly (no sub-agent dispatch). Clean `tmp/issue-1382/artifacts/pipeline-z3-check-*` first. **→ all SCs**
- [ ] 43. **Structural checks (task-card).** Run the finishing checklist (lint, typecheck, branch readiness): `task(..., prompt: "execute checklist task from finishing-a-development-branch")`. Clean `tmp/issue-1382/artifacts/pipeline-structural-checks-*` first. **→ all SCs**
- [ ] 44. **Pre-PR gate (task-card).** Verify all SC verdicts — BLOCK if any FAIL: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1382/artifacts/pipeline-pre-pr-gate-*` first. **→ all SCs**
- [ ] 45. **Regression check (task-card).** Final regression check before PR: `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1382/artifacts/pipeline-regression-check-*` first. **→ all SCs**
- [ ] 46. **Review-prep (task-card).** Prepare PR review context: `task(..., prompt: "execute review-prep from git-workflow-pr. Read 'git-workflow-pr/tasks/review-prep.md' first")`. **→ all SCs**
- [ ] 47. **Create PR (task-card).** Create the pull request (stacked strategy — one branch, N commits, one PR): `task(..., prompt: "execute create task from git-workflow-pr")`. Human-only merge — the agent does not merge. **→ all SCs**
- [ ] 48. **Completion summary (task-card).** Generate the completion executive summary: `task(..., prompt: "execute completion task from completion-core")`. **→ all SCs**

**Cost frame:** Verifying the full-suite gate costs minutes of execution time plus a DB re-sync. Skipping costs an unverifiable completion claim — the AGENTS.md tests-run mandate makes behavioral evidence with `tests_run > 0` and `all_passed == true` a hard gate; a suite claimed green without the recorded artifact is a fabricated pass.

**Phase 5 completion (VbC assertions):**
- [ ] Full-suite run: all tests pass; DB pre-synced via `bash scripts/sync_prod_to_local.sh`; tests-run.yaml recorded.
- [ ] Audit, z3-check, structural checks, pre-PR gate, regression check, review-prep, PR creation, completion summary — all gates PASS.
- [ ] `git status` clean; files outside the declared set untouched.

**Concern transition:** Leaving the suite-health gate and post-implementation pipeline — all 10 SCs covered, phase DAG complete with no cycles. Plan execution ends here; human-only merge applies.

---

## Exit Criteria

- [ ] C1. SC-1 passes: `generate_sort_lx("kꝏ") == "koozzz"` (unit assertion, committed).
- [ ] C2. SC-2 passes: scan count/list matches fixture truth exactly; soft-deleted defective record excluded.
- [ ] C3. SC-3 passes: sidebar option visible to admin, blocked for non-admin (StreamlitAppTest).
- [ ] C4. SC-4 passes: count display before action; zero-state informational; no mutation until button click.
- [ ] C5. SC-5 passes: apply-all remediates every detected record; exactly one EditHistory row each with correct snapshots and version.
- [ ] C6. SC-6 passes: remediate A / skip B leaves A clean+history, B unchanged+no history.
- [ ] C7. SC-7 passes: sort_lx and normalized_term byte-identical pre/post remediation.
- [ ] C8. SC-8 passes: FTS ꝏ post-remediation result set identical to ∞ pre-remediation result set.
- [ ] C9. SC-9 passes: both seed files contain 0 U+221E and 364 U+A74F.
- [ ] C10. SC-10 passes: ∞ → oozzz mapping present in symbol_map source; ∞ unit pin passes.
- [ ] C11. Post-implementation pipeline gates all pass (audit, z3-check, structural checks, pre-PR gate, regression check) and the PR is created for the stacked branch.

---

## lifecycle_events

- timestamp: 2026-09-29T22:40:00Z
  event: plan_created
  plan_path: .issues/1382/plan.md
  phase_count: 5

---

<!-- Pre-Flight Guard section above is canonical per plan-artifact-format §3.5 — reason code ORCHESTRATOR_ONLY_PLAN -->
<!-- Plan rebuilt in house format per developer defect report: full pre-regression + per-item red/green/post-regression/verify/commit chains as checkbox lists, phase table, admonishments, cost frames, VbC assertions, exit criteria -->

🤖 Co-authored with AI: OpenCode (ollama-cloud/glm-5.3)