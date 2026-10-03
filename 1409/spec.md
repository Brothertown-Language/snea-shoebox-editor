> **Full spec and artifacts: [`.issues/1409/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1409/)** — this issue is a condensed exec summary; the authoritative spec lives in the `issues-data` branch.
>
> **Local artifacts:** `.issues/1409/` — analysis artifacts, plan, audit findings

# Spec: Fix Streamlit dual-set widget warning on semantic threshold slider

## Intent and Executive Summary

1. **Problem Statement** — On the Records page sidebar, Streamlit emits the `SessionStateReinitializationWarning` dual-set warning for both `semantic_threshold_slider` and `semantic_threshold_number` whenever a saved `records/semantic_threshold` preference is present: the pre-instantiation block writes the widget keys via the Session State API while the widget calls also pass an explicit `value=` argument.
2. **Root Cause / Motivation** — The dual-set anti-pattern at `records.py` widget instantiation (pre-instantiation session-state writes to widget-bound keys combined with explicit `value=` arguments on `st.slider` and `st.number_input`) is Streamlit's documented invalid combination. The defect was not caught because the E2E fixture deletes saved preferences, so synthetic sessions never exercise the saved-preference branch and no test asserts warning absence. It must be solved now because the warning surfaces on every real user's Records page load with a saved preference.
3. **Approach Chosen** — Restructure the widget instantiation block so widget-bound keys are written to session state exactly once (at/before first instantiation only) and the explicit `value=` arguments are removed from both keyed widgets; widget values then flow solely from session state. Backing-value seeding, validation guard, on_change callbacks, and preference persistence are untouched.
4. **Alternatives Considered & Why Discarded** — (a) Suppress the warning via logging filters — rejected: masks the defect rather than removing it, and Streamlit documents the dual-set combination as incorrect. (b) Drop the pre-instantiation writes and keep `value=` — rejected: `value=` would then override saved preferences on reruns, breaking saved-override behavior (SC-3). (c) Service-layer/preference-store changes — rejected: blast radius analysis shows the persistence layer is correct and unaffected.
5. **Key Design Decisions** — (a) Single-source-of-value: widget keys are seeded by session state only; explicit `value=` is removed — tradeoff: slightly more seeding code in exchange for eliminating the warning class entirely. (b) Backing value (`st.session_state.semantic_threshold`) semantics preserved exactly — tradeoff: none; this isolates the fix to widget-instantiation mechanics. (c) Behavioral Playwright evidence per the repo UI testing standard — tradeoff: slower than AppTest smoke checks, but user-visible-behavior claims require real-browser evidence.
6. **User Intent / Original Prompt** — Stakeholder-visible Streamlit warning on the Records page semantic threshold slider ("The widget with key 'semantic_threshold_slider' was created with a default value but also had its value set via the Session State API") reported via issue #1409; fix the warning without changing any user-visible threshold behavior.

## Not Included

- **Preference service / persistence layer changes** — verified unaffected by blast-radius analysis; only widget-instantiation mechanics change.
- **Calibration constant (`CALIBRATED_FLOOR`) changes** — the 0.93 calibrated default is correct per #1400 and is preserved.
- **Other frontend pages or other widget keys** — grep verified no other `src/` references to `semantic_threshold_slider` or `semantic_threshold_number`.
- **Unicode/linguistic text processing** — no interaction with linguistic data handling.

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method | Documentation Sources |
|----|-----------|---------------|---------------------|-----------------------|
| SC-1 | With a saved `records/semantic_threshold` preference present for the session user, the Records page renders with no Streamlit `SessionStateReinitializationWarning` (dual-set warning) for either `semantic_threshold_slider` or `semantic_threshold_number`. | behavioral | Playwright real-browser test against live app on :8501 (`SNEA_E2E=1`): seed the saved preference before page load, navigate to Records, assert no dual-set warning in captured console/page errors and widget renders the saved value; screenshot artifact under `tmp/<issue>/artifacts/`. | Streamlit session-state docs (docs.streamlit.io); `docs/development/ui_testing_standard.md`; `test/ui/test_sc9_ui_threshold_default_red.py` |
| SC-2 | With no saved preference, the semantic threshold slider defaults to the calibrated floor 0.93. | behavioral | Existing SC-9 fresh-default Playwright test in `test/ui/test_sc9_ui_threshold_default_red.py` establishes the no-preference precondition and asserts 0.93 rendering; MUST still pass post-change. | `test/ui/test_sc9_ui_threshold_default_red.py`; `src/frontend/pages/records.py` |
| SC-3 | Saved user overrides are preserved and honored after the change: an override value round-trips (edit → persist → render) and survives page reruns without resetting to default. | behavioral | Existing SC-2 DOM round-trip Playwright test (edit→persist→render) still passes; add rerun/navigation assertion (saved value survives a page rerun) if not already present. | `test/ui/test_sc9_ui_threshold_default_red.py`; `src/frontend/pages/records.py` |
| SC-4 | Full pytest suite passes with zero new failures relative to pre-change baseline. | behavioral | `uv run pytest test/` baseline comparison before/after change; `SNEA_E2E=1` run for the UI standard-of-record tier when live app is up. | `pyproject.toml`; `test/` suite |

## Requirements

1. R-1. The Records page widget instantiation block SHALL write widget-bound keys (`semantic_threshold_slider`, `semantic_threshold_number`) to session state at most once per session (at/before first instantiation) and SHALL NOT combine a pre-seeded widget key with an explicit `value=` argument on the keyed widget call.
2. R-2. The system SHALL preserve the #1400 backing-value contract: when no saved preference exists, `st.session_state.semantic_threshold` is seeded from `CALIBRATED_FLOOR` (0.93); when a saved preference exists and parses in-range, it is seeded from the saved value.
3. R-3. The system SHALL preserve `_validate_threshold()` invalid-edit rejection running pre-instantiation, with widgets rendering the last accepted value on rejection.
4. R-4. The `on_change` callbacks SHALL continue to propagate widget → backing value and persist preferences for logged-in users unchanged.
5. R-5. The rendered threshold values (default 0.93 when no preference; saved override when present) SHALL be identical to pre-change behavior across first load, rerun, and page navigation.
6. R-6. A Playwright test SHALL assert dual-set warning absence with a saved preference present, using a dedicated fixture that is not defeated by `_delete_saved_threshold_preferences()` deletion of user preference rows.

## Items

### Item 1 (SC-1): Remove the dual-set warning under saved-preference load

- RED: Playwright real-browser test that seeds a saved `records/semantic_threshold` preference (via a dedicated fixture that survives `_delete_saved_threshold_preferences`), loads Records, and asserts no `SessionStateReinitializationWarning` for either widget key — fails against the current code.
- GREEN: Restructure the widget instantiation block in the Records page (`records.py` widget block): write widget-bound keys to session state exactly once at/before first instantiation and remove the explicit `value=` arguments from `st.slider` and `st.number_input`; remove the redundant unconditional pre-instantiation re-sync writes.
- verify: The SC-1 Playwright test passes (live app on :8501, `SNEA_E2E=1`); screenshot artifact captured.
- commit: Widget block change + new test in one commit.

### Item 2 (SC-2): Preserve calibrated default rendering

- RED: Run the existing SC-9 fresh-default Playwright test against the restructured widget block — must already pass post-change; it is a preservation gate, so the RED step is a baseline run against pre-change code to record the passing state.
- GREEN: No production change beyond Item 1; fix any regression the restructure introduced to fresh-default seeding.
- verify: Fresh-default test asserts 0.93 rendering with no-preference precondition.
- commit: Any regression fix included in the Item 2 commit.

### Item 3 (SC-3): Preserve saved-override round-trip and rerun stability

- RED: Baseline run of the existing DOM round-trip Playwright test; add a rerun/navigation assertion (saved value survives page rerun without resetting to default) that fails against pre-change code only if behavior was already broken — otherwise it serves as the post-change preservation gate.
- GREEN: Ensure on_change callback → backing value → persistence flow is intact after the widget-block restructure.
- verify: Round-trip test (edit → persist → render) and rerun assertion pass.
- commit: Test additions + any needed adjustment in one commit.

### Item 4 (SC-4): Full suite regression gate

- RED: Record pre-change baseline of `uv run pytest test/` pass/fail set.
- GREEN: Post-change, run the full suite; zero new failures.
- verify: Baseline comparison before/after.
- commit: No production change; verification item committed as test evidence.

## Dependencies

- **#1385 (`_validate_threshold` guard, SC-3)** — must remain in place; validation semantics this spec preserves. Status: merged.
- **#1400 (calibrated default 0.93 contract)** — must remain in place; backing-value default semantics this spec preserves. Status: merged.
- **`docs/development/ui_testing_standard.md`** — must be read before writing/running the Playwright evidence. Status: available.
- **`test/ui/test_sc9_ui_threshold_default_red.py`** — reuse as SC-2/SC-3 gates and fixture reference. Status: available.

## Traceability

| Requirement | SC(s) | Item(s) |
|-------------|-------|---------|
| R-1 | SC-1 | Item 1 |
| R-2 | SC-2, SC-3 | Item 2, Item 3 |
| R-3 | SC-3 | Item 3 |
| R-4 | SC-3 | Item 3 |
| R-5 | SC-2, SC-3 | Item 2, Item 3 |
| R-6 | SC-1 | Item 1 |

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

- SC-1: Running the saved-preference Playwright warning-absence test costs minutes of live-app execution. Skipping means the dual-set warning ships on every real user's Records page load and surfaces as a support report instead of a CI failure — the rework pipeline (diagnose, fix, redeploy, re-verify) costs orders of magnitude more.
- SC-2: Re-running the existing fresh-default Playwright test costs minutes. Skipping means a regression to the 0.93 default ships silently — a wrong calibration default propagates into every query users run, discovered only when search results stop matching expectations.
- SC-3: Running the round-trip and rerun Playwright assertions costs minutes. Skipping means saved user overrides silently reset to defaults on rerun — user trust damage discovered downstream, unrecoverable without a support cycle.
- SC-4: Running the full pytest suite costs minutes of execution. Skipping means any regression in adjacent behavior reaches production before the next scheduled suite run — weeks of discovery latency instead of minutes.

## Edge Cases

- **Input boundaries:** Saved preference values that are non-numeric, unparseable, or out-of-range — `_validate_threshold()` restores the last accepted value pre-instantiation (R-3); the widget keys must still not be dual-set in that path.
- **State transitions:** First load (no preference → 0.93; saved → saved value), user edit (callback propagates + persists), rerun/navigation (no re-seeding writes; widgets read existing session-state values), invalid edit rejected (last accepted value rendered). All covered in state-analysis.
- **Failure modes:** PreferenceService read failure or missing preference row — falls back to `CALIBRATED_FLOOR` per the existing seeding contract (preserved, unchanged). Preference deletion between page loads — next session re-seeds from default.
- **Concurrency:** Multiple sessions are independent (per-session `st.session_state`); no shared-state race introduced by the fix.
- **Recovery:** If the restructure accidentally breaks callback propagation, SC-3's round-trip test catches it at the pre-commit gate (break, not death spiral).

---

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
