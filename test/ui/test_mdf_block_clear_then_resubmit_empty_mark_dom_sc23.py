"""Issue #1401 SC-23 — Playwright real-browser DOM assertion: clearing a
previously typed query then re-submitting an EMPTY search on the Records page
removes all ``<mark class="search-token">`` elements from the rendered MDF
block (st.html inline render), i.e. an empty query re-submitted after marks
were present leaves zero highlight marks.

This is the distinct aspect beyond SC-19 (which submits empty from a cold
page): here marks must first exist (> 0) after a lexical search, then drop
to 0 after clearing the input and re-submitting.

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
from pathlib import Path

import pytest
from playwright.sync_api import Page, sync_playwright

APP_URL = "http://localhost:8501/records"
ARTIFACTS_DIR = Path("tmp") / "issue-1401" / "artifacts"

SEARCH_TERM = os.environ.get("SNEA_E2E_SEARCH_TERM", "kekineas")

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
    storage = Path("tmp") / "issue-36" / "auth-state.json"
    if not storage.exists():
        raise AssertionError(
            "No saved OAuth session at tmp/issue-36/auth-state.json — "
            "log in once via the headed Playwright window to generate it."
        )
    return str(storage)


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
    let total = 0;
    const countIn = (doc) => {
        total += doc.querySelectorAll('.mdf-wrap-block mark.search-token').length;
    };
    countIn(document);
    for (const frame of document.querySelectorAll('iframe')) {
        try {
            const doc = frame.contentDocument;
            if (doc) countIn(doc);
        } catch (e) {}
    }
    return total;
}"""


def _blocks_present(page: Page) -> bool:
    return page.evaluate(
        """() => {
        if (document.querySelector('.mdf-wrap-block')) return true;
        for (const frame of document.querySelectorAll('iframe')) {
            try {
                const doc = frame.contentDocument;
                if (doc && doc.querySelector('.mdf-wrap-block')) return true;
            } catch (e) {}
        }
        return false;
    }"""
    )


def test_sc23_clear_then_resubmit_empty_query_zero_marks(session):
    """Search with a term → marks > 0 → clear input → re-submit → marks == 0."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    def flow(page: Page):
        page.goto(APP_URL, wait_until="domcontentloaded")
        page.wait_for_selector('[data-testid="stTextInput"] input', state="visible", timeout=45_000)
        page.wait_for_timeout(2500)

        # Step 1: lexical search with a real term — Lexeme mode.
        page.locator('[data-testid="stRadio"] label', has_text="Lexeme").first.click()
        page.wait_for_timeout(2500)
        page.locator('[data-testid="stTextInput"] input').fill(SEARCH_TERM)
        page.locator('[data-testid="stBaseButton-secondary"]:has-text("🔍")').first.click()
        page.wait_for_function("() => document.body.textContent.includes('Search: ')", timeout=30_000)
        page.wait_for_timeout(3000)
        assert _blocks_present(page), "SC-23 precondition: no rendered MDF block after lexical search"

        marks_after_search = page.evaluate(_COUNT_SEARCH_TOKENS)
        page.screenshot(path=str(ARTIFACTS_DIR / "e2e-sc23-marks-after-search.png"))
        assert marks_after_search > 0, (
            "SC-23 precondition RED: no mark.search-token in rendered MDF block after "
            f"searching '{SEARCH_TERM}' — cannot exercise the clear-then-resubmit aspect."
        )

        # Step 2: clear the query input and re-submit the (now empty) search.
        page.locator('[data-testid="stTextInput"] input').fill("")
        page.locator('[data-testid="stBaseButton-secondary"]:has-text("🔍")').first.click()
        page.wait_for_timeout(3000)
        assert _blocks_present(page), "SC-23: no rendered MDF block after clearing and re-submitting"

        marks_after_clear = page.evaluate(_COUNT_SEARCH_TOKENS)
        page.screenshot(path=str(ARTIFACTS_DIR / "e2e-sc23-marks-after-clear-resubmit.png"))
        assert marks_after_clear == 0, (
            f"SC-23 RED: {marks_after_clear} mark.search-token element(s) remain in the "
            "rendered MDF block DOM after clearing the query and re-submitting an empty "
            "search — cleared-query re-submit leaks highlight marks."
        )

    session.run(flow)