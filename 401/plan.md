# Plan: Records View Left Panel Filter UX Improvements

> **Compliance Requirement:** All steps and sub-steps in this document MUST be followed in order. Failure to comply with any step — including but not limited to verification gates, test phases, audit checkpoints, and review steps — will result in the feature branch being rejected and discarded, requiring a full rework from scratch and loss of all prior work. There is no valid reason to skip, compress, reorder, or omit any step. If a step appears redundant or unnecessary, follow it anyway — the cost of following an extra step is negligible compared to the cost of rework from a skipped step.

## Goal

Implement UX improvements for the Records view left panel filter controls:
1. Rename ambiguous dropdown defaults to explicit labels
2. Disable inapplicable language filters in FTS mode with tooltips
3. Replace vertical search/clear button stack with horizontal side-by-side layout
4. Add immediate `st.rerun()` to clear handler for instant visual feedback
5. Verify Headword and Gloss modes work correctly with language filters

## Architecture

- **Frontend:** Streamlit page (`src/frontend/pages/records.py`) — sidebar filter controls
- **Backend:** `src/services/linguistic_service.py` — search logic with language filters
- **Tests:** New test files for each concern area
- **State:** Streamlit session state for filter persistence across mode switches

## Tech Stack

- Python 3.12+
- Streamlit (UI framework)
- SQLAlchemy + PostgreSQL (backend search)
- pytest (testing)

## File Structure

| File | Responsibility |
|------|-------------|
| `src/frontend/pages/records.py` | UI filter controls, session state, search layout |
| `src/services/linguistic_service.py` | Backend search logic, language filter application |
| `tests/ui/test_records_filter_labels.py` | Phase 1: Label update tests |
| `tests/ui/test_records_fts_disable.py` | Phase 2: FTS disable behavior tests |
| `tests/ui/test_records_lexeme_regression.py` | Phase 2: Lexeme mode regression tests |
| `tests/ui/test_records_fts_tooltips.py` | Phase 2: Tooltip tests |
| `tests/ui/test_records_button_layout.py` | Phase 3: Button layout tests |
| `tests/ui/test_records_clear_behavior.py` | Phase 3: Clear behavior tests |
| `tests/ui/test_records_empty_search.py` | Phase 3: Empty search tests |
| `tests/ui/test_records_unicode.py` | Phase 3: Unicode safety tests |
| `tests/ui/test_records_state_persistence.py` | Phase 3: State persistence tests |
| `tests/ui/test_records_headword_gloss.py` | Phase 4: New search mode tests |
| `tests/ui/test_records_language_role.py` | Phase 1: Language role behavior tests |
| `tests/ui/mocks/records.py` | Test mocks for UI filter controls |

---

## Phase 1: Filter Label Updates

**Concern:** User Clarity
**Interdependencies:** NONE
**Files:** `src/frontend/pages/records.py`, `tests/ui/test_records_filter_labels.py`, `tests/ui/test_records_language_role.py`
**SCs covered:** SC-1, SC-2, SC-3

### Dispatch Table

| Gate | Dispatch Type | Blind? | Sub-Agent Type | Receives Context | SCs |
|------|--------------|--------|----------------|-----------------|-----|
| G1: sc-coherence-gate | sub-task | yes (blind) | general | {"task":"verify spec coherence for filter label updates","issue_number":401,"phase":1} | SC-1, SC-2, SC-3 |
| G2: pre-red-baseline | sub-task | yes (blind) | general | {"task":"establish baseline for filter label tests","issue_number":401,"phase":1} | SC-1, SC-2, SC-3 |
| G3: red-phase | sub-task | yes (blind) | general | {"task":"write failing tests for filter label updates","issue_number":401,"phase":1} | SC-1, SC-2, SC-3 |
| G4: red-doublecheck | sub-task | yes (blind) | general | {"task":"verify RED tests fail as expected","issue_number":401,"phase":1} | SC-1, SC-2, SC-3 |
| G5: post-red-enforcement | sub-task | yes (blind) | general | {"task":"verify RED structural gate","issue_number":401,"phase":1} | SC-1, SC-2, SC-3 |
| G6: green-phase | sub-task | yes (blind) | general | {"task":"implement filter label updates","issue_number":401,"phase":1} | SC-1, SC-2, SC-3 |
| G7: post-green-enforcement | sub-task | yes (blind) | general | {"task":"verify GREEN structural gate","issue_number":401,"phase":1} | SC-1, SC-2, SC-3 |
| G8: checkpoint-commit | inline | N/A | N/A | — | SC-1, SC-2, SC-3 |
| G9: structural-checks | sub-task | yes (blind) | general | {"task":"run lint/typecheck for Phase 1","issue_number":401,"phase":1} | SC-1, SC-2, SC-3 |
| G10: green-doublecheck | sub-task | yes (blind) | general | {"task":"verify GREEN intent matches spec","issue_number":401,"phase":1} | SC-1, SC-2, SC-3 |
| G11: green-vbc | sub-task | yes (blind) | general | {"task":"verify completion for Phase 1","issue_number":401,"phase":1} | SC-1, SC-2, SC-3 |
| G12: adversarial-audit | sub-task | yes (blind) | auditor_1/auditor_2 | {"task":"audit Phase 1 implementation","issue_number":401,"phase":1,"audit_phase":"verification-audit"} | SC-1, SC-2, SC-3 |
| G13: cross-validate | sub-task | yes (blind) | general | {"task":"cross-validate Phase 1 audit results","issue_number":401,"phase":1} | SC-1, SC-2, SC-3 |
| G14: regression-check | sub-task | yes (blind) | general | {"task":"run regression tests for Phase 1","issue_number":401,"phase":1} | SC-1, SC-2, SC-3 |
| G15: review-prep | sub-task | yes (blind) | general | {"task":"prepare review for Phase 1","issue_number":401,"phase":1} | SC-1, SC-2, SC-3 |
| G16: exec-summary | sub-task | yes (blind) | general | {"task":"completion summary for Phase 1","issue_number":401,"phase":1} | SC-1, SC-2, SC-3 |

### Concern Boundary

**Entering:** User-facing label clarity. This concern is purely cosmetic and does not affect search logic or data flow. It modifies display strings and session state initialization only.

**Leaving to Phase 2:** Filter disable logic. Phase 2 needs the new labels as the baseline state but adds mode-dependent behavior on top.

**Handoff point:** Session state keys for source and language filters must use the new default label values ("All Sources", "All Languages") as the initialized defaults.

### Tasks

- [ ] 1.1 Update sources dropdown options to use "All Sources" as the default option label
- [ ] 1.2 Update languages dropdown options to use "All Languages" as the default option label
- [ ] 1.3 Update session state initialization for `selected_source_id` default to "All Sources"
- [ ] 1.4 Update session state initialization for `selected_language_id` default to "All Languages"
- [ ] 1.5 Extract label strings to named constants at module level (e.g., `DEFAULT_SOURCE_LABEL = "All Sources"`)
- [ ] 1.6 Investigate language role filter behavior: verify that "Any", "Primary", and "Secondary" options correctly filter results in `search_records()`
- [ ] 1.7 Document language role filter behavior in code comments if non-obvious
- [ ] 1.8 Adjust language role filter labels if investigation reveals ambiguity

### RED/GREEN Conditions

**RED:** Sources dropdown shows "All" as default option; Languages dropdown shows "All" as default option; Language role filter behavior is undocumented or unclear.

**GREEN:** Sources dropdown shows "All Sources" as default option; Languages dropdown shows "All Languages" as default option; Language role filter behavior is verified and documented; All label strings extracted to named constants.

---

## Phase 2: FTS Filter Disabling

**Concern:** Search Mode UX
**Interdependencies:** NONE (frontend-only change; backend investigation deferred to Phase 5)
**Files:** `src/frontend/pages/records.py`, `tests/ui/test_records_fts_disable.py`, `tests/ui/test_records_lexeme_regression.py`, `tests/ui/test_records_fts_tooltips.py`
**SCs covered:** SC-4, SC-5, SC-6

### Dispatch Table

| Gate | Dispatch Type | Blind? | Sub-Agent Type | Receives Context | SCs |
|------|--------------|--------|----------------|-----------------|-----|
| G1: sc-coherence-gate | sub-task | yes (blind) | general | {"task":"verify spec coherence for FTS filter disabling","issue_number":401,"phase":2} | SC-4, SC-5, SC-6 |
| G2: pre-red-baseline | sub-task | yes (blind) | general | {"task":"establish baseline for FTS disable tests","issue_number":401,"phase":2} | SC-4, SC-5, SC-6 |
| G3: red-phase | sub-task | yes (blind) | general | {"task":"write failing tests for FTS filter disabling","issue_number":401,"phase":2} | SC-4, SC-5, SC-6 |
| G4: red-doublecheck | sub-task | yes (blind) | general | {"task":"verify RED tests fail as expected","issue_number":401,"phase":2} | SC-4, SC-5, SC-6 |
| G5: post-red-enforcement | sub-task | yes (blind) | general | {"task":"verify RED structural gate","issue_number":401,"phase":2} | SC-4, SC-5, SC-6 |
| G6: green-phase | sub-task | yes (blind) | general | {"task":"implement FTS filter disabling","issue_number":401,"phase":2} | SC-4, SC-5, SC-6 |
| G7: post-green-enforcement | sub-task | yes (blind) | general | {"task":"verify GREEN structural gate","issue_number":401,"phase":2} | SC-4, SC-5, SC-6 |
| G8: checkpoint-commit | inline | N/A | N/A | — | SC-4, SC-5, SC-6 |
| G9: structural-checks | sub-task | yes (blind) | general | {"task":"run lint/typecheck for Phase 2","issue_number":401,"phase":2} | SC-4, SC-5, SC-6 |
| G10: green-doublecheck | sub-task | yes (blind) | general | {"task":"verify GREEN intent matches spec","issue_number":401,"phase":2} | SC-4, SC-5, SC-6 |
| G11: green-vbc | sub-task | yes (blind) | general | {"task":"verify completion for Phase 2","issue_number":401,"phase":2} | SC-4, SC-5, SC-6 |
| G12: adversarial-audit | sub-task | yes (blind) | auditor_1/auditor_2 | {"task":"audit Phase 2 implementation","issue_number":401,"phase":2,"audit_phase":"verification-audit"} | SC-4, SC-5, SC-6 |
| G13: cross-validate | sub-task | yes (blind) | general | {"task":"cross-validate Phase 2 audit results","issue_number":401,"phase":2} | SC-4, SC-5, SC-6 |
| G14: regression-check | sub-task | yes (blind) | general | {"task":"run regression tests for Phase 2","issue_number":401,"phase":2} | SC-4, SC-5, SC-6 |
| G15: review-prep | sub-task | yes (blind) | general | {"task":"prepare review for Phase 2","issue_number":401,"phase":2} | SC-4, SC-5, SC-6 |
| G16: exec-summary | sub-task | yes (blind) | general | {"task":"completion summary for Phase 2","issue_number":401,"phase":2} | SC-4, SC-5, SC-6 |

### Concern Boundary

**Entering:** Mode-dependent filter state. This concern introduces behavioral logic that changes UI state based on search mode selection. It is independent of label changes (Phase 1) but builds on them.

**Leaving to Phase 3:** Search control layout. Phase 3 modifies the spatial arrangement of buttons without changing their behavioral logic. The disable state from Phase 2 must remain intact.

**Handoff point:** The `is_fts_mode` boolean (or equivalent mode detection variable) computed in this phase must be available for any future mode-dependent UI logic.

### Tasks

- [ ] 2.1 Add mode detection helper: derive `is_fts_mode = st.session_state.search_mode == "FTS"`
- [ ] 2.2 Add `disabled=is_fts_mode` parameter to Language dropdown (`st.selectbox`)
- [ ] 2.3 Add `disabled=is_fts_mode` parameter to Language Role radio (`st.radio`)
- [ ] 2.4 Add `help="Language filters do not apply to Full-Text Search mode"` tooltip to disabled Language dropdown
- [ ] 2.5 Add `help="Language role filters do not apply to Full-Text Search mode"` tooltip to disabled Language Role radio
- [ ] 2.6 Verify session state preserves `selected_language_id` and `language_role_filter` values when disabled (Streamlit default behavior)
- [ ] 2.7 Add explicit session state preservation guard if Streamlit does not preserve values for disabled widgets
- [ ] 2.8 Write regression test: verify Lexeme mode search with language filters continues to work
- [ ] 2.9 Write regression test: verify Headword mode search with language filters continues to work
- [ ] 2.10 Write regression test: verify Gloss mode search with language filters continues to work

### RED/GREEN Conditions

**RED:** Language dropdown and Language Role radio are enabled regardless of search mode; No tooltips explain disabled state.

**GREEN:** Language dropdown and Language Role radio are disabled when search mode is FTS; Enabled for Headword, Gloss, and Lexeme modes; Tooltips explain why filters are disabled; Session state preserves filter values across mode switches; All existing Lexeme mode tests pass.

---

## Phase 3: Search Control Layout and Clear Behavior

**Concern:** Search Input UX
**Interdependencies:** NONE
**Files:** `src/frontend/pages/records.py`, `tests/ui/test_records_button_layout.py`, `tests/ui/test_records_clear_behavior.py`, `tests/ui/test_records_empty_search.py`, `tests/ui/test_records_unicode.py`, `tests/ui/test_records_state_persistence.py`
**SCs covered:** SC-8, SC-9, SC-10, SC-11, SC-12

### Dispatch Table

| Gate | Dispatch Type | Blind? | Sub-Agent Type | Receives Context | SCs |
|------|--------------|--------|----------------|-----------------|-----|
| G1: sc-coherence-gate | sub-task | yes (blind) | general | {"task":"verify spec coherence for search control layout","issue_number":401,"phase":3} | SC-8, SC-9, SC-10, SC-11, SC-12 |
| G2: pre-red-baseline | sub-task | yes (blind) | general | {"task":"establish baseline for search control tests","issue_number":401,"phase":3} | SC-8, SC-9, SC-10, SC-11, SC-12 |
| G3: red-phase | sub-task | yes (blind) | general | {"task":"write failing tests for search control layout","issue_number":401,"phase":3} | SC-8, SC-9, SC-10, SC-11, SC-12 |
| G4: red-doublecheck | sub-task | yes (blind) | general | {"task":"verify RED tests fail as expected","issue_number":401,"phase":3} | SC-8, SC-9, SC-10, SC-11, SC-12 |
| G5: post-red-enforcement | sub-task | yes (blind) | general | {"task":"verify RED structural gate","issue_number":401,"phase":3} | SC-8, SC-9, SC-10, SC-11, SC-12 |
| G6: green-phase | sub-task | yes (blind) | general | {"task":"implement search control layout and clear behavior","issue_number":401,"phase":3} | SC-8, SC-9, SC-10, SC-11, SC-12 |
| G7: post-green-enforcement | sub-task | yes (blind) | general | {"task":"verify GREEN structural gate","issue_number":401,"phase":3} | SC-8, SC-9, SC-10, SC-11, SC-12 |
| G8: checkpoint-commit | inline | N/A | N/A | — | SC-8, SC-9, SC-10, SC-11, SC-12 |
| G9: structural-checks | sub-task | yes (blind) | general | {"task":"run lint/typecheck for Phase 3","issue_number":401,"phase":3} | SC-8, SC-9, SC-10, SC-11, SC-12 |
| G10: green-doublecheck | sub-task | yes (blind) | general | {"task":"verify GREEN intent matches spec","issue_number":401,"phase":3} | SC-8, SC-9, SC-10, SC-11, SC-12 |
| G11: green-vbc | sub-task | yes (blind) | general | {"task":"verify completion for Phase 3","issue_number":401,"phase":3} | SC-8, SC-9, SC-10, SC-11, SC-12 |
| G12: adversarial-audit | sub-task | yes (blind) | auditor_1/auditor_2 | {"task":"audit Phase 3 implementation","issue_number":401,"phase":3,"audit_phase":"verification-audit"} | SC-8, SC-9, SC-10, SC-11, SC-12 |
| G13: cross-validate | sub-task | yes (blind) | general | {"task":"cross-validate Phase 3 audit results","issue_number":401,"phase":3} | SC-8, SC-9, SC-10, SC-11, SC-12 |
| G14: regression-check | sub-task | yes (blind) | general | {"task":"run regression tests for Phase 3","issue_number":401,"phase":3} | SC-8, SC-9, SC-10, SC-11, SC-12 |
| G15: review-prep | sub-task | yes (blind) | general | {"task":"prepare review for Phase 3","issue_number":401,"phase":3} | SC-8, SC-9, SC-10, SC-11, SC-12 |
| G16: exec-summary | sub-task | yes (blind) | general | {"task":"completion summary for Phase 3","issue_number":401,"phase":3} | SC-8, SC-9, SC-10, SC-11, SC-12 |

### Concern Boundary

**Entering:** Spatial layout and immediate feedback. This concern modifies the visual arrangement of search controls and the responsiveness of the clear action. It is independent of Phase 2's disable logic.

**Leaving to Phase 4:** New search mode support. Phase 4 verifies that Headword and Gloss modes (already present in the code) work with language filters. The layout changes from Phase 3 must not interfere.

**Handoff point:** The search/clear button layout must remain side-by-side when Phase 4 adds mode-specific tests.

### Tasks

- [ ] 3.1 Replace sequential button blocks with `st.columns(2)` for search and clear buttons
- [ ] 3.2 Move search button (`icon="🔍"`) into column 1 with `use_container_width=True`
- [ ] 3.3 Move clear button (`icon="❌"`) into column 2 with `use_container_width=True`
- [ ] 3.4 Verify buttons render side-by-side at equal width
- [ ] 3.5 Add `st.rerun()` call immediately after `st.session_state.search_query = ""` in clear handler
- [ ] 3.6 Verify clear action resets `current_page = 1`
- [ ] 3.7 Add guard to prevent infinite rerun loops in clear handler
- [ ] 3.8 Verify empty search input returns all records without error
- [ ] 3.9 Verify Unicode characters in filter values do not crash the application
- [ ] 3.10 Verify active filter state persists across mode switches (set filter, switch mode, switch back, verify values)

### RED/GREEN Conditions

**RED:** Search and clear buttons are stacked vertically; Clear button does not immediately empty input; Empty search causes errors; Unicode crashes; State does not persist across mode switches.

**GREEN:** Search and clear buttons render side-by-side horizontally; Clear button immediately empties input and refreshes results; Empty search returns all records safely; Unicode filter values accepted; Filter state persists across mode switches.

---

## Phase 4: New Search Mode Filter Behavior

**Concern:** Headword/Gloss Support
**Interdependencies:** Spec #400 (Headword and Gloss modes must exist in codebase)
**Files:** `src/frontend/pages/records.py`, `tests/ui/test_records_headword_gloss.py`
**SCs covered:** SC-7

### Dispatch Table

| Gate | Dispatch Type | Blind? | Sub-Agent Type | Receives Context | SCs |
|------|--------------|--------|----------------|-----------------|-----|
| G1: sc-coherence-gate | sub-task | yes (blind) | general | {"task":"verify spec coherence for new search mode support","issue_number":401,"phase":4} | SC-7 |
| G2: pre-red-baseline | sub-task | yes (blind) | general | {"task":"establish baseline for Headword/Gloss mode tests","issue_number":401,"phase":4} | SC-7 |
| G3: red-phase | sub-task | yes (blind) | general | {"task":"write failing tests for Headword/Gloss mode filter behavior","issue_number":401,"phase":4} | SC-7 |
| G4: red-doublecheck | sub-task | yes (blind) | general | {"task":"verify RED tests fail as expected","issue_number":401,"phase":4} | SC-7 |
| G5: post-red-enforcement | sub-task | yes (blind) | general | {"task":"verify RED structural gate","issue_number":401,"phase":4} | SC-7 |
| G6: green-phase | sub-task | yes (blind) | general | {"task":"implement Headword/Gloss mode filter enable logic","issue_number":401,"phase":4} | SC-7 |
| G7: post-green-enforcement | sub-task | yes (blind) | general | {"task":"verify GREEN structural gate","issue_number":401,"phase":4} | SC-7 |
| G8: checkpoint-commit | inline | N/A | N/A | — | SC-7 |
| G9: structural-checks | sub-task | yes (blind) | general | {"task":"run lint/typecheck for Phase 4","issue_number":401,"phase":4} | SC-7 |
| G10: green-doublecheck | sub-task | yes (blind) | general | {"task":"verify GREEN intent matches spec","issue_number":401,"phase":4} | SC-7 |
| G11: green-vbc | sub-task | yes (blind) | general | {"task":"verify completion for Phase 4","issue_number":401,"phase":4} | SC-7 |
| G12: adversarial-audit | sub-task | yes (blind) | auditor_1/auditor_2 | {"task":"audit Phase 4 implementation","issue_number":401,"phase":4,"audit_phase":"verification-audit"} | SC-7 |
| G13: cross-validate | sub-task | yes (blind) | general | {"task":"cross-validate Phase 4 audit results","issue_number":401,"phase":4} | SC-7 |
| G14: regression-check | sub-task | yes (blind) | general | {"task":"run regression tests for Phase 4","issue_number":401,"phase":4} | SC-7 |
| G15: review-prep | sub-task | yes (blind) | general | {"task":"prepare review for Phase 4","issue_number":401,"phase":4} | SC-7 |
| G16: exec-summary | sub-task | yes (blind) | general | {"task":"completion summary for Phase 4","issue_number":401,"phase":4} | SC-7 |

### Concern Boundary

**Entering:** Verification of existing search mode compatibility. Headword and Gloss modes already exist in the codebase. This phase verifies they interact correctly with language filters rather than introducing new modes.

**Leaving to Phase 5:** Backend investigation. Phase 5 investigates whether language filters should apply to FTS backend queries. The enable/disable logic from this phase defines the frontend contract.

**Handoff point:** The mode detection logic must correctly identify Headword and Gloss as non-FTS modes (i.e., language filters enabled).

### Tasks

- [ ] 4.1 Verify Headword mode has language filters enabled (mode detection excludes it from FTS disable)
- [ ] 4.2 Verify Gloss mode has language filters enabled (mode detection excludes it from FTS disable)
- [ ] 4.3 Verify language role filter works correctly with Headword mode
- [ ] 4.4 Verify language role filter works correctly with Gloss mode
- [ ] 4.5 Add comprehensive test matrix: all 4 modes × language filter states
- [ ] 4.6 Verify table-driven mode detection (not if-else chain) for maintainability

### RED/GREEN Conditions

**RED:** Headword or Gloss mode incorrectly disables language filters; Language role filter does not work with Headword/Gloss modes.

**GREEN:** Headword and Gloss modes have language filters enabled; Language role filter returns correct results for Headword and Gloss modes; Mode detection is table-driven (dictionary/map, not if-else chain).

---

## Phase 5: Behavior Investigation

**Concern:** Backend Correctness
**Interdependencies:** NONE (frontend changes from Phases 1-4 may inform investigation scope)
**Files:** `src/services/linguistic_service.py`, `tests/integration/test_fts_language_filters.py`
**SCs covered:** (Investigation phase — no direct SC binding; findings inform future specs if needed)

### Dispatch Table

| Gate | Dispatch Type | Blind? | Sub-Agent Type | Receives Context | SCs |
|------|--------------|--------|----------------|-----------------|-----|
| G1: sc-coherence-gate | sub-task | yes (blind) | general | {"task":"verify investigation scope coherence","issue_number":401,"phase":5} | — |
| G2: pre-red-baseline | sub-task | yes (blind) | general | {"task":"establish baseline for FTS backend investigation","issue_number":401,"phase":5} | — |
| G3: red-phase | sub-task | yes (blind) | general | {"task":"write investigation tests for FTS language filters","issue_number":401,"phase":5} | — |
| G4: red-doublecheck | sub-task | yes (blind) | general | {"task":"verify investigation tests establish current behavior","issue_number":401,"phase":5} | — |
| G5: post-red-enforcement | sub-task | yes (blind) | general | {"task":"verify RED structural gate","issue_number":401,"phase":5} | — |
| G6: green-phase | sub-task | yes (blind) | general | {"task":"document or fix FTS backend language filter behavior","issue_number":401,"phase":5} | — |
| G7: post-green-enforcement | sub-task | yes (blind) | general | {"task":"verify GREEN structural gate","issue_number":401,"phase":5} | — |
| G8: checkpoint-commit | inline | N/A | N/A | — | — |
| G9: structural-checks | sub-task | yes (blind) | general | {"task":"run lint/typecheck for Phase 5","issue_number":401,"phase":5} | — |
| G10: green-doublecheck | sub-task | yes (blind) | general | {"task":"verify GREEN intent matches investigation goals","issue_number":401,"phase":5} | — |
| G11: green-vbc | sub-task | yes (blind) | general | {"task":"verify completion for Phase 5","issue_number":401,"phase":5} | — |
| G12: adversarial-audit | sub-task | yes (blind) | auditor_1/auditor_2 | {"task":"audit Phase 5 investigation","issue_number":401,"phase":5,"audit_phase":"verification-audit"} | — |
| G13: cross-validate | sub-task | yes (blind) | general | {"task":"cross-validate Phase 5 audit results","issue_number":401,"phase":5} | — |
| G14: regression-check | sub-task | yes (blind) | general | {"task":"run regression tests for Phase 5","issue_number":401,"phase":5} | — |
| G15: review-prep | sub-task | yes (blind) | general | {"task":"prepare review for Phase 5","issue_number":401,"phase":5} | — |
| G16: exec-summary | sub-task | yes (blind) | general | {"task":"completion summary for Phase 5","issue_number":401,"phase":5} | — |

### Concern Boundary

**Entering:** Backend investigation. This concern examines whether `search_records()` applies language filters in FTS mode. It may result in documentation, a backend fix, or confirmation that current behavior is correct.

**Leaving:** None — this is the final phase.

**Handoff point:** Investigation findings documented in code comments or a new spec issue if backend changes are needed.

### Tasks

- [ ] 5.1 Investigate `search_records()` method to determine if `language_id` and `language_role` parameters affect FTS query results
- [ ] 5.2 If language filters do NOT apply in FTS mode: document this behavior with code comments
- [ ] 5.3 If language filters SHOULD apply in FTS mode: fix backend logic to respect language filters in FTS queries
- [ ] 5.4 Add integration test for FTS mode with language filters (end-to-end)
- [ ] 5.5 Ensure frontend disable state (Phase 2) matches backend behavior

### RED/GREEN Conditions

**RED:** Unknown whether language filters apply to FTS mode; Frontend disable logic may contradict backend behavior.

**GREEN:** Language filter application in FTS mode is understood and documented; Frontend and backend behavior are consistent; Integration test verifies FTS + language filter behavior.

---

## Per-Unit Pipeline Gate Tables

### Phase 1 Unit: Filter Label Updates

| Gate | Name | Exit Criterion (unit-specific) |
|------|------|-------------------------------|
| 1 | sc-coherence-gate | Spec SC-1/SC-2/SC-3 are coherent with codebase state |
| 2 | pre-red-baseline | Baseline test captures current "All" labels |
| 3 | red-phase | Test asserts "All Sources" / "All Languages" labels exist — FAILS |
| 4 | red-doublecheck | RED test fails as expected (labels not yet updated) |
| 5 | green-phase | Source/lang labels updated to "All Sources" / "All Languages" |
| 6 | checkpoint-commit | Phase 1 changes committed |
| 7 | structural-checks | Lint/typecheck pass on modified files |
| 8 | green-doublecheck | GREEN test passes — labels match spec |
| 9 | green-vbc | SC-1/SC-2 verified PASS |
| 10 | adversarial-audit | No orphan SCs; no scope creep |
| 11 | cross-validate | Dual-auditor consensus PASS |
| 12 | regression-check | No regressions in existing tests |
| 13 | review-prep | Phase 1 ready for review |
| 14 | exec-summary | Phase 1 completion reported |

### Phase 2 Unit: FTS Filter Disabling

| Gate | Name | Exit Criterion (unit-specific) |
|------|------|-------------------------------|
| 1 | sc-coherence-gate | Spec SC-4/SC-5/SC-6 are coherent with codebase state |
| 2 | pre-red-baseline | Baseline test captures current always-enabled behavior |
| 3 | red-phase | Test asserts disabled state in FTS mode — FAILS |
| 4 | red-doublecheck | RED test fails as expected (no disable logic yet) |
| 5 | green-phase | Disable logic added for FTS mode; tooltips added |
| 6 | checkpoint-commit | Phase 2 changes committed |
| 7 | structural-checks | Lint/typecheck pass on modified files |
| 8 | green-doublecheck | GREEN test passes — disabled state matches spec |
| 9 | green-vbc | SC-4/SC-5/SC-6 verified PASS |
| 10 | adversarial-audit | No orphan SCs; no scope creep |
| 11 | cross-validate | Dual-auditor consensus PASS |
| 12 | regression-check | Lexeme/Headword/Gloss mode regression tests pass |
| 13 | review-prep | Phase 2 ready for review |
| 14 | exec-summary | Phase 2 completion reported |

### Phase 3 Unit: Search Control Layout

| Gate | Name | Exit Criterion (unit-specific) |
|------|------|-------------------------------|
| 1 | sc-coherence-gate | Spec SC-8 through SC-12 are coherent with codebase state |
| 2 | pre-red-baseline | Baseline test captures vertical button layout and delayed clear |
| 3 | red-phase | Test asserts horizontal layout and immediate clear — FAILS |
| 4 | red-doublecheck | RED test fails as expected (layout not yet updated) |
| 5 | green-phase | Buttons placed in columns; `st.rerun()` added to clear handler |
| 6 | checkpoint-commit | Phase 3 changes committed |
| 7 | structural-checks | Lint/typecheck pass on modified files |
| 8 | green-doublecheck | GREEN test passes — layout and clear behavior match spec |
| 9 | green-vbc | SC-8 through SC-12 verified PASS |
| 10 | adversarial-audit | No orphan SCs; no scope creep |
| 11 | cross-validate | Dual-auditor consensus PASS |
| 12 | regression-check | No regressions in existing tests |
| 13 | review-prep | Phase 3 ready for review |
| 14 | exec-summary | Phase 3 completion reported |

### Phase 4 Unit: New Search Mode Filter Behavior

| Gate | Name | Exit Criterion (unit-specific) |
|------|------|-------------------------------|
| 1 | sc-coherence-gate | Spec SC-7 is coherent with codebase state |
| 2 | pre-red-baseline | Baseline test captures current mode detection behavior |
| 3 | red-phase | Test asserts Headword/Gloss have filters enabled — FAILS if not |
| 4 | red-doublecheck | RED test fails as expected (if detection incorrect) |
| 5 | green-phase | Mode detection table includes Headword/Gloss as enabled |
| 6 | checkpoint-commit | Phase 4 changes committed |
| 7 | structural-checks | Lint/typecheck pass on modified files |
| 8 | green-doublecheck | GREEN test passes — mode detection correct |
| 9 | green-vbc | SC-7 verified PASS |
| 10 | adversarial-audit | No orphan SCs; no scope creep |
| 11 | cross-validate | Dual-auditor consensus PASS |
| 12 | regression-check | All 4 mode regression tests pass |
| 13 | review-prep | Phase 4 ready for review |
| 14 | exec-summary | Phase 4 completion reported |

### Phase 5 Unit: Behavior Investigation

| Gate | Name | Exit Criterion (unit-specific) |
|------|------|-------------------------------|
| 1 | sc-coherence-gate | Investigation scope is coherent with codebase |
| 2 | pre-red-baseline | Baseline documents current FTS backend behavior |
| 3 | red-phase | Investigation test establishes current behavior |
| 4 | red-doublecheck | RED test characterizes current behavior accurately |
| 5 | green-phase | Backend behavior documented or fixed; consistency verified |
| 6 | checkpoint-commit | Phase 5 changes committed |
| 7 | structural-checks | Lint/typecheck pass on modified files |
| 8 | green-doublecheck | GREEN matches investigation goals |
| 9 | green-vbc | Backend behavior understood and consistent with frontend |
| 10 | adversarial-audit | Investigation is thorough and conclusions are evidenced |
| 11 | cross-validate | Dual-auditor consensus PASS |
| 12 | regression-check | No regressions in existing tests |
| 13 | review-prep | Phase 5 ready for review |
| 14 | exec-summary | Phase 5 completion reported |

---

## Inter-Phase Handoff Protocol

Between phases, the orchestrator MUST:

1. Update Z3 state file with completed phase gate states
2. Run `solve check` to confirm dependency contract still SAT
3. Verify checkpoint tag exists for completed phase
4. Append lifecycle manifest event for phase completion

### Phase Dependency Ordering

```yaml
# .issues/401/dependency-ordering-verification/ordering.yaml
phase_dependencies:
  - phase: Phase_1_Filter_Label_Updates
    depends_on: []
    constraints:
      - "Phase_1_has_no_prerequisites"
  - phase: Phase_2_FTS_Filter_Disabling
    depends_on: [Phase_1_Filter_Label_Updates]
    constraints:
      - "Phase_2_starts_after_Phase_1_completes"
  - phase: Phase_3_Search_Control_Layout
    depends_on: [Phase_1_Filter_Label_Updates]
    constraints:
      - "Phase_3_starts_after_Phase_1_completes"
  - phase: Phase_4_New_Search_Mode_Filter_Behavior
    depends_on: [Phase_2_FTS_Filter_Disabling, Phase_3_Search_Control_Layout]
    constraints:
      - "Phase_4_starts_after_Phase_2_and_Phase_3_complete"
  - phase: Phase_5_Behavior_Investigation
    depends_on: [Phase_4_New_Search_Mode_Filter_Behavior]
    constraints:
      - "Phase_5_starts_after_Phase_4_completes"
```

**Dependency note:** Phase 2 and Phase 3 are independent after Phase 1. They may execute in parallel if the orchestrator supports parallel dispatch. Phase 4 depends on both Phase 2 (disable logic) and Phase 3 (layout stability). Phase 5 depends on Phase 4 (mode detection correctness).

### Z3 Contract Verification

Run contract generation and verification after plan creation:

```bash
# Generate per-phase Z3 contracts
mkdir -p .issues/401/dependency-ordering-verification/
cat > .issues/401/dependency-ordering-verification/phase-contract.z3 << 'CONTRACT'
; Phase dependency contract
(declare-const Phase_1 Bool)
(declare-const Phase_2 Bool)
(declare-const Phase_3 Bool)
(declare-const Phase_4 Bool)
(declare-const Phase_5 Bool)

(assert (=> Phase_2 Phase_1))
(assert (=> Phase_3 Phase_1))
(assert (=> Phase_4 (and Phase_2 Phase_3)))
(assert (=> Phase_5 Phase_4))

(check-sat)
CONTRACT
```

Expected result: `sat`

---

## SC Coverage Cross-Reference

| SC | Phase | Evidence Type | Verification Gate | Test File |
|----|-------|---------------|-------------------|-----------|
| SC-1 | Phase 1 | semantic | red-green | test_records_filter_labels.py |
| SC-2 | Phase 1 | semantic | red-green | test_records_filter_labels.py |
| SC-3 | Phase 1 | behavioral | red-green | test_records_language_role.py |
| SC-4 | Phase 2 | behavioral | pre-commit | test_records_fts_disable.py |
| SC-5 | Phase 2 | behavioral | pre-commit | test_records_lexeme_regression.py |
| SC-6 | Phase 2 | semantic | pre-commit | test_records_fts_tooltips.py |
| SC-7 | Phase 4 | behavioral | pre-commit | test_records_headword_gloss.py |
| SC-8 | Phase 3 | behavioral | pre-commit | test_records_empty_search.py |
| SC-9 | Phase 3 | behavioral | ci | test_records_unicode.py |
| SC-10 | Phase 3 | behavioral | pre-commit | test_records_state_persistence.py |
| SC-11 | Phase 3 | semantic | red-green | test_records_button_layout.py |
| SC-12 | Phase 3 | behavioral | red-green | test_records_clear_behavior.py |

---

## Explicit Non-Goals (Preserved from Spec)

- Backend search algorithm changes — out of scope unless investigation reveals actual bugs
- New search mode creation — Headword and Gloss modes are already present in codebase
- Internationalization of labels — English labels only for this release

## Regression Invariants (Preserved from Spec)

1. Existing Lexeme mode authentication flows MUST continue to work with current filter values
2. All existing public API signatures in `linguistic_service.py` MUST remain unchanged
3. Database schema for filter storage MUST NOT be modified

> **Compliance Requirement:** All steps and sub-steps in this document MUST be followed in order. Failure to comply with any step — including but not limited to verification gates, test phases, audit checkpoints, and review steps — will result in the feature branch being rejected and discarded, requiring a full rework from scratch and loss of all prior work. There is no valid reason to skip, compress, reorder, or omit any step. If a step appears redundant or unnecessary, follow it anyway — the cost of following an extra step is negligible compared to the cost of rework from a skipped step.

---

Created plan at `.issues/401/plan.md` for [Brothertown-Language/snea-shoebox-editor#401](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/401) (Records View Left Panel Filter UX Improvements). 5 phases across 5 items.

🤖 Co-authored with AI: OpenCode (ollama-cloud/kimi-k2.6)
