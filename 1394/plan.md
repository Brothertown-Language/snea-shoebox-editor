---
plan_schema_version: 1
issue: 1394
title: "Fix sync_prod_to_local DDL builder — vector typmod and nextval defaults"
authorization_scope: for_pr
pr_strategy: stacked
phase_count: 4
dispatch:
  - phase 1: test-driven-development (red, green), verification-before-completion (verify), orchestrator (commit-inline)
  - phase 2: test-driven-development (red, green), verification-before-completion (verify), orchestrator (commit-inline)
  - phase 3: verification-before-completion (verify), orchestrator (commit-inline)
  - phase 4: verification-before-completion (verify), orchestrator (commit-inline)
  - post: test-driven-development (pre-regression, post-regression), audit, finishing-a-development-branch (structural-checks), verification-before-completion (pre-pr-gate), git-workflow-pr (review-prep, create-pr), completion-core (exec-summary), orchestrator (z3-check)
---

# Implementation Plan — Issue 1394

- **Issue:** .issues/1394/spec.md — [SPEC-FIX] sync_prod_to_local DDL builder drops vector typmod and nextval column defaults — 5 pre-existing test failures after mandated pre-regression sync

## Goal

Fix the `CREATE TABLE` DDL builder in `scripts/sync_prod_to_local.py` so vector columns are rebuilt as `vector(384)` (SC1) and autoincrement columns keep their `nextval` defaults (SC2); then re-run a fresh sync and verify the full pytest suite is green (SC3) and the TDD phase-0 pre-regression baseline passes on the synced database (SC4).

## Architecture

Single-script fix: the DDL reconstruction loop in `scripts/sync_prod_to_local.py` generalizes its existing `character varying` atttypmod handling to `vector` columns, and restores `nextval(...)` column defaults (either inline in the rebuilt DDL or via post-CREATE `ALTER TABLE ... SET DEFAULT`, coexisting with the existing sequence-reset step). `scripts/sync_prod_to_local.sh` invocation contract is unchanged. `src/database/migrations.py` and production schema are untouched.

## Files

- `scripts/sync_prod_to_local.py` — primary change (column-type CASE + defaults handling)
- `scripts/sync_prod_to_local.sh` — re-run only, no change
- `test/test_semantic_search_schema_sc3.py`, `test/test_upload_search_entries.py` — read-only baseline evidence
- `src/database/migrations.py` — read-only reference, out of scope

## Dispatch

- Phases 1-2: `test-driven-development` red/green tasks via `task()`, `verification-before-completion` verify via `task()`, orchestrator commit-inline
- Phases 3-4: `verification-before-completion` verify via `task()`, orchestrator commit-inline (no new RED tests — baseline evidence pre-exists)
- Pre/post: pre-regression (TDD phase-0), audit, structural-checks, pre-pr-gate, regression-check, review-prep, create-pr, exec-summary via `task()`; z3-check orchestrator-direct

## Blast Radius

- LOW — single-script reconstruction path; no production schema or API changes.
- Downstream dependents: `scripts/sync_prod_to_local.sh` (calls the python tool); TDD phase-0 pre-regression baseline on freshly synced local DB (per AGENTS.md Regression Test Protocol).

> **Compliance:** All SCs must pass before completion. Partial implementation is not permitted. Each item is daisy-chained — item N's commit is precondition for item N+1's RED.

> **One step at a time.** Execute exactly one step. Report progress. Wait for instruction before the next step.

> **Step status:** Report `[item N] [PASS|FAIL]` after each step. If FAIL, report blocker and halt.

## Enforcement Gate

> **Enforcement gate:** All SCs must pass before this plan is complete.

## Pre-Flight Guard (Mandatory)

Check your tool list for a tool named `task`.

- Present ⇒ orchestrator — proceed.
- Absent ⇒ sub-agent — do NOT execute any instruction below. Return `BLOCKED` with `ORCHESTRATOR_ONLY_SKILL_CARD` (cards) or `ORCHESTRATOR_ONLY_PLAN` (plans) and halt.

## Phase Table

| Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch |
|-------|------|---------|-----|------------|------------|----------|
| 1 | Restore vector column typmod in DDL builder | C1_vector_typmod | SC1 | — | 5-8 | direct (8) + task-card (5-7) |
| 2 | Restore nextval column defaults in rebuilt DDL | C2_nextval_defaults | SC2 | 1 | 9-12 | direct (12) + task-card (9-11) |
| 3 | Fresh sync + full suite green | C3_verification | SC3 | 1, 2 | 13-16 | direct (13, 16) + task-card (14-15) |
| 4 | TDD phase-0 pre-regression baseline gate passes on synced DB | C3_verification | SC4 | 3 | 17-20 | direct (17, 20) + task-card (18-19) |
| 5 | Post-implementation | C3_verification | — | 4 | 21-30 | direct (23, 27) + task-card (21, 22, 24-26, 28-30) |

## Pre-Implementation Steps

- [ ] 1. **Coherence gate** `(**direct**)`
  - Verify plan phases, SCs, and DAG are coherent with `.issues/1394/artifacts/structure.yaml`; confirm every SC maps to exactly one phase (SC1→1, SC2→2, SC3→3, SC4→4).
- [ ] 2. **Baseline check** `(**direct**)`
  - Confirm working tree is on the feature branch with trunk-tip baseline evidence recorded (5 failed / 169 passed / 8 skipped at trunk tip `eb467b8`).
  - Confirm local DB is reachable via socket `tmp/local_db` for live-DB evidence queries.
- [ ] 3. **Pre-regression (TDD phase-0)** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute phase-0 task from test-driven-development")` — run regression test patterns before RED phase on the current synced-database baseline.
  - SC context: baseline evidence is the 5 pre-existing failures at trunk tip `eb467b8`.
- [ ] 4. **Pre-regression verify** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — verify pre-regression results recorded and baseline consistent with spec Detailed Findings.

## Self-Remediation Protocol

> **Self-Remediation Protocol:** If a step FAILs: diagnose root cause, fix the deliverable, re-verify. If the fix requires spec revision, update the spec and re-enter the plan. Escalate only after remediation failure.

## Exit Criteria

1. C1 — SC1 verified: `format_type` returns `vector(384)` for every `embedding` column after fresh sync.
2. C2 — SC2 verified: `nextval` defaults present on autoincrement `id` columns in `pg_attrdef` after fresh sync; ORM inserts omitting `id` succeed.
3. C3 — SC3 verified: full pytest suite after fresh sync reports 0 failures.
4. C4 — SC4 verified: TDD phase-0 pre-regression baseline passes on the synced database.
5. C5 — `scripts/sync_prod_to_local.sh` invocation contract unchanged; `src/database/migrations.py` and production schema untouched.
6. C6 — All verification evidence artifacts exist under the issue artifacts directory and tmp pipeline artifacts are retained per retention rules.
7. C7 — PR created (stacked strategy) with all SC verdicts PASS.

## Phase 1 — Restore vector column typmod in DDL builder

- **Concern:** C1_vector_typmod
- **Files:** `scripts/sync_prod_to_local.py` (CREATE TABLE builder column-type CASE)
- **SCs:** SC1 — after fresh sync, `format_type(atttypid, atttypmod)` returns `vector(384)` for every `embedding` column
- **Dependencies:** none
- **Entry:** pre-implementation steps complete; working tree on feature branch
- **Exit:** SC1 enforcement test passes; commit contains test + change

### Code Path Coverage

- P1 (SC1): entry `scripts/sync_prod_to_local.py` CREATE TABLE builder column loop — the column-type CASE branch `t.typname = 'vector'` emits bare `vector`; `a.atttypmod` is selected but applied only for `character varying`. Generalize the typmod special-case: emit `vector({typmod})` when `atttypmod > -1`. During the fix, audit the remaining CASE branches for other typmod-bearing types per spec Impact mitigation.

### Cross-Cutting SCs

- SC1 is isolated to the column-type CASE branch (not cross-cutting per cross-cutting matrix).

### Interface Boundaries

- sync tool → local PostgreSQL catalog: rebuilt DDL must reproduce prod-equivalent schema for vector columns. DDL string emitted must be valid PostgreSQL CREATE TABLE syntax; builder return shape (dict with `regular_cols`, `generated_cols`, `all_cols`, `ddl`) preserved for callers.

### State Transitions

- T1 (SC1): embedding columns (`records`, `gloss_search_entries`, `semantic_search_entries`) from column type `vector` (atttypmod lost) to `vector(384)` via `format_type`.

### Step-by-Step

- [ ] 5. **RED — SC1 enforcement test** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute red task from test-driven-development")`.
  - SC: SC1. Write a failing enforcement test asserting the rebuilt DDL emits `vector(384)` for embedding columns. The test FAILS at baseline because the builder emits bare `vector`.
  - RED must fail before GREEN begins. No scope creep.
- [ ] 6. **GREEN — vector typmod fix** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute green task from test-driven-development")`.
  - SC: SC1. Apply the same `atttypmod` handling used for `character varying` to `vector` columns in the CREATE TABLE builder, emitting `vector({typmod})` when `atttypmod > -1`. Minimum change only — test passes, nothing more.
- [ ] 7. **Verify — SC1** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`.
  - SC: SC1. Verify against live local-DB evidence: after a sync run, `format_type` returns `vector(384)` for every `embedding` column; behavioral evidence, not structural.
- [ ] 8. **Commit — SC1** `(**direct**)`
  - Orchestrator runs `git add <files> && git commit -m "<message>"` — test and implementation committed as one atomic slice. No co-author trailers (added at PR-time squash). Pre-cleanup per reference card: none pending.

### Phase Completion Block

- VbC assertions: SC1 enforcement test PASS with behavioral evidence; commit recorded; artifact `pipeline-verify-*` retained.
- **Cost frame:** Verifying SC1 with a behavioral test costs minutes — a bounded delay that catches the typmod defect at gate 1 (break). Skipping it costs weeks — a structural PASS lets the bare-`vector` defect ship, and the 2 failing schema tests surface downstream (death spiral). Correctness is the only metric.

### Concern Transition

- Phase 1 complete → proceed to Phase 2 (same builder loop, nextval defaults layered on top of the committed typmod fix).

## Phase 2 — Restore nextval column defaults in rebuilt DDL

- **Concern:** C2_nextval_defaults
- **Files:** `scripts/sync_prod_to_local.py` (defaults handling in the same builder loop)
- **SCs:** SC2 — after fresh sync, `records.id` (and other ORM-autoincrement `id` columns) carry their `nextval` defaults
- **Dependencies:** Phase 1 (same DDL builder; nextval handling layered on the committed vector-typmod fix)
- **Entry:** Phase 1 commit complete
- **Exit:** SC2 enforcement test passes; commit contains test + change

### Code Path Coverage

- P2 (SC2): entry `scripts/sync_prod_to_local.py` defaults handling in the column loop — `pg_attrdef` lookup and the guard `if "nextval" not in info_default:` that strips autoincrement defaults. Two permitted implementations: emit `nextval(...)` in the rebuilt DDL line, or post-CREATE `ALTER TABLE ... SET DEFAULT`. Must coexist with the existing sequence-reset step and the migration in `src/database/migrations.py` that re-adds nextval defaults (read-only reference).

### Cross-Cutting SCs

- SC2 is cross-cutting (C2, C3): re-added defaults must not conflict with the existing sequence-reset step; ORM insert behavior (`test_sc8_*`) must be verified after sync per spec Impact risk 2.

### Interface Boundaries

- sync tool → local PostgreSQL catalog: `nextval` defaults present in `pg_attrdef` after rebuild; sequences intact from the prior #1314/#1316 fix; sequence-reset step preserved.
- ORM models → local DB: inserts omitting `id` must succeed; sync output must not regress the migration's default-restoring guarantee.

### State Transitions

- T2 (SC2): autoincrement `id` column defaults from no `nextval` default (only `now()`, `false` exprs in `pg_attrdef` per live evidence) to `nextval('{table}_{column}_seq')` DEFAULT present; ordering-compatible with the sequence-reset step.

### Step-by-Step

- [ ] 9. **RED — SC2 enforcement test** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute red task from test-driven-development")`.
  - SC: SC2. Write a failing enforcement test asserting a `nextval('{table}_{column}_seq')` default is present after sync (live evidence: `IntegrityError` on ORM insert omitting `id`). The test FAILS at baseline.
  - RED must fail before GREEN begins.
- [ ] 10. **GREEN — nextval default restoration** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute green task from test-driven-development")`.
  - SC: SC2. Emit the `nextval` default in the rebuilt DDL or re-add via `ALTER TABLE ... SET DEFAULT` after `CREATE TABLE`, keeping the existing sequence-reset step intact. Minimum change only.
- [ ] 11. **Verify — SC2** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`.
  - SC: SC2. Verify against live local-DB evidence: `pg_attrdef` contains the `nextval` default for `records.id` after sync; ORM insert omitting `id` succeeds; sequence-reset step unharmed.
- [ ] 12. **Commit — SC2** `(**direct**)`
  - Orchestrator runs `git add <files> && git commit -m "<message>"` — test and implementation committed as one atomic slice. No co-author trailers.

### Phase Completion Block

- VbC assertions: SC2 enforcement test PASS with behavioral evidence; `pg_attrdef` live evidence retained; commit recorded.
- **Cost frame:** Verifying SC2 behaviorally costs minutes — the missing-default defect is caught at gate 1 (break). Skipping it costs weeks — the `IntegrityError` resurfaces in every future pipeline run on a synced DB (death spiral). Correctness is the only metric.

### Concern Transition

- Phase 2 complete → proceed to Phase 3 (integration gate: fresh sync + full suite green).

## Phase 3 — Fresh sync + full suite green

- **Concern:** C3_verification
- **Files:** `scripts/sync_prod_to_local.sh` (re-run only), `scripts/sync_prod_to_local.py` (unchanged in this phase)
- **SCs:** SC3 — full test suite after sync: 0 failures (5 baseline failures gone, no new failures)
- **Dependencies:** Phases 1 and 2 (both fixes committed)
- **Entry:** SC1 and SC2 commits complete on the feature branch
- **Exit:** fresh sync executed; full pytest run with 0 failures; live-DB evidence before-and-after recorded; evidence committed

### Code Path Coverage

- P3 (SC3, SC4): entry `scripts/sync_prod_to_local.sh` (re-run) → `sync_prod_to_local.py` (`load_secrets`, `_ensure_pgserver`, `sync_data`). Verification path only: fresh sync rebuilds local schema, then full pytest run and psql evidence checks (`pg_attribute.atttypmod`, `pg_attrdef`) against socket `tmp/local_db`.

### Cross-Cutting SCs

- SC3 is cross-cutting (C1, C2, C3): the integration gate spanning both defect fixes. Any new failure is treated as a separate finding, not part of this fix (spec Impact risk 3).

### Interface Boundaries

- shell script → python sync tool: invocation contract MUST NOT change (spec key dependency); fix is internal to the DDL builder, CLI surface untouched.
- tests → schema: `test/test_semantic_search_schema_sc3.py` and `test/test_upload_search_entries.py` are read-only baseline evidence; no test changes.

### State Transitions

- T3 (SC3): test suite state from `5 failed, 169 passed, 8 skipped` (baseline at trunk tip `eb467b8`) to `0 failures`.

### Step-by-Step

- [ ] 13. **RED — SC3 baseline evidence (no new RED test)** `(**direct**)`
  - SC: SC3. RED baseline already exists — 5 failed / 169 passed / 8 skipped at trunk tip `eb467b8` (spec Detailed Findings). Record the baseline pointer; no new RED test is required for this verification SC.
- [ ] 14. **GREEN — fresh sync + full suite** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute green task from test-driven-development")` — for this verification SC, GREEN is execution, not code change.
  - SC: SC3. Run `bash scripts/sync_prod_to_local.sh` fresh (per AGENTS.md Regression Test Protocol, script from the feature branch), then run the full pytest suite. What must be true: 0 failures — the 5 baseline failures gone, no new failures.
- [ ] 15. **Verify — SC3** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`.
  - SC: SC3. Verify before-and-after live-DB evidence: `format_type` → `vector(384)` for embedding columns, `nextval` defaults in `pg_attrdef`, plus full-suite output showing 0 failures. Behavioral evidence only.
- [ ] 16. **Commit — SC3 evidence artifacts** `(**direct**)`
  - Orchestrator runs `git add <files> && git commit -m "<message>"` committing the evidence artifacts (no code change; evidence committed per structure artifact).

### Phase Completion Block

- VbC assertions: fresh-sync evidence and full-suite output retained showing 0 failures; invocation contract unchanged.
- **Cost frame:** Running the fresh sync and full suite costs minutes — the integration gate catches any cross-defect interaction at gate 1 (break). Skipping it costs weeks — a masked defect ships and resurfaces in every downstream pipeline (death spiral). Correctness is the only metric.

### Concern Transition

- Phase 3 complete → proceed to Phase 4 (downstream consumer gate: TDD phase-0 baseline on the synced DB).

## Phase 4 — TDD phase-0 pre-regression baseline gate passes on synced DB

- **Concern:** C3_verification
- **Files:** none changed (consequence of SC1-SC3)
- **SCs:** SC4 — TDD phase-0 pre-regression baseline passes on a synced database for subsequent pipelines
- **Dependencies:** Phase 3 (baseline gate is a direct consequence of the SC3 green suite)
- **Entry:** Phase 3 evidence committed
- **Exit:** baseline gate verified passing on the freshly synced database; evidence committed

### Code Path Coverage

- P3 (SC3, SC4): downstream consumer of the sync entry-point contract — the TDD phase-0 pre-regression gate runs against the freshly synced local DB. `scripts/sync_prod_to_local.sh` invocation contract must remain unchanged.

### Cross-Cutting SCs

- SC4 is cross-cutting (C3): the gate is a downstream consumer of SC1-SC3; no code change beyond the sync script.

### Interface Boundaries

- shell script → python sync tool: unchanged; the gate exercises the same entry point mandated by AGENTS.md Regression Test Protocol.

### State Transitions

- T4 (SC4): TDD phase-0 pre-regression baseline gate from blocked on synced databases (5 pre-existing failures) to passing on a freshly synced database.

### Step-by-Step

- [ ] 17. **RED — SC4 baseline evidence (no new RED test)** `(**direct**)`
  - SC: SC4. RED baseline already exists — the baseline gate previously blocked on synced databases (state-analysis T4 from-state). No new RED test required.
- [ ] 18. **GREEN — confirm baseline gate passes** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute green task from test-driven-development")` — for this verification SC, GREEN is execution, not code change.
  - SC: SC4. Confirm the TDD phase-0 pre-regression baseline passes on the freshly synced database — a consequence of SC1-SC3.
- [ ] 19. **Verify — SC4** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`.
  - SC: SC4. Verify with execution evidence that the phase-0 gate run on the synced DB reports a clean baseline.
- [ ] 20. **Commit — SC4 evidence artifacts** `(**direct**)`
  - Orchestrator runs `git add <files> && git commit -m "<message>"` committing the evidence artifacts.

### Phase Completion Block

- VbC assertions: phase-0 baseline gate evidence retained showing PASS on the synced DB; all four SCs now have committed evidence.
- **Cost frame:** Re-running the baseline gate costs minutes — the downstream gate is verified green before PR (break). Skipping it costs weeks — the next pipeline discovers a blocked baseline on a synced DB (death spiral). Correctness is the only metric.

### Concern Transition

- Phase 4 complete → proceed to Phase 5 (post-implementation gates and PR).

## Phase 5 — Post-Implementation

- **Concern:** C3_verification
- **Files:** none changed (gates and PR only)
- **SCs:** all (gate checks)
- **Dependencies:** Phase 4
- **Entry:** all SC evidence committed
- **Exit:** audit clean, z3-check done, structural checks pass, pre-pr-gate PASS, regression-check clean, PR created, exec summary reported

### Step-by-Step

- [ ] 21. **Post-regression** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after the GREEN phases.
- [ ] 22. **Audit — adversarial verification audit** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute verification-audit DiMo investigator from audit. Read \`audit/tasks/verification-audit-investigator.md\` first")` — followed by validator, evaluator, arbiter in sequence. Audit the deliverable against all SCs.
- [ ] 23. **Z3 check** `(**direct**)`
  - Orchestrator runs `.opencode/tools/solve check --state-path ... --contract-path ...` directly — Z3 constraint solver verification of the workflow state against the dependency contract.
- [ ] 24. **Structural checks** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute checklist task from finishing-a-development-branch")` — finishing checklist (lint, typecheck, etc.) on modified files.
- [ ] 25. **Pre-PR gate** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — reads all SC verdicts, BLOCKs if any FAIL. DONE_WITH_CONCERNS and EVIDENCE_TYPE_MISMATCH coerce to FAIL.
- [ ] 26. **Regression check** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — final regression check before PR.
- [ ] 27. **Final structural read-back** `(**direct**)`
  - Orchestrator verifies: no prohibited patterns in the deliverable; `scripts/sync_prod_to_local.sh` invocation contract unchanged; `src/database/migrations.py` untouched; all SC evidence artifacts in place.
- [ ] 28. **Review prep** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute review-prep from git-workflow-pr. Read \`git-workflow-pr/tasks/review-prep.md\` first")` — prepare PR review context.
- [ ] 29. **Create PR** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute create task from git-workflow-pr")` — create the pull request (stacked strategy, squash to one commit at PR time). HALT after PR creation — merge is human-only.
- [ ] 30. **Executive summary** `(**task-card**)`
  - Dispatch `task(..., prompt: "execute completion task from completion-core")` — generate completion executive summary, then HALT.

### Phase Completion Block

- VbC assertions: audit verdict recorded; z3-check output recorded; structural checks pass; pre-pr-gate verdict PASS; PR URL recorded; exec summary delivered.
- **Cost frame:** Running the full post-implementation gate chain costs minutes per gate — every defect is caught before merge (break). Skipping any gate costs weeks — a missed defect ships to the trunk and resurfaces in downstream pipelines (death spiral). Correctness is the only metric.

## lifecycle_events

- 2026-10-01T18:06:13Z — `plan_created` — plan file `.issues/1394/plan.md` verified present; 4 implementation phases + Phase 5 post-implementation recorded.

