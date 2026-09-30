# Plan-input verification ledger — issue #1385 (create task)

Written once: 2026-09-30. Subsequent steps re-read THIS file, not sources.

## Issue state + labels (from .issues/1385/issue.yaml)

- status: open
- labels: [approved-for-for_pr]
- authorization scope: for_pr (halt_at = pr_created; PR creation authorized, human-only merge)
- github_url: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1385

## SC list with evidence types (from spec.md §Success Criteria)

All SCs are behavioral (Playwright/pytest evidence; zero structural/string SCs).

- SC-1: mode radio renders Semantic Gloss + Semantic All; SEARCH_MODE_CAPTIONS ADDs entries; single selected-mode caption pattern preserved. Evidence: Playwright.
- SC-2: threshold slider+numeric two-way coupled, persists via PreferenceService (records/semantic_threshold, default 0.80), stable slot in ALL modes, disabled + "Applies only in Semantic modes." help text in non-semantic modes. Evidence: Playwright/pytest.
- SC-3: non-numeric/out-of-range threshold edit rejected, widget snap-back, preference unchanged. Evidence: Playwright.
- SC-4: semantic rows show scores descending, inline in card header line, fixed two decimals; exact-match rows show none. Evidence: Playwright.
- SC-5: pagination slices ranked list; no re-invocation; max(1, total_pages) clamping preserved. Evidence: Playwright.
- SC-6: per-status empty states in MAIN panel (st.info: empty_query, zero-results; st.warning: no_embeddings, stale_model); stale/none copy names Embedding Backfill remedy; zero-results reuses empty-batch branch. Evidence: Playwright/mocked payload.
- SC-7: mode switching yields correct result sets per mode; existing 4 modes unchanged. Evidence: Playwright behavioral harness (precedent test_search_mode_ui_red.py).
- SC-8: language selectbox + language-role radio disabled with help text in both semantic modes, mirroring FTS idiom; existing modes unchanged. Evidence: Playwright.

## Structure artifact mappings (.issues/1385/artifacts/structure.yaml)

- Phase 1: UI surface scaffolding — SC-1, SC-2, SC-3, SC-8; depends_on: []
- Phase 2: Seam consumption — SC-7, SC-4, SC-5, SC-6; depends_on: [1] (SC-7 wired first inside phase 2)
- DAG: 1 → 2, no cycles; triplet colocation PASS (8/8); no cross-phase RED dependencies.

## Per-task cycle steps (from implementation-workflow reference card)

RED → GREEN → post-regression → verify → commit-inline (orchestrator). Pre-implementation: pre-regression, pre-regression-verify. Post-implementation: audit, z3-check (orchestrator solve check), structural-checks, pre-pr-gate, regression-check, review-prep, create-pr, exec-summary.

## CLI surface needed

- Label write (step 9): `./.opencode/tools/local-issues update .#1385 --labels approved-for-for_pr,spec-cleared` — replaces entire labels array; must include existing `approved-for-for_pr`.
- Z3 check: `./.opencode/tools/solve check --state-path <state> --contract-path .issues/1385/dependency-contract.yaml`

## Format notes

Guard block (ORCHESTRATOR_ONLY_PLAN) copied verbatim from plan-artifact-format.md §3.5. Cost frames follow dark-prose-007. Frontmatter field order: plan_schema_version, issue, title, authorization_scope, pr_strategy, phase_count, dispatch. Phase-table columns: Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch. Steps numbered continuously 1..N. Body: no fenced code blocks, no TBD, no line numbers.