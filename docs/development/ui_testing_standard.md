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

1. **One-time login setup (manual, per developer):** launch a headed Chromium
   via `sync_playwright()` at `http://localhost:8501/maintenance`, complete
   real GitHub OAuth, save the session with `context.storage_state(path=...)`
   to `tmp/issue-36/auth-state.json`. The `gh_auth_token` cookie must be
   present in the saved state.
2. **Automated runs:** tests load `storage_state=...` into a fresh context —
   no cookie injection, no token minting, no GitHub API calls from tests.
   Regenerate storage state whenever missing or stale; tests fail loudly
   (never fall back to unauthenticated).
3. **Server:** run against the local app (`scripts/start_streamlit.sh`,
   health check `/_stcore/health`) with the synced+migrated DB.
4. **Gating:** E2E tests carry the `playwright_e2e` pytest marker and skip
   unless `SNEA_E2E=1` is set, so `pytest test/` stays green without the
   live server.

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
