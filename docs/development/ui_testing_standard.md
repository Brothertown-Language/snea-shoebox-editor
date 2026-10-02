<!-- Copyright (c) 2026 Brothertown Language -->
<!-- SPDX-License-Identifier: MIT -->
<!-- Provenance: AI-assisted -->

# UI Testing Standard — Playwright with Vision

## Directive

Streamlit UI verification SHALL prefer real-browser Playwright tests against
the running app over `streamlit.testing.v1.AppTest` going forwards. Where
visual confirmation of rendering, layout, or progress affordances matters,
pair Playwright with vision analysis of captured screenshots.

Established 2026-09-30 during issue #36 (SC-13): an AppTest-based
backfill-button test and a Playwright click-through disagreed in coverage.
AppTest exercises page logic in-process but never proves the browser actually
renders the button, streams a progress bar, or surfaces a status. The
Playwright run caught real-browser behavior AppTest cannot, and is the
standard of record.

## Why (evidence from #36)

| Behavior AppTest validated   | What only Playwright proved   |
| ---------------------------- | ----------------------------- |
| Service invoked with callback | Button visible in real DOM   |
| Status strings returned      | Progressbar streamed          |
| `handle_ui_error` wiring     | Status collapsed on completion |
| Role branches reachable      | Deep-link redirects strangers |

## Test architecture

Established by `test/ui/test_playwright_backfill_clickthrough.py`.

1. **Authentication — test-only bypass (established 2026-10-02, issue #1400
   SC-11/SC-11a by developer directive):** E2E runs authenticate via the
   `SNEA_E2E`-gated test-only auth bypass hook in
   `src/services/security_manager.py` (`rehydrate_session`). When
   `SNEA_E2E=1` the app establishes a clearly-marked synthetic test-only
   session (no real GitHub credentials, no headed OAuth login, no saved
   auth state). The E2E harness starts a fresh browser context with no
   `storage_state` and relies on the app-side bypass. With `SNEA_E2E`
   unset the auth path is byte-identical to production (verified by
   `test/test_security_manager_e2e_bypass_inert_sc11a_red.py`). The
   bypass requires NO real credential fabrication — the synthetic identity
   is a test-only constant, never a token minted from CLI credentials.
   - **Legacy fallback (headed login window):** if the bypass hook is
     unavailable (e.g. older branch), the agent prepares everything it can
     autonomously (start the local app, health-check `/_stcore/health` →
     200), then launches a headed Chromium via `sync_playwright()`
     (headless=False) at the login page and waits for the developer to
     complete the real GitHub OAuth in that window, saving
     `context.storage_state(path=...)` to `tmp/issue-36/auth-state.json`
     (the gh_auth_token cookie must be present — sanity-check the cookie
     names before consuming). Do NOT fabricate auth state from CLI tokens:
     gh CLI tokens typically lack the `user:email` scope the app's identity
     sync requires and dehydrate to the login page; `gh auth refresh -s
     user` exists as a fallback only. Full agent-facing procedure:
     [test/ui/AGENTS.md](../../test/ui/AGENTS.md).
2. **Automated runs:** tests start a fresh browser context and rely on the
   app-side `SNEA_E2E=1` auth bypass (SC-11) — no cookie injection, no
   token minting, no GitHub API calls from tests. Legacy saved-state runs
   load `storage_state=...` when the bypass is unavailable; regenerate
   storage state whenever missing or stale; tests fail loudly (never fall
   back to unauthenticated).
3. **Server:** run against the local app with the synced+migrated DB.
   **ALWAYS launch Streamlit with `--server.headless true`** — without it,
   Streamlit auto-opens the system default browser (the developer's
   desktop browser) on every server start. Never open the app in the
   developer's browser; agents interact only through their own Playwright
   instances. Example: `uv run --extra local python -m streamlit run
   streamlit_app.py --server.address 0.0.0.0 --server.port 8501
   --server.headless true` (add `SNEA_E2E=1` for E2E runs). Health check:
   `/_stcore/health`.
4. **Gating:** E2E tests carry the `playwright_e2e` pytest marker and skip
   unless `SNEA_E2E=1` is set, so `pytest test/` stays green without the
   live server.

## Agent instructions pointer (MANDATORY)

AI agents working in `test/ui/` MUST read [test/ui/AGENTS.md](../../test/ui/AGENTS.md)
first — it is the agent-facing operational guide for this standard: the
headed-login-window procedure for the developer, automated E2E run steps,
harness conventions, and the never-fabricate-auth-state rule.

## AppTest — remaining sanctioned uses

AppTest is NOT banned; it is downgraded to fast in-process smoke checks where
browser rendering is irrelevant (pure function branches, service-call
wiring). Any SC whose evidence type claims user-visible behavior (rendering,
progress, UI role gating) requires Playwright evidence of record.

## Vision Pairing

For layout/rendering-sensitive SCs, attach the Playwright screenshots
(written under `tmp/<issue>/artifacts/`) to the verification report and
review them with vision analysis rather than relying on text extraction
alone — text extraction misses empty panels and layout corruption (observed
repeatedly during #36 debugging).

---

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
