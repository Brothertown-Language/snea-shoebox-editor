# Plan: Phase 3 — Migration for Existing Data

**Issue:** [#1306](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1306)
**Parent:** [#400](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/400) — Add Headword and Gloss Search Modes
**Goal:** Backfill `HeadwordSearchEntry` and `GlossSearchEntry` tables for existing records using Phase 2's `populate_search_entries()` method. Migration must be rollback-safe (SC-13).
**Architecture:** MigrationManager → `_migrate_backfill_search_entries()` → `UploadService.populate_search_entries()` → 3 search entry tables
**Tech Stack:** Python 3.12+, SQLAlchemy ORM, PostgreSQL, pytest

---

## Phase 3: Migration — Backfill New Tables for Existing Records

**Concern (entering):** Migration registry — a new migration method that queries all non-deleted records and calls `populate_search_entries()` for their IDs. Must use the same session pattern as `_migrate_reprocess_all_records`.

**Concern (leaving):** Migration applied — all existing records have `HeadwordSearchEntry` and `GlossSearchEntry` entries populated. Rollback (DROP new tables) causes zero data loss to `SearchEntry` or `records`.

**Handoff from Phase 2:** `populate_search_entries()` in `UploadService` already handles all three tables (SearchEntry, HeadwordSearchEntry, GlossSearchEntry) for given record IDs. Phase 3 calls it for all existing records.

**Files affected:** `src/database/migrations.py`
**SCs covered:** SC-13

### Dispatch Table

| Gate | Dispatch Type | Blind? | Sub-Agent Type | Receives Context | SCs |
|------|--------------|--------|----------------|-----------------|-----|
| G1: sc-coherence-gate | sub-task | yes (blind) | general | `{"task": "execute sc-coherence-gate from implementation-pipeline", "issue_number": 1306, "phase": 3}` | SC-13 |
| G2: pre-red-baseline | sub-task | yes (blind) | general | `{"task": "execute pre-red-baseline from implementation-pipeline", "issue_number": 1306, "phase": 3}` | SC-13 |
| G3: red-phase | sub-task | yes (blind) | general | `{"task": "execute red-phase from implementation-pipeline", "issue_number": 1306, "phase": 3}` | SC-13 |
| G4: red-doublecheck | sub-task | yes (blind) | general | `{"task": "execute red-doublecheck from implementation-pipeline", "issue_number": 1306, "phase": 3}` | SC-13 |
| G5: post-red-enforcement | sub-task | yes (blind) | general | `{"task": "execute post-red-enforcement from implementation-pipeline", "issue_number": 1306, "phase": 3}` | SC-13 |
| G6: green-phase | sub-task | yes (blind) | general | `{"task": "execute green-phase from implementation-pipeline", "issue_number": 1306, "phase": 3}` | SC-13 |
| G7: post-green-enforcement | sub-task | yes (blind) | general | `{"task": "execute post-green-enforcement from implementation-pipeline", "issue_number": 1306, "phase": 3}` | SC-13 |
| G8: checkpoint-commit | inline | N/A | N/A | — | SC-13 |
| G9: structural-checks | sub-task | yes (blind) | general | `{"task": "execute structural-checks from implementation-pipeline", "issue_number": 1306, "phase": 3}` | SC-13 |
| G10: green-doublecheck | sub-task | yes (blind) | general | `{"task": "execute green-doublecheck from implementation-pipeline", "issue_number": 1306, "phase": 3}` | SC-13 |
| G11: green-vbc | sub-task | yes (blind) | general | `{"task": "execute green-vbc from implementation-pipeline", "issue_number": 1306, "phase": 3}` | SC-13 |
| G12: adversarial-audit | sub-task | yes (blind) | general | `{"task": "execute adversarial-audit from implementation-pipeline", "issue_number": 1306, "phase": 3}` | SC-13 |
| G13: cross-validate | sub-task | yes (blind) | general | `{"task": "execute cross-validate from implementation-pipeline", "issue_number": 1306, "phase": 3}` | SC-13 |
| G14: regression-check | sub-task | yes (blind) | general | `{"task": "execute regression-check from implementation-pipeline", "issue_number": 1306, "phase": 3}` | SC-13 |
| G15: review-prep | sub-task | yes (blind) | general | `{"task": "execute review-prep from implementation-pipeline", "issue_number": 1306, "phase": 3}` | SC-13 |
| G16: exec-summary | sub-task | yes (blind) | general | `{"task": "execute exec-summary from implementation-pipeline", "issue_number": 1306, "phase": 3}` | SC-13 |

### Per-Unit Pipeline Gate Table

| Gate | Name | Exit Criterion |
|------|------|----------------|
| 1 | sc-coherence-gate | Spec/plan coherence verified — migration scope matches spec intent |
| 2 | pre-red-baseline | Source currency documented; SC-ID cross-ref traceability established |
| 3 | red-phase | Behavioral tests for SC-13 FAIL because migration does not exist yet |
| 4 | red-doublecheck | RED-side SC evidence collected — test output shows expected failures |
| 5 | post-red-enforcement | `git diff --name-only -- src/` shows zero src/ changes |
| 6 | green-phase | `_migrate_backfill_search_entries()` added to `MigrationManager` and registered in `_MIGRATIONS`; all behavioral tests PASS |
| 7 | post-green-enforcement | `git diff --name-only -- test/` shows test file changes exist |
| 8 | checkpoint-commit | Phase 3 changes committed with descriptive message |
| 9 | structural-checks | `ruff check --fix`, `ruff format`, `pyright` all pass on `src/database/migrations.py` and test files |
| 10 | green-doublecheck | Semantic-intent verification: migration calls `populate_search_entries()` for all non-deleted records; rollback-safe |
| 11 | green-vbc | SC-13 verified before completion |
| 12 | adversarial-audit | Dual-auditor PASS on migration changes |
| 13 | cross-validate | Consensus PASS between auditors |
| 14 | regression-check | All existing tests pass; `SearchEntry` population unchanged |
| 15 | review-prep | PR diff reviewed; compare URL generated |
| 16 | exec-summary | Push complete; issue comment posted |

### TDD Steps

#### Item 3.1: Create backfill migration method

**RED condition:** Existing records do NOT have `HeadwordSearchEntry` or `GlossSearchEntry` entries. A test querying `session.query(HeadwordSearchEntry).count()` and `session.query(GlossSearchEntry).count()` returns 0 for records that were created before the migration. The behavioral test FAILS.

**GREEN condition:** `_migrate_backfill_search_entries()` method added to `MigrationManager`. It queries all non-deleted records, collects their IDs, and calls `populate_search_entries(record_ids=all_ids, session=session)`. After running the migration, the test query returns >0 entries. The behavioral test PASSES.

**Implementation:**
- Add `_migrate_backfill_search_entries(self)` method to `MigrationManager` (following the same pattern as `_migrate_reprocess_all_records` at line 655)
- Method queries `Record` for all non-deleted records (`session.query(Record).filter(Record.deleted_at.is_(None))`)
- Collects `record.id` into a list
- Calls `UploadService.populate_search_entries(record_ids=all_ids, session=session)`
- Commits the session
- Migration version: `20260615125509`
- Description: `"Backfill HeadwordSearchEntry and GlossSearchEntry for existing records"`

**Test file:** `test/test_migration_backfill_search_entries.py`

#### Item 3.2: Register migration in _MIGRATIONS list

**RED condition:** Migration version `20260615125509` is NOT in `MigrationManager._MIGRATIONS`. A test asserting `any(v == 20260615125509 for v, _, _ in MigrationManager._MIGRATIONS)` FAILS.

**GREEN condition:** The tuple `(20260615125509, "_migrate_backfill_search_entries", "Backfill HeadwordSearchEntry and GlossSearchEntry for existing records")` is added to `_MIGRATIONS` list (before the closing `]` at line 127). The test PASSES.

**Implementation:**
- Add entry to `_MIGRATIONS` list at line ~127 (before the closing bracket)
- Follow existing format: `(20260615125509, "_migrate_backfill_search_entries", "Backfill HeadwordSearchEntry and GlossSearchEntry for existing records"),`

#### Item 3.3: Verify rollback safety (SC-13)

**RED condition:** A test that drops `headword_search_entries` and `gloss_search_entries` tables, then verifies `SearchEntry` and `records` data is intact, FAILS because the test doesn't exist yet.

**GREEN condition:** The test PASSES — dropping the two new tables has zero effect on `SearchEntry` or `records` data. The migration is inherently rollback-safe because it only adds data to new tables (no schema changes to existing tables, no data written to existing tables).

**Implementation:**
- The migration is inherently rollback-safe: it only calls `populate_search_entries()` which writes to `HeadwordSearchEntry` and `GlossSearchEntry` tables
- No changes to `SearchEntry` schema, `records` schema, or any existing table
- Rollback = `DROP TABLE headword_search_entries, gloss_search_entries` — no data loss
- The test verifies this by simulating the rollback and checking data integrity

---

## Post-All-Phases Sweep

- [ ] FINISHING CHECKLIST — orchestrator routes to finishing sub-agent: `git status` clean, lint/typecheck from scratch, coverage sweep
- [ ] PR CREATION — orchestrator routes to `git-workflow` pr-creation: via `github_create_pull_request`, extract `html_url` from response
- [ ] POST-MERGE CLEANUP — orchestrator routes to `git-workflow` cleanup: delete merged branches, close issues, sync dev
