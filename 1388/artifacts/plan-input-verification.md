# Plan Input Verification Ledger — #1388

## Issue State + Labels (from issue.yaml, read live this session)
- status: open
- labels: `approved-for-for_pr`, `spec-draft`
- authorization_scope: for_pr
- pr_strategy: stacked
- github_url: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1388

## SC List with Evidence Types (from spec.md)
- SC-1: behavioral — order-pair subprocess pytest run (search-mode carrier THEN migration victim); zero migration-file failures; residual failures confined to 3 named stale-RED tests.
- SC-2: behavioral — `pytest --collect-only` scans; neither `test_grouping_separators_render` nor `test_help_text_below_radio` collected.
- SC-3: behavioral — experiment A/B pairwise run (filter_ux carrier THEN migration victim) zero failures + no `src.services.*` MagicMock leak post-run.
- SC-4: behavioral — rewritten header test passes single-file; rewritten body uses any-of scan, no `markdown[0]` indexing.
- SC-5: behavioral — full-suite default-alphabetical-order run: 52 passed, 0 failed; DB pre-synced via `bash scripts/sync_prod_to_local.sh`; tests-run.yaml artifact recorded.

## Structure Artifact Phase/SC Mapping
- phase-1 → SC-1 (item 1), SC-2 (item 2); depends: none; same-file serialization note (item 1 → 2)
- phase-2 → SC-3 (item 3); depends: none
- phase-3 → SC-4 (item 4); depends: phase-1
- phase-4 → SC-5 (item 5); depends: phase-1, phase-2, phase-3
- DAG edges: 1→3, 1→4, 2→4, 3→4. triplet_colocation_check: PASS; cross_phase_dependency_check: PASS. No cycles.

## Workflow Reference Card Steps (per-task cycle)
- Pre-implementation: pre-regression, pre-regression-verify
- Per item: red → green → post-regression → verify → commit-inline; commit-inline is orchestrator-direct
- Post-implementation: audit (+validator/evaluator/arbiter), z3-check (orchestrator, ./.opencode/tools/solve check), structural-checks, pre-pr-gate, regression-check, review-prep, create-pr, exec-summary

## CLI Surface Flags Needed
- Label write: `./.opencode/tools/local-issues update <repo>#1388 --labels spec-cleared` — `local-issues update` replaces entire labels array; include existing labels (`approved-for-for_pr`, `spec-draft`) plus `spec-cleared`.
- Z3 check: `./.opencode/tools/solve check --state-path <state.yaml> --contract-path <contract.yaml>`

## Baked Facts (verified in spec, not re-probed)
- Module-level script constant is `RECORDS_SCRIPT` in both `test/test_search_mode_ui_red.py` and `test/test_filter_ux_red.py` (spec round-2 edit B).
- Baseline: 49 passed / 5 failed of 54 tests; post-repair suite: 52 tests.
- Product freeze (C-1): `src/**` MUST NOT change. Victim file `test/test_migration_backfill_search_entries.py` read-only.
- Diagnosis artifacts at `tmp/issue-36/artifacts/baseline-failure-diagnosis.yaml` and `tmp/issue-36/artifacts/pre-regression-baseline.yaml` — must be read before implementation.