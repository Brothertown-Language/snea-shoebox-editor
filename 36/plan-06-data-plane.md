# Phase 6 — Data plane — upload inline embedding + admin backfill UI

**Concern:** Embed new primary `ge` rows inline inside `populate_search_entries()` (signature unchanged) inside the upload pipeline, and add the admin-role Embedding Backfill button as a sibling section in Table Maintenance → Data Reprocessing — the sole authorized Streamlit surface in this spec (R-8, R-9, R-11, SC-8, SC-9, CG-4).

**Files:**
- `src/services/upload_service.py`
- `test/test_upload_search_entries.py`
- `src/frontend/pages/table_maintenance.py`

**SCs:** SC-8 (behavioral), SC-9 (behavioral)

**Dependencies:** Phases 2, 3, 4, 5 — the upload path needs encode (Phase 2) + columns (Phase 3); the admin UI needs the backfill recompute semantics proven by Phase 5's exclusion behavior. RED/GREEN/COMMIT for both SCs inside this phase.

**Entry Conditions:**
- Phases 2-5 committed and VbC consolidated
- Playwright tooling available for the SC-9 click-through

**Exit Conditions:**
- `populate_search_entries(record_ids, session=None) → int` (signature unchanged) embeds new primary ge rows inline during ingestion — pin-stamped embedding_model, batch ≤512, exact Unicode preservation, contextual failure with no silent skip
- Admin-role Embedding Backfill button present beside `render_data_reprocessing_maintenance()`, reusing the role gate, with `st.progress` + progress callback + `st.status`, handle_ui_error surfacing, and model-change recompute
- Non-admin role rejected; Playwright click-through green on the synced DB
- Commits per item

**Code Path Coverage:** P4 (UploadService.ingest → populate_search_entries(record_ids, session=None) → ge rows parsed → embed inline (batch ≤512) → upsert with embedding_model = pin), P5 (Table Maintenance main() role gate → render_data_reprocessing_maintenance() sibling section → Embedding Backfill button → backfill service method with st.progress + progress callback + st.status → handle_ui_error on exception)

**Cross-Cutting SCs:** SC-8 spans ingestion pipeline + embedding correctness + Unicode integrity (Algonquian-context Unicode preservation per the AGENTS.md linguistic data constraints). SC-9 spans admin UI + long-running batch + auth role gate — isolated from the #1347 sibling section; the only authorized st.* surface in this spec.

**Interface Boundaries:** populate_search_entries — PRESERVE_SIGNATURE: `populate_search_entries(record_ids: list[int], session=None) → int`; internals gain inline ge embedding (batch ≤512, pin stamp, Unicode exact). Consumers: UploadService ingestion pipeline, the existing test module, admin full-reprocessing path. Row embedding via `embedding_service.encode` (1-5 ge strings/record, measured 10-60 ms/record reference).

**State Transitions:** Search entry row — no_embedding → embedded_current_pin (upload-path inline embed OR admin backfill run; guard: batch ≤512, embedding_model stamped to pin, Unicode exact, fail-fast on embed error); embedded_stale_pin → embedded_current_pin (admin backfill re-embed after a model pin change — model-change recompute). Admin backfill run — idle → running (admin-role button click; non-admin rejected by the reused role gate) → complete (completion results surfaced) or failed (exception → handle_ui_error surfacing; stale rows remain excluded at query). Invariant: stale rows remain excluded at query until re-embedded.

**Cost frame:** Running the extended upload test and the Playwright click-through costs minutes. Skipping means silently unsearchable new records — a data-integrity defect discovered only by the absence of results — and a broken admin tool discovered during the first real backfill attempt under operational pressure.

---

- [ ] 55. **pre-cleanup + R-12 re-sync + RED — Item 8 (**direct**, then **task-card**).** Clean Item 8 artifacts, re-sync the DB, then dispatch the red task extending the existing upload test.
  - Sub-bullet: `rm -f ./tmp/issue-36/artifacts/pipeline-red-*` then `bash scripts/sync_prod_to_local.sh` (from the branch under test)
  - Sub-bullet: dispatch — `task(..., prompt: "execute red task from test-driven-development")`
  - Sub-bullet: RED describes what fails — the extended `test_upload_search_entries.py` assertions find no embeddings produced, no pin-stamped embedding_model, or Unicode drift on real synced records
  - Sub-bullet: SC reference — SC-8 (behavioral: extended existing test with real synced records)
- [ ] 56. **GREEN — Item 8 (**task-card**).** Dispatch the green task: extend `populate_search_entries()` internals in `src/services/upload_service.py` so new primary ge rows embed inline during ingestion — signature unchanged, embedding_model stamped with the pin, DB write batches ≤512 (R-11; PostgreSQL parameter cap safe), Unicode preserved exactly, every embed failure raising contextually with no silent skip.
  - Sub-bullet: dispatch — `task(..., prompt: "execute green task from test-driven-development")`
  - Sub-bullet: only the minimum internal change; MDF parser and ingestion format untouched
  - Sub-bullet: SC reference — SC-8
- [ ] 57. **post-regression + verify — Item 8 (**task-card**).** Dispatch the phase-4 regression task and the verify task: the extended test on real synced records asserts embeddings present, pin stamp, Unicode fidelity, and batch ≤512.
  - Sub-bullet: regression dispatch — `task(..., prompt: "execute phase-4 task from test-driven-development")`; verify dispatch — `task(..., prompt: "execute verify task from verification-before-completion")`; pre-clean both artifact sets
  - Sub-bullet: SC reference — SC-8
- [ ] 58. **commit-inline — Item 8 (**direct**).** Commit the Item 8 test extension and upload service change as one atomic slice.
  - Sub-bullet: `git add src/services/upload_service.py test/test_upload_search_entries.py && git commit -m "issue#36: inline embedding of new ge rows in populate_search_entries (SC-8)"`
  - Sub-bullet: no co-author trailers during implementation commits
- [ ] 59. **pre-cleanup + R-12 re-sync + RED — Item 9 (**direct**, then **task-card**).** Clean Item 9 artifacts, re-sync the DB, then dispatch the red task for the admin backfill UI.
  - Sub-bullet: `rm -f ./tmp/issue-36/artifacts/pipeline-red-*` then `bash scripts/sync_prod_to_local.sh`
  - Sub-bullet: dispatch — `task(..., prompt: "execute red task from test-driven-development")`
  - Sub-bullet: RED describes what fails — the Playwright assertion finds no backfill control in Table Maintenance → Data Reprocessing (or it appears for non-admin roles)
  - Sub-bullet: SC reference — SC-9 (behavioral: Playwright click-through on the synced DB)
- [ ] 60. **GREEN — Item 9 (**task-card**).** Dispatch the green task: add the sibling backfill section beside `render_data_reprocessing_maintenance()` in `src/frontend/pages/table_maintenance.py` with the reused role gate, the backfill service method using the `st.progress` + progress callback + `st.status` idiom, handle_ui_error surfacing, and model-change recompute (a pin change re-embeds stale rows).
  - Sub-bullet: dispatch — `task(..., prompt: "execute green task from test-driven-development")`
  - Sub-bullet: this section is the ONLY authorized st.* surface in the spec; isolated from the #1347 sibling section; rate reference 6,266 terms/72.2 s
  - Sub-bullet: SC reference — SC-9
- [ ] 61. **post-regression + verify — Item 9 (**task-card**).** Dispatch the phase-4 regression task and the verify task: Playwright click-through on the synced DB confirms the role-gated button, st.progress reporting, callback progress, st.status completion results, and handle_ui_error surfacing; non-admin rejection verified.
  - Sub-bullet: regression dispatch — `task(..., prompt: "execute phase-4 task from test-driven-development")`; verify dispatch — `task(..., prompt: "execute verify task from verification-before-completion")`; pre-clean both artifact sets
  - Sub-bullet: SC reference — SC-9
- [ ] 62. **commit-inline — Item 9 (**direct**).** Commit the Item 9 test and table_maintenance/backfill changes as one atomic slice.
  - Sub-bullet: `git add src/frontend/pages/table_maintenance.py <test file> && git commit -m "issue#36: admin Embedding Backfill button with progress reporting (SC-9)"`
  - Sub-bullet: no co-author trailers during implementation commits
- [ ] 63. **Phase regression sweep (**task-card**).** Dispatch the phase-4 regression task once more after the Item 9 commit to confirm SC-8 and SC-9 suites pass together.
  - Sub-bullet: dispatch — `task(..., prompt: "execute phase-4 task from test-driven-development")`; pre-clean: `rm -f ./tmp/issue-36/artifacts/pipeline-post-regression-*`
- [ ] 64. **Phase VbC consolidation (**direct**).** Confirm the SC-8 extended-test evidence and SC-9 Playwright evidence are both recorded PASS before the post-implementation steps begin.
  - Sub-bullet: any missing evidence artifact re-runs its verify dispatch before proceeding

#### Phase 6 VbC

- Upload path: real synced records show inline pin-stamped embeddings, batch ≤512, exact Unicode, contextual failures — SC-8 behavioral evidence recorded PASS.
- Admin backfill: role-gated click-through green with progress reporting, completion results, error surfacing, non-admin rejection — SC-9 behavioral evidence recorded PASS.
- UI boundary honored: the backfill section is the only st.* code added in this spec's scope; no mode radios, threshold widgets, or result rendering added (#1385 owns those).

**Concern transition:** Leaving the data plane → entering post-implementation verification, audit, review-prep, and PR creation (plan index post-implementation steps, step range 65-72).