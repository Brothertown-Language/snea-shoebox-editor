"""Issue #1401 SC-20 — Playwright real-browser behavioral test: Semantic Gloss
and Semantic All modes never receive highlight parameters, so no
``mark.search-token`` appears in rendered blocks even with an active query.

Evidence mix (per SC-20 evidence type = behavioral):
1. DOM (Playwright): select the 'Semantic Gloss' radio, run a search on the
   live app, and assert no ``mark.search-token`` exists in any rendered MDF
   block (st.html renders inline in the main document — no iframes). The
   test is written to FAIL pre-GREEN if semantic modes ever show marks;
   if it passes today it stands as the regression slice.
2. DOM (Playwright): same for the 'Semantic All' radio.

Gated by the ``playwright_e2e`` marker + ``SNEA_E2E=1`` (live app on :8501,
test-only auth bypass per docs/development/ui_testing_standard.md). Without
the gate the test records SKIPPED by design.

Worker-thread pattern per test/ui/AGENTS.md harness conventions
(reuse of test_records_highlight_threading_dom_sc17.py structure).

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


class _BrowserSession:
    """Chromium + authed context + page inside one worker thread (pytest 9 +
    anyio keeps an asyncio loop on the main thread; the Playwright sync API
    forbids entering under a running loop)."""

    def __init__(self):
        self._jobs: queue.Queue = queue.Queue()
        self._result_box: list[BaseException | None] = []
        self._done_evt = threading.Event()
        self._ready_evt = threading.Event()
        self._shutdown = threading.Event()
        self.thread = threading.Thread(target=self._main, daemon=True)
        self.thread.start()
        self._ready_evt.wait(timeout=60)

    def _main(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            context = browser.new_context()
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

    def run(self, fn, timeout: float = 300.0):
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
    sess = _BrowserSession()
    yield sess
    sess.close()


def _run_semantic_search(page: Page, mode_label: str):
    """Select a Semantic mode radio and run a search on the live app."""
    page.goto(APP_URL, wait_until="domcontentloaded")
    # The SNEA_E2E bypass lands on Records directly (same flow as SC-13/SC-17).
    page.wait_for_selector('[data-testid="stTextInput"] input', state="visible", timeout=45_000)
    page.wait_for_timeout(2500)
    # Semantic mode — the radio exposes 'Semantic Gloss' / 'Semantic All'
    # labels directly (records.py mode options list).
    page.locator('[data-testid="stRadio"] label', has_text=mode_label).first.click()
    page.wait_for_timeout(2500)
    # Lower the semantic threshold to 0 so results actually render — a search
    # that matches zero records would make the "no marks" assertion vacuous.
    # records.py exposes the threshold via a dedicated st.number_input.
    threshold_input = page.locator('[data-testid="stNumberInput"] input').first
    threshold_input.fill("0")
    threshold_input.press("Enter")
    page.wait_for_timeout(4000)
    page.locator('[data-testid="stTextInput"] input').fill(SEARCH_TERM)
    page.locator('[data-testid="stBaseButton-secondary"]:has-text("🔍")').first.click()
    page.wait_for_function(
        """() => document.body.textContent.includes('Search: ')""",
        timeout=60_000,
    )
    page.wait_for_timeout(5000)


_COUNT_SEARCH_TOKENS = """() => {
    // Streamlit renders st.html blocks inline in the main document (no iframes).
    // Count marks in the main document AND inside same-origin iframes.
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
    return {total};
}"""


def test_sc20_semantic_gloss_no_search_token_in_blocks(session):
    """DOM: Semantic Gloss mode must produce zero mark.search-token in rendered blocks."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    def flow(page: Page):
        _run_semantic_search(page, "Semantic Gloss")
        counts = page.evaluate(_COUNT_SEARCH_TOKENS)
        page.screenshot(path=str(ARTIFACTS_DIR / "e2e-sc20-semantic-gloss-no-tokens.png"))
        assert counts["total"] == 0, (
            "SC-20: mark.search-token elements found in rendered MDF blocks under "
            f"Semantic Gloss mode with query '{SEARCH_TERM}' — semantic modes must "
            "never receive highlight parameters."
        )

    session.run(flow)


def test_sc20_semantic_all_no_search_token_in_blocks(session):
    """DOM: Semantic All mode must produce zero mark.search-token in rendered blocks."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    def flow(page: Page):
        _run_semantic_search(page, "Semantic All")
        counts = page.evaluate(_COUNT_SEARCH_TOKENS)
        page.screenshot(path=str(ARTIFACTS_DIR / "e2e-sc20-semantic-all-no-tokens.png"))
        assert counts["total"] == 0, (
            "SC-20: mark.search-token elements found in rendered MDF blocks under "
            f"Semantic All mode with query '{SEARCH_TERM}' — semantic modes must "
            "never receive highlight parameters."
        )

    session.run(flow)