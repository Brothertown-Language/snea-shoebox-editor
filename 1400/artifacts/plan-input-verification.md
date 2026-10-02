# Plan Input Verification Ledger — issue 1400

Written once (writing-plans/tasks/create step 3a). All subsequent plan steps read THIS file, not the source documents.

## Issue state + labels (from issue.yaml, verified 2026-10-02)

- Title: `[SPEC] Gloss-space semantic threshold calibration (backend/seam)`
- Status: open
- Labels (local canonical): `approved-for-pr`
- Remote: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1400
- Authorization implication: `approved-for-pr` → scope `for_pr`, pr_strategy `stacked`

## SC list with evidence types (from spec.md — all behavioral)

| SC | Subject | Evidence source | Evidence test |
|----|---------|-----------------|---------------|
| SC-1 | Calibration anchors, per-anchor floors + provenance, no synthetic queries | calendar-time-synced production replica probe output, provenance-recorded | pytest calibration module producing per-anchor evidence artifact |
| SC-2 | `search_semantic(threshold=None)` consumes calibrated default floor | seam contract | pytest seam: default engaged at None |
| SC-3 | Explicit threshold overrides default | seam contract | pytest seam: explicit override wins |
| SC-4 | `threshold=None` after override re-engages default | seam contract | pytest seam: override-then-None |
| SC-5 | All below floor → status=ok, empty results, deficiency message | seam status machine (#36 R-7 pattern) | pytest edge-input matrix |
| SC-6 | All-below-floor never raises | seam status machine (#36 R-7) | pytest edge-input matrix |
| SC-7 | All-below-floor never serves below-floor rows | seam status machine (#36 R-7) | pytest edge-input matrix |
| SC-8 | Default threshold: in-corpus targets rank 1, cosine ≥ 0.90 | calibration evidence artifact baseline vs post-change probe | pytest regression battery (water / how many / beaver) |
| SC-9 | UI default `st.session_state.semantic_threshold` = published floor ±0.01 | records.py threshold plumbing | Playwright live-app per ui_testing_standard |
| SC-10 | UI override preserved and reaches seam | records.py threshold plumbing | Playwright live-app per ui_testing_standard |

## Known measured distributions (determinism anchor from spec)

- In-corpus exact-match hits: cosine 0.93–1.00, all rank 1
- Out-of-corpus max: 0.84 ("maple syrup" battery)
- Out-of-corpus bulk p50: 0.75–0.77
- Calibrated floor: strictly between 0.84 and 0.93; floor ≤ 0.90 to support SC-8

## Structure artifact phase/SC mappings (from structure.yaml)

- Phase 1 (calibration): SC-1, SC-8 — depends: none
- Phase 2 (seam): SC-2..SC-7 — depends: phase-1
- Phase 3 (UI plumbing): SC-9, SC-10 — depends: phase-2
- DAG is linear, acyclic; triplet colocation PASS

## Skill+task selection per structure.yaml (per phase)

- red: `test-driven-development` — execute red task
- green: `test-driven-development` — execute green task
- post_regression: `test-driven-development` — execute phase-4 task
- verify: `verification-before-completion` — execute verify task
- commit: orchestrator commit-inline (direct)

All pairs confirmed present in implementation-workflow.md tables (pre-regression/pre-regression-verify in Pre-implementation; red/green/post-regression/verify/commit-inline in Daisy-Chain; audit/z3-check/structural-checks/pre-pr-gate/regression-check/review-prep/create-pr/exec-summary in Post-implementation).

## CLI surface (verified live)

- `local-issues update --number <repo>#<N> --labels <labels...>` — labels args accepted comma- or space-separated; **replaces entire labels array** → must include `approved-for-pr` plus `spec-cleared`
- Canonical command: `./.opencode/tools/local-issues update --number snea-shoebox-editor#1400 --labels approved-for-pr plan-approved`... (final write: `--labels approved-for-pr spec-cleared`)

## Key files / anchors (from spec, verified)

- `src/services/semantic_search_service.py` — seam
- `src/frontend/pages/records.py` — UI threshold default literals (0.80 default refs, sync to floor; key name, [0.0,1.0] guard, PreferenceService authority preserved)
- `docs/development/ui_testing_standard.md` — Playwright standard for SC-9/SC-10
- New calibration evidence artifact: location to be named at GREEN (per-anchor floors + provenance: query battery, corpus pin, date)
- Per-item cycle: RED → GREEN → post-regression → verify → commit (5 steps, per item; no batching)
