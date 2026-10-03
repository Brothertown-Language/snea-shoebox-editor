"""Issue #1401 SC-12 — Playwright real-browser DOM assertion: in the live app,
where a highlight span overlaps a diff-token span, the diff-token span renders
UNCHANGED and the overlapping search-token mark is OMITTED — i.e. no
``mark.search-token`` element may ever appear nested inside a
``mark.diff-token`` in the rendered MDF block (st.html iframe).

Gated by the ``playwright_e2e`` marker + ``SNEA_E2E=1`` (live app on :8501,
test-only auth bypass per docs/development/ui_testing_standard.md and
test/ui/AGENTS.md). Without the gate the test records SKIPPED by design —
plain ``pytest test/`` stays green serverless. Pre-GREEN (overlap precedence
not implemented) a gate-enabled run over a search that overlaps diff tokens
MUST FAIL: the nested mark.search-token exists in the block DOM.

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


def _sc12_flow(page: Page):
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

    # SC-12 DOM assertion, evaluated across all st.html iframes:
    #   1. At least one rendered MDF block exists (results rendered).
    #   2. No mark.search-token is nested inside any mark.diff-token —
    #      where a highlight overlaps a diff-token span, the diff-token
    #      markup renders unchanged and the overlapping search-token mark
    #      is omitted.
    result = page.evaluate(
        """() => {
        let blockCount = 0;
        const docs = [document];
        for (const frame of document.querySelectorAll('iframe')) {
            try {
                if (frame.contentDocument) docs.push(frame.contentDocument);
            } catch (e) {}
        }
        for (const doc of docs) {
            blockCount += doc.querySelectorAll('.mdf-wrap-block').length;
            for (const dt of doc.querySelectorAll('.mdf-wrap-block mark.diff-token')) {
                if (dt.querySelector('mark.search-token')) {
                    return {blockCount, nested: true, text: dt.textContent};
                }
            }
        }
        return {blockCount, nested: false};
    }"""
    )
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, "e2e-sc12-diff-token-overlap.png"))
    assert result["blockCount"] > 0, (
        "SC-12: no rendered .mdf-wrap-block found — the search must yield "
        "records before the overlap assertion is meaningful."
    )
    assert not result["nested"], (
        "SC-12 RED: found mark.search-token nested inside mark.diff-token "
        f"(text={result['text']!r}) — the diff-token span must render unchanged "
        "and the overlapping search-token mark must be omitted."
    )


def test_sc12_no_search_token_nested_in_diff_token_dom(session):
    session.run(_sc12_flow)
