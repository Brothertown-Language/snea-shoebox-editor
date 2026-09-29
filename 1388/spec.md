# [SPEC-FIX] #1388 — Remediate 5 pre-existing test-harness failures surfaced by #36 pre-regression baseline (stale-RED tests + sys.modules mock leak)

> **Full spec and artifacts: [`https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1388/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1388/)**

## Intent and Executive Summary

**Problem Statement:** The #36 pre-regression baseline (synced DB, trunk tip `08c1e93`, zero #36 changes) records 5 pre-existing pytest failures: 3 stale-RED tests in `test/test_search_mode_ui_red.py` asserting UI removed/superseded by commit `3f54ad3`, and 2 order-dependent failures in `test/test_migration_backfill_search_entries.py` caused by module-level `sys.modules` mock leaks in two other test files.

**Root Cause / Motivation:** Live diagnosis (systematic-debugging; pairwise A/B/C experiments, DOM probes, git forensics) classified all 5 as test-harness defects — zero real product regressions. Two carrier test scripts install `MagicMock()` into `sys.modules["src.services.*"]` at module level and never restore them; `migrations.py` lazily imports `UploadService` at call time, so migration tests resolve a MagicMock when a carrier runs first. The stale-RED tests assert superseded product behavior (grouping separators, "HW:" help text) or a broken stimulation path (`text_input.set_value` no longer propagates after `907843d` removed `on_change`). This fix is a prerequisite for #36's regression sweep to be meaningful.

**Approach Chosen:** Test-side repair only, per baked developer dispositions: (1) contain the `sys.modules` leak at its source in both carrier files using save/restore semantics (`unittest.mock.patch.dict` or exec-time save + teardown restore, insert-only semantics); (2) delete the 2 superseded stale-RED tests; (3) rewrite `test_header_shows_mode_name_and_count` to seed `st.session_state.search_query` directly then `run()`, asserting the "Search:" header across all markdown values.

**Alternatives Considered & Why Discarded:**
- *Defensive product change in `migrations.py`* (re-import or import-guard at the lazy-import site) — discarded: violates the baked C-1 constraint (product code SHALL NOT be modified); the migration code is faultless, the pollution is at the carriers.
- *Rewrite the 2 stale-RED tests to assert the new `st.caption` behavior* — discarded: developer explicitly chose deletion over caption rewrite (disposition 1), even though the diagnosis artifact offered the rewrite path.
- *Global conftest.py sys.modules auto-cleanup fixture* — discarded: `test/conftest.py` does not exist (verified live); adding it would expand scope beyond the two named carriers and mask, not contain, future leaks at the boundary (`test/ui/**` files are explicitly out of scope).

**Key Design Decisions:**
- *Insert-only restore semantics for sys.modules containment* — entries that existed before carrier execution are never deleted; only entries the carrier itself inserted are reverted. Tradeoff: slightly more code than naive `del sys.modules[...]`, but eliminates the regression mode where restoring deletes a pre-existing real module (decompose-output failure-mode analysis).
- *Containment precedes rewrite (item 1 → item 3 dependency)* — the rewrite lands on a module whose leak is already contained, so the module-level mock-installation lifecycle is stable when the new test path is added. Tradeoff: serialization of edits to the same file, accepted for stability.
- *No defensive product change* (C-1) — success is defined at suite level: 5 baseline failures resolve to green under the full suite in default alphabetical order.

**User Intent / Original Prompt:** Developer directive (2026-09-29): "triage the test and regression fails and create a fix spec" — issued when #36's pre-regression baseline gate reported 5 pre-existing failures and halted for disposition.

## Not Included

- **`src/**` (all product code)** — C-1 product freeze: test-harness repair only; `migrations.py` and `records.py` are faultless (verified live) and MUST NOT change.
- **`test/test_migration_backfill_search_entries.py`** — victim file is faultless; it flips to green solely as a verified side-effect of carrier containment (order-dependence A/B experiments).
- **`test/ui/test_records_*.py`** (5 files also mutate `sys.modules`) — not in the baseline failure set, currently passing, no open spec covers them; flagged at the boundary only.
- **Defensive re-import or import-guard in `migrations.py`** — rejected alternative; would harden the product against pollution it does not cause.
- **Caption-rewrite of the 2 deleted stale-RED tests** — developer chose deletion (superseded intent), not rewrite.

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method |
|----|-----------|---------------|---------------------|
| SC-1 | `test/test_search_mode_ui_red.py`'s module-level `sys.modules` mock installation is contained at source (prior entries saved and restored; insert-only semantics); `test_grouping_separators_render` and `test_help_text_below_radio` no longer exist in the file; its 3 surviving tests pass; a subprocess running `test_search_mode_ui_red.py` followed by `test_migration_backfill_search_entries.py` (diagnosis experiment C shape) reports 0 failures, and no `src.services.*` MagicMock survives the search-mode module's execution. | behavioral | pytest subprocess order-pair run + `--collect-only` count of deleted test names; pytest exit codes compared pre/post change |
| SC-2 | `test/test_filter_ux_red.py`'s module-level `sys.modules` mock installation is contained with the same save/restore semantics; its 4 existing tests pass; a subprocess running `test_filter_ux_red.py` followed by `test_migration_backfill_search_entries.py` (diagnosis experiment A shape) reports 0 failures; a post-run `sys.modules` probe shows no `src.services.*` MagicMock leak. | behavioral | pytest subprocess order-pair run (experiment A/B equivalence) + tmp/ probe script output |
| SC-3 | `test_header_shows_mode_name_and_count` in `test_search_mode_ui_red.py` seeds `st.session_state.search_query` with a non-empty value before/during `run()` and asserts the `"Search:"` header against all collected markdown values (no `markdown[0]` indexing); the test passes single-file, and a full-suite pytest run in default alphabetical order reports 0 failures (baseline contract: 49 previously passing + 5 repaired = all green). | behavioral | pytest single-file run + full-suite default-order run with exit codes; tests-run artifact per tests-run.yaml mandate |

> **Enforcement gate:** All success criteria MUST pass before this spec is considered complete. Partial implementation is not permitted.

## Requirements

R-1. `test_search_mode_ui_red.py` SHALL delete the test methods `test_grouping_separators_render` and `test_help_text_below_radio` — superseded by the intentional product change in commit `3f54ad3` — as clean removals with no re-export or backward-compat shim.

R-2. `test_search_mode_ui_red.py` SHALL contain its module-level `sys.modules` mock installation at source with save/restore semantics, and containment SHALL use insert-only restore semantics: entries that existed in `sys.modules` before carrier-execution are never deleted; only entries the carrier itself inserted are reverted after its execution scope.

R-3. `test_filter_ux_red.py` SHALL contain its module-level `sys.modules` mock installation at source with the same save/restore insert-only semantics applied for `test_search_mode_ui_red.py` (identical containment pattern, per cross-cutting consistency).

R-4. `test_header_shows_mode_name_and_count` SHALL be rewritten to stimulate the header render path by seeding `st.session_state.search_query` with a non-empty value (before/at run start such that the `records.py` state-init guard does not reset it) and then `run()` — it SHOULD NOT use `text_input.set_value` as the stimulation path (propagation broken by `907843d`).

R-5. The rewritten header test SHALL assert the `"Search:"` header against all collected markdown values (ordering-independent any-of scan) and SHALL NOT index `markdown[0]` (which holds pagination markdown, not the header).

R-6. The containment pattern in both carrier files SHALL restore prior `sys.modules` entries (or scope them via `unittest.mock.patch.dict`) such that after any carrier module's execution, no `src.services.*` MagicMock entry survives in `sys.modules`.

R-7. Product code (`src/**`) SHALL NOT be modified; the repair MUST be confined to `test/test_search_mode_ui_red.py` and `test/test_filter_ux_red.py`.

R-8. Containment MUST NOT break the carrier files' own currently-passing tests: all non-deleted, non-rewritten tests in both carrier files SHALL remain green after repair (within-execution service-mock resolution inside `AppTest.from_string` script execution is preserved).

## Cost Frame

Cost is measured in defect-discovery-latency, not tool calls. Correctness is the only metric.

- SC-1: Verifying containment + deletions via the order-pair subprocess pytest run costs minutes of execution time — the defect surfaces at gate 1 and the fix cost is bounded. Skipping means leaked MagicMocks keep poisoning in-process migration tests in every future full-suite run — an order-dependent, invisible-in-isolation failure class with unbounded rework latency (each future regression sweep re-trips it: diagnose, re-run, re-triage).
- SC-2: Verifying the filter_ux containment via the experiment A/B pairwise run costs minutes. Skipping means carrier 1 remains live and any test file loaded after it inherits the same contamination — the death-spiral pattern where a suite that passes in isolation silently fails in the full run, discovered only downstream.
- SC-3: Verifying the rewritten header test single-file and full-suite costs minutes. Skipping means a stale stimulation path (broken by `907843d`) ships as a permanent RED — masking real regressions in the header contract for every future baseline run.

## Items

### Item 1 (SC-1): Contain sys.modules mock leak in test_search_mode_ui_red.py + delete its 2 superseded stale-RED tests

- RED: subprocess pytest run of `test_search_mode_ui_red.py` followed by `test_migration_backfill_search_entries.py` (diagnosis experiment C shape) reports failures pre-change (5 baseline failures reproduce); `--collect-only` lists the 2 deleted test names pre-change.
- GREEN: add save/restore containment (insert-only semantics) around the module-level `sys.modules` mock installation in `RECORDS_TEST_SCRIPT`; delete `test_grouping_separators_render` and `test_help_text_below_radio`; same order-pair run reports 0 failures, surviving 3 tests pass, deleted names absent from collection.
- verify: collection-count check + order-pair exit codes + confirm within-execution mocking still resolves for the surviving tests' own `records()` imports.
- commit: one commit scoped to `test/test_search_mode_ui_red.py` (containment + 2 deletions).

### Item 2 (SC-2): Contain sys.modules mock leak in test_filter_ux_red.py

- RED: subprocess pytest run of `test_filter_ux_red.py` followed by `test_migration_backfill_search_entries.py` (experiment A shape) reports 2 failures pre-change.
- GREEN: apply the identical save/restore containment pattern to `RECORDS_TEST_SCRIPT`'s `sys.modules` block; run reports 8 passed (experiment B equivalence) and a tmp/ post-run `sys.modules` probe shows no `src.services.*` MagicMock.
- verify: pairwise exit codes + probe output + the file's 4 existing tests green.
- commit: one commit scoped to `test/test_filter_ux_red.py`.

### Item 3 (SC-3): Rewrite test_header_shows_mode_name_and_count — seed search_query directly, assert "Search:" across all markdown values

- RED: pre-rewrite test fails under stale path (`set_value` never reaches `session_state.search_query`; `markdown[0]` is pagination markdown) — already recorded in the #36 baseline.
- GREEN: replace the stimulation path with a direct non-empty `st.session_state.search_query` seed before `run()`; replace `markdown[0]` indexing with an any-of-all-values `"Search:"` scan; single-file run passes.
- verify: full-suite pytest run in default alphabetical order reports 0 failures (49 + 5 → all green); tests-run artifact written.

## Dependencies

| Reference | Relationship | Status |
|-----------|--------------|--------|
| #36 (`Brothertown-Language/snea-shoebox-editor`) | Surfacing issue — #36's pre-regression baseline and its diagnosis artifacts are the evidence base; this fix unblocks #36's regression sweep. No code-path coupling to #36's own SCs. | in progress on `feature/36-semantic-gloss-search-pgvector` (satisfied — no merge dependency; independent concern) |
| `tmp/issue-36/artifacts/baseline-failure-diagnosis.yaml` | Must be read before implementation — authoritative per-failure diagnosis (experiments A/B/C shapes define the RED/GREEN verification contracts). | present in `tmp/` (verified) |
| `tmp/issue-36/artifacts/pre-regression-baseline.yaml` | Must be read before implementation — baseline record (49 passed / 5 failed) defining the suite-health contract. | present in `tmp/` (verified) |
| Commits `85b9586`, `3f54ad3`, `907843d`, `5523299` | Git forensics grounding: `3f54ad3` (#1321) superseded the 2 deleted tests' assertions; `907843d` broke the `set_value` propagation path. | satisfied (merged on trunk tip `08c1e93`) |

## Traceability

| Requirement | SC(s) | Item(s) |
|-------------|-------|---------|
| R-1 (delete superseded ×2) | SC-1 | Item 1 |
| R-2 (contain carrier 2) | SC-1 | Item 1 |
| R-3 (contain carrier 1) | SC-2 | Item 2 |
| R-4 (rewrite stimulation) | SC-3 | Item 3 |
| R-5 (rewrite assertion) | SC-3 | Item 3 |
| R-6 (insert-only restore) | SC-1, SC-2 | Item 1, Item 2 |
| R-7 (product freeze) | SC-1, SC-2, SC-3 | Item 1, Item 2, Item 3 |
| R-8 (own-tests stay green) | SC-1, SC-2, SC-3 | Item 1, Item 2, Item 3 |

## Documentation Sources

| Source | Type | Location | Verification |
|--------|------|----------|-------------|
| Baseline failure diagnosis | code/local artifact | `tmp/issue-36/artifacts/baseline-failure-diagnosis.yaml` | read live this session; pairwise A/B/C experiments + DOM probes + git forensics |
| #36 pre-regression baseline | code/local artifact | `tmp/issue-36/artifacts/pre-regression-baseline.yaml` | read live this session; 49 passed / 5 failed record |
| Stale-RED test file | code | `test/test_search_mode_ui_red.py` (UI assertions, mock block, method locations) | direct file read, live session |
| Mock-leak carrier 1 | code | `test/test_filter_ux_red.py` (module-level `sys.modules` mutations) | direct file read, live session |
| Victim (read-only) | code | `test/test_migration_backfill_search_entries.py` + `src/database/migrations.py` lazy-import site (call-time `from src.services.upload_service import UploadService`) | direct file read, live session |
| Product path — header contract (read-only) | code | `src/frontend/pages/records.py` (header render, `st.caption` captions, state init, button-trigger propagation) | direct file read, live session |
| Superseding commit | git | commit `3f54ad3` (#1321 — grouping separators / "HW:" help text intentionally removed) | git forensics in diagnosis artifact; commit read |
| Propagation-breaking commit | git | commit `907843d` (removed `on_change`; `set_value` no longer reaches `session_state.search_query`) | git forensics in diagnosis artifact; commit read |
| Superseded-stale-RED commits | git | commits `85b9586`, `5523299` | git forensics in diagnosis artifact |

## Edge Cases

**Input boundaries:**
- **Empty/non-empty search query:** the header renders only when `search_term` is truthy — the rewritten test MUST seed a non-empty value or the assertion target never renders. Resolution: seed `"test"` (or equivalent non-empty string) before `run()`.
- **Empty markdown collection:** `AppTest` markdown collection may be empty in edge renders; the any-of scan naturally yields False and fails the test — correct behavior (assert fires only when the header is omitted).

**State transitions:**
- **Seeding vs. state-init guard:** `records.py` state init sets `search_query` only when the key is absent; seeding before/at run start survives it. Seeding after the first `run()` risks the widget-state init overwriting the seed — the rewrite order (seed then run in the same setup path verified in RED/GREEN) handles this.
- **sys.modules lifecycle:** pre-fix CLEAN → CONTAMINATED (persists across modules, victims fail); post-fix CLEAN → CONTAMINATED-within-execution → RESTORED (saved entries reinstated; carrier-inserted entries do not outlive the carrier's scope).

**Failure modes:**
- **Restoring deletes a pre-existing real module:** containment MUST use insert-only semantics — revert/delete only entries the carrier itself inserted; never delete entries that existed before execution (decompose-output failure-mode analysis).
- **Containment breaks within-execution mocking:** `records()` inside the AppTest script needs the service mocks during its own script execution — containment restores at teardown/scope-exit, not during exec; the carrier files' surviving green tests are the invariant check.
- **Seeding overwritten by widget-state init:** if the seed lands after first `run()`, the test fails RED — order verified during implementation RED/GREEN.
- **Order-dependence regression masking:** any full-suite GREEN claim MUST come from the default alphabetical-order run (the reproduction mechanism), never from isolation-only runs (which reverse-order runs also pass — verified in diagnosis).

**Concurrency:**
- None material — pytest in-process execution is single-threaded here; the sys.modules lifecycle is the only shared mutable state and is owned by the containment pattern (save/restore is deterministic, dict-iteration-order independent).

**Recovery:**
- If a containment pattern breaks a currently-passing carrier test (RED within GREEN run), the pattern is scoped further (per-execution save inside the script wrapper) rather than reverting product files — the C-1 freeze forbids product-side fixes for any repair failure.
- If the full-suite run still reports failures post-repair, the residual failures are triaged against the baseline diagnosis artifact as new defects (not silently absorbed) — out of this spec's scope.

---

🤖 Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
