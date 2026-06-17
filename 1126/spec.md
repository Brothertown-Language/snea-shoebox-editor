---
issue_number: 1126
title: '[Task: #400] Phase 5 — Search Mode UI: Vertical Radio with Grouping'
state: open
repo: Brothertown-Language/snea-shoebox-editor
created_at: 2026-04-22T04:08:37Z
updated_at: 2026-04-22T04:08:37Z
labels:
  - task
  - needs-approval
promotion_type: retroactive_import
---

STATUS: 1 (DRAFT)
CREATED: 2026-04-22
PARENT: #400 (Phase 5)

> **Full spec: [Issue #1126](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1126)**

## Executive Summary

Phase 5 frontend implementation for #400: add Headword and Gloss search modes. The search mode selector changes from a 2-option horizontal radio to a 4-option vertical radio with Focused/Broad grouping, Headword as the new default, and active mode name in the search results header. Lexeme and FTS modes remain UNCHANGED in behavior — only their UI representation changes (moved to Broad group, buttons reflow below radio group).

## Problem

The current search mode selector is a 2-option horizontal radio (`Lexeme` / `FTS`) occupying a narrow column alongside search/clear buttons. Adding Headword and Gloss modes increases the option count to 4, which does not fit the horizontal layout. The current UI also lacks:
- Visual grouping to distinguish focused modes (Headword, Gloss) from broad modes (Lexeme, FTS)
- Any indicator of which search mode is active in the results header
- Help text explaining what each mode searches
- Space for search/clear buttons (currently crammed into 0.15-width columns)

These gaps make the 4-mode selector confusing and hard to use in the current layout.

## Context

### Current UI Layout

```
[Search...] [🔍][❌]       ← search_term input + buttons in columns
(Lexeme)  (FTS)            ← horizontal radio at column width 0.7
Search (15 records)         ← no mode name in header
```

| Element | Current Behavior |
|---------|-----------------|
| Radio layout | Horizontal, 2 options: `["Lexeme", "FTS"]` |
| Default mode | `"Lexeme"` |
| Search header | `"Search (N records)"` — no mode name |
| Mode column width | 0.7 (shared row with search/clear buttons) |
| Help text | None |

### Target UI Layout

```
Search: Headword (15 records)      ← header shows mode name + count

── Focused ──                      ← grouping separator
○ Headword                         ← NEW default
○ Gloss
── Broad ──                        ← grouping separator  
○ Lexeme
○ FTS

HW: \lx+\va (primary) | Gloss: \ge (primary) | LX: all markers | FTS: all fields
                                    ← help text below radio

[🔍 Search] [❌ Clear]             ← full-width buttons below
```

### Implementation Approach: Single Vertical Radio with Markdown Separators

Use one `st.radio` with the four options in order and markdown separators rendered immediately before and after the radio to create the Focused/Broad grouping illusion. This avoids the state-synchronization complexity of two synchronized radios and keeps the implementation minimal.

```python
st.markdown("── Focused ──")
st.radio(
    "Search Mode",
    ["Headword", "Gloss", "Lexeme", "FTS"],
    index=0,
    key="search_mode_radio",
    label_visibility="collapsed",
    on_change=on_mode_change,
)
st.markdown("── Broad ──")
```

**Note:** Because the separators sit outside the widget, they appear as static text above the first option and below the last option. The four options themselves remain a single contiguous list.

## Constraints

| Constraint | Details |
|------------|---------|
| **Lexeme/FTS UNCHANGED** | No changes to Lexeme or FTS search behavior — only UI position and layout change |
| **Headword new default** | New sessions and search clears default to `"Headword"` |
| **Session state persists** | `st.session_state.search_mode` must survive pagination and `st.rerun()` |
| **Existing tests pass** | All existing search tests must continue to pass unchanged |
| **Backend untouched** | No changes to `src/services/linguistic_service.py` — backend already handles all 4 modes (see #1305) |

## Affected Files

| File | Change |
|------|--------|
| `src/frontend/pages/records.py` | Search mode UI: vertical radio, grouping, default change, header update, help text, button reflow |

## Success Criteria

| SC | Criterion | Evidence Type | Verification Method |
|----|-----------|---------------|---------------------|
| SC-1 | New session/search defaults to Headword | `behavioral` | `uv run pytest tests/frontend/...::test_search_defaults_to_headword` |
| SC-2 | Vertical radio shows 4 options with grouping separators | `behavioral` | `uv run pytest tests/frontend/...::test_vertical_radio_shows_four_options` |
| SC-3 | Selecting Headword triggers HeadwordSearchEntry search | `behavioral` | `uv run pytest tests/frontend/...::test_selecting_headword_triggers_headword_search` |
| SC-4 | Selecting Gloss triggers GlossSearchEntry search | `behavioral` | `uv run pytest tests/frontend/...::test_selecting_gloss_triggers_gloss_search` |
| SC-5 | Selecting Lexeme preserves existing SearchEntry join behavior | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_search_records_lexeme_mode_unchanged` |
| SC-6 | Search results header shows mode name and count when search_term is truthy | `behavioral` | `uv run pytest tests/frontend/...::test_header_shows_mode_name_and_count` |
| SC-7 | Help text visible below radio grouping | `string` | `grep -c "HW:.*Gloss.*LX.*FTS" src/frontend/pages/records.py` |
| SC-8 | Focused/Broad separators render correctly | `behavioral` | `uv run pytest tests/frontend/...::test_grouping_separators_render` |
| SC-9 | Search/clear buttons full width below radio, not 0.15 columns | `behavioral` | `uv run pytest tests/frontend/...::test_search_buttons_full_width_below_radio` |
| SC-10 | Search mode persists across pagination | `behavioral` | `uv run pytest tests/frontend/...::test_mode_persists_across_pagination` |
| SC-11 | All existing search and export tests continue to pass | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py -v` |

## Edge Cases

| Edge Case | Handling |
|-----------|----------|
| Empty search term with Headword mode | Returns all records (no filter applied — behavior unchanged from Lexeme) |
| Rapid mode switching | Session state updates synchronously via `on_change` callback; no debounce needed |
| Session state cleared (cache clear) | Falls back to `"Headword"` default in initialization block |
| No records match in Headword/Gloss mode | Returns empty results; header shows `"Search: Headword (0 records)"` |

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Existing Lexeme/FTS search broken by default change | Low | High | Regression tests verifying Lexeme and FTS modes unchanged (SC-5, SC-11) |
| Session state key collision | Low | Low | Continue using existing key `search_mode_radio`; no new keys required |

## Dependencies

| Dependency | Type | Impact |
|------------|------|--------|
| Phase 1 (Schema) — #1303 | Hard | Tables must exist |
| Phase 2 (Indexing) — #1304 | Hard | Tables must be populated |
| Phase 3 (Migration) — #1306 | Hard | Existing data must be backfilled |
| Phase 4 (Search) — #1305 | Hard | Backend must support all 4 search modes |

## Explicit Non-Goals

| Non-Goal | Rationale |
|----------|-----------|
| No backend changes | Backend already handles all 4 modes (Phase 4 complete) |
| No new database tables | All search tables created in Phases 1-3 |
| No styling beyond Streamlit defaults | Grouping via markdown separators; no custom CSS |
| No keyboard shortcuts | Not requested in spec scope |
| No two-radio widget synchronization | Single-radio approach avoids this complexity |

## Decision Ledger

| DEC-ID | Decision | Rationale | Alternatives Considered |
|--------|----------|-----------|------------------------|
| DEC-1 | Vertical radio layout with Focused/Broad grouping | 4 options do not fit horizontal layout; grouping clarifies mode categories | Horizontal with dropdown (rejected: hidden options), horizontal with icons (rejected: over-engineered) |
| DEC-2 | Headword as default mode | Primary search use case per user request; Lexeme default was arbitrary | Keep Lexeme default (rejected: contradicts user need for focused search) |
| DEC-3 | Buttons below radio group (full width) | Separates mode selection from action; gives radio group full sidebar width | Keep buttons inline with search bar (rejected: too narrow at 0.15 column width) |
| DEC-4 | Single vertical radio with markdown separators (Approach B) | Avoids state-synchronization complexity of two radios; minimal implementation | Two-radio Approach A (rejected: fragile deselection/sync logic) |

## Documentation Sources

| Source | Description | Version/Date | URL |
|--------|-------------|--------------|-----|
| Spec #400 — Headword/Gloss Search Modes | Parent spec with full architecture and phase dependencies | Active | https://github.com/Brothertown-Language/snea-shoebox-editor/issues/400 |
| `src/frontend/pages/records.py` | Current search UI implementation | Current | `src/frontend/pages/records.py` |

## Revision Policy

| Artifact | Cascade Trigger | Action on Parent Revision |
|----------|-----------------|--------------------------|
| Implementation plan | MUST | Revise to match revised spec |
| Behavioral tests | SHOULD | Review for continued validity |

## AI Agent Instructions

This issue is a task sub-issue of #400 Phase 5. Implementation targets `src/frontend/pages/records.py` only — no backend changes. The backend already handles all 4 search modes (Phase 4, #1305). Headword is the new default search mode. Use a single vertical `st.radio` with markdown separators for Focused/Broad grouping. Lexeme and FTS UI behavior must remain unchanged except position in radio group and button layout.

🤖 📝 Updated by OpenCode (ollama-cloud/deepseek-v4-flash)
