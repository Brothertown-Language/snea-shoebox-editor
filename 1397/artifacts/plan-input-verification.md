# Plan Input Verification Ledger — issue 1397

Verified once from sources at plan-creation time; subsequent plan-writing steps read THIS file only.

## Issue State

- Local `issue.yaml` (`.issues/1397/issue.yaml`): status `open`, labels `['approved-for-for_pr']`, title `[SPEC-FIX] Production outage: fail-fast contact.maintainer_label guard crashed deployed app — no deployed-secrets verification gate`.
- Authorization scope: `for_pr`; PR strategy: `stacked`.
- Spec exists at `.issues/1397/spec.md`.

## Success Criteria (from structure.yaml `success_criteria`, matching spec)

- SC-1: Machine-checkable inventory of required st.secrets keys as single-source-of-truth manifest.
- SC-2: Verification mechanism compares deploy target secrets store against manifest BEFORE app can crash (startup preflight and/or CI/deploy step) with structured report naming missing key PATHS only.
- SC-3: Preflight tied to fail-fast guard's key list so the two cannot diverge silently (guard consumes the same manifest).
- SC-4: Supply contact.maintainer_label in Streamlit Cloud secrets store (developer action, documented in runbook/report).
- SC-5: Never log or expose secret VALUES; key-presence-only checks (cross-cutting constraint, co-located with SC-2 in phase-2).

## Structure Artifact Mappings

- Phase DAG edges: 1→2, 1→3, 2→3, 2→4. No cycles. Phase 1 has no dependencies.
- Phase → SC: phase-1=[SC-1], phase-2=[SC-2, SC-5], phase-3=[SC-3], phase-4=[SC-4]. All 5 SCs covered.
- Triplet colocation: PASS; cross-phase dependency: PASS (per structure.yaml verification block).

## Workflow Reference Card Dispatch Strings (verified from implementation-workflow.md)

- pre-regression / red / green / post-regression: `task(..., prompt: "execute <task> task from test-driven-development")` (post-regression uses phase-4 task name).
- verify: `task(..., prompt: "execute verify task from verification-before-completion")`.
- commit-inline: orchestrator-direct `git add && git commit` — no sub-agent.
- audit: audit investigator → validator → evaluator → arbiter sequence.
- z3-check: orchestrator-direct `.opencode/tools/solve check`.
- structural-checks: finishing-a-development-branch checklist task.
- pre-pr-gate: verification-before-completion verify task.
- regression-check: test-driven-development phase-4 task.
- review-prep: git-workflow-pr review-prep task.
- create-pr: git-workflow-pr create task.
- exec-summary: completion-core completion task.

## CLI Surface Flags

- Label write (canonical local): `./.opencode/tools/local-issues update snea-shoebox-editor#1397 --labels approved-for-for_pr,spec-cleared` — replaces entire labels array, so all existing labels must be included (existing: `approved-for-for_pr`).

## Affected Files (from blast-radius.yaml)

- streamlit_app.py (guard, lines 229-243 — preflight integration point)
- .streamlit/secrets.toml, .streamlit/secrets.toml.production
- src/services/infrastructure_service.py (presence-check helpers, lines 104-113)
- src/aiven_utils.py (duplicate audit logic, lines 157-167)
- test/ (new tests; pattern: test_startup_maintainer_label_sc4.py)
- New: required-secrets manifest, preflight module, remediation runbook
