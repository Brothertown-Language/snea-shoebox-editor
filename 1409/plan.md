---
plan_schema_version: "1.0"
issue: 1409
title: "Fix Streamlit dual-set widget warning on semantic threshold slider"
authorization_scope: for_pr
pr_strategy: stacked
phase_count: 3
dispatch:
  - "phase-1: test-driven-development (red, green), verification-before-completion (verify), commit-inline (orchestrator)"
  - "phase-2: test-driven-development (red, green), verification-before-completion (verify), commit-inline (orchestrator)"
  - "phase-3: test-driven-development (red, green), verification-before-completion (verify), commit-inline (orchestrator)"
  - "post-implementation: audit, solve z3-check (orchestrator), finishing-a-development-branch (checklist), verification-before-completion (verify), test-driven-development (phase-4), git-workflow-pr (review-prep, create), completion-core (completion)"
---

# Implementation Plan — #1409 — Fix Streamlit dual-set widget warning on semantic threshold slider

**Issue:** .issues/1409/spec.md — https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1409

**Goal:** Eliminate the Streamlit `SessionStateReinitializationWarning` dual-set warning on the Records page semantic threshold widgets by making session state the sole source of widget values, while preserving all rendered threshold behavior.

**Architecture:** Restructure the widget instantiation block in `src/frontend/pages/records.py` so widget-bound keys (`semantic_threshold_slider`, `semantic_threshold_number`) are written to session state exactly once at/before first instantiation and the explicit `value=` arguments are removed from `st.slider` / `st.number_input`. Backing-value seeding, `_validate_threshold()` guard, `on_change` callbacks, and preference persistence are untouched. Evidence is behavioral (Playwright real-browser per the repo UI testing standard); preservation gates (SC-1b, SC-2, SC-3a, SC-3b) verify no regression to default/override rendering, and SC-4 is a full-suite regression gate.

**Files:**
- `src/frontend/pages/records.py`
- `test/ui/test_sc9_ui_threshold_default_red.py` (and related `test/ui/` fixtures)
- `test/` (pytest suite — verification surface only)
- `docs/development/ui_testing_standard.md` (read-only prerequisite)

---

## Phase Table

| Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch |
|-------|------|---------|-----|------------|------------|----------|
| 1 | Core dual-set fix | Widget-instantiation mechanics — remove dual-set | SC-1a | — | 3–8 | task-card (3–5, 7–8) + direct (6) |
| 2 | Preservation gates (behavioral invariants) | Preserve default/override/rerun rendering | SC-1b, SC-2, SC-3a, SC-3b | 1 | 9–25 | task-card (9–11, 13–15, 17–19, 21–23, 25) + direct (12, 16, 20, 24) |
| 3 | Full suite regression gate | Zero new failures vs baseline | SC-4 | 2 | 26–30 | task-card (26–28, 30) + direct (29) |
| Post | Verification, audit, PR | Completion gates | all | 3 | 31–38 | task-card (31, 33–38) + direct (32) |

## Pre-Implementation Steps

- [ ] 1. **Coherence gate (**direct**).** Confirm spec `.issues/1409/spec.md` has 6 SCs (SC-1a, SC-1b, SC-2, SC-3a, SC-3b, SC-4), all behavioral; confirm phase/SC mapping in `.issues/1409/artifacts/plan-input-verification.md` matches this plan's phase table; confirm no phase's RED depends on a later phase's output.
- [ ] 2. **Baseline check (**direct**).** Confirm live app availability for Playwright evidence (`:8501`, `SNEA_E2E=1` when up), the repo UI testing standard (`docs/development/ui_testing_standard.md`) has been read, and the current `uv run pytest test/` pass/fail set is recorded as the SC-4 baseline under `tmp/issue-1409/artifacts/`.

## Self-Remediation Protocol

> **Self-Remediation Protocol:** If a step FAILs: diagnose root cause, fix the deliverable, re-verify. If the fix requires spec revision, update the spec and re-enter the plan. Escalate only after remediation failure.

## Exit Criteria

- [ ] C1. SC-1a passes: with a saved `records/semantic_threshold` preference present, the Records page shows no Streamlit widget-state warning box for the semantic threshold widgets (Playwright, live app, screenshot artifact).
- [ ] C2. SC-1b passes: the slider renders the seeded saved value with a saved preference present (Playwright, screenshot artifact).
- [ ] C3. SC-2 passes: with no saved preference, the slider defaults to 0.93 (existing SC-9 fresh-default test).
- [ ] C4. SC-3a passes: saved-override round-trip (edit → persist → render) preserved.
- [ ] C5. SC-3b passes: saved value survives page rerun/navigation without resetting to default (unconditional suite assertion).
- [ ] C6. SC-4 passes: `uv run pytest test/` shows zero new failures vs the recorded baseline.
- [ ] C7. All SC verdicts PASS at the pre-PR gate; no E2E skip silently treated as PASS.

## Pre-Flight Guard (Mandatory)

Check your tool list for a tool named `task`.

- Present ⇒ orchestrator — proceed.
- Absent ⇒ sub-agent — do NOT execute any instruction below. Return `BLOCKED` with `ORCHESTRATOR_ONLY_SKILL_CARD` (cards) or `ORCHESTRATOR_ONLY_PLAN` (plans) and halt.

---

# Phase 1 — Core dual-set fix

**Concern:** Remove the Streamlit dual-set anti-pattern from the semantic threshold widget instantiation block so session state is the sole source of widget values.

**Files:**
- `src/frontend/pages/records.py` (widget instantiation block)
- `test/ui/test_sc9_ui_threshold_default_red.py` (new saved-preference Playwright test + dedicated fixture)

**SCs:** SC-1a

**Dependencies:** None

**Entry Conditions:**
- Coherence gate and baseline check (steps 1–2) passed
- Feature branch exists; live app available on :8501 with `SNEA_E2E=1` for Playwright evidence

**Exit Conditions:**
- Widget-bound keys are written to session state at most once per session (at/before first instantiation); no explicit `value=` argument remains on the keyed `st.slider` / `st.number_input` calls
- Redundant unconditional pre-instantiation re-sync writes removed
- SC-1a Playwright test passes with a saved preference present; screenshot artifact captured

**Code Path Coverage:** pre-instantiation widget-key seeding (kept, made sole value source); unconditional re-sync writes (removed); widget instantiation with explicit `value=` (removed kwarg). Backing-value seeding, `on_change` callbacks, `_validate_threshold` guard, and consumers are untouched.

**Cross-Cutting SCs:** SC-1a spans widget-instantiation-mechanics and test-infrastructure (dedicated fixture that survives `_delete_saved_threshold_preferences` deletion, per R-6).

**Interface Boundaries:** widget calls → Streamlit session-state API CHANGED internally (drop `value=` for the keyed widgets; `key=`, `on_change=`, min/max/step/label unchanged). All other boundaries preserved.

**State Transitions:** widget-bound keys go absent → seeded exactly once (backing value); rerun reads seeded value with NO re-seeding writes. Unconditional re-sync writes and `value=` overriding seeded state are forbidden transitions.

**Cost frame:** Running the saved-preference Playwright warning-absence test costs minutes of live-app execution — a bounded behavioral gate that catches the dual-set defect before it compounds. Skipping it costs the full rework pipeline when the warning ships on every real user's Records page load — the 1000× production discovery path. Correctness is the only metric.

---

- [ ] 3. **Pre-step cleanup (**direct**).** Remove stale step artifacts: `rm -f tmp/issue-1409/artifacts/pipeline-red-* tmp/issue-1409/artifacts/pipeline-green-* tmp/issue-1409/artifacts/pipeline-pre-regression-*`.
- [ ] 4. **RED (**task-card**).** Write a failing Playwright real-browser test: seed a saved `records/semantic_threshold` preference via a dedicated fixture that survives `_delete_saved_threshold_preferences`, load Records, and assert the rendered page contains no Streamlit widget-state warning box for the semantic threshold widgets. The test FAILS because the dual-set warning still occurs. **→ SC-1a**
    - Dispatch: `task(..., prompt: "execute red task from test-driven-development")`
    - Evidence: screenshot artifact under `tmp/issue-1409/artifacts/`
- [ ] 5. **GREEN (**task-card**).** Restructure the widget instantiation block: write widget-bound keys to session state exactly once at/before first instantiation; remove the explicit `value=` arguments from the keyed widget calls; remove the redundant unconditional pre-instantiation re-sync writes. No other behavior changes. **→ SC-1a**
    - Dispatch: `task(..., prompt: "execute green task from test-driven-development")`
    - Constraint: backing-value seeding, `_validate_threshold()` guard, `on_change` callbacks, and persistence are untouched
- [ ] 6. **Verify (**task-card**).** Verify SC-1a: the Playwright test passes against the live app on :8501 (`SNEA_E2E=1`); warning-absence assertion holds for both widget keys; screenshot artifact captured. **→ SC-1a**
    - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`
- [ ] 7. **COMMIT (**direct**).** Commit the widget block change and the new test together as one atomic slice: `git add src/frontend/pages/records.py test/ui/test_sc9_ui_threshold_default_red.py && git commit -m "fix(records): make session state sole source of semantic threshold widget values (SC-1a)"`. No co-author trailers at implementation time.

#### Phase 1 VbC

- [ ] 8. **Phase completion (**task-card**).** Verify: no `value=` on the keyed widget calls; widget keys seeded at most once per session; SC-1a test passes; commit contains test + change. **→ SC-1a**
    - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`

**Concern transition:** Leaving widget-instantiation mechanics → entering behavioral invariant preservation. Phase 2 depends on Phase 1's committed restructure.

# Phase 2 — Preservation gates (behavioral invariants)

**Concern:** Preserve the #1400 default/override rendering contract, the round-trip persistence flow, and rerun stability after the Phase 1 widget-block restructure.

**Files:**
- `test/ui/test_sc9_ui_threshold_default_red.py` (and related `test/ui/` fixtures)
- `src/frontend/pages/records.py` (only if a regression fix is needed)

**SCs:** SC-1b, SC-2, SC-3a, SC-3b

**Dependencies:** Phase 1 (SC-1a committed restructure)

**Entry Conditions:**
- Phase 1 exit conditions met; SC-1a committed
- Live app available on :8501 with `SNEA_E2E=1`

**Exit Conditions:**
- Saved-value rendering, 0.93 fresh-default, override round-trip, and rerun survival all verified against the restructured widget block
- Any regression introduced by the restructure is fixed and committed

**Code Path Coverage:** backing-value seeding (preserved per R-2); `on_change` callbacks → backing value → `PreferenceService.set_preference` (preserved per R-4); `_validate_threshold` guard restoring last accepted value (preserved per R-3); test fixtures (dedicated saved-preference fixture reused from Phase 1; existing tests as gates).

**Cross-Cutting SCs:** SC-1b spans widget-instantiation-mechanics and preference-persistence (verifies the seeding/persistence seam); SC-3b spans widget-instantiation-mechanics and the Streamlit rerun lifecycle.

**Interface Boundaries:** widget-block → session_state backing value preserved; on_change → backing value → PreferenceService preserved; `_validate_threshold` → session_state preserved; test fixture contract extended (rerun assertion added unconditionally).

**State Transitions:** absent → 0.93 with no saved preference (SC-2); absent → saved value with saved preference (SC-1b); current → effective value via on_change + persistence (SC-3a); rerun reads existing session-state values with no re-seeding writes (SC-3b); invalid edit renders last accepted value (R-3).

**Cost frame:** Running the four preservation Playwright gates costs minutes of live-app execution — a bounded check that catches any rendering regression before commit. Skipping them costs the full rework pipeline when a broken 0.93 default or a resetting saved override ships to users — the 1000× production discovery path. Correctness is the only metric.

---

- [ ] 9. **RED — item 2 (**task-card**).** Extend the Phase 1 Playwright test to assert the slider renders the seeded saved value. Record this assertion passing against the current (restructured) code as the preservation baseline. **→ SC-1b**
    - Dispatch: `task(..., prompt: "execute red task from test-driven-development")`
    - Cleanup first: `rm -f tmp/issue-1409/artifacts/pipeline-red-*`
- [ ] 10. **GREEN — item 2 (**task-card**).** No production change beyond Phase 1; fix any regression the restructure introduced to saved-value rendering. **→ SC-1b**
    - Dispatch: `task(..., prompt: "execute green task from test-driven-development")`
- [ ] 11. **Verify — item 2 (**task-card**).** Slider renders the saved value with a saved preference present; screenshot artifact captured. **→ SC-1b**
    - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`
- [ ] 12. **COMMIT — item 2 (**direct**).** Commit the test assertion plus any regression fix in one atomic slice: `git add test/ui/test_sc9_ui_threshold_default_red.py src/frontend/pages/records.py && git commit -m "test(records): assert saved threshold value renders (SC-1b)"`.

- [ ] 13. **RED — item 3 (**task-card**).** Baseline run of the existing SC-9 fresh-default Playwright test to record the passing state (preservation gate; runs against the restructured code and must pass). **→ SC-2**
    - Dispatch: `task(..., prompt: "execute red task from test-driven-development")`
    - Cleanup first: `rm -f tmp/issue-1409/artifacts/pipeline-red-*`
- [ ] 14. **GREEN — item 3 (**task-card**).** No production change beyond Phase 1; fix any regression the restructure introduced to fresh-default seeding (0.93). **→ SC-2**
    - Dispatch: `task(..., prompt: "execute green task from test-driven-development")`
- [ ] 15. **Verify — item 3 (**task-card**).** Fresh-default test asserts 0.93 rendering with the no-preference precondition. **→ SC-2**
    - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`
- [ ] 16. **COMMIT — item 3 (**direct**).** Commit any regression fix and baseline evidence: `git add -A test/ui/ && git commit -m "test(records): preserve 0.93 calibrated default (SC-2)"`.

- [ ] 17. **RED — item 4 (**task-card**).** Baseline run of the existing DOM round-trip Playwright test (edit → persist → render) to record the passing state. **→ SC-3a**
    - Dispatch: `task(..., prompt: "execute red task from test-driven-development")`
    - Cleanup first: `rm -f tmp/issue-1409/artifacts/pipeline-red-*`
- [ ] 18. **GREEN — item 4 (**task-card**).** Ensure the on_change callback → backing value → persistence flow is intact after the widget-block restructure; rendered value equals the edited value after persistence. **→ SC-3a**
    - Dispatch: `task(..., prompt: "execute green task from test-driven-development")`
- [ ] 19. **Verify — item 4 (**task-card**).** Round-trip test (edit → persist → render) passes post-change. **→ SC-3a**
    - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`
- [ ] 20. **COMMIT — item 4 (**direct**).** Commit test additions plus any needed adjustment in one atomic slice: `git add -A test/ui/ src/frontend/pages/records.py && git commit -m "test(records): preserve override round-trip (SC-3a)"`.

- [ ] 21. **RED — item 5 (**task-card**).** Add a rerun/navigation Playwright assertion — after a page rerun, the rendered value equals the saved value and does not reset to the default — included unconditionally in the suite. **→ SC-3b**
    - Dispatch: `task(..., prompt: "execute red task from test-driven-development")`
    - Cleanup first: `rm -f tmp/issue-1409/artifacts/pipeline-red-*`
- [ ] 22. **GREEN — item 5 (**task-card**).** Ensure the widget-block restructure preserves rerun stability — no re-seeding writes; widgets read existing session-state values on rerun. **→ SC-3b**
    - Dispatch: `task(..., prompt: "execute green task from test-driven-development")`
- [ ] 23. **Verify — item 5 (**task-card**).** Rerun assertion passes post-change against the live app. **→ SC-3b**
    - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`
- [ ] 24. **COMMIT — item 5 (**direct**).** Commit the test addition plus any needed adjustment in one atomic slice: `git add test/ui/test_sc9_ui_threshold_default_red.py src/frontend/pages/records.py && git commit -m "test(records): saved threshold survives rerun (SC-3b)"`.

#### Phase 2 VbC

- [ ] 25. **Phase completion (**task-card**).** Verify all four preservation gates pass: saved-value rendering (SC-1b), 0.93 default (SC-2), round-trip (SC-3a), rerun survival (SC-3b); each item committed. **→ SC-1b, SC-2, SC-3a, SC-3b**
    - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`

**Concern transition:** Leaving behavioral invariant preservation → entering the full-suite regression gate. Phase 3 depends on all Phase 2 items being committed.

# Phase 3 — Full suite regression gate

**Concern:** Prove the widget-block restructure introduces zero new failures across the full pytest suite.

**Files:**
- `test/` (full pytest suite — verification surface; no production change)

**SCs:** SC-4

**Dependencies:** Phase 2 (all preservation gates committed)

**Entry Conditions:**
- Phase 2 exit conditions met; SC-4 baseline recorded at step 2
- Live app on :8501 with `SNEA_E2E=1` when running the UI standard-of-record tier

**Exit Conditions:**
- Post-change `uv run pytest test/` shows zero new failures relative to the step-2 baseline
- Any new failure is diagnosed, fixed, and re-verified before proceeding

**Code Path Coverage:** aggregate regression signal across all concerns — the suite exercises every code path touched or adjacent to the widget block (backing-value seeding, validation guard, callbacks, persistence, consumers).

**Cross-Cutting SCs:** SC-4 spans all concerns and aggregates the regression signal across the change.

**Interface Boundaries:** none changed — this is a verification-only phase.

**State Transitions:** none changed — this is a verification-only phase.

**Cost frame:** Running the full pytest suite costs minutes of execution — a bounded gate that catches any adjacent regression before review. Skipping it costs weeks of discovery latency when an adjacent behavior regression reaches production ahead of the next scheduled suite run. Correctness is the only metric.

---

- [ ] 26. **RED (**task-card**).** Confirm the step-2 pre-change baseline record of `uv run pytest test/` (pass/fail set) is on disk under `tmp/issue-1409/artifacts/`. **→ SC-4**
    - Dispatch: `task(..., prompt: "execute red task from test-driven-development")`
    - Cleanup first: `rm -f tmp/issue-1409/artifacts/pipeline-red-*`
- [ ] 27. **GREEN (**task-card**).** Run the full suite post-change (`uv run pytest test/`, with `SNEA_E2E=1` when the live app is up) and compare against the baseline — zero new failures. **→ SC-4**
    - Dispatch: `task(..., prompt: "execute green task from test-driven-development")`
- [ ] 28. **Verify (**task-card**).** Verify the baseline comparison: pass/fail set post-change contains no new failures; evidence artifact written. **→ SC-4**
    - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`
- [ ] 29. **COMMIT (**direct**).** Commit the verification evidence as test evidence (no production change): `git add tmp/issue-1409/artifacts/ && git commit -m "test(records): full-suite regression gate evidence (SC-4)"`.

#### Phase 3 VbC

- [ ] 30. **Phase completion (**task-card**).** Verify SC-4: baseline comparison artifact exists and shows zero new failures. **→ SC-4**
    - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`

**Concern transition:** Leaving the regression gate → entering post-implementation completion gates. The post-implementation steps depend on Phase 3's clean suite run.

# Post-Implementation

**Concern:** Completion gates — adversarial audit, structural checks, pre-PR verification, PR creation, completion summary.

**Files:** none modified (verification and PR operations only)

**SCs:** all (SC-1a, SC-1b, SC-2, SC-3a, SC-3b, SC-4)

**Dependencies:** Phase 3

**Entry Conditions:** Phase 3 exit conditions met (zero new failures); all SC evidence artifacts on disk

**Exit Conditions:** all SC verdicts PASS at the pre-PR gate; PR created (stacked, targets trunk); completion summary generated

---

- [ ] 31. **Adversarial audit (**task-card**).** Run the adversarial audit of the deliverable against the spec's SCs — investigator, then validator, then evaluator, then arbiter in sequence. **→ all SCs**
    - Dispatch: `task(..., prompt: "execute verification-audit DiMo investigator from audit. Read \`audit/tasks/verification-audit-investigator.md\` first")`, followed by validator, evaluator, arbiter in sequence
    - Cleanup first: `rm -f tmp/issue-1409/artifacts/pipeline-audit-*`
- [ ] 32. **Z3 check (**direct**).** Run the Z3 constraint solver verification directly: `.opencode/tools/solve check --state-path <state> --contract-path <contract>`.
    - Cleanup first: `rm -f tmp/issue-1409/artifacts/pipeline-z3-check-*`
- [ ] 33. **Structural checks (**task-card**).** Run the finishing checklist (lint, typecheck, format, etc.) via `finishing-a-development-branch`. **→ all SCs**
    - Dispatch: `task(..., prompt: "execute checklist task from finishing-a-development-branch")`
    - Cleanup first: `rm -f tmp/issue-1409/artifacts/pipeline-structural-checks-*`
- [ ] 34. **Pre-PR gate (**task-card**).** Verify all SC verdicts before PR creation — reads all SC verdicts, BLOCKs if any FAIL (DONE_WITH_CONCERNS and EVIDENCE_TYPE_MISMATCH coerce to FAIL). **→ all SCs**
    - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`
    - Cleanup first: `rm -f tmp/issue-1409/artifacts/pipeline-pre-pr-gate-*`
- [ ] 35. **Final regression check (**task-card**).** Final regression run before PR. **→ SC-4**
    - Dispatch: `task(..., prompt: "execute phase-4 task from test-driven-development")`
    - Cleanup first: `rm -f tmp/issue-1409/artifacts/pipeline-regression-check-*`
- [ ] 36. **Review prep (**task-card**).** Prepare PR review context. **→ all SCs**
    - Dispatch: `task(..., prompt: "execute review-prep from git-workflow-pr. Read \`git-workflow-pr/tasks/review-prep.md\` first")`
- [ ] 37. **Create PR (**task-card**).** Create the pull request (stacked strategy, targets trunk). PR body carries no auto-closing keywords for stakeholder-facing issues. Human-only merge — HALT after PR creation; do not merge. **→ all SCs**
    - Dispatch: `task(..., prompt: "execute create task from git-workflow-pr")`
- [ ] 38. **Completion summary (**task-card**).** Generate the completion executive summary. **→ all SCs**
    - Dispatch: `task(..., prompt: "execute completion task from completion-core")`

---

## Enforcement Gate

> **Enforcement gate:** All SCs must pass before this plan is complete.

---

## Lifecycle Events

- 20261003235343 — plan_created — plan verified at `.issues/1409/plan.md`; 3 implementation phases + post-implementation; dependency contract present at `.issues/1409/dependency-contract.yaml`.

---

🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
