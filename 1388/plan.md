---
plan_schema_version: "1.1"
issue: 1388
title: "Remediate 5 pre-existing test-harness failures (stale-RED tests + sys.modules mock leak)"
authorization_scope: for_pr
pr_strategy: stacked
phase_count: 5
dispatch: [test-driven-development:red, test-driven-development:green, test-driven-development:post-regression, verification-before-completion:verify, (orchestrator):commit-inline, audit:verification-audit, (orchestrator):z3-check, finishing-a-development-branch:checklist, git-workflow-pr:review-prep, git-workflow-pr:create, completion-core:completion]
---

# Implementation Plan — #1388 — Remediate 5 Pre-Existing Test-Harness Failures

- **Issue:** .issues/1388/spec.md
- **URL:** https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1388

**Goal:** Repair the 5 pre-existing test-harness failures recorded by the #36 pre-regression baseline — containing the module-level `sys.modules` mock leaks in two carrier test files, deleting 2 superseded stale-RED tests, and rewriting the header test — so the full suite is 52 tests green in default alphabetical order, unblocking #36's regression sweep.

**Architecture:** Test-side repair only (C-1 product freeze — `src/**` untouched). Carrier containment uses save/restore insert-only semantics: entries that pre-existed in `sys.modules` are never deleted; only carrier-inserted entries are reverted after the carrier's execution scope. Same-file serialization within `test_search_mode_ui_red.py` (containment → deletion → rewrite). The victim file `test/test_migration_backfill_search_entries.py` heals solely as a verified side-effect. Success is defined at suite level: 52 passed, 0 failed in default alphabetical order (54 baseline minus 2 deleted; 49 previously passing plus 3 repaired). One phase per SC — 5 phases map 1:1 to the spec's 5 SCs (revision: the former Phase 1 bundled containment+deletions and was split into two concern-pure phases).

**Files:**
- `test/test_search_mode_ui_red.py`
- `test/test_filter_ux_red.py`

**Out of scope (unchanged):** all `src/**` product code; `test/test_migration_backfill_search_entries.py`; `test/ui/test_records_*.py`.

---

## Pre-Flight Guard (Mandatory)

Check your tool list for a tool named `task`.

- Present ⇒ orchestrator — proceed.
- Absent ⇒ sub-agent — do NOT execute any instruction below. Return `BLOCKED` with `ORCHESTRATOR_ONLY_SKILL_CARD` (cards) or `ORCHESTRATOR_ONLY_PLAN` (plans) and halt.

---

## Phase Table

| Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch |
|-------|------|---------|-----|------------|------------|----------|
| 1 | Search-mode containment | Contain sys.modules leak at source in `test_search_mode_ui_red.py` | SC-1 | — | 5-9 | task-card (5,6,7,8) + direct (9) |
| 2 | Stale-RED deletions | Delete the 2 superseded stale-RED tests in `test_search_mode_ui_red.py` | SC-2 | 1 | 10-14 | task-card (10,11,12,13) + direct (14) |
| 3 | Filter-UX carrier repair | Contain sys.modules leak at source in `test_filter_ux_red.py` | SC-3 | — | 15-19 | task-card (15,16,17,18) + direct (19) |
| 4 | Header test rewrite | Direct session_state seed + any-of markdown scan in `test_header_shows_mode_name_and_count` | SC-4 | 2 | 20-24 | task-card (20,21,22,23) + direct (24) |
| 5 | Suite-health gate + completion | Full-suite default-order green gate (52/0) + post-implementation pipeline | SC-5 | 1, 2, 3, 4 | 25-35 | task-card (25,26,27,28,30,31,32,33,34,35) + direct (29) |

---

## Pre-Implementation

- [ ] 1. **Coherence gate (**direct**).** Re-read `.issues/1388/spec.md` and `.issues/1388/artifacts/structure.yaml`; confirm 5 SCs map to 5 phases 1:1 with no structural drift; read `tmp/issue-36/artifacts/baseline-failure-diagnosis.yaml` and `tmp/issue-36/artifacts/pre-regression-baseline.yaml` (spec Dependencies mandate) before any implementation. **→ all SCs**
- [ ] 2. **Baseline check (**direct**).** Verify working tree is on the issue feature branch, trunk tip aligned, and the 5 baseline failures reproduce per the diagnosis artifact; record baseline evidence under `tmp/issue-1388/artifacts/`. **→ all SCs**
- [ ] 3. **Pre-regression (**task-card**).** Run regression test patterns before the RED phase per test-driven-development phase-0 task: `task(..., prompt: "execute phase-0 task from test-driven-development")`. Clean `tmp/issue-1388/artifacts/pipeline-pre-regression-*` first. **→ all SCs**
- [ ] 4. **Pre-regression verify (**task-card**).** Verify pre-regression results per verification-before-completion: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1388/artifacts/pipeline-pre-regression-verify-*` first. **→ all SCs**

---

## Admonishments

> **Compliance:** All SCs must pass before completion. Partial implementation is not permitted. Each item is daisy-chained — item N's commit is precondition for item N+1's RED.

> **One step at a time.** Execute exactly one step. Report progress. Wait for instruction before the next step.

> **Step status:** Report `[item N] [PASS|FAIL]` after each step. If FAIL, report blocker and halt.

> **Self-Remediation Protocol:** If a step FAILs: diagnose root cause, fix the deliverable, re-verify. If the fix requires spec revision, update the spec and re-enter the plan. Escalate only after remediation failure.

> **Enforcement gate:** All SCs (SC-1 through SC-5) must pass before this plan is complete. The post-repair suite contract is 52 passed, 0 failed in default alphabetical order — isolation-only green is not valid evidence (SC-5).

---

### Phase 1 — Search-mode containment

**Concern:** Contain the module-level `sys.modules` mock leak at source in `test_search_mode_ui_red.py` only — no deletions, no rewrites in this phase.

**Code Path Coverage:** File under repair is `test/test_search_mode_ui_red.py` only; its module-level `sys.modules["src.services.*"]` MagicMock installation block in `RECORDS_SCRIPT` is the containment target. No product path is touched (C-1 freeze).

**Cross-Cutting SCs:** R-6 insert-only restore semantics spans Phases 1 and 3 (identical containment pattern); R-8 (carrier's own tests stay green) is asserted here for the surviving tests.

**Interface Boundaries:** Containment restores at the carrier's execution-scope exit (teardown), never during `AppTest.from_string` script execution — within-execution service-mock resolution for the surviving tests' own `records()` imports must be preserved.

**State Transitions:** `sys.modules` CLEAN → CONTAMINATED-within-execution → RESTORED. Residual stale-RED failures (the 2 stale-RED deletion targets and the header test) are carried forward deliberately to later phases — this phase's gate scopes zero failures to the migration victim file only.

**Steps:**

- [ ] 5. **RED (**task-card**).** Run the order-pair subprocess pytest run (`test_search_mode_ui_red.py` THEN `test_migration_backfill_search_entries.py`, diagnosis experiment C shape) and assert the pre-change contract: 5 failed, 5 passed of 10 collected, with the 2 migration-file order-dependence failures present. **→ SC-1** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1388/artifacts/pipeline-red-*` first.
- [ ] 6. **GREEN (**task-card**).** Add save/restore insert-only containment around the module-level `sys.modules` mock installation in `RECORDS_SCRIPT` (`test_search_mode_ui_red.py`): save pre-existing `src.services.*` entries before installation, revert only carrier-inserted entries at scope-exit; never delete pre-existing entries. Re-run the order-pair: zero failures from the migration victim file, residuals confined to the three named stale-RED tests. **→ SC-1** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 7. **Post-regression (**task-card**).** Run regression test patterns after GREEN per test-driven-development phase-4 task: `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1388/artifacts/pipeline-post-regression-*` first. **→ SC-1**
- [ ] 8. **Verify (**task-card**).** Verify per verification-before-completion: order-pair exit codes with per-file failure inventory (zero migration-file failures; residuals only the named stale-RED set) + assert within-execution service-mock resolution still holds for the surviving tests' own `records()` imports. **→ SC-1** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1388/artifacts/pipeline-verify-*` first.
- [ ] 9. **Commit (**direct**).** Stage and commit: `git add test/test_search_mode_ui_red.py && git commit -m "test(1388): contain sys.modules mock leak in search-mode carrier (insert-only restore)"`. Test + change committed as one atomic slice. **→ SC-1**

**Cost frame:** Verifying the containment via the order-pair subprocess run costs minutes of execution time — the order-dependence defect is caught at gate 1 and fix cost is bounded (behavioral break). Skipping the verification costs unbounded rework latency — leaked MagicMocks poison in-process migration tests in every future full-suite run, an order-dependent failure class invisible in isolation; each future regression sweep re-trips it.

**Phase 1 completion (VbC assertions):**
- [ ] Order-pair run: zero failures from `test_migration_backfill_search_entries.py`; residual failures exactly the 3 named stale-RED tests.
- [ ] `git status` clean; `src/**` and the victim file untouched.

**Concern transition:** Leaving search-mode containment → entering stale-RED deletions. Phase 2 is same-file-serialized on the now-contained module (Phase 1 enables Phase 2).

---

### Phase 2 — Stale-RED deletions

**Concern:** Delete the 2 superseded stale-RED tests (`test_grouping_separators_render`, `test_help_text_below_radio`) from `test_search_mode_ui_red.py` as clean removals — no re-export, no backward-compat shim.

**Code Path Coverage:** File under repair is `test/test_search_mode_ui_red.py` only (the two stale-RED test methods). No product path is touched (C-1 freeze).

**Cross-Cutting SCs:** R-8 (carrier's own tests stay green) continues to hold for the surviving 4 tests on the contained module.

**Interface Boundaries:** None new — pure collection-surface reduction; the deletion must leave zero importers/references (verified via grep per the dependency contract).

**State Transitions:** Collection in `test_search_mode_ui_red.py` drops 6 → 4 tests. The header stale-RED residual is carried forward deliberately to Phase 4 — same-file serialization (deletions before rewrite) applies.

**Steps:**

- [ ] 10. **RED (**task-card**).** `pytest --collect-only` on `test_search_mode_ui_red.py` lists `test_grouping_separators_render` and `test_help_text_below_radio` pre-change (6 tests collected). **→ SC-2** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1388/artifacts/pipeline-red-*` first.
- [ ] 11. **GREEN (**task-card**).** Delete `test_grouping_separators_render` and `test_help_text_below_radio` as clean removals (no re-export, no backward-compat shim); `--collect-only` collects 4 tests and neither deleted name. **→ SC-2** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 12. **Post-regression (**task-card**).** Run regression test patterns after GREEN: `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1388/artifacts/pipeline-post-regression-*` first. **→ SC-2**
- [ ] 13. **Verify (**task-card**).** Verify: collect-only collected-name scan + count delta 6 → 4. **→ SC-2** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1388/artifacts/pipeline-verify-*` first.
- [ ] 14. **Commit (**direct**).** `git add test/test_search_mode_ui_red.py && git commit -m "test(1388): delete 2 superseded stale-RED tests"`. **→ SC-2**

**Cost frame:** Verifying the deletions via `--collect-only` costs seconds — the collection surface is asserted exactly once (6→4) before downstream phases build on the reduced set. Skipping the verification costs silent drift — a wrongly-deleted surviving test or an undeleted stale-RED name propagates into the header rewrite phase and the suite gate.

**Phase 2 completion (VbC assertions):**
- [ ] Collect-only: neither deleted stale-RED name collected; 4 tests collected.
- [ ] `git status` clean; `src/**` and the victim file untouched.

**Concern transition:** Leaving stale-RED deletions → entering filter-UX carrier repair. Phase 3 is independent (no file overlap). Phase 4 (header rewrite) is enabled by Phase 2's deletions landing on the Phase-1-contained module.

---

### Phase 3 — Filter-UX carrier repair

**Concern:** Contain the identical module-level `sys.modules` mock leak at source in `test_filter_ux_red.py`, healing the migration victim file's order-dependence as a verified side-effect.

**Code Path Coverage:** File under repair is `test/test_filter_ux_red.py` only; its module-level `sys.modules` MagicMock installation block in `RECORDS_SCRIPT` is the containment target. No product path is touched (C-1 freeze); the victim file is read-only.

**Cross-Cutting SCs:** R-3 mandates the identical containment pattern as Phase 1 (cross-cutting consistency); R-6 insert-only restore semantics apply here equally; R-8 asserts the carrier file's 4 existing tests remain green.

**Interface Boundaries:** Restoration at the carrier's execution-scope exit only — never during `AppTest.from_string` script execution.

**State Transitions:** Experiment A shape pre-change: filter-ux carrier THEN victim reports 2 failed (migration), 6 passed; post-change zero failures in both orders (experiment A/B equivalence: 8 passed either way). `sys.modules` post-run probe shows no `src.services.*` MagicMock.

**Steps:**

- [ ] 15. **RED (**task-card**).** Run the order-pair subprocess pytest run (`test_filter_ux_red.py` THEN `test_migration_backfill_search_entries.py`, experiment A shape) and assert the pre-change contract: 2 failed, 6 passed; a `tmp/` post-run probe shows the `src.services.*` MagicMock leak in `sys.modules`. **→ SC-3** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1388/artifacts/pipeline-red-*` first.
- [ ] 16. **GREEN (**task-card**).** Apply the identical save/restore insert-only containment pattern (per Phase 1's pattern, cross-cutting consistency) to `RECORDS_SCRIPT`'s `sys.modules` block in `test_filter_ux_red.py`; the order-pair rerun reports zero failures (experiment A/B equivalence: 8 passed in either order) and the `tmp/` post-run probe shows no `src.services.*` MagicMock. **→ SC-3** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 17. **Post-regression (**task-card**).** Run regression test patterns after GREEN: `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1388/artifacts/pipeline-post-regression-*` first. **→ SC-3**
- [ ] 18. **Verify (**task-card**).** Verify: pairwise exit codes (both orders green) + `tmp/` probe output (no `src.services.*` MagicMock) + the carrier file's 4 existing tests green. **→ SC-3** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1388/artifacts/pipeline-verify-*` first.
- [ ] 19. **Commit (**direct**).** `git add test/test_filter_ux_red.py && git commit -m "test(1388): contain sys.modules mock leak in filter-ux carrier (insert-only restore)"`. **→ SC-3**

**Cost frame:** Verifying the filter-ux containment via the experiment A/B pairwise run costs minutes of execution time — carrier 1 is confirmed dead before the full gate. Skipping the verification costs downstream death-spiral discovery — the carrier stays live and any test file loaded after it inherits the same contamination; a suite that passes in isolation silently fails in the full run, discovered only downstream.

**Phase 3 completion (VbC assertions):**
- [ ] Order-pair run: zero failures in both orders; 8 passed.
- [ ] Post-run `sys.modules` probe: no `src.services.*` MagicMock.
- [ ] `git status` clean; `src/**` and the victim file untouched.

**Concern transition:** Leaving filter-UX carrier repair → entering header test rewrite. Phase 4 depends on Phase 2 (same-file serialization: the rewrite lands after the deletions, transitively on the Phase-1-contained module).

---

### Phase 4 — Header test rewrite

**Concern:** Rewrite `test_header_shows_mode_name_and_count` to stimulate the header render path via a direct `st.session_state.search_query` seed and assert the `"Search:"` header with an ordering-independent any-of markdown scan.

**Code Path Coverage:** File under repair is `test/test_search_mode_ui_red.py` only (the header test method). The product path exercised read-only: `src/frontend/pages/records.py` header render and state-init guard. No product code changes (C-1 freeze).

**Cross-Cutting SCs:** R-4 (seed-then-run stimulation, no `set_value`) and R-5 (any-of assertion, no `markdown[0]`) both land in this single item.

**Interface Boundaries:** The stimulation must survive the `records.py` state-init guard — the guard sets `search_query` only when the key is absent, so seeding before/at run start survives it; seeding after the first `run()` risks the widget-state init overwriting the seed.

**State Transitions:** Pre-rewrite: the test fails under the stale path (`text_input.set_value` never reaches `session_state.search_query` after `907843d` removed `on_change`; `markdown[0]` holds pagination markdown). Post-rewrite: single-file run passes.

**Steps:**

- [ ] 20. **RED (**task-card**).** Confirm the pre-rewrite header test fails single-file under the stale path (already recorded in the #36 baseline — verify it still fails rather than assuming). **→ SC-4** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1388/artifacts/pipeline-red-*` first.
- [ ] 21. **GREEN (**task-card**).** Replace the stimulation path with a direct non-empty `st.session_state.search_query` seed before `run()`; replace `markdown[0]` indexing with an any-of-all-collected-markdown-values `"Search:"` scan; single-file run passes. **→ SC-4** — dispatch: `task(..., prompt: "execute green task from test-driven-development")`.
- [ ] 22. **Post-regression (**task-card**).** Run regression test patterns after GREEN: `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1388/artifacts/pipeline-post-regression-*` first. **→ SC-4**
- [ ] 23. **Verify (**task-card**).** Verify: single-file pytest run passes + a read of the rewritten method body confirming the any-of scan form in place of `markdown[0]` indexing. **→ SC-4** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1388/artifacts/pipeline-verify-*` first.
- [ ] 24. **Commit (**direct**).** `git add test/test_search_mode_ui_red.py && git commit -m "test(1388): rewrite header test — seed search_query directly, any-of markdown scan"`. **→ SC-4**

**Cost frame:** Verifying the rewritten header test single-file costs minutes of execution time — the stale stimulation path is confirmed dead before the suite gate. Skipping the verification costs a permanent stale-RED in every future baseline run — masking real regressions in the header contract.

**Phase 4 completion (VbC assertions):**
- [ ] Single-file run of `test_search_mode_ui_red.py`: header test passes.
- [ ] Rewritten body: non-empty `search_query` seed before `run()`; any-of scan present; zero `markdown[0]` indexing.
- [ ] `git status` clean; `src/**` untouched.

**Concern transition:** Leaving header test rewrite → entering the suite-health gate and post-implementation pipeline. Phase 5 requires all repairs committed.

---

### Phase 5 — Suite-health gate + completion

**Concern:** Prove the full suite green under the reproduction mechanism (default alphabetical order) and run the post-implementation pipeline (audit → z3-check → structural checks → pre-PR gate → regression check → review-prep → PR → completion summary).

**Code Path Coverage:** No new code paths — verification-only plus pipeline gates. File coverage re-asserted unchanged: `test/test_search_mode_ui_red.py`, `test/test_filter_ux_red.py` (both fully committed by now); `src/**` zero deltas.

**Cross-Cutting SCs:** SC-5 is the terminal cross-cutting gate — it aggregates R-7 (product freeze) and R-8 (carrier own-tests green) at suite level.

**Interface Boundaries:** The gate reproduces the order-dependent defect class only in default alphabetical order — the mandated run order; reverse-order or isolation-only green is not valid evidence.

**State Transitions:** Intermediate suite states (post Phase-1 residual state, post Phase-2 4-test collection, post Phase-3 filter-ux repair, post Phase-4 rewrite) converge to the final 52-test contract. DB lifecycle: re-synced from production immediately before the gate per the Regression Test Protocol.

**Steps:**

- [ ] 25. **RED — gate precondition (**task-card**).** Run the full-suite pytest in default alphabetical order pre-gate and assert the target is unmet (failures present while repairs are incomplete). **→ SC-5** — dispatch: `task(..., prompt: "execute red task from test-driven-development")`. Clean `tmp/issue-1388/artifacts/pipeline-red-*` first.
- [ ] 26. **GREEN — full-suite gate (**task-card**).** Run `bash scripts/sync_prod_to_local.sh` (Regression Test Protocol) then the full-suite pytest in default alphabetical order; assert 52 passed, 0 failed; record the tests-run.yaml artifact per the tests-run mandate. **→ SC-5** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1388/artifacts/pipeline-verify-*` first. (Verification-only item — green is the gate itself.)
- [ ] 27. **Verify — suite gate (**task-card**).** Verify per verification-before-completion: full-suite exit code 0 with 52 passed / 0 failed from the default-order run + tests-run artifact recorded. **→ SC-5** — dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1388/artifacts/pipeline-verify-*` first.
- [ ] 28. **Audit (**task-card**).** Adversarial audit of the deliverable: `task(..., prompt: "execute verification-audit DiMo investigator from audit. Read 'audit/tasks/verification-audit-investigator.md' first")` — followed by validator, evaluator, arbiter in sequence. Clean `tmp/issue-1388/artifacts/pipeline-audit-*` first. **→ all SCs**
- [ ] 29. **Z3 check (**direct**).** Run `./.opencode/tools/solve check --state-path tmp/issue-1388/artifacts/state.yaml --contract-path .issues/1388/dependency-contract.yaml` directly (no sub-agent dispatch). Clean `tmp/issue-1388/artifacts/pipeline-z3-check-*` first. **→ all SCs**
- [ ] 30. **Structural checks (**task-card**).** Run the finishing checklist (lint, typecheck, branch readiness): `task(..., prompt: "execute checklist task from finishing-a-development-branch")`. Clean `tmp/issue-1388/artifacts/pipeline-structural-checks-*` first. **→ all SCs**
- [ ] 31. **Pre-PR gate (**task-card**).** Verify all SC verdicts — BLOCK if any FAIL: `task(..., prompt: "execute verify task from verification-before-completion")`. Clean `tmp/issue-1388/artifacts/pipeline-pre-pr-gate-*` first. **→ all SCs**
- [ ] 32. **Regression check (**task-card**).** Final regression check before PR: `task(..., prompt: "execute phase-4 task from test-driven-development")`. Clean `tmp/issue-1388/artifacts/pipeline-regression-check-*` first. **→ SC-5**
- [ ] 33. **Review-prep (**task-card**).** Prepare PR review context: `task(..., prompt: "execute review-prep from git-workflow-pr. Read 'git-workflow-pr/tasks/review-prep.md' first")`. **→ all SCs**
- [ ] 34. **Create PR (**task-card**).** Create the pull request (stacked strategy — one branch, N commits, one PR): `task(..., prompt: "execute create task from git-workflow-pr")`. Human-only merge — the agent does not merge. **→ all SCs**
- [ ] 35. **Completion summary (**task-card**).** Generate the completion executive summary: `task(..., prompt: "execute completion task from completion-core")`. **→ all SCs**

**Cost frame:** Verifying the full-suite default-order gate costs minutes of execution time. Skipping the verification costs an unverifiable suite-health claim — the default-alphabetical order is the one order in which the order-dependent defect class reproduces, so a green claimed from isolation-only runs is worthless against the exact defect class this spec repairs.

**Phase 5 completion (VbC assertions):**
- [ ] Full-suite default-order run: 52 passed, 0 failed; DB was pre-synced via `bash scripts/sync_prod_to_local.sh`.
- [ ] Audit, z3-check, structural checks, pre-PR gate, regression check, review-prep, PR creation, completion summary — all gates PASS.
- [ ] `git status` clean; `src/**` untouched (`C-1` freeze asserted one final time).

**Concern transition:** Leaving the suite-health gate and post-implementation pipeline — all SCs covered (SC-1 through SC-5), phase DAG complete with no cycles. Plan execution ends here; human-only merge applies.

---

## Exit Criteria

- [ ] C1. SC-1 passes: order-pair subprocess run (search-mode carrier → migration victim) reports zero failures from `test_migration_backfill_search_entries.py`, residuals confined to the 3 named stale-RED tests (pre-deletion state).
- [ ] C2. SC-2 passes: `pytest --collect-only` collects neither `test_grouping_separators_render` nor `test_help_text_below_radio` from the repaired file.
- [ ] C3. SC-3 passes: experiment A/B pairwise run reports zero failures; no `src.services.*` MagicMock survives in `sys.modules` post-run.
- [ ] C4. SC-4 passes: rewritten header test passes single-file; body uses the any-of markdown scan, zero `markdown[0]` indexing.
- [ ] C5. SC-5 passes: full-suite default-alphabetical-order run reports 52 passed, 0 failed; DB pre-synced via `bash scripts/sync_prod_to_local.sh`; tests-run.yaml artifact recorded.
- [ ] C6. Product code unchanged: `src/**` has zero modifications (C-1 freeze); the victim file is untouched.
- [ ] C7. Post-implementation pipeline gates all pass (audit, z3-check, structural checks, pre-PR gate, regression check) and the PR is created for the stacked branch.

---

## lifecycle_events

- timestamp: 2026-09-29T21:28:00Z
  event: plan_created
  plan_path: .issues/1388/plan.md
  phase_count: 5

---

<!-- Pre-Flight Guard section above is canonical per plan-artifact-format §3.5 — reason code ORCHESTRATOR_ONLY_PLAN -->
<!-- Rev 2 (2026-09-29): category-4 FAIL remediation — former Phase 1 (containment + deletions bundle) split into Phase 1 (containment SC-1) / Phase 2 (deletions SC-2); filter-ux containment → Phase 3 (SC-3), header rewrite → Phase 4 (SC-4), suite gate → Phase 5 (SC-5); 5 phases map 1:1 to the spec's 5 SCs -->