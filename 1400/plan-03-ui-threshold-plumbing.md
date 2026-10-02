# Phase 3 — UI threshold plumbing — default parity and override preservation

**Concern:** ui plumbing

**Files:**
- `src/frontend/pages/records.py` — `st.session_state.semantic_threshold` default literals and override passthrough
- `test/ui/test_semantic_search_ui_flow_e2e.py` — Playwright evidence for SC-9/SC-10

**SCs:** SC-9, SC-10

**Dependencies:** Phase 2 (seam default-floor semantics published)

**Entry Conditions:**
- Phase 2 complete: seam default floor engaged at `threshold=None`; below-floor outcome shape stable
- Phase 2 VbC passed; all Phase 2 commits landed
- Playwright auth state available — if missing, run the one-time OAuth login procedure per `docs/development/ui_testing_standard.md` (HEADLESS=False window; agents never fabricate auth state)

**Exit Conditions:**
- Fresh-session `st.session_state.semantic_threshold` default equals the published calibrated floor within ±0.01 (key name, [0.0, 1.0] guard, and PreferenceService authority preserved)
- A user override in the UI threshold control reaches `search_semantic()` unchanged — never silently replaced by the default
- Playwright real-browser evidence captured; E2E skips (no `SNEA_E2E=1` / app not on :8501) reported as skipped, never as PASS

**Code Path Coverage:**
- SC-9: `src/frontend/pages/records.py` — `st.session_state.semantic_threshold` initialization; default currently hardcoded "0.80" with PreferenceService fallback 0.80; sync the 0.80 default literals to the published calibrated floor
- SC-10: `src/frontend/pages/records.py` — threshold widget → `search_semantic(threshold=...)`; `_validate_threshold` guard rejects non-numeric / out-of-range edits; override value must flow to the seam unchanged

**Cross-Cutting SCs:**
- SC-9 spans calibration and ui plumbing concerns — the UI default must equal the published calibration constant within ±0.01 (parity between the calibration concern and the UI concern)

**Interface Boundaries:**
- `st.session_state['semantic_threshold']` — key PRESERVED, default value changes
- `PreferenceService.get_preference(user_email, 'records', 'semantic_threshold', default)` — PRESERVED; saved user preferences remain authoritative over the default; the default literal changes from 0.80 to the calibrated floor; no schema change
- UI → seam boundary: `search_semantic(threshold=st.session_state.semantic_threshold)` — override passthrough verified end-to-end
- UI threshold float in [0.0, 1.0]; persisted as string preference; out-of-range rejected by the guard

**State Transitions:**
- `semantic_threshold` initialization: 0.80 → published calibrated floor (fresh session); saved preferences still trump the default
- User override → override holds for the session/query call (prior behavior unchanged, now Playwright-verified — the default must not silently replace an explicit UI override)

**Cost frame:** Running the Playwright live-app checks costs minutes of browser-session execution time plus auth-state setup. Skipping live-browser evidence for the parity and override SCs costs a silent UI/seam disagreement shipping to production — user-visible behavior contradicting the calibration — discovered by users, not tests, at 100×–1000× the discovery-latency cost.

---

## Step-by-step

### Item 10 — SC-9: UI default equals the published floor

- [ ] 48. **RED (**task-card**).** Dispatch the red task from test-driven-development: write a failing Playwright/AppTest-standard check asserting `st.session_state.semantic_threshold` default equals the published calibrated floor within ±0.01 on a fresh session. The check FAILS because the default is still 0.80. **→ SC-9**
- [ ] 49. **GREEN (**task-card**).** Dispatch the green task from test-driven-development: sync the 0.80 default literals in the `semantic_threshold` initialization block to the published calibrated floor; keep the session-state key name, the [0.0, 1.0] guard, and PreferenceService authority. Minimum change only. **→ SC-9**
- [ ] 50. **Post-regression (**task-card**).** Dispatch the phase-4 task from test-driven-development: existing UI/seam tests and preference-handling tests unaffected. **→ non-regression for SC-9**
- [ ] 51. **Verify (**task-card**).** Dispatch the verify task from verification-before-completion: verify parity within ±0.01 with live-browser evidence per the ui testing standard (AppTest smoke acceptable only as auxiliary; skips reported as skipped). **→ SC-9**
- [ ] 52. **Commit (**direct**).** Stage and commit test + implementation together. **→ SC-9**

### Item 11 — SC-10: UI override preserved through to the seam

- [ ] 53. **RED (**task-card**).** Dispatch the red task from test-driven-development: write a failing Playwright test asserting a user override in the UI threshold control reaches `search_semantic()` and is not silently replaced by the default. The test FAILS because the override passthrough is unverified against the new default behavior. **→ SC-10**
- [ ] 54. **GREEN (**task-card**).** Dispatch the green task from test-driven-development: verify (and fix if needed) override passthrough from the UI control through to the seam. **→ SC-10**
- [ ] 55. **Post-regression (**task-card**).** Dispatch the phase-4 task from test-driven-development: `_validate_threshold` guard tests and preference tests unaffected. **→ non-regression for SC-10**
- [ ] 56. **Verify (**task-card**).** Dispatch the verify task from verification-before-completion: verify the override value flows from the control to the seam unchanged, with live-browser evidence per the ui testing standard (skips reported as skipped). **→ SC-10**
- [ ] 57. **Commit (**direct**).** Stage and commit test + implementation together. **→ SC-10**

---

## Phase 3 VbC Completion Block

- [ ] Verify SC-9: fresh-session UI default equals the published floor within ±0.01.
- [ ] Verify SC-10: UI override reaches the seam; never silently replaced by the default.
- [ ] Verify preserved invariants: session-state key name, [0.0, 1.0] guard, PreferenceService authority.
- [ ] Verify Playwright evidence exists per the ui testing standard; any E2E skip is reported as skipped.

**Concern transition:** Leaving UI threshold plumbing → entering post-implementation (audit, Z3 check, structural checks, pre-PR gate, regression check, review prep, PR creation, executive summary).
