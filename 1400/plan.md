---
plan_schema_version: "1.0"
issue: 1400
title: "Gloss-space semantic threshold calibration (backend/seam)"
authorization_scope: for_pr
pr_strategy: stacked
phase_count: 3
dispatch:
  - phase-1: "test-driven-development (red, green, phase-4 post-regression); verification-before-completion (verify); orchestrator commit-inline"
  - phase-2: "test-driven-development (red, green, phase-4 post-regression); verification-before-completion (verify); orchestrator commit-inline"
  - phase-3: "test-driven-development (red, green, phase-4 post-regression); verification-before-completion (verify); orchestrator commit-inline"
---

# Implementation Plan — #1400 — Gloss-space semantic threshold calibration (backend/seam)

- **Issue:** .issues/1400/spec.md (remote: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1400)

**Goal:** Calibrate a real-data default threshold floor for the gloss-space `search_semantic()` seam from the production replica, engage it when `threshold=None` (with honest all-below-floor outcomes and preserved explicit-override control), and sync the UI default threshold state to the published floor.

**Architecture:** Three-phase linear pipeline. Phase 1 derives per-anchor calibration floors with provenance from real corpus queries and publishes a named calibration constant (evidence artifact + module constant, strictly between the measured out-of-corpus max 0.84 and in-corpus min 0.93, floor ≤ 0.90). Phase 2 implements default-on-`None` semantics in the seam of `src/services/semantic_search_service.py` and maps the all-below-floor outcome onto `status=ok` + empty results + message (unchanged signature and status enum per R-3). Phase 3 syncs the `st.session_state.semantic_threshold` default in `src/frontend/pages/records.py` to the published floor and verifies override passthrough with Playwright per `docs/development/ui_testing_standard.md`.

**Files:**
- `src/services/semantic_search_service.py`
- `src/frontend/pages/records.py`
- `src/services/embedding_service.py` (read-only dependency — PIN `thenlper/gte-small`)
- `test/test_semantic_threshold_red.py`, plus new pytest calibration/seam test files
- `test/ui/test_semantic_search_ui_flow_e2e.py` (Playwright, SC-9/SC-10)
- calibration evidence artifact (new, per-anchor floors + provenance)

---

> **Compliance:** All SCs must pass before completion. Partial implementation is not permitted. Each item is daisy-chained — item N's commit is precondition for item N+1's RED.

> **One step at a time.** Execute exactly one step. Report progress. Wait for instruction before the next step.

> **Step status:** Report `[item N] [PASS|FAIL]` after each step. If FAIL, report blocker and halt.

> **Self-Remediation Protocol:** If a step FAILs: diagnose root cause, fix the deliverable, re-verify. If the fix requires spec revision, update the spec and re-enter the plan. Escalate only after remediation failure.

> **Enforcement gate:** All SCs must pass before this plan is complete.

---

## Phase Table

| Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch |
|-------|------|---------|-----|------------|-----------|----------|
| 1 | Real-data calibration of the semantic-seam default floor | calibration | SC-1, SC-8 | — | 3-12 | direct (2) + task-card (3-12) |
| 2 | Seam default-floor semantics (threshold=None) + all-below-floor outcome | seam | SC-2..SC-7 | 1 | 13-42 | direct (0) + task-card (13-42) |
| 3 | UI threshold plumbing — default parity and override preservation | ui plumbing | SC-9, SC-10 | 2 | 43-52 | direct (0) + task-card (43-52) |
| — | Post-implementation (audit → PR) | pipeline closeout | all | 1,2,3 | 53-60 | mixed (per step) |

Pre-implementation steps 1-2 run once before Phase 1. Post-implementation steps 53-60 run once after Phase 3.

---

## Phase Details

### Phase 1 — Real-data calibration of the semantic-seam default floor

| Field | Value |
|-------|-------|
| Skill | `test-driven-development`, `verification-before-completion` |
| Task | red, green, post-regression, verify, commit |
| Target | calibration evidence artifact + module-level calibration constant in `src/services/semantic_search_service.py` |
| SCs | SC-1, SC-8 |
| Depends On | — |

**Context:**

- Corpus: production replica, 6,681 embedded glosses, pin `thenlper/gte-small`, synced 2026-10-02
- Measured distributions: in-corpus exact match 0.93–1.00 at rank 1; out-of-corpus max 0.84; out-of-corpus bulk p50 0.75–0.77
- Floor constraint: float strictly in (0.84, 0.93), floor ≤ 0.90
- Provenance required per anchor: query battery, corpus pin, date
- Synthetic queries prohibited (R-1)

### Phase 2 — Seam default-floor semantics (threshold=None) + all-below-floor outcome

| Field | Value |
|-------|-------|
| Skill | `test-driven-development`, `verification-before-completion` |
| Task | red, green, post-regression, verify, commit |
| Target | `src/services/semantic_search_service.py` — `search_semantic()`, `_candidate_sql()` threshold filter, post-query result assembly |
| SCs | SC-2, SC-3, SC-4, SC-5, SC-6, SC-7 |
| Depends On | 1 |

**Context:**

- Seam signature: `search_semantic(mode, query, threshold, source_id, limit) -> SemanticSearchResult` — unchanged (R-3)
- Status enum: `ok`, `empty_query`, `no_embeddings`, `stale_model` — unchanged (R-3)
- Below-floor outcome: `status=ok` + empty results + deficiency message (mirrors existing empty-results branch shape and `.issues/36` R-7)
- Stateless per call — no module-level sticky threshold state
- Override precedence: explicit threshold value > default; `None` → default

### Phase 3 — UI threshold plumbing — default parity and override preservation

| Field | Value |
|-------|-------|
| Skill | `test-driven-development`, `verification-before-completion` |
| Task | red, green, post-regression, verify, commit |
| Target | `src/frontend/pages/records.py` — `st.session_state.semantic_threshold` default literals and override passthrough |
| SCs | SC-9, SC-10 |
| Depends On | 2 |

**Context:**

- UI standard: `docs/development/ui_testing_standard.md` — Playwright real-browser evidence; AppTest is smoke-only for these SCs
- Default parity: `semantic_threshold` default = published floor ± 0.01 on fresh session
- Preserve: session-state key name, [0.0, 1.0] `_validate_threshold` guard, PreferenceService authority, override passthrough to seam
- E2E gating: `SNEA_E2E=1` + live app on :8501; skips reported as skipped, never as PASS
- Auth state: one-time OAuth login procedure per ui_testing_standard when saved auth state is missing

---

## Pre-Implementation (once per plan)

- [ ] 1. **Coherence gate (**direct**).** Read the ledger at `.issues/1400/artifacts/plan-input-verification.md`; confirm every SC (SC-1..SC-10) maps to exactly one phase and one plan item, the phase DAG is linear and acyclic (1 → 2 → 3), and each phase's red/green/post-regression/verify/commit skill+task selection matches the implementation-workflow reference card. **→ all SCs**
- [ ] 2. **Baseline check (**direct**).** Verify production replica is freshly synced (`bash scripts/sync_prod_to_local.sh`), the feature branch exists, and existing seam/UI tests (`test/test_semantic_threshold_red.py` and siblings listed in the blast radius) pass before the first RED. Record the measured pre-calibration baseline (in-corpus rank-1 cosine 0.93–1.00) for SC-8 comparison. **→ all SCs**

---

## Phase 1 — Real-data calibration of the semantic-seam default floor

> See `plan-01-calibration.md`.

---

## Phase 2 — Seam default-floor semantics (threshold=None) + all-below-floor outcome

> See `plan-02-seam-default-floor.md`.

---

## Phase 3 — UI threshold plumbing — default parity and override preservation

> See `plan-03-ui-threshold-plumbing.md`.

---

## Post-Implementation (once per plan)

- [ ] 53. **Audit (**task-card**).** Dispatch `task(..., prompt: "execute verification-audit DiMo investigator from audit. Read \`audit/tasks/verification-audit-investigator.md\` first")`, then validator, evaluator, arbiter in sequence. **→ all SCs**
- [ ] 54. **Z3 check (**direct**).** Run `.opencode/tools/solve check --state-path {project_root}/tmp/1400/state.yaml --contract-path {project_root}/tmp/1400/constraints.yaml` directly. **→ pipeline dependency integrity**
- [ ] 55. **Structural checks (**task-card**).** `task(..., prompt: "execute checklist task from finishing-a-development-branch")` — lint, typecheck, finishing checklist. **→ all SCs (code hygiene)**
- [ ] 56. **Pre-PR gate (**task-card**).** `task(..., prompt: "execute verify task from verification-before-completion")` — read all SC verdicts; BLOCK if any FAIL (DONE_WITH_CONCERNS coerces to FAIL). **→ all SCs**
- [ ] 57. **Regression check (**task-card**).** `task(..., prompt: "execute phase-4 task from test-driven-development")` — final regression batch before PR. **→ all SCs (non-regression)**
- [ ] 58. **Review prep (**task-card**).** `task(..., prompt: "execute review-prep from git-workflow-pr. Read \`git-workflow-pr/tasks/review-prep.md\` first")`. **→ review readiness**
- [ ] 59. **Create PR (**task-card**).** `task(..., prompt: "execute create task from git-workflow-pr")` — stacked PR targeting the trunk; squash to one commit for the issue at PR creation. PR creation then HALT for human review — agents never merge. **→ pr_created**
- [ ] 60. **Executive summary (**task-card**).** `task(..., prompt: "execute completion task from completion-core")` — completion report with SC verdict table and byline. **→ completion**

---

## Exit Criteria

- [ ] C1. Calibration evidence artifact exists with per-anchor floor values and full source provenance (query battery, corpus pin, date) for in-corpus and out-of-corpus batteries; no synthetic queries. **→ SC-1**
- [ ] C2. Published calibrated default floor is a named constant strictly between 0.84 and 0.93, ≤ 0.90, carrying provenance. **→ SC-1, SC-2**
- [ ] C3. `search_semantic(threshold=None)` filters on the calibrated floor; explicit values override; `None` after an override re-engages the default. **→ SC-2, SC-3, SC-4**
- [ ] C4. All-below-floor outcome returns `status=ok`, empty `results`, deficiency message — no exception, no below-floor rows served. **→ SC-5, SC-6, SC-7**
- [ ] C5. Default threshold: in-corpus battery targets rank at rank 1 with cosine ≥ 0.90 (no recall regression vs baseline 0.93–1.00). **→ SC-8**
- [ ] C6. Fresh-session `st.session_state.semantic_threshold` equals the published floor within ±0.01; UI overrides reach the seam unchanged. **→ SC-9, SC-10**
- [ ] C7. All pytest suites pass; Playwright SC-9/SC-10 evidence captured per ui_testing_standard (skips reported as skipped, never as PASS). **→ SC-8, SC-9, SC-10, non-regression**
- [ ] C8. Stacked PR created; all post-implementation gates (audit, Z3, structural checks, pre-PR gate, regression check) PASS. **→ pipeline completion**

---

## Pre-Flight Guard (Mandatory)

Check your tool list for a tool named `task`.

- Present ⇒ orchestrator — proceed.
- Absent ⇒ sub-agent — do NOT execute any instruction below. Return `BLOCKED` with `ORCHESTRATOR_ONLY_SKILL_CARD` (cards) or `ORCHESTRATOR_ONLY_PLAN` (plans) and halt.

---

## lifecycle_events

- 2026-10-02T16:13:51Z — plan_created — plan verified at `.issues/1400/plan.md`; 3 phases + pre-implementation (2 steps) + post-implementation (8 steps); dispatch: phase-1/2/3 task-card via test-driven-development + verification-before-completion with orchestrator commit-inline; dependency contract present at `.issues/1400/dependency-contract.yaml`.
