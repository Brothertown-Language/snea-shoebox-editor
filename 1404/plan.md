---
plan_schema_version: "1.0"
issue: 1404
title: "Fix search_records semantic-mode dispatch against the real search_semantic contract"
authorization_scope: for_pr
pr_strategy: stacked
phase_count: 2
dispatch:
  - "P1: test-driven-development (red, green, post-regression), verification-before-completion (verify), orchestrator commit-inline"
  - "P2: test-driven-development (post-regression), verification-before-completion (verify), orchestrator commit-inline; then audit, z3-check (direct), finishing-a-development-branch (structural-checks), verification-before-completion (pre-pr-gate), test-driven-development (regression-check), git-workflow-pr (review-prep, create-pr), completion-core (exec-summary)"
---

# Implementation Plan — #1404 — Fix search_records Semantic-Mode Dispatch

**Issue:** .issues/1404/spec.md

**Goal:** Make `LinguisticService.search_records()` work for Semantic Gloss and Semantic All modes by threading the caller's mode into `search_semantic`, normalizing both real hit shapes, consuming the seam's `matched_terms` dict, and rewriting the masked SC-8 regression tests against the real seam contract.

**Architecture:** The seam `search_semantic()` (src/services/semantic_search_service.py) is the fixed contract source — it returns a `SemanticSearchResult` whose hits are `(record_id, score)` tuples plus a `matched_terms: dict[int, set]`. The dispatch fix lives entirely in `LinguisticService.search_records()` (src/services/linguistic_service.py): pass `mode='gloss'`/`mode='all'` explicitly per search_mode, normalize both hit shapes in the id-filter and matched_terms loops, and bound matched_terms to the returned page. Regression tests in `test/test_search_records_matched_terms_none_sc8_red.py` are rewritten to patch only the DB session/encoder — no `_search_strategies` shape stubs. No change to the seam itself.

**Files:**
- `src/services/linguistic_service.py`
- `test/test_search_records_matched_terms_none_sc8_red.py`

---

## Phase Table

| Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch |
|-------|------|---------|-----|------------|-----------|----------|
| 1 | semantic-dispatch-fix-and-real-shape-tests | Correct semantic dispatch in `search_records` (mode threading, hit-shape normalization, matched_terms consumption) plus real-shape regression tests | SC-1, SC-2, SC-3 | — | 3–25 | direct (5, 10, 12, 14, 17, 19, 22, 24) + task-card (3–4, 6–9, 11, 13, 15–16, 18, 20–21, 23, 25) |
| 2 | no-regression-check | Whole-suite regression verification and any incidental fixes | SC-4 | 1 | 26–30 | direct (28, 30) + task-card (26–27, 29) |

Post-implementation steps run after Phase 2 (steps 31–38).

---

## Admonishments

> **Compliance:** All SCs must pass before completion. Partial implementation is not permitted. Each item is daisy-chained — item N's commit is precondition for item N+1's RED.

> **One step at a time.** Execute exactly one step. Report progress. Wait for instruction before the next step.

> **Step status:** Report `[item N] [PASS|FAIL]` after each step. If FAIL, report blocker and halt.

> **Self-Remediation Protocol:** If a step FAILs: diagnose root cause, fix the deliverable, re-verify. If the fix requires spec revision, update the spec and re-enter the plan. Escalate only after remediation failure.

> **Enforcement gate:** All SCs must pass before this plan is complete.

---

## Pre-Implementation Steps

- [ ] 1. **Coherence gate (**direct**).** Confirm the spec (`.issues/1404/spec.md`) and structure artifact agree: 4 SCs, 2 phases, SC-3 depends on SC-1/SC-2, SC-4 depends on all. If any mismatch, return BLOCKED before proceeding.
- [ ] 2. **Baseline check (**direct**).** Verify the working tree is on the feature branch with zero pending changes; run `uv run pytest test/` to record the pre-change baseline suite state. Report the baseline result.

## Phase 1 — semantic-dispatch-fix-and-real-shape-tests

**Concern:** One concern — the `search_records` semantic dispatch path: thread the caller's mode into `search_semantic`, normalize both real hit shapes, consume the seam's `matched_terms` dict, and rewrite the masked regression tests against the real seam contract.

**Files:**
- `src/services/linguistic_service.py`
- `test/test_search_records_matched_terms_none_sc8_red.py`

**SCs:** SC-1, SC-2, SC-3

**Dependencies:** None

**Entry Conditions:**
- Baseline check (step 2) passed
- Coherence gate (step 1) passed

**Exit Conditions:**
- `search_records` with Semantic Gloss and Semantic All returns `RecordSearchResult` without raising, with `matched_terms` populated from the seam
- Regression tests exercise only real `search_semantic` hit shapes with DB session/encoder isolation
- Per-SC commits landed in SC order (SC-1 → SC-2 → SC-3)

**Code Path Coverage:** `LinguisticService.search_records` semantic dispatch branch (strategy table entries for `"Semantic Gloss"` and `"Semantic All"`, the container-consumption id-filter, the matched_terms population loop). No other `search_records` mode branch is touched.

**Cross-Cutting SCs:** None — all three SCs are phase-local to the dispatch concern.

**Interface Boundaries:** The `search_semantic(mode, query, ...)` seam signature and `SemanticSearchResult` shape (`results` list, `matched_terms` dict) are FIXED inputs — the seam is not modified. The `RecordSearchResult` return contract of `search_records` is preserved for non-semantic modes.

**State Transitions:** None — pure query path; no persistence state changes.

**Cost frame:** Verifying the semantic dispatch fix costs minutes of behavioral test execution against the real seam contract. Skipping means a tuple-shaped hit ships a live `AttributeError` crash — discovered downstream at 100×–1000× the cost of the RED/GREEN cycle that would have caught it at gate 1.

### Step-by-step

- [ ] 3. **pre-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-0 task from test-driven-development")`. Clean previous artifacts: `rm -f tmp/1404/artifacts/pipeline-pre-regression-*`. Run the pre-RED regression pattern baseline for the affected suites. Report the regression snapshot.
- [ ] 4. **pre-regression-verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`. Clean previous artifacts: `rm -f tmp/1404/artifacts/pipeline-pre-regression-verify-*`. Verify the pre-regression snapshot is clean before any RED begins.
- [ ] 5. **SC-1 RED setup (**direct**).** Clean previous artifacts: `rm -f tmp/1404/artifacts/pipeline-red-*`. Confirm the SC-1 RED test target lives in `test/test_search_records_matched_terms_none_sc8_red.py` against the real `search_semantic` contract (real tuples plus `matched_terms` dict), with only the DB session patched.
- [ ] 6. **SC-1 RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")`. Write the failing live-path test: `search_records(search_mode='Semantic Gloss', ...)` against the real seam — it must FAIL because mode threading is absent and the tuple hit shape is not consumed. **→ SC-1**
- [ ] 7. **SC-1 RED confirm (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")`. Run the RED test and confirm it FAILS for the right reason (missing mode threading / shape mismatch), not an import or fixture error. **→ SC-1**
- [ ] 8. **SC-1 GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")`. Implement the minimum change in `search_records`: thread `mode='gloss'` explicitly into `search_semantic` for `"Semantic Gloss"`, normalize `(record_id, score)` tuples AND attribute-bearing hits in the id-filter, and populate `matched_terms` from the seam's real dict bounded to the returned page. **→ SC-1**
- [ ] 9. **SC-1 GREEN confirm (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")`. Run the SC-1 RED test and confirm it PASSES; confirm no other mode regressed in the same file. **→ SC-1**
- [ ] 10. **SC-1 post-regression (**direct**).** Clean previous artifacts: `rm -f tmp/1404/artifacts/pipeline-post-regression-*`. Run the SC-8 regression file plus neighboring service tests to confirm no collateral breakage. **→ SC-1**
- [ ] 11. **SC-1 verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`. Verify against SC-1: no raise, `RecordSearchResult` returned, `matched_terms` populated from the seam's real per-record matched terms. **→ SC-1**
- [ ] 12. **SC-1 commit (**direct**).** `git add src/services/linguistic_service.py test/test_search_records_matched_terms_none_sc8_red.py && git commit -m "fix(search): thread gloss mode and normalize real hit shapes in search_records (SC-1)"` — test and change in one atomic slice, no co-author trailers.
- [ ] 13. **SC-2 RED (**task-card**).** Clean previous artifacts: `rm -f tmp/1404/artifacts/pipeline-red-*`. Dispatch `task(..., prompt: "execute red task from test-driven-development")`. Write the failing live-path test for `search_mode='Semantic All'` against the real `search_semantic('all')` contract — it must FAIL because `mode='all'` is never threaded. **→ SC-2**
- [ ] 14. **SC-2 RED confirm (**direct**).** Run the SC-2 RED test and confirm it FAILS for the right reason (missing `all` mode threading), not a fixture error. **→ SC-2**
- [ ] 15. **SC-2 GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")`. Implement the minimum change: thread `mode='all'` explicitly into `search_semantic` for `"Semantic All"`; extend the shared shape normalization and matched_terms consumption already landed for SC-1 to the `all` path. **→ SC-2**
- [ ] 16. **SC-2 GREEN confirm (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")`. Run the SC-2 RED test and confirm it PASSES; re-run the SC-1 test to confirm the shared path still holds. **→ SC-2**
- [ ] 17. **SC-2 post-regression (**direct**).** Clean previous artifacts: `rm -f tmp/1404/artifacts/pipeline-post-regression-*`. Run the SC-8 regression file plus neighboring service tests. **→ SC-2**
- [ ] 18. **SC-2 verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`. Verify against SC-2: no raise, `RecordSearchResult` returned, `matched_terms` populated from the seam's real per-record matched terms. **→ SC-2**
- [ ] 19. **SC-2 commit (**direct**).** `git add src/services/linguistic_service.py test/test_search_records_matched_terms_none_sc8_red.py && git commit -m "fix(search): thread all mode through search_records semantic dispatch (SC-2)"` — test and change in one atomic slice.
- [ ] 20. **SC-3 RED (**task-card**).** Clean previous artifacts: `rm -f tmp/1404/artifacts/pipeline-red-*`. Dispatch `task(..., prompt: "execute red task from test-driven-development")`. Rewrite the SC-8 regression tests in `test/test_search_records_matched_terms_none_sc8_red.py` to exercise the REAL `search_semantic` hit shapes for both modes — the rewritten suite FAILS only if any shape stub remains or the real contract is not exercised. **→ SC-3**
- [ ] 21. **SC-3 GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")`. Make the rewritten suite PASS against the fixed dispatch: both container hits and `(record_id, score)` tuples exercised, only DB session/encoder patched, no `_search_strategies` shape stubs. **→ SC-3**
- [ ] 22. **SC-3 post-regression (**direct**).** Clean previous artifacts: `rm -f tmp/1404/artifacts/pipeline-post-regression-*`. Run the rewritten SC-8 suite plus neighboring service tests. **→ SC-3**
- [ ] 23. **SC-3 verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`. Verify against SC-3: no shape stubs remain, both real hit shapes covered for both modes, DB-session-only isolation. **→ SC-3**
- [ ] 24. **SC-3 commit (**direct**).** `git add test/test_search_records_matched_terms_none_sc8_red.py && git commit -m "test(search): rewrite SC-8 regression tests against real search_semantic hit shapes (SC-3)"` — test and any supporting change in one atomic slice.

#### Phase 1 VbC

- [ ] 25. **VbC (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`. Verify all Phase 1 exit conditions: SC-1, SC-2, SC-3 evidence artifacts present with PASS verdicts; three atomic commits landed in SC order.

**Concern transition:** Leaving the semantic dispatch fix and real-shape tests → entering whole-suite regression verification. Phase 2 depends on all three Phase 1 commits.

## Phase 2 — no-regression-check

**Concern:** One concern — whole-suite regression health after the Phase 1 dispatch changes are committed.

**Files:**
- `test/` (whole-suite run; any incidental test fix lands in the touched test files only)

**SCs:** SC-4

**Dependencies:** Phase 1 (all three SC commits landed)

**Entry Conditions:**
- Phase 1 VbC passed
- SC-1, SC-2, SC-3 committed

**Exit Conditions:**
- `uv run pytest test/` reports zero failures
- Any incidental fix required to keep suites green is committed with its verifying test run

**Code Path Coverage:** Whole-suite execution over `test/` — no new production code paths; any fix is confined to incidental breakage surfaced by the run.

**Cross-Cutting SCs:** SC-4 is the only cross-cutting SC in the plan (it spans all suites) and is owned entirely by this phase.

**Interface Boundaries:** None new — this phase verifies existing boundaries.

**State Transitions:** None.

**Cost frame:** Running the full suite costs minutes of execution time. Skipping means a silent regression ships into review and PR CI — caught days later at 10×–100× the cost of this phase's single test run.

### Step-by-step

- [ ] 26. **post-regression (**task-card**).** Clean previous artifacts: `rm -f tmp/1404/artifacts/pipeline-regression-check-*`. Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")`. Run the full suite `uv run pytest test/` and report the failure list, if any. **→ SC-4**
- [ ] 27. **verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`. Clean previous artifacts: `rm -f tmp/1404/artifacts/pipeline-verify-*`. Verify against SC-4: zero failures across the suite; if any failure exists, classify it as incidental (fix here) or Phase 1 defect (return to Phase 1 remediation). **→ SC-4**
- [ ] 28. **incidental-fix commit if needed (**direct**).** If the verify step required an incidental fix, commit it: `git add <touched files> && git commit -m "test: keep suites green after semantic dispatch fix (SC-4)"`. If no fix was needed, record PASS with no commit. **→ SC-4**
- [ ] 29. **SC-4 verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")`. Final SC-4 verdict: suite green, evidence artifact written. **→ SC-4**

#### Phase 2 VbC

- [ ] 30. **VbC (**direct**).** Confirm Phase 2 exit conditions: suite green, SC-4 verdict PASS recorded.

**Concern transition:** Leaving regression verification → entering post-implementation gates.

## Post-Implementation Steps

**Cost frame:** Running the audit, structural checks, and pre-PR gate costs minutes each. Skipping any gate means a spec-fidelity or evidence-type defect surfaces in review — or worse, ships — at compounding cost far above the bounded execution cost paid here.

- [ ] 31. **audit (**task-card**).** Clean previous artifacts: `rm -f tmp/1404/artifacts/pipeline-audit-*`. Dispatch `task(..., prompt: "execute verification-audit DiMo investigator from audit. Read \`audit/tasks/verification-audit-investigator.md\` first")` — followed by validator, evaluator, arbiter in sequence. Adversarial audit of the deliverable against the spec.
- [ ] 32. **z3-check (**direct**).** Clean previous artifacts: `rm -f tmp/1404/artifacts/pipeline-z3-check-*`. Run `.opencode/tools/solve check --state-path ... --contract-path ...` against the phase state and dependency contract for this issue.
- [ ] 33. **structural-checks (**task-card**).** Clean previous artifacts: `rm -f tmp/1404/artifacts/pipeline-structural-checks-*`. Dispatch `task(..., prompt: "execute checklist task from finishing-a-development-branch")`. Run lint, typecheck, and the finishing checklist.
- [ ] 34. **pre-pr-gate (**task-card**).** Clean previous artifacts: `rm -f tmp/1404/artifacts/pipeline-pre-pr-gate-*`. Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — reads all SC verdicts (SC-1 through SC-4), BLOCKs if any FAIL. DONE_WITH_CONCERNS coerces to FAIL.
- [ ] 35. **regression-check (**task-card**).** Clean previous artifacts: `rm -f tmp/1404/artifacts/pipeline-regression-check-*`. Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")`. Final regression check before PR creation.
- [ ] 36. **review-prep (**task-card**).** Dispatch `task(..., prompt: "execute review-prep from git-workflow-pr. Read \`git-workflow-pr/tasks/review-prep.md\` first")`. Prepare PR review context.
- [ ] 37. **create-pr (**task-card**).** Dispatch `task(..., prompt: "execute create task from git-workflow-pr")`. Create the stacked PR targeting the trunk; squash to one commit per issue at PR time; co-author trailers added at squash.
- [ ] 38. **exec-summary (**task-card**).** Dispatch `task(..., prompt: "execute completion task from completion-core")`. Generate the completion executive summary and append the `plan_created` lifecycle record with `plan_file: .issues/1404/plan.md` and `phase_count: 2`.

## Exit Criteria

- [ ] C1. `search_records(search_mode='Semantic Gloss')` does not raise and returns a `RecordSearchResult` with `matched_terms` populated from the seam's real per-record matched terms (SC-1)
- [ ] C2. `search_records(search_mode='Semantic All')` does not raise and returns a `RecordSearchResult` with `matched_terms` populated from the seam's real per-record matched terms (SC-2)
- [ ] C3. Regression tests exercise real `search_semantic` hit shapes for both modes with only DB session/encoder patched — no shape stubs remain (SC-3)
- [ ] C4. `uv run pytest test/` reports zero failures (SC-4)
- [ ] C5. All four SC verdicts PASS with behavioral evidence; audit, z3-check, structural checks, and pre-PR gate all clean before PR creation

## Pre-Flight Guard (Mandatory)

Check your tool list for a tool named `task`.

- Present ⇒ orchestrator — proceed.
- Absent ⇒ sub-agent — do NOT execute any instruction below. Return `BLOCKED` with `ORCHESTRATOR_ONLY_SKILL_CARD` (cards) or `ORCHESTRATOR_ONLY_PLAN` (plans) and halt.

## Lifecycle Events

- event: plan_created
  timestamp: 2026-10-03T19:20:00+00:00
  detail: >-
    Plan file verified at .issues/1404/plan.md with dependency contract present.
    2 phases (semantic-dispatch-fix-and-real-shape-tests, no-regression-check),
    4 SCs. Execution strategy: mixed direct + task-card dispatch with
    test-driven-development / verification-before-completion cycles per SC,
    post-implementation gates (audit, z3-check, structural-checks, pre-pr-gate,
    regression-check, review-prep, create-pr, exec-summary) after Phase 2.
    Recommended next pipeline step: Phase 1 pre-regression (step 3).
  plan_file: .issues/1404/plan.md
  phase_count: 2

- event: plan_concern_map_sync
  timestamp: 2026-10-03T19:15:00+00:00
  detail: >-
    Validation category 4 FAIL remediation (non-substantive artifact sync):
    concern-map.yaml phase_boundary values synced to the plan's 2-phase structure —
    C1/C2/C3/C4 → Phase 1 (semantic-dispatch-fix-and-real-shape-tests), C5 → Phase 2
    (no-regression-check). Plan structure unchanged; no phase split, no SC remapping.
  source: .issues/1404/artifacts/validate-findings.yaml (category_4_concern_separation)
  synced_artifact: .issues/1404/artifacts/concern-map.yaml
