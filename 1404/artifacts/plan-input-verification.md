# Plan Input Verification Ledger — issue #1404

Written once: 2026-10-03. Re-read THIS file for plan composition; do not re-verify sources.

## Issue state

- Repo: `snea-shoebox-editor` (root), issues prefix `.issues/`
- Local issue.yaml: does NOT exist yet (`.issues/1404/` contains spec.md, artifacts/, dependency-contract.yaml)
- Current labels (verified via `local-issues read-labels --number snea-shoebox-editor#1404`): `[]` (empty)
- Label write plan: `local-issues update --number snea-shoebox-editor#1404 --labels spec-cleared` (replace-all semantics fine since existing set is empty); remote GitHub label write is best-effort, non-blocking
- Platform: github.com, owner Brothertown-Language (remote label via gh best-effort)

## SC list with evidence types (from spec.md §Revised success criteria)

- SC-1: `search_records(search_mode='Semantic Gloss')` does not raise; `matched_terms` populated from the seam's real per-record matched terms — evidence: behavioral (live-path regression test against real search_semantic contract)
- SC-2: same for `search_mode='Semantic All'` — evidence: behavioral
- SC-3: regression tests exercise REAL `search_semantic` hit shapes (container hits AND `(record_id, score)` tuples), only DB session patched, no shape stubs — evidence: behavioral
- SC-4: no regression in existing suites — evidence: behavioral (full `uv run pytest test/` run)

## Structure artifact mappings

- Phases: P1 `semantic-dispatch-fix-and-real-shape-tests` (SC-1..SC-3), P2 `no-regression-check` (SC-4)
- DAG: P1 → P2. SC-3 depends on SC-1, SC-2. SC-4 depends on SC-1..SC-3.
- Files per structure: `src/services/linguistic_service.py`, `test/test_search_records_matched_terms_none_sc8_red.py`
- Per-phase skill_task_selection (from structure.yaml):
  - red → `task(..., "execute red task from test-driven-development")`
  - green → `task(..., "execute green task from test-driven-development")`
  - verify → `task(..., "execute verify task from verification-before-completion")`
  - commit → orchestrator commit-inline (direct, no dispatch)
  - P2 post-regression → `task(..., "execute phase-4 task from test-driven-development")`

## Implementation-workflow reference card — per-task cycle steps (authoritative)

- Pre-implementation: `pre-regression` (test-driven-development, task-card), `pre-regression-verify` (verification-before-completion, task-card)
- Per-SC cycle: `red` (task-card), `green` (task-card), `post-regression` (test-driven-development phase-4, task-card), `verify` (task-card), `commit-inline` (direct — orchestrator runs git add/commit)
- Post-implementation: `audit` (audit, task-card, DiMo sequence), `z3-check` (direct, `.opencode/tools/solve check`), `structural-checks` (finishing-a-development-branch, task-card), `pre-pr-gate` (verification-before-completion, task-card), `regression-check` (task-card), `review-prep` (git-workflow-pr, task-card), `create-pr` (git-workflow-pr, task-card), `exec-summary` (completion-core, task-card)
- Step-specific pre-cleanup table rows apply per step label (rm tmp/1404/artifacts/pipeline-<step>-*)

## CLI surface flags verified

- `local-issues read-labels --number repo#N`
- `local-issues update --number repo#N --labels <csv>` (replace-all — include all existing labels)

## Format decisions (pinned per plan-structure-standards)

- Frontmatter order: plan_schema_version, issue, title, authorization_scope, pr_strategy, phase_count, dispatch
- authorization_scope: for_pr; pr_strategy: stacked
- Phase-table columns: Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch
- Steps numbered 1..N continuous across pre-implementation, phases, post-implementation
- Dispatch indicators: `(**direct**)` / `(**task-card**)` only
- Single-file plan (plan.md) with phase sections per tasks/create.md target; guard block verbatim from guidelines/023-pre-flight-guard.md
