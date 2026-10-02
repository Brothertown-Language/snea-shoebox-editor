<!-- Copyright (c) 2026 Brothertown Language -->
<!-- SPDX-License-Identifier: MIT -->
<!-- Provenance: AI-assisted -->

# AI Agent Instructions — UI Testing (test/ui/)

## MANDATORY FIRST STEP — read the UI testing standard

Before writing, modifying, or running ANY UI test in `test/ui/`, the AI agent
MUST read and follow [the UI testing standard](../../docs/development/ui_testing_standard.md):

- **Playwright real-browser tests against the live app are the standard of
  record** for any success criterion claiming user-visible behavior
  (rendering, layout, progress affordances, role gating).
- **`streamlit.testing.v1.AppTest` is downgraded to in-process smoke checks**
  (pure function branches, service-call wiring) — it is NOT sufficient
  evidence for user-visible-behavior claims.
- Layout/rendering-sensitive criteria require **vision review of Playwright
  screenshots** attached under `tmp/<issue>/artifacts/` — text extraction
  alone misses empty panels and layout corruption.

## Starting the app — ALWAYS use --server.headless true

Enforced globally: `.streamlit/config.toml` sets `server.headless = true`, so
every Streamlit invocation in this project runs headless regardless of CLI
args. Do not remove or override this setting; do not launch Streamlit any
other way.

Without `--server.headless true`, Streamlit auto-opens the system default
browser (the developer's desktop browser) on every server start. Agents MUST
NOT open the app in the developer's browser — all agent interaction happens
through the agent's own Playwright instances. Canonical launch:

```bash
# E2E runs (auth bypass active):
SNEA_E2E=1 nohup uv run --extra local python -m streamlit run streamlit_app.py \
  --server.address 0.0.0.0 --server.port 8501 --server.headless true \
  > tmp/<issue>/artifacts/streamlit.log 2>&1 &
# wait for /_stcore/health -> 200
```

## E2E authentication — SNEA_E2E test-only bypass (default)

Established 2026-10-02 (issue #1400 SC-11/SC-11a, developer directive): with
`SNEA_E2E=1` the app authenticates via the test-only bypass hook in
`src/services/security_manager.py::rehydrate_session` — a clearly-marked
synthetic test-only identity, no real GitHub credentials. E2E tests start a
fresh browser context with NO `storage_state` and NO headed login; the
saved-state path below is a legacy fallback only. With `SNEA_E2E` unset the
auth path is byte-identical to production (verified by
`test/test_security_manager_e2e_bypass_inert_sc11a_red.py`).

## Legacy fallback — headed login window (only when the bypass is unavailable)

When the bypass hook is unavailable (e.g. older branch), saved OAuth state is
required before any E2E run. When the saved state is
missing or stale (401/dehydrated-to-login during a probe run), the AI agent
MUST generate the login session by **opening a headed browser window and
handing it to the developer to complete the GitHub OAuth login** — never
fabricate auth state from CLI tokens (gh CLI tokens may lack the
`user:email` scope the app's identity sync requires; `gh auth refresh -s user`
is a fallback, not the default).

Agent-side preparation (all steps the agent CAN do autonomously):

1. Start the local app with `--server.headless true` (see the launch section
   above) — wait for `/_stcore/health` → 200 on `http://localhost:8501`.
2. Verify the saved state location for the current issue scope:
   `tmp/issue-36/auth-state.json` is the established path (the E2E harness
   loads it via `STORAGE_PATH`); per-issue copies may be written alongside.
3. Launch the headed login window (a real visible Chromium the developer
   completes):

   ```python
   # Run from project root. Blocks until the developer finishes login.
   from playwright.sync_api import sync_playwright

   def save_login():
       with sync_playwright() as pw:
           browser = pw.chromium.launch(headless=False)
           context = browser.new_context()
           page = context.new_page()
           page.goto("http://localhost:8501/login")
           input("Developer: complete the GitHub login in the opened window, "
                 "then press ENTER here to save the session... ")
           context.storage_state(path="tmp/issue-36/auth-state.json")
           print("Session saved.")
           browser.close()

   save_login()
   ```

4. After saving, sanity-check the state contains the `gh_auth_token` cookie
   (`jq`/python cookie-name check) before consuming it in automated runs.

The headed window is the default and the developer-facing step — the agent
does not authenticate on the developer's behalf.

## Automated E2E runs (bypass active with SNEA_E2E=1)

1. App must be running: `/_stcore/health` → 200 (agent-owned, launched with
   `--server.headless true`).
2. `SNEA_E2E=1 uv run pytest test/ui/<file>.py` — the `playwright_e2e`
   marker gates these tests so plain `pytest test/` stays green serverless;
   the app-side auth bypass authenticates the fresh context (no saved
   state, no headed login).
3. Legacy saved-state runs (bypass unavailable) load the saved
   `storage_state` fresh — no cookie injection, no token minting in tests.
   Stale state fails loudly; regenerate via the headed-login fallback
   above, never by falling back to unauthenticated.
4. Attach screenshots to `tmp/<issue>/artifacts/` and apply vision review
   per the standard.

## E2E harness conventions (established by test_playwright_backfill_clickthrough.py)

- Run `sync_playwright` bodies in a worker thread (`pytest 9 + anyio` keeps
  an asyncio loop on the main thread; the Playwright sync API forbids
  entering under a running loop).
- Deep-link assertion pattern: unauthenticated access must redirect to
  `/login` (the OAuth button is an iframe component invisible to the main
  frame's text locator).
- Artifacts (screenshots, JSON results) go to `tmp/<issue>/artifacts/`.

---

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
