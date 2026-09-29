# [SPEC-FIX] #1388 — Remediate 5 pre-existing test-harness failures surfaced by #36 pre-regression baseline (stale-RED tests + sys.modules mock leak)

> **Full spec and artifacts: [`https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1388/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1388/)**

## Intent and Executive Summary

**Problem Statement:** The #36 pre-regression baseline (synced DB, trunk tip `08c1e93`, zero #36 changes) records 5 pre-existing pytest failures: 3 stale-RED tests in `test/test_search_mode_ui_red.py` asserting UI removed/superseded by commit `3f54ad3`, and 2 order-dependent failures in `test/test_migration_backfill_search_entries.py` caused by module-level `sys.modules` mock leaks in two other test files.

**Root Cause / Motivation:** Live diagnosis (systematic-debugging; pairwise A/B/C experiments, DOM probes, git forensics) classified all 5 as test-harness defects — zero real product regressions. Two carrier test scripts install `MagicMock()` into `sys.modules["src.services.*"]` at module level and never restore them; `migrations.py` lazily imports `UploadService` at call time, so migration tests resolve a MagicMock when a carrier runs first. The stale-RED tests assert superseded product behavior (grouping separators, "HW:" help text) or a broken stimulation path (`text_input.set_value` no longer propagates after `907843d` removed `on_change`). This fix is a prerequisite for #36's regression sweep to be meaningful.

**Approach Chosen:** Test-side repair only, per baked developer dispositions: (1) contain the `sys.modules` leak at its source in both carrier files using save/restore semantics (`unittest.mock.patch.dict` or exec-time save + teardown restore, insert-only semantics); (2) delete the 2 superseded stale-RED tests; (3) rewrite `test_header_shows_mode_name_and_count` to seed `st.session_state.search_query` directly then `run()`, asserting the "Search:" header across all markdown values. The repair is decomposed into 5 atomic success criteria with 1:1 SC↔item mapping (spec-creation validate remediation).

**Alternatives Considered & Why Discarded:**
- *Defensive product change in `migrations.py`* (re-import or import-guard at the lazy-import site) — discarded: violates the baked C-1 constraint (product code SHALL NOT be modified); the migration code is faultless, the pollution is at the carriers.
- *Rewrite the 2 stale-RED tests to assert the new `st.caption` behavior* — discarded: developer explicitly chose deletion over caption rewrite (disposition 1), even though the diagnosis artifact offered the rewrite path.
- *Global conftest.py sys.modules auto-cleanup fixture* — discarded: `test/conftest.py` does not exist (verified live); adding it would expand scope beyond the two named carriers and mask, not contain, future leaks at the boundary (`test/ui/**` files are explicitly out of scope).

**Key Design Decisions:**
- *Insert-only restore semantics for sys.modules containment* — entries that existed before carrier execution are never deleted; only entries the carrier itself inserted are reverted. Tradeoff: slightly more code than naive `del sys.modules[...]`, but eliminates the regression mode where restoring deletes a pre-existing real module (decompose-output failure-mode analysis).
- *Same-file serialization (Item 1 → Item 2 → Item 4; Item 3 independent; Item 5 terminal)* — containment lands first so the module-level mock-installation lifecycle is stable before the deletion and rewrite edits touch the same file; the filter_ux containment (Item 3) has no file overlap. Tradeoff: serialization of edits to `test_search_mode_ui_red.py`, accepted for stability.
- *No defensive product change* (C-1) — success is defined at suite level: the post-repair suite is 52 tests (54 baseline minus 2 deleted stale-RED); all 52 green under the full suite in default alphabetical order = 49 previously passing + 3 repaired (header rewrite plus 2 order-dependence healings).

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
| SC-1 | A subprocess pytest run of `test/test_search_mode_ui_red.py` followed by `test/test_migration_backfill_search_entries.py` (diagnosis experiment C shape) reports zero failures from `test_migration_backfill_search_entries.py`, with all residual failures confined to the three named stale-RED tests in the search-mode file. | behavioral | pytest subprocess order-pair run with per-file failure inventory compared pre/post change |
| SC-2 | A `pytest --collect-only` run on the repaired `test/test_search_mode_ui_red.py` collects neither deleted stale-RED name — neither `test_grouping_separators_render` nor `test_help_text_below_radio` appears in collection. | behavioral | `pytest --collect-only` collected-name scan pre/post change |
| SC-3 | A subprocess pytest run of `test/test_filter_ux_red.py` followed by `test/test_migration_backfill_search_entries.py` (diagnosis experiment A shape) reports zero failures, reproducing experiment B's reversed-order equivalence. | behavioral | pytest subprocess order-pair run (experiment A/B equivalence) + tmp/ post-run `sys.modules` probe showing no `src.services.*` MagicMock leak |
| SC-4 | The rewritten `test_header_shows_mode_name_and_count` in `test/test_search_mode_ui_red.py` passes a single-file pytest run after being rewritten to seed `st.session_state.search_query` with a non-empty value before `run()` and assert the `"Search:"` header via an any-of scan across all collected markdown values. | behavioral | pytest single-file run + collected-source scan of the rewritten method body confirming zero `markdown[0]` indexing |
| SC-5 | A full-suite pytest run in default alphabetical order reports the post-repair suite green: 52 passed, 0 failed (54 baseline tests minus 2 deleted stale-RED; 49 previously passing plus 3 repaired). Before every regression test cycle, the local database MUST be re-synced from production via `bash scripts/sync_prod_to_local.sh` (repo Regression Test Protocol) so the run executes against a fresh production replica. | behavioral | full-suite pytest run in default alphabetical order with exit code + tests-run artifact per tests-run.yaml mandate |

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

- SC-1: Verifying the search-mode containment via the order-pair subprocess pytest run costs minutes of execution time — the defect surfaces at gate 1 and the fix cost is bounded. Skipping means leaked MagicMocks keep poisoning in-process migration tests in every future full-suite run — an order-dependent, invisible-in-isolation failure class with unbounded rework latency (each future regression sweep re-trips it: diagnose, re-run, re-triage).
- SC-2: Verifying the deletions via `--collect-only` costs seconds of execution time. Skipping means superseded assertions keep failing as a permanent RED against intentionally removed UI — masking real regressions in every future baseline run.
- SC-3: Verifying the filter_ux containment via the experiment A/B pairwise run costs minutes. Skipping means carrier 1 remains live and any test file loaded after it inherits the same contamination — the death-spiral pattern where a suite that passes in isolation silently fails in the full run, discovered only downstream.
- SC-4: Verifying the rewritten header test single-file costs minutes. Skipping means a stale stimulation path (broken by `907843d`) ships as a permanent RED — masking real regressions in the header contract for every future baseline run.
- SC-5: Verifying the full-suite default-order run costs minutes. Skipping means a suite-health green claim never passes through the reproduction mechanism (default alphabetical order) — the one order in which order-dependent failures reproduce, so a green claimed from isolation-only runs is unverifiable against the defect class this spec repairs.

## Items

### Item 1 (SC-1): Contain sys.modules mock leak at source in test_search_mode_ui_red.py

- RED: subprocess pytest run of `test_search_mode_ui_red.py` followed by `test_migration_backfill_search_entries.py` (diagnosis experiment C shape) reports 5 failed, 5 passed pre-change (10 tests collected — 6 search-mode + 4 migration; the 5 baseline failures reproduce).
- GREEN: add save/restore containment (insert-only semantics) around the module-level `sys.modules` mock installation in `RECORDS_SCRIPT`; the same order-pair run reports zero failures from `test_migration_backfill_search_entries.py`, with residual failures confined to the three named stale-RED tests (header failure carried to Item 4's full-suite gate).
- verify: order-pair exit codes with per-file failure inventory (zero migration-file failures in GREEN) + confirm within-execution mocking still resolves for the surviving tests' own `records()` imports.
- commit: one commit scoped to `test/test_search_mode_ui_red.py` (containment only).
- depends on: none (first edit to the file).
- enables: Items 2 and 4 (same-file serialization — the deletion and rewrite land on a module whose leak is already contained).

### Item 2 (SC-2): Delete the 2 superseded stale-RED tests from test_search_mode_ui_red.py

- RED: `pytest --collect-only` on `test_search_mode_ui_red.py` lists `test_grouping_separators_render` and `test_help_text_below_radio` pre-change (6 tests collected).
- GREEN: delete `test_grouping_separators_render` and `test_help_text_below_radio` as clean removals (no re-export, no shim); `--collect-only` neither lists the deleted names (collects 4 tests).
- verify: collect-only collected-name scan + the count delta 6 → 4 as derived from it.
- commit: one commit scoped to `test/test_search_mode_ui_red.py` (2 deletions).
- depends on: Item 1.
- enables: Item 4.

### Item 3 (SC-3): Contain sys.modules mock leak at source in test_filter_ux_red.py

- RED: subprocess pytest run of `test_filter_ux_red.py` followed by `test_migration_backfill_search_entries.py` (experiment A shape) reports 2 failed, 6 passed pre-change; tmp/ post-run probe shows the `src.services.*` MagicMock leak.
- GREEN: apply the identical save/restore insert-only containment pattern to `RECORDS_SCRIPT`'s `sys.modules` block; the order-pair rerun reports zero failures (experiment A/B equivalence: 8 passed in either order) and a tmp/ post-run probe shows no `src.services.*` MagicMock.
- verify: pairwise exit codes + probe output + the file's 4 existing tests green.
- commit: one commit scoped to `test/test_filter_ux_red.py`.
- depends on: none (independent file).
- enables: Item 5.

### Item 4 (SC-4): Rewrite test_header_shows_mode_name_and_count — seed search_query directly, assert "Search:" across all markdown values

- RED: pre-rewrite test fails under stale path (`set_value` never reaches `session_state.search_query`; `markdown[0]` is pagination markdown) — already recorded in the #36 baseline.
- GREEN: replace the stimulation path with a direct non-empty `st.session_state.search_query` seed before `run()`; replace `markdown[0]` indexing with an any-of-all-values `"Search:"` scan; single-file run passes.
- verify: single-file pytest run + a read of the rewritten method body confirming the any-of scan form in place of `markdown[0]`.
- commit: one commit scoped to `test/test_search_mode_ui_red.py` (header rewrite).
- depends on: Item 2.
- enables: Item 5.

### Item 5 (SC-5): Full-suite default-order suite-health gate

- RED: any pre-completion full-suite pytest run in default alphabetical order reports failures while the carried header test or residuals remain — the gate target is unmet.
- GREEN: full-suite pytest run in default alphabetical order reports 52 passed, 0 failed (54 baseline minus 2 deleted; 49 previously passing plus 3 repaired).
- verify: full-suite pytest exit code + tests-run artifact per tests-run.yaml mandate; DB pre-synced via `bash scripts/sync_prod_to_local.sh` per the repo Regression Test Protocol.
- commit: none — verification-only item; tests-run artifact recorded.
- depends on: Items 1, 2, 3, and 4.

## Dependencies

| Reference | Relationship | Status |
|-----------|--------------|--------|
| #36 (`Brothertown-Language/snea-shoebox-editor`) | Surfacing issue — #36's pre-regression baseline and its diagnosis artifacts are the evidence base; this fix unblocks #36's regression sweep. No code-path coupling to #36's own SCs. | in progress on `feature/36-semantic-gloss-search-pgvector` (satisfied — no merge dependency; independent concern) |
| `tmp/issue-36/artifacts/baseline-failure-diagnosis.yaml` | Must be read before implementation — authoritative per-failure diagnosis (experiments A/B/C shapes define the RED/GREEN verification contracts). | present in `tmp/` (verified) |
| `tmp/issue-36/artifacts/pre-regression-baseline.yaml` | Must be read before implementation — baseline record (49 passed / 5 failed of 54 tests) defining the suite-health contract. | present in `tmp/` (verified) |
| Commits `85b9586`, `3f54ad3`, `907843d`, `5523299` | Git forensics grounding: `3f54ad3` (#1321) superseded the 2 deleted tests' assertions; `907843d` broke the `set_value` propagation path. | satisfied (merged on trunk tip `08c1e93`) |

## Traceability

| Requirement | SC(s) | Item(s) |
|-------------|-------|---------|
| R-1 (delete superseded ×2) | SC-2 | Item 2 |
| R-2 (contain carrier 2) | SC-1 | Item 1 |
| R-3 (contain carrier 1) | SC-3 | Item 3 |
| R-4 (rewrite stimulation) | SC-4 | Item 4 |
| R-5 (rewrite assertion) | SC-4 | Item 4 |
| R-6 (insert-only restore) | SC-1, SC-3 | Item 1, Item 3 |
| R-7 (product freeze) | SC-5 | Item 5 |
| R-8 (own-tests stay green) | SC-1, SC-3, SC-5 | Item 1, Item 3, Item 5 |

## Documentation Sources

| Source | Type | Location | Verification |
|--------|------|----------|-------------|
| Baseline failure diagnosis | code/local artifact | `tmp/issue-36/artifacts/baseline-failure-diagnosis.yaml` | read live this session; pairwise A/B/C experiments + DOM probes + git forensics |
| #36 pre-regression baseline | code/local artifact | `tmp/issue-36/artifacts/pre-regression-baseline.yaml` | read live this session; 49 passed / 5 failed of 54 collected tests |
| Stale-RED test file | code | `test/test_search_mode_ui_red.py` (UI assertions, mock block, method locations; 6 tests verified live) | direct file read, live session |
| Mock-leak carrier 1 | code | `test/test_filter_ux_red.py` (module-level `sys.modules` mutations; 4 tests) | direct file read, live session |
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
- **Intermediate suite states between items:** Item 1's gate runs while the search-mode file still collects 6 tests (3 known-stale RED remain failing); Item 2 removes the deletion pair from collection; Item 4 heals the header test. Each item's GREEN expectation scopes which failures are carried, so no intermediate state requires premature green.

**Failure modes:**
- **Restoring deletes a pre-existing real module:** containment MUST use insert-only semantics — revert/delete only entries the carrier itself inserted; never delete entries that existed before execution (decompose-output failure-mode analysis).
- **Containment breaks within-execution mocking:** `records()` inside the AppTest script needs the service mocks during its own script execution — containment restores at teardown/scope-exit, not during exec; the carrier files' surviving green tests are the invariant check.
- **Seeding overwritten by widget-state init:** if the seed lands after first `run()`, the test fails RED — order verified during implementation RED/GREEN.
- **Order-dependence regression masking:** any full-suite GREEN claim MUST come from the default alphabetical-order run (the reproduction mechanism), never from isolation-only runs (which reverse-order runs also pass — verified in diagnosis).
- **Item 1 GREEN misread as full-suite green:** the Item-1 order-pair run cannot report zero total failures before Items 2 and 4 land — its contract scopes zero failures to the migration file, with residuals confined to the named stale-RED set; a failure outside that set signals a containment defect.

**Concurrency:**
- None material — pytest in-process execution is single-threaded here; the sys.modules lifecycle is the only shared mutable state and is owned by the containment pattern (save/restore is deterministic, dict-iteration-order independent).

**Recovery:**
- If a containment pattern breaks a currently-passing carrier test (RED within GREEN run), the pattern is scoped further (per-execution save inside the script wrapper) rather than reverting product files — the C-1 freeze forbids product-side fixes for any repair failure.
- If the full-suite run still reports failures post-repair, the residual failures are triaged against the baseline diagnosis artifact as new defects (not silently absorbed) — out of this spec's scope.

## Change Control

| Date | Change | Reason | Authorized By |
|------|--------|--------|---------------|
| 2026-09-29 | Revised from 3 SCs to 5 atomic SCs with 1:1 SC↔item mapping; corrected Item-1 GREEN expectation to zero failures from `test_migration_backfill_search_entries.py` with residual stale-RED carried to Items 2/4; corrected suite arithmetic to the 52-test post-repair contract (49 previously passing plus 3 repaired; 2 of the 5 baseline failures deleted rather than repaired); added intermediate-suite-state edge case and a carry-forward failure-mode note. Requirements R-1 through R-8, scope, Not Included, and Documentation Sources preserved. | spec-creation validate gate FAIL ×3: (1) ordering contradiction — SC-1 GREEN required order-pair 0 total failures while `test_header_shows_mode_name_and_count` still fails until the rewrite item; (2) compound SCs — SC-1/SC-2/SC-3 each bundled 4+ independent verification targets via and/semicolon chains; (3) SC-3 arithmetic error — "49 + 5 = all green" counts the 2 deleted tests as repaired, but the post-repair suite is 52 tests. | spec-creation --task revise on issue #1388, per the validation findings dispatched by the spec-creation orchestrator |
| 2026-09-29 | Validation round-2 targeted edits: (A) corrected Item-1 RED line contract from "5 failed, 1 passed" to "5 failed, 5 passed" (10 tests collected in the order-pair run — 6 search-mode + 4 migration; consistent with the diagnosis artifact's experiment C: `C_searchmode_THEN_migration: 5 failed`). (B) corrected phantom symbol `RECORDS_TEST_SCRIPT` → `RECORDS_SCRIPT` in Item 1 and Item 3 GREEN lines (verified live: module-level script constant is `RECORDS_SCRIPT` at `test/test_search_mode_ui_red.py:10` and `test/test_filter_ux_red.py:12`; no `RECORDS_TEST_SCRIPT` exists in either file). (C) added the AGENTS.md Regression Test Protocol DB-sync precondition (`bash scripts/sync_prod_to_local.sh`) to SC-5's criterion and Item 5 verify line (advisory from completeness check, applied as SC-method note). Analytical artifacts directory restored from `tmp/1388/artifacts/` (10 artifacts) with the same finding-B symbol correction applied to 3 artifact lines (code-path-inventory.yaml, interface-compatibility.yaml, pre-spec-inspection.yaml) so restored evidence does not carry the phantom symbol. | spec-creation validate round-2 findings (2 targeted edits + artifact restore + advisory) | spec-creation --task revise on issue #1388, per the round-2 revision_reason dispatched by the spec-creation orchestrator |

---

🤖 Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)