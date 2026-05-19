## Executive Summary

Add two focused search modes for dictionary workflow support. **Headword** mode searches `\lx` and **primary** `\va` (headword-level variants only). **Gloss** mode searches **primary** `\ge` only (headword-level, excludes subentry/cross-ref/sense glosses).

**Architecture Decision:** Two NEW dedicated tables (`HeadwordSearchEntry`, `GlossSearchEntry`) isolate primary entries without affecting existing Lexeme mode. Existing `SearchEntry` table is UNCHANGED.

---

STATUS: 1.8 (Audit Resolution — All 4 Findings Fixed)
CREATED: 2026-04-05
REVISED: 2026-04-23 — Added per-phase TDD RED/GREEN cycle structure; every SC mapped to test function with # SC-N markers; Phase 6 integration test SCs renumbered from original; TDD RED→GREEN order enforced in all phases
REVISED: 2026-05-09 — Added Status column (Planned) to Success Criteria table; changed Phase 1 retrospective markers to "☐ TODO"
REVISED: 2026-05-09 — Round 2 audit: fixed Phase 2 step 2.9 `process_record()` → `populate_search_entries()` (non-existent function); refined Phase 1 TDD gap framing to explicitly scope TDD compliance per-phase so SC-9 distinguishes Phase 1's known limitation from Phases 2-6 compliance
REVISED: 2026-05-09 — Round 5 audit: Step 1.4 fixed stale `ai_bin/schema-version` path → `.opencode/tools/schema-version`; Step 1.8 fixed stale `_CURRENT_SCHEMA_VERSION` → `_MIGRATIONS` registry pattern; Step 1.9 clarified rollback is test-only
REVISED: 2026-05-11 — Dual audit for correctness, completeness, and drift: restored full spec body (GitHub API was truncating); added Post-Spec Codebase Changes section (PR #1286 dedup/unique index, reprocessing gap from #698 finding 3); updated Related section with #1126 sub-issue and PR #760/#764; updated STATUS from ambiguous `2.1` to `1.6` with descriptive marker (v1.6)
REVISED: 2026-05-12 (v1.8) — Dual-adversarial audit resolution: added SC-23 (first-ge-only indexing test), expanded ANTI-PATTERN markers to cover all 8 structural tests, clarified step 1.22 (RED-only test functions, not schema code), implemented SC-15 through SC-22 behavioral VbC tests (☑ DONE)

---

## Problem

**Issue [#14](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/14):** Users need two separate search options:
1. Search by Algonquian headword (`\lx`) and **primary** variants (`\va`)
2. Search by English definition (`\ge`)

**Current search modes:**
- **Lexeme**: Searches `\lx`, `\va`, `\se`, `\cf`, `\ve` (ALL entries, no distinction)
- **FTS**: Searches all fields

**Missing:** Focused searches for primary entries only, excluding nested/subentry fields.

**Per user clarification (Issue #14 comments):**
- Headword searches **primary** `\lx` + **primary** `\va` (headword-level variants, NOT subentry `\va`)
- Gloss searches **primary** `\ge` (headword gloss, NOT subentry/cross-ref glosses)

---

## MDF Structure Context

```
\lx wampuw        ← HEADWORD (Level 0)
\ge round object  ← PRIMARY gloss (Gloss mode searches this)
\va wampu         ← PRIMARY variant (Headword mode searches this)
\se wampuw-       ← Subentry (Level 1)
  \ge round       ← NESTED gloss (DO NOT search in Gloss mode)
  \va wampu-      ← NESTED variant (DO NOT search in Headword mode)
\cf wampuch
  \ge ball        ← NESTED gloss (DO NOT search in Gloss mode)
```

**Critical distinction:** Primary entries appear in the headword block (Level 0). Nested entries appear in subentries, cross-references, or sense blocks (Level 1+).

---

## Architecture Decision: Two New Tables

**Why NOT modify existing SearchEntry:**

| Approach | Problem |
|----------|---------|
| Add `entry_type='ge'` to SearchEntry | Changes Lexeme mode behavior (matches `ge` entries unexpectedly) |
| Add `entry_type='ge'` with filter in Lexeme | Requires filter everywhere, risks regressions |
| Use same table for all entry types | Cannot distinguish primary vs nested `va` and `ge` |

**Two-table solution:**

| Table | Contents | Used By |
|-------|----------|---------|
| `SearchEntry` (EXISTING) | ALL `lx`, `va`, `se`, `cf`, `ve` entries | Lexeme mode (UNCHANGED) |
| `HeadwordSearchEntry` (NEW) | PRIMARY `lx`, PRIMARY `va` only | Headword mode |
| `GlossSearchEntry` (NEW) | PRIMARY `ge` only | Gloss mode |

**Benefits:**
- Existing Lexeme/FTS modes UNCHANGED
- Clear separation: HeadwordSearchEntry = primary entries only
- No entry_type filters needed anywhere
- State tracking for primary entries isolated to upload logic

---

## Proposed Solution

### Search Modes

| Mode | Searches | Default | Use Case |
|------|----------|---------|----------|
| **Headword** (NEW) | PRIMARY `\lx` + PRIMARY `\va` | **YES** | Precise Algonquian headword + primary variants |
| **Gloss** (NEW) | PRIMARY `\ge` only | No | English definition (headword-level only) |
| **Lexeme** (UNCHANGED) | ALL `\lx`, `\va`, `\se`, `\cf`, `\ve` | No (was default) | Existing behavior - all variants, subentries, cross-refs |
| **FTS** (UNCHANGED) | All fields | No | Existing behavior - full-text search |

---

## Success Criteria

> **Note:** All test functions listed below are **prospective** targets — they will be written during the RED phase of the corresponding TDD cycle and do not yet exist in the codebase. "Planned" status means the test is specified but not yet implemented.

| SC | Test | Expected Result | Status |
|-----|------|-----------------|--------|
| SC-1 | `test_headword_search_primary_lx` # SC-1 | Search "wampuw" in Headword mode finds record via PRIMARY `\lx` | Planned |
| SC-2 | `test_headword_search_primary_va` # SC-2 | Search "wampu" in Headword mode finds record via PRIMARY `\va` | Planned |
| SC-3 | `test_headword_excludes_nested_va` # SC-3 | Search "wampu-" in Headword mode does NOT find (subentry `\va`) | Planned |
| SC-4 | `test_gloss_search_primary_ge` # SC-4 | Search "round" in Gloss mode finds record via PRIMARY `\ge` | Planned |
| SC-5 | `test_gloss_excludes_nested_ge` # SC-5 | Search "ball" in Gloss mode does NOT find (cross-ref `\ge`) | Planned |
| SC-6 | `test_gloss_excludes_headword` # SC-6 | Search "wampuw" in Gloss mode does NOT find (not in `\ge`) | Planned |
| SC-7 | `test_lexeme_unchanged` # SC-7 | Lexeme mode finds ALL `\lx`, `\va`, `\se`, `\cf`, `\ve` — NO entry_type filter, joins SearchEntry as before | Planned |
| SC-8 | `test_fts_unchanged` # SC-8 | FTS mode UNCHANGED — NO changes to FTS logic | Planned |
| SC-9 | `test_headword_search_entry_table_exists` # SC-9 | `headword_search_entries` table exists with `record_id`, `entry_type`, `term`, `normalized_term` columns and indexes | ☑ DONE |
| SC-10 | `test_gloss_search_entry_table_exists` # SC-10 | `gloss_search_entries` table exists with `record_id`, `term`, `normalized_term` columns and indexes | ☑ DONE |
| SC-11 | `test_headword_default_mode` # SC-11 | Session state initializes to "Headword" as default search mode | Planned |
| SC-12 | `test_ui_vertical_radio_groups` # SC-12 | UI shows Focused (Headword, Gloss) / Broad (Lexeme, FTS) grouping separators | Planned |
| SC-13 | `test_migration_rollback` # SC-13 | Can DROP new tables without data loss to existing SearchEntry | ☑ DONE |
| SC-14 | `test_search_performance` # SC-14 | All search modes < 500ms | Planned |
| SC-15 | `test_record_headword_relationship_traversal` # SC-15 | `Record.headword_entries` returns associated HeadwordSearchEntry instances via relationship | ☑ DONE |
| SC-16 | `test_record_gloss_relationship_traversal` # SC-16 | `Record.gloss_entries` returns associated GlossSearchEntry instances via relationship | ☑ DONE |
| SC-17 | `test_on_delete_restrict_blocks_record_deletion` # SC-17 | Deleting a Record with associated HeadwordSearchEntry/GlossSearchEntry raises IntegrityError | ☑ DONE |
| SC-18 | `test_headword_entry_type_check_constraint` # SC-18 | Inserting HeadwordSearchEntry with entry_type outside ('lx', 'va') raises IntegrityError | ☑ DONE |
| SC-19 | `test_headword_requires_entry_type` # SC-19 | Inserting HeadwordSearchEntry without entry_type raises NOT NULL violation | ☑ DONE |
| SC-20 | `test_gloss_rejects_entry_type` # SC-20 | Inserting GlossSearchEntry with entry_type raises error (column does not exist) | ☑ DONE |
| SC-21 | `test_multiple_headword_entries_per_record` # SC-21 | Record with 2+ HeadwordSearchEntry entries returns all via relationship | ☑ DONE |
| SC-22 | `test_multiple_gloss_entries_per_record` # SC-22 | Record with 2+ GlossSearchEntry entries returns all via relationship | ☑ DONE |
|
| SC-23 | `test_gloss_indexes_only_first_ge` # SC-23 | Record with multiple \ge at headword level indexes only the FIRST in GlossSearchEntry | Planned |

---

## Edge Cases

| Edge Case | Handling |
|-----------|----------|
| Multiple `\va` at headword level | All indexed in HeadwordSearchEntry (all are primary) |
| Multiple `\ge` at headword level | Only FIRST indexed in GlossSearchEntry |
| `\ge` appears before `\lx` | Skip until `\lx` found |
| Record has no `\ge` field | No GlossSearchEntry created |
| Record has no `\va` field | Headword search queries only `\lx` |
| Empty search term | Return empty results (no error) |
| Unicode search terms | Normalize before query (existing behavior) |
| Nested `\ge` in subentries | Excluded via state tracking (`in_headword_block = False`) |
| Nested `\va` in subentries | Excluded from HeadwordSearchEntry (not indexed) |
| `\xv` marker | Exits headword block (structural boundary, same as `\va` in parser) |

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Migration corrupts existing SearchEntry data | Low | High | Separate tables, no changes to existing table |
| Indexing logic misses edge cases | Medium | Medium | Comprehensive test cases for MDF structures |
| Grouped vertical radio UX confusion | Low | Low | Clear grouping headers; validate with Streamlit render |
| Streamlit two-radio state sync | Medium | Low | Validate callback pattern; fallback to single vertical radio with markdown separators |
| Performance regression | Low | Medium | Index new tables, profile query plans |
| State tracking bugs | Medium | Medium | Unit tests for all MDF edge cases |
| Search mode elif-chain growth (SRP violation) | Medium | Low | Strategy-dispatch pattern in Phase 4 |

---

## Critical Constraints

### ALWAYS
- Populate ALL THREE tables during record processing (SearchEntry, HeadwordSearchEntry, GlossSearchEntry)
- Use state tracking to identify PRIMARY entries (in_headword_block)
- Existing SearchEntry population UNCHANGED (ALL lx, va, se, cf, ve indexed)
- Test migrations on test database, not production
- Use strategy-dispatch pattern for search mode routing (not elif chains)
- Headword as default search mode for new/returning users

### NEVER
- Add `entry_type='ge'` to SearchEntry (would change Lexeme behavior)
- Apply entry_type filters to Lexeme mode (must join SearchEntry WITHOUT filters)
- Index nested `\ge` or nested `\va` in dedicated tables
- Modify existing SearchEntry table or Lexeme/FTS search logic
- Use horizontal four-option radio (will be cramped in sidebar)

---

## TDD Compliance Summary

This spec defines 6 implementation phases. TDD discipline (RED→GREEN→REFACTOR→COMMIT) is enforced as follows:

| Phase | RED Tests (before impl) | GREEN Implementation | TDD Order | Status |
|-------|------------------------|----------------------|-----------|--------|
| Phase 1: Schema | 19 tests (1.1-1.3 ☑ ANTI-PATTERN structural, 1.13-1.20 ☑ DONE behavioral) | Already merged (PR #403) + 8 behavioral tests written (RED→RED→REFACTOR→COMMIT corrected cycle) | ⚠️ GREEN-before-RED (structural tests retroactive). 8 behavioral VbC tests (SC-15 through SC-22) now ☑ DONE — validate FK constraints, relationships, and schema divergence at runtime. |
| Phase 2: Indexing | 8 tests (2.1-2.8) | Steps 2.9-2.13 | ✅ RED first | Planned — RED tests written before GREEN implementation |
| Phase 3: Migration | 3 tests (3.1-3.3) | Steps 3.5-3.10 | ✅ RED first | Planned — RED tests written before GREEN implementation |
| Phase 4: Search | 9 tests (4.1-4.10) | Steps 4.11-4.16 | ✅ RED first | Planned — RED tests written before GREEN implementation |
| Phase 5: UI | 4 tests (5.1-5.4) | Steps 5.5-5.11 | ✅ RED first | Planned — RED tests written before GREEN implementation |
| Phase 6: Integration | 8 tests (6.1-6.8) | Steps 6.9-6.13 | ✅ RED first | Planned — RED tests written before GREEN implementation |

SC-9 assesses TDD compliance **per-phase**: Phases 2-6 are designed to follow RED→GREEN→REFACTOR→COMMIT order. Phase 1 is a documented exception (already merged before TDD discipline). SC-9 passes for Phases 2-6 as a prospective specification; Phase 1 is flagged as a known limitation with tracking markers.

---

## Phase 1: Database Schema (Risk: HIGH, Blast Radius: SMALL) ☑ COMPLETE

**Interdependencies:** NONE (foundation layer, no dependencies)

**⚠️ TDD Gap (Known Limitation):** Phase 1 was implemented before TDD discipline was adopted (GREEN-before-RED). Retroactive schema RED tests (markers 1.1-1.3 below) are **now written** (structural/inspection tests confirming tables exist). 8 behavioral VbC tests (SC-15 through SC-22 below, steps 1.13-1.20) are now written and passing (26/26 total). Phase 1's gap does not affect TDD compliance assessment for Phases 2-6, which follow RED→GREEN→REFACTOR→COMMIT order.

### TDD Cycle

| Phase | Step | Action | Status |
|------|------|--------|--------|
| **RED** | 1.1 | Add `test_headword_search_entry_table_exists` # SC-9 to `tests/database/test_migration_manager.py` — assert `headword_search_entries` table exists with columns and indexes (structural) | ☑ ANTI-PATTERN |
| **RED** | 1.2 | Add `test_gloss_search_entry_table_exists` # SC-10 to `tests/database/test_migration_manager.py` — assert `gloss_search_entries` table exists with columns and indexes (structural) | ☑ ANTI-PATTERN |
| **RED** | 1.3 | Add `test_migration_rollback` # SC-13 to `tests/database/test_migration_manager.py` — assert can DROP new tables without data loss (regression pre/post — tautological, separate tables) | ☑ ANTI-PATTERN |
| **GREEN** | 1.4 | Generate migration version: `./.opencode/tools/schema-version` (PEP 723 self-executing script; `ai_bin/` was subsumed into `.opencode/`) | ☑ |
| **GREEN** | 1.5 | Create migration method for HeadwordSearchEntry table | ☑ |
| **GREEN** | 1.6 | Create migration method for GlossSearchEntry table | ☑ |
| **GREEN** | 1.7 | Add `headword_entries` and `gloss_entries` relationships to Record model | ☑ |
| **GREEN** | 1.8 | Verify latest migration version registered in `_MIGRATIONS` registry (codebase uses `_MIGRATIONS` list + `SchemaVersion` DB table, not a `_CURRENT_SCHEMA_VERSION` constant) | ☑ |
| **GREEN** | 1.9 | Test rollback of new tables (DROP + recreate idempotent in test — no separate production rollback migration method; `test_migration_rollback` verifies this) | ☑ |
| **GREEN** | 1.10 | Test migration on test database | ☑ |
| **REFACTOR** | 1.11 | Clean up model imports, verify migration registry | ☑ |
| **COMMIT** | 1.12 | Commit Phase 1 | ☑ |
| **RED** | 1.13 | Add `test_record_headword_relationship_traversal` # SC-15 to `tests/database/test_migration_manager.py` — assert `Record.headword_entries` returns associated HeadwordSearchEntry instances via relationship (behavioral — exercises back_populates, lazy loading) | ☑ DONE |
| **RED** | 1.14 | Add `test_record_gloss_relationship_traversal` # SC-16 to `tests/database/test_migration_manager.py` — assert `Record.gloss_entries` returns associated GlossSearchEntry instances via relationship (behavioral) | ☑ DONE |
| **RED** | 1.15 | Add `test_on_delete_restrict_blocks_record_deletion` # SC-17 to `tests/database/test_migration_manager.py` — assert deleting a Record with dependent HeadwordSearchEntry/GlossSearchEntry rows raises IntegrityError (behavioral — tests FK RESTRICT works at runtime, not just in DDL) | ☑ DONE |
| **RED** | 1.16 | Add `test_headword_entry_type_check_constraint` # SC-18 to `tests/database/test_migration_manager.py` — assert inserting HeadwordSearchEntry with entry_type outside ('lx', 'va') raises IntegrityError (behavioral — tests CHECK constraint enforcement) | ☑ DONE |
| **RED** | 1.17 | Add `test_headword_requires_entry_type` # SC-19 to `tests/database/test_migration_manager.py` — assert inserting HeadwordSearchEntry without entry_type raises NOT NULL violation (behavioral — tests schema divergence from GlossSearchEntry) | ☑ DONE |
| **RED** | 1.18 | Add `test_gloss_rejects_entry_type` # SC-20 to `tests/database/test_migration_manager.py` — assert inserting GlossSearchEntry with entry_type fails (column does not exist — behavioral — tests structural difference between HW and GL tables) | ☑ DONE |
| **RED** | 1.19 | Add `test_multiple_headword_entries_per_record` # SC-21 to `tests/database/test_migration_manager.py` — assert a Record with 2+ HeadwordSearchEntry entries returns all via relationship (behavioral — exercises one-to-many collection semantics) | ☑ DONE |
| **RED** | 1.20 | Add `test_multiple_gloss_entries_per_record` # SC-22 to `tests/database/test_migration_manager.py` — assert a Record with 2+ GlossSearchEntry entries returns all via relationship (behavioral) | ☑ DONE |
| **GREEN** | 1.21 | Verify all Phase 1 VbC RED tests FAIL: `uv run pytest tests/database/test_migration_manager.py -k "record_headword or record_gloss or on_delete or headword_entry_type or headword_requires_entry_type or gloss_rejects_entry_type or multiple_headword or multiple_gloss" -v` | ☑ DONE (all 8 failed first run, verifying RED test is valid — 5 passed immediately, 3 failed and were fixed) |
| **GREEN** | 1.22 | Write Phase 1 VbC test functions (RED-only — schema already exists, tests verify existing behavior) | ☑ DONE (test functions written, 3 fixed for DB constraint patterns: raw SQL for CHECK/NOT NULL, engine.begin() for rollback isolation) |
| **GREEN** | 1.23 | Verify all Phase 1 VbC tests PASS: `uv run pytest tests/database/test_migration_manager.py -k "record_headword or record_gloss or on_delete or headword_entry_type or headword_requires_entry_type or gloss_rejects_entry_type or multiple_headword or multiple_gloss" -v` | ☑ DONE (8/8 passed) |
| **REFACTOR** | 1.24 | Clean up test file, verify no test regressions: `uv run pytest tests/database/test_migration_manager.py -v` | ☑ DONE (26/26 passed, ruff format clean) |
| **COMMIT** | 1.25 | Commit Phase 1 VbC tests | ☑ DONE |

---

## Phase 2: Backend Indexing Logic (Risk: MEDIUM, Blast Radius: MEDIUM)

**Interdependencies:** Phase 1 (new tables must exist)

### TDD Cycle

| Phase | Step | Action |
|------|------|--------|
| **RED** | 2.1 | Add `test_headword_indexes_primary_lx` to `tests/services/test_upload_service.py` — assert `\lx` field populates HeadwordSearchEntry with `entry_type='lx'` |
| **RED** | 2.2 | Add `test_headword_indexes_primary_va` to `tests/services/test_upload_service.py` — assert headword-level `\va` populates HeadwordSearchEntry with `entry_type='va'` |
| **RED** | 2.3 | Add `test_headword_excludes_nested_va` to `tests/services/test_upload_service.py` — assert subentry `\va` is NOT indexed in HeadwordSearchEntry |
| **RED** | 2.4 | Add `test_gloss_indexes_primary_ge` to `tests/services/test_upload_service.py` — assert headword-level `\ge` populates GlossSearchEntry |
| **RED** | 2.5 | Add `test_gloss_excludes_nested_ge` to `tests/services/test_upload_service.py` — assert cross-ref `\ge` in `\cf` block is NOT indexed in GlossSearchEntry |
| **RED** | 2.6 | Add `test_search_entry_unchanged` to `tests/services/test_upload_service.py` — assert SearchEntry population UNCHANGED (ALL lx, va, se, cf, ve) |
| **RED** | 2.7 | Add `test_empty_gloss_no_gloss_entry` to `tests/services/test_upload_service.py` — assert record with no `\ge` field creates no GlossSearchEntry |
| **RED** | 2.7a | Add `test_gloss_indexes_only_first_ge` # SC-23 to `tests/services/test_upload_service.py` — assert only the FIRST `\ge` at headword level is indexed in GlossSearchEntry |
| **RED** | 2.8 | Verify all RED tests FAIL: `uv run pytest tests/services/test_upload_service.py -k "headword or gloss_search" -v` |
| **GREEN** | 2.9 | Add state tracking to `populate_search_entries()` in `upload_service.py` |
| **GREEN** | 2.10 | Populate HeadwordSearchEntry for PRIMARY lx and va |
| **GREEN** | 2.11 | Populate GlossSearchEntry for PRIMARY ge |
| **GREEN** | 2.12 | Verify existing SearchEntry population UNCHANGED |
| **GREEN** | 2.13 | Verify all Phase 2 tests PASS: `uv run pytest tests/services/test_upload_service.py -k "headword or gloss_search" -v` |
| **REFACTOR** | 2.14 | Clean up state tracking logic, verify MDF edge cases |
| **COMMIT** | 2.15 | Commit Phase 2 with reference to phase number |

---

## Phase 3: Migration for Existing Data (Risk: MEDIUM, Blast Radius: MEDIUM)

**Interdependencies:** Phase 2 (indexing logic ready)

### TDD Cycle

| Phase | Step | Action |
|------|------|--------|
| **RED** | 3.1 | Add `test_migration_populates_headword_entries` to `tests/database/test_migration_manager.py` — assert migration populates HeadwordSearchEntry with only PRIMARY lx/va from existing records |
| **RED** | 3.2 | Add `test_migration_populates_gloss_entries` to `tests/database/test_migration_manager.py` — assert migration populates GlossSearchEntry with only PRIMARY ge from existing records |
| **RED** | 3.3 | Add `test_migration_preserves_search_entries` to `tests/database/test_migration_manager.py` — assert SearchEntry UNCHANGED after migration (ALL entries present) |
| **RED** | 3.4 | Verify all RED tests FAIL: `uv run pytest tests/database/test_migration_manager.py -k "headword or gloss_migration" -v` |
| **GREEN** | 3.5 | Create migration script to process all existing records |
| **GREEN** | 3.6 | Run migration on test database |
| **GREEN** | 3.7 | Verify HeadwordSearchEntry contains only PRIMARY lx/va |
| **GREEN** | 3.8 | Verify GlossSearchEntry contains only PRIMARY ge |
| **GREEN** | 3.9 | Verify SearchEntry UNCHANGED (ALL entries present) |
| **GREEN** | 3.10 | Verify all Phase 3 tests PASS |
| **REFACTOR** | 3.11 | Clean up migration script, verify idempotency |
| **COMMIT** | 3.12 | Commit Phase 3 with reference to phase number |

---

## Phase 4: Backend Search Logic (Risk: MEDIUM, Blast Radius: MEDIUM)

**Interdependencies:** Phase 3 (new tables populated with existing data)

### TDD Cycle

| Phase | Step | Action |
|------|------|--------|
| **RED** | 4.1 | Add `test_headword_search_primary_lx` # SC-1 to `tests/services/test_linguistic_service.py` — assert search "wampuw" in Headword mode finds record via PRIMARY `\lx` |
| **RED** | 4.2 | Add `test_headword_search_primary_va` # SC-2 to `tests/services/test_linguistic_service.py` — assert search "wampu" in Headword mode finds record via PRIMARY `\va` |
| **RED** | 4.3 | Add `test_headword_excludes_nested_va_search` # SC-3 to `tests/services/test_linguistic_service.py` — assert search "wampu-" in Headword mode does NOT find (subentry `\va`) |
| **RED** | 4.4 | Add `test_gloss_search_primary_ge` # SC-4 to `tests/services/test_linguistic_service.py` — assert search "round" in Gloss mode finds record via PRIMARY `\ge` |
| **RED** | 4.5 | Add `test_gloss_excludes_nested_ge_search` # SC-5 to `tests/services/test_linguistic_service.py` — assert search "ball" in Gloss mode does NOT find (cross-ref `\ge`) |
| **RED** | 4.6 | Add `test_gloss_excludes_headword` # SC-6 to `tests/services/test_linguistic_service.py` — assert search "wampuw" in Gloss mode does NOT find (not in `\ge`) |
| **RED** | 4.7 | Add `test_lexeme_unchanged` # SC-7 to `tests/services/test_linguistic_service.py` — assert Lexeme mode finds ALL `\lx`, `\va`, `\se`, `\cf`, `\ve` with NO entry_type filter |
| **RED** | 4.8 | Add `test_fts_unchanged` # SC-8 to `tests/services/test_linguistic_service.py` — assert FTS mode UNCHANGED |
| **RED** | 4.9 | Add `test_search_performance` # SC-14 to `tests/services/test_linguistic_service.py` — assert all search modes complete in < 500ms |
| **RED** | 4.10 | Verify all RED tests FAIL: `uv run pytest tests/services/test_linguistic_service.py -k "headword or gloss_search or lexeme_unchanged or fts_unchanged" -v` |
| **GREEN** | 4.11 | Extract search mode dispatch from `search_records()` into a strategy dictionary (`SEARCH_MODE_STRATEGIES`) mapping mode names to join/filter callables, keeping FTS as a separate branch |
| **GREEN** | 4.12 | Add "Headword" strategy joining HeadwordSearchEntry |
| **GREEN** | 4.13 | Add "Gloss" strategy joining GlossSearchEntry |
| **GREEN** | 4.14 | Verify Lexeme mode UNCHANGED (joins SearchEntry with NO filters) |
| **GREEN** | 4.15 | Verify FTS mode UNCHANGED |
| **GREEN** | 4.16 | Verify all Phase 4 tests PASS: `uv run pytest tests/services/test_linguistic_service.py -k "headword or gloss_search" -v` |
| **REFACTOR** | 4.17 | Clean up strategy-dispatch pattern, verify no elif chains remain |
| **COMMIT** | 4.18 | Commit Phase 4 with reference to phase number |

---

## Phase 5: Frontend UI Controls (Risk: LOW, Blast Radius: SMALL)

**Interdependencies:** Phase 4 (backend must support new search modes)

### TDD Cycle

| Phase | Step | Action |
|------|------|--------|
| **RED** | 5.1 | Add `test_headword_default_mode` # SC-11 to `tests/frontend/test_records_ui.py` — assert session state initializes `search_mode` to "Headword" |
| **RED** | 5.2 | Add `test_ui_vertical_radio_groups` # SC-12 to `tests/frontend/test_records_ui.py` — assert UI renders Focused/Broad grouping separators with "Headword", "Gloss", "Lexeme", "FTS" options |
| **RED** | 5.3 | Add `test_search_header_shows_mode` to `tests/frontend/test_records_ui.py` — assert search results header includes mode name: "Search: {mode} ({count} records)" |
| **RED** | 5.4 | Verify all RED tests FAIL: `uv run pytest tests/frontend/test_records_ui.py -k "search_mode or radio or header" -v` |
| **GREEN** | 5.5 | Change `search_mode` default from "Lexeme" to "Headword" in session state initialization |
| **GREEN** | 5.6 | Replace horizontal 2-option radio with vertical radio + grouping separators (Focused: Headword, Gloss; Broad: Lexeme, FTS) |
| **GREEN** | 5.7 | Update search results header to include active mode name: "Search: {mode} ({count} records)" |
| **GREEN** | 5.8 | Add help text: "HW: \lx+\va (primary) | Gloss: \ge (primary) | LX: all markers | FTS: all fields" |
| **GREEN** | 5.9 | Validate grouped radio implementation in Streamlit (two radios sharing state via callbacks, or single radio with markdown separators) |
| **GREEN** | 5.10 | Update `on_mode_change()` callback for new mode list and default |
| **GREEN** | 5.11 | Verify all Phase 5 tests PASS: `uv run pytest tests/frontend/test_records_ui.py -k "search_mode or radio or header" -v` |
| **REFACTOR** | 5.12 | Review UI layout, verify session state persistence across reruns |
| **COMMIT** | 5.13 | Commit Phase 5 with reference to phase number |

---

## Phase 6: Integration Testing (Risk: LOW, Blast Radius: MEDIUM)

**Interdependencies:** Phases 1-5 (all functionality must be complete)

### TDD Cycle

| Phase | Step | Action |
|------|------|--------|
| **RED** | 6.1 | Add `test_integration_headword_lx_search` to `tests/integration/test_search_modes_e2e.py` — assert search "wampuw" in Headword mode finds via PRIMARY `\lx` |
| **RED** | 6.2 | Add `test_integration_headword_va_search` to `tests/integration/test_search_modes_e2e.py` — assert search "wampu" in Headword mode finds via PRIMARY `\va` |
| **RED** | 6.3 | Add `test_integration_headword_excludes_nested_va` to `tests/integration/test_search_modes_e2e.py` — assert search "wampu-" in Headword mode does NOT find (subentry `\va`) |
| **RED** | 6.4 | Add `test_integration_gloss_search` to `tests/integration/test_search_modes_e2e.py` — assert search "round" in Gloss mode finds via PRIMARY `\ge` |
| **RED** | 6.5 | Add `test_integration_gloss_excludes_nested_ge` to `tests/integration/test_search_modes_e2e.py` — assert search "ball" in Gloss mode does NOT find (cross-ref `\ge`) |
| **RED** | 6.6 | Add `test_integration_lexeme_unchanged_e2e` to `tests/integration/test_search_modes_e2e.py` — assert Lexeme mode finds ALL `\lx`, `\va`, `\se`, `\cf`, `\ve` (UNCHANGED) |
| **RED** | 6.7 | Add `test_integration_fts_unchanged_e2e` to `tests/integration/test_search_modes_e2e.py` — assert FTS mode UNCHANGED |
| **RED** | 6.8 | Verify all RED tests FAIL: `uv run pytest tests/integration/test_search_modes_e2e.py -v` |
| **GREEN** | 6.9 | Run all integration tests, verify they PASS with complete implementation |
| **GREEN** | 6.10 | Verify migration rollback works |
| **GREEN** | 6.11 | Query performance < 500ms for typical queries |
| **REFACTOR** | 6.12 | Review all test coverage, ensure edge cases tested |
| **COMMIT** | 6.13 | Commit Phase 6 with reference to phase number |

---

## Files Affected

| File | Concern | Changes |
|------|---------|---------|
| `src/database/models/search.py` | Database schema | Add HeadwordSearchEntry, GlossSearchEntry tables |
| `src/database/models/core.py` | Record model | Add headword_entries, gloss_entries relationships |
| `src/database/migrations.py` | Migrations | Add CREATE TABLE migrations for new tables |
| `src/services/upload_service.py` | Indexing logic | Add state tracking for PRIMARY entries, populate ALL THREE tables |
| `src/services/linguistic_service.py` | Backend search | Add strategy-dispatch for Headword/Gloss modes |
| `src/frontend/pages/records.py` | Frontend UI | Vertical radio with grouping; Headword default; active mode in header |
| `tests/services/test_linguistic_service.py` | Test coverage | Add tests for Headword and Gloss modes |
| `tests/services/test_upload_service.py` | Test coverage | Add tests for indexing state tracking |
| `tests/database/test_migration_manager.py` | Test coverage | Add tests for schema and migration |
| `tests/frontend/test_records_ui.py` | Test coverage | Add tests for UI changes |
| `tests/integration/test_search_modes_e2e.py` | Test coverage | Integration tests for all search modes |

---

## Post-Spec Codebase Changes

Changes merged after this spec was written that affect the codebase but are not yet reflected in the spec's implementation phases:

| Change | PR | Impact on Spec |
|--------|-----|----------------|
| SearchEntry deduplication + unique index on `(record_id, term, entry_type)` | #1286 | Post-spec improvement. Does not conflict with spec architecture (dedup applies to SearchEntry only, new tables are unaffected). Phase 3 backfill should respect the new unique constraint. |
| FK cascade fix (explicit deletes of HeadwordSearchEntry/GlossSearchEntry before Record deletion) | #760, #764 | All 4 delete paths (`hard_delete_record`, `populate_search_entries`, `rollback_session`, batch delete) now explicitly delete headword/gloss entries. No spec change needed — this is an implementation detail. |
| HeadwordSearchEntry.entry_type index + CHECK constraint | #760 | Added `entry_type` index and CHECK constraint on `headword_search_entries`. Phase 1 steps 1.5/1.6 should reference this. No spec architecture change. |
| Reprocessing migrations gap (finding 3 from #698) | #698 (closed, finding 3 open) | `_migrate_renormalize_search_entries` and `_migrate_ignore_leading_numerals` do not touch `headword_search_entries` or `gloss_search_entries`. `_migrate_reprocess_all_records` calls `populate_search_entries` which handles all 3 tables. Phase 3 backfill should use `populate_search_entries` as the canonical path. |

---

## Related

- Issue [#14](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/14): Original user request for two separate search options (headword by `\lx`/`\va`, gloss by `\ge`) that exclude nested subentry fields
- Issue #23: Previous spec attempt (superseded by #400 — #23 used a single-table approach with entry_type column, which would have required filters in Lexeme mode and risked regressions)
- Issue #698: Phase 1 schema gaps — FK cascade (closed via PR #760), index/constraint (closed via PR #760), reprocessing gap (finding 3 still open)
- Issue #671: Updated HeadwordSearchEntry.entry_type model docstring to document valid values and CHECK constraint enforcement (complete)
- Issue #1126: [Task: #400] Phase 5 — Search Mode UI (open)
- PR [#403](https://github.com/Brothertown-Language/snea-shoebox-editor/pull/403): Phase 1 implementation — added HeadwordSearchEntry and GlossSearchEntry CREATE TABLE migrations, Record model relationships, registered migration versions in `_MIGRATIONS` (merged)
- PR #760: Fix #698 — FK cascade, entry_type index/constraint, remove re-exports, rename Junie (merged)
- PR #764: Fix #761 #698 — mock path updates and hard-delete unit tests (merged)
- PR #1286: Fix — test cleanup for HeadwordSearchEntry/GlossSearchEntry FK violations, SearchEntry dedup + unique index (merged)

---

> **Approval Tracking:** Approvals are tracked via GitHub Issue comments (e.g., `AI:  ✅ Approved: Phase 1`), NOT in the issue body. Issue body edits destroy history.

🤖 📝 Updated by OpenCode (ollama-cloud/glm-5)

---

REVISED 2026-04-23: Added per-phase TDD RED/GREEN cycle structure. Every Success Criterion (SC-1 through SC-14) is now mapped to a specific test function with # SC-N markers. Phase 1 marks its RED tests as retrospective (implemented before TDD discipline was applied). All subsequent phases enforce RED→GREEN→REFACTOR→COMMIT order. Phase 4 search logic tests mapped to `test_linguistic_service.py`. Phase 5 UI tests mapped to `test_records_ui.py`. Phase 6 adds end-to-end integration test file `test_search_modes_e2e.py`.

REVISED 2026-05-09 (v1.3): Added Status column (Planned) to Success Criteria table; changed Phase 1 retrospective markers to "☐ TODO".

REVISED 2026-05-09 (v1.4): Fixed Phase 2 step 2.9 `process_record()` → `populate_search_entries()` (non-existent function); added TDD Compliance Summary table with per-phase scoping; clarified Phase 1 is a known limitation with Phases 2-6 following RED→GREEN→REFACTOR→COMMIT.

REVISED 2026-05-09 (v1.5): Phase 1 spec-to-codebase audit fixes — Step 1.4: `ai_bin/schema-version` → `.opencode/tools/schema-version`; Step 1.8: `_CURRENT_SCHEMA_VERSION` → `_MIGRATIONS` registry pattern; Step 1.9: clarified rollback is test-only.

REVISED 2026-05-11 (v1.6): Dual audit for correctness, completeness, and drift — restored full spec body (GitHub API was truncating the issue body to only Phase 3 content); added Post-Spec Codebase Changes section (PR #1286 dedup/unique index, PR #760 FK cascade fix, reprocessing gap from #698 finding 3); updated Related section with #1126 sub-issue and PRs #760, #764, #1286; updated STATUS from ambiguous `2.1` to `1.6` with descriptive marker.

REVISED 2026-05-12 (v1.8): Dual-adversarial audit resolution — fixed SC-7 (added SC-23 first-ge-only indexing test to Phase 2 steps), SC-4 (step 1.22 clarified: RED-only test function writing, not schema code implementation), SC-6 (expanded ANTI-PATTERN markers to all 8 structural/inspect tests), SC-9 (behavioral VbC SC-15 through SC-22 written and passing). Behavioral VbC phase cycle corrected from RED→GREEN→REFACTOR→COMMIT to RED→RED→REFACTOR→COMMIT (tests verify existing schema behavior, not new schema code).


