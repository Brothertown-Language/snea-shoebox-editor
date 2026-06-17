# Plan: Replace Focused/Broad labels with dynamic search mode caption

## Issue

[#1321 [SPEC-FIX] Replace Focused/Broad grouping with dynamic search mode caption](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1321)

## Summary

Replace the static "── Focused ──" / "── Broad ──" group labels and the dense help-text block in the Records view search panel with a single dynamic caption line that explains the currently selected search mode in plain language.

## Phase 1: UI Label Replacement

### Concern Boundary
Purely cosmetic UI change in `src/frontend/pages/records.py`. No backend logic affected.

### Tasks

#### Task 1: RED — Verify current labels exist
**Goal:** Confirm the current implementation matches the spec's "Before" state.

1. Open `src/frontend/pages/records.py`
2. Verify lines 199–211 contain:
   - `st.markdown("**── Focused ──**")` (line 199)
   - `st.radio(...)` with search modes (lines 200–207)
   - `st.markdown("**── Broad ──**")` (line 208)
   - Help text block: `"HW: \\lx+\\va (primary) | Gloss: \\ge (primary) | LX: all markers | FTS: all fields"` (lines 209–211)
3. **Expected result:** All four elements confirmed present. If any element is missing, HALT and report drift.

#### Task 2: GREEN — Replace labels with dynamic caption
**Goal:** Implement the dynamic caption as specified.

1. Define a caption mapping dictionary:
   ```python
   SEARCH_MODE_CAPTIONS = {
       "Headword": "Algonquian headwords and variants (\\lx, \\va)",
       "Gloss": "Primary English glosses (\\ge)",
       "Lexeme": "All Algonquian terms",
       "FTS": "Every field",
   }
   ```
2. Remove lines 199 and 208 (`st.markdown("**── Focused ──**")` and `st.markdown("**── Broad ──**")`).
3. Replace lines 209–211 (the help text block) with:
   ```python
   st.caption(SEARCH_MODE_CAPTIONS.get(st.session_state.search_mode, ""))
   ```
   placed immediately after the `st.radio(...)` block.
4. Ensure the Search and Clear buttons (lines 212–218) remain in the same position/functionality.

#### Task 3: REFACTOR — Verify layout and accessibility
**Goal:** Confirm the UI matches the spec's "After" state.

1. Verify the radio group renders without group labels.
2. Verify the caption displays below the radio group.
3. Verify caption text updates when search mode changes.
4. Verify caption text matches the approved table exactly:

   | Mode | Caption |
   |------|---------|
   | Headword | Algonquian headwords and variants (\\lx, \\va) |
   | Gloss | Primary English glosses (\\ge) |
   | Lexeme | All Algonquian terms |
   | FTS | Every field |

5. Verify Search and Clear buttons remain functional.

### Files Modified

- `src/frontend/pages/records.py`

### Success Criteria Mapping

| SC | Criterion | How This Plan Verifies |
|----|-----------|------------------------|
| SC-1 | "Focused" label removed from search panel | Task 3, step 1 |
| SC-2 | "Broad" label and help-text block removed | Task 3, step 1 |
| SC-3 | Dynamic caption appears below radio group for all four modes | Task 3, steps 2–3 |
| SC-4 | Caption text matches approved table for each mode | Task 3, step 4 |
| SC-5 | Search and Clear buttons remain functional | Task 3, step 5 |

## Commit Message

```
feat(records): replace Focused/Broad labels with dynamic search mode caption

Replace static "── Focused ──" / "── Broad ──" group labels and dense
help-text block with a single dynamic caption below the search-mode radio
group. Caption updates to explain the currently selected mode in plain
language.

Fixes #1321
```

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Caption text wraps awkwardly on narrow screens | Low | Low | `st.caption()` uses smaller font; monitor during review |
| Streamlit `st.caption` styling differs from markdown | Low | Low | Verify visually; fallback to `st.markdown("*italic*")` if needed |

## Notes

- Single-task plan — no sub-issues required.
- No backend or API changes.
- No tests to update (frontend is manually verified).

🤖 Co-authored with AI: OpenCode (ollama-cloud/kimi-k2.6)
