"""Issue #1401 SC-10 — Playwright real-browser DOM assertion: a search executed
on the Records page renders ``<mark class="search-token">`` highlight wrapping
inside the rendered MDF block (st.html iframe), not just in the captured HTML.

Gated by the ``playwright_e2e`` marker + ``SNEA_E2E=1`` (live app on :8501,
test-only auth bypass per docs/development/ui_testing_standard.md). Without
the gate the test records SKIPPED by design — plain ``pytest test/`` stays
green serverless. Pre-GREEN (wrapping not implemented) the gate-enabled run
MUST FAIL: no mark.search-token element exists in the block DOM.

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

# Search term executed against the synced local DB (overridable per run).
SEARCH_TERM = os.environ.get("SNEA_E2E_SEARCH_TERM", "Shookekineas")

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

    def run(self, fn, timeout: float = 180.0):
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


def _sc10_flow(page: Page):
    page.goto(APP_URL, wait_until="domcontentloaded")
    # Sidebar rendered: search text input visible.
    page.wait_for_selector('[data-testid="stTextInput"] input', state="visible", timeout=45_000)

    # Execute a search that yields records → result blocks render.
    page.locator('[data-testid="stTextInput"] input').fill(SEARCH_TERM)
    page.locator('button:has-text("🔍")').first.click()
    page.wait_for_timeout(3000)

    # Results header must confirm the search ran.
    page.wait_for_function(
        "() => document.body.textContent.includes('Search: ')",
        timeout=30_000,
    )

    # SC-10 DOM assertion: at least one mark.search-token inside the rendered
    # mdf-wrap-block (st.html renders inside an iframe — search its frames).
    found = page.evaluate(
        """() => {
        const docs = [document];
        for (const frame of document.querySelectorAll('iframe')) {
            try {
                if (frame.contentDocument) docs.push(frame.contentDocument);
            } catch (e) {}
        }
        return docs.some((doc) => doc.querySelector('.mdf-wrap-block mark.search-token'));
    }"""
    )
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, "e2e-sc10-search-token.png"))
    assert found, (
        "SC-10 RED: no mark.search-token element found in the rendered MDF block "
        f"DOM after searching '{SEARCH_TERM}' — highlight wrapping not yet implemented."
    )


def test_sc10_search_token_in_rendered_block_dom(session):
    session.run(_sc10_flow)