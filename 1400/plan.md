---
plan_schema_version: "1.0"
issue: 1400
title: "Gloss-space semantic threshold calibration (backend/seam)"
authorization_scope: for_pr
pr_strategy: stacked
phase_count: 4
dispatch:
  - phase-1: "test-driven-development (red, green, phase-4 post-regression); verification-before-completion (verify); orchestrator commit-inline"
  - phase-2: "test-driven-development (red, green, phase-4 post-regression); verification-before-completion (verify); orchestrator commit-inline"
  - phase-3: "test-driven-development (red, green, phase-4 post-regression); verification-before-completion (verify); orchestrator commit-inline"
  - phase-4: "test-driven-development (red, green, phase-4 post-regression); verification-before-completion (verify); orchestrator commit-inline"
---

# Implementation Plan — #1400 — Gloss-space semantic threshold calibration (backend/seam)

- **Issue:** .issues/1400/spec.md (remote: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1400)

**Goal:** Calibrate a real-data default threshold floor for the gloss-space `search_semantic()` seam from the production replica, engage it when `threshold=None` (with honest all-below-floor outcomes and preserved explicit-override control), and sync the UI default threshold state to the published floor.

**Architecture:** Three-phase linear pipeline. Phase 1 derives per-anchor calibration floors with provenance from real corpus queries and publishes a named calibration constant (evidence artifact + module constant, strictly between the measured out-of-corpus max 0.9018 and the smallest floor-clearing in-corpus anchor 0.9753 — floor ∈ (0.9018, 0.9753); measured distributions overlap, so the in-corpus anchor "how many" 0.8917 legitimately falls below the floor and returns the below-floor empty outcome per SC-5 semantics). Phase 2 implements default-on-`None` semantics in the seam of `src/services/semantic_search_service.py` and maps the all-below-floor outcome onto `status=ok` + empty results + message (unchanged signature and status enum per R-3). Phase 3 syncs the `st.session_state.semantic_threshold` default in `src/frontend/pages/records.py` to the published floor and verifies override passthrough with Playwright per `docs/development/ui_testing_standard.md`. Phase 4 implements the pinned test-only auth bypass — a `SNEA_E2E`-gated auth bypass hook in the app's auth path (`src/services/security_manager.py` auth resolution) — so the Playwright E2E tier authenticates headlessly (no headed OAuth login, no fabricated credentials; SC-11), with bypass inertness outside `SNEA_E2E=1` verified by pytest against the production auth path (SC-11a).

**Files:**
- `src/services/semantic_search_service.py`
- `src/frontend/pages/records.py`
- `src/services/embedding_service.py` (read-only dependency — PIN `thenlper/gte-small`)
- `test/test_semantic_threshold_red.py`, plus new pytest calibration/seam test files
- `test/ui/test_semantic_search_ui_flow_e2e.py` (Playwright, SC-9/SC-10)
- `src/services/security_manager.py` (app auth path — SC-11/SC-11a pinned test-only bypass hook location)
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
| 1 | Real-data calibration of the semantic-seam default floor | calibration (SC-1); recall-regression (SC-8, SC-8a) | SC-1, SC-8, SC-8a | — | 3-17 | direct (2) + task-card (3-17) |
| 2 | Seam default-floor semantics (threshold=None) + all-below-floor outcome | seam-default (SC-2..SC-4); floor-empty (SC-5..SC-7) | SC-2..SC-7 | 1 | 18-47 | direct (0) + task-card (18-47) |
| 3 | UI threshold plumbing — default parity and override preservation | ui-default (SC-9, SC-10) | SC-9, SC-10 | 2 | 48-57 | direct (0) + task-card (48-57) |
| 4 | E2E auth bypass — test-only SNEA_E2E-gated authentication | e2e-auth-bypass (SC-11, SC-11a) | SC-11, SC-11a | 3 | 66-74 | direct (0) + task-card (66-74) |
| — | Post-implementation (audit → PR) | pipeline closeout | all | 1,2,3,4 | 75-82 | mixed (per step) |

Pre-implementation steps 1-2 run once before Phase 1. Post-implementation steps 75-82 run once after Phase 4.

**Concern alignment (per validate-findings F-1/F-2/F-3, option (a) — non-structural):** `artifacts/concern-map.yaml` defines 5 concerns; the plan decomposes into 3 implementation phases by file/seam boundary. Each phase's Concern column enumerates ALL concern-map concerns it addresses, with the SC mapping shown inline. No concern is shared between phases; the mapping is a strict partition of the 5 concerns:

- Phase 1 = `calibration` (SC-1) + `recall-regression` (SC-8, SC-8a)
- Phase 2 = `seam-default` (SC-2..SC-4) + `floor-empty` (SC-5..SC-7)
- Phase 3 = `ui-default` (SC-9, SC-10)
- Phase 4 = `e2e-auth-bypass` (SC-11, SC-11a)

Both concerns in a phase co-locate because they target the same seam boundary and commit atomically per the per-item TDD cycle (e.g., `recall-regression` SC-8/SC-8a assertions are measured-evidence regression items executed alongside the calibration battery against the same corpus pin; `floor-empty` SC-5..SC-7 is the outcome-rendering half of the same `search_semantic()` seam change as `seam-default`). Phase 4's `e2e-auth-bypass` concern targets a distinct boundary — the app's auth path and E2E test harness — and is separated from Phase 3's UI-default concern accordingly (SC-11 revision, 2026-10-02).

---

## Phase Details

### Phase 1 — Real-data calibration of the semantic-seam default floor

| Field | Value |
|-------|-------|
| Skill | `test-driven-development`, `verification-before-completion` |
| Task | red, green, post-regression, verify, commit |
| Target | calibration evidence artifact + module-level calibration constant in `src/services/semantic_search_service.py` |
| SCs | SC-1, SC-8, SC-8a |
| Depends On | — |

**Context:**

- Corpus: production replica, 6,681 embedded glosses, pin `thenlper/gte-small`, synced 2026-10-02
- Measured distributions (verification probe `tmp/1400/artifacts/verification-probe.yaml`, 2026-10-02): floor-clearing in-corpus anchors water 1.0000, beaver 0.9753, money 0.9970, gun 0.9959, book 0.9936 (all rank 1); in-corpus anchor "how many" 0.8917 (below any floor that clears the OOC max); out-of-corpus battery max "light bulb" 0.9018, battery range 0.8471–0.9018; out-of-corpus bulk p50 0.75–0.77 (earlier probe)
- Floor constraint: float strictly in (0.9018, 0.9753); "how many" documented as below-floor empty outcome (SC-5), not a recall regression
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
- Auth state: E2E authentication handled by the Phase 4 test-only bypass (SC-11); one-time OAuth login procedure per ui_testing_standard remains documented for manual/interactive sessions only

---

## Phase 4 — E2E auth bypass — test-only SNEA_E2E-gated authentication

> See `plan-04-e2e-auth-bypass.md`.

---

## Pre-Implementation (once per plan)

- [ ] 1. **Coherence gate (**direct**).** Read the ledger at `.issues/1400/artifacts/plan-input-verification.md`; confirm every SC (SC-1..SC-11 incl. SC-8a and SC-11a) maps to exactly one phase and one plan item, the phase DAG is linear and acyclic (1 → 2 → 3 → 4), and each phase's red/green/post-regression/verify/commit skill+task selection matches the implementation-workflow reference card. **→ all SCs**
- [ ] 2. **Baseline check (**direct**).** Verify production replica is freshly synced (`bash scripts/sync_prod_to_local.sh`), the feature branch exists, and existing seam/UI tests (`test/test_semantic_threshold_red.py` and siblings listed in the blast radius) pass before the first RED. Record the measured pre-calibration baseline (floor-clearing in-corpus anchors water 1.0000 / beaver 0.9753 / money 0.9970 / gun 0.9959 / book 0.9936 at rank 1; anchor "how many" 0.8917 documented below floor per SC-8a) for SC-8/SC-8a comparison. **→ all SCs**

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

- [ ] 75. **Audit (**task-card**).** Dispatch `task(..., prompt: "execute verification-audit DiMo investigator from audit. Read \`audit/tasks/verification-audit-investigator.md\` first")`, then validator, evaluator, arbiter in sequence. **→ all SCs**
- [ ] 76. **Z3 check (**direct**).** Run `.opencode/tools/solve check --state-path {project_root}/tmp/1400/state.yaml --contract-path {project_root}/tmp/1400/constraints.yaml` directly. **→ pipeline dependency integrity**
- [ ] 77. **Structural checks (**task-card**).** `task(..., prompt: "execute checklist task from finishing-a-development-branch")` — lint, typecheck, finishing checklist. **→ all SCs (code hygiene)**
- [ ] 78. **Pre-PR gate (**task-card**).** `task(..., prompt: "execute verify task from verification-before-completion")` — read all SC verdicts; BLOCK if any FAIL (DONE_WITH_CONCERNS coerces to FAIL). **→ all SCs**
- [ ] 79. **Regression check (**task-card**).** `task(..., prompt: "execute phase-4 task from test-driven-development")` — final regression batch before PR. **→ all SCs (non-regression)**
- [ ] 80. **Review prep (**task-card**).** `task(..., prompt: "execute review-prep from git-workflow-pr. Read \`git-workflow-pr/tasks/review-prep.md\` first")`. **→ review readiness**
- [ ] 81. **Create PR (**task-card**).** `task(..., prompt: "execute create task from git-workflow-pr")` — stacked PR targeting the trunk; squash to one commit for the issue at PR creation. PR creation then HALT for human review — agents never merge. **→ pr_created**
- [ ] 82. **Executive summary (**task-card**).** `task(..., prompt: "execute completion task from completion-core")` — completion report with SC verdict table and byline. **→ completion**

---

## Exit Criteria

- [ ] C1. Calibration evidence artifact exists with per-anchor floor values and full source provenance (query battery, corpus pin, date) for in-corpus and out-of-corpus batteries; no synthetic queries. **→ SC-1**
- [ ] C2. Published calibrated default floor is a named constant strictly between 0.9018 and 0.9753, carrying provenance. **→ SC-1, SC-2**
- [ ] C3. `search_semantic(threshold=None)` filters on the calibrated floor; explicit values override; `None` after an override re-engages the default. **→ SC-2, SC-3, SC-4**
- [ ] C4. All-below-floor outcome returns `status=ok`, empty `results`, deficiency message — no exception (SC-5, SC-6); per-row filtering: below-floor rows excluded from `results` whenever a threshold is active, verified via the mixed above/below-floor distribution under an explicit threshold (SC-7). **→ SC-5, SC-6, SC-7**
- [ ] C5. Default threshold: floor-clearing in-corpus battery anchors (water / beaver / money / gun / book) rank at rank 1 with cosine ≥ published floor. **→ SC-8**
- [ ] C5a. Anchor "how many" (0.8917) returns the below-floor empty outcome per SC-5 semantics (documented overlap behavior, not recall regression). **→ SC-8a**
- [ ] C6. Fresh-session `st.session_state.semantic_threshold` equals the published floor within ±0.01; UI overrides reach the seam unchanged. **→ SC-9, SC-10**
- [ ] C7. All pytest suites pass; Playwright SC-9/SC-10 evidence captured per ui_testing_standard (skips reported as skipped, never as PASS). **→ SC-8, SC-8a, SC-9, SC-10, non-regression**
- [ ] C8. E2E Playwright suite authenticates headlessly via the pinned `SNEA_E2E`-gated test-only auth bypass hook in `src/services/security_manager.py` with no headed OAuth login and no fabricated credentials. **→ SC-11**
- [ ] C8a. Bypass verified inert by pytest: with `SNEA_E2E` unset, the auth path in `src/services/security_manager.py` behaves identically to production. **→ SC-11a**
- [ ] C9. Stacked PR created; all post-implementation gates (audit, Z3, structural checks, pre-PR gate, regression check) PASS. **→ pipeline completion**

---

## Pre-Flight Guard (Mandatory)

Check your tool list for a tool named `task`.

- Present ⇒ orchestrator — proceed.
- Absent ⇒ sub-agent — do NOT execute any instruction below. Return `BLOCKED` with `ORCHESTRATOR_ONLY_SKILL_CARD` (cards) or `ORCHESTRATOR_ONLY_PLAN` (plans) and halt.

---

## lifecycle_events

- 2026-10-02T16:13:51Z — plan_created — plan verified at `.issues/1400/plan.md`; 3 phases + pre-implementation (2 steps) + post-implementation (8 steps); dispatch: phase-1/2/3 task-card via test-driven-development + verification-before-completion with orchestrator commit-inline; dependency contract present at `.issues/1400/dependency-contract.yaml`.
- 2026-10-02T17:10:00Z — plan_revised — regenerated against revised spec (structure/decomposition revision: compound SC-8 split into atomic SC-8 (floor-clearing anchors rank 1 + cosine ≥ published floor) and SC-8a ("how many" below-floor empty outcome with pinned SC-5 message); SC-5 deficiency message pinned to "No gloss results meet the sensitivity floor."; SC count 10 → 11). Plan updated: Phase 1 SCs SC-1/SC-8/SC-8a with new Item 3 (SC-8a, steps 13-17); Phase 2 items/steps renumbered (18-47); Phase 3 renumbered (48-57); post-implementation renumbered (58-65); exit criteria C5 split into C5/C5a; phase plan files updated.
- 2026-10-02T16:40:31Z — plan_revised — regenerated against revised spec (measured-reality recalibration: floor interval (0.9018, 0.9753), in-corpus anchors incl. "how many" 0.8917 below-floor, OOC max "light bulb" 0.9018; probe `tmp/1400/artifacts/verification-probe.yaml`); Architecture, Phase 1 context, step 2 baseline, C2, C5 updated to match revised SC-8; phase plan files and dependency contract updated.
- 2026-10-02T17:30:00Z — plan_revised — validate-findings F-1/F-2 (Cat 4 concern-separation FAIL) remediated via non-structural option (a): Phase Table Concern column and concern-alignment note updated to enumerate all concern-map concerns per phase (Phase 1 = calibration + recall-regression; Phase 2 = seam-default + floor-empty; Phase 3 = ui-default), strict partition of the 5 concern-map concerns, no concern shared between phases. SC coverage (11 SCs), linear DAG (1→2→3), and per-item TDD cycles unchanged; concern-map.yaml annotated with a phase-mapping note; dependency-contract.yaml unchanged.
- 2026-10-02T19:20:00Z — plan_revised — regenerated against revised spec (developer directive 2026-10-02: SC-11 added — test-only SNEA_E2E-gated auth bypass so Playwright E2E tests authenticate without headed OAuth login or fabricated credentials, bypass inert outside SNEA_E2E=1). Plan updated: phase_count 3→4; new Phase 4 (e2e-auth-bypass, SC-11, steps 66-72, plan-04-e2e-auth-bypass.md); Phase Table DAG 1→2→3→4; concern alignment adds e2e-auth-bypass partition; post-implementation renumbered 58-65 → 73-80; exit criteria C8 (SC-11) added; pre-implementation coherence gate updated to SC-1..SC-11 and DAG 1→2→3→4; dependency contract updated (phase4_complete, new precondition/invariant edges, e2e_auth_bypass contract entry). No existing phase or SC removed or weakened.
- 2026-10-02T19:55:00Z — plan_revised — regenerated against revised spec (validation findings: SC-11 pinned to EXACTLY ONE mechanism — `SNEA_E2E`-gated test-only auth bypass hook in `src/services/security_manager.py` auth resolution, cookie/context-injection alternative removed; compound SC-11 split into SC-11 + SC-11a). Plan updated: Architecture Phase 4 wording pinned to the bypass hook with SC-11a added; Files entry pinned to `src/services/security_manager.py`; Phase Table Phase 4 SCs SC-11, SC-11a, step range 66-74; concern alignment Phase 4 = e2e-auth-bypass (SC-11, SC-11a); coherence gate SC list updated; plan-04 item 13 (SC-11a, steps 71-74) added; post-implementation renumbered 73-80 → 75-82; exit criteria C8 split into C8 (SC-11) / C8a (SC-11a); dependency-contract.yaml e2e_auth_bypass target pinned to the security_manager.py hook and phase4_complete description extended to SC-11a. No existing phase or SC removed or weakened.
- 2026-10-02T19:19:26Z — plan_created — plan verified at `.issues/1400/plan.md` (post-revision completion check); 4 phases + pre-implementation (2 steps) + post-implementation (8 steps); dependency contract present at `.issues/1400/dependency-contract.yaml`.
