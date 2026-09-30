---
plan_schema_version: 1
issue: 1385
title: "Semantic Search end-user interface — records page modes, threshold, scores, pagination, empty states"
authorization_scope: for_pr
pr_strategy: stacked
phase_count: 2
dispatch:
  - "test-driven-development: pre-regression (pre), red+green+post-regression (phases 1-2), regression-check (post)"
  - "verification-before-completion: pre-regression-verify (pre), verify (phases 1-2), pre-pr-gate (post)"
  - "orchestrator: commit-inline (per item), z3-check (post)"
  - "audit: verification-audit (post)"
  - "finishing-a-development-branch: checklist (post)"
  - "git-workflow-pr: review-prep, create (post)"
  - "completion-core: completion (post)"
---

# Implementation Plan — Issue #1385: Semantic Search end-user interface

- **Issue:** .issues/1385/spec.md — https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1385
- **Authorization:** approved-for-for_pr — full pipeline through PR creation; human-only merge
- **PR strategy:** stacked — one feature branch, N commits, one PR

## Goal

Extend the records-page search panel in `src/frontend/pages/records.py` to consume the #36 `search_semantic` seam: two new mode-radio entries, a coupled threshold control persisted per user, inline descending two-decimal score badges on semantic rows, rank-once pagination slicing, and per-status clean empty states.

## Architecture

The UI binds ONLY to the `search_semantic` / `SemanticSearchResult` v1 contract (results list[(record_id, score)], status ∈ {ok, empty_query, no_embeddings, stale_model}, message) — no pgvector/ORM imports. `preference_service.py` and `linguistic_service.py` are consumed unchanged; all edits are additive to `records.py`.

## Files

- `src/frontend/pages/records.py` — MODIFIED_EXTENSIVE (primary; all 8 SCs land here)
- `src/services/preference_service.py` — consumed as-is (get_preference/set_preference)
- `src/services/linguistic_service.py` — consumed seam (widened SearchMode owned by #36)
- `src/frontend/pages/table_maintenance.py` — referenced only (backfill-remedy copy for SC-6)

## Dispatch

- Phase 1: direct (1) + task-card (2-8)
- Phase 2: task-card (9-17)
- Post-implementation: task-card (18-22) + direct (23)

## Blast Radius

Single primary modification: `src/frontend/pages/records.py` (additive UI work). Three consumed dependencies remain untouched (`preference_service.py`, `linguistic_service.py`, `table_maintenance.py`). No test files outside the Playwright harness; no dependency or model changes. Impact zones: sidebar search-controls block (radio, caption, threshold slot, filters), main-panel record-card render loop (header line scores, empty-state branches), pagination session-state handling (`current_page`).

## Admonishment — Compliance

> **Compliance:** All SCs must pass before completion. Partial implementation is not permitted. Each item is daisy-chained — item N's commit is precondition for item N+1's RED.

## One-Step-at-a-Time

> **One step at a time.** Execute exactly one step. Report progress. Wait for instruction before the next step.

## Step Status

> **Step status:** Report `[item N] [PASS|FAIL]` after each step. If FAIL, report blocker and halt.

## Enforcement Gate

> **Enforcement gate:** All SCs must pass before this plan is complete. Partial implementation is not permitted.

## Phase Table

| Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch |
|---|---|---|---|---|---|---|
| 1 | UI surface scaffolding — mode entries, threshold control, language-filter disabled parity | Additive UI surface not dependent on seam result data: mode radio + captions (SC-1), coupled threshold w/ persistence + snap-back (SC-2, SC-3), language-filter disabled-parity mirroring FTS idiom (SC-8) | SC-1, SC-2, SC-3, SC-8 | — | 2-8 | direct (1) + task-card (2-8) |
| 2 | Seam consumption — mode dispatch, score display, pagination slicing, empty states | Render/dispatch paths consuming the #36 `search_semantic` seam: widened SearchMode dispatch (SC-7 wired first), score badges (SC-4), rank-once pagination (SC-5), per-status empty states (SC-6) | SC-7, SC-4, SC-5, SC-6 | 1 | 9-17 | task-card (9-17) |

## Self-Remediation Protocol

> **Self-Remediation Protocol:** If a step FAILs: diagnose root cause, fix the deliverable, re-verify. If the fix requires spec revision, update the spec and re-enter the plan. Escalate only after remediation failure.

## Exit Criteria

- [ ] C1. All 8 SCs verified PASS with behavioral evidence matching each SC's declared evidence type (all behavioral; structural substitution is EVIDENCE_TYPE_MISMATCH → FAIL)
- [ ] C2. Phase-1 SCs (SC-1, SC-2, SC-3, SC-8) pass before Phase-2 RED steps begin
- [ ] C3. Each SC has its own RED/GREEN/COMMIT cycle with test + implementation in one atomic commit
- [ ] C4. Existing four search modes verified regression-safe (SC-7 regression harness)
- [ ] C5. UI imports no pgvector/ORM internals; binds only to `search_semantic`/`SemanticSearchResult` v1 (R-8)
- [ ] C6. Z3 dependency-check passes against `.issues/1385/dependency-contract.yaml`
- [ ] C7. Audit executed; all findings remediated or explicitly dispositioned
- [ ] C8. PR created (human-only merge; no auto-close keywords for stakeholder issues)

# Phase 1 — UI surface scaffolding — mode entries, threshold control, language-filter disabled parity

- **Concern:** records.py additive UI surface independent of seam result data.
- **Files:** `src/frontend/pages/records.py`
- **SCs:** SC-1, SC-2, SC-3, SC-8
- **Dependencies:** none
- **Entry condition:** clean pre-regression baseline on the feature branch.
- **Exit condition:** SC-1, SC-2, SC-3, SC-8 verified PASS and committed.

## Code Path Coverage (Phase 1)

- SC-1: sidebar search-controls block — mode radio creation call; `SEARCH_MODE_CAPTIONS` dict ADDs "Semantic Gloss" and "Semantic All"; single selected-mode `st.caption` under the radio unchanged.
- SC-2: threshold control render — `st.slider` + `st.number_input` two-way coupled in stable slot below mode caption, above search/clear buttons, present in ALL modes, `disabled=` in non-semantic modes; init seeds session state from `PreferenceService.get_preference('records', 'semantic_threshold', default 0.80)`; persist via `set_preference('records', 'semantic_threshold', str(value))` matching page_size string idiom.
- SC-3: threshold numeric-input validation guard — reject non-numeric/out-of-range, snap back, leave preference unchanged.
- SC-8: language selectbox + language-role radio — disabled state + explanatory help text in both semantic modes, mirroring FTS idiom; previously-selected value preserved but inert.

## Cross-Cutting SCs (Phase 1)

- R-8 binding constraint (no pgvector/ORM imports) applies to every Phase-1 GREEN step; none of Phase 1 touches `linguistic_service.py` or imports below the seam.

## Interface Boundaries (Phase 1)

- `get_preference('records', 'semantic_threshold', default 0.80)` → str; `set_preference('records', 'semantic_threshold', str(value))` with value float in [0.0, 1.0].
- No seam calls in Phase 1 — the `search_semantic` contract is consumed only in Phase 2.

## State Transitions (Phase 1)

- Session state: threshold key seeded once from stored-or-default preference; radio selection state extends with two new keys in the existing mode list; language/role session-state keys unchanged (values preserved but inert in semantic modes).

## Steps (Phase 1)

- [ ] 1. (**direct**) Coherence gate — confirm plan is faithful to spec (R-1..R-9 mapped to items below; DAG 1→2 acyclic; all 8 SCs colocated in their assigned phase per structure.yaml triplet-colocation PASS)
  - Spec: `.issues/1385/spec.md`; structure: `.issues/1385/artifacts/structure.yaml`
- [ ] 2. (**task-card**) Baseline check — dispatch `task(..., prompt: "execute pre-regression from test-driven-development. Read test-driven-development/tasks/pre-regression.md first")`
  - Pre-clean `tmp/{issue-1385}/artifacts/pipeline-pre-regression-*`
  - Confirms existing mode radio, captions, filters, pagination behavior green before any edit

Item 1 (SC-1): Mode radio entries + captions
- [ ] 3. (**task-card**) RED — dispatch `task(..., prompt: "execute red task from test-driven-development. Read test-driven-development/tasks/red.md first")`
  - Pre-clean `tmp/{issue-1385}/artifacts/pipeline-red-*`
  - Playwright test asserts the mode radio lacks "Semantic Gloss" and "Semantic All" and SEARCH_MODE_CAPTIONS lacks the two keys — test FAILS (change doesn't exist yet). SC: SC-1
- [ ] 4. (**task-card**) GREEN — dispatch `task(..., prompt: "execute green task from test-driven-development. Read test-driven-development/tasks/green.md first")`
  - Pre-clean `tmp/{issue-1385}/artifacts/pipeline-green-*`
  - ADD the two entries to SEARCH_MODE_CAPTIONS + mode radio; existing 4 options and captions untouched; single selected-mode caption pattern unchanged. SC: SC-1
- [ ] 5. (**task-card**) Post-regression — dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - Pre-clean `tmp/{issue-1385}/artifacts/pipeline-post-regression-*` — no regression across existing UI assertions. SC: SC-1
- [ ] 6. (**task-card**) Verify — dispatch `task(..., prompt: "execute verify task from verification-before-completion. Read verification-before-completion/tasks/verify.md first")`
  - Pre-clean `tmp/{issue-1385}/artifacts/pipeline-verify-*`; behavioral Playwright evidence only. SC: SC-1
- [ ] 7. (**direct**) Commit-inline — `git add src/frontend/pages/records.py <test file> && git commit -m "feat(records): add Semantic Gloss and Semantic All mode radio entries with captions"`
  - Test + change in one atomic slice; no co-author trailers (squash adds them at PR time). SC: SC-1

Item 2 (SC-2): Threshold preference control — coupled, persists, stable slot
- [ ] 8. (**task-card**) RED/GREEN/post-regression/verify/commit-inline daisy chain per the reference-card cycle
  - RED: widget test asserts no `semantic_threshold` preference control exists on the records page (fails)
  - GREEN: render coupled slider+numeric in stable sidebar slot (below mode caption, above search/clear buttons) present in ALL modes with `disabled=` + "Applies only in Semantic modes." help text in non-semantic modes; init from `get_preference('records','semantic_threshold', default 0.80)`; persist via `set_preference(str(value))`
  - Verify: Playwright/pytest two-way synchronisation, persistence round-trip, placement + disabled/help assertions
  - Commit: threshold control. SC: SC-2

Item 3 (SC-3): Invalid threshold edit rejected + snap-back
- [ ] 9. (**task-card**) RED/GREEN/post-regression/verify/commit-inline daisy chain per the reference-card cycle
  - RED: Playwright test asserts an invalid threshold edit persists with no snap-back (fails)
  - GREEN: validation guard rejecting non-numeric/out-of-range with widget snap-back to last accepted value; preference unchanged
  - Verify: Playwright invalid-input revert assertion
  - Commit: threshold control validation. SC: SC-3

Item 4 (SC-8): Language filters disabled in semantic modes
- [ ] 10. (**task-card**) RED/GREEN/post-regression/verify/commit-inline daisy chain per the reference-card cycle
  - RED: Playwright test asserts language selectbox + language-role radio remain enabled in both semantic modes (fails)
  - GREEN: disabled state + explanatory help text mirroring the FTS disabled-filter idiom; previously-selected value preserved but inert
  - Verify: Playwright disabled + help-text assertions in both semantic modes; existing modes' filter state unchanged
  - Commit: language-filter disabled state. SC: SC-8

## Phase 1 Completion Block

- [ ] 11. (**task-card**) Phase-1 completion verification — dispatch `task(..., prompt: "execute verify task from verification-before-completion. Read verification-before-completion/tasks/verify.md first")`
  - Assert SC-1, SC-2, SC-3, SC-8 all PASS with behavioral evidence; any FAIL → self-remediation protocol before Phase 2

## Phase 1 Cost Frame

Computation frame: Cost is measured in defect-discovery-latency, not tool calls. Correctness is the only metric.
- Action cost: Four behavioral cycles (mode entries, threshold coupling + persistence, snap-back guard, disabled-filter parity) each cost minutes of Playwright execution — every sidebar control on the app's highest-traffic page is touched correctly.
- Skipping cost: Skipping any Phase-1 verification costs days-to-weeks of user-reported defect latency — a broken radio silently wrong-returns results, thresholds reset per session and erode linguist trust, a typo corrupts stored preferences silently, and enabled-but-ignored language filters produce a silent wrong-result class found in support tickets.
- Identity anchor: Correctness is the only metric.

## Concern Transition — Phase 1 → Phase 2

Phase 2's RED/GREEN assertions operate on the Semantic Gloss/Semantic All mode entries and the stable threshold slot created in Phase 1; SC-7 dispatch requires selectable semantic modes (SC-1). Phase 1's committed state is the precondition for Phase 2's first RED.

# Phase 2 — Seam consumption — mode dispatch, score display, pagination slicing, empty states

- **Concern:** records.py render/dispatch paths consuming the #36 `search_semantic` seam.
- **Files:** `src/frontend/pages/records.py` (primary), `test/` Playwright harness (tests)
- **SCs:** SC-7, SC-4, SC-5, SC-6
- **Dependencies:** Phase 1
- **Seam dependency:** #36 must have delivered `search_semantic` + `SemanticSearchResult` v1 (verified stable on disk; consumed as a frozen contract per `.issues/1385/artifacts/interface-compatibility.yaml`)
- **Entry condition:** Phase 1 completion block PASS.
- **Exit condition:** SC-7, SC-4, SC-5, SC-6 verified PASS and committed.

## Code Path Coverage (Phase 2)

- SC-7: `search_records` entry dispatch widened SearchMode Literal; wire results per mode; regression coverage for the existing four modes.
- SC-4: record-card render loop header line ("Record #id (Source: X)") — append score in semantic branch; fixed two decimals; skip in exact-match modes; data already sorted desc with record_id-asc tie-break.
- SC-5: pagination — slice already-returned ranked list on page change; no service re-invocation; `max(1, total_pages)` clamping preserved.
- SC-6: empty-state branch — map status + message to MAIN-panel blocks (st.info informational; st.warning remedy-required); zero-results reuses empty-batch branch with status-specific copy.

## Cross-Cutting SCs (Phase 2)

- R-8 binding constraint: no pgvector/ORM imports; SC-6 empty-state copy cross-references `table_maintenance.py` Data Reprocessing → Embedding Backfill (naming reference only, no code coupling).

## Interface Boundaries (Phase 2)

- `search_semantic(mode, query, threshold, source_id, limit)` → SemanticSearchResult v1 (results list[(record_id, score)], status, message). Frozen contract; UI consumes `results` + `status` + `message` and nothing below the seam.
- Only `source_id` passes through — no language_id, no language_role (drives SC-8 disabled state).

## State Transitions (Phase 2)

- Session state `current_page`: page navigation slices the stored ranked list (desc score, record_id asc tie-break); clamping `max(1, total_pages)` preserved; single search invocation per query.

## Steps (Phase 2)

Item 5 (SC-7): Mode dispatch through the seam
- [ ] 12. (**task-card**) RED — dispatch `task(..., prompt: "execute red task from test-driven-development. Read test-driven-development/tasks/red.md first")`
  - Pre-clean `tmp/{issue-1385}/artifacts/pipeline-red-*`
  - Behavioral harness asserts semantic modes yield errors / existing modes regress (fails). Harness precedent: `test_search_mode_ui_red.py`. SC: SC-7
- [ ] 13. (**task-card**) GREEN — dispatch `task(..., prompt: "execute green task from test-driven-development. Read test-driven-development/tasks/green.md first")`
  - Pre-clean `tmp/{issue-1385}/artifacts/pipeline-green-*`
  - Dispatch by widened SearchMode Literal through `search_records` entry; wire results per mode. SC: SC-7
- [ ] 14. (**task-card**) Post-regression/verify/commit-inline — dispatch post-regression `task(..., prompt: "execute phase-4 task from test-driven-development")`, pre-clean `pipeline-post-regression-*`; then verify `task(..., prompt: "execute verify task from verification-before-completion. Read verification-before-completion/tasks/verify.md first")`, pre-clean `pipeline-verify-*`; then orchestrator commits dispatch wiring + regression test
  - Verify result sets differ per mode; existing four modes unchanged. Commit: "feat(records): wire semantic modes through search_records dispatch". SC: SC-7

Item 6 (SC-4): Score badges on semantic rows
- [ ] 15. (**task-card**) RED/GREEN/post-regression/verify/commit-inline daisy chain per the reference-card cycle
  - RED: test asserts no score badges render for any mode (fails)
  - GREEN: consume seam `results` scores in the semantic branch; render descending, inline in the card header line, fixed two decimals; skip exact-match modes; theme-aware native elements only (no hex/rgba, no st.html iframe CSS)
  - Verify: Playwright badge presence/order/format + absence assertions
  - Commit: "feat(records): render two-decimal similarity scores inline on semantic rows". SC: SC-4

Item 7 (SC-5): Pagination rank-once slice
- [ ] 16. (**task-card**) RED/GREEN/post-regression/verify/commit-inline daisy chain per the reference-card cycle
  - RED: test asserts page navigation re-invokes search or reorders results (fails)
  - GREEN: slice the already-returned ranked list on page change; no service re-invocation; `max(1, total_pages)` clamping preserved
  - Verify: Playwright order stability across navigation + invocation count
  - Commit: "fix(records): slice cached ranked list on page navigation without re-search". SC: SC-5

Item 8 (SC-6): Empty-state rendering per status payload
- [ ] 17. (**task-card**) RED/GREEN/post-regression/verify/commit-inline daisy chain per the reference-card cycle
  - RED: test asserts no crash-guard rendering exists for seam statuses (fails)
  - GREEN: map each status+message to MAIN-panel empty state — st.info for `empty_query` and zero-results-after-threshold (reusing the existing empty-batch branch with status-specific copy), st.warning for `no_embeddings` and `stale_model`; stale/none message names the backfill remedy (Table Maintenance → Data Reprocessing → Embedding Backfill)
  - Verify: Playwright mocked-payload per-status rendering assertions; never a crash
  - Commit: "feat(records): render per-status semantic empty states in main panel". SC: SC-6

# Post-Implementation

- [ ] 18. (**task-card**) Adversarial audit — dispatch `task(..., prompt: "execute verification-audit DiMo investigator from audit. Read audit/tasks/verification-audit-investigator.md first")`, followed by validator, evaluator, arbiter in sequence
  - Pre-clean `tmp/{issue-1385}/artifacts/pipeline-audit-*`; DONE_WITH_CONCERNS coerces to FAIL; findings demand remediation before PR
- [ ] 19. (**direct**) Z3 dependency check — `./.opencode/tools/solve check --state-path .issues/1385/artifacts/solve-output.yaml --contract-path .issues/1385/dependency-contract.yaml`
  - Pre-clean `tmp/{issue-1385}/artifacts/pipeline-z3-check-*`; phase DAG 1→2 must verify
- [ ] 20. (**task-card**) Structural checks — dispatch `task(..., prompt: "execute checklist task from finishing-a-development-branch. Read finishing-a-development-branch/tasks/checklist.md first")`
  - Pre-clean `tmp/{issue-1385}/artifacts/pipeline-structural-checks-*`; lint/typecheck/format checks on modified files
- [ ] 21. (**task-card**) Pre-PR gate — dispatch `task(..., prompt: "execute verify task from verification-before-completion. Read verification-before-completion/tasks/verify.md first")`
  - Pre-clean `tmp/{issue-1385}/artifacts/pipeline-pre-pr-gate-*`; reads all SC verdicts; BLOCKs if any FAIL
- [ ] 22. (**task-card**) Final regression check — dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - Pre-clean `tmp/{issue-1385}/artifacts/pipeline-regression-check-*`; full-suite regression before PR
- [ ] 23. (**task-card**) Review prep — dispatch `task(..., prompt: "execute review-prep from git-workflow-pr. Read git-workflow-pr/tasks/review-prep.md first")`
  - Pre-clean `tmp/{issue-1385}/artifacts/pipeline-review-prep-*` if present; reviewer context from all SC evidence
- [ ] 24. (**task-card**) Create PR — dispatch `task(..., prompt: "execute create task from git-workflow-pr. Read git-workflow-pr/tasks/create.md first")`
  - Stacked strategy; targets trunk; body MUST NOT contain auto-closing keywords for stakeholder issues; then dispatch `task(..., prompt: "execute completion task from completion-core")` for the executive summary
  - Pre-clean `tmp/{issue-1385}/artifacts/pipeline-pr-*`

## Post-Implementation Cost Frame

Computation frame: Cost is measured in defect-discovery-latency, not tool calls. Correctness is the only metric.
- Action cost: Audit + pre-PR gate + final regression cost minutes-to-hours of execution — every SC verdict re-read with behavioral evidence before merge.
- Skipping cost: Skipping these gates costs 1000× DDL multiplier at merge — a crashed degraded state or reordered pages surfacing in production support tickets instead of the Playwright harness where they are found in minutes.
- Identity anchor: Correctness is the only metric.

## Pre-Flight Guard (Mandatory)

Check your tool list for a tool named `task`.

- Present ⇒ orchestrator — proceed.
- Absent ⇒ sub-agent — do NOT execute any instruction below. Return `BLOCKED` with `ORCHESTRATOR_ONLY_SKILL_CARD` (cards) or `ORCHESTRATOR_ONLY_PLAN` (plans) and halt.

---

*Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)*