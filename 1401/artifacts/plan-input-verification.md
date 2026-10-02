# Plan Input Verification Ledger — Issue 1401

Written once from verified sources; all subsequent plan-composition steps re-read this ledger, not the sources.

## Issue State

- Issue: 1401 — `[SPEC] Search-match highlighting in Records view`
- Local `issue.yaml` labels: `approved-for-pr` (authorization scope `for_pr`, PR strategy `stacked`)
- Status: open; local canonical source is `.issues/1401/issue.yaml`
- Spec: `.issues/1401/spec.md` (23 SCs, all `behavioral` evidence type)
- Structure artifact: `.issues/1401/artifacts/structure.yaml` (4 phases, DAG edges 1→3, 2→3, 3→4; independent pair [1,2])

## SC List with Evidence Types

All 23 SCs are `behavioral` evidence, pytest/Playwright execution with output inspection:

- SC-1, SC-2: pure stored-term span helper — occurrence spans / no-match empty contract (Phase 1)
- SC-3, SC-4: pure FTS query-token span helper — match spans / no-match empty contract (Phase 1)
- SC-5, SC-6, SC-7, SC-8: service data layer — additive matched-terms field, mirror container, ILIKE-mode collection, FTS/Semantic return None (Phase 2)
- SC-9 through SC-20: renderer default-off params, markup wrapping, malformed-span ignore, diff-token precedence, status-tint non-interference, base styling, distinctness, contrast ≥ 4.5:1, View-mode-only threading, auto-activation, empty-query boundary, semantic-mode boundary (Phase 3)
- SC-21, SC-22, SC-23: gated Playwright E2E on live local app — lexical highlight flow, semantic absence, empty-query absence (Phase 4)

## Structure Artifact Mappings

- Phase 1: SC-1..SC-4 — `test-driven-development` — items 1-4, cycle [RED, GREEN, verify, COMMIT]
- Phase 2: SC-5..SC-8 — `test-driven-development` — items 5-8, cycle [RED, GREEN, verify, COMMIT]
- Phase 3: SC-9..SC-20 — `test-driven-development` — items 9-20, cycle [RED, GREEN, verify, COMMIT]
- Phase 4: SC-21..SC-23 — `test-driven-development` with E2E gating per `test/ui/AGENTS.md` — items 21-23, cycle [RED, GREEN, verify, COMMIT]
- DAG: Phase 3 depends on Phases 1 and 2; Phase 4 depends on Phase 3; Phases 1 and 2 are independent.

## Per-Task Cycle Steps (from implementation-workflow reference card)

RED → GREEN → post-regression → verify → commit-inline (orchestrator-direct). Pre-implementation adds `pre-regression` and `pre-regression-verify`. Post-implementation: audit, z3-check (direct), structural-checks, pre-pr-gate, regression-check, review-prep, create-pr, exec-summary.

## CLI Surface Flags Needed

- `./.opencode/tools/local-issues update snea-shoebox-editor#1401 --labels <comma-separated list>` — replaces the entire labels array; every write MUST include existing labels (`approved-for-pr`) plus the new one (`spec-cleared`).
- Local `issue.yaml` labels array is the primary canonical label source; remote GitHub label write is best-effort secondary, never blocking.

## Plan Format Decisions (pinned)

- Single plan.md target per task-card instruction; frontmatter order: `plan_schema_version`, `issue`, `title`, `authorization_scope`, `pr_strategy`, `phase_count`, `dispatch`
- Phase-table columns exactly: `Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch`
- Continuous step numbering 1..N across pre-implementation, phases, post-implementation
- Dispatch indicators: `(**direct**)` and `(**task-card**)` only
- Pre-Flight Guard block verbatim with reason code `ORCHESTRATOR_ONLY_PLAN`
- Each item references exactly one SC-ID
