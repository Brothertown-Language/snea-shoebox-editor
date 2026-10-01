---
remote_issue: 1394
remote_url: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1394
promoted_at: 2026-10-01T13:10:00Z
labels:
  - needs-approval
---

# [SPEC-FIX] sync_prod_to_local DDL builder drops vector typmod and nextval column defaults

> Full spec and plan artifacts: https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/1394/

## Problem

Every `bash scripts/sync_prod_to_local.sh` run (mandated by AGENTS.md Regression Test Protocol) leaves the local database schema degraded — vector columns lose their `(384)` typmod and autoincrement columns lose their `nextval` defaults — producing 5 pre-existing test failures that block the TDD phase-0 pre-regression baseline on any synced database. Full suite after sync at trunk tip `eb467b8`: `5 failed, 169 passed, 8 skipped`.

## Scope

- Fix the `CREATE TABLE` builder in `scripts/sync_prod_to_local.py` so `vector` columns are rebuilt as `vector(384)` instead of bare `vector`.
- Restore `nextval(...)` column defaults that the builder strips, so ORM inserts omitting `id` succeed after sync.
- Re-run `scripts/sync_prod_to_local.sh` and verify the full test suite is green on the freshly synced database.
- Verify both defects against live local-DB evidence (`pg_attribute.atttypmod`, `pg_attrdef`) before and after the fix.

**Out of scope:**

- Sequence creation itself (already handled; closed issues #1314 / #1316).
- The unrelated 5 pre-existing failures tracked in #1388 (stale-RED Search Mode UI tests + `sys.modules` mock leak).
- Search Mode UI RED tests tracked in #1347.
- Changes to `src/database/migrations.py` or production schema — only the local sync reconstruction path is touched.

## Approach

Apply the same `atttypmod` handling the builder already performs for `character varying` to `vector` columns, emitting `vector({typmod})` when `atttypmod > -1`. Then either emit `nextval` defaults directly in the rebuilt DDL or re-add them via `ALTER TABLE ... SET DEFAULT` after `CREATE TABLE`, keeping the existing sequence-reset step intact. Finally, re-run a fresh sync and the full pytest suite to confirm the 5 baseline failures are gone with no regressions.

## Impact

- **Risk:** other column types may also lose typmod/constraint fidelity — mitigate by auditing the full CASE builder for remaining `atttypmod`/default gaps during the fix.
- **Risk:** re-adding defaults could conflict with the existing sequence-reset step — mitigate by verifying `pg_attrdef` contents and ORM insert behavior after sync.
- **Risk:** fix may expose additional previously masked failures — mitigate by treating any new failure as a separate finding, not part of this fix.

Key dependency: `scripts/sync_prod_to_local.sh` remains the mandated pre-regression sync entry point; this fix must not change its invocation contract. Call to action: after merge, the TDD phase-0 pre-regression baseline must pass on a freshly synced database.

---

## Detailed Findings

### Failing tests (5)

- `test/test_semantic_search_schema_sc3.py::test_gloss_search_entries_embedding_is_vector384`
- `test/test_semantic_search_schema_sc3.py::test_semantic_search_entries_embedding_is_vector384`
- `test/test_upload_search_entries.py::test_sc8_upload_row_count` (plus the other 2 `test_sc8_*` tests)

All 5 are pre-existing at trunk tip `eb467b8` with zero issue-#1392 changes in the working tree — verified on branch `feature/1392-maintainer-contact-placeholder` (clean tree, branch at trunk tip).

### Root cause

Both defects are in the `scripts/sync_prod_to_local.py` DDL reconstruction (`CREATE TABLE` builder).

**Defect 1 — vector typmod lost (2 failures):** the column-type CASE maps `t.typname = 'vector'` to bare `vector`. `a.atttypmod` is selected but only applied for `character varying`. `src/database/migrations.py` and the schema tests assert `vector(384)`.

Live evidence (local DB after sync, `psql` via socket `tmp/local_db`):

```
 table_name           | column_name | full_type
----------------------+-------------+-----------
 records               | embedding   | vector
 gloss_search_entries  | embedding   | vector
 semantic_search_entries | embedding | vector
```

Expected: `vector(384)`.

**Defect 2 — `nextval` column defaults stripped, never re-added (3 failures):** the builder excludes `nextval` from rebuilt defaults (`if "nextval" not in info_default:`) and no later step re-adds them. The sequence exists (`records_id_seq` in `pg_sequences`) but the column has no `DEFAULT`, so ORM inserts omitting `id` fail.

Live evidence:

```
SELECT pg_get_expr(adbin, adrelid) FROM pg_attrdef WHERE adrelid='records'::regclass;
 now()
 false
(2 rows)          -- no nextval default
```

Failure: `IntegrityError: null value in column "id" of relation "records" violates not-null constraint`.

### Relationship to existing issues

- **#1314** (closed) — created missing *sequences* post-sync; did not restore *column defaults*. Distinct mechanism; defect 2 here is still live.
- **#1388** (open) — different 5 pre-existing failures (stale-RED `test_search_mode_ui_red.py` + `sys.modules` leak in `test_migration_backfill_search_entries.py`). Not these tests.
- **#1347** (open) — Search Mode UI RED tests. Not these tests.
- No existing issue covers the vector-typmod or nextval-default defects.

### Success criteria

- After a fresh sync, `format_type(atttypid, atttypmod)` output for every `embedding` column exactly matches production: `records.embedding` = `vector(1536)`, `gloss_search_entries.embedding` = `vector(384)`, `semantic_search_entries.embedding` = `vector(384)`.
- After a fresh sync, `records.id` (and other ORM-autoincrement `id` columns) carry their `nextval` defaults.
- Full test suite after sync: 0 failures (the 5 baseline failures gone, no new failures).
- TDD phase-0 pre-regression baseline passes on a synced database for subsequent pipelines.

---

## Change Control

- **2026-10-01** — SC1 wording synced to verified production state (guideline 130 documentation-drift sync): production `records.embedding` is `vector(1536)`, not `vector(384)`; `gloss_search_entries` and `semantic_search_entries` are `vector(384)`. SC1 now requires the fresh sync to exactly reproduce production typmod per column. Non-substantive wording sync — no change to implementation intent, scope, or evidence type (behavioral live-DB verification unchanged); the criterion is strengthened in precision, not weakened. Pipeline-initiated; no developer re-authorization required per approval-gate-008.

---

🤖 OpenCode (opencode/mimo-v2.6-flash-free) created
🤖 Co-authored with AI: OpenCode (opencode/mimo-v2.6-flash-free)
