"""Issue #1401 SC-20 — Playwright real-browser DOM assertion: with an active
query, switching to the SEMANTIC modes ("Semantic Gloss" and "Semantic All")
renders NO ``<mark class="search-token">`` elements inside the rendered MDF
block — semantic modes never receive highlight parameters (records.py
View-mode wiring guards ``view_highlight_spans`` behind
``not is_semantic_mode``).

Gated by the ``playwright_e2e`` marker + ``SNEA_E2E=1`` (live app on :8501,
test-only auth bypass per docs/development/ui_testing_standard.md). Without
the gate the test records SKIPPED by design — plain ``pytest test/`` stays
green serverless. Gate-skipping is never silently treated as a pass.

Worker-thread pattern per test/ui/AGENTS.md harness conventions.

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

import os
import queue
import threading

import pytest
from playwright.sync_api import Page, sync_playwright

APP_URL = "http://localhost:8501/records"
ARTIFACTS_DIR = os.path.join("tmp", "issue-1401", "artifacts")
STORAGE_PATH = os.path.join("tmp", "issue-36", "auth-state.json")

pytest.importorskip("playwright.sync_api")

pytestmark = [
    pytest.mark.playwright_e2e,
    pytest.mark.skipif(
        os.environ.get("SNEA_E2E", "") != "1",
        reason="live-app E2E — run with SNEA_E2E=1 while streamlit is up on :8501",
    ),
]


def _require_auth_storage() -> str | None:
    """SNEA_E2E=1 → app-side test-only auth bypass, fresh context, no saved state."""
    if os.environ.get("SNEA_E2E") == "1":
        return None
    if not os.path.exists(STORAGE_PATH):
        raise AssertionError(
            "No saved OAuth session at tmp/issue-36/auth-state.json — "
            "log in once via the headed Playwright window to generate it."
        )
    return STORAGE_PATH


class _BrowserSession:
    """Chromium + authed context + page inside one worker thread (pytest 9 +
    anyio keeps an asyncio loop on the main thread; the Playwright sync API
    forbids entering under a running loop)."""

    def __init__(self, storage: str | None):
        self._jobs: queue.Queue = queue.Queue()
        self._result_box: list[BaseException | None] = []
        self._done_evt = threading.Event()
        self._ready_evt = threading.Event()
        self._shutdown = threading.Event()
        self._storage = storage
        self.thread = threading.Thread(target=self._main, daemon=True)
        self.thread.start()
        self._ready_evt.wait(timeout=60)

    def _main(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            context = browser.new_context(storage_state=self._storage)
            page = context.new_page()
            self._ready_evt.set()
            while not self._shutdown.is_set():
                try:
                    fn = self._jobs.get(timeout=0.2)
                except queue.Empty:
                    continue
                if fn is None:
                    break
                self._result_box.clear()
                try:
                    fn(page)
                    self._result_box.append(None)
                except BaseException as e:  # noqa: BLE001 — propagate verbatim
                    self._result_box.append(e)
                self._done_evt.set()
            browser.close()

    def run(self, fn, timeout: float = 240.0):
        self._done_evt.clear()
        self._jobs.put(fn)
        if not self._done_evt.wait(timeout=timeout):
            raise TimeoutError(f"test body exceeded {timeout}s in worker thread")
        err = self._result_box[0] if self._result_box else RuntimeError("worker returned no result")
        if err is not None:
            raise err

    def close(self):
        self._shutdown.set()
        self._jobs.put(None)
        self.thread.join(timeout=30)


@pytest.fixture(scope="module")
def session():
    sess = _BrowserSession(_require_auth_storage())
    yield sess
    sess.close()


_COUNT_SEARCH_TOKENS = """() => {
    let count = document.querySelectorAll('.mdf-wrap-block mark.search-token').length;
    for (const frame of document.querySelectorAll('iframe')) {
        try {
            const doc = frame.contentDocument;
            if (doc) count += doc.querySelectorAll('.mdf-wrap-block mark.search-token').length;
        } catch (e) {}
    }
    return count;
}"""

_BLOCKS_PRESENT = """() => {
    if (document.querySelector('.mdf-wrap-block')) return true;
    for (const frame of document.querySelectorAll('iframe')) {
        try {
            const doc = frame.contentDocument;
            if (doc && doc.querySelector('.mdf-wrap-block')) return true;
        } catch (e) {}
    }
    return false;
}"""


def _sc20_flow(page: Page, mode: str, shot: str):
    """Select the semantic mode, run an active query, assert zero
    mark.search-token in the rendered block."""
    page.goto(APP_URL, wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="stTextInput"] input', state="visible", timeout=45_000)
    page.wait_for_timeout(2500)

    # Switch to the semantic mode via the sidebar Search Mode radio.
    page.locator('[data-testid="stRadio"] label', has_text=mode).first.click()
    page.wait_for_timeout(2500)

    # Active query: fill the search input and execute the search. The first
    # semantic query pays a one-time embedding-model warm load (60s budget).
    page.locator('[data-testid="stTextInput"] input').fill("")
    page.locator('[data-testid="stTextInput"] input').fill("he")
    page.locator('button:has-text("🔍")').first.click()
    page.wait_for_function("() => document.body.textContent.includes('Search: ')", timeout=90_000)
    page.wait_for_timeout(5000)

    # Precondition: rendered MDF blocks must be present so the zero-token
    # assertion is not vacuous (semantic search for 'he' returns results on
    # the local DB replica).
    blocks_present = page.evaluate(_BLOCKS_PRESENT)
    assert blocks_present, (
        f"SC-20 precondition failed: no rendered MDF block found after a "
        f"{mode}-mode search for an active query — cannot validate the "
        "semantic no-highlight boundary."
    )

    # SC-20 DOM assertion: ZERO mark.search-token inside any rendered
    # mdf-wrap-block (main document + same-origin iframes).
    token_count = page.evaluate(_COUNT_SEARCH_TOKENS)
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, shot))
    assert token_count == 0, (
        f"SC-20 RED: {token_count} mark.search-token element(s) found in the rendered MDF "
        f"block DOM after a {mode}-mode search with an active query — semantic modes "
        "received highlight parameters (mode-guard leak in records.py View-mode wiring)."
    )


def test_sc20_semantic_gloss_no_search_token_in_rendered_block_dom(session):
    session.run(lambda page: _sc20_flow(page, "Semantic Gloss", "e2e-sc20-semantic-gloss-no-tokens.png"))


def test_sc20_semantic_all_no_search_token_in_rendered_block_dom(session):
    session.run(lambda page: _sc20_flow(page, "Semantic All", "e2e-sc20-semantic-all-no-tokens.png"))