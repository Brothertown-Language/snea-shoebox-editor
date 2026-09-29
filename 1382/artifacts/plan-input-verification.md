# Plan Input Verification Ledger — #1382

## Issue State + Labels (from issue.yaml, read live this session)
- status: open
- labels: `approved-for-plan`, `spec-fix`, `database`, `data-integrity`
- authorization_scope: for_plan
- pr_strategy: none (implementation awaits separate authorization)
- github_url: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1382

## SC List with Evidence Types (from spec.md + sc-summary.yaml)
- SC-1: behavioral — `generate_sort_lx("kꝏ") == "koozzz"` (and `generate_sort_lx("k∞") == "koozzz"` regression pin)
- SC-2: behavioral — scan counts/lists exactly non-deleted ∞-bearing records; soft-deleted excluded; preview non-empty
- SC-3: behavioral — sidebar option admin-only (existing main() guard blocks non-admin)
- SC-4: behavioral — count display before action; zero-state informational; no mutation until button click
- SC-5: behavioral — apply-all remediates every record + exactly one EditHistory row each with correct snapshots/version
- SC-6: behavioral — remediate A / skip B leaves A clean+history, B unchanged+no history
- SC-7: behavioral — sort_lx and normalized_term byte-identical pre/post
- SC-8: behavioral — FTS ꝏ post-remediation query result set == ∞ pre-remediation result set
- SC-9: string — 0 U+221E occurrences in both seed files; 364 U+A74F each
- SC-10: string — "U+221E maps to oozzz" entry remains in symbol_map

## Structure Artifact Phase/SC Mapping
- phase-1 → SC-9 (item 1), SC-1+SC-10 (item 2); depends: none
- phase-2 → SC-2 (item 4); depends: phase-1
- phase-3 → SC-5 (item 5), SC-6 (item 6), SC-7 (item 7), SC-8 (item 8); depends: phase-2
- phase-4 → SC-3 (item 9), SC-4 (item 10); depends: phase-2, phase-3
- phase-5 → all SCs (item 11 terminal gate); depends: all
- DAG edges: 1→4, 2→4, 4→5, 5→6, 5→7, 5→8, 4→9, 5→9, 6→9, 8→9, 9→10, all→11. triplet_colocation_check: PASS; cross_phase_dependency_check: PASS. No cycles.
- Z3: SAT (+ postconditions + invariants) — solve-output.yaml; plan validate: valid

## Workflow Reference Card Steps (per-task cycle)
- Pre-implementation: pre-regression, pre-regression-verify
- Per item: red → green → post-regression → verify → commit-inline; commit-inline is orchestrator-direct
- Post-implementation: audit (+validator/evaluator/arbiter), z3-check (orchestrator, ./.opencode/tools/solve check), structural-checks, pre-pr-gate, regression-check, review-prep, create-pr, exec-summary

## CLI Surface Flags Needed
- Z3 check: `./.opencode/tools/solve check --state-path tmp/issue-1382/artifacts/state.yaml --contract-path .issues/1382/dependency-contract.yaml`
- Plan validate: `./.opencode/tools/plan validate --problem .issues/1382/artifacts/plan-problem.yaml --plan .issues/1382/artifacts/plan-output.yaml`
- Tests: `uv run pytest test/` (never bare pytest)

## Baked Facts (verified live this session, not from memory)
- `symbol_map` at src/services/linguistic_service.py generate_sort_lx() lines 152-157: `"\u221e": "oozzz"`, `"\u2714": ""`
- `populate_search_entries(record_ids, session=None)` at src/services/upload_service.py line 1758 — deletes+rebuilds SearchEntry/HeadwordSearchEntry/GlossSearchEntry/FTSEntry per record; fts_vector via to_tsvector('simple', generate_sort_lx(mdf_data))
- EditHistory model at src/database/models/workflow.py line 48: record_id, user_email, session_id, version, change_summary, prev_data, current_data
- update_record() EditHistory pattern at src/services/linguistic_service.py lines ~656-700: prev_data snapshot, version=current+1
- table_maintenance.py main() at line 124: admin guard `user_role != "admin"`; sidebar radio options ["Sources", "Soft Deleted Records", "Data Reprocessing"] at lines 145-152; dispatch chain 155-162; render_data_reprocessing_maintenance() progress pattern at lines 165-198
- Seed files: 364 U+221E occurrences each (verified via grep)
- pgserver fixture pattern: test/test_upload_search_entries.py setUpClass (pgserver.get_server, Base.metadata.create_all, sessionmaker)
- Locked-record guard exists in update_record() (`Rejecting update to locked record`) — remediation must mirror it
- Record model: is_deleted Boolean at src/database/models/core.py line 106
- Test suite: test/ (pgserver pattern), test/ui/ (StreamlitAppTest pattern)

## Regression Test Protocol (AGENTS.md mandate)
- Before every regression cycle: `bash scripts/sync_prod_to_local.sh` — MUST be the sync script from the feature branch under test
- pgserver fixture tests do not use the local DB, but the protocol applies before any regression cycle