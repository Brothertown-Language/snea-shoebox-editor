"""Issue #1400 SC-11 — RED: E2E harness authenticates headlessly.

SC-11: with SNEA_E2E=1, the Playwright E2E UI test harness must complete
authentication WITHOUT any headed GitHub OAuth login and WITHOUT fabricated
real GitHub credentials, via the pinned test-only SNEA_E2E-gated auth bypass
hook in src/services/security_manager.py auth resolution.

This RED test opens the app in a FRESH headless Chromium context — no
storage_state, no tmp/issue-36/auth-state.json, no headed login step — and
asserts the records page reaches its authenticated state (the sidebar search
mode radio renders; unauthenticated users are gated to the login page).

Expected to FAIL (RED): the current harness depends on saved auth state
(tmp/issue-36/auth-state.json, which lacks the gh_auth_token cookie because
the app sets the token server-side) and no bypass hook exists yet.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import os

import pytest
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:8501/records"
ARTIFACTS_DIR = os.path.join("tmp", "issue-1400", "artifacts")

pytest.importorskip("playwright.sync_api")

pytestmark = [
    pytest.mark.playwright_e2e,
    pytest.mark.skipif(
        os.environ.get("SNEA_E2E", "") != "1",
        reason="live-app E2E — run with SNEA_E2E=1 while streamlit is up on :8501",
    ),
]


def test_sc11_headless_authentication_without_saved_auth_state():
    """SC-11: fresh headless context reaches the authenticated records page
    with no headed OAuth login and no saved/fabricated credentials."""
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # FRESH context: deliberately NO storage_state — no auth-state.json,
        # no headed-login capture, no fabricated GitHub credentials.
        context = browser.new_context()
        page = context.new_page()
        page.goto(APP_URL, wait_until="domcontentloaded")

        authenticated = False
        try:
            # Authenticated marker: the records-page sidebar search mode radio.
            page.wait_for_selector(
                '[data-testid="stRadio"] input[type="radio"]',
                state="attached",
                timeout=45_000,
            )
            authenticated = True
        except Exception:
            authenticated = False

        page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc11-red-headless-auth.png"))
        browser.close()

        assert authenticated, (
            "SC-11 RED: fresh headless context did NOT reach the authenticated "
            "records page — the SNEA_E2E=1 auth bypass hook in "
            "src/services/security_manager.py does not exist yet, so the E2E "
            "harness still depends on saved auth state / headed OAuth login."
        )