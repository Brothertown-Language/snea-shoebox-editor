---
issue: 400
phase: 1
type: test-artifacts
branch: feature/400-phase1-retroactive-tests
date: "2026-05-11"
---

# Phase 1 Retroactive Test Artifacts

## Test File

`tests/database/test_migration_manager.py` — 18 tests total (7 original + 11 Phase 1)

## Test Classes and Methods

### TestHeadwordSearchEntrySchema (SC-9)

| # | Test Method | Verifies | SC |
|---|-------------|----------|----|
| 1 | `test_headword_search_entry_table_exists` | `headword_search_entries` table exists | SC-9 |
| 2 | `test_headword_search_entry_columns` | Columns: id, record_id, entry_type, term, normalized_term | SC-9 |
| 3 | `test_headword_search_entry_indexes` | Indexes on record_id, entry_type, normalized_term | SC-9 |
| 4 | `test_headword_search_entry_foreign_key` | record_id FK → records.id | SC-9 |
| 5 | `test_headword_search_entry_orm_roundtrip` | ORM create/read roundtrip with Source+Record | SC-9 |

### TestGlossSearchEntrySchema (SC-10)

| # | Test Method | Verifies | SC |
|---|-------------|----------|----|
| 1 | `test_gloss_search_entry_table_exists` | `gloss_search_entries` table exists | SC-10 |
| 2 | `test_gloss_search_entry_columns` | Columns: id, record_id, term, normalized_term (NO entry_type) | SC-10 |
| 3 | `test_gloss_search_entry_indexes` | Indexes on record_id, normalized_term | SC-10 |
| 4 | `test_gloss_search_entry_foreign_key` | record_id FK → records.id | SC-10 |
| 5 | `test_gloss_search_entry_orm_roundtrip` | ORM create/read roundtrip with Source+Record | SC-10 |

### TestSearchEntryRollback (SC-13)

| # | Test Method | Verifies | SC |
|---|-------------|----------|----|
| 1 | `test_drop_and_recreate_preserves_search_entries` | DROP + recreate HeadwordSearchEntry/GlossSearchEntry idempotent; SearchEntry count preserved | SC-13 |

## Test Run Results

```
18 passed in 1.35s
```

Idempotency verified across multiple runs.

## Design Decisions

- Combined Phase 1.3 rollback test into single method to avoid test ordering/state issues with module-scoped DB
- Used `uuid.uuid4().hex[:8]` suffixes for Source/Record names to prevent cross-test collisions
- Rollback test uses raw SQL `CREATE TABLE IF NOT EXISTS` + `CREATE INDEX IF NOT EXISTS` (not `MigrationManager.run_all()` — `_run_migrations` skips when `current >= version`)
- Record model requires `source_id` (NOT NULL FK) and `mdf_data` — all ORM roundtrip tests create Source + Record first
- GlossSearchEntry has no `entry_type` column (unlike HeadwordSearchEntry)

## Spec Drift Fix

Step 1.4 corrected: `uv run .opencode/tools/schema-version` → `./.opencode/tools/schema-version`
(PEP 723 self-executing script with shebang `#!/usr/bin/env -S uv run --script`)