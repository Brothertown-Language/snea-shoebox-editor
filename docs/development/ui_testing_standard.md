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

1. **One-time login setup (headed window shown to the developer — the agent
   MUST NOT authenticate on the developer's behalf):** the agent prepares
   everything it can autonomously (start the local app, health-check
   `/_stcore/health` → 200, verify the saved-state path), then launches a
   headed Chromium via `sync_playwright()` (headless=False) at the login
   page and waits for the developer to complete the real GitHub OAuth in
   that window; the agent then saves the session with
   `context.storage_state(path=...)` to `tmp/issue-36/auth-state.json`
   (the gh_auth_token cookie must be present — sanity-check the cookie
   names before consuming). Do NOT fabricate auth state from CLI tokens:
   gh CLI tokens typically lack the `user:email` scope the app's identity
   sync requires and dehydrate to the login page; `gh auth refresh -s user`
   exists as a fallback only. Full agent-facing procedure:
   [test/ui/AGENTS.md](../../test/ui/AGENTS.md).
2. **Automated runs:** tests load `storage_state=...` into a fresh context —
   no cookie injection, no token minting, no GitHub API calls from tests.
   Regenerate storage state whenever missing or stale; tests fail loudly
   (never fall back to unauthenticated).
3. **Server:** run against the local app (`scripts/start_streamlit.sh`,
   health check `/_stcore/health`) with the synced+migrated DB.
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
