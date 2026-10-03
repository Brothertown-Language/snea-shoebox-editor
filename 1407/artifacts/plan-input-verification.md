# Plan Input Verification Ledger — Issue 1407

> Written once at create step 3a. All subsequent steps re-read THIS ledger, not the sources.

## Issue state + labels (from .issues/1407/issue.yaml)

- Labels at create time: `needs-approval`, `spec-draft`
- github_url: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1407
- Authorization context: `for_implementation` (dispatch context); pipeline halts after verification_complete

## SC list with evidence types (from spec.md §Success Criteria + sc-summary.yaml)

- SC-1 — Enter triggers search; commit from current suffixed key; current_page reset — behavioral
- SC-2 — after clear, Enter commits no stale query — behavioral
- SC-3 — button click = exactly one commit; unchanged path — behavioral
- SC-4a — neutral placeholder + coupled E2E aria-label selector updated same cycle, proven by execution — behavioral
- SC-4b — full pytest suite, zero new failures — behavioral

## Structure artifact mappings

- Single phase (Phase 1) covers all SCs; DAG item1 → item2, item1 → item3, item3 → item4a, item4a → item4b; no triplet split; no cross-phase deps
- Skill+task refs verified against implementation-workflow reference card: pre-regression, pre-regression-verify, red, green, post-regression, verify, commit-inline, audit, z3-check, structural-checks, pre-pr-gate, regression-check

## CLI surface flags actually needed

- `local-issues update snea-shoebox-editor#1407 --labels <full-array>` — replaces entire labels array; must include needs-approval, spec-draft, spec-cleared
- `local-issues validate-yaml --number snea-shoebox-editor#1407` (scoped mode; positional arg not accepted)
- `local-issues sync` for completion
- solve: `model --contract-path --query`, `check --contract-path --state-path` (state `variables` = flat name→bool map)
- plan: `plan --problem <problem.yaml>` (NOT --contract-path/--output; problem top-level keys limited to domain/types/objects/fluents/actions/init/goals; params must be dicts)

## Verified code facts

- records.py: `on_search_change` reads stale key `search_query_input` (dead code); text_input uses suffixed key, label "Enter text...", no on_change; clear handler increments `_search_input_key`
- test/ui/test_semantic_search_ui_flow_e2e.py: E2E locator aria-label "Enter text..." (single occurrence)
