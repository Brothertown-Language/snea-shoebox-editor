# Plan Input Verification Ledger — Issue #1409

Written once (2026-10-03). Downstream steps re-read THIS ledger, not the sources.

## Issue state + labels (from `.issues/1409/issue.yaml`)

- title: `[SPEC] Fix Streamlit dual-set widget warning on semantic threshold slider`
- status: open
- labels (pre-write): `needs-approval`, `spec-draft`
- Label write required: append `spec-cleared` → final array: `needs-approval`, `spec-draft`, `spec-cleared` (local-issues `update` REPLACES the whole labels array — include all existing)

## SC list with evidence types (from spec.md)

| SC | Criterion (condensed) | Evidence Type | Verification |
|----|----------------------|---------------|--------------|
| SC-1a | No Streamlit dual-set warning box for semantic_threshold_slider / _number with saved preference present | behavioral | Playwright :8501, SNEA_E2E=1, dedicated fixture surviving _delete_saved_threshold_preferences; screenshot artifact |
| SC-1b | Slider renders the saved value with saved preference present | behavioral | Same Playwright test; screenshot artifact |
| SC-2 | No preference → slider defaults to 0.93 (CALIBRATED_FLOOR) | behavioral | Existing SC-9 fresh-default test in test/ui/test_sc9_ui_threshold_default_red.py still passes |
| SC-3a | Saved override round-trips: edit → persist → render | behavioral | Existing SC-2 DOM round-trip Playwright test still passes |
| SC-3b | Saved value survives page rerun/navigation (no reset to default) | behavioral | New rerun/navigation Playwright assertion, unconditional in suite |
| SC-4 | Full pytest suite, zero new failures vs baseline | behavioral | `uv run pytest test/` baseline comparison; SNEA_E2E=1 when live app up |

All 6 SCs are behavioral — no structural/string SCs in this plan.

## Structure artifact mappings (from structure.yaml)

- Phases: phase-1 (Core dual-set fix, SC-1a), phase-2 (Preservation gates, SC-1b/SC-2/SC-3a/SC-3b, depends phase-1), phase-3 (Full suite regression gate, SC-4, depends phase-2)
- DAG: phase-1 → phase-2 → phase-3 (acyclic, verified)
- SC→item mapping: SC-1a→item1/p1; SC-1b→item2/p2; SC-2→item3/p2; SC-3a→item4/p2; SC-3b→item5/p2; SC-4→item6/p3
- Triplet colocation check: passed (each SC has RED/GREEN/COMMIT in exactly one phase)
- Cross-phase dependency check: passed (no RED depends on a later phase's output)

## Per-task cycle steps (from implementation-workflow reference card)

Per-item: RED (`test-driven-development`, task "red") → GREEN (`test-driven-development`, task "green") → verify (`verification-before-completion`, task "verify") → commit-inline (orchestrator direct `git add <files> && git commit -m "<message>"`; no co-author trailers at implementation time).

Pre-implementation: `pre-regression` (tdd phase-0 task) → `pre-regression-verify` (vbc verify).
Post-implementation: audit → z3-check (orchestrator, `.opencode/tools/solve check`) → structural-checks (finishing-a-development-branch checklist) → pre-pr-gate (vbc) → regression-check (tdd phase-4) → review-prep (git-workflow-pr) → create-pr (git-workflow-pr) → exec-summary (completion-core).

Step-specific pre-cleanup: `rm -f {project_root}/tmp/{issue-1409}/artifacts/pipeline-<step>-*` at the start of each pipeline step.

## CLI surface flags needed

- `./.opencode/tools/local-issues update snea-shoebox-editor#1409 --labels needs-approval,spec-draft,spec-cleared`
- `uv run pytest test/` (with SNEA_E2E=1 when live app on :8501)
- `.opencode/tools/solve check --state-path <state> --contract-path <contract>`

## Files

- src/frontend/pages/records.py (primary — widget instantiation block)
- test/ui/test_sc9_ui_threshold_default_red.py (test — reuse + extend)
- docs/development/ui_testing_standard.md (read before Playwright work)
- test/ (SC-4 regression surface)
