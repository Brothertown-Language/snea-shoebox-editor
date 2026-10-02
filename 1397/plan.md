---
plan_schema_version: 1
issue: 1397
title: "Required-secrets manifest, preflight verification, guard coupling, and outage remediation runbook"
authorization_scope: for_pr
pr_strategy: stacked
phase_count: 4
dispatch:
  - test-driven-development (phases 1-4: red, green, post-regression)
  - verification-before-completion (phases 1-4 verify; pre-pr-gate)
  - finishing-a-development-branch (structural-checks)
  - audit (post-implementation adversarial audit)
  - git-workflow-pr (review-prep, create-pr)
  - completion-core (exec-summary)
---

# Implementation Plan — Issue #1397

- **Issue:** .issues/1397/spec.md

## Goal

Restore and prevent recurrence of the production outage caused by the fail-fast `contact.maintainer_label` guard crashing the deployed Streamlit app. Introduce a required-secrets manifest as the single machine-readable source of truth, a preflight verification that compares a deploy target's secrets store against the manifest (naming missing key PATHS only, never values), tie the fail-fast guard to the same manifest so guard and preflight cannot diverge, and document the developer-only remediation for the current Streamlit Cloud outage.

## Architecture

- New required-secrets manifest (YAML list of dotted key paths) under `.streamlit/`.
- New preflight module: takes a store mapping + manifest paths, returns a structured missing-path report.
- `streamlit_app.py` fail-fast guard refactored to consume the manifest (single source; no duplicated key list).
- Remediation runbook documenting the developer-only Streamlit Cloud secrets-store action.

## Files

- `streamlit_app.py` — guard refactor + preflight integration (existing)
- `.streamlit/secrets.toml`, `.streamlit/secrets.toml.production` — reference stores and production template (existing)
- `.streamlit/required_secrets.yaml` — new manifest
- preflight module (new) — location finalized during GREEN within phase-2 scope
- remediation runbook (new, under `docs/`)
- `test/` — new RED tests per SC

## Dispatch

- Phases 1-4: RED/GREEN/post-regression via `test-driven-development`, verify via `verification-before-completion`, commit-inline by orchestrator.
- Post-implementation: audit, z3-check, structural-checks, pre-pr-gate, regression-check, review-prep, create-pr, exec-summary.

## Blast Radius

- `streamlit_app.py` guard (startup path) — behavior preserved (RuntimeError naming missing key); key list source changes.
- `src/services/infrastructure_service.py` and `src/aiven_utils.py` — reuse/supersede existing presence-check helpers; duplicated logic must not diverge.
- `src/services/identity_service.py`, `src/database/connection.py`, `src/logging_config.py`, `src/frontend/pages/login.py`, `src/frontend/ui_utils.py` — st.secrets access sites inventoried in phase-1 manifest completeness.
- `.streamlit/secrets.toml.production` — must mirror manifest additions.
- No production data files touched. Streamlit Cloud store is external (developer action, phase-4 runbook).

## Admonishment

> **Compliance:** All SCs must pass before completion. Partial implementation is not permitted. Each item is daisy-chained — item N's commit is precondition for item N+1's RED.

> **One step at a time.** Execute exactly one step. Report progress. Wait for instruction before the next step.

> **Step status:** Report `[item N] [PASS|FAIL]` after each step. If FAIL, report blocker and halt.

> **Self-Remediation Protocol:** If a step FAILs: diagnose root cause, fix the deliverable, re-verify. If the fix requires spec revision, update the spec and re-enter the plan. Escalate only after remediation failure.

> **Enforcement gate:** All SCs must pass before this plan is complete.

## Pre-Flight Guard (Mandatory)

Check your tool list for a tool named `task`.

- Present ⇒ orchestrator — proceed.
- Absent ⇒ sub-agent — do NOT execute any instruction below. Return `BLOCKED` with `ORCHESTRATOR_ONLY_SKILL_CARD` (cards) or `ORCHESTRATOR_ONLY_PLAN` (plans) and halt.

## Phase Table

| Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch |
|-------|------|---------|-----|------------|------------|----------|
| 1 | Required-secrets manifest definition | required-secrets manifest | SC-1 | — | 5-9 | direct (5) + task-card (6-9) |
| 2 | Preflight verification implementation (incl. secret-value-safety) | preflight verification | SC-2, SC-5 | 1 | 10-19 | task-card (10-18) + direct (19) |
| 3 | Fail-fast guard / manifest coupling | guard-manifest coupling | SC-3 | 1, 2 | 20-24 | task-card (20-23) + direct (24) |
| 4 | Outage remediation runbook (developer action) | production remediation | SC-4 | 2 | 25-29 | task-card (25-28) + direct (29) |
| — | Post-implementation | pipeline gates | all | 1-4 | 30-37 | direct (31) + task-card (30, 32-37) |

## Pre-Implementation

- [ ] 1. Coherence gate (**direct**)
  - Re-read `.issues/1397/spec.md` and `.issues/1397/artifacts/structure.yaml`; confirm SC list, phase DAG edges (1→2, 1→3, 2→3, 2→4), and triplet colocation are consistent.
  - Confirm all 5 SCs map to exactly one phase and no phase covers an SC not assigned to it.
  - SC reference: all (gate covers whole plan).
- [ ] 2. Baseline check (**direct**)
  - Run the existing test suite (`uv run pytest test/`) and record the passing baseline; confirm clean working tree on the feature branch.
  - SC reference: all (baseline for all phases).
- [ ] 3. Pre-regression (**task-card**)
  - `task(..., prompt: "execute phase-0 task from test-driven-development")`
  - Pre-clean `tmp/1397/artifacts/pipeline-pre-regression-*`.
  - Run regression test patterns before RED phase; SC reference: all.
- [ ] 4. Pre-regression verify (**task-card**)
  - `task(..., prompt: "execute verify task from verification-before-completion")`
  - Pre-clean `tmp/1397/artifacts/pipeline-pre-regression-verify-*`.
  - Verify pre-regression results; SC reference: all.

## Phase 1 — Required-secrets manifest definition

- **Concern:** machine-checkable required-secrets inventory
- **Files:** `.streamlit/required_secrets.yaml` (new); st.secrets access sites inventoried: `streamlit_app.py` fail-fast guard, `src/services/infrastructure_service.py`, `src/aiven_utils.py`, `src/services/identity_service.py`, `src/database/connection.py`, `src/logging_config.py`, `src/frontend/pages/login.py`, `src/frontend/ui_utils.py`; local reference store `.streamlit/secrets.toml`
- **SCs:** SC-1
- **Depends On:** none
- **Entry condition:** clean baseline from pre-implementation steps; branch checked out
- **Exit condition:** manifest committed; RED test passes after GREEN

### Code Path Coverage

- Fail-fast guard `st.secrets['contact']['maintainer_label']` access in `streamlit_app.py` startup path.
- All st.secrets access sites listed in the code-path inventory artifact are enumerated to build the manifest key list.

### Cross-Cutting SCs

- SC-5 (value-safety): the manifest holds dotted key PATHS only — never value pairs. Asserted in this phase's RED test.

### Interface Boundaries

- Manifest file ↔ consumers (guard, preflight): manifest is a list of dotted key paths (str), parseable without reading secret values.

### State Transitions

- From: key requirements implicit in scattered code access sites. To: single machine-readable manifest that phase-2 preflight and phase-3 guard both consume.

### Steps

- [ ] 5. RED for SC-1 (**task-card**)
  - `task(..., prompt: "execute red task from test-driven-development")`
  - Pre-clean `tmp/1397/artifacts/pipeline-red-*`.
  - RED: failing test asserting the required-secrets manifest exists at `.streamlit/required_secrets.yaml` and covers every `st.secrets` key path accessed in code (including `contact.maintainer_label`, `contact.mastodon_url`), with the manifest containing paths only and no values.
- [ ] 6. GREEN for SC-1 (**task-card**)
  - `task(..., prompt: "execute green task from test-driven-development")`
  - GREEN: the manifest file exists listing every required dotted key path; the RED test passes. Minimum change only.
- [ ] 7. Post-regression for SC-1 (**task-card**)
  - `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - Pre-clean `tmp/1397/artifacts/pipeline-post-regression-*`.
  - Run regression test patterns after GREEN; SC reference: SC-1.
- [ ] 8. Verify SC-1 (**task-card**)
  - `task(..., prompt: "execute verify task from verification-before-completion")`
  - Pre-clean `tmp/1397/artifacts/pipeline-verify-*`.
  - Verify implementation against SC-1; behavioral evidence per declared evidence type.
- [ ] 9. Commit SC-1 (**direct**)
  - `git add <manifest file and test files> && git commit -m "test(secrets): required-secrets manifest as single source of truth (SC-1)"` — exact paths resolved at execution time; no co-author trailers during implementation commits.

**Cost frame:** Verifying manifest completeness against all st.secrets access sites costs a grep-enumeration pass plus the RED test run — minutes. Skipping means a required key missing from the manifest is invisible until preflight (phase-2) trusts it and production crashes again — the exact defect this plan exists to close.

### Phase 1 Completion

- Verify: SC-1 verdict PASS with behavioral evidence; commit contains test + manifest atomically.

### Concern Transition

- Manifest is now the single source of truth → phase-2 preflight consumes it.

## Phase 2 — Preflight verification implementation (incl. secret-value-safety)

- **Concern:** preflight verification of deployed secrets store
- **Files:** new preflight module (location finalized in GREEN; reuse candidate: presence-check helpers in `src/services/infrastructure_service.py`); new tests under `test/`
- **SCs:** SC-2, SC-5
- **Depends On:** phase 1
- **Entry condition:** phase-1 manifest committed
- **Exit condition:** preflight check and value-safety guarantees committed and verified

### Code Path Coverage

- Preflight module: takes a store mapping (nested dict, e.g. parsed secrets structure) plus the manifest's dotted key paths; returns a missing-path list.
- Startup integration point near the fail-fast guard in `streamlit_app.py`; optional CI/deploy step in `.github/workflows/` if chosen during GREEN per spec latitude.

### Cross-Cutting SCs

- SC-5 is co-located here as the cross-cutting value-safety constraint on all preflight output and logging.

### Interface Boundaries

- Preflight ↔ guard: both read the same manifest; preflight returns a structured dict of missing key paths, no values.
- Preflight ↔ existing secrets-audit helpers (`src/services/infrastructure_service.py` presence checks; duplicated logic in `src/aiven_utils.py` must not diverge).

### State Transitions

- From: app startup with partial/missing secrets store crashes opaquely. To: structured preflight report naming missing key paths before the guard raises.

### Steps

- [ ] 10. RED for SC-2 (**task-card**)
  - `task(..., prompt: "execute red task from test-driven-development")`
  - Pre-clean `tmp/1397/artifacts/pipeline-red-*`.
  - RED: failing test calling the preflight check with a store mapping missing one manifest key; test asserts a structured report naming the missing key PATH only.
- [ ] 11. GREEN for SC-2 (**task-card**)
  - `task(..., prompt: "execute green task from test-driven-development")`
  - GREEN: preflight check implemented — compares store mapping against manifest paths, returns structured report (missing key paths only); runs at startup preflight and/or CI/deploy per spec latitude. RED test passes.
- [ ] 12. Post-regression for SC-2 (**task-card**)
  - `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - Pre-clean `tmp/1397/artifacts/pipeline-post-regression-*`.
  - SC reference: SC-2.
- [ ] 13. Verify SC-2 (**task-card**)
  - `task(..., prompt: "execute verify task from verification-before-completion")`
  - Pre-clean `tmp/1397/artifacts/pipeline-verify-*`.
  - SC reference: SC-2.
- [ ] 14. Commit SC-2 (**direct**)
  - `git add <preflight module and test files> && git commit -m "feat(secrets): preflight verification against required-secrets manifest (SC-2)"`
- [ ] 15. RED for SC-5 (**task-card**)
  - `task(..., prompt: "execute red task from test-driven-development")`
  - Pre-clean `tmp/1397/artifacts/pipeline-red-*`.
  - RED: failing test asserting preflight output and logs contain no secret VALUES — key presence comparison only (e.g. feed a store mapping with dummy values; assert no value appears in report or captured logs).
- [ ] 16. GREEN for SC-5 (**task-card**)
  - `task(..., prompt: "execute green task from test-driven-development")`
  - GREEN: value-redaction guarantees enforced in preflight report and logging; RED test passes.
- [ ] 17. Post-regression for SC-5 (**task-card**)
  - `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - SC reference: SC-5.
- [ ] 18. Verify SC-5 (**task-card**)
  - `task(..., prompt: "execute verify task from verification-before-completion")`
  - SC reference: SC-5.
- [ ] 19. Commit SC-5 (**direct**)
  - `git add <redaction changes and test files> && git commit -m "feat(secrets): value-safety guarantees in preflight report and logging (SC-5)"`

**Cost frame:** Running the preflight RED tests costs minutes of execution time. Skipping means a missing-key path is not reported before the crash, or a secret VALUE leaks into logs — the latter is a security defect that ships silently and costs 1000× more to remediate after exposure.

### Phase 2 Completion

- Verify: SC-2 and SC-5 verdicts PASS with behavioral evidence; commits atomic per item.

### Concern Transition

- Preflight and manifest in place → phase-3 couples the fail-fast guard to the same manifest so they cannot diverge silently.

## Phase 3 — Fail-fast guard / manifest coupling

- **Concern:** guard-manifest single-source coupling
- **Files:** `streamlit_app.py` (fail-fast guard, startup path); new divergence-prevention test under `test/`
- **SCs:** SC-3
- **Depends On:** phases 1, 2
- **Entry condition:** manifest (phase 1) and preflight (phase 2) committed
- **Exit condition:** guard consumes the manifest; divergence test passes

### Code Path Coverage

- `streamlit_app.py` fail-fast guard refactored to read `.streamlit/required_secrets.yaml` instead of a hardcoded key list; existing RuntimeError-with-actionable-message behavior (missing key named) preserved unchanged.

### Cross-Cutting SCs

- SC-3 itself is the cross-cutting coupling constraint recorded in the cross-cutting matrix (manifest ↔ preflight ↔ guard).

### Interface Boundaries

- Guard ↔ preflight/manifest loader: same required-key list source; adding a required secret is one manifest edit and both behaviors update automatically.

### State Transitions

- From: guard key list hardcoded (can silently diverge from manifest). To: guard keys == manifest keys, asserted by test.

### Steps

- [ ] 20. RED for SC-3 (**task-card**)
  - `task(..., prompt: "execute red task from test-driven-development")`
  - Pre-clean `tmp/1397/artifacts/pipeline-red-*`.
  - RED: failing test asserting the guard's required-key list is sourced from the manifest — a test adding a key to the manifest must change guard behavior, with no duplicated hardcoded list.
- [ ] 21. GREEN for SC-3 (**task-card**)
  - `task(..., prompt: "execute green task from test-driven-development")`
  - GREEN: guard refactored to consume the manifest; divergence-prevention test passes; existing guard RuntimeError behavior unchanged.
- [ ] 22. Post-regression for SC-3 (**task-card**)
  - `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - SC reference: SC-3.
- [ ] 23. Verify SC-3 (**task-card**)
  - `task(..., prompt: "execute verify task from verification-before-completion")`
  - SC reference: SC-3.
- [ ] 24. Commit SC-3 (**direct**)
  - `git add <guard refactor and test files> && git commit -m "refactor(app): fail-fast guard consumes required-secrets manifest (SC-3)"`

**Cost frame:** Verifying guard/manifest coupling costs one behavioral test run — minutes. Skipping means a stale manifest masks future missing keys (the spec's second risk) and the divergence is found only by the next production crash.

### Phase 3 Completion

- Verify: SC-3 verdict PASS; guard behavior regression-free.

### Concern Transition

- Guard and preflight now share one source of truth → phase-4 documents the developer-only remediation of the live outage.

## Phase 4 — Outage remediation runbook (developer action)

- **Concern:** production remediation documentation
- **Files:** new remediation runbook under `docs/`; test/assertion under `test/` (structural RED)
- **SCs:** SC-4
- **Depends On:** phase 2 (runbook documents preflight verification as the post-remediation confirmation step)
- **Entry condition:** phases 1-3 committed
- **Exit condition:** runbook committed; developer action item documented (agent cannot reach the Streamlit Cloud store)

### Code Path Coverage

- Streamlit Cloud secrets store is external and not in the codebase — documented instructions only.
- `.streamlit/secrets.toml.production` template updated to include `contact.maintainer_label` so the template mirrors the manifest.

### Cross-Cutting SCs

- None beyond SC-5 (runbook names key PATHS only, never values).

### Interface Boundaries

- Manifest ↔ Cloud store: the runbook maps each missing manifest key to the exact Cloud-store action required.

### State Transitions

- From: Cloud store lacking `contact.maintainer_label` (production DOWN). To: Cloud store contains the key; production renders; preflight confirms post-remediation.

### Steps

- [ ] 25. RED for SC-4 (**task-card**)
  - `task(..., prompt: "execute red task from test-driven-development")`
  - Pre-clean `tmp/1397/artifacts/pipeline-red-*`.
  - RED: failing assertion that the runbook document exists and names the exact Cloud-store key to add (`contact.maintainer_label`) and the preflight verification step.
- [ ] 26. GREEN for SC-4 (**task-card**)
  - `task(..., prompt: "execute green task from test-driven-development")`
  - GREEN: runbook written documenting the developer-only Cloud-store action (add `contact.maintainer_label`), plus preflight as the post-remediation confirmation step; RED assertion passes.
- [ ] 27. Post-regression for SC-4 (**task-card**)
  - `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - SC reference: SC-4.
- [ ] 28. Verify SC-4 (**task-card**)
  - `task(..., prompt: "execute verify task from verification-before-completion")`
  - SC reference: SC-4.
- [ ] 29. Commit SC-4 (**direct**)
  - `git add <runbook, template, test files> && git commit -m "docs(secrets): outage remediation runbook for Cloud-store maintainer_label (SC-4)"`

**Cost frame:** Verifying the runbook names the exact key and confirmation step costs one assertion run. Skipping means the developer remediates from memory and the next outage has no documented procedure — the runbook is the only durable record of the human-only action.

### Phase 4 Completion

- Verify: SC-4 verdict PASS; runbook committed with template mirror update.

### Concern Transition

- All SCs implemented → post-implementation pipeline gates.

## Post-Implementation

- [ ] 30. Adversarial audit (**task-card**)
  - `task(..., prompt: "execute verification-audit DiMo investigator from audit. Read \`audit/tasks/verification-audit-investigator.md\` first")` — followed by validator, evaluator, arbiter in sequence
  - Pre-clean `tmp/1397/artifacts/pipeline-audit-*`.
  - SC reference: all.
- [ ] 31. Z3 constraint check (**direct**)
  - `.opencode/tools/solve check --state-path <state file> --contract-path <contract file>` — paths resolved at execution time from `tmp/1397/` constraints artifacts.
  - Pre-clean `tmp/1397/artifacts/pipeline-z3-check-*`.
  - SC reference: all.
- [ ] 32. Structural checks (**task-card**)
  - `task(..., prompt: "execute checklist task from finishing-a-development-branch")`
  - Pre-clean `tmp/1397/artifacts/pipeline-structural-checks-*`.
  - Finishing checklist: lint, typecheck, format checks on modified files; SC reference: all.
- [ ] 33. Pre-PR gate (**task-card**)
  - `task(..., prompt: "execute verify task from verification-before-completion")`
  - Pre-clean `tmp/1397/artifacts/pipeline-pre-pr-gate-*`.
  - Reads all SC verdicts; BLOCKs if any FAIL. DONE_WITH_CONCERNS coerces to FAIL. SC reference: all.
- [ ] 34. Final regression check (**task-card**)
  - `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - Pre-clean `tmp/1397/artifacts/pipeline-regression-check-*`.
  - SC reference: all.
- [ ] 35. Review prep (**task-card**)
  - `task(..., prompt: "execute review-prep from git-workflow-pr. Read \`git-workflow-pr/tasks/review-prep.md\` first")`
  - SC reference: all.
- [ ] 36. Create PR (**task-card**)
  - `task(..., prompt: "execute create task from git-workflow-pr")`
  - Stacked strategy — one branch, squashed commits, one PR targeting the trunk. Do not merge (human-only merge).
  - SC reference: all.
- [ ] 37. Completion summary (**task-card**)
  - `task(..., prompt: "execute completion task from completion-core")`
  - Generate completion executive summary.
  - SC reference: all.

**Post-implementation cost frame:** Running the full post-implementation gate chain costs a bounded sequence of dispatches. Skipping any gate means an SC verdict failure, evidence-type mismatch, or audit finding surfaces after PR creation — rework costs more roundtrips than every gate combined. Correctness is the only metric.

## Exit Criteria

- C1: Manifest exists as single source of truth covering every required `st.secrets` key path (SC-1 PASS).
- C2: Preflight verification produces a structured report naming missing key PATHS only, run before the app can crash (SC-2 PASS).
- C3: Fail-fast guard consumes the manifest; divergence-prevention test passes (SC-3 PASS).
- C4: Remediation runbook exists naming the exact Cloud-store key and the preflight confirmation step (SC-4 PASS).
- C5: No secret VALUES are logged or exposed anywhere in preflight output (SC-5 PASS).
- C6: Audit, z3-check, structural checks, pre-PR gate, and final regression check all PASS.
- C7: PR created (stacked strategy); completion summary emitted.

## lifecycle_events

- event: plan_created
  timestamp: "2026-10-01T23:15:00-04:00"
  plan_path: ".issues/1397/plan.md"
  phase_count: 4
