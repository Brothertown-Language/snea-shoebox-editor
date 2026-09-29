# [SPEC] Semantic Search end-user interface — records page modes, threshold, scores, pagination, empty states

> **Full spec and artifacts: [`https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1385/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1385/)** — this issue is a condensed exec summary; the authoritative spec lives in the `issues-data` branch.
>
> **Local artifacts:** `.issues/1385/` — analytical artifacts, sc-summary, plan, audit findings

## Intent and Executive Summary

**Problem Statement:** The records page offers no way to use the semantic gloss search delivered by #36 — the mode radio exposes only Headword/Gloss/Lexeme/FTS, there is no similarity-threshold control, no similarity-score display, and no handling for the semantic search degraded-state payloads.

**Root Cause / Motivation:** #36 was split by developer directive: the db/embed components land in #36 while the end-user search interface is specified separately. This spec is the UI half; it binds only to the `search_semantic` seam contract from #36 and to the existing records page structure.

**Approach Chosen:** Extend the existing records page search panel — two new entries in the existing mode radio, one new per-user threshold control persisted through the existing PreferenceService, score badges/captions rendered only on semantic-mode rows, rank-once pagination slicing of the service's full ranked list, and empty-state rendering keyed off the seam's `status`+`message` payload.

**Alternatives Considered & Why Discarded:**
- *Full-text-search expansion (synonym tables)* — rejected: FTS is exact-text; synonym lists require curated data maintenance and miss cross-concept matches that embedding similarity captures.
- *Dedicated semantic-search page* — rejected: fragments the search UX; the existing page already owns filters, pagination, result rendering, and role plumbing, so a second page would duplicate all of it.

**Key Design Decisions:**
- UI binds to the `search_semantic` seam contract (v1 field list) and nothing below it — no pgvector/ORM imports in the UI layer (tradeoff: UI cannot bypass the service for performance tweaks; correctness of layering wins).
- Threshold is a per-user preference (`records`/`semantic_threshold`, default `0.80`), not a global config — tradeoff: per-user storage rows, but each linguist's retrieval precision preference is preserved across sessions.
- Pagination is pure slicing of the service's full ranked list (rank-once) — tradeoff: larger session payloads, but page navigation can never reorder results.
- Score display on semantic rows only — tradeoff: a second rendering branch, but exact-match modes keep their unchanged layout.

**User Intent / Original Prompt:** Developer brainstorming session 2026-09-28 (handoff.yaml, 10 turns, design approved, finalization "proceed"): split #36's scope; db/embed stays with #36; end-user search interface becomes a follow-up spec filed REMOTE-FIRST to obtain its number.

## Not Included

- **Semantic search payload/rules (embedding service, pgvector schema, migrations, backfill, calibration, statuses)** — owned by issue #36; this spec only consumes `SemanticSearchResult`.
- **Threshold preference storage layer** — `preference_service.py` is consumed as-is; no code change in either spec.
- **Score badge styling beyond placement** — the exact visual design of badges/captions is an implementation detail for the plan; the SC covers semantic-rows-only visibility and sorted order.
- **Any model artifact or dependency changes** — #36 owns `models/`, ONNX, and dependency declarations.

## Success Criteria

| ID | Criterion | Evidence Type | Documentation Sources | Verification Method |
|----|-----------|---------------|----------------------|---------------------|
| SC-1 | The records-page mode radio renders Semantic Gloss and Semantic All entries, each with a developer-approved caption, while existing entries and captions remain unchanged | behavioral | `src/frontend/pages/records.py` (mode list + SEARCH_MODE_CAPTIONS, :215 region); seam contract in `.issues/36/artifacts/interface-compat.yaml` | Playwright: radio options include both new modes; captions render; existing 4 options untouched |
| SC-2 | Setting the similarity threshold via the slider or numeric input persists a round-trip through PreferenceService (`records`/`semantic_threshold`, default `0.80`) and the two widgets always agree | behavioral | `src/services/preference_service.py:17,37` (verified fresh); `concern-map.yaml` boundaries | Playwright/pytest: widget coupling sync, persistence round-trip via get/set_preference |
| SC-3 | A non-numeric threshold edit is rejected and the widget snaps back to the previously accepted value | behavioral | `handoff.yaml` developer decisions (widget contract) | Playwright: invalid input entry → widget value reverts; preference unchanged |
| SC-4 | Semantic-mode result rows display similarity scores in sorted order, and exact-match mode rows do not display scores | behavioral | `records.py` result render block (:155-185 region); seam `results: list[(record_id, score)]` | Playwright: badges/captions present on semantic rows in descending order; absent for existing modes |
| SC-5 | Pagination slices the returned ranked list without re-invoking search: page navigation preserves order deterministically (desc score, record_id asc tie-break) | behavioral | `records.py` pagination state keys (current_page); seam rules in `concern-map.yaml` | Playwright: navigate pages; assert sequence stability across navigation, single search invocation |
| SC-6 | Each seam status (`empty_query`, `no_embeddings`, `stale_model`, plus zero-results-after-threshold) renders its designated clean empty state, never a crash or unhandled error; stale/none message names the admin backfill remedy | behavioral | seam status enum in `concern-map.yaml` + `decompose-output.yaml` D2-ITEM-5 | Playwright/mocked-payload rendering: each status branch renders the correct copy |
| SC-7 | Switching between exact-match and semantic modes changes returned results correctly, and the existing four modes' results are unchanged after the addition | behavioral | `linguistic_service.py:28` SearchMode widening (verified live); `testability.yaml` regression risk | Playwright behavioral harness (precedent `test_search_mode_ui_red.py`): result sets differ per mode; existing modes regression-safe |

## Requirements

R-1. The records page SHALL expose Semantic Gloss and Semantic All as selectable search modes through the existing mode radio, preserving all existing mode keys and captions.

R-2. The records page SHALL provide a similarity-threshold control (slider + numeric input, two-way coupled) whose value persists per user via PreferenceService under view_name `records`, key `semantic_threshold`, defaulting to `0.80`.

R-3. The records page SHOULD reject a non-numeric or out-of-range threshold edit and snap the widget back to the last accepted value.

R-4. Semantic-mode result rows SHALL display similarity scores in sorted (descending) order; exact-match mode rows SHALL NOT display similarity scores.

R-5. Pagination SHALL slice the full ranked list returned by the seam; the service SHALL NOT be re-invoked on page navigation.

R-6. The records page SHALL render a designated clean empty state for each seam status (`empty_query`, `no_embeddings`, `stale_model`, all-below-threshold) and SHALL NOT crash on any status; the `stale_model` and no-embeddings message SHALL name the admin backfill remedy (Table Maintenance → Data Reprocessing → Embedding Backfill).

R-7. Switching between exact-match and semantic modes SHALL change the returned result set per mode semantics; existing modes' result behavior SHALL remain unchanged.

R-8. The UI layer SHALL bind to `search_semantic`/`SemanticSearchResult` (v1 field list: `results: list[(record_id, score)]`, `status` ∈ {ok, empty_query, no_embeddings, stale_model}, `message`) and SHALL NOT import pgvector or ORM internals.

## Items

### Item 1 (SC-1): Mode radio entries + captions for Semantic Gloss / Semantic All
- RED: Playwright test asserting the mode radio lacks Semantic Gloss / Semantic All (fails)
- GREEN: extend mode list + SEARCH_MODE_CAPTIONS dict in `records.py`; session_state keys preserved
- verify: Playwright radio options + captions, existing options unchanged
- commit: records.py mode list only

### Item 2 (SC-2): Threshold preference — slider+numeric coupled, persists
- RED: widget test asserting no `semantic_threshold` preference control exists
- GREEN: render coupled slider+numeric control; persist via set_preference(`records`,`semantic_threshold`); init from get_preference default `0.80`
- verify: Playwright/pytest two-way sync + persistence round-trip
- commit: records.py (or ui_utils.py shared component) threshold control

### Item 3 (SC-3): Invalid threshold edit rejected + snap-back
- RED: test asserting invalid edit persists (no snap-back exists)
- GREEN: validation guard rejecting non-numeric/out-of-range with snap-back
- verify: Playwright invalid-input revert assertion
- commit: threshold control validation

### Item 4 (SC-4): Score badge/caption on semantic rows only, sorted order
- RED: test asserting no score badges render for any mode
- GREEN: consume `results` scores in the semantic rendering branch; render badges/captions descending; skip for exact-match modes
- verify: Playwright badge presence/order and absence in exact-match modes
- commit: records.py result render block

### Item 5 (SC-5): Pagination rank-once slice
- RED: test asserting page navigation re-invokes search or reorders results
- GREEN: slice the already-returned ranked list on page change; no service re-invocation
- verify: Playwright order-stability across navigation + invocation count
- commit: records.py pagination slicing

### Item 6 (SC-6): Empty-state rendering per status payload
- RED: test asserting no crash-guard rendering exists for statuses
- GREEN: map each status + message to UI copy; stale/none message names backfill remedy
- verify: Playwright/mocked-payload per-status rendering assertions
- commit: records.py empty-state branch

### Item 7 (SC-7): Mode-switching regression + correctness
- RED: behavioral harness asserting semantic modes yield errors / existing modes regress
- GREEN: dispatch by SearchMode through `search_records` entry (widened Literal consumed); wire results per mode
- verify: behavioral Playwright harness (precedent `test_search_mode_ui_red.py`), result sets differ per mode, existing modes unchanged
- commit: dispatch wiring + regression test

## Dependencies

| Reference | Relationship | Status |
|-----------|--------------|--------|
| Issue #36 (https://github.com/Brothertown-Language/snea-shoebox-editor/issues/36) | must deliver the `search_semantic` seam + `SemanticSearchResult` v1 contract before UI items 4-6 can verify | pending (this pipeline) |
| Issue #400 (closed, merged) | provides existing records-page search panel state keys and rendering structure this spec extends | satisfied |
| `preference_service.py` | consumed as-is (get/set_preference verified fresh at :17,:37) | satisfied |
| Playwright harness precedent (`test_search_mode_ui_red.py`) | test-harness pattern for behavioral UI SCs; coordinate to avoid compounding #1347 red state | satisfied (pattern) |

## Traceability

| Requirement | SC(s) | Phase(s) |
|-------------|-------|----------|
| R-1 | SC-1 | 1 |
| R-2 | SC-2 | 1 |
| R-3 | SC-3 | 1 |
| R-4 | SC-4 | 1 |
| R-5 | SC-5 | 1 |
| R-6 | SC-6 | 1 |
| R-7 | SC-7 | 1 |
| R-8 | SC-1, SC-4, SC-6 | 1 |

## Documentation Sources

| Source | Type | Location | Verification |
|--------|------|----------|--------------|
| SearchMode Literal + search_records | code | `src/services/linguistic_service.py:28,:391` | live `rg` read 2026-09-28 |
| records.py search panel (mode list, captions, current_page, radio) | code | `src/frontend/pages/records.py:63,:162-163,:212-219` | live `sed`/`rg` read 2026-09-28 |
| Role guard + reprocess idiom (backfill remedy context) | code | `src/frontend/pages/table_maintenance.py:125-130,:169-196` | live `sed` read 2026-09-28 |
| PreferenceService get/set_preference | code | `src/services/preference_service.py:17,:37` | live `sed` read 2026-09-28 |
| Parent seam contract + status enum | analysis artifact | `.issues/36/artifacts/concern-map.yaml`, `interface-compat.yaml` | read this session |
| #36 parent spec (db/embed) | spec | `.issues/36/spec.md` + https://github.com/Brothertown-Language/snea-shoebox-editor/issues/36 | fetched 2026-09-28 |

## Enforcement Gate

> **Enforcement gate:** All success criteria MUST pass before this spec is considered complete. Partial implementation is not permitted.

## Cost Frame

Cost is measured in defect-discovery-latency, not tool calls. Correctness is the only metric.

- **SC-1:** Behavioral radio test costs minutes of Playwright execution. Skipping means a broken mode dispatch ships and every semantic search session on the highest-traffic page hits a silently wrong result set — days-to-weeks of user-reported defect latency.
- **SC-2:** Persistence round-trip test costs minutes. Skipping means thresholds silently reset per session, making retrieval precision unpredictable across reruns — discovered only after linguists lose trust in tuned results.
- **SC-3:** Snap-back test costs minutes. Skipping means a typo silently corrupts a stored preference and degrades every future search for that user until manually diagnosed.
- **SC-4:** Rendering assertion costs minutes. Skipping means scores vanish or appear on wrong rows — discovered in stakeholder review after merge (10× DDL multiplier).
- **SC-5:** Order-stability harness costs minutes. Skipping means page navigation reorders results — the exact instability class that surfaces only after data volume grows, costing a full diagnosis of session-state flow days later.
- **SC-6:** Per-status rendering test costs minutes. Skipping means degraded states crash the page for real users when embeddings are missing — highest-frequency failure surface, found in production support tickets (1000× escalation).
- **SC-7:** Regression harness costs minutes. Skipping means breaking the four existing search modes on the app's primary page — discovered by linguists immediately, with full rework cycle.

## Edge Cases

| Condition | Expected Behavior | Resolution |
|-----------|-------------------|------------|
| Empty or whitespace-only query in semantic mode | Designated `empty_query` empty state; no service/model call | SC-6 rendering branch |
| No records have embeddings yet | `no_embeddings` empty state; message names the admin backfill remedy | SC-6 |
| Stored model pin differs from rows (`stale_model`) | `stale_model` empty state; message names the backfill remedy | SC-6 |
| All results below threshold | Empty result set with a clean zero-results message — not an error | SC-6 |
| Non-numeric or out-of-range threshold edit | Rejected; widget snaps back to last accepted value | SC-3 |
| Page navigation with large ranked list | Slice-only; order identical across pages; no re-rank | SC-5 |
| Rapid mode switching between exact-match and semantic | Correct result set per mode; no stale widget state | SC-1, SC-7 |
| Session state `current_page` beyond result count | Existing clamping behavior (max(1, total_pages)) preserved | SC-5 |

---

*Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)*