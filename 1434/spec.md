> Full spec: this issue body (remote spec). Plan artifacts will be created at https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/1434/ when this enters its plan cycle.

## Problem
`test/ui/test_mdf_reference_e2e.py::test_split_independent_scrolling_on_navigation` is flaky — it fails intermittently (~50% of repeated single-test runs; 2 failures in 4 runs observed). The rail's scroll position reads 0 immediately after the test sets `el.scrollTop = el.scrollHeight` and waits 400 ms, so the `s0 > 400` assertion fires. Filed 2026-10-11 during the #1431/#1433 PR cycle as the required disposition for a red-in-history suite run; that PR cycle reruns to green and does not depend on this test's flake.

Evidence (recorded in the issue filing, 2026-10-11):
- Reproduced on `main` at 1be2185 with the #1431/#1433 feature work stashed: 2 failures in 4 runs — the flake is pre-existing, not caused by that change.
- Also intermittent with the change applied (passes and fails across repeated single-test runs).

Triage (2026-10-11, grounded in both sides of the race):
- The test asserts inside a non-quiescent window. `_open_mdf_page()` returns as soon as the page body text renders; Streamlit's render sequence can still be in flight. The test immediately sets the rail's `scrollTop` to `scrollHeight` and reads it back after a single fixed 400 ms sleep (`test_split_independent_scrolling_on_navigation`, lines 764-767).
- A rerun that lands between the set and the read replaces the rail element: the fresh element starts at `scrollTop` 0, so the read-back returns 0. The app's rail-scroll preservation (`restoreRailScroll`, `src/frontend/pages/mdf_reference.py:719-729`) cannot rescue the position — it re-applies only a session-stored value greater than 40 px, and the scroll listener commits the test's new position to session storage only after a 120 ms debounce (`mdf_reference.py:710-716`), which a replacement within that window preempts.

Root cause: test-side — the scroll-establishment window is not quiescence-gated, so the read-back races the rerun. The app-side preservation behavior is #1379's design, works as intended, and is not defective; the flake reproduces on unmodified `main`.

## Design direction (developer-stated, 2026-10-11)
The issue disposition states two fix directions: await script-idle before the scroll assertion, or retry-once on scroll reset.

Chosen approach — closed-loop, reset-triggered scroll establishment. A Streamlit rerun has no public script-idle signal a test can await (reruns arrive over the websocket; they are not script-load events, and the running-status widget is not reliably present for the post-first-paint render that produces the race), so a script-idle wait would key on a proxy signal. The race's own observable — the read-back reset — is the deterministic signal instead: set the rail scroll, wait on a stability condition observed on the rail itself (the set position persisting on the same DOM node across a probe window), read back, and on an observed reset re-establish the scroll and repeat, bounded. The retry bound and the stability-window mechanics are plan decisions; the required properties are normative in SC-2. The navigation-side 1500 ms settle stays as-is: it covers the app's bounded restore loop (~840 ms) and is not part of the reported flake.

Rejected alternative — retry-once on scroll reset with no stability gate: re-setting blind re-enters the same race; without an observed-stability condition the attempt sequence degenerates into repeated blind windows, and "once" leaves residual flake whenever more than one rerun lands in the window.

## Requirements
- **SC-1 (behavioral; the reported flake):** `pytest test/ui/test_mdf_reference_e2e.py::test_split_independent_scrolling_on_navigation` passes 10 consecutive single-test invocations against the live app (`SNEA_E2E=1`, app on :8501). This is the determinism bar: the recorded flake rate was 2 failures in 4 runs, so 10 consecutive green runs demonstrate the race is gone, not merely deferred.
- **SC-2 (structural; the race is removed, not suppressed):** the test's scroll-establishment sequence contains no fixed sleep between the scroll set and the read-back; the read-back follows a stability condition observed on the rail (the set position persisting across a probe window); an observed reset (a read-back that does not show the set position) triggers a bounded re-establishment — at most 2 re-sets after the initial attempt; the `s0 > 400` assertion fires only on a read-back that observed the set position persist. Exhausting the bound fails the test loudly.
- **SC-3 (structural; contract preserved):** the test's page-contract assertions are unchanged in strength after the fix — the rail-is-its-own-scroll-container check (`s0 > 400`), the rail-scroll-preservation check (`abs(s1 - s0) < 60`), and the detail-lands-at-top check (`dtop < 10`) remain present with the same thresholds; stabilization must not weaken what the test proves (the 2026-10-06 developer layout directive the test verifies).
- **Unchanged by this spec:** the app-side scroll preservation (`restoreRailScroll` and the 120 ms scroll-listener debounce), the page's split-pane behavior, and the sibling split tests (`test_split_drag_resizes_rail_and_persists_across_rerun`, `test_split_deeplink_lands_with_detail_at_top`, `test_split_hide_show_rail_persists_state`) — none is reported flaky.

## Verification instruments
- **SC-1:** executed runs — 10 consecutive `uv run pytest test/ui/test_mdf_reference_e2e.py::test_split_independent_scrolling_on_navigation` invocations against the live app, all green; per the regression protocol the local database is re-synced from production (`bash scripts/sync_prod_to_local.sh`) before the cycle, and the runs happen on the feature branch under test. Run outputs are recorded under `tmp/1434/artifacts/`.
- **SC-2, SC-3:** fact-decidable code inspection — the test file's diff shows the closed-loop establishment sequence (no fixed sleep before the read-back, stability-gated, bounded at 2 re-sets) and the three contract assertions present with unchanged thresholds.

## Out of scope
- App-side changes — `restoreRailScroll`, the scroll listener, the debounce interval, and any `mdf_reference.py` rendering or scroll behavior.
- The other split-pane tests and their settle waits — not reported flaky; the 1500 ms navigation-side settle in the targeted test stays.
- Suite-level flake machinery (pytest rerun plugins, CI retry policies) — the fix is deterministic establishment, not masking.
- Any change to what the test verifies — the split-pane contract of the 2026-10-06 layout directive.

## Impact
- **Scope:** one test function in `test/ui/test_mdf_reference_e2e.py`; no application code, no data, no dependencies.
- **Risk:** a stability condition keyed too narrowly could mask a genuine regression in rail scrolling — mitigated by SC-3 (the contract assertions keep their thresholds) and SC-2 (the establishment loop fails loudly at its bound rather than absorbing resets).
- **Test impact:** the targeted test's runtime gains the probe windows (seconds); the suite's other tests are untouched.

🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
