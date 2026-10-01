---
remote_issue: 1394
remote_url: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1394
promoted_at: 2026-10-01T13:10:00Z
labels:
  - needs-approval
---

# [SPEC-FIX] sync_prod_to_local DDL builder drops vector typmod and nextval column defaults

> Full spec and plan artifacts: https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/1394/

## Preamble

1. **Problem Statement:** Every `bash scripts/sync_prod_to_local.sh` run (mandated by AGENTS.md Regression Test Protocol) leaves the local database schema degraded — vector columns lose their typmod (`records.embedding` rebuilds as bare `vector` instead of `vector(1536)`) and autoincrement columns lose their `nextval` defaults (`records.id` inserts fail with `IntegrityError: null value in column "id"`) — producing 5 pre-existing test failures that block the TDD phase-0 pre-regression baseline on any synced database. Full suite after sync at trunk tip `eb467b8`: `5 failed, 169 passed, 8 skipped`.
2. **Root Cause / Motivation:** The `CREATE TABLE` builder in `scripts/sync_prod_to_local.py` emits a bare `vector` type for `vector` columns in its column-type CASE (it applies `atttypmod` only for `character varying`), and its defaults guard `if "nextval" not in info_default:` deliberately strips `nextval` default expressions from rebuilt DDL. The defect is in the local sync reconstruction path only — production schema is correct. It must be solved now because the degraded schema fails the mandated pre-regression sync protocol on every run, blocking all TDD phase-0 baselines on synced databases.
3. **Approach Chosen:** Apply the same `atttypmod` handling the builder already performs for `character varying` to `vector` columns, emitting `vector({typmod})` when `atttypmod > -1`, and emit the introspected `pg_attrdef` `nextval(...)` expression directly in the rebuilt CREATE TABLE column line (remove the stripping guard). Keep the existing sequence-reset step intact. Then re-run a fresh sync and the full pytest suite to verify the 5 documented baseline failures are green with no additional failures versus the pre-fix suite.
4. **Alternatives Considered & Why Discarded:** `ALTER TABLE ... SET DEFAULT nextval(...)` as a post-CREATE pass over the synced schema — discarded in favor of emitting `DEFAULT nextval(...)` directly in the rebuilt DDL: the single-pass approach avoids a post-DDL mutation step entirely, and the builder already introspects `info_default` from `pg_attrdef`, so the introspected expression can be emitted verbatim in the column line with no additional machinery.
5. **Key Design Decisions:** (a) Apply `atttypmod` for `vector` columns **without** the -4 offset used elsewhere — pgvector stores precision directly in `atttypmod`; (b) enumerate the 16-column autoincrement set from the live production catalog rather than leaving it an open set — a fixed, verified enumeration keeps SC4 deterministic; (c) drop the former SC4 ceremony criterion ("TDD phase-0 baseline passes") because it is entailed by the suite-green SCs (SC5/SC6) — a green full suite is a superset of the 5-failure baseline set passing.
6. **User Intent / Original Prompt:** The developer authorized stacking the #1394 fix into `feature/1392-maintainer-contact-placeholder` after the 5 pre-existing failures blocked the #1392 phase-0 baseline; the fix is dispatched via the spec-creation revise task against aggregate-FAIL validation findings.

## Problem

Every `bash scripts/sync_prod_to_local.sh` run (mandated by AGENTS.md Regression Test Protocol) leaves the local database schema degraded — vector columns lose their typmod and autoincrement columns lose their `nextval` defaults — producing 5 pre-existing test failures that block the TDD phase-0 pre-regression baseline on any synced database. Full suite after sync at trunk tip `eb467b8`: `5 failed, 169 passed, 8 skipped`.

## Scope

- Fix the `CREATE TABLE` builder in `scripts/sync_prod_to_local.py` so `vector` columns are rebuilt with their production typmod: `records.embedding` = `vector(1536)`, `gloss_search_entries.embedding` = `vector(384)`, `semantic_search_entries.embedding` = `vector(384)` — exactly matching production.
- Restore `nextval(...)` column defaults that the builder strips, so ORM inserts omitting `id` succeed after sync. The full set of affected columns is enumerated in SC4 (from the live production catalog).
- Re-run `scripts/sync_prod_to_local.sh` and verify the documented 5-failure baseline set is green and no new failures appear versus the pre-fix suite.
- Verify all sync outcomes against live local-DB evidence (`pg_attribute.atttypmod`, `pg_attrdef`) before and after the fix.

**Out of scope:**

- Sequence creation itself (already handled; closed issues #1314 / #1316).
- The unrelated 5 pre-existing failures tracked in #1388 (stale-RED Search Mode UI tests + `sys.modules` mock leak).
- Search Mode UI RED tests tracked in #1347.
- Changes to `src/database/migrations.py` or production schema — only the local sync reconstruction path is touched.

## Approach

Single path — no either/or alternatives. Apply the same `atttypmod` handling the builder already performs for `character varying` to `vector` columns, emitting `vector({typmod})` when `atttypmod > -1`. Emit the `DEFAULT nextval(...)` clause **directly in the rebuilt DDL** (the builder already introspects `pg_attrdef` via `info_default`; the guard `if "nextval" not in info_default:` currently strips it — remove the stripping so the introspected expression is emitted verbatim in the CREATE TABLE column line). Keep the existing sequence-reset step intact. Then re-run a fresh sync and the full pytest suite: the 5 documented baseline failures must be green with no additional failures versus the pre-fix suite.

## Requirements

- **R-1** — The `CREATE TABLE` builder SHALL emit `vector({typmod})` for `vector` columns when `atttypmod > -1`, using the same `atttypmod` handling already applied to `character varying`.
- **R-2** — The builder SHALL emit the `DEFAULT nextval(...)` clause directly in the rebuilt DDL column definition for every column whose production `pg_attrdef` expression is a `nextval` expression. The existing sequence-reset step SHALL be preserved and MUST NOT conflict with the emitted default.
- **R-3** — `scripts/sync_prod_to_local.sh` invocation contract SHALL remain unchanged (CLI surface untouched; fix internal to the DDL builder). *(Evidence type: structural — script-contract invariant.)*
- **R-4** — `src/database/migrations.py` and the production schema SHALL NOT be modified. *(Evidence type: structural — git-diff invariant.)*
- **R-5** — During the fix, the remaining column-type CASE branches SHALL be audited for other typmod/default fidelity gaps; any additional gap found SHALL be reported as a separate finding, not silently fixed in this scope.
- **R-6** — `test/test_semantic_search_schema_sc3.py` and `test/test_upload_search_entries.py` SHALL remain read-only baseline evidence — no test modifications.

## Success Criteria

Every SC is atomic. Per-SC Evidence Type and Verification Method are declared; EVIDENCE_TYPE_MISMATCH is a hard FAIL and must not be defaulted.

| SC | Statement | Evidence Type | Verification Method |
|----|-----------|---------------|---------------------|
| SC1 | After a fresh sync, `format_type(atttypid, atttypmod)` output for `records.embedding` is exactly `vector(1536)`, matching production. | behavioral (live-DB) | Live `psql` query against local replica via socket `tmp/local_db` after sync run |
| SC2 | After a fresh sync, `format_type(atttypid, atttypmod)` output for `gloss_search_entries.embedding` is exactly `vector(384)`, matching production. | behavioral (live-DB) | Live `psql` query against local replica via socket `tmp/local_db` after sync run |
| SC3 | After a fresh sync, `format_type(atttypid, atttypmod)` output for `semantic_search_entries.embedding` is exactly `vector(384)`, matching production. | behavioral (live-DB) | Live `psql` query against local replica via socket `tmp/local_db` after sync run |
| SC4 | After a fresh sync, every column in the enumerated production set of `nextval`-defaulted columns carries its `nextval` default in `pg_attrdef`, verbatim from production. The enumerated set (verified by live read-only production catalog query, 2026-10-01): `edit_history.id`, `fts_entries.id`, `gloss_search_entries.id`, `headword_search_entries.id`, `languages.id`, `matchup_queue.id`, `permissions.id`, `record_languages.id`, `records.id`, `schema_version.id`, `search_entries.id`, `semantic_search_entries.id`, `sources.id`, `user_activity_log.id`, `user_preferences.id`, `users.id`. The verified failing case at baseline is `records.id` (`IntegrityError: null value in column "id"`). | behavioral (live-DB) | Live `psql` query on `pg_attrdef` for all 16 enumerated columns after sync run; ORM insert omitting `id` succeeds (`test_sc8_*`) |
| SC5 | After a fresh sync, the documented 5-failure baseline set at trunk tip `eb467b8` is green: 2 vector-typmod failures in `test/test_semantic_search_schema_sc3.py` (`test_gloss_search_entries_embedding_is_vector384`, `test_semantic_search_entries_embedding_is_vector384`) and 3 NotNullViolation null-`id` failures in `test/test_upload_search_entries.py` (`test_sc8_upload_row_count` and the other 2 `test_sc8_*` tests). | behavioral (test-suite) | Full pytest run after fresh sync; the 5 named tests report PASS |
| SC6 | After a fresh sync, the full pytest suite reports no failures beyond the pre-fix suite state: exactly the pre-fix `169 passed, 8 skipped` set plus the 5 baseline failures of SC5 now passing — i.e., zero failures and zero new failures versus the pre-fix suite at trunk tip `eb467b8` (`5 failed, 169 passed, 8 skipped`). This is a deterministic comparison against the documented baseline set, not an open-ended "no new failures" assertion. | behavioral (test-suite) | Full pytest run output compared against the documented pre-fix baseline (5 failed / 169 passed / 8 skipped at trunk tip `eb467b8`) |
| SC7 | After the fix, the `scripts/sync_prod_to_local.sh` invocation contract and CLI surface are unchanged — no command, argument, environment variable, or exit-code contract present at trunk tip `eb467b8` is altered by this fix. | structural | `git diff` against trunk tip `eb467b8` showing no change to `scripts/sync_prod_to_local.sh` |
| SC8 | After the fix, `src/database/migrations.py` and the production schema are untouched — no modification to migrations source or any production DDL artifact attributable to this fix. | structural | `git diff` against trunk tip `eb467b8` showing no change under `src/database/` or production schema artifacts |
| SC9 | After the fix, an audit of the DDL-builder column-type CASE in `scripts/sync_prod_to_local.py` confirms every remaining typmod-bearing type branch is handled: `character varying` already applies typmod; all other CASE branches are either typmod-free (emit the bare type, correctly, for types that take no typmod) or typmod-applied (emit the production typmod correctly). Each CASE branch and its typmod handling is recorded in the audit artifact. | structural | Structural code inspection of `scripts/sync_prod_to_local.py` CASE branches with a recorded audit artifact listing each branch and its typmod handling |

**Dropped:** the former SC4 ("TDD phase-0 pre-regression baseline passes on a synced database") is dropped as ceremony — it is entailed by SC5/SC6 (a green suite ⊇ baseline green) and was forward-looking rather than a deliverable of this fix (decomposition-ceremony / decomposition-coverage findings). No criterion is weakened: the phase-0 gate passing is a logical consequence of SC5+SC6, not a separate success condition.

## Items

### Item 1 (SC1): Emit `vector(1536)` for `records.embedding`

- RED: enforcement test asserting the builder's rebuilt DDL for `records.embedding` includes the production typmod `vector(1536)` — fails against the current bare-`vector` emission.
- GREEN: generalize `atttypmod` handling in the `scripts/sync_prod_to_local.py` column-type CASE to `vector` columns (no -4 offset; pgvector stores precision directly), emitting `vector({typmod})` when `atttypmod > -1`.
- verify: live `psql` `format_type` check on the local replica after sync run.
- commit: builder change for the vector typmod path (SC1 scope) + test.

### Item 2 (SC2): Emit `vector(384)` for `gloss_search_entries.embedding`

- RED: enforcement test asserting the rebuilt DDL for `gloss_search_entries.embedding` includes `vector(384)` — fails against the current emission.
- GREEN: same generalized `atttypmod` handling covering the `gloss_search_entries.embedding` column.
- verify: live `psql` `format_type` check on the local replica after sync run.
- commit: builder change (SC2 scope) + test.

### Item 3 (SC3): Emit `vector(384)` for `semantic_search_entries.embedding`

- RED: enforcement test asserting the rebuilt DDL for `semantic_search_entries.embedding` includes `vector(384)` — fails against the current emission.
- GREEN: same generalized `atttypmod` handling covering the `semantic_search_entries.embedding` column.
- verify: live `psql` `format_type` check on the local replica after sync run.
- commit: builder change (SC3 scope) + test.

### Item 4 (SC4): Restore `nextval` defaults for the enumerated 16-column set

- RED: enforcement test asserting the rebuilt DDL emits the introspected `pg_attrdef` `nextval(...)` expression for each of the 16 enumerated columns — fails while the stripping guard is present.
- GREEN: restore `nextval` defaults in the rebuilt DDL by emitting the introspected `pg_attrdef` expression in the column line (remove the stripping guard); keep the sequence-reset step; verify the reset does not conflict with the emitted default.
- verify: live `psql` `pg_attrdef` check for all 16 enumerated columns after sync run; ORM insert omitting `id` succeeds.
- commit: defaults-emission change (SC4 scope) + test.

### Item 5 (SC5): Baseline failure set green after fresh sync

- RED: the documented 5 named baseline tests (`test_gloss_search_entries_embedding_is_vector384`, `test_semantic_search_entries_embedding_is_vector384`, and the 3 `test_sc8_*` tests in `test/test_upload_search_entries.py`) fail against the post-sync pre-fix state — this is the recorded baseline.
- GREEN: with Items 1–4 implemented, a fresh sync makes all 5 named tests PASS. Baseline tests remain read-only (R-6) — the fix, not test modification, makes them green.
- verify: full pytest run after fresh sync; the 5 named tests report PASS.
- commit: no source change (verification item); commit evidence artifact.

### Item 6 (SC6): Full suite deterministic comparison vs pre-fix baseline

- RED: post-sync suite at pre-fix state reports `5 failed, 169 passed, 8 skipped` at trunk tip `eb467b8` — the documented baseline comparison target.
- GREEN: after Items 1–4, a fresh sync + full pytest run yields zero failures: the pre-fix `169 passed, 8 skipped` set plus the 5 baseline tests of SC5 now passing.
- verify: full pytest run output compared against the documented pre-fix baseline (`5 failed / 169 passed / 8 skipped` at trunk tip `eb467b8`).
- commit: no source change (verification item); commit evidence artifact.

### Item 7 (SC7): Invocation contract unchanged (R-3, structural)

- RED: invariant check asserting `git diff` against trunk tip `eb467b8` shows no change to `scripts/sync_prod_to_local.sh` — recorded before any fix commits to establish the invariant target.
- GREEN: the fix keeps all changes internal to the DDL builder in `scripts/sync_prod_to_local.py`; the `.sh` entry point is not modified.
- verify: `git diff` against trunk tip `eb467b8` showing no `.sh` change (structural evidence).
- commit: no source change (verification item); commit evidence artifact.

### Item 8 (SC8): Migrations source and production schema untouched (R-4, structural)

- RED: invariant check asserting `git diff` against trunk tip `eb467b8` shows no change under `src/database/` or production schema artifacts — recorded before any fix commits.
- GREEN: the fix touches only `scripts/sync_prod_to_local.py`; `src/database/migrations.py` and the production schema are not modified.
- verify: `git diff` against trunk tip `eb467b8` (structural evidence).
- commit: no source change (verification item); commit evidence artifact.

### Item 9 (SC9): Typmod fidelity audit of remaining column-type CASE branches (R-5, structural)

- RED: the audit artifact for the column-type CASE branches does not exist — no recorded branch-by-branch typmod-handling evidence.
- GREEN: perform structural code inspection of the `scripts/sync_prod_to_local.py` column-type CASE; record each branch and its typmod handling (`character varying` = typmod-applied; all other branches typmod-free or typmod-applied) in the audit artifact; report any additional fidelity gap as a separate finding per R-5, not fixed in this scope.
- verify: recorded audit artifact listing each CASE branch and its typmod handling (structural evidence).
- commit: no source change (audit item); commit audit artifact.

## Traceability

| SC | Requirement(s) | Item | Verification |
|----|----------------|------|--------------|
| SC1 | R-1 | I-1 | Live-DB psql `format_type` check |
| SC2 | R-1 | I-2 | Live-DB psql `format_type` check |
| SC3 | R-1 | I-3 | Live-DB psql `format_type` check |
| SC4 | R-2 | I-4 | Live-DB psql `pg_attrdef` check + ORM insert |
| SC5 | R-1, R-2, R-6 | I-5 | Full pytest run (named tests PASS) |
| SC6 | R-1, R-2, R-6 | I-6 | Full pytest run vs documented pre-fix baseline |
| SC7 | R-3 | I-7 | `git diff` vs trunk tip `eb467b8` — no `.sh` change (structural) |
| SC8 | R-4 | I-8 | `git diff` vs trunk tip `eb467b8` — no `src/database/` or production schema change (structural) |
| SC9 | R-5 | I-9 | Recorded CASE-branch typmod audit artifact (structural) |

## Dependencies

- Sequence creation already exists post-sync (closed issues #1314 / #1316) — SC4 depends on sequences being present; this fix adds only column defaults.
- `scripts/sync_prod_to_local.sh` remains the mandated pre-regression sync entry point (AGENTS.md Regression Test Protocol); the fix must not change its invocation contract (R-3, verified by SC7).
- The pre-fix suite baseline is pinned to trunk tip `eb467b8`: `5 failed, 169 passed, 8 skipped`; the 5-failure baseline set is documented in SC5.
- AGENTS.md Regression Test Protocol: the sync script used in verification MUST be the one from the feature branch under test.

## Edge Cases

- **`atttypmod = -1`** (no typmod): emit bare type — do not emit `vector(-1)`. Guard applies (`atttypmod > -1`).
- **Generated columns:** `info_default` handling for generated columns must not be conflated with the `nextval` default path; only plain column defaults change.
- **Sequence reset interplay:** the emitted `DEFAULT nextval(...)` and the existing sequence-reset step both target sequence state; verify post-sync that the reset still leaves `max(id)`-consistent sequence values and does not error on an existing DEFAULT.
- **Non-`nextval` defaults** (`now()`, `false`): must be preserved unchanged — the fix only stops stripping `nextval` defaults; it must not alter other default expressions.
- **Additional fidelity gaps found during the R-5 audit:** report as separate findings; do not expand this fix's scope.

## Cost Frame

- SC1: live `psql` catalog check after a real sync — minutes.
- SC2: live `psql` catalog check after a real sync — minutes.
- SC3: live `psql` catalog check after a real sync — minutes.
- SC4: live `psql` `pg_attrdef` check + ORM insert after a real sync — minutes.
- SC5: full pytest run after fresh sync — minutes.
- SC6: full pytest run compared against documented pre-fix baseline — minutes.
- SC7: `git diff` structural check — seconds.
- SC8: `git diff` structural check — seconds.
- SC9: structural code inspection of CASE branches + audit artifact recording — minutes.

Skipping behavioral verification in favor of structural string checks on the emitted DDL costs weeks — a structural PASS lets a degraded schema ship and resurface the 5 baseline failures in every future pre-regression baseline (death spiral). Correctness is the only metric; resource cost is never a factor in verification decisions.

## Documentation Sources

| Source | Type | Location | Verification |
|--------|------|----------|--------------|
| Local replica catalog: vector column typmod lost post-sync | Live psql query | Local PostgreSQL via socket `tmp/local_db` — `format_type(atttypid, atttypmod)` for `records`, `gloss_search_entries`, `semantic_search_entries` `embedding` columns returned bare `vector` | Verified live (2026-10-01); expected production values `vector(1536)` / `vector(384)` / `vector(384)` |
| Local replica catalog: `nextval` default stripped post-sync | Live psql query | Local PostgreSQL via socket `tmp/local_db` — `pg_get_expr(adbin, adrelid) FROM pg_attrdef WHERE adrelid='records'::regclass` returned only `now()` and `false` (no `nextval`) | Verified live (2026-10-01); failure mode `IntegrityError: null value in column "id"` |
| Production catalog: enumerated set of `nextval`-defaulted columns | Live psql query (read-only) | Production PostgreSQL `information_schema.columns` JOIN `pg_attrdef` — 16 rows returned (`edit_history.id` … `users.id`) | Verified live (2026-10-01) — enumeration recorded in SC4 |
| Pre-fix test suite baseline | pytest run record | Trunk tip `eb467b8`, clean tree — `5 failed, 169 passed, 8 skipped`; named failures listed in SC5 | Verified by suite run at trunk tip on clean working tree |
| DDL builder defect locations | Source code read | `scripts/sync_prod_to_local.py` — column-type CASE (`t.typname = 'vector'` → bare `vector`) and defaults guard (`if "nextval" not in info_default:`) | Verified by code inspection |
| Schema expectation reference | Source code read | `src/database/migrations.py` — asserts `vector(384)` (read-only reference; out of scope for changes) | Verified by code inspection |

## Enforcement Gate

> **Enforcement gate:** All SCs (SC1–SC9) must PASS before this fix is complete. Each SC's declared Evidence Type is binding — behavioral live-DB evidence for sync outcomes (SC1–SC4), behavioral test-suite evidence for SC5–SC6, and structural evidence for the script-contract invariants and audit (SC7, SC8, SC9, implementing R-3, R-4, and R-5). EVIDENCE_TYPE_MISMATCH is a hard FAIL and MUST NOT be defaulted. Per-SC decomposition: one RED/GREEN/verify/commit cycle per item (I-1 through I-9), never per-file or batched.

---

## Change Control

- **2026-10-01** — SC1 wording synced to verified production state (guideline 130 documentation-drift sync): production `records.embedding` is `vector(1536)`, not `vector(384)`; `gloss_search_entries` and `semantic_search_entries` are `vector(384)`. SC1 now requires the fresh sync to exactly reproduce production typmod per column. Non-substantive wording sync — no change to implementation intent, scope, or evidence type (behavioral live-DB verification unchanged); the criterion is strengthened in precision, not weakened. Pipeline-initiated; no developer re-authorization required per approval-gate-008.
- **2026-10-01** — Structural reformation per aggregate-FAIL validation (11 verdicts, pipeline-initiated remediation; no scope reduction — all criteria preserved or strengthened). Changes: (1) added missing structural sections — Preamble fields, Requirements (R-1–R-6 with RFC 2119 SHALL language), Items, Traceability, Dependencies, Edge Cases, Cost Frame, Documentation Sources (Source/Type/Location/Verification table with live psql evidence), Enforcement Gate; (2) declared per-SC Evidence Type and Verification Method columns — behavioral live-DB evidence for sync outcomes (SC1–SC4), behavioral test-suite evidence for SC5–SC6, structural only for script-contract invariants (R-3, R-4); (3) decomposed compound SCs into atomic SCs: former SC1 comma-list (records/gloss/semantic) split into SC1/SC2/SC3 per-table; former SC2 open-set "other ORM-autoincrement id columns" replaced with the enumerated 16-column production set verified by live read-only catalog query (records.id remains the verified failing case); former SC3 compound ("baseline failures gone AND no new failures") split into SC5 and SC6, with SC6 made deterministic against the documented 5-failure baseline set at trunk tip `eb467b8` (2 vector typmod in `test_semantic_search_schema_sc3.py` + 3 NotNullViolation null-id in `test_upload_search_entries.py`; pre-fix suite `5 failed, 169 passed, 8 skipped`); (4) dropped former SC4 (TDD phase-0 baseline gate) as ceremony — entailed by SC5/SC6, forward-looking, per decomposition-ceremony/decomposition-coverage findings; not a weakening (green suite ⊇ baseline green); (5) resolved the Approach either/or disjunction to the single path: emit `DEFAULT nextval(...)` directly in the rebuilt DDL (builder already introspects `info_default`); existing sequence-reset step kept. Authorized: pipeline-initiated validation remediation dispatched via spec-creation revise task.
- **2026-10-01** — Revision per 3 hard FAILs from validation iteration 2 (pipeline-initiated remediation via spec-creation revise task; no SC weakened): (1) Preamble reformed to the canonical 6 required fields per spec-structure-standards.md §1 (Problem Statement, Root Cause/Motivation, Approach Chosen, Alternatives Considered & Why Discarded, Key Design Decisions, User Intent/Original Prompt) — Root Cause prose moved from Detailed Findings context into the preamble Root Cause field; Alternatives documents the discarded `ALTER TABLE ... SET DEFAULT` post-CREATE path; Key Design Decisions records the no-(-4-offset) typmod rule, the closed 16-column enumeration from live prod catalog, and the SC4-ceremony drop; User Intent records the #1392 stacking authorization. (2) SC↔item 1:1 mapping restored per the 091 TDD chaining gate — Items decomposed from 3 to 8 (I-1→SC1, I-2→SC2, I-3→SC3, I-4→SC4, I-5→SC5, I-6→SC6, I-7→SC7, I-8→SC8); Traceability table updated. (3) Orphan requirements R-3 and R-4 traced to new SC7 (invocation contract unchanged; structural evidence via `git diff` showing no `.sh` change) and SC8 (`src/database/migrations.py` and production schema untouched; structural evidence via `git diff`) — chosen over re-scoping as Verification-Method constraints so the 1:1 SC-item mapping and full traceability are preserved. (4) Cost Frame reformatted to canonical per-SC `- SC-N:` list format. Authorized: pipeline-initiated validation remediation dispatched via spec-creation revise task.
- **2026-10-01** — Revision per single hard FAIL from validation iteration 3 (pipeline-initiated remediation via spec-creation revise task; no SC weakened): orphan requirement R-5 (typmod/default fidelity audit of remaining CASE branches) traced to no SC. Added atomic SC9 (structural evidence: code inspection of `scripts/sync_prod_to_local.py` column-type CASE branches with a recorded audit artifact listing each branch and its typmod handling), Item 9 (I-9→SC9, 1:1 mapping preserved), SC9 row in Traceability tracing R-5, Cost Frame SC9 entry, and Enforcement Gate count updated to SC1–SC9 / I-1 through I-9. All existing SCs unchanged. Authorized: pipeline-initiated validation remediation dispatched via spec-creation revise task.

---

🤖 OpenCode (opencode/mimo-v2.6-flash-free) created
🤖 Co-authored with AI: OpenCode (opencode/mimo-v2.6-flash-free)
