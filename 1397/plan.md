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

Restore and prevent recurrence of the production outage caused by the fail-fast `contact.maintainer_label` guard crashing the deployed Streamlit app. Introduce a required-secrets manifest as the single machine-readable source of truth, a preflight verification that compares a deploy target's secrets store against the manifest (naming missing key PATHS only, never values), replace the fail-fast crash for contact keys with a manifest-coupled default-fallback resolution path (per spec Revision 1: missing contact key → static default `contact.mastodon_url` rendered as the contact, one-time non-blocking operator warning naming the missing key PATH, startup continues — NO RuntimeError), and document the developer-only remediation for the current Streamlit Cloud outage.

## Architecture

- New required-secrets manifest (YAML list of dotted key paths) under `.streamlit/`.
- New preflight module: takes a store mapping + manifest paths, returns a structured missing-path report.
- `streamlit_app.py` guard refactored to consume the manifest (single source; no duplicated key list) and REPLACED by a default-fallback resolution path for contact keys (spec Revision 1): missing contact key → static default (`contact.mastodon_url` rendered as the contact), one-time non-blocking operator warning naming the missing key PATH only, startup continues. The manifest still declares required keys; preflight still reports drift to operators; startup never crashes on a missing contact key.
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

- `streamlit_app.py` guard (startup path) — behavior CHANGES per spec Revision 1: the RuntimeError crash on a missing contact key is replaced by default-fallback resolution (static default + one-time warning naming the missing key PATH); key list source changes to the manifest.
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
| 3 | Guard/manifest coupling + default-fallback resolution (Revision 1) | guard-manifest coupling + default-fallback | SC-3, SC-6 | 1, 2 | 20-29 | task-card (20-28) + direct (29) |
| 4 | Outage remediation runbook (developer action) | production remediation | SC-4 | 2 | 30-34 | task-card (30-33) + direct (34) |
| — | Post-implementation | pipeline gates | all | 1-4 | 35-42 | direct (36) + task-card (35, 37-42) |

## Pre-Implementation

- [ ] 1. Coherence gate (**direct**)
  - Re-read `.issues/1397/spec.md` and `.issues/1397/artifacts/structure.yaml`; confirm SC list, phase DAG edges (1→2, 1→3, 2→3, 2→4), and triplet colocation are consistent.
  - Confirm all 6 SCs map to exactly one phase and no phase covers an SC not assigned to it.
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

- From: app startup with partial/missing secrets store crashes opaquely. To: structured preflight report naming missing key paths before startup fallback resolution.

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

- Preflight and manifest in place → phase-3 couples the guard to the same manifest and replaces the missing-contact-key crash with default-fallback resolution (spec Revision 1).

## Phase 3 — Guard/manifest coupling + default-fallback resolution (Revision 1)

- **Concern:** guard-manifest single-source coupling + default-fallback for missing contact keys
- **Files:** `streamlit_app.py` (fail-fast guard, startup path); new divergence-prevention and fallback tests under `test/`
- **SCs:** SC-3, SC-6
- **Depends On:** phases 1, 2
- **Entry condition:** manifest (phase 1) and preflight (phase 2) committed
- **Exit condition:** guard consumes the manifest; missing contact keys fall back to a static default with a one-time warning; no RuntimeError raised; divergence test passes

### Code Path Coverage

- `streamlit_app.py` guard refactored to read `.streamlit/required_secrets.yaml` instead of a hardcoded key list.
- Per spec Revision 1, the RuntimeError guard for contact keys is REPLACED by the default-fallback resolution path: a missing `contact.maintainer_label` (or any manifest-required contact key) falls back to the static default (render `contact.mastodon_url` as the contact when no label configured), logs a ONE-TIME non-blocking operator warning naming the missing key PATH only (value-safety applies — no values in the warning), and startup continues. The crash path is removed; the manifest still declares required keys and preflight still reports drift to operators.

### Cross-Cutting SCs

- SC-3 is the cross-cutting coupling constraint recorded in the cross-cutting matrix (manifest ↔ preflight ↔ guard/fallback).
- SC-5 (value-safety) applies to the SC-6 warning output: the warning names the missing key PATH only, never a value.

### Interface Boundaries

- Guard/fallback ↔ preflight/manifest loader: same required-key list source; adding a required secret is one manifest edit and both behaviors update automatically.
- Fallback ↔ contact rendering: `contact.maintainer_label` missing → render `contact.mastodon_url` as the contact (static default), never crash.

### State Transitions

- From: guard key list hardcoded (can silently diverge from manifest) and a missing contact key crashes startup with RuntimeError. To: guard keys == manifest keys (asserted by test) and a missing contact key resolves via the manifest-declared default with a one-time warning; startup never crashes on a missing contact key.

### Steps

- [ ] 20. RED for SC-3 (**task-card**)
  - `task(..., prompt: "execute red task from test-driven-development")`
  - Pre-clean `tmp/1397/artifacts/pipeline-red-*`.
  - RED: failing test asserting the guard's required-key list is sourced from the manifest — a test adding a key to the manifest must change guard/preflight behavior, with no duplicated hardcoded list.
- [ ] 21. GREEN for SC-3 (**task-card**)
  - `task(..., prompt: "execute green task from test-driven-development")`
  - GREEN: guard refactored to consume the manifest; divergence-prevention test passes.
- [ ] 22. Post-regression for SC-3 (**task-card**)
  - `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - SC reference: SC-3.
- [ ] 23. Verify SC-3 (**task-card**)
  - `task(..., prompt: "execute verify task from verification-before-completion")`
  - SC reference: SC-3.
- [ ] 24. Commit SC-3 (**direct**)
  - `git add <guard refactor and test files> && git commit -m "refactor(app): guard consumes required-secrets manifest (SC-3)"`

**Cost frame:** Verifying guard/manifest coupling plus the fallback behavior costs two behavioral test runs — minutes. Skipping means a stale manifest masks future missing keys (the spec's second risk) and a missing contact key still crashes production (the exact outage this plan exists to close, per Revision 1).

### Phase 3 Completion

- Verify: SC-3 and SC-6 verdicts PASS with behavioral evidence; commits atomic per item; no RuntimeError path remains for missing contact keys.

### Concern Transition

- Guard and preflight now share one source of truth and missing contact keys resolve via fallback → phase-4 documents the developer-only remediation of the live outage.

- [ ] 25. RED for SC-6 (**task-card**)
  - `task(..., prompt: "execute red task from test-driven-development")`
  - Pre-clean `tmp/1397/artifacts/pipeline-red-*`.
  - RED: failing test asserting that a store mapping missing `contact.maintainer_label` does NOT raise RuntimeError — startup continues with the static default (`contact.mastodon_url` rendered as the contact), exactly one non-blocking operator warning naming the missing key PATH (no values) is logged, and the app proceeds to render.
- [ ] 26. GREEN for SC-6 (**task-card**)
  - `task(..., prompt: "execute green task from test-driven-development")`
  - GREEN: the RuntimeError guard for contact keys is replaced by the default-fallback resolution path consuming the manifest; one-time warning logged (path only, value-safe); startup continues on a missing contact key. RED test passes. Minimum change only.
- [ ] 27. Post-regression for SC-6 (**task-card**)
  - `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - Pre-clean `tmp/1397/artifacts/pipeline-post-regression-*`.
  - SC reference: SC-6.
- [ ] 28. Verify SC-6 (**task-card**)
  - `task(..., prompt: "execute verify task from verification-before-completion")`
  - Pre-clean `tmp/1397/artifacts/pipeline-verify-*`.
  - SC reference: SC-6.
- [ ] 29. Commit SC-6 (**direct**)
  - `git add <fallback resolution and test files> && git commit -m "feat(app): default-fallback contact resolution, never crash on missing contact key (SC-6)"`

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

- [ ] 30. RED for SC-4 (**task-card**)
  - `task(..., prompt: "execute red task from test-driven-development")`
  - Pre-clean `tmp/1397/artifacts/pipeline-red-*`.
  - RED: failing assertion that the runbook document exists and names the exact Cloud-store key to add (`contact.maintainer_label`) and the preflight verification step.
- [ ] 31. GREEN for SC-4 (**task-card**)
  - `task(..., prompt: "execute green task from test-driven-development")`
  - GREEN: runbook written documenting the developer-only Cloud-store action (add `contact.maintainer_label`), plus preflight as the post-remediation confirmation step; RED assertion passes.
- [ ] 32. Post-regression for SC-4 (**task-card**)
  - `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - SC reference: SC-4.
- [ ] 33. Verify SC-4 (**task-card**)
  - `task(..., prompt: "execute verify task from verification-before-completion")`
  - SC reference: SC-4.
- [ ] 34. Commit SC-4 (**direct**)
  - `git add <runbook, template, test files> && git commit -m "docs(secrets): outage remediation runbook for Cloud-store maintainer_label (SC-4)"`

**Cost frame:** Verifying the runbook names the exact key and confirmation step costs one assertion run. Skipping means the developer remediates from memory and the next outage has no documented procedure — the runbook is the only durable record of the human-only action.

### Phase 4 Completion

- Verify: SC-4 verdict PASS; runbook committed with template mirror update.

### Concern Transition

- All SCs implemented → post-implementation pipeline gates.

## Post-Implementation

- [ ] 35. Adversarial audit (**task-card**)
  - `task(..., prompt: "execute verification-audit DiMo investigator from audit. Read \`audit/tasks/verification-audit-investigator.md\` first")` — followed by validator, evaluator, arbiter in sequence
  - Pre-clean `tmp/1397/artifacts/pipeline-audit-*`.
  - SC reference: all.
- [ ] 36. Z3 constraint check (**direct**)
  - `.opencode/tools/solve check --state-path <state file> --contract-path <contract file>` — paths resolved at execution time from `tmp/1397/` constraints artifacts.
  - Pre-clean `tmp/1397/artifacts/pipeline-z3-check-*`.
  - SC reference: all.
- [ ] 37. Structural checks (**task-card**)
  - `task(..., prompt: "execute checklist task from finishing-a-development-branch")`
  - Pre-clean `tmp/1397/artifacts/pipeline-structural-checks-*`.
  - Finishing checklist: lint, typecheck, format checks on modified files; SC reference: all.
- [ ] 38. Pre-PR gate (**task-card**)
  - `task(..., prompt: "execute verify task from verification-before-completion")`
  - Pre-clean `tmp/1397/artifacts/pipeline-pre-pr-gate-*`.
  - Reads all SC verdicts; BLOCKs if any FAIL. DONE_WITH_CONCERNS coerces to FAIL. SC reference: all.
- [ ] 39. Final regression check (**task-card**)
  - `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - Pre-clean `tmp/1397/artifacts/pipeline-regression-check-*`.
  - SC reference: all.
- [ ] 40. Review prep (**task-card**)
  - `task(..., prompt: "execute review-prep from git-workflow-pr. Read \`git-workflow-pr/tasks/review-prep.md\` first")`
  - SC reference: all.
- [ ] 41. Create PR (**task-card**)
  - `task(..., prompt: "execute create task from git-workflow-pr")`
  - Stacked strategy — one branch, squashed commits, one PR targeting the trunk. Do not merge (human-only merge).
  - SC reference: all.
- [ ] 42. Completion summary (**task-card**)
  - `task(..., prompt: "execute completion task from completion-core")`
  - Generate completion executive summary.
  - SC reference: all.

**Post-implementation cost frame:** Running the full post-implementation gate chain costs a bounded sequence of dispatches. Skipping any gate means an SC verdict failure, evidence-type mismatch, or audit finding surfaces after PR creation — rework costs more roundtrips than every gate combined. Correctness is the only metric.

## Exit Criteria

- C1: Manifest exists as single source of truth covering every required `st.secrets` key path (SC-1 PASS).
- C2: Preflight verification produces a structured report naming missing key PATHS only, run before startup fallback resolution (SC-2 PASS).
- C3: Guard consumes the manifest; divergence-prevention test passes (SC-3 PASS).
- C4: Missing contact keys resolve via default-fallback (static default `contact.mastodon_url` rendered as the contact, one-time non-blocking warning naming the missing key PATH only); no RuntimeError raised; startup continues (SC-6 PASS).
- C5: Remediation runbook exists naming the exact Cloud-store key and the preflight confirmation step (SC-4 PASS).
- C6: No secret VALUES are logged or exposed anywhere in preflight output or fallback warnings (SC-5 PASS).
- C7: Audit, z3-check, structural checks, pre-PR gate, and final regression check all PASS.
- C8: PR created (stacked strategy); completion summary emitted.

## lifecycle_events

- event: plan_created
  timestamp: "2026-10-01T23:15:00-04:00"
  plan_path: ".issues/1397/plan.md"
  phase_count: 4
- event: plan_revised
  timestamp: "2026-10-01T23:45:00-04:00"
  plan_path: ".issues/1397/plan.md"
  reason: >
    Spec Revision 1 (developer directive 2026-10-01: default-value fallback, never crash).
    Plan fidelity failure fixed — RuntimeError-guard preservation removed; SC-6 added;
    phase 3 revised to replace the crash path with manifest-coupled default-fallback
    resolution. Spec, structure.yaml, concern-map.yaml, dependency-contract.yaml,
    blast radius, phase table, DAG, and exit criteria updated.
    Revision artifact: artifacts/plan-revision.yaml.
  phase_count: 4
