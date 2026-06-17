STATUS: 1 (DRAFT)
CREATED: 2026-06-15
PARENT: #400 (Phase 4)

> **Full spec: [Issue #1305](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1305)**

## Executive Summary

Phase 4 implementation for #400: add Headword and Gloss search modes to all three backend search methods. `search_records()` already uses `_search_strategies` dictionary dispatch (lines 441-445). `get_all_records_for_export()` and `stream_records_to_temp_file()` have inline `if/else` branching that only handles Lexeme and FTS — Headword/Gloss are missing. This phase refactors those two methods to use the same strategy-dispatch pattern, then verifies all SCs pass.

Lexeme and FTS modes remain UNCHANGED.

---

## Problem

`get_all_records_for_export()` (line 513) and `stream_records_to_temp_file()` (line 596) both use inline `if search_mode == "Lexeme": ... else: ...` branching. The `else` branch assumes FTS mode. When called with `"Headword"` or `"Gloss"`, they silently fall through to the FTS branch — producing incorrect results.

`search_records()` already uses `_search_strategies` dictionary dispatch (line 442) and correctly handles all four modes.

---

## Context

**Current state:**

| Method | Lines | Dispatch Pattern | Headword/Gloss Support |
|--------|-------|-----------------|------------------------|
| `search_records()` | 441-445 | `_search_strategies.get(search_mode)` | ✅ Already works |
| `get_all_records_for_export()` | 513-544 | `if search_mode == "Lexeme" else ...` | ❌ Falls through to FTS |
| `stream_records_to_temp_file()` | 596-626 | `if search_mode == "Lexeme" else ...` | ❌ Falls through to FTS |

**Strategy functions already exist** (lines 31-74):

| Function | Lines | Table Joined | Filter |
|----------|-------|-------------|--------|
| `_search_lexeme()` | 31-36 | `Record.search_entries` → `SearchEntry` | `normalized_term` ILIKE |
| `_search_fts()` | 39-52 | `Record.fts_entry` → `FTSEntry` | `fts_vector @@ to_tsquery('simple', ...)` |
| `_search_headword()` | 55-64 | `Record.headword_entries` → `HeadwordSearchEntry` | `normalized_term` ILIKE |
| `_search_gloss()` | 67-74 | `Record.gloss_entries` → `GlossSearchEntry` | `normalized_term` ILIKE |

**Dispatch dictionary** (lines 77-82):
```python
_search_strategies: dict[str, callable] = {
    "Lexeme": _search_lexeme,
    "FTS": _search_fts,
    "Headword": _search_headword,
    "Gloss": _search_gloss,
}
```

---

## Constraints

| Constraint | Details |
|------------|---------|
| **Lexeme/FTS UNCHANGED** | No changes to Lexeme or FTS query logic in any method |
| **Strategy-dispatch pattern** | Refactored methods must use `_search_strategies` dict, not inline elif chains |
| **Column projection preserved** | `get_all_records_for_export()` uses column projection (no `Record.*`) — must be preserved |
| **Streaming preserved** | `stream_records_to_temp_file()` uses `yield_per(1000)` — must be preserved |
| **Existing tests must pass** | All existing search tests must continue to pass unchanged |

---

## Affected Files

| File | Anchor | Change |
|------|--------|--------|
| `src/services/linguistic_service.py` | `get_all_records_for_export()` (line 513) | Replace inline `if/else` with `_search_strategies` dispatch; add Headword/Gloss query builders using column-projected join |
| `src/services/linguistic_service.py` | `stream_records_to_temp_file()` (line 596) | Replace inline `if/else` with `_search_strategies` dispatch; add Headword/Gloss query builders using column-projected join |
| `tests/services/test_linguistic_service.py` | Export/stream test functions | Add tests for Headword/Gloss modes in export and stream methods |

---

## Success Criteria

| SC | Criterion | Evidence Type | Verification Method |
|----|-----------|---------------|---------------------|
| SC-1 | Headword search finds primary lx — "wampuw" returns exactly 1 record | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_search_records_headword_finds_primary_lx` |
| SC-2 | Headword search finds primary va — "wampu" returns exactly 1 record | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_search_records_headword_finds_primary_va` |
| SC-3 | Headword excludes nested va — "wampu-" returns 0 records | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_search_records_headword_excludes_nested_va` |
| SC-4 | Gloss search finds primary ge — "round object" returns exactly 1 record | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_search_records_gloss_finds_primary_ge` |
| SC-5 | Gloss excludes nested ge — "ball" returns 0 records | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_search_records_gloss_excludes_nested_ge` |
| SC-6 | Gloss excludes headword — "wampuw" returns 0 records | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_search_records_gloss_excludes_headword` |
| SC-7 | Lexeme mode UNCHANGED — all variants returned, no entry_type filter | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_search_records_lexeme_mode_unchanged` |
| SC-8 | FTS mode UNCHANGED — no changes to FTS logic | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_search_records_fts_mode_unchanged` |
| SC-14 | Search performance < 500ms for all modes | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_search_records_performance` |
| SC-24 | Empty search input returns all records without error/crash | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_search_records_empty_input` |
| SC-25 | Special characters no crash or SQL injection | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_search_records_special_characters` |
| SC-28 | `get_all_records_for_export()` Headword mode returns correct results | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_export_headword_mode` |
| SC-29 | `get_all_records_for_export()` Gloss mode returns correct results | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_export_gloss_mode` |
| SC-30 | `stream_records_to_temp_file()` Headword mode returns correct results | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_stream_headword_mode` |
| SC-31 | `stream_records_to_temp_file()` Gloss mode returns correct results | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_stream_gloss_mode` |
| SC-32 | `get_all_records_for_export()` Lexeme mode UNCHANGED | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_export_lexeme_mode_unchanged` |
| SC-33 | `stream_records_to_temp_file()` Lexeme mode UNCHANGED | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_stream_lexeme_mode_unchanged` |
| SC-34 | `get_all_records_for_export()` FTS mode UNCHANGED | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_export_fts_mode_unchanged` |
| SC-35 | `stream_records_to_temp_file()` FTS mode UNCHANGED | `behavioral` | `uv run pytest tests/services/test_linguistic_service.py::test_stream_fts_mode_unchanged` |

---

## Edge Cases

| Edge Case | Handling |
|-----------|----------|
| `get_all_records_for_export()` called with Headword mode, empty search term | Return all records (no filter applied) |
| `stream_records_to_temp_file()` called with Gloss mode, empty search term | Return all records (no filter applied) |
| Unknown search mode passed to any method | `_search_strategies.get()` returns `None` → raise `ValueError` (consistent with `search_records()`) |
| Column projection with Headword/Gloss joins | Join adds no columns to projection — `Record.id` is sufficient for join; `.distinct()` prevents duplicates |
| `yield_per(1000)` with Headword/Gloss joins | Join + distinct works correctly with yield_per (tested by existing stream tests) |

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking existing export/stream behavior | Low | Medium | Regression tests for Lexeme/FTS modes (SC-32 through SC-35) |
| Column projection incompatible with join | Low | High | Use `Record.id` for join target; `.distinct()` prevents row multiplication |
| Performance regression in export/stream | Low | Low | No new indexes needed — HeadwordSearchEntry/GlossSearchEntry already indexed on `normalized_term` |

---

## Dependencies

| Dependency | Type | Impact |
|------------|------|--------|
| Phase 1 (Schema) — #1303 | Hard | Tables must exist |
| Phase 2 (Indexing) — #1304 | Hard | Tables must be populated |
| Phase 3 (Migration) — #1306 | Hard | Existing data must be backfilled |
| `_search_strategies` dict (lines 77-82) | Internal | Already exists — no changes needed |
| `_search_headword()` / `_search_gloss()` functions (lines 55-74) | Internal | Already exist — no changes needed |

---

## TDD Phase: Refactor Export/Stream to Strategy-Dispatch

**Concern (entering):** `get_all_records_for_export()` and `stream_records_to_temp_file()` have inline `if/else` branching that only handles Lexeme and FTS.

**Concern (leaving):** Both methods use `_search_strategies` dictionary dispatch and correctly handle all four modes (Lexeme, FTS, Headword, Gloss).

### Per-Item TDD Cycle

#### Item 1: Refactor `get_all_records_for_export()` to use strategy-dispatch

**RED condition:** `test_export_headword_mode` and `test_export_gloss_mode` FAIL because `get_all_records_for_export()` falls through to FTS branch when called with Headword/Gloss mode.

**GREEN condition:** Replace inline `if search_mode == "Lexeme": ... else: ...` (lines 513-544) with `_search_strategies` dispatch. The strategy functions already exist and work with `query` + `search_term` — but `get_all_records_for_export()` uses column projection (not `Record.*`). The strategy functions join via `Record.search_entries` / `Record.headword_entries` / `Record.gloss_entries` which works with column-projected queries because the join target is the `Record` model, not the column list.

**Implementation:**
- Replace lines 513-544 with:
  ```python
  if search_term:
      strategy = _search_strategies.get(search_mode)
      if strategy is None:
          raise ValueError(f"Unknown search mode: {search_mode}")
      query = strategy(query, search_term)
  ```
- This is identical to the `search_records()` dispatch at lines 441-445
- No changes to strategy functions needed — they already handle all four modes

**Test file:** `tests/services/test_linguistic_service.py`

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|-------|------------------|-------------------|----------|--------|
| Item 1 | Write tests: `test_export_headword_mode`, `test_export_gloss_mode`, `test_export_lexeme_mode_unchanged`, `test_export_fts_mode_unchanged` — all FAIL | Replace inline if/else with `_search_strategies` dispatch | Verify column projection preserved; verify `.distinct()` still applied | Export dispatch + tests |

#### Item 2: Refactor `stream_records_to_temp_file()` to use strategy-dispatch

**RED condition:** `test_stream_headword_mode` and `test_stream_gloss_mode` FAIL because `stream_records_to_temp_file()` falls through to FTS branch when called with Headword/Gloss mode.

**GREEN condition:** Replace inline `if search_mode == "Lexeme": ... else: ...` (lines 596-626) with `_search_strategies` dispatch. Same pattern as Item 1.

**Implementation:**
- Replace lines 596-626 with:
  ```python
  if search_term:
      strategy = _search_strategies.get(search_mode)
      if strategy is None:
          raise ValueError(f"Unknown search mode: {search_mode}")
      query = strategy(query, search_term)
  ```
- The strategy functions work with column-projected queries (same as Item 1)

**Test file:** `tests/services/test_linguistic_service.py`

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|-------|------------------|-------------------|----------|--------|
| Item 2 | Write tests: `test_stream_headword_mode`, `test_stream_gloss_mode`, `test_stream_lexeme_mode_unchanged`, `test_stream_fts_mode_unchanged` — all FAIL | Replace inline if/else with `_search_strategies` dispatch | Verify `yield_per(1000)` preserved; verify `.distinct()` still applied | Stream dispatch + tests |

---

## Documentation Sources

| Source | Description | Version/Date | URL |
|--------|-------------|--------------|-----|
| Spec #400 — Headword/Gloss Search Modes | Parent spec with full architecture, SCs, and phase dependencies | Active | https://github.com/Brothertown-Language/snea-shoebox-editor/issues/400 |
| `src/services/linguistic_service.py` | Current search dispatch implementation | Current | `src/services/linguistic_service.py` |
| `tests/services/test_linguistic_service.py` | Existing search tests | Current | `tests/services/test_linguistic_service.py` |

---

## Revision Policy

| Artifact | Cascade Trigger | Action on Parent Revision |
|----------|-----------------|--------------------------|
| Implementation plan | MUST | Revise to match revised spec |
| Behavioral tests | SHOULD | Review for continued validity |

---

## AI Agent Instructions

This issue is a task sub-issue of #400 Phase 4. The authoritative spec is at `.issues/400/open/400-add-headword-gloss-search-modes/spec.md`. Implementation MUST NOT modify Lexeme or FTS search logic. All four strategy functions already exist — the work is refactoring two methods to use the existing dispatch pattern.

🤖 Co-authored with AI: OpenCode (ollama-cloud/deepseek-v4-flash)
