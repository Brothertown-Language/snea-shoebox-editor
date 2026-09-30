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
- Threshold control occupies a stable sidebar slot in ALL modes — rendered below the mode caption, above the search/clear buttons — with the widgets disabled (plus an explanatory help/caption note) in non-semantic modes. Research-backed rationale: consistent layout beats reflow-on-mode-flip, and disable-with-reason (the hidden-vs-disabled rule; the WorldCat/EBSCO/Jira convention) beats conditional hiding.
- Pagination is pure slicing of the service's full ranked list (rank-once) — tradeoff: larger session payloads, but page navigation can never reorder results.
- Score display on semantic rows only — tradeoff: a second rendering branch, but exact-match modes keep their unchanged layout.
- Language/role filters disabled in semantic modes, mirroring the FTS disabled-filter idiom, because the seam accepts only `source_id` — tradeoff: a previously-selected language filter value is preserved but inert during semantic mode, but no false language constraint can silently leak into result expectations.

**User Intent / Original Prompt:** Developer brainstorming session 2026-09-28 (handoff.yaml, 10 turns, design approved, finalization "proceed"): split #36's scope; db/embed stays with #36; end-user search interface becomes a follow-up spec filed REMOTE-FIRST to obtain its number.

## Not Included

- **Semantic search payload/rules (embedding service, pgvector schema, migrations, backfill, calibration, statuses)** — owned by issue #36; this spec only consumes `SemanticSearchResult`.
- **Threshold preference storage layer** — `preference_service.py` is consumed as-is; no code change in either spec.
- **Score badge styling beyond the pinned placement, format, and theme-safety** — R-4 pins the location (semantic-mode record card header line), the display format (fixed two decimals), and theme-aware native-element styling; the exact native-element variants and visual polish remain implementation details for the plan.
- **Any model artifact or dependency changes** — #36 owns `models/`, ONNX, and dependency declarations.

## Success Criteria

| ID | Criterion | Evidence Type | Documentation Sources | Verification Method |
|----|-----------|---------------|----------------------|---------------------|
| SC-1 | The records-page mode radio renders Semantic Gloss and Semantic All entries while existing entries and captions remain unchanged; the new modes ADD SEARCH_MODE_CAPTIONS dict entries and the single selected-mode caption pattern (one caption for the SELECTED mode, rendered under the radio) is preserved unchanged | behavioral | `src/frontend/pages/records.py` (SEARCH_MODE_CAPTIONS dict, mode radio, single st.caption under the radio); seam contract in `.issues/36/artifacts/interface-compatibility.yaml` | Behavioral pytest via streamlit AppTest (repo precedent harness; see Change Control note on "Playwright"): radio options include both new modes; the selected-mode caption renders for each selection; existing 4 options and captions untouched |
| SC-2 | Setting the similarity threshold via the slider or numeric input persists a round-trip through PreferenceService (`records`/`semantic_threshold`, default `0.80`) and the two widgets always agree | behavioral | PreferenceService `get_preference`/`set_preference` in `src/services/preference_service.py` (preference getter/setter pair, verified fresh 2026-09-30); `concern-map.yaml` boundaries | Behavioral pytest via streamlit AppTest: widget coupling sync, persistence round-trip via get/set_preference; stable-slot placement (control present in ALL modes below the mode caption, above the search/clear buttons) with widgets disabled + the "Applies only in Semantic modes." help text in non-semantic modes |
| SC-3 | A non-numeric threshold edit is rejected and the widget snaps back to the previously accepted value | behavioral | `handoff.yaml` developer decisions (widget contract) | Behavioral pytest via streamlit AppTest: invalid input entry → widget value reverts; preference unchanged |
| SC-4 | Semantic-mode result rows display similarity scores in sorted (descending) order, rendered inline in each record card's header line (not behind a disclosure/expander) as fixed two-decimal values, and exact-match mode rows do not display scores | behavioral | `records.py` record-card render loop (card header line); seam `results: list[(record_id, score)]` | Behavioral pytest via streamlit AppTest: badges/captions present on semantic rows in descending order, formatted to two decimals, inline in the header line; absent for existing modes |
| SC-5 | Pagination slices the returned ranked list without re-invoking search: page navigation preserves order deterministically (desc score, record_id asc tie-break) | behavioral | `records.py` pagination state keys (current_page); seam rules in `concern-map.yaml` | Behavioral pytest via streamlit AppTest with invocation-count spy: navigate pages; assert sequence stability across navigation, single search invocation |
| SC-6 | Each seam status (`empty_query`, `no_embeddings`, `stale_model`, plus zero-results-after-threshold) renders its designated clean empty state, never a crash or unhandled error; stale/none message names the admin backfill remedy | behavioral | seam status enum in `concern-map.yaml` + `decompose-output.yaml` D2-ITEM-5 (unit "empty-state rendering per status payload", SC-U5) — decomposition artifact in `tmp/issue-36/contracts/decompose-output.yaml`, verified on disk 2026-09-30 (tmp/ is volatile scratch; `.issues/36/artifacts/decompose-output.yaml` holds the D1 items only) | Behavioral pytest via streamlit AppTest with mocked seam payloads: each status branch renders the correct copy |
| SC-7 | Switching between exact-match and semantic modes changes returned results correctly, and the existing four modes' results are unchanged after the addition | behavioral | SearchMode widening in `src/services/linguistic_service.py` (search mode union type at module top, verified live 2026-09-30); regression-risk rows in `.issues/36/artifacts/testability-assessment.yaml` | Behavioral pytest behavioral harness (precedent `test_search_mode_ui_red.py`): result sets differ per mode; existing modes regression-safe |
| SC-8 | In Semantic Gloss and Semantic All modes, the language selectbox and language-role radio are disabled with explanatory help text (mirroring the FTS-mode idiom), and the existing modes' filter behavior is unchanged | behavioral | FTS disabled-filter idiom in `src/frontend/pages/records.py` (language selectbox + language-role radio use a disabled state with help text); seam contract in `.issues/36/artifacts/interface-compatibility.yaml` (`search_semantic` accepts only `source_id`) | Behavioral pytest via streamlit AppTest: both controls disabled with help text in both semantic modes; existing modes' filter state unchanged (Headword/Gloss/Lexeme enabled, FTS disabled per the existing idiom — no regression) |

## Requirements

R-1. The records page SHALL expose Semantic Gloss and Semantic All as selectable search modes through the existing mode radio, preserving all existing mode keys and captions; the new modes ADD entries to the SEARCH_MODE_CAPTIONS dict, and the single selected-mode caption pattern (one caption for the selected mode, rendered under the radio) SHALL be preserved unchanged.

R-2. The records page SHALL provide a similarity-threshold control (slider + numeric input, two-way coupled) whose value persists per user via PreferenceService under view_name `records`, key `semantic_threshold`, defaulting to `0.80`. The threshold SHALL be a proportion in [0.0, 1.0], displayed as a decimal (default 0.80) in BOTH coupled widgets, and stored via `str(value)` matching the existing page_size string idiom. The control SHALL render in the sidebar search-controls block directly below the mode caption and above the search/clear buttons; it SHALL be present in ALL modes (stable slot — no conditional render and no layout reflow), with the widgets disabled (native Streamlit `disabled=`) in non-semantic modes alongside the explanatory help/caption text "Applies only in Semantic modes."

R-3. The records page SHOULD reject a non-numeric or out-of-range threshold edit and snap the widget back to the last accepted value.

R-4. Semantic-mode result rows SHALL display similarity scores in sorted (descending) order; exact-match mode rows SHALL NOT display similarity scores. Scores SHALL render inline in each semantic-mode record card's header line (the "Record #id (Source: X)" line of the record-card render loop) — NOT behind a disclosure/expander. Scores SHALL display as fixed two-decimal values; raw float reproduction (e.g. 0.8333333) is unacceptable. Score/empty-state styling SHOULD use theme-aware native Streamlit elements (st.badge, st.caption) with no hardcoded hex/rgba colors and no new st.html iframe CSS.

R-5. Pagination SHALL slice the full ranked list returned by the seam; the service SHALL NOT be re-invoked on page navigation.

R-6. The records page SHALL render a designated clean empty state for each seam status (`empty_query`, `no_embeddings`, `stale_model`, all-below-threshold) and SHALL NOT crash on any status; the `stale_model` and no-embeddings message SHALL name the admin backfill remedy (Table Maintenance → Data Reprocessing → Embedding Backfill). Empty states SHALL render in the MAIN panel as full-width blocks in the records area (precedent: the existing empty-batch path renders st.info("No records found matching your criteria.") in the main panel); sidebar rendering is prohibited (long backfill-remedy messages wrap badly in the narrow sidebar). st.info SHALL be used for informational states (`empty_query`, zero-results-after-threshold) and st.warning for remedy-required states (`no_embeddings`, `stale_model`); the zero-results-after-threshold state SHALL reuse the existing empty-batch rendering branch with status-specific copy. Empty-state styling SHOULD use theme-aware native Streamlit elements (st.info, st.warning, st.badge, st.caption) with no hardcoded hex/rgba colors and no new st.html iframe CSS (the `.streamlit/config.toml` has no `[theme]` section).

R-7. Switching between exact-match and semantic modes SHALL change the returned result set per mode semantics; existing modes' result behavior SHALL remain unchanged.

R-8. The UI layer SHALL bind to `search_semantic`/`SemanticSearchResult` (v1 field list: `results: list[(record_id, score)]`, `status` ∈ {ok, empty_query, no_embeddings, stale_model}, `message`) and SHALL NOT import pgvector or ORM internals.

R-9. In Semantic Gloss and Semantic All modes, the language selectbox and language-role radio SHALL be disabled with explanatory help text, mirroring the existing FTS-mode idiom (language selectbox and role radio rendered with a disabled state and help text), because the semantic seam `search_semantic(mode, query, threshold, source_id, limit)` accepts ONLY `source_id` — no `language_id`, no `language_role`. The source filter SHALL remain live in semantic modes (`source_id` IS in the seam). A language/role value selected before switching to a semantic mode SHALL be preserved but inert — no false language constraint SHALL leak into result expectations.

## Items

### Item 1 (SC-1): Mode radio entries + captions for Semantic Gloss / Semantic All
- RED: behavioral AppTest asserting the mode radio lacks Semantic Gloss / Semantic All (fails)
- GREEN: extend mode list + SEARCH_MODE_CAPTIONS dict in `records.py`; session_state keys preserved; single selected-mode caption pattern unchanged
- verify: AppTest radio options + selected-mode captions, existing options unchanged
- commit: records.py mode list only

### Item 2 (SC-2): Threshold preference — slider+numeric coupled, persists, stable slot
- RED: widget test asserting no `semantic_threshold` preference control exists
- GREEN: render coupled slider+numeric control in the stable sidebar slot (below the mode caption, above the search/clear buttons) present in all modes with disabled widgets + help text in non-semantic modes; persist via set_preference(`records`,`semantic_threshold`); init from get_preference default `0.80`
- verify: AppTest two-way sync + persistence round-trip + stable-slot/disabled-in-non-semantic assertions
- commit: records.py (or ui_utils.py shared component) threshold control

### Item 3 (SC-3): Invalid threshold edit rejected + snap-back
- RED: test asserting invalid edit persists (no snap-back exists)
- GREEN: validation guard rejecting non-numeric/out-of-range with snap-back
- verify: AppTest invalid-input revert assertion
- commit: threshold control validation

### Item 4 (SC-4): Score badge/caption on semantic rows only, sorted order, inline in header line
- RED: test asserting no score badges render for any mode
- GREEN: consume `results` scores in the semantic rendering branch; render badges/captions descending, inline in the record card header line, fixed two decimals; skip for exact-match modes
- verify: AppTest badge presence/order/format and absence in exact-match modes
- commit: records.py record-card render loop

### Item 5 (SC-5): Pagination rank-once slice
- RED: test asserting page navigation re-invokes search or reorders results
- GREEN: slice the already-returned ranked list on page change; no service re-invocation
- verify: AppTest order-stability across navigation + invocation-count spy
- commit: records.py pagination slicing

### Item 6 (SC-6): Empty-state rendering per status payload
- RED: test asserting no crash-guard rendering exists for statuses
- GREEN: map each status + message to UI copy in the MAIN panel records area (st.info for informational states, st.warning for remedy-required states; zero-results path reuses the existing empty-batch branch); stale/none message names backfill remedy
- verify: AppTest mocked-payload per-status rendering assertions
- commit: records.py empty-state branch

### Item 7 (SC-7): Mode-switching regression + correctness
- RED: behavioral harness asserting semantic modes yield errors / existing modes regress
- GREEN: dispatch by SearchMode through `search_records` entry (widened Literal consumed); wire results per mode
- verify: behavioral AppTest harness (precedent `test_search_mode_ui_red.py`), result sets differ per mode, existing modes unchanged
- commit: dispatch wiring + regression test

### Item 8 (SC-8): Language filters disabled in semantic modes
- RED: AppTest asserting the language selectbox + language-role radio remain enabled in Semantic Gloss / Semantic All modes (no disabled-parity with the FTS idiom exists)
- GREEN: add the disabled state with explanatory help text for semantic modes, mirroring the FTS disabled-filter idiom; previously-selected value preserved but inert
- verify: AppTest disabled + help-text assertions in both semantic modes; existing modes' filter state unchanged
- commit: records.py language-filter disabled state

## Dependencies

| Reference | Relationship | Status |
|-----------|--------------|--------|
| Issue #36 (https://github.com/Brothertown-Language/snea-shoebox-editor/issues/36) | delivered the `search_semantic` seam + `SemanticSearchResult` v1 contract; seam verified stable on disk 2026-09-30 (SearchMode Literal + `_search_strategies` mapping in `linguistic_service.py`, `search_semantic` in `semantic_search_service.py`) | satisfied |
| Issue #400 (closed, merged) | provides existing records-page search panel state keys and rendering structure this spec extends | satisfied |
| `preference_service.py` | consumed as-is (`get_preference`/`set_preference` on PreferenceService, verified fresh) | satisfied |
| AppTest harness precedent (`test_search_mode_ui_red.py`) | test-harness pattern for behavioral UI SCs (streamlit.testing.v1.AppTest, mocked services); coordinate to avoid compounding #1347 red state | satisfied (pattern) |

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
| R-9 | SC-8 | 1 |

## Documentation Sources

| Source | Type | Location | Verification |
|--------|------|----------|--------------|
| SearchMode Literal + search_records | code | `src/services/linguistic_service.py` — SearchMode Literal (search mode union type, module top) and `search_records` entry (search dispatch entry point on LinguisticService) | live `rg` read 2026-09-28; re-verified stable names 2026-09-30 |
| records.py search panel (search input, mode radio, SEARCH_MODE_CAPTIONS dict, single selected-mode caption, FTS disabled-filter idiom, threshold slot) + record-card render loop (main panel: empty-batch block, per-record loop, card container, header line) + page_size string-preference idiom | code | `src/frontend/pages/records.py` (sidebar search-controls block; main-panel records render region; `SEARCH_MODE_CAPTIONS` dict; `current_page` session-state pagination keys) | live audit read 2026-09-30 (visual-audit.yaml) |
| Role guard + reprocess idiom (backfill remedy context) | code | `src/frontend/pages/table_maintenance.py` — admin role guard in `main()` and Data Reprocessing / Embedding Backfill section in `render_data_reprocessing_maintenance()` | live `sed` read 2026-09-28; re-verified stable names 2026-09-30 |
| PreferenceService get/set_preference | code | `src/services/preference_service.py` — `get_preference` and `set_preference` methods on PreferenceService | live `sed` read 2026-09-28; re-verified stable names 2026-09-30 |
| Parent seam contract + status enum | analysis artifact | `.issues/36/artifacts/concern-map.yaml`, `interface-compatibility.yaml` | verified on disk 2026-09-30 (filename confirmed in `.issues/36/artifacts/`) |
| Streamlit theme config (theme-awareness rationale) | config | `.streamlit/config.toml` (verified: no `[theme]` section) | verified 2026-09-30 (visual-audit.yaml) |
| #36 parent spec (db/embed) | spec | `.issues/36/spec.md` + https://github.com/Brothertown-Language/snea-shoebox-editor/issues/36 | fetched 2026-09-28 |

## Enforcement Gate

> **Enforcement gate:** All success criteria MUST pass before this spec is considered complete. Partial implementation is not permitted.

## Cost Frame

Cost is measured in defect-discovery-latency, not tool calls. Correctness is the only metric.

- **SC-1:** Behavioral radio test costs minutes of AppTest execution. Skipping means a broken mode dispatch ships and every semantic search session on the highest-traffic page hits a silently wrong result set — days-to-weeks of user-reported defect latency.
- **SC-2:** Persistence round-trip test costs minutes. Skipping means thresholds silently reset per session, making retrieval precision unpredictable across reruns — discovered only after linguists lose trust in tuned results.
- **SC-3:** Snap-back test costs minutes. Skipping means a typo silently corrupts a stored preference and degrades every future search for that user until manually diagnosed.
- **SC-4:** Rendering assertion costs minutes. Skipping means scores vanish or appear on wrong rows — discovered in stakeholder review after merge (10× DDL multiplier).
- **SC-5:** Order-stability harness costs minutes. Skipping means page navigation reorders results — the exact instability class that surfaces only after data volume grows, costing a full diagnosis of session-state flow days later.
- **SC-6:** Per-status rendering test costs minutes. Skipping means degraded states crash the page for real users when embeddings are missing — highest-frequency failure surface, found in production support tickets (1000× escalation).
- **SC-7:** Regression harness costs minutes. Skipping means breaking the four existing search modes on the app's primary page — discovered by linguists immediately, with full rework cycle.
- **SC-8:** Disabled-filter-parity test costs minutes. Skipping means language filters stay enabled-but-silently-ignored in semantic modes and linguists believe a language constraint is being applied when it is not — a silent wrong-result class found in support tickets.

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
| Language filter previously set → user switches to semantic mode | Language selectbox + language-role radio render disabled with help text; previously-selected value preserved but inert — no false language constraint leaks into result expectations | SC-8, R-9 |

## Change Control

| Date | Change | Reason | Authorized By |
|------|--------|--------|---------------|
| 2026-09-30 | Citation/anchor hygiene only — no SC, requirement, or scope changes: (1) SC-7 evidence citation corrected to `.issues/36/artifacts/testability-assessment.yaml` (validator-flagged filename drift `testability.yaml`; actual filename verified on disk 2026-09-30); (2) SC-6 D2-ITEM-5 citation redirected to its true location `tmp/issue-36/contracts/decompose-output.yaml` — anchor content verified on disk (unit "empty-state rendering per status payload", SC-U5), with volatile-scratch note; `.issues/36/artifacts/decompose-output.yaml` holds the D1 items only; (3) all line-number-only anchors replaced with stable symbol/section descriptions per the 080 cross-reference standard (SearchMode Literal + `search_records` entry in linguistic_service.py — post-#1390/#1391 drift :28/:391→:29/:387 confirmed live before replacing; `get_preference`/`set_preference` in preference_service.py; admin role guard in `main()` + `render_data_reprocessing_maintenance()` in table_maintenance.py; removed the Dependency-table :17,:37 ref) | Validation returned aggregate PASS with 3 non-blocking anchor warnings; developer directive "revise until 100% clean pass" | Developer 2026-09-30 |

| 2026-09-30 | Evidence-accuracy revision — no SC, requirement, or scope changes; verification-method terminology corrected and dependency status synced to reality: (1) SC-1..SC-8 "Verification Method" column relabeled from "Playwright" to "Behavioral pytest via streamlit AppTest" — the plan executed verification through streamlit.testing.v1.AppTest (the repo's own precedent harness `test_search_mode_ui_red.py` is AppTest-based), NOT a Playwright browser; the original label was factually wrong about what the harness is; (2) SC-5 method upgraded to name the invocation-count spy that actually verified the single-search-invocation invariant; (3) Dependencies table row for #36 corrected from "pending (this pipeline)" to "satisfied" — the seam was delivered and verified stable on disk during this pipeline; (4) audit note recorded: the two default-skipped tests in the full-suite count (test/ui/test_playwright_backfill_clickthrough.py, gated by SNEA_E2E=1 + live app on :8501) are #36 SC-13-owned live-server E2E, not this spec's items; they skipped identically at the pre-regression baseline before any #1385 edit | Developer directive "revise this spec to correct the incorrect" after E2E scope-drift finding 2026-09-30 | Developer 2026-09-30 |

---

*Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)*
*Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash) revised 2026-09-30*
*Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash) revised (citation/anchor hygiene) 2026-09-30*
*Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash) revised (evidence-accuracy) 2026-09-30*