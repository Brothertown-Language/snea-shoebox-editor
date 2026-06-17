# Plan: Phase 4 — Strategy-Dispatch for Headword/Gloss Modes

**Issue:** #1305
**Spec:** #1305
**Parent:** #400 (Phase 4)
**Authorization Scope:** `for_pr`
**PR Strategy:** `stacked`

---

## Concern Boundary

**Entering:** `get_all_records_for_export()` and `stream_records_to_temp_file()` have inline `if/else` branching that only handles Lexeme and FTS — Headword/Gloss silently fall through to FTS.

**Leaving:** Both methods use `_search_strategies` dictionary dispatch and correctly handle all four modes (Lexeme, FTS, Headword, Gloss). Lexeme/FTS modes remain UNCHANGED.

---

## Phase 1: Refactor `get_all_records_for_export()` to Strategy-Dispatch

**File:** `src/services/linguistic_service.py`
**Target:** `get_all_records_for_export()` (lines 513-544)
**SC Coverage:** SC-28, SC-29, SC-32, SC-34

### Item 1.1 — RED: Write failing tests for Headword/Gloss export modes

| Step | Action | File | Command |
|------|--------|------|---------|
| 1.1.1 | Write `test_export_headword_mode` — Headword search returns correct record | `tests/services/test_linguistic_service.py` | `uv run pytest tests/services/test_linguistic_service.py::TestLinguisticService::test_export_headword_mode -x` |
| 1.1.2 | Write `test_export_gloss_mode` — Gloss search returns correct record | `tests/services/test_linguistic_service.py` | `uv run pytest tests/services/test_linguistic_service.py::TestLinguisticService::test_export_gloss_mode -x` |
| 1.1.3 | Write `test_export_lexeme_mode_unchanged` — Lexeme regression guard | `tests/services/test_linguistic_service.py` | `uv run pytest tests/services/test_linguistic_service.py::TestLinguisticService::test_export_lexeme_mode_unchanged -x` |
| 1.1.4 | Write `test_export_fts_mode_unchanged` — FTS regression guard | `tests/services/test_linguistic_service.py` | `uv run pytest tests/services/test_linguistic_service.py::TestLinguisticService::test_export_fts_mode_unchanged -x` |

**RED condition:** All 4 tests FAIL because `get_all_records_for_export()` falls through to FTS branch for Headword/Gloss.

### Item 1.2 — GREEN: Replace inline if/else with `_search_strategies` dispatch

| Step | Action | File | Details |
|------|--------|------|---------|
| 1.2.1 | Replace lines 515-519 with `_search_strategies.get(search_mode)` dispatch | `src/services/linguistic_service.py` | Pattern: `strategy = _search_strategies.get(search_mode); if strategy is None: raise ValueError(...); query = strategy(query, search_term)` |
| 1.2.2 | Verify column projection preserved | `src/services/linguistic_service.py` | Query selects `Record.id, Record.lx, Record.hm, Record.ps, Record.ge, Record.status, Record.source_id, Record.sort_lx, Record.mdf_data, Source.name.label("source_name")` — join adds no columns |
| 1.2.3 | Verify `.distinct()` still applied | `src/services/linguistic_service.py` | Strategy functions already call `.distinct()` |

**GREEN condition:** All 4 tests PASS.

### Item 1.3 — REFACTOR: Verify

| Step | Action | Command |
|------|--------|---------|
| 1.3.1 | Run full export test suite | `uv run pytest tests/services/test_linguistic_service.py -k "export" -v` |
| 1.3.2 | Run full search test suite (regression) | `uv run pytest tests/services/test_linguistic_service.py -v` |

---

## Phase 2: Refactor `stream_records_to_temp_file()` to Strategy-Dispatch

**File:** `src/services/linguistic_service.py`
**Target:** `stream_records_to_temp_file()` (lines 571-575)
**SC Coverage:** SC-30, SC-31, SC-33, SC-35

### Item 2.1 — RED: Write failing tests for Headword/Gloss stream modes

| Step | Action | File | Command |
|------|--------|------|---------|
| 2.1.1 | Write `test_stream_headword_mode` — Headword stream returns correct content | `tests/services/test_linguistic_service.py` | `uv run pytest tests/services/test_linguistic_service.py::TestLinguisticService::test_stream_headword_mode -x` |
| 2.1.2 | Write `test_stream_gloss_mode` — Gloss stream returns correct content | `tests/services/test_linguistic_service.py` | `uv run pytest tests/services/test_linguistic_service.py::TestLinguisticService::test_stream_gloss_mode -x` |
| 2.1.3 | Write `test_stream_lexeme_mode_unchanged` — Lexeme regression guard | `tests/services/test_linguistic_service.py` | `uv run pytest tests/services/test_linguistic_service.py::TestLinguisticService::test_stream_lexeme_mode_unchanged -x` |
| 2.1.4 | Write `test_stream_fts_mode_unchanged` — FTS regression guard | `tests/services/test_linguistic_service.py` | `uv run pytest tests/services/test_linguistic_service.py::TestLinguisticService::test_stream_fts_mode_unchanged -x` |

**RED condition:** All 4 tests FAIL because `stream_records_to_temp_file()` falls through to FTS branch for Headword/Gloss.

### Item 2.2 — GREEN: Replace inline if/else with `_search_strategies` dispatch

| Step | Action | File | Details |
|------|--------|------|---------|
| 2.2.1 | Replace lines 571-575 with `_search_strategies.get(search_mode)` dispatch | `src/services/linguistic_service.py` | Same pattern as Phase 1 Item 1.2.1 |
| 2.2.2 | Verify `yield_per(1000)` preserved | `src/services/linguistic_service.py` | `query.yield_per(1000)` at line 581 — join + distinct works correctly with yield_per |
| 2.2.3 | Verify `.distinct()` still applied | `src/services/linguistic_service.py` | Strategy functions already call `.distinct()` |

**GREEN condition:** All 4 tests PASS.

### Item 2.3 — REFACTOR: Verify

| Step | Action | Command |
|------|--------|---------|
| 2.3.1 | Run full stream test suite | `uv run pytest tests/services/test_linguistic_service.py -k "stream" -v` |
| 2.3.2 | Run full test suite (regression) | `uv run pytest tests/services/test_linguistic_service.py -v` |

---

## Pipeline-Readiness Check

| Check | Status | Notes |
|-------|--------|-------|
| Spec approved | ✅ | Label: `approved-for-pr` |
| All strategy functions exist | ✅ | `_search_lexeme`, `_search_fts`, `_search_headword`, `_search_gloss` (lines 31-74) |
| Dispatch dict exists | ✅ | `_search_strategies` (lines 79-84) |
| Tests exist for all SCs | ✅ | SC-28 through SC-35 all have test methods |
| Lexeme/FTS unchanged | ✅ | No changes to Lexeme or FTS query logic |
| Column projection preserved | ✅ | Export query uses explicit column list |
| `yield_per(1000)` preserved | ✅ | Stream query uses `yield_per(1000)` |
| Dependencies met | ✅ | Phases 1-3 complete (tables exist, populated, backfilled) |

---

## Concern Boundary Annotations

| Phase | Concern | Files Touched | Risk |
|-------|---------|--------------|------|
| Phase 1 | Export method dispatch | `src/services/linguistic_service.py`, `tests/services/test_linguistic_service.py` | Low — same pattern as `search_records()` |
| Phase 2 | Stream method dispatch | `src/services/linguistic_service.py`, `tests/services/test_linguistic_service.py` | Low — same pattern as Phase 1 |

---

## Implementation Checklist

- [ ] Phase 1 RED: 4 export tests written and FAIL
- [ ] Phase 1 GREEN: `get_all_records_for_export()` dispatch refactored
- [ ] Phase 1 REFACTOR: Export tests pass, regression suite passes
- [ ] Phase 2 RED: 4 stream tests written and FAIL
- [ ] Phase 2 GREEN: `stream_records_to_temp_file()` dispatch refactored
- [ ] Phase 2 REFACTOR: Stream tests pass, regression suite passes
- [ ] Lint: `uvx ruff check --fix src/services/linguistic_service.py tests/services/test_linguistic_service.py`
- [ ] Type check: `uvx pyright src/services/linguistic_service.py`
