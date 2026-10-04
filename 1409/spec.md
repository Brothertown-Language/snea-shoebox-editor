> **Full spec and artifacts: [`.issues/1409/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1409/)** — this issue is a condensed exec summary; the authoritative spec lives in the `issues-data` branch.
>
> **Local artifacts:** `.issues/1409/` — analysis artifacts, plan, audit findings

# Spec: Fix Streamlit dual-set widget warning on semantic threshold slider

## Intent and Executive Summary

1. **Problem Statement** — On the Records page sidebar, Streamlit emits the `SessionStateReinitializationWarning` dual-set warning for both `semantic_threshold_slider` and `semantic_threshold_number` whenever a saved `records/semantic_threshold` preference is present: the pre-instantiation block writes the widget keys via the Session State API while the widget calls also pass an explicit `value=` argument.
2. **Root Cause / Motivation** — The dual-set anti-pattern at `records.py` widget instantiation (pre-instantiation session-state writes to widget-bound keys combined with explicit `value=` arguments on `st.slider` and `st.number_input`) is Streamlit's documented invalid combination. The defect was not caught because the E2E fixture deletes saved preferences, so synthetic sessions never exercise the saved-preference branch and no test asserts warning absence. It must be solved now because the warning surfaces on every real user's Records page load with a saved preference.
3. **Approach Chosen** (final, implementation-verified at commit 3fa64ec) — Pre-instantiation seeding of both widget keys (`semantic_threshold_slider`, `semantic_threshold_number`) guarded to run once (only when the key is absent), PLUS a pre-instantiation resync-when-mismatched from the backing value (`st.session_state.semantic_threshold`, seeded from the saved preference or `CALIBRATED_FLOOR`) on every rerun; the explicit `value=` argument is REMOVED from both keyed widgets. The dual-set warning requires BOTH an API write to a widget key AND an explicit `value=` parameter on the same key (Streamlit `policies.py:87`: `default_value != None and is_new_state_value`) — with `value=` removed, zero warning fires even though session-state writes to the widget keys exist. The resync-when-mismatched write keeps the two coupled widgets in lockstep with the backing value on every rerun (Streamlit does not re-apply `value=` to keyed widgets on later runs), preserving SC-3a/SC-3b round-trip and rerun survival. Backing-value seeding, validation guard, on_change callbacks, and preference persistence are untouched.
4. **Alternatives Considered & Why Discarded** — (a) Suppress the warning via logging filters — rejected: masks the defect rather than removing it, and Streamlit documents the dual-set combination as incorrect. (b) Seed widget keys via session state once and remove `value=`, with no per-rerun resync (an intermediate implemented mechanism) — rejected based on live verification in Streamlit 1.54: a keyed widget without `value=` receives an API-written key value in the browser only on the run where the key was written; later reruns re-render from the widget default (0.0), so the seeded-once value is lost after the first run and the rerun race clobbers the saved preference through `on_change` (observed: a DB preference row was updated to 0.0 — a data-integrity hazard). (c) Remove ALL pre-instantiation session-state writes and keep `value=st.session_state.semantic_threshold` (an intermediate implemented mechanism) — rejected based on live verification in Streamlit 1.54: Streamlit does not re-apply `value=` to keyed widgets on later runs (it applies only at first instantiation of the key), so after first instantiation the two coupled widgets decouple from the backing value, breaking the SC-3a round-trip and SC-3b rerun survival. (d) Service-layer/preference-store changes — rejected: blast radius analysis shows the persistence layer is correct and unaffected.
5. **Key Design Decisions** (final, per commit 3fa64ec) — (a) Seeded-once + resync-when-mismatched with `value=` removed: the warning condition (Streamlit `policies.py:87`) fires only when `default_value != None` (an explicit `value=` was passed) AND the state value is new (API-written); removing `value=` from both widgets makes the first conjunct false, so no warning fires despite the session-state writes — tradeoff: none observed; the resync write on every rerun keeps both coupled widgets rendering the backing value, and first paint is driven by the seeded backing value (preference load / `CALIBRATED_FLOOR` fallback) with no race. (b) Backing value (`st.session_state.semantic_threshold`) semantics preserved exactly — tradeoff: none; this isolates the fix to widget-instantiation mechanics. (c) Behavioral Playwright evidence per the repo UI testing standard — tradeoff: slower than AppTest smoke checks, but user-visible-behavior claims require real-browser evidence. Preservation evidence for the final mechanism: 7/7 combined battery (SC-1a/SC-1b no-warning + saved render, SC-9 fresh default 0.93, SC-3a round-trip including DOM render of the edited value in BOTH coupled widgets, SC-3b rerun + full page reload survival).
6. **User Intent / Original Prompt** — Stakeholder-visible Streamlit warning on the Records page semantic threshold slider ("The widget with key 'semantic_threshold_slider' was created with a default value but also had its value set via the Session State API") reported via issue #1409; fix the warning without changing any user-visible threshold behavior.

## Not Included

- **Preference service / persistence layer changes** — verified unaffected by blast-radius analysis; only widget-instantiation mechanics change.
- **Calibration constant (`CALIBRATED_FLOOR`) changes** — the 0.93 calibrated default is correct per #1400 and is preserved.
- **Other frontend pages or other widget keys** — grep verified no other `src/` references to `semantic_threshold_slider` or `semantic_threshold_number`.
- **Unicode/linguistic text processing** — no interaction with linguistic data handling.

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method | Documentation Sources |
|----|-----------|---------------|---------------------|-----------------------|
| SC-1a | With a saved `records/semantic_threshold` preference present for the session user, the rendered Records page contains no Streamlit widget-state warning box (`SessionStateReinitializationWarning`, dual-set) for the semantic threshold widgets (`semantic_threshold_slider` and `semantic_threshold_number`). | behavioral | Playwright real-browser test against live app on :8501 (`SNEA_E2E=1`): seed the saved preference before page load, navigate to Records, assert the rendered page contains no Streamlit widget-state warning box for the semantic threshold widgets in captured console/page errors; screenshot artifact under `tmp/<issue>/artifacts/`. | Streamlit session-state docs (docs.streamlit.io); `docs/development/ui_testing_standard.md`; `test/ui/test_sc9_ui_threshold_default_red.py` |
| SC-1b | With a saved `records/semantic_threshold` preference present for the session user, the semantic threshold slider renders the saved value. | behavioral | Same Playwright test as SC-1a: assert the slider's rendered value equals the seeded saved preference; screenshot artifact under `tmp/<issue>/artifacts/`. | Streamlit session-state docs (docs.streamlit.io); `docs/development/ui_testing_standard.md`; `test/ui/test_sc9_ui_threshold_default_red.py` |
| SC-2 | With no saved preference, the semantic threshold slider defaults to the calibrated floor 0.93. | behavioral | Existing SC-9 fresh-default Playwright test in `test/ui/test_sc9_ui_threshold_default_red.py` establishes the no-preference precondition and asserts 0.93 rendering; MUST still pass post-change. | `test/ui/test_sc9_ui_threshold_default_red.py`; `src/frontend/pages/records.py` |
| SC-3a | A saved user override round-trips: the user edits the threshold, the edit persists to `records/semantic_threshold`, and the rendered value equals the edited value after persistence. | behavioral | Existing SC-2 DOM round-trip Playwright test (edit → persist → render) still passes post-change. | `test/ui/test_sc9_ui_threshold_default_red.py`; `src/frontend/pages/records.py` |
| SC-3b | The saved threshold value survives a page rerun/navigation: after a rerun, the rendered value equals the saved value and does not reset to the default. | behavioral | Playwright rerun/navigation assertion (saved value survives a page rerun without resetting to default), added unconditionally to the Playwright suite. | `test/ui/test_sc9_ui_threshold_default_red.py`; `src/frontend/pages/records.py` |
| SC-4 | Full pytest suite passes with zero new failures relative to pre-change baseline. | behavioral | `uv run pytest test/` baseline comparison before/after change; `SNEA_E2E=1` run for the UI standard-of-record tier when live app is up. | `pyproject.toml`; `test/` suite |

## Requirements

1. R-1. The Records page widget instantiation block SHALL pre-instantiate the widget-bound keys (`semantic_threshold_slider`, `semantic_threshold_number`) with guarded once-only seeding (write only when the key is absent) PLUS a pre-instantiation resync-when-mismatched write from the backing value (`st.session_state.semantic_threshold`) on every rerun, and the keyed widget calls SHALL NOT pass an explicit `value=` argument — with `value=` removed, Streamlit's dual-set warning condition (`policies.py:87`: `default_value != None and is_new_state_value`) is never satisfied.
2. R-2. The system SHALL preserve the #1400 backing-value contract: when no saved preference exists, `st.session_state.semantic_threshold` is seeded from `CALIBRATED_FLOOR` (0.93); when a saved preference exists and parses in-range, it is seeded from the saved value.
3. R-3. The system SHALL preserve `_validate_threshold()` invalid-edit rejection running pre-instantiation, with widgets rendering the last accepted value on rejection.
4. R-4. The `on_change` callbacks SHALL continue to propagate widget → backing value and persist preferences for logged-in users unchanged.
5. R-5. The rendered threshold values (default 0.93 when no preference; saved override when present) SHALL be identical to pre-change behavior across first load, rerun, and page navigation.
6. R-6. A Playwright test SHALL assert dual-set warning absence with a saved preference present, using a dedicated fixture that is not defeated by `_delete_saved_threshold_preferences()` deletion of user preference rows.

## Items

### Item 1 (SC-1a): Remove the dual-set warning under saved-preference load

- RED: Playwright real-browser test that seeds a saved `records/semantic_threshold` preference (via a dedicated fixture that survives `_delete_saved_threshold_preferences`), loads Records, and asserts the rendered page contains no Streamlit widget-state warning box for the semantic threshold widgets — fails against the current code.
- GREEN: Restructure the Records page widget block (`records.py`) to the final mechanism (commit 3fa64ec): pre-instantiation seeding of both widget keys (`semantic_threshold_slider`, `semantic_threshold_number`) guarded to run once (only when absent), a pre-instantiation resync-when-mismatched write from the backing value on every rerun, and the explicit `value=` argument REMOVED from both `st.slider` and `st.number_input`. The warning condition (`policies.py:87`) requires both an API write and a `value=` parameter — with `value=` removed, zero warning fires even though session-state writes exist, and the seeded/resynced backing value drives first paint.
- verify: The SC-1a Playwright test passes (live app on :8501, `SNEA_E2E=1`); screenshot artifact captured.
- commit: Widget block change + new test in one commit.

### Item 2 (SC-1b): Render the saved value under saved-preference load

- RED: Extend the SC-1a Playwright test to assert the slider renders the seeded saved value; this assertion passes against pre-change code (preservation gate) and is recorded as baseline.
- GREEN: No production change beyond Item 1; fix any regression the restructure introduced to saved-value rendering.
- verify: Slider renders the saved value with a saved preference present; screenshot artifact captured.
- commit: Test assertion + any regression fix in one commit.

### Item 3 (SC-2): Preserve calibrated default rendering

- RED: Run the existing SC-9 fresh-default Playwright test against the restructured widget block — must already pass post-change; it is a preservation gate, so the RED step is a baseline run against pre-change code to record the passing state.
- GREEN: No production change beyond Item 1; fix any regression the restructure introduced to fresh-default seeding.
- verify: Fresh-default test asserts 0.93 rendering with no-preference precondition.
- commit: Any regression fix included in the Item 3 commit.

### Item 4 (SC-3a): Preserve saved-override round-trip

- RED: Baseline run of the existing DOM round-trip Playwright test (edit → persist → render) against pre-change code to record the passing state.
- GREEN: Ensure the on_change callback → backing value → persistence flow is intact after the widget-block restructure; the rendered value equals the edited value after persistence.
- verify: Round-trip test (edit → persist → render) passes post-change.
- commit: Test additions + any needed adjustment in one commit.

### Item 5 (SC-3b): Preserve rerun survival of the saved value

- RED: Add a rerun/navigation Playwright assertion (after a page rerun, the rendered value equals the saved value and does not reset to the default); unconditionally included in the suite.
- GREEN: Ensure the widget-block change preserves rerun stability — each rerun re-seeds/resyncs the widget keys from the backing session-state value (`st.session_state.semantic_threshold`) via the pre-instantiation resync-when-mismatched write (Streamlit does not re-apply `value=` to keyed widgets on later runs, so the resync write is what keeps the widgets coupled to the backing value), so the saved value survives rerun/navigation without resetting to the default.
- verify: Rerun assertion passes post-change.
- commit: Test addition + any needed adjustment in one commit.

### Item 6 (SC-4): Full suite regression gate

- RED: Record pre-change baseline of `uv run pytest test/` pass/fail set.
- GREEN: Post-change, run the full suite; zero new failures.
- verify: Baseline comparison before/after.
- commit: No production change; verification item committed as test evidence.

## Dependencies

- **#1385 (`_validate_threshold` guard, SC-3a/SC-3b)** — must remain in place; validation semantics this spec preserves. Status: merged.
- **#1400 (calibrated default 0.93 contract)** — must remain in place; backing-value default semantics this spec preserves. Status: merged.
- **`docs/development/ui_testing_standard.md`** — must be read before writing/running the Playwright evidence. Status: available.
- **`test/ui/test_sc9_ui_threshold_default_red.py`** — reuse as SC-2/SC-3a/SC-3b gates and fixture reference. Status: available.

## Traceability

| Requirement | SC(s) | Item(s) |
|-------------|-------|---------|
| R-1 | SC-1a | Item 1 |
| R-2 | SC-1b, SC-2 | Item 2, Item 3 |
| R-3 | SC-3a, SC-3b | Item 4, Item 5 |
| R-4 | SC-3a | Item 4 |
| R-5 | SC-1b, SC-2, SC-3a, SC-3b | Item 2, Item 3, Item 4, Item 5 |
| R-6 | SC-1a | Item 1 |

## Documentation Sources

| Source | Type | Location | Verification |
|--------|------|----------|-------------|
| Streamlit session-state widget-key contract | doc/code | Streamlit docs (Session State widget-key semantics) + `src/frontend/pages/records.py` widget block | Read of `records.py` instantiation block during pre-spec inspection |
| Repo UI testing standard | doc | `docs/development/ui_testing_standard.md` | Read during pre-spec inspection |
| Existing E2E tests / fixtures | code | `test/ui/test_sc9_ui_threshold_default_red.py` | Read during pre-spec inspection |
| Backing-value consumers | code | `records.py` search-query consumers and caption, `on_change` callbacks | Grep + read during pre-spec inspection |

## Enforcement Gate

> **Enforcement gate:** All success criteria MUST pass before this spec is considered complete. Partial implementation is not permitted.

## Cost Frame

Cost is measured in defect-discovery-latency, not tool calls. Correctness is the only metric.

- SC-1a/SC-1b: Running the saved-preference Playwright warning-absence and saved-value-rendering tests costs minutes of live-app execution. Skipping means the dual-set warning ships on every real user's Records page load and surfaces as a support report instead of a CI failure — the rework pipeline (diagnose, fix, redeploy, re-verify) costs orders of magnitude more.
- SC-2: Re-running the existing fresh-default Playwright test costs minutes. Skipping means a regression to the 0.93 default ships silently — a wrong calibration default propagates into every query users run, discovered only when search results stop matching expectations.
- SC-3a/SC-3b: Running the round-trip and rerun Playwright assertions costs minutes. Skipping means saved user overrides silently reset to defaults on rerun — user trust damage discovered downstream, unrecoverable without a support cycle.
- SC-4: Running the full pytest suite costs minutes of execution. Skipping means any regression in adjacent behavior reaches production before the next scheduled suite run — weeks of discovery latency instead of minutes.

## Edge Cases

- **Input boundaries:** Saved preference values that are non-numeric, unparseable, or out-of-range — `_validate_threshold()` restores the last accepted value pre-instantiation (R-3); the keyed widget calls must still not pass `value=` in that path (the warning condition's `value=` conjunct must remain unsatisfied).
- **State transitions:** First load (no preference → 0.93; saved → saved value — both driven by the guarded once-only seeding of the widget keys from the backing session-state value, with `value=` removed), user edit (callback propagates + persists), rerun/navigation (pre-instantiation resync-when-mismatched write re-couples the widget keys to the backing value on every rerun — Streamlit does not re-apply `value=` to keyed widgets, so the resync is the coupling mechanism; no reset-to-default race), invalid edit rejected (last accepted value rendered). All covered in state-analysis.
- **Failure modes:** PreferenceService read failure or missing preference row — falls back to `CALIBRATED_FLOOR` per the existing seeding contract (preserved, unchanged). Preference deletion between page loads — next session re-seeds from default.
- **Concurrency:** Multiple sessions are independent (per-session `st.session_state`); no shared-state race introduced by the fix.
- **Recovery:** If the restructure accidentally breaks callback propagation, SC-3a's round-trip test catches it at the pre-commit gate (break, not death spiral).

---

## Change Control

| Date | Change | Reason | Authorized By |
|------|--------|--------|---------------|
| 2026-10-03 | Split SC-1 into SC-1a (no Streamlit widget-state warning box for the semantic threshold widgets — single binary assertion covering both widgets) and SC-1b (slider renders the saved value with a saved preference present); split SC-3 into SC-3a (override round-trip: edit → persist → render) and SC-3b (rerun survival — unconditional assertion, no "if not already present" conditional); removed hedging language ("honored", conditional assertions); updated Items to 1:1 SC:ITEM (6 items), Traceability, Cost Frame, Dependencies, and Edge Cases references accordingly. | Validation findings: compound-SC pattern in SC-1 and SC-3; hedging language in SC-3 and sc-summary. | Validation gate revision (spec-creation revise task) |
| 2026-10-03 | Approach mechanism change (SC contracts SC-1a..SC-4 unchanged): replaced the originally prescribed mechanism (seed widget keys via session state once, remove `value=`) with: remove ALL pre-instantiation session-state writes to the widget keys and keep `value=st.session_state.semantic_threshold` on both widgets. Updated Intent §3 (Approach Chosen), §4 (Alternatives — former approach now rejected with live evidence), §5 (Key Design Decisions), R-1, Item 1 GREEN, Item 5 GREEN, and Edge Cases state transitions. | Implementation-verified mechanism change: in Streamlit 1.54, the seeded-key approach was proven defective — with a keyed widget and no `value=`, the value reaches the browser only on the run where the key was API-written; subsequent client reruns re-render from the default (0.0), and the rerun race clobbers the saved preference through `on_change` (observed: DB preference row updated to 0.0 — data-integrity hazard). The implemented mechanism relies on Streamlit's dual-set warning condition (policies.py:87) requiring both an API write to a widget key AND an explicit `value=` on the same key; zero API writes to widget keys means the condition is never satisfied, and the backing value (preference load / `CALIBRATED_FLOOR` fallback) drives first paint with no race. | Implementation-verified revision (spec-creation revise task, developer-directed) |
| 2026-10-03 | Approach mechanism change to FINAL implementation-verified mechanism (SC contracts SC-1a..SC-4 unchanged): replaced the intermediate mechanism (remove ALL pre-instantiation writes + keep `value=`) with: pre-instantiation seeding of both widget keys (guarded once, only when absent) PLUS a pre-instantiation resync-when-mismatched write from the backing value on every rerun, with the explicit `value=` parameter REMOVED from both widgets. Updated Intent §3 (Approach Chosen), §4 (Alternatives — BOTH intermediate mechanisms now rejected with live evidence), §5 (Key Design Decisions), R-1, Item 1 GREEN, Item 5 GREEN, and Edge Cases (input boundaries, state transitions). | Implementation-verified mechanism change (commit 3fa64ec): live verification proved BOTH earlier mechanisms wrong. (1) Seeded-once-without-`value=` loses the value after the first run — Streamlit 1.54 sends API-written key values to the browser only on the run where the key was written; later reruns re-render from the widget default 0.0. (2) No-seeding-with-`value=` decouples the two coupled widgets after first instantiation — Streamlit does not re-apply `value=` to keyed widgets on later runs, breaking SC-3a/SC-3b round-trip and rerun survival. The FINAL mechanism matches the spec's original Key Design Decision (a): the dual-set warning requires BOTH an API write AND a `value=` parameter (Streamlit policies.py:87: `default_value != None and is_new_state_value`) — with `value=` removed, zero warning fires even though session-state writes exist; the per-rerun resync keeps the widgets coupled to the backing value. Preservation evidence: 7/7 combined battery (SC-1a/1b no-warning + saved render, SC-9 fresh default 0.93, SC-3a round-trip incl. DOM render of edited value in BOTH coupled widgets, SC-3b rerun + full page reload survival). | Implementation-verified revision (spec-creation revise task, developer-directed) |

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
