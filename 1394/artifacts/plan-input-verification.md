# Plan Input Verification Ledger — issue 1394

## Issue state + labels (from issue.yaml)
- Issue 1394, status open
- Labels: `approved-for-for_pr`
- Remote: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1394

## SC list with evidence types (from sc-summary.yaml)
- SC1 — After fresh sync, `format_type(atttypid, atttypmod)` for every `embedding` column returns `vector(384)`. Evidence: live-DB query + enforcement test (behavioral).
- SC2 — After fresh sync, `records.id` (and other autoincrement id columns) carry `nextval` defaults. Evidence: live-DB `pg_attrdef` query + enforcement test (behavioral).
- SC3 — Full test suite after sync: 0 failures (5 baseline failures gone, no new failures). Evidence: pytest run output (behavioral). RED baseline already exists (5 failed / 169 passed / 8 skipped at trunk tip eb467b8).
- SC4 — TDD phase-0 pre-regression baseline passes on synced DB. Evidence: baseline gate run (behavioral). RED baseline already exists (gate blocked at trunk tip).

## Structure artifact mappings (structure.yaml)
- Phase 1 (SC1): vector typmod in DDL builder — depends: none
- Phase 2 (SC2): nextval column defaults — depends: [1]
- Phase 3 (SC3): fresh sync + full suite green — depends: [1, 2]
- Phase 4 (SC4): TDD phase-0 baseline gate passes on synced DB — depends: [3]
- DAG verified; triplet co-location verified; no RED in phases 3-4.

## Skill+task dispatch refs (implementation-workflow.md reference card)
- pre-regression: test-driven-development :: phase-0 task
- pre-regression-verify: verification-before-completion :: verify task
- red / green / post-regression: test-driven-development :: red / green / phase-4 tasks
- verify: verification-before-completion :: verify task
- commit-inline: orchestrator direct
- audit: audit :: verification-audit investigator → validator → evaluator → arbiter
- z3-check: orchestrator direct via `.opencode/tools/solve`
- structural-checks: finishing-a-development-branch :: checklist task
- pre-pr-gate / regression-check: verification-before-completion / test-driven-development phase-4
- review-prep / create-pr: git-workflow-pr
- exec-summary: completion-core :: completion task

## CLI surface flags needed
- `./.opencode/tools/local-issues update snea-shoebox-editor#1394 --labels <full array>` — replaces entire labels array; must include all existing labels plus new one.

status: DONE
blocker_reason: null
