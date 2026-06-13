> **Full spec and artifacts: [`.issues/open/400-add-headword-gloss-search-modes/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/open/400-add-headword-gloss-search-modes)** — this issue IS the authoritative spec, mirrored in the `issues-data` branch at `open/400-add-headword-gloss-search-modes/spec.md`.

## Executive Summary

**Card 1: Requirement** — Add two focused search modes for dictionary workflow support.

| Dependency | Prerequisite | Status |
|---|---|---|
| Headword search mode | MUST search `\lx` and primary `\va` (headword-level variants only) | Core requirement |
| Gloss search mode | MUST search primary `\ge` only (headword-level, excludes subentry/cross-ref/sense glosses) | Core requirement |
| Lexeme/FTS preservation | MUST remain UNCHANGED — no entry_type filters, no logic changes | Regression invariant |

**Card 2: Architecture** — Two NEW dedicated tables isolate primary entries without affecting existing Lexeme mode.

| Decision | Rationale | Constraint |
|---|---|---|
| `HeadwordSearchEntry` table | PRIMARY lx + primary va only | entry_type CHECK constraint ('lx', 'va') |
| `GlossSearchEntry` table | PRIMARY ge only | No entry_type column |
| `SearchEntry` (EXISTING) | UNCHANGED — no new columns, no entry_type='ge' additions | Regression invariant |

**Card 3: Design Pattern** — Strategy-dispatch for search mode routing instead of elif chains.

**Key Decision:** DEC-1 (separate tables), DEC-2 (strategy dispatch), DEC-3 (headword default), DEC-4 (state tracking), DEC-5 (first-ge-only indexing).

**Risk Callout:** Migration corrupting SearchEntry would break Lexeme mode (RISK-1). Mitigated by separate tables — no changes to existing schema.

---

## Problem

**Issue [#14](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/14):** Users need two separate search options:
1. Search by Algonquian headword (`\lx`) and **primary** variants (`\va`)
2. Search by English definition (`\ge`)

**Current search modes:**
- **Lexeme**: Searches `\lx`, `\va`, `\se`, `\cf`, `\ve` (ALL entries, no distinction)
- **FTS**: Searches all fields

**Missing:** Focused searches for primary entries only, excluding nested/subentry fields.

**Per user clarification (Issue [#14](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/14) comments):**
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

## Decision Ledger

| DEC-ID | Decision | Rationale | Requirement Key | Affected SCs |
|--------|----------|-----------|-----------------|--------------|
| DEC-1 | Two NEW dedicated tables (HeadwordSearchEntry, GlossSearchEntry) instead of modifying SearchEntry | Separate table isolation avoids Lexeme mode regressions; no entry_type filters needed | MUST | SC-9, SC-10, SC-13 |
| DEC-2 | Strategy-dispatch pattern for search mode routing instead of elif chains | SRP compliance, extensibility for future modes | MUST | SC-7, SC-8 |
| DEC-3 | Headword as default search mode | User requirement per [#14](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/14) | MUST | SC-11 |
| DEC-4 | State tracking (in_headword_block) for identifying PRIMARY entries | Excludes nested/subentry entries from dedicated tables | MUST | SC-3, SC-5, SC-23 |
| DEC-5 | First-ge-only indexing in GlossSearchEntry | Spec requirement — only first `\ge` at headword level is indexed | MUST | SC-23 |

---

## Interfaces

### Database Models

**HeadwordSearchEntry**
- Columns: `id` (PK), `record_id` (FK &rarr; `records.id`, ON DELETE RESTRICT), `entry_type` (VARCHAR, CHECK 'lx' or 'va', NOT NULL), `term` (VARCHAR, NOT NULL), `normalized_term` (VARCHAR, indexed)
- Indexes: `record_id`, `entry_type`, `normalized_term`
- Relationships: `Record.headword_entries` (one-to-many, back_populates)

**GlossSearchEntry**
- Columns: `id` (PK), `record_id` (FK &rarr; `records.id`, ON DELETE RESTRICT), `term` (VARCHAR, NOT NULL), `normalized_term` (VARCHAR, indexed)
- Indexes: `record_id`, `normalized_term`
- Relationships: `Record.gloss_entries` (one-to-many, back_populates)
- Note: NO `entry_type` column &mdash; structural divergence from HeadwordSearchEntry

### Search Dispatch Interface

```
search_records(term: str | None, mode: Literal["Headword", "Gloss", "Lexeme", "FTS"]) -> Sequence[Record]
```

| Mode | Join Target | Filter | Behavior |
|------|-------------|--------|----------|
| Headword | `HeadwordSearchEntry` on `record_id` | Match on `normalized_term` | PRIMARY lx + va only |
| Gloss | `GlossSearchEntry` on `record_id` | Match on `normalized_term` | PRIMARY ge only |
| Lexeme | `SearchEntry` on `record_id` | Match on `normalized_term` | UNCHANGED &mdash; no entry_type filter |
| FTS | Full-text search branch | Full-text index | UNCHANGED |

Dispatch MUST use strategy-dispatch pattern (dictionary mapping mode name to join/filter callable), not elif chains.

### Upload Indexing Interface

```
populate_search_entries(record: Record) -> None
```

Side effects:
1. Populate `SearchEntry` with ALL `lx`, `va`, `se`, `cf`, `ve` (UNCHANGED)
2. Populate `HeadwordSearchEntry` with PRIMARY `lx` and primary `va` only (uses `in_headword_block` state tracking)
3. Populate `GlossSearchEntry` with FIRST primary `ge` only (uses `in_headword_block` state tracking)
4. Missing `\lx`: no HeadwordSearchEntry created (SC-26)

### UI State Interface

```
st.session_state.search_mode: str  # Default: "Headword"
```

| Property | Specification |
|----------|--------------|
| Default | `"Headword"` on session start (SC-11) |
| Radio layout | Vertical, Focused (Headword, Gloss) | Broad (Lexeme, FTS) groups |
| Grouping separators | `&mdash;&mdash; Focused &mdash;&mdash;`, `&mdash;&mdash; Broad &mdash;&mdash;` (SC-12) |
| Search header | `"Search: {mode} ({count} records)"` |
| Help text | `"HW: \\lx+\\va (primary) | Gloss: \\ge (primary) | LX: all markers | FTS: all fields"` |
| Action buttons | Search + Clear below radio group (full width) |

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

> **Cost-model note:** Each SC's evidence type reflects the defect-discovery-latency (DDL) hierarchy from `065-verification-honesty.md` §Cost Model. `behavioral` SCs catch defects at gate 1 (break dynamics — minutes DDL). `semantic` SCs catch at pre-PR (hours–days DDL). `structural` SCs verify file/table existence (weeks DDL — acceptable for schema-only checks).
>
> **Sample data convention:** All search result assertions in SC-1 through SC-6 refer to the single MDF example record shown in §MDF Structure Context (the `\lx wampuw` record). Deterministic assertions use exact record counts (0 or 1) from this single-record test fixture.

### Core Table

| SC | Criterion | Verification Method | Remediation |
|----|-----------|-------------------|-------------|
| SC-1 | Headword search finds primary lx — "wampuw" returns exactly 1 record | Behavioral test execution | Fix HeadwordSearchEntry join target |
| SC-2 | Headword search finds primary va — "wampu" returns exactly 1 record | Behavioral test execution | Fix HeadwordSearchEntry va indexing |
| SC-3 | Headword excludes nested va — "wampu-" returns 0 records | Behavioral test execution | Fix in_headword_block state tracking |
| SC-4 | Gloss search finds primary ge — "round object" returns exactly 1 record | Behavioral test execution | Fix GlossSearchEntry join target |
| SC-5 | Gloss excludes nested ge — "ball" returns 0 records | Behavioral test execution | Fix in_headword_block state tracking |
| SC-6 | Gloss excludes headword — "wampuw" returns 0 records | Behavioral test execution | Fix GlossSearchEntry query scope |
| SC-7 | Lexeme mode UNCHANGED — all variants returned, no entry_type filter | Behavioral test + code inspection | Restore original SearchEntry join |
| SC-8 | FTS mode UNCHANGED — no changes to FTS logic | Behavioral test + code inspection | Restore original FTS branch |
| SC-9 | headword_search_entries table exists with columns and indexes | Structural inspection (table existence) | Create migration |
| SC-10 | gloss_search_entries table exists with columns and indexes | Structural inspection (table existence) | Create migration |
| SC-11 | Headword default search mode — session state initializes to "Headword" | Semantic inspection (frontend test setup) | Fix session state default |
| SC-12 | UI vertical radio groupings — Focused/Broad separators | Semantic inspection (Streamlit component presence) | Fix UI rendering |
| SC-13 | Migration rollback safe — DROP new tables without data loss | Behavioral test (round-trip) | Fix migration script |
| SC-14 | Search performance < 500ms for all modes | Behavioral test (profiling) | Add indexes, optimize queries |
| SC-15 | Record.headword_entries relationship traversal | Behavioral test (ORM) | Fix back_populates |
| SC-16 | Record.gloss_entries relationship traversal | Behavioral test (ORM) | Fix back_populates |
| SC-17 | FK RESTRICT blocks record deletion (IntegrityError) | Behavioral test (DB constraint) | Fix FK policy |
| SC-18 | Headword entry_type CHECK constraint | Behavioral test (DB constraint) | Fix CHECK constraint |
| SC-19 | Headword requires entry_type (NOT NULL) | Behavioral test (DB constraint) | Fix NOT NULL |
| SC-20 | Gloss rejects entry_type (no column) | Behavioral test (schema divergence) | Fix GlossSearchEntry model |
| SC-21 | Multiple headword entries per record | Behavioral test (ORM collection) | Fix relationship cardinality |
| SC-22 | Multiple gloss entries per record | Behavioral test (ORM collection) | Fix relationship cardinality |
| SC-23 | Gloss indexes only first ge at headword level | Behavioral test execution | Fix first-ge-only logic |
| SC-24 | Empty search input returns all records without error/crash | Behavioral test execution | Fix empty input handler |
| SC-25 | Special characters no crash or SQL injection | Behavioral test execution | Fix sanitization/escaping |
| SC-26 | Records missing \lx excluded from headword results | Behavioral test execution | Fix null-lx filter |

### Metadata Table

| SC | Evidence Type | Phase Binding | Pipeline Step | Semantic Intent |
|----|--------------|---------------|---------------|-----------------|
| SC-1 | `behavioral` | Phase 4 | Query routing | Verifies query routing correctness — grep doesn't capture routing |
| SC-2 | `behavioral` | Phase 4 | Query routing | Primary va is a distinct code path from primary lx |
| SC-3 | `behavioral` | Phase 2/4 | State tracking | Essential negative test for in_headword_block exclusion |
| SC-4 | `behavioral` | Phase 4 | Query routing | Gloss mode uses GlossSearchEntry — different join target |
| SC-5 | `behavioral` | Phase 2/4 | State tracking | Cross-ref ge exclusion validates state tracking |
| SC-6 | `behavioral` | Phase 4 | Query routing | Ensures gloss mode doesn't accidentally match lx field |
| SC-7 | `behavioral` | Phase 4 | Search dispatch | Lexeme joins SearchEntry with NO filters |
| SC-8 | `behavioral` | Phase 4 | Search dispatch | FTS is a separate code path — no changes allowed |
| SC-9 | `structural` | Phase 1 | Schema | Table existence at audit time, not runtime |
| SC-10 | `structural` | Phase 1 | Schema | Same as SC-9 for gloss table |
| SC-11 | `semantic` | Phase 5 | UI | Session state initialization — verified by test setup |
| SC-12 | `semantic` | Phase 5 | UI | UI rendering — verified by Streamlit component presence |
| SC-13 | `behavioral` | Phase 1/3 | Migration | Rollback safety — restoring state without data loss |
| SC-14 | `behavioral` | Phase 4 | Performance | < 500ms ensures user-facing responsiveness |
| SC-15 | `behavioral` | Phase 1 | ORM | Relationship traversal — back_populates bidirectional |
| SC-16 | `behavioral` | Phase 1 | ORM | Same as SC-15 for gloss relationship |
| SC-17 | `behavioral` | Phase 1 | Schema | FK RESTRICT blocks cascade — DB-level enforcement |
| SC-18 | `behavioral` | Phase 1 | Schema | CHECK constraint at DB level — IntegrityError on invalid entry_type |
| SC-19 | `behavioral` | Phase 1 | Schema | NOT NULL — entry_type truly mandatory |
| SC-20 | `behavioral` | Phase 1 | Schema | Structural divergence — gloss has no entry_type column |
| SC-21 | `behavioral` | Phase 1 | ORM | One-to-many collection semantics |
| SC-22 | `behavioral` | Phase 1 | ORM | Same as SC-21 for gloss |
| SC-23 | `behavioral` | Phase 2 | Indexing | Spec requirement — multiple ge, only first indexed |
| SC-24 | `behavioral` | Phase 4 | Search | Empty input must not crash |
| SC-25 | `behavioral` | Phase 4 | Search | Sanitization — no injection or crash |
| SC-26 | `behavioral` | Phase 2 | Indexing | Records without lx excluded from headword results |

---

## Risk Traceability

| RISK-ID | Risk | Likelihood | Impact | Mitigation | Verifying SC |
|---------|------|------------|--------|------------|--------------|
| RISK-1 | Migration corrupts existing SearchEntry data | Low | High | Separate tables, no changes to existing table | SC-13 |
| RISK-2 | Indexing logic misses edge cases | Medium | Medium | Comprehensive test cases | SC-1–SC-6, SC-23 |
| RISK-3 | Grouped vertical radio UX confusion | Low | Low | Clear grouping headers | SC-12 |
| RISK-4 | Streamlit two-radio state sync | Medium | Low | Validate callback; fallback to single vertical radio | SC-12, SC-11 |
| RISK-5 | Performance regression | Low | Medium | Index new tables, profile query plans | SC-14 |
| RISK-6 | State tracking bugs | Medium | Medium | Unit tests for all MDF edge cases | SC-3, SC-5, SC-23 |
| RISK-7 | Search mode elif-chain growth (SRP violation) | Medium | Low | Strategy-dispatch pattern | SC-8 |

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
| Empty search input (no term submitted) | Return all records (no error/crash) — SC-24 |
| Special characters in search term | Normalize/escape; no crash or injection — SC-25 |
| Record missing `\lx` field | Excluded from HeadwordSearchEntry results — SC-26 |
| Unicode search terms | Normalize before query (existing behavior) |
| Nested `\ge` in subentries | Excluded via state tracking (`in_headword_block = False`) |
| Nested `\va` in subentries | Excluded from HeadwordSearchEntry (not indexed) |
| `\xv` marker | Exits headword block (structural boundary, same as `\va` in parser) |

---

## Regression Invariants

Behaviors that MUST NOT change:

1. Existing Lexeme mode MUST join SearchEntry WITHOUT entry_type filters
2. Existing FTS mode MUST remain UNCHANGED — no changes to FTS logic
3. Existing SearchEntry table structure MUST remain unchanged (no new columns, no entry_type='ge' additions)
4. Hard-delete record MUST cascade-delete HeadwordSearchEntry and GlossSearchEntry rows before Record deletion
5. All existing search API signatures MUST remain compatible

---

## Dependencies

| Phase | Depends On | Dependency Type | Rationale |
|-------|-----------|-----------------|-----------|
| Phase 1: Schema | None (foundation) | Hard | New tables must exist before any indexing |
| Phase 2: Indexing | Phase 1 | Hard | `populate_search_entries()` needs HeadwordSearchEntry and GlossSearchEntry tables |
| Phase 3: Migration | Phase 2 | Hard | Backfill uses `populate_search_entries()` with state tracking logic from Phase 2 |
| Phase 4: Search | Phase 3 | Hard | Search queries join HeadwordSearchEntry/GlossSearchEntry which must be populated |
| Phase 5: UI + Integration | Phases 1-4 | Hard | End-to-end tests require all layers present |

**External dependencies:** None beyond existing project stack (SQLAlchemy, Alembic, Streamlit, pytest).

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

## TDD Phases Overview

### Phase 1: Database Schema (Risk: HIGH, Blast Radius: SMALL)

**Interdependencies:** NONE (foundation layer, no dependencies)

**TDD Cycle Summary:**

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|-------|-----------------|-------------------|----------|--------|
| Phase 1: Schema | Structural tests + behavioral VbC tests | Schema migration, model relationships | Cleanup | Commit |

### Phase 2: Backend Indexing Logic (Risk: MEDIUM, Blast Radius: MEDIUM)

**Interdependencies:** Phase 1 (new tables must exist)

**TDD Cycle Summary:**

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|-------|-----------------|-------------------|----------|--------|
| Phase 2: Indexing | Indexing tests | populate_search_entries state tracking | Cleanup | Commit |

### Phase 3: Migration for Existing Data (Risk: MEDIUM, Blast Radius: MEDIUM)

**Interdependencies:** Phase 2 (indexing logic ready)

**TDD Cycle Summary:**

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|-------|-----------------|-------------------|----------|--------|
| Phase 3: Migration | Migration tests | Backfill script, verify data | Cleanup | Commit |

### Phase 4: Backend Search Logic (Risk: MEDIUM, Blast Radius: MEDIUM)

**Interdependencies:** Phase 3 (new tables populated with existing data)

**TDD Cycle Summary:**

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|-------|-----------------|-------------------|----------|--------|
| Phase 4: Search | Search mode tests | Strategy dispatch, queries | Cleanup | Commit |

### Phase 5: Frontend UI Controls + Integration Verification (Risk: LOW, Blast Radius: SMALL)

**Interdependencies:** Phase 4 (backend must support new search modes); all prior phases (for integration tests)

**TDD Cycle Summary:**

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|-------|-----------------|-------------------|----------|--------|
| Phase 5: UI | UI tests | Radio groups, default mode | Cleanup | Commit |
| Phase 5: Integration | Integration tests | Full end-to-end verification | Cleanup | Commit |

---

## Files Affected

| File | Concern | Changes |
|------|---------|---------|
| `src/database/models/search.py` | Database schema | Add HeadwordSearchEntry, GlossSearchEntry tables |
| `src/database/models/core.py` | Record model | Add headword_entries, gloss_entries relationships |
| `src/database/migrations.py` | Migrations | Add CREATE TABLE migrations for new tables |
| `src/services/upload_service.py` | Indexing logic | Add state tracking for PRIMARY entries, populate ALL THREE tables |
| `src/services/linguistic_service.py` | Backend search | Add strategy-dispatch for Headword/Gloss modes; handle empty input and special characters |
| `src/frontend/pages/records.py` | Frontend UI | Vertical radio with grouping; Headword default; active mode in header |
| `tests/services/test_linguistic_service.py` | Test coverage | Add tests for Headword, Gloss modes, empty input, special characters |
| `tests/services/test_upload_service.py` | Test coverage | Add tests for indexing state tracking, missing lx exclusion |
| `tests/database/test_migration_manager.py` | Test coverage | Add tests for schema and migration |
| `tests/frontend/test_records_ui.py` | Test coverage | Add tests for UI changes |
| `tests/integration/test_search_modes_e2e.py` | Test coverage | Integration tests for all search modes |

---

## Revision Policy

| Artifact | Cascade Trigger | Action on Parent Revision |
|----------|-----------------|--------------------------|
| Implementation plan | MUST | Revise to match revised spec |
| Behavioral tests | SHOULD | Review for continued validity |
| Risk traceability | MAY | Update if new risks introduced |

---

## Documentation Sources

| Source | Type | Relevance |
|--------|------|-----------|
| [Shoebox/MDF standard (SIL)](https://software.sil.org/shoebox/) | External specification | MDF marker format (\lx, \ge, \va, \se, \cf, \xv) and nesting semantics for headword/subentry structures |
| [Standard Format (aka MDF) Reference](https://www.sil.org/resources/archives/700) | External specification | Complete marker reference for `\lx` headword blocks, `\va` variants, `\ge` glosses, `\se` subentries, `\cf` cross-references |
| [Issue #14](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/14) | Internal requirement | Original user request for headword/gloss search modes |
| [Issue #23](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/23) | Internal spec | Previous single-table approach (superseded) |
| [Issue #698](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/698) | Internal spec | Phase 1 schema gap findings (closed) |
| [Issue #671](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/671) | Internal issue | entry_type model docstring update |
| [Issue #1126](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1126) | Internal task | Phase 5 implementation sub-issue |
| [PR #403](https://github.com/Brothertown-Language/snea-shoebox-editor/pull/403) | Internal code | Phase 1 implementation |
| [PR #760](https://github.com/Brothertown-Language/snea-shoebox-editor/pull/760) | Internal code | Fix #698 — FK cascade, entry_type index/constraint |
| [PR #764](https://github.com/Brothertown-Language/snea-shoebox-editor/pull/764) | Internal code | Mock path updates and hard-delete unit tests |
| [PR #1286](https://github.com/Brothertown-Language/snea-shoebox-editor/pull/1286) | Internal code | SearchEntry dedup + unique index |

---

## Related

- [Issue #14](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/14): Original user request for two separate search options (headword by `\lx`/`\va`, gloss by `\ge`) that exclude nested subentry fields
- [Issue #23](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/23): Previous spec attempt (superseded by #400 — used a single-table approach with entry_type column)
- [Issue #698](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/698): Phase 1 schema gaps — FK cascade (closed via [PR #760](https://github.com/Brothertown-Language/snea-shoebox-editor/pull/760)), index/constraint (closed via [PR #760](https://github.com/Brothertown-Language/snea-shoebox-editor/pull/760)), reprocessing gap (finding 3 still open)
- [Issue #671](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/671): Updated HeadwordSearchEntry.entry_type model docstring (complete)
- [Issue #1126](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1126): [Task: #400] Phase 5 — Search Mode UI (open)
- [PR #403](https://github.com/Brothertown-Language/snea-shoebox-editor/pull/403): Phase 1 implementation (merged)
- [PR #760](https://github.com/Brothertown-Language/snea-shoebox-editor/pull/760): Fix [#698](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/698) — FK cascade, entry_type index/constraint (merged)
- [PR #764](https://github.com/Brothertown-Language/snea-shoebox-editor/pull/764): Fix [#761](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/761) [#698](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/698) (merged)
- [PR #1286](https://github.com/Brothertown-Language/snea-shoebox-editor/pull/1286): SearchEntry dedup + unique index (merged)

---

> **Approval Tracking:** Approvals are tracked via GitHub Issue comments (e.g., `AI: ✅ Approved: Phase 1`), NOT in the issue body. Issue body edits destroy history.

🤖 📝 Updated by OpenCode (ollama-cloud/deepseek-v4-flash)