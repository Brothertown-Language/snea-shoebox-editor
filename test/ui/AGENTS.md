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

## One-time login setup — DISPLAY THE LOGIN WINDOW FOR THE DEVELOPER

Saved OAuth state is required before any E2E run. When the saved state is
missing or stale (401/dehydrated-to-login during a probe run), the AI agent
MUST generate the login session by **opening a headed browser window and
handing it to the developer to complete the GitHub OAuth login** — never
fabricate auth state from CLI tokens (gh CLI tokens may lack the
`user:email` scope the app's identity sync requires; `gh auth refresh -s user`
is a fallback, not the default).

Agent-side preparation (all steps the agent CAN do autonomously):

1. Start the local app: `bash scripts/start_streamlit.sh` — wait for
   `/_stcore/health` → 200 on `http://localhost:8501`.
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

## Automated E2E runs (after saved state exists)

1. App must be running: `/_stcore/health` → 200 (agent-owned).
2. `SNEA_E2E=1 uv run pytest test/ui/<file>.py` — the `playwright_e2e`
   marker gates these tests so plain `pytest test/` stays green serverless.
3. Tests load the saved `storage_state` fresh — no cookie injection, no
   token minting in tests. Stale state fails loudly; regenerate via the
   headed-login step above, never by falling back to unauthenticated.
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
