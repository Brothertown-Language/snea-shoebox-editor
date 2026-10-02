# Phase 4 — E2E auth bypass — test-only SNEA_E2E-gated authentication

**Concern:** e2e-auth-bypass (SC-11, SC-11a) — per concern-map.yaml (added by SC-11 revision, 2026-10-02; pinned mechanism + SC-11a split, 2026-10-02)

**Files:**
- `src/services/security_manager.py` (app auth path — pinned location of the `SNEA_E2E`-gated test-only bypass hook in the auth resolution)
- `test/ui/test_semantic_search_ui_flow_e2e.py` — Playwright E2E suite consuming the bypass

**SCs:** SC-11, SC-11a

**Dependencies:** Phase 3 (UI threshold plumbing complete; E2E suite otherwise ready to run)

**Entry Conditions:**
- Phase 3 complete: SC-9/SC-10 verified; Phase 3 commits landed
- Live app runnable on :8501 with `SNEA_E2E=1`
- Current E2E auth-state failure reproduced (stale saved auth state; headed-login capture attempts cannot capture the token because the app sets it server-side)

**Exit Conditions:**
- `SNEA_E2E=1` Playwright E2E suite executes fully authenticated with NO headed OAuth login step and NO fabricated real GitHub credentials
- Bypass mechanism is the PINNED single mechanism: a `SNEA_E2E`-gated test-only hook in the app's auth path (`src/services/security_manager.py` auth resolution) — direct cookie/context injection is NOT an authorized alternative (the app sets the token server-side and validates tokens against the live GitHub API, so injected cookies fail server-side validation)
- Bypass verified inert by pytest (SC-11a): with `SNEA_E2E` unset, the auth resolution follows the production path exactly (no bypass branch taken, no code path altered)
- No weakening of production auth: the bypass never ships active outside the test gate

**Code Path Coverage:**
- SC-11: `src/services/security_manager.py` auth resolution — add test-only bypass gated on `SNEA_E2E=1` env (short-circuit session-token establishment when the gate variable is set); E2E harness consumes the bypass path
- SC-11: E2E harness — remove dependency on `tmp/issue-36/auth-state.json` / headed-login capture for E2E runs; use the bypass path for authentication
- SC-11a: `src/services/security_manager.py` — pytest auth-path test asserting that with `SNEA_E2E` unset the production auth resolution path is followed with no bypass branch

**Interface Boundaries:**
- Production auth behavior: UNCHANGED (bypass branch reachable only when `SNEA_E2E=1`; verified by SC-11a test)
- `SNEA_E2E` env var: already the E2E gating mechanism per ui_testing_standard — reused as the bypass gate; no new env surface
- Real GitHub credentials: never fabricated; bypass requires none

**State Transitions:**
- With `SNEA_E2E=1`: test session establishes authenticated state via the pinned test-only bypass hook in the auth resolution instead of the OAuth redirect flow
- Without `SNEA_E2E`: auth flow identical to current production behavior (SC-11a verified)

**Cost frame:** Implementing the gated bypass costs a small, strictly-gated code path plus an inertness verification run. Skipping it costs a permanently unrunnable E2E tier — every UI regression check (SC-9/SC-10 and future UI changes) requires a developer to sit through a headed OAuth login whose token capture has already failed twice — the E2E tier regresses into manual-only testing and user-visible regressions ship undetected.

---

## Step-by-step

### Item 12 — SC-11: test-only SNEA_E2E-gated auth bypass for the E2E harness

- [ ] 66. **RED (**task-card**).** Dispatch the red task from test-driven-development: write a failing E2E harness assertion that the `SNEA_E2E=1` Playwright suite completes authentication without any headed OAuth login and without fabricated credentials. The test FAILS because the current harness depends on saved auth state / headed login. **→ SC-11**
- [ ] 67. **GREEN (**task-card**).** Dispatch the green task from test-driven-development: implement the PINNED test-only mechanism — a `SNEA_E2E`-gated auth bypass hook in the app's auth path (`src/services/security_manager.py` auth resolution). Direct cookie/context injection is NOT an authorized alternative (the app sets the token server-side and validates tokens against the live GitHub API). Real production auth behavior unchanged; bypass inert without the gate. Minimum change only. **→ SC-11**
- [ ] 68. **Post-regression (**task-card**).** Dispatch the phase-4 task from test-driven-development: existing auth-related tests and app tests unaffected; production auth path byte-identical when `SNEA_E2E` is unset. **→ non-regression for SC-11**
- [ ] 69. **Verify (**task-card**).** Dispatch the verify task from verification-before-completion: run the E2E suite with `SNEA_E2E=1` + live app on :8501 — authenticated completion with no headed login; then run the app without `SNEA_E2E` and verify the bypass branch is not taken. **→ SC-11**
- [ ] 70. **Commit (**direct**).** Stage and commit test + bypass implementation together. **→ SC-11**

### Item 13 — SC-11a: bypass inert outside `SNEA_E2E=1` (pytest-verified)

- [ ] 71. **RED (**task-card**).** Dispatch the red task from test-driven-development: write a failing pytest auth-path test that with `SNEA_E2E` unset the auth resolution in `src/services/security_manager.py` follows the production path (no bypass branch). The test FAILS because the bypass branch as implemented is reachable (or the assertion surface does not yet exist). **→ SC-11a**
- [ ] 72. **GREEN (**task-card**).** Dispatch the green task from test-driven-development: make the bypass branch unreachable when `SNEA_E2E` is unset so the auth resolution behaves identically to production. Minimum change only. **→ SC-11a**
- [ ] 73. **Verify (**task-card**).** Dispatch the verify task from verification-before-completion: run the pytest auth-path test with `SNEA_E2E` unset — production auth path confirmed unchanged; cross-check against the Phase 3/4 non-regression run. **→ SC-11a**
- [ ] 74. **Commit (**direct**).** Stage and commit test + inertness change together. **→ SC-11a**

---

## Phase 4 VbC Completion Block

- [ ] Verify SC-11: E2E suite runs authenticated with `SNEA_E2E=1`, no headed OAuth login, no fabricated GitHub credentials.
- [ ] Verify SC-11a: with `SNEA_E2E` unset, pytest auth-path test confirms the production auth resolution path is followed with no bypass branch.
- [ ] Verify no secrets or real credentials embedded in test code or bypass code.

**Concern transition:** Leaving E2E auth bypass → entering post-implementation (audit, Z3 check, structural checks, pre-PR gate, regression check, review prep, PR creation, executive summary).

---

🤖 Co-authored with AI: OpenCode (zai-org/GLM-5.3-Flash)
