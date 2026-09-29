---
remote_issue: 1387
remote_url: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1387
promoted_at: 2026-09-29T15:32:58+00:00
---

# [SPEC] Algonquian term-space semantic search — end-user interface (records page modes, threshold, scores, pagination, empty states)

> **Full spec and artifacts: [`https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1387/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1387/)** — this issue is a condensed exec summary; the authoritative spec lives in the `issues-data` branch.
>
> **Local artifacts:** `.issues/1387/` — analytical artifacts, sc-summary, plan, audit findings

## Intent and Executive Summary

**Problem Statement:** Vernacular term-space semantic search has a backend spec (#1386) but no end-user surface: the records-page mode radio exposes only Headword/Gloss/Lexeme/FTS, there is no term-space similarity-threshold control, no per-term score display, and no handling for the term-space seam's degraded-state payloads.

**Root Cause / Motivation:** #1385's UI spec is scoped to the gloss-space seam (`search_semantic`/`SemanticSearchResult`) and cannot carry term-space modes: #1386 explicitly rejected widening the SearchMode Literal, and term rows carry metadata gloss rows do not (entry_type, language_code, source, term). Without this spec, `search_terms` becomes reachable with no way for linguists to invoke it — vernacular variant spellings (the cross-source-comparison scenario) remain invisible to end users.

**Approach Chosen:** Extend the records page additively — two new mode entries ("Semantic Term", "Semantic Phrase") in the existing mode radio, one shared per-user threshold control persisted through the existing PreferenceService, dispatch through a seam-only binding (no SearchMode widening, no `search_records` routing), client-side entry_type filtering by the selected mode, similarity scores on term rows with per-row metadata, rank-once pagination slicing, and status-keyed empty states.

**Alternatives Considered & Why Discarded:**
- *Widening SearchMode so term modes route through `search_records`* — rejected: #1386 explicitly rejected widening; `search_records` raises ValueError on unknown modes and its result shape carries no per-row term metadata.
- *Dedicated term-search page* — rejected: fragments the search UX; the existing page already owns filters, pagination, rendering, and role plumbing, so a second page would duplicate all of it.
- *Per-mode threshold keys (one preference per term mode)* — rejected: two nearly identical controls with distinct stored values create tuning confusion; one shared value keeps retrieval-precision preference uniform until calibration floors (REQ-U3 resolution).

**Key Design Decisions:**
- UI binds to #1386's `search_terms`/`TermSearchResult` v1 contract and nothing below it — seam import lazy/guarded with a contract-shaped fixture for verification until #1386 lands (tradeoff: pre-implementation verification uses mocks rather than the live service; layered correctness and mockable dispatch win).
- Threshold is a per-user preference (`records`/`term_threshold`, provisional default `0.80` pending the #1386 SC-6 calibration floors), shared across both term modes — tradeoff: mode-specific precision tuning is deferred, but the control set and stored-value behavior stay uniform while calibration is pending.
- Entry-type targeting is client-side filtering on the seam's per-row `entry_type` field, one seam invocation per query (tradeoff: rows of the other entry type are fetched but not displayed; keeps the v1 seam signature unchanged and rank-once preserved).
- Pagination is pure slicing of the seam's full ranked list (rank-once) — page navigation can never reorder results.
- Per-row metadata display (term, entry_type, language_code, source) on term rows only — tradeoff: a second rendering branch, but exact-match and gloss modes keep their unchanged layout.

**User Intent / Original Prompt:** Stakeholder request (2026-09-29): the term-space split has a backend spec (#1386) but no end-user UI spec; #1385's interface covers gloss-space only. Remote stub filed first to reserve #1387; full spec body generated via the spec-creation pipeline from the reserved number.

## Not Included

- **Term-space backend (embedding service, derived table, migrations, backfill, calibration, model pins, statuses)** — owned by issue #1386; this spec only consumes `TermSearchResult`.
- **Threshold preference storage layer** — `preference_service.py` is consumed as-is; no code change in either spec.
- **Gloss-space UI changes beyond coexistence verification** — owned by issue #1385; term modes must be strictly additive.
- **Admin Term-space Backfill button work** — Table Maintenance's term-space button is #1386 SC-9; this spec only cites the remedy in empty-state copy.
- **Score display styling beyond placement** — the exact visual design of score badges/captions is a plan implementation detail; the SCs cover term-rows-only visibility and sorted order.
- **Term-mode export semantics beyond the existing export-path guard** — matching term records' export behavior is undefined (flagged in code-path-inventory as a plan decision; the #1385 precedent left semantic export equally undefined).
- **Any model artifact, ONNX, or dependency changes** — #1386 owns `models/` and dependency declarations.

## Success Criteria

| ID | Criterion | Evidence Type | Documentation Sources | Verification Method |
|----|-----------|---------------|----------------------|---------------------|
| SC-1 | The records-page mode radio renders the two new term-space entries "Semantic Term" and "Semantic Phrase", each with a caption, while the existing four entries (Headword, Gloss, Lexeme, FTS) and their captions remain unchanged | behavioral | `src/frontend/pages/records.py` mode list + SEARCH_MODE_CAPTIONS (`:206-221`, live-verified 2026-09-29); `.issues/1387/artifacts/interface-compat.yaml` | Playwright/AppTest: radio options include both new modes; captions render; existing 4 options untouched |
| SC-2 | The term-space threshold control (two-way coupled slider + numeric) persists a round-trip through PreferenceService under view_name `records` / key `term_threshold`, shared across both term modes with provisional default `0.80`, and a non-numeric or out-of-range edit is rejected with the widget snapping back to the last accepted value without persisting | behavioral | `src/services/preference_service.py:17,:37` (verified fresh); #1385 spec R-2/R-3 widget contract precedent; `.issues/1387/artifacts/cross-cutting-matrix.yaml` persistence rules | Playwright/pytest: widget coupling sync; persistence round-trip via get/set_preference; invalid edit → snap-back, no write |
| SC-3 | Selecting a term-space mode invokes the #1386 `search_terms` seam with the per-user threshold (never routing through `search_records`, never widening SearchMode) and renders returned rows with per-row term metadata (term, entry_type, language_code, source) and similarity scores in descending order | behavioral | `src/services/linguistic_service.py:28,:451-453` SearchMode Literal + ValueError path (live-verified); #1386 spec R-7 seam contract; `.issues/1387/artifacts/code-path-inventory.yaml` dispatch fork | pytest dispatch branch with contract-shaped mock: seam invoked once per query; row mapping field-exact; `search_records` path untouched for term modes |
| SC-4 | Exact-match modes (Headword, Gloss, Lexeme, FTS) and #1385's gloss-space modes display no scores and return results identical to pre-extension behavior after the term-mode addition | behavioral | `records.py` result render block (`:540-543`, live-verified); `.issues/1387/artifacts/cross-cutting-matrix.yaml` regression-safety rules | Playwright behavioral harness (precedent `test_search_mode_ui_red.py`): existing modes regression-safe; no score badges on non-term rows |
| SC-5 | Pagination slices the full ranked term list rank-once: page navigation preserves order deterministically (descending score with the seam tie-break), never re-invokes the seam, and existing page-clamping behavior is unchanged | behavioral | `records.py` pagination state keys + clamping (`:137-179`, `:174-176`, live-verified); `.issues/1387/artifacts/cross-cutting-matrix.yaml` rank-once invariants | Playwright: navigate pages; assert order stability across navigation and single seam invocation |
| SC-6 | Each seam status (empty_query, no_embeddings, stale_model, zero-below-threshold ok) renders its designated clean empty state, never a crash or unhandled seam exception; the stale_model and no-embeddings copy names the admin remedy (Table Maintenance → Data Reprocessing → Term-space Backfill) | behavioral | #1386 spec SC-7 status semantics; `.issues/1387/artifacts/state-analysis.yaml` term-mode lifecycle; `src/frontend/pages/table_maintenance.py:124-196` (live-verified) | Playwright/mock-payload rendering: each status branch renders the correct copy; seam exception renders degraded state |
| SC-7 | Term-mode result rows display Unicode term text byte-exact (IPA characters, combining diacritics, ꝏ, ∞) with entry_type, language_code, and source labels rendered, with no normalization in the rendering path | behavioral | AGENTS.md Tier 1 Unicode mandate; `.issues/1387/artifacts/research-card-consultation.yaml` (roger-williams diacritic repertoire, confidence 0.9) | pytest Unicode round-trip on the rendered structure asserting byte-exact term text and metadata labels |

## Requirements

R-1. The records page SHALL expose "Semantic Term" and "Semantic Phrase" as selectable search modes through the existing mode radio, preserving all existing mode keys and captions (Headword, Gloss, Lexeme, FTS).

R-2. The records page SHALL provide a term-space similarity-threshold control (two-way coupled slider + numeric input) whose value persists per user via PreferenceService under view_name `records`, key `term_threshold`, shared across both term modes, defaulting to the provisional value `0.80` pending the #1386 SC-6 calibration floors.

R-3. The records page SHOULD reject a non-numeric or out-of-range threshold edit and snap the widget back to the last accepted value without persisting.

R-4. The records page SHALL dispatch term-space mode selection to the #1386 `search_terms` seam (NOT `search_records`) and SHALL NOT widen the SearchMode Literal in `linguistic_service.py`; the search mode machine in `linguistic_service.py` SHALL remain unchanged.

R-5. The records page SHALL target the selected entry type by client-side filtering on the seam's per-row `entry_type` field, making exactly one seam invocation per query; when the selected mode's entry type yields zero displayed rows, the records page SHALL render the designated zero-results empty state.

R-6. Term-mode result rows SHALL display similarity scores in sorted (descending) order with the seam's tie-break preserved, together with per-row term, entry_type, language_code, and source labels; exact-match and gloss-space mode rows SHALL NOT display similarity scores.

R-7. Pagination SHALL slice the full ranked list returned by the seam; the seam SHALL NOT be re-invoked on page navigation, and the existing page-clamping behavior SHALL be preserved.

R-8. The records page SHALL render a designated clean empty state for each seam status (`empty_query`, `no_embeddings`, `stale_model`, zero-below-threshold) and SHALL NOT crash or surface an unhandled exception on any degraded status or seam exception; the `stale_model` and no-embeddings message SHALL name the admin backfill remedy (Table Maintenance → Data Reprocessing → Term-space Backfill).

R-9. Term-mode result rows SHALL display term text byte-exact (IPA characters, combining diacritics, ꝏ, ∞ first-class data), with no normalization applied in the rendering path.

R-10. The UI layer SHALL bind to `search_terms`/`TermSearchResult` (v1 field list: `results: list[(record_id, score, entry_type, language_code, source_id, term)]`, `status` ∈ {ok, empty_query, no_embeddings, stale_model}, `message`) through an import-guarded, contract-fixture-shaped binding and SHALL NOT import pgvector or ORM internals.

## Items

### Item 1 (SC-1): Mode radio entries + captions for Semantic Term / Semantic Phrase
- RED: behavioral test asserting the mode radio lacks the two term-space entries while the four existing entries render
- GREEN: extend the mode list + SEARCH_MODE_CAPTIONS in records.py with the two term-space entries; preserve session_state keys; guard the radio index lookup against stale session values
- verify: Playwright/AppTest radio options + captions; existing options unchanged
- commit: records.py mode list + captions only

### Item 2 (SC-2): Shared threshold control + persistence + snap-back
- RED: test asserting no term-space threshold preference control exists
- GREEN: two-way coupled slider+numeric control; persist via PreferenceService (`records`/`term_threshold`, provisional default `0.80`); invalid edit snaps back without writing
- verify: pytest/Playwright persistence round-trip + widget coupling + snap-back
- commit: records.py threshold control

### Item 3 (SC-3): Term-mode dispatch through the search_terms seam
- RED: test asserting term-mode selection still routes through search_records (ValueError path or zero results)
- GREEN: term-mode dispatch branch: import-guarded search_terms binding, one invocation per query, threshold from the shared preference; map TermSearchResult rows to records with per-row metadata
- verify: pytest dispatch branch + row mapping field-exact; search_records path untouched for term modes
- commit: records.py term-mode dispatch + seam binding

### Item 4 (SC-4): Exact/gloss-mode regression guard (additive dispatch)
- RED: behavioral harness asserting existing modes' results/captions regress after the additions
- GREEN: guard dispatch so the term branch is strictly additive; existing modes untouched; no score rendering on non-term rows
- verify: Playwright harness per test_search_mode_ui_red.py precedent
- commit: dispatch wiring + regression test

### Item 5 (SC-5): Rank-once pagination slicing for term results
- RED: test asserting page navigation re-invokes the seam or reorders the ranked term list
- GREEN: rank-once slice of the full ranked list through the existing current_page/page_size keys; preserve page clamping
- verify: Playwright order-stability + invocation-count assertions
- commit: records.py term pagination slicing

### Item 6 (SC-6): Status-keyed empty states (incl. Term-space Backfill remedy copy)
- RED: test asserting seam statuses crash the page or render wrong copy
- GREEN: status→empty-state mapping; stale_model/no_embeddings copy names Table Maintenance → Data Reprocessing → Term-space Backfill; zero-below-threshold renders clean zero-results; seam exceptions degrade to empty state via the handle_ui_error idiom
- verify: Playwright/mock-payload per-status assertions; 4 statuses + zero-results
- commit: records.py empty-state branch

### Item 7 (SC-7): Unicode-faithful term-row rendering with metadata labels
- RED: test asserting Unicode mangling or missing metadata in term-row rendering
- GREEN: render term text byte-exact + entry_type + language_code + source labels; scores descending; no normalization in the rendering path
- verify: pytest Unicode round-trip on the rendered structure
- commit: records.py term-row rendering

## Dependencies

| Reference | Relationship | Status |
|-----------|--------------|--------|
| Issue #1386 (https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1386) | must deliver the `search_terms` seam + `TermSearchResult` v1 contract; SC-3/SC-5/SC-6/SC-7 verify against a contract-shaped mock until Item 5 (seam) lands, then green-path verification runs against the real service | pending |
| Issue #1385 (https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1385) | provides the approved records-page UI pattern precedent (threshold widget contract, rank-once pagination, per-status empty states, harness idiom); gloss modes are coexistence-verified, not modified | in progress (pattern) |
| `preference_service.py` | consumed as-is (get/set_preference verified fresh at :17,:37) | satisfied |
| Playwright/AppTest harness precedent (`test/test_search_mode_ui_red.py`) | test-harness pattern for behavioral UI SCs | satisfied (pattern) |

## Traceability

| Requirement | SC(s) | Phase(s) |
|-------------|-------|----------|
| R-1 | SC-1 | 1 |
| R-2 | SC-2 | 1 |
| R-3 | SC-2 | 1 |
| R-4 | SC-3, SC-4 | 1 |
| R-5 | SC-3, SC-6 | 1 |
| R-6 | SC-3, SC-4, SC-7 | 1 |
| R-7 | SC-5 | 1 |
| R-8 | SC-6 | 1 |
| R-9 | SC-7 | 1 |
| R-10 | SC-3, SC-5, SC-6 | 1 |

## Documentation Sources

| Source | Type | Location | Verification |
|--------|------|----------|--------------|
| records.py mode radio + SEARCH_MODE_CAPTIONS | code | `src/frontend/pages/records.py:206-221` | live `sed` read 2026-09-29 |
| records.py result calculation + pagination state + clamping | code | `src/frontend/pages/records.py:130-179` (search_records call :157, clamp :174-176) | live `sed` read 2026-09-29 |
| records.py result render block | code | `src/frontend/pages/records.py:540-543` | live `sed` read 2026-09-29 |
| SearchMode Literal + ValueError path | code | `src/services/linguistic_service.py:28,:451-453` | live `rg`/`sed` read 2026-09-29 |
| PreferenceService get/set_preference | code | `src/services/preference_service.py:17,:37` | live read (srclight verified-fresh) 2026-09-29 |
| Table Maintenance Data Reprocessing section (remedy copy target) | code | `src/frontend/pages/table_maintenance.py:124-196` | live `sed` read 2026-09-29 |
| #1386 seam contract + status semantics + calibration ownership | spec | `.issues/1386/spec.md` R-7/SC-5/SC-6/SC-7 + https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1386 | read this session |
| #1385 UI precedent (threshold widget, rank-once, empty states, regression harness) | spec | `.issues/1385/spec.md` R-2/R-3/R-5/R-6 + Items + Cost Frame + https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1385 | read this session |
| TermSearchResult v1 field list + seam signature | analysis artifact | `.issues/1387/artifacts/pre-spec-inspection.yaml` (seam_contract), `interface-compat.yaml` (dependency_contract) | read this session |
| Unicode diacritic repertoire (rendering fidelity constraint) | research card | `.issues/research-cards/roger-williams-key-research.md` | read this session (confidence 0.9) |
| Variant-spelling problem grounding | research card | `.issues/research-cards/cross-source-comparison.md` | read this session (confidence 0.9) |

## Enforcement Gate

> **Enforcement gate:** All success criteria MUST pass before this spec is considered complete. Partial implementation is not permitted.

## Cost Frame

Cost is measured in defect-discovery-latency, not tool calls. Correctness is the only metric.

- **SC-1:** Behavioral radio test costs minutes of Playwright/AppTest execution. Skipping means a broken mode dispatch ships and every term-space session on the highest-traffic page is silently unreachable — user-reported days after the backend feature it serves is live.
- **SC-2:** Persistence round-trip + snap-back tests cost minutes. Skipping means thresholds silently reset per session or a typo corrupts the stored preference — discovered only after linguists lose trust in tuned retrieval precision.
- **SC-3:** Dispatch-branch test costs minutes. Skipping means term modes route into `search_records`'s ValueError path or return zero results with no error surfaced — the entire feature ships inert, caught only when the first stakeholder tries it.
- **SC-4:** Regression harness costs minutes. Skipping means breaking the four existing search modes plus #1385's gloss modes on the app's primary page — discovered by linguists immediately, with a full rework and re-review cycle.
- **SC-5:** Order-stability + invocation-count harness costs minutes. Skipping means page navigation reorders or re-ranks term results — the instability class that surfaces only after data volume grows, costing a full session-state-flow diagnosis days later.
- **SC-6:** Per-status rendering test costs minutes. Skipping means degraded states crash the page when embeddings are missing or the model pin drifts — the highest-frequency failure surface for a derived index populated by a separate backfill, found in production support tickets (1000× escalation).
- **SC-7:** Unicode round-trip test costs minutes. Skipping means mangled or normalized vernacular display — silent corruption of the exact data class (diacritics, ꝏ, ∞) that motivated the feature, surfacing in linguistic review with re-render and re-verify cycles.

## Edge Cases

| Condition | Expected Behavior | Resolution |
|-----------|-------------------|------------|
| Empty or whitespace-only query in a term mode | Designated `empty_query` empty state; no seam/model call | SC-6 rendering branch |
| No term-space rows exist yet (fresh deploy, no backfill) | `no_embeddings` empty state; message names the Term-space Backfill remedy | SC-6 |
| Stored model pin differs from rows (`stale_model`) | `stale_model` empty state; message names the backfill remedy | SC-6 |
| All rows below the shared threshold | `ok` with empty results → clean zero-results message — not an error | SC-5, SC-6 |
| Zero rows of the selected entry type after filtering (mode targets phrases; only terms matched) | Clean zero-results empty state for the mode — not the other type's rows | R-5, SC-3, SC-6 |
| Seam raises an unexpected exception | Degraded empty state via the handle_ui_error idiom — never a crash | R-8, SC-6 |
| Non-numeric or out-of-range threshold edit | Rejected; widget snaps back to last accepted value; nothing persists | SC-2 |
| Stale session_state `search_mode` value not present in the radio list | Guarded index lookup renders the default mode — no ValueError crash | Item 1 guard (SC-1) |
| Page navigation with large ranked list | Slice-only; order identical across pages; no re-rank or seam re-call | SC-5 |
| `current_page` beyond result count after a narrowing query | Existing clamping behavior (max(1, total_pages)) preserved | SC-5 |
| Rapid mode switching between exact-match, gloss, and term modes | Correct result set per mode; no stale widget state; scores only on term rows | SC-1, SC-3, SC-4 |
| Term text with combining diacritics rendered from results | Byte-exact display; no normalization in the rendering path | SC-7 |

---

*Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)*
