plan_schema_version: 1
issue: 1394
title: "Fix sync_prod_to_local DDL builder — vector typmod and nextval defaults"
authorization_scope: for_pr
pr_strategy: stacked
phase_count: 5
dispatch:
  - phase 1: test-driven-development (red, green), verification-before-completion (verify), orchestrator (commit-inline)
  - phase 2: test-driven-development (red, green), verification-before-completion (verify), orchestrator (commit-inline)
  - phase 3: verification-before-completion (verify), orchestrator (commit-inline)
  - phase 4: verification-before-completion (verify), orchestrator (commit-inline)
  - post: test-driven-development (pre-regression, post-regression, green for I-9 structural audit), audit, finishing-a-development-branch (structural-checks), verification-before-completion (verify for I-9, pre-pr-gate), git-workflow-pr (review-prep, create-pr), completion-core (exec-summary), orchestrator (commit-inline for I-9 artifact, z3-check)
---

# Implementation Plan — Issue 1394

- **Issue:** .issues/1394/spec.md — [SPEC-FIX] sync_prod_to_local DDL builder drops vector typmod and nextval column defaults — 5 pre-existing test failures after mandated pre-regression sync

## Goal

Fix the `CREATE TABLE` DDL builder in `scripts/sync_prod_to_local.py` so vector columns are rebuilt with their production typmod — `records.embedding` = `vector(1536)` (SC1), `gloss_search_entries.embedding` = `vector(384)` (SC2), `semantic_search_entries.embedding` = `vector(384)` (SC3) — and the enumerated 16-column set of autoincrement columns keeps its `nextval` defaults, emitted directly in the rebuilt DDL (SC4); then re-run a fresh sync and verify the documented 5-failure baseline set at trunk tip `eb467b8` is green (SC5) with no new failures versus the pre-fix suite `5 failed, 169 passed, 8 skipped` (SC6); and verify the structural invariants — `.sh` invocation contract unchanged (SC7) and `src/database/migrations.py`/production schema untouched (SC8) — then perform the post-implementation typmod fidelity audit of the remaining column-type CASE branches in `scripts/sync_prod_to_local.py`, recording each branch and its typmod handling in an audit artifact (SC9). Note: the former SC4 (TDD phase-0 baseline gate) was dropped as ceremony — it is entailed by SC5+SC6.

## Architecture

Single-script fix, single approach path (no either/or alternatives): the DDL reconstruction loop in `scripts/sync_prod_to_local.py` generalizes its existing `character varying` atttypmod handling to `vector` columns (no -4 offset — pgvector stores precision directly in `atttypmod`), and emits the `DEFAULT nextval(...)` clause directly in the rebuilt CREATE TABLE column line (the builder already introspects `pg_attrdef` via `info_default`; the stripping guard is removed so the introspected expression is emitted verbatim). The existing sequence-reset step is kept intact. `scripts/sync_prod_to_local.sh` invocation contract is unchanged (SC7). `src/database/migrations.py` and production schema are untouched (SC8).

## Files

- `scripts/sync_prod_to_local.py` — primary change (column-type CASE + defaults handling)
- `scripts/sync_prod_to_local.sh` — re-run only, no change (SC7 invariant)
- `test/test_semantic_search_schema_sc3.py`, `test/test_upload_search_entries.py` — read-only baseline evidence
- `src/database/migrations.py` — read-only reference, out of scope (SC8 invariant)

## Dispatch

- Phases 1-2: `test-driven-development` red/green tasks via `task()`, `verification-before-completion` verify via `task()`, orchestrator commit-inline
- Phases 3-4: `verification-before-completion` verify via `task()`, orchestrator commit-inline (no new RED tests — baseline evidence and structural invariants pre-exist)
- Post: I-9 (SC9) structural audit via `task()` (test-driven-development green-execution + verification-before-completion verify + orchestrator commit-inline); pre-regression (TDD phase-0), audit, structural-checks, pre-pr-gate, regression-check, review-prep, create-pr, exec-summary via `task()`; z3-check orchestrator-direct

## Blast Radius

- LOW — single-script reconstruction path; no production schema or API changes.
- Downstream dependents: `scripts/sync_prod_to_local.sh` (calls the python tool); TDD phase-0 pre-regression baseline on freshly synced local DB (per AGENTS.md Regression Test Protocol).

> **Compliance:** All SCs must pass before completion. Partial implementation is not permitted. Each item is daisy-chained — item N's commit is precondition for item N+1's RED.

> **One step at a time.** Execute exactly one step. Report progress. Wait for instruction before the next step.

> **Step status:** Report `[item N] [PASS|FAIL]` after each step. If FAIL, report blocker and halt.

## Enforcement Gate

> **Enforcement gate:** All SCs (SC1–SC9) must pass before this plan is complete. Declared Evidence Types are binding (behavioral live-DB for SC1–SC4; behavioral test-suite for SC5–SC6; structural for SC7–SC9); EVIDENCE_TYPE_MISMATCH is a hard FAIL. Per-SC decomposition: one RED/GREEN/verify/commit cycle per item (I-1 through I-9; structural items I-7/I-8/I-9 use the verify-only structural cycle — no new RED/GREEN where no code changes), never per-file or batched.

## Pre-Flight Guard (Mandatory)

Check your tool list for a tool named `task`.

- Present ⇒ orchestrator — proceed.
- Absent ⇒ sub-agent — do NOT execute any instruction below. Return `BLOCKED` with `ORCHESTRATOR_ONLY_SKILL_CARD` (cards) or `ORCHESTRATOR_ONLY_PLAN` (plans) and halt.

## Phase Table

| Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch |
|-------|------|---------|-----|------------|------------|----------|
| 1 | Restore vector column typmod in DDL builder | C1_vector_typmod | SC1, SC2, SC3 | — | 5-16 | direct (8, 12, 16) + task-card (5-7, 9-11, 13-15) |
| 2 | Restore nextval column defaults in rebuilt DDL | C2_nextval_defaults | SC4 | 1 | 17-20 | direct (20) + task-card (17-19) |
| 3 | Fresh sync + suite green vs documented baseline | C3_verification | SC5, SC6 | 1, 2 | 21-25 | direct (21, 25) + task-card (22-24) |
| 4 | Structural invariants: invocation contract + scope boundaries | C4_structural_invariants | SC7, SC8 | 1, 2, 3 | 26-30 | direct (26, 30) + task-card (27-29) |
| 5 | Post-implementation + CASE-branch typmod audit | C5_audit | SC9 (gate checks for all SCs) | 4 | 31-43 | direct (33, 37, 40) + task-card (31, 32, 34-36, 38, 39, 41, 42, 43) |

## Pre-Implementation Steps

- [ ] 1. **Coherence gate** `(**direct**)`
  - Verify plan phases, SCs, and DAG are coherent with the revised spec `.issues/1394/spec.md`; confirm every SC maps to exactly one item (I-1→SC1 … I-9→SC9) and one phase (SC1-SC3→1, SC4→2, SC5-SC6→3, SC7-SC8→4, SC9→5).
- [ ] 2. **Baseline check** `(**direct**)`
  - Confirm working tree is on the feature branch with trunk-tip baseline evidence recorded (5 failed / 169 passed / 8 skipped at trunk tip `eb467b8`; the 5-failure baseline set documented in spec SC5).
  - Confirm local DB is reachable via socket `tmp/local_db` for live-DB evidence queries.
- [ ] 3. **Pre-regression (TDD phase-0)** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute phase-0 task from test-driven-development")` — run regression test patterns before RED phase on the current synced-database baseline.
  - SC context: baseline evidence is the 5 pre-existing failures at trunk tip `eb467b8`.
- [ ] 4. **Pre-regression verify** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — verify pre-regression results recorded and baseline consistent with spec Detailed Findings.

## Self-Remediation Protocol

> **Self-Remediation Protocol:** If a step FAILs: diagnose root cause, fix the deliverable, re-verify. If the fix requires spec revision, update the spec and re-enter the plan. Escalate only after remediation failure.

## Exit Criteria

1. C1 — SC1 verified: after fresh sync, `format_type(atttypid, atttypmod)` for `records.embedding` is exactly `vector(1536)`, matching production.
2. C2 — SC2 verified: `gloss_search_entries.embedding` is exactly `vector(384)`, matching production.
3. C3 — SC3 verified: `semantic_search_entries.embedding` is exactly `vector(384)`, matching production.
4. C4 — SC4 verified: `nextval` defaults present in `pg_attrdef` for all 16 enumerated columns after fresh sync; ORM inserts omitting `id` succeed.
5. C5 — SC5 verified: the documented 5-failure baseline set at trunk tip `eb467b8` is green after fresh sync.
6. C6 — SC6 verified: full suite reports no failures and no new failures versus the pre-fix baseline (`5 failed, 169 passed, 8 skipped` at trunk tip `eb467b8`).
7. C7 — SC7 verified (structural): `git diff` vs trunk tip `eb467b8` shows no change to `scripts/sync_prod_to_local.sh`.
8. C8 — SC8 verified (structural): `git diff` vs trunk tip `eb467b8` shows no change under `src/database/` or production schema artifacts.
9. C9 — All verification evidence artifacts exist under the issue artifacts directory and tmp pipeline artifacts are retained per retention rules.
10. C10 — PR created (stacked strategy) with all SC verdicts PASS.
11. C11 — SC9 verified (structural): the CASE-branch typmod audit artifact records every column-type CASE branch in `scripts/sync_prod_to_local.py` and its typmod handling (`character varying` = typmod-applied; all other branches typmod-free or typmod-applied); any additional fidelity gap found is reported as a separate finding per R-5, not silently fixed in this scope.

## Phase 1 — Restore vector column typmod in DDL builder

- **Concern:** C1_vector_typmod
- **Files:** `scripts/sync_prod_to_local.py` (CREATE TABLE builder column-type CASE)
- **SCs:** SC1, SC2, SC3 — after fresh sync, `format_type(atttypid, atttypmod)` output per column exactly matches production: `records.embedding` = `vector(1536)` (I-1), `gloss_search_entries.embedding` = `vector(384)` (I-2), `semantic_search_entries.embedding` = `vector(384)` (I-3). Evidence type: behavioral (live-DB).
- **Dependencies:** none
- **Entry:** pre-implementation steps complete; working tree on feature branch
- **Exit:** SC1-SC3 enforcement tests pass; commit contains test + change

### Code Path Coverage

- P1 (SC1-SC3, items I-1/I-2/I-3): entry `scripts/sync_prod_to_local.py` CREATE TABLE builder column loop — the column-type CASE branch `t.typname = 'vector'` emits bare `vector`; `a.atttypmod` is selected but applied only for `character varying`. Generalize the typmod special-case: emit `vector({typmod})` when `atttypmod > -1` (bare type when `atttypmod = -1` — edge case). No -4 offset for vector — pgvector stores precision directly in `atttypmod`. During the fix, audit the remaining CASE branches for other typmod-bearing types per R-5 (report gaps as separate findings).

### Cross-Cutting SCs

- SC1-SC3 are isolated to the column-type CASE branch (not cross-cutting per cross-cutting matrix).

### Interface Boundaries

- sync tool → local PostgreSQL catalog: rebuilt DDL must reproduce prod-equivalent schema for vector columns. DDL string emitted must be valid PostgreSQL CREATE TABLE syntax; builder return shape (dict with `regular_cols`, `generated_cols`, `all_cols`, `ddl`) preserved for callers.

### State Transitions

- T1 (SC1): `records.embedding` column type from bare `vector` (atttypmod lost) to `vector(1536)` via `format_type`.
- T2 (SC2): `gloss_search_entries.embedding` from bare `vector` to `vector(384)`.
- T3 (SC3): `semantic_search_entries.embedding` from bare `vector` to `vector(384)`.

### Step-by-Step

- [ ] 5. **RED — I-1 (SC1) enforcement test** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute red task from test-driven-development")`.
  - Item I-1 / SC SC1 only. Write a failing enforcement test asserting the rebuilt DDL emits `records.embedding` with typmod `vector(1536)`. The test FAILS at baseline because the builder emits bare `vector`.
  - RED must fail before GREEN begins. No scope creep — no other column in this cycle.
- [ ] 6. **GREEN — I-1 (SC1) vector typmod fix** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute green task from test-driven-development")`.
  - Item I-1 / SC SC1 only. Apply the same `atttypmod` handling used for `character varying` to `vector` columns, emitting `vector({typmod})` when `atttypmod > -1` (no -4 offset). Minimum change only — the I-1 test passes, nothing more.
- [ ] 7. **Verify — I-1 (SC1)** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`.
  - Item I-1 / SC SC1. Verify against live local-DB evidence: after a sync run, `format_type` output for `records.embedding` is exactly `vector(1536)`; behavioral evidence, not structural.
- [ ] 8. **Commit — I-1 (SC1)** `(**direct**)`
  - Orchestrator runs `git add <files> && git commit -m "<message>"` — test and implementation committed as one atomic slice. No co-author trailers (added at PR-time squash). Pre-cleanup per reference card: none pending.
- [ ] 9. **RED — I-2 (SC2) enforcement test** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute red task from test-driven-development")`.
  - Item I-2 / SC SC2 only. Failing enforcement test asserting `gloss_search_entries.embedding` rebuilds as `vector(384)`. Fails at baseline.
- [ ] 10. **GREEN — I-2 (SC2)** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute green task from test-driven-development")`.
  - Item I-2 / SC SC2 only. Same generalized `atttypmod` handling covering `gloss_search_entries.embedding`. Minimum change only.
- [ ] 11. **Verify — I-2 (SC2)** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`.
  - Item I-2 / SC SC2. Live `psql` `format_type` check after sync run: `gloss_search_entries.embedding` is exactly `vector(384)`.
- [ ] 12. **Commit — I-2 (SC2)** `(**direct**)`
  - Orchestrator runs `git add <files> && git commit -m "<message>"` — test and implementation as one atomic slice.
- [ ] 13. **RED — I-3 (SC3) enforcement test** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute red task from test-driven-development")`.
  - Item I-3 / SC SC3 only. Failing enforcement test asserting `semantic_search_entries.embedding` rebuilds as `vector(384)`. Fails at baseline.
- [ ] 14. **GREEN — I-3 (SC3)** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute green task from test-driven-development")`.
  - Item I-3 / SC SC3 only. Same generalized `atttypmod` handling covering `semantic_search_entries.embedding`. Minimum change only.
- [ ] 15. **Verify — I-3 (SC3)** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`.
  - Item I-3 / SC SC3. Live `psql` `format_type` check after sync run: `semantic_search_entries.embedding` is exactly `vector(384)`.
- [ ] 16. **Commit — I-3 (SC3)** `(**direct**)`
  - Orchestrator runs `git add <files> && git commit -m "<message>"` — test and implementation as one atomic slice.

### Phase Completion Block

- VbC assertions: SC1-SC3 enforcement tests PASS with behavioral evidence; commits recorded; artifact `pipeline-verify-*` retained.
- **Cost frame:** Verifying SC1-SC3 with behavioral tests costs minutes — a bounded delay that catches the typmod defect at gate 1 (break). Skipping it costs weeks — a structural PASS lets the bare-`vector` defect ship, and the 2 failing schema tests surface downstream (death spiral). Correctness is the only metric.

### Concern Transition

- Phase 1 complete → proceed to Phase 2 (same builder loop, nextval defaults layered on top of the committed typmod fix).

## Phase 2 — Restore nextval column defaults in rebuilt DDL

- **Concern:** C2_nextval_defaults
- **Files:** `scripts/sync_prod_to_local.py` (defaults handling in the same builder loop)
- **SCs:** SC4 (item I-4) — after fresh sync, every column in the enumerated production set of `nextval`-defaulted columns (`edit_history.id`, `fts_entries.id`, `gloss_search_entries.id`, `headword_search_entries.id`, `languages.id`, `matchup_queue.id`, `permissions.id`, `record_languages.id`, `records.id`, `schema_version.id`, `search_entries.id`, `semantic_search_entries.id`, `sources.id`, `user_activity_log.id`, `user_preferences.id`, `users.id`) carries its `nextval` default in `pg_attrdef`, verbatim from production. Verified failing case at baseline: `records.id`. Evidence type: behavioral (live-DB).
- **Dependencies:** Phase 1 (same DDL builder; nextval handling layered on the committed vector-typmod fix)
- **Entry:** Phase 1 commits complete
- **Exit:** SC4 enforcement test passes; commit contains test + change

### Code Path Coverage

- P2 (SC4, item I-4): entry `scripts/sync_prod_to_local.py` defaults handling in the column loop — `pg_attrdef` lookup and the guard `if "nextval" not in info_default:` that strips autoincrement defaults. Single-path implementation (spec resolved the either/or): emit the `DEFAULT nextval(...)` clause directly in the rebuilt DDL column line; the guard is removed so the introspected expression is emitted verbatim. Must coexist with the existing sequence-reset step and the migration in `src/database/migrations.py` that re-adds nextval defaults (read-only reference). Edge cases: `atttypmod = -1` no-typmod guard; non-`nextval` defaults (`now()`, `false`) preserved unchanged; generated-column defaults not conflated with the nextval path.

### Cross-Cutting SCs

- SC4 is cross-cutting (C2, C3): re-added defaults must not conflict with the existing sequence-reset step; ORM insert behavior (`test_sc8_*`) must be verified after sync per spec Impact risk 2.

### Interface Boundaries

- sync tool → local PostgreSQL catalog: `nextval` defaults present in `pg_attrdef` after rebuild; sequences intact from the prior #1314/#1316 fix; sequence-reset step preserved.
- ORM models → local DB: inserts omitting `id` must succeed; sync output must not regress the migration's default-restoring guarantee.

### State Transitions

- T4 (SC4, item I-4): all 16 enumerated autoincrement `id` column defaults from no `nextval` default (only `now()`, `false` exprs in `pg_attrdef` per live evidence) to `nextval('{table}_{column}_seq')` DEFAULT present; ordering-compatible with the sequence-reset step.

### Step-by-Step

- [ ] 17. **RED — I-4 (SC4) enforcement test** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute red task from test-driven-development")`.
  - Item I-4 / SC SC4. Write a failing enforcement test asserting the rebuilt DDL contains the `DEFAULT nextval('{table}_{column}_seq')` clause (live evidence: `IntegrityError` on ORM insert omitting `id`). The test FAILS at baseline.
  - RED must fail before GREEN begins.
- [ ] 18. **GREEN — I-4 (SC4) nextval default restoration** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute green task from test-driven-development")`.
  - Item I-4 / SC SC4. Emit the `DEFAULT nextval(...)` clause directly in the rebuilt DDL column line (remove the stripping guard), keeping the existing sequence-reset step intact. Minimum change only.
- [ ] 19. **Verify — I-4 (SC4)** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`.
  - Item I-4 / SC SC4. Verify against live local-DB evidence: `pg_attrdef` contains the `nextval` default for all 16 enumerated columns after sync; ORM insert omitting `id` succeeds; sequence-reset step unharmed.
- [ ] 20. **Commit — I-4 (SC4)** `(**direct**)`
  - Orchestrator runs `git add <files> && git commit -m "<message>"` — test and implementation committed as one atomic slice. No co-author trailers.

### Phase Completion Block

- VbC assertions: SC4 enforcement test PASS with behavioral evidence; `pg_attrdef` live evidence retained; commit recorded.
- **Cost frame:** Verifying SC4 behaviorally costs minutes — the missing-default defect is caught at gate 1 (break). Skipping it costs weeks — the `IntegrityError` resurfaces in every future pipeline run on a synced DB (death spiral). Correctness is the only metric.

### Concern Transition

- Phase 2 complete → proceed to Phase 3 (integration gate: fresh sync + suite green versus the documented baseline).

## Phase 3 — Fresh sync + suite green vs documented baseline

- **Concern:** C3_verification
- **Files:** `scripts/sync_prod_to_local.sh` (re-run only), `scripts/sync_prod_to_local.py` (unchanged in this phase)
- **SCs:** SC5 (item I-5) — the documented 5-failure baseline set at trunk tip `eb467b8` (2 vector typmod in `test/test_semantic_search_schema_sc3.py` + 3 NotNullViolation null-`id` in `test/test_upload_search_entries.py`) is green after fresh sync; SC6 (item I-6) — no failures and no new failures versus the pre-fix suite (`5 failed, 169 passed, 8 skipped` at trunk tip `eb467b8`). Evidence type: behavioral (test-suite).
- **Dependencies:** Phases 1 and 2 (both fixes committed)
- **Entry:** SC1-SC4 commits complete on the feature branch
- **Exit:** fresh sync executed; full pytest run green; live-DB evidence before-and-after recorded; evidence committed

### Code Path Coverage

- P3 (SC5, SC6 — items I-5, I-6): entry `scripts/sync_prod_to_local.sh` (re-run) → `sync_prod_to_local.py` (`load_secrets`, `_ensure_pgserver`, `sync_data`). Verification path only: fresh sync rebuilds local schema, then full pytest run and psql evidence checks (`pg_attribute.atttypmod`, `pg_attrdef`) against socket `tmp/local_db`.

### Cross-Cutting SCs

- SC5/SC6 are cross-cutting (C1, C2, C3): the integration gate spanning both defect fixes. Any new failure is treated as a separate finding, not part of this fix (spec Impact risk 3). SC6 is deterministic: compare the suite result against the documented pre-fix baseline set, never an open-ended assertion.

### Interface Boundaries

- shell script → python sync tool: invocation contract MUST NOT change (R-3, verified by SC7 in Phase 4); fix is internal to the DDL builder, CLI surface untouched.
- tests → schema: `test/test_semantic_search_schema_sc3.py` and `test/test_upload_search_entries.py` are read-only baseline evidence (R-6); no test changes.

### State Transitions

- T5 (SC5, item I-5): the 5 named baseline tests from FAIL to PASS after fresh sync.
- T6 (SC6, item I-6): test suite state from `5 failed, 169 passed, 8 skipped` (baseline at trunk tip `eb467b8`) to 0 failures with exactly the pre-fix passed/skipped set plus the 5 baseline tests now green.

### Step-by-Step

- [ ] 21. **RED — I-5/I-6 baseline evidence (no new RED test)** `(**direct**)`
  - Items I-5 (SC5), I-6 (SC6). RED baseline already exists — `5 failed, 169 passed, 8 skipped` at trunk tip `eb467b8`; the 5-failure set is documented in spec SC5. Record the baseline pointer; no new RED test is required for these verification SCs.
- [ ] 22. **GREEN — I-5 (SC5) fresh sync + named tests** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute green task from test-driven-development")` — for this verification item, GREEN is execution, not code change.
  - Item I-5 / SC SC5. Run `bash scripts/sync_prod_to_local.sh` fresh (per AGENTS.md Regression Test Protocol, script from the feature branch), then run the 5 documented baseline tests. What must be true: all 5 named tests PASS.
- [ ] 23. **GREEN — I-6 (SC6) full suite** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute green task from test-driven-development")`.
  - Item I-6 / SC SC6. Run the full pytest suite after the same fresh sync. What must be true: zero failures — the pre-fix `169 passed, 8 skipped` set plus the 5 baseline tests now green, deterministically compared against the documented baseline.
- [ ] 24. **Verify — I-5/I-6 (SC5, SC6)** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`.
  - Items I-5 (SC5), I-6 (SC6). Verify before-and-after live-DB evidence (`format_type` for embedding columns per SC1-SC3, `pg_attrdef` per SC4) plus full-suite output compared deterministically against the documented pre-fix baseline. Behavioral evidence only.
- [ ] 25. **Commit — I-5/I-6 (SC5, SC6) evidence artifacts** `(**direct**)`
  - Orchestrator runs `git add <files> && git commit -m "<message>"` committing the evidence artifacts (no code change; evidence committed per structure artifact).

### Phase Completion Block

- VbC assertions: fresh-sync evidence and full-suite output retained showing the 5 baseline tests green and zero failures.
- **Cost frame:** Running the fresh sync and full suite costs minutes — the integration gate catches any cross-defect interaction at gate 1 (break). Skipping it costs weeks — a masked defect ships and resurfaces in every downstream pipeline (death spiral). Correctness is the only metric.

### Concern Transition

- Phase 3 complete → proceed to Phase 4 (structural invariants). The former SC4 (TDD phase-0 baseline gate) is entailed by SC5+SC6 (green suite ⊇ baseline green) and is no longer a separate phase.

## Phase 4 — Structural invariants: invocation contract + scope boundaries

- **Concern:** C4_structural_invariants
- **Files:** none changed (structural verification only)
- **SCs:** SC7 (item I-7) — `scripts/sync_prod_to_local.sh` invocation contract and CLI surface unchanged; SC8 (item I-8) — `src/database/migrations.py` and the production schema untouched. Evidence type: structural (`git diff`).
- **Dependencies:** Phases 1, 2, 3 (diff compared against the completed-fix working tree)
- **Entry:** SC1-SC6 evidence committed on the feature branch
- **Exit:** both structural diffs clean; evidence committed

### Code Path Coverage

- P4 (SC7, SC8 — items I-7, I-8): no code path — structural verification items. `git diff` against trunk tip `eb467b8` scoped to `scripts/sync_prod_to_local.sh` (SC7) and `src/database/` + production schema artifacts (SC8).

### Cross-Cutting SCs

- SC7/SC8 are cross-cutting scope-boundary invariants (R-3, R-4): they constrain every phase's permitted change surface, verified once after all fix commits.

### Interface Boundaries

- shell script → python sync tool: invocation contract unchanged (SC7); callers see the same CLI surface, arguments, environment variables, and exit codes as at trunk tip `eb467b8`.
- migrations source → schema: `src/database/migrations.py` and production schema untouched (SC8).

### State Transitions

- T7 (SC7, item I-7): no state change — invariant preservation verified by diff.
- T8 (SC8, item I-8): no state change — invariant preservation verified by diff.

### Step-by-Step

- [ ] 26. **RED — I-7/I-8 invariant baselines (no new RED test)** `(**direct**)`
  - Items I-7 (SC7), I-8 (SC8). RED baseline already exists: at trunk tip `eb467b8` the `.sh` invocation contract and `src/database/` state are the reference definitions. Record the diff targets; no new RED test is required for these structural SCs.
- [ ] 27. **GREEN — I-7 (SC7) diff check** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute green task from test-driven-development")` — for this structural item, GREEN is execution of the invariant check, not code change.
  - Item I-7 / SC SC7. Run `git diff eb467b8 -- scripts/sync_prod_to_local.sh`. What must be true: empty diff — no change to the `.sh` entry point.
- [ ] 28. **GREEN — I-8 (SC8) diff check** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute green task from test-driven-development")`.
  - Item I-8 / SC SC8. Run `git diff eb467b8 -- src/database/`. What must be true: empty diff — migrations source and production schema untouched.
- [ ] 29. **Verify — I-7/I-8 (SC7, SC8)** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`.
  - Items I-7 (SC7), I-8 (SC8). Verify the structural evidence: `git diff` output (empty for both scopes) recorded as the artifact. Structural evidence is the declared evidence type for these SCs — not a substitution for behavioral evidence.
- [ ] 30. **Commit — I-7/I-8 (SC7, SC8) evidence artifacts** `(**direct**)`
  - Orchestrator runs `git add <files> && git commit -m "<message>"` committing the structural evidence artifacts (no code change).

### Phase Completion Block

- VbC assertions: both `git diff` artifacts retained showing empty diffs for SC7/SC8 scopes.
- **Cost frame:** Running the two structural diff checks costs seconds — the invariant gate catches scope-creep mutations before they reach review (break). Skipping it costs weeks — a silent contract change ships and breaks every downstream caller of the sync script (death spiral). Correctness is the only metric.

### Concern Transition

- Phase 4 complete → proceed to Phase 5 (post-implementation gates and PR).

## Phase 5 — Post-Implementation + CASE-branch typmod audit

- **Concern:** C5_audit (Typmod fidelity audit of remaining CASE branches — SC9 — post-implementation, per concern-map `phase_boundary: Post-implementation audit (R-5)`)
- **Files:** none changed (audit artifact + gates and PR only)
- **SCs:** SC9 (item I-9) — structural code inspection of the `scripts/sync_prod_to_local.py` column-type CASE confirms every remaining typmod-bearing type branch is handled: `character varying` already applies typmod; all other CASE branches are typmod-free (emit the bare type, correctly) or typmod-applied (emit the production typmod correctly). Each branch and its handling recorded in the audit artifact; additional gaps reported as separate findings per R-5, not fixed in this scope. Evidence type: structural (code inspection + recorded audit artifact). Gate checks for all SCs (audit, z3-check, structural checks, pre-pr-gate, regression-check, PR, exec summary).
- **Dependencies:** Phase 4
- **Entry:** all SC evidence committed
- **Exit:** SC9 audit artifact committed; audit clean, z3-check done, structural checks pass, pre-pr-gate PASS, regression-check clean, PR created, exec summary reported

### Code Path Coverage

- P5 (SC9, item I-9): no code change — structural audit path. Entry `scripts/sync_prod_to_local.py` column-type CASE: enumerate every branch, record typmod handling per branch (typmod-free vs typmod-applied, and whether the production typmod is emitted correctly). Audit artifact at `.issues/1394/artifacts/case-branch-typmod-audit.md`.

### Step-by-Step

- [ ] 31. **Post-regression** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after the GREEN phases.
- [ ] 32. **Audit — adversarial verification audit** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute verification-audit DiMo investigator from audit. Read \`audit/tasks/verification-audit-investigator.md\` first")` — followed by validator, evaluator, arbiter in sequence. Audit the deliverable against all SCs.
- [ ] 33. **Z3 check** `(**direct**)`
  - Orchestrator runs `.opencode/tools/solve check --state-path ... --contract-path ...` directly — Z3 constraint solver verification of the workflow state against the dependency contract.
- [ ] 34. **Structural checks** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute checklist task from finishing-a-development-branch")` — finishing checklist (lint, typecheck, etc.) on modified files.
- [ ] 35. **Audit — I-9 (SC9) CASE-branch typmod audit** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute green task from test-driven-development")` — for this structural item, GREEN is execution of the audit, not code change.
  - Item I-9 / SC SC9. Structurally inspect every column-type CASE branch in `scripts/sync_prod_to_local.py`; record each branch and its typmod handling (`character varying` = typmod-applied; all other branches typmod-free or typmod-applied) in the audit artifact `.issues/1394/artifacts/case-branch-typmod-audit.md`. Report any additional fidelity gap as a separate finding per R-5 — not fixed in this scope.
- [ ] 36. **Verify — I-9 (SC9)** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`.
  - Item I-9 / SC SC9. Verify the structural evidence: the audit artifact exists and lists every CASE branch with its typmod handling; no silent gap fix. Structural evidence is the declared evidence type — not a substitution for behavioral evidence elsewhere.
- [ ] 37. **Commit — I-9 (SC9) audit artifact** `(**direct**)`
  - Orchestrator runs `git add <files> && git commit -m "<message>"` committing the audit artifact (no code change).
- [ ] 38. **Pre-PR gate** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — reads all SC verdicts (SC1–SC9), BLOCKs if any FAIL. DONE_WITH_CONCERNS and EVIDENCE_TYPE_MISMATCH coerce to FAIL.
- [ ] 39. **Regression check** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — final regression check before PR.
- [ ] 40. **Final structural read-back** `(**direct**)`
  - Orchestrator verifies: no prohibited patterns in the deliverable; `scripts/sync_prod_to_local.sh` invocation contract unchanged (SC7); `src/database/migrations.py` untouched (SC8); SC9 audit artifact in place; all SC evidence artifacts in place.
- [ ] 41. **Review prep** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute review-prep from git-workflow-pr. Read \`git-workflow-pr/tasks/review-prep.md\` first")` — prepare PR review context.
- [ ] 42. **Create PR** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute create task from git-workflow-pr")` — create the pull request (stacked strategy, squash to one commit at PR time). HALT after PR creation — merge is human-only.
- [ ] 43. **Executive summary** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute completion task from completion-core")` — generate completion executive summary, then HALT.

### Phase Completion Block

- VbC assertions: SC9 CASE-branch typmod audit artifact recorded and committed; audit verdict recorded; z3-check output recorded; structural checks pass; pre-pr-gate verdict PASS; PR URL recorded; exec summary delivered.
- **Cost frame:** Running the full post-implementation gate chain costs minutes per gate — every defect is caught before merge (break). Skipping any gate costs weeks — a missed defect ships to the trunk and resurfaces in downstream pipelines (death spiral). Correctness is the only metric.

## lifecycle_events

- 2026-10-01T18:44:00Z — `plan_created` — plan regenerated after spec reformation to SC1–SC9 and validation PASS (post revise loops); 5-phase plan verified present at `.issues/1394/plan.md` (phases 1–5, phase_count: 5, items I-1 through I-9); dependency-contract.yaml verified present.
- 2026-10-01T18:06:13Z — `plan_created` — plan file `.issues/1394/plan.md` verified present; 4 implementation phases + post-implementation recorded.
- 2026-10-01 — `plan_revised` — regenerated against revised spec SC set (SC1–SC6 atomic): phase 1 covers SC1–SC3, phase 2 covers SC4 (enumerated 16-column set, single-path DDL default emission), phase 3 covers SC5/SC6 (deterministic baseline comparison); former SC4 phase removed as ceremony; Pre-Flight Guard preserved verbatim.
- 2026-10-01 — `plan_revised` — regenerated against revised spec SC set (SC1–SC8): per-SC 1:1 item decomposition per the 091 TDD chaining gate (I-1→SC1 … I-8→SC8) — phase 1 steps split per-SC for SC1/SC2/SC3 (items I-1/I-2/I-3), phase 2 = I-4 (SC4), phase 3 = I-5/I-6 (SC5/SC6), new phase 4 = I-7/I-8 (SC7/SC8 structural invariants tracing R-3/R-4), phase 5 post-implementation; dependency contract updated with phase-4 invariants; Pre-Flight Guard preserved verbatim.
- 2026-10-01 — `plan_revised` — remediation of validate-findings F1 (SC9_NOT_COVERED) and F2 (DUPLICATE_CONCERN_PHASE_4_5): added item I-9 (SC9, R-5) — CASE-branch typmod fidelity audit with structural verify-only cycle (audit step 35, verify step 36, artifact commit step 37) in phase 5, exit criterion C11, Goal/Enforcement Gate updated to SC1–SC9 / I-1 through I-9; phase 5 concern reassigned from C4_structural_invariants to C5_audit per concern-map (`phase_boundary: Post-implementation audit (R-5)`), Phase Table step ranges corrected to actual step numbers; dependency contract gained phase5 variable + invariant; structure.yaml phase-5 concern/scs/items updated; Pre-Flight Guard preserved verbatim; DAG remains SAT-consistent.
