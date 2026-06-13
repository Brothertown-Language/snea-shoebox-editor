# Spec: Records View: Left Panel Filter UX Improvements

STATUS: 1.2
CREATED: 2026-04-05

---

## Objective

Improve the user experience of the left panel filter controls in the Records view by making filter labels clearer and disabling inapplicable filters based on search mode.

---

## Dependencies

| Dependency | Type | Impact |
|------------|------|--------|
| **Spec #400** | Spec | MUST be implemented first — provides Headword and Gloss search modes that this spec depends on |
| Streamlit session state | Internal | Filter values stored in session state |
| LinguisticService.search_records() | Internal | Backend search method must handle language filters correctly |

**⚠️ CRITICAL: Spec #400 MUST be implemented before this spec.** The filter behavior changes depend on the search mode architecture from #400, particularly:
- Headword mode (PRIMARY \lx + PRIMARY \va) — language filters apply
- Gloss mode (PRIMARY \ge) — language filters apply
- Lexeme mode (ALL \lx, \va, \se, \cf, \ve) — language filters apply
- FTS mode (all fields) — language filters may be disabled based on implementation

---

## Problem Statement

**Current Issues:**

1. **Ambiguous Filter Labels**: The sources filter dropdown shows "All" which is unclear for end users who don't know what "All" refers to.

2. **Ambiguous Language Filter Label**: The languages filter dropdown also shows "All" with the same clarity issue.

3. **Language Role Filter Behavior**: The "Any | Primary | Secondary" language role radio buttons may have behavior that needs clarification or adjustment (specific behavior to be determined during investigation).

4. **Inapplicable Filters Active During FTS Searches**: When searching via headword+va (FTS mode with \va variants), the "Languages" and "Primary vs Secondary" filters do not apply correctly but remain enabled, confusing users.

**Impact:** Users are confused about what filters are available and whether filters apply to their current search mode.

---

## Context

**Location:** `src/frontend/pages/records.py` lines 177-206 (sidebar filter controls)

**Current Filter State:**
- Sources dropdown: Shows "All" as default option
- Languages dropdown: Shows "All" as default option  
- Language Role radio: "Any | Primary | Secondary" options
- Search modes: "Lexeme" and "FTS" (full-text search)

**Search Mode Behavior:**
- Lexeme mode: Searches headword (\lx) - Language filters apply
- FTS mode: Searches headword (\lx) AND variants (\va) - Language filters may not apply correctly

**Related Spec:** #400 adds Headword and Gloss search modes. This spec's filter changes will apply to those modes as well:
- Headword mode: PRIMARY \lx + PRIMARY \va — language filters SHOULD apply
- Gloss mode: PRIMARY \ge — language filters SHOULD apply

**Affected Code:**
- `src/frontend/pages/records.py` - Streamlit UI filter controls
- `src/services/linguistic_service.py` - Search query construction
- `tests/ui/mocks/records.py` - Mock UI (if filter behavior needs mocking)

---

## Constraints

| Constraint Type | Details |
|-----------------|---------|
| **Technical** | Must not break existing filter functionality for Lexeme mode searches |
| **UX** | Changes should improve clarity without breaking muscle memory |
| **Testing** | Existing tests should continue to pass; may need new tests for FTS + filter behavior |
| **Dependency** | Spec #400 must be implemented first |

---

## Affected Files

| File | Anchor | Description |
|------|--------|-------------|
| `src/frontend/pages/records.py` | `"Select Source"` selectbox (line ~177) | Sources dropdown with "All" option |
| `src/frontend/pages/records.py` | `"Select Language"` selectbox (line ~183) | Languages dropdown with "All" option |
| `src/frontend/pages/records.py` | `"Language Role"` radio (line ~189) | Language role filter radio buttons |
| `src/frontend/pages/records.py` | Sidebar filter section | Filter disable logic based on search mode |
| `src/services/linguistic_service.py` | `search_records()` method | Backend search logic with language filters |
| `tests/ui/mocks/records.py` | Mock filter controls | Test mock for UI filters |

---

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method |
|----|-----------|---------------|---------------------|
| SC-1 | Sources dropdown default label shows "All Sources" instead of "All" | `semantic` | Render records page, inspect sources dropdown default option |
| SC-2 | Languages dropdown default label shows "All Languages" instead of "All" | `semantic` | Render records page, inspect languages dropdown default option |
| SC-3 | Language role filter behavior is clarified/adjusted (specific fix TBD during investigation) | `behavioral` | Execute search with each language role option, verify expected results |
| SC-4 | Language and Language Role filters are disabled when search mode is FTS | `behavioral` | Select FTS mode, verify Language dropdown and Language Role radio are disabled |
| SC-5 | Existing Lexeme mode searches continue to work with language filters | `behavioral` | Execute Lexeme mode search with language filters, verify results are filtered |
| SC-6 | Clear visual indication when filters are disabled (grayed out, tooltip explanation) | `semantic` | Select FTS mode, verify disabled filters appear grayed out with tooltip |
| SC-7 | Headword and Gloss modes (from #400) work with language filters enabled | `behavioral` | Select Headword/Gloss mode, verify Language and Language Role filters are enabled |
| SC-8 | Empty search input returns all records / no error | `behavioral` | Submit empty search, verify all records returned without error |
| SC-9 | Unicode characters in filter values don't crash | `behavioral` | Enter Unicode filter values (e.g., accented chars, CJK), verify no crash |
| SC-10 | Active filter state persists across mode switches (Lexicon ↔ Grammar ↔ Culture) | `behavioral` | Set filter, switch modes, switch back, verify filter values preserved |

---

## Edge Cases

1. **User switches from FTS to Lexeme/Headword/Gloss**: Filters should re-enable with previous values preserved
2. **User has language filter selected then switches to FTS**: Selected filter should be visually disabled but not cleared
3. **URL query parameters**: If search mode is passed via URL, filters should respect the mode on load
4. **New search modes from #400**: Headword and Gloss modes should have language filters enabled

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking existing filter behavior | Low | Medium | Test both Lexeme and FTS modes thoroughly |
| User confusion about disabled filters | Medium | Low | Add helpful tooltips explaining why filters are disabled |
| Session state bugs with disabled filters | Low | Low | Session state logic is straightforward |
| Dependency on #400 | High | High | Implement #400 first, then this spec |

---

## Phase 1: Investigation and Filter Label Updates (Concern: User Clarity)

**Interdependencies:** NONE (independent of #400)

### Steps

1. ☐ Investigate current language role filter behavior to determine if behavior adjustment is needed
2. ☐ Update sources filter dropdown label from "All" to "All Sources"
3. ☐ Update languages filter dropdown label from "All" to "All Languages"
4. ☐ Update default name mapping in session state initialization

### TDD Cycle

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|-------|------------------|-------------------|----------|--------|
| Step 1 | Write test: assert language role filter returns expected results for each option | Investigate and document language role filter behavior; adjust if needed | Clean up investigation artifacts | Investigation findings |
| Step 2-3 | Write test: assert sources dropdown default is "All Sources" and languages dropdown default is "All Languages" | Update dropdown default label strings in `records.py` and session state init | Extract label strings to named constants if inline literals remain | Label updates + tests |
| Step 4 | Write test: assert session state initializes with "All Sources" / "All Languages" keys | Update session state initialization to use new default names | Verify no other code references old "All" default | Session state update + tests |

---

## Phase 2: FTS Filter Disabling (Concern: Search Mode UX)

**Interdependencies:** Spec #400 (needs Headword and Gloss modes to exist for correct mode detection)

### Steps

1. ☐ Add search mode detection in sidebar render to identify FTS mode (vs Lexeme, Headword, Gloss)
2. ☐ Disable Language dropdown when search mode is FTS (using Streamlit's `disabled` parameter)
3. ☐ Disable Language Role radio when search mode is FTS
4. ☐ Add tooltips explaining why filters are disabled in FTS mode
5. ☐ Verify session state preserves filter values when disabled

### TDD Cycle

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|-------|------------------|-------------------|----------|--------|
| Step 1 | Write test: assert search mode detection correctly identifies FTS vs Lexeme/Headword/Gloss | Add search mode detection logic in sidebar render | Extract mode detection to a helper function if inline logic grows | Mode detection + tests |
| Step 2-3 | Write test: assert Language dropdown and Language Role radio are disabled when mode is FTS | Add `disabled` parameter to Language dropdown and Language Role radio based on mode detection | Verify disabled state reads from single mode variable, not duplicated checks | FTS filter disabling + tests |
| Step 4 | Write test: assert tooltip text is present when filters are disabled in FTS mode | Add Streamlit tooltips to disabled filter widgets | Verify tooltip wording is consistent across disabled widgets | Tooltips + tests |
| Step 5 | Write test: assert filter values preserved in session state when switching to/from FTS mode | Verify session state preservation logic; add explicit preservation if needed | Consolidate session state preservation into single function | Session state preservation + tests |

---

## Phase 3: New Search Mode Filter Behavior (Concern: Headword/Gloss Support)

**Interdependencies:** Spec #400 (new search modes must exist)

### Steps

1. ☐ Verify Headword mode (from #400) has language filters ENABLED
2. ☐ Verify Gloss mode (from #400) has language filters ENABLED
3. ☐ Test language role filter with Headword and Gloss modes
4. ☐ Add tests for all four search modes with language filters

### TDD Cycle

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|-------|------------------|-------------------|----------|--------|
| Step 1-2 | Write test: assert Headword and Gloss modes have Language and Language Role filters enabled | Add enable-logic for Headword/Gloss modes (may already work if mode detection is correct) | Verify enable/disable logic is table-driven, not if-else chain | Headword/Gloss filter enablement + tests |
| Step 3 | Write test: assert language role filter returns correct results for Headword and Gloss modes | Verify or fix language role filter behavior with new modes | Merge test cases with Phase 1 language role tests if overlapping | Language role + mode integration + tests |
| Step 4 | Write test: comprehensive test matrix covering all 4 modes × language filter states | Add remaining test coverage for mode/filter combinations | Consolidate test fixtures for multi-mode testing | Full mode filter test coverage |

---

## Phase 4: Behavior Investigation (Concern: Backend Correctness)

**Interdependencies:** NONE (independent of frontend changes)

### Steps

1. ☐ Confirm whether language filters apply correctly in FTS mode (headword+va search)
2. ☐ If filters don't apply: document behavior and proceed with disabled state
3. ☐ If filters should apply: fix backend search logic to respect language filters in FTS mode
4. ☐ Add test coverage for FTS mode with language filters

### TDD Cycle

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|-------|------------------|-------------------|----------|--------|
| Step 1 | Write test: assert FTS search with language filter returns linguistically filtered results (or documents that filters don't apply) | Investigate FTS backend behavior with language filters applied | Clean up investigation test artifacts if they are throwaway | Investigation findings + documentation |
| Step 2-3 | Write test: if filters should apply, assert FTS search respects language filter; if not, assert FTS search ignores filter correctly | Fix backend or document behavior based on investigation | Ensure backend and frontend filter-disable logic are consistent | Backend fix or documented behavior + tests |
| Step 4 | Write test: FTS mode with language filters end-to-end test | Add integration test for FTS + language filter combination | Merge with Phase 2 FTS disable tests for coherent coverage | FTS language filter test coverage |

---

## Documentation Sources

| Source | Description | Version/Date | URL |
|--------|-------------|--------------|-----|
| Spec #400 — Headword/Gloss Search Modes | Adds Headword/Gloss search modes; Phase 3 dependency for filter behavior | Active | https://github.com/Brothertown-Language/snea-shoebox-editor/issues/400 |
| Extant Search/Records View | Current search mode behavior, filter controls, session state management | Current | `src/frontend/pages/records.py` |
| Existing Filter Logic | Language dropdown and Language Role radio binding | Current | `src/services/search_service.py` |

---

> **Approval Tracking**: Approvals are tracked via GitHub Issue comments (e.g., `AI: ✅ Approved: Phase 1`), NOT in the issue body. Issue body edits destroy history.

**⚠️ CRITICAL: Phase names MUST describe specific concerns, NOT generic activities.**
- ✅ Good: "Investigation and Filter Label Updates", "FTS Filter Disabling", "Headword/Gloss Support"
- ❌ Bad: "Implementation", "Testing", "Development"
