---
plan_schema_version: "1.0"
issue: 1399
title: "Populate :lim bind param in search_semantic — limit seam fix"
authorization_scope: for_pr
pr_strategy: stacked
phase_count: 1
dispatch:
  - "Phase 1: test-driven-development (pre-regression, red, green, post-regression), verification-before-completion (pre-regression-verify, verify, pre-pr-gate), audit (audit), finishing-a-development-branch (structural-checks), git-workflow-pr (review-prep, create-pr), completion-core (exec-summary), orchestrator-direct (commit-inline, z3-check), regression-check via test-driven-development"
---

# Implementation Plan — #1399 — Populate :lim bind param in search_semantic

**Issue:** .issues/1399/spec.md

## Goal

Restore the declared `limit` parameter of `search_semantic` by populating `params["lim"] = int(limit)` under the existing `limit is not None` guard, so `LIMIT :lim` bind-param parity holds and no `InvalidRequestError` is raised.

## Architecture

Single-phase defect fix pinned by the spec: the params seam of `search_semantic()` in `src/services/semantic_search_service.py`. One dict-key assignment under the same conditional pattern already used for `thr` and `source_id`. No SQL string change, no signature change, no caller change, no threshold/calibration changes (#1400 scope), no UI changes. Four behavioral SCs ride one per-item RED/GREEN/verify/commit daisy chain inside the single phase.

## Files

- `src/services/semantic_search_service.py/` — params construction in `search_semantic`
- `test/` — new `test_semantic_limit_bind_sc1_red.py` + existing semantic suites (regression gate)

## Blast Radius

- `src/services/semantic_search_service.py` — params dict in `search_semantic` (additive `lim` key); `_candidate_sql` signature unchanged
- `test/test_semantic_limit_bind_sc1_red.py` — new test file (this issue's RED/GREEN cycles)
- No ripple: `lim` key is additive; `records.py` (passes `limit=None`) unaffected.

## Phase Table

| Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch |
|-------|------|---------|-----|------------|------------|----------|
| 1 | Limit bind-param fix | SQL bind-parameter correctness (params seam of `search_semantic`) | SC-1, SC-2, SC-3, SC-4 | — | 5-32 | task-card (5-8, 10-13, 15-18, 20-24, 26-31) + direct (9, 14, 19, 23, 25, 32) |

## Pre-Implementation (global)

**Admonishment:**

> **Compliance:** All SCs must pass before completion. Partial implementation is not permitted. Each item is daisy-chained — item N's commit is precondition for item N+1's RED.

**One step at a time:**

> **One step at a time.** Execute exactly one step. Report progress. Wait for instruction before the next step.

**Step status:**

> **Step status:** Report `[item N] [PASS|FAIL]` after each step. If FAIL, report blocker and halt.

**Self-remediation:**

> **Self-Remediation Protocol:** If a step FAILs: diagnose root cause, fix the deliverable, re-verify. If the fix requires spec revision, update the spec and re-enter the plan. Escalate only after remediation failure.

**Enforcement gate:**

> **Enforcement gate:** All SCs must pass before this plan is complete.

- [ ] 1. `coherence gate` (**direct**) — spec-to-plan coherence: re-read `.issues/1399/spec.md` §Success Criteria and the fix approach; confirm the plan's single-phase structure covers SC-1..SC-4 with the pinned approach (`params["lim"] = int(limit)` under the existing `limit is not None` guard in `search_semantic`). If the spec and plan diverge on intent, stop and revise before proceeding.
  - SC reference: all SCs (gate is global)
- [ ] 2. `baseline check` (**direct**) — verify the workspace is on branch `feature/1400-semantic-threshold-calibration`, the working tree has zero pending changes, and the local PostgreSQL replica is up; record the pre-fix baseline by running `uv run pytest test/test_semantic_search_edge_matrix_sc7.py` and confirming green suites before any change.
  - SC reference: SC-4 baseline (regression gate input)
- [ ] 3. `pre-regression` (**task-card**) — dispatch `task(..., prompt: "execute phase-0 task from test-driven-development")` — run regression test patterns before RED phase.
  - SC reference: SC-4 (pre-gate evidence)
- [ ] 4. `pre-regression-verify` (**task-card**) — dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — verify pre-regression results; halt on FAIL.
  - SC reference: SC-4 (pre-gate evidence)

## Phase 1 — Limit Bind-Param Fix

**Concern:** SQL bind-parameter correctness — `search_semantic()` params construction only (separated from `_candidate_sql` SQL string construction, threshold semantics #1400, and UI wiring in `records.py`).

**Files:** `src/services/semantic_search_service.py` (`search_semantic` params construction); `test/test_semantic_limit_bind_sc1_red.py` (new, items 1-3).

**SCs:** SC-1, SC-2, SC-3, SC-4. **Dependencies:** none (first phase). **Entry:** Step 4 verified green baseline.

**Code path coverage:** `search_semantic()` → params dict construction → `_candidate_sql(has_limit=limit is not None)` → `text(sql)` → `conn.execute(sql, params)` — the `lim` key added to params before execute when `limit is not None`; test path `test/test_semantic_limit_bind_sc1_red.py` → `search_semantic(limit=5)` → local DB replica engine. Untouched: empty-query guard, `_encode_query`, diagnostics block, backfill.

**Cross-cutting SCs:** none split across phases (single phase); cross-cutting concerns: security (parameterized LIMIT preserved, no interpolation), data integrity (real DB-replica rows, no synthetic data), backward compatibility (limit=None path byte-identical), Unicode (untouched — numeric bind param only).

**Interface boundaries:** `search_semantic(mode, query, threshold, source_id, limit=None)` status unchanged, backward compatible — the fix restores the already-declared contract.

**State transitions:** from `search_semantic(limit=<n>)` raises `InvalidRequestError` to returns `SemanticSearchResult(status="ok", results capped at n)` on populating `params["lim"]`; `limit=None` full-ranked-list path unchanged; ordering (score DESC, record_id ASC) and status taxonomy are invariants.

**Cost frame:** Running the limit behavioral tests costs minutes of execution time — a bounded delay that surfaces the bind-param crash at the earliest gate. Skipping means the first `limit=<n>` caller discovers the crash in production, at 1000× the fix cost, per the spec's cost frame.

### Item 1 (SC-1) — Populate the :lim bind param — no-exception path

- [ ] 5. `red` (**task-card**) — dispatch `task(..., prompt: "execute red task from test-driven-development")`.
  - SC-1. Create `test/test_semantic_limit_bind_sc1_red.py` with a test calling `search_semantic(mode="gloss", query=<real non-empty query>, limit=5)` against the local DB replica asserting no exception is raised; delete previous-run `tmp/1399-artifacts/pipeline-red-*` artifacts first. Test FAILS on current HEAD with `InvalidRequestError: A value is required for bind parameter 'lim'`.
- [ ] 6. `green` (**task-card**) — dispatch `task(..., prompt: "execute green task from test-driven-development")`.
  - SC-1. In `search_semantic()`, add the conditional population of the `lim` params key as a positive integer coercion under the same `limit is not None` guard that already drives `has_limit` (matching the existing `thr`/`source_id` conditional-param pattern); no other change. The RED test now PASSES.
- [ ] 7. `post-regression` (**task-card**) — dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN.
  - SC-4 (in-flight regression evidence).
- [ ] 8. `verify` (**task-card**) — dispatch `task(..., prompt: "execute verify task from verification-before-completion")`.
  - SC-1. Verify the no-exception criterion with behavioral evidence (test run output) against the local DB replica; verdict EXECUTED/PASS or FAIL.
  - Clean previous-run `tmp/1399-artifacts/pipeline-verify-*` artifacts before dispatching.
- [ ] 9. `commit-inline` (**direct**) — stage and commit `src/services/semantic_search_service.py` + `test/test_semantic_limit_bind_sc1_red.py` together as one atomic slice with a message describing the SC-1 fix. No co-author trailers during implementation commits.

### Item 2 (SC-2) — Cap semantics: LIMIT honored

- [ ] 10. `red` (**task-card**) — dispatch `task(..., prompt: "execute red task from test-driven-development")`.
  - SC-2. Add a `limit=1` case to `test/test_semantic_limit_bind_sc1_red.py` asserting the returned results list contains exactly the top-ranked pair of the unlimited ordering (cap of 1; ordering score DESC then record_id ASC). Confirm the assertion logic is meaningful — count of at most one and pair identity against the `limit=None` ordering — before GREEN.
- [ ] 11. `green` (**task-card**) — dispatch `task(..., prompt: "execute green task from test-driven-development")`.
  - SC-2. Satisfied by Item 1's params fix (shared implementation); the GREEN task verifies the cap evidence stands and applies no new production change. If the assertion is unsatisfiable, the defect is in Item 1's fix — remediate the fix, not the test.
- [ ] 12. `post-regression` (**task-card**) — dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")`.
- [ ] 13. `verify` (**task-card**) — dispatch `task(..., prompt: "execute verify task from verification-before-completion")`.
  - SC-2. Verify the top-ranked-pair cap criterion with behavioral evidence from the same test file.
- [ ] 14. `commit-inline` (**direct**) — commit the SC-2 test case (test file only; may ride with Item 1's slice if sequenced together).

### Item 3 (SC-3) — limit=None invariance guard

- [ ] 15. `red` (**task-card**) — dispatch `task(..., prompt: "execute red task from test-driven-development")`.
  - SC-3. Invariant-preserving guard — need not fail. Record the pre-fix baseline: run `search_semantic(mode="gloss", query=<real non-empty query>, limit=None)` on the pre-fix branch state and record the result count for the fixed real query. Add a guard test to the same file asserting the `limit=None` result count equals the recorded pre-fix baseline count.
- [ ] 16. `green` (**task-card**) — dispatch `task(..., prompt: "execute green task from test-driven-development")`.
  - SC-3. No production code change beyond Item 1; the guard asserts the `limit=None` path is unchanged (no LIMIT clause emitted, full ranked list returned, ordering unchanged).
- [ ] 17. `post-regression` (**task-card**) — dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")`.
- [ ] 18. `verify` (**task-card**) — dispatch `task(..., prompt: "execute verify task from verification-before-completion")`.
  - SC-3. Verify the guard test passes on the fixed branch against the recorded baseline count.
- [ ] 19. `commit-inline` (**direct**) — commit the guard test.

### Item 4 (SC-4) — Existing-suite regression gate

- [ ] 20. `red` (**task-card**) — dispatch `task(..., prompt: "execute red task from test-driven-development")`.
  - SC-4. Regression gate — need not fail. Baseline evidence from step 2 establishes the suites were green on the pre-fix branch; run the full existing semantic suite set on the fixed branch.
- [ ] 21. `green` (**task-card**) — dispatch `task(..., prompt: "execute green task from test-driven-development")`.
  - SC-4. No production code change beyond Item 1; all existing semantic suites pass on the fixed branch.
- [ ] 22. `verify` (**task-card**) — dispatch `task(..., prompt: "execute verify task from verification-before-completion")`.
  - SC-4. Verify `uv run pytest test/test_semantic_*.py test/test_migration_semantic_schema_sc4.py` reports all passing on the fixed branch; preserve the test-run output as the run evidence artifact enumerating tests run, exit codes, and pass/fail counts.
- [ ] 23. `commit-inline` (**direct**) — regression evidence was recorded with the Item 1 slice; nothing new to deliver (no new commit unless a fix was required during items 2-4).

## Post-Implementation (global, in the last phase)

- [ ] 24. `audit` (**task-card**) — dispatch `task(..., prompt: "execute verification-audit DiMo investigator from audit. Read audit/tasks/verification-audit-investigator.md first")` — followed by validator, evaluator, arbiter in sequence; adversarial audit of the deliverable (spec fidelity + drift detection across all SCs).
- [ ] 25. `z3-check` (**direct**) — run the Z3 constraint-solver verification directly: `./.opencode/tools/solve check --contract-path .issues/1399/dependency-contract.yaml --state-path .issues/1399/artifacts/state-analysis.yaml` — require SAT.
- [ ] 26. `structural-checks` (**task-card**) — dispatch `task(..., prompt: "execute checklist task from finishing-a-development-branch")` — lint, typecheck, format check on touched Python files.
- [ ] 27. `pre-pr-gate` (**task-card**) — dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — reads all SC verdicts; BLOCKs if any is FAIL (DONE_WITH_CONCERNS coerces to FAIL; EVIDENCE_TYPE_MISMATCH is a hard FAIL for behavioral SCs).
- [ ] 28. `regression-check` (**task-card**) — dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — final regression check before PR.
- [ ] 29. `review-prep` (**task-card**) — dispatch `task(..., prompt: "execute review-prep from git-workflow-pr. Read git-workflow-pr/tasks/review-prep.md first")` — prepare PR review context.
- [ ] 30. `create-pr` (**task-card**) — dispatch `task(..., prompt: "execute create task from git-workflow-pr")` — squash to exactly one commit for the issue; stacked PR targeting the trunk. `authorization_scope: for_pr` authorizes PR creation; halt_at is pr_created.
- [ ] 31. `exec-summary` (**task-card**) — dispatch `task(..., prompt: "execute completion task from completion-core")` — generate the completion executive summary.
- [ ] 32. halt — after PR creation is confirmed, report status and stop; do not merge (human-only merge).

## Phase Details

| Field | Value |
|-------|-------|
| Skill | test-driven-development (red/green/post-regression), verification-before-completion (verify), orchestrator (commit-inline) |
| Task | per-item cycle steps above |
| Target | params construction in `search_semantic`, `src/services/semantic_search_service.py`; tests under `test/` |
| SCs | SC-1, SC-2, SC-3, SC-4 |
| Depends On | — |

**Phase completion block:** VbC verification assertions — all four SC verdicts EXECUTED/PASS with behavioral evidence artifacts; commit log contains the atomic test+fix slice; regression suites green.

**Concern transition:** end of plan — single phase; no downstream phase transitions.

## Exit Criteria

1. C1 — `search_semantic(mode="gloss", query=<real>, limit=5)` executes against the local DB replica without raising (SC-1). [Phase 1]
2. C2 — `limit=1` returns exactly the top-ranked pair of the unlimited ordering (SC-2). [Phase 1]
3. C3 — `limit=None` result count equals the recorded pre-fix baseline count (SC-3). [Phase 1]
4. C4 — all existing semantic suites pass on the fixed branch (SC-4). [Phase 1]
5. C5 — audit, z3-check, structural-checks, pre-pr-gate all pass; PR created (stacked, one commit) [Phase 1]

## Pre-Flight Guard (Mandatory)

Check your tool list for a tool named `task`.

- Present ⇒ orchestrator — proceed.
- Absent ⇒ sub-agent — do NOT execute any instruction below. Return `BLOCKED` with `ORCHESTRATOR_ONLY_SKILL_CARD` (cards) or `ORCHESTRATOR_ONLY_PLAN` (plans) and halt.
