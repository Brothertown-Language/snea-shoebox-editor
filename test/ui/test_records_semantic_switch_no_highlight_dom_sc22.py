"""Issue #1401 SC-22 — Playwright real-browser behavioral test: the semantic
no-search-token guarantee holds during a mid-session mode switch. A lexical
(Lexeme-mode) search is executed first — marks ARE present (precondition,
non-vacuous) — then the Search Mode radio is switched to a semantic mode with
the query still active; the re-rendered MDF blocks must contain ZERO
``mark.search-token`` elements.

This aspect is distinct from the fresh-page SC-20 slices
(test_records_semantic_no_highlight_dom_sc20.py,
test_mdf_block_semantic_mode_no_mark_dom_sc20.py): those select the semantic
mode BEFORE any search executes. SC-22 covers the state-transition path where
the app holds highlight parameters for the active lexical query and must drop
them when the mode changes to Semantic Gloss / Semantic All.

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


def _lexical_search_then_switch(page: Page, semantic_mode_label: str):
    """Run a lexical search (marks expected), then switch to a semantic mode
    with the query still active."""
    page.goto(APP_URL, wait_until="domcontentloaded")
    # The SNEA_E2E bypass lands on Records directly (same flow as SC-17/SC-20).
    page.wait_for_selector('[data-testid="stTextInput"] input', state="visible", timeout=45_000)
    page.wait_for_timeout(2500)
    # Lexical search — Lexeme mode (Algonquian terms).
    page.locator('[data-testid="stRadio"] label', has_text="Lexeme").first.click()
    page.wait_for_timeout(2500)
    page.locator('[data-testid="stTextInput"] input').fill(SEARCH_TERM)
    page.locator('[data-testid="stBaseButton-secondary"]:has-text("🔍")').first.click()
    page.wait_for_function(
        """() => document.body.textContent.includes('Search: ')""",
        timeout=30_000,
    )
    page.wait_for_timeout(3000)
    # Precondition: the lexical state MUST show marks — otherwise the switch
    # assertion is vacuous.
    lexical_counts = page.evaluate(_COUNT_SEARCH_TOKENS)
    assert lexical_counts["total"] > 0, (
        "SC-22 precondition failed: no mark.search-token after a Lexeme-mode "
        f"search for '{SEARCH_TERM}' — the lexical baseline is missing, so a "
        "post-switch zero-mark assertion would be vacuous."
    )
    # Mid-session mode switch with the query still active.
    page.locator('[data-testid="stRadio"] label', has_text=semantic_mode_label).first.click()
    page.wait_for_timeout(2500)
    page.wait_for_timeout(5000)


def test_sc22_semantic_gloss_after_lexical_switch_no_search_token(session):
    """DOM: switching Lexeme -> Semantic Gloss with an active query must clear marks."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    def flow(page: Page):
        _lexical_search_then_switch(page, "Semantic Gloss")
        counts = page.evaluate(_COUNT_SEARCH_TOKENS)
        page.screenshot(path=str(ARTIFACTS_DIR / "e2e-sc22-lexical-to-semantic-gloss-no-tokens.png"))
        assert counts["total"] == 0, (
            "SC-22: mark.search-token elements persisted after switching from a "
            f"Lexeme-mode search ('{SEARCH_TERM}') to Semantic Gloss with the query "
            "still active — the mode switch must drop highlight parameters."
        )

    session.run(flow)


def test_sc22_semantic_all_after_lexical_switch_no_search_token(session):
    """DOM: switching Lexeme -> Semantic All with an active query must clear marks."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    def flow(page: Page):
        _lexical_search_then_switch(page, "Semantic All")
        counts = page.evaluate(_COUNT_SEARCH_TOKENS)
        page.screenshot(path=str(ARTIFACTS_DIR / "e2e-sc22-lexical-to-semantic-all-no-tokens.png"))
        assert counts["total"] == 0, (
            "SC-22: mark.search-token elements persisted after switching from a "
            f"Lexeme-mode search ('{SEARCH_TERM}') to Semantic All with the query "
            "still active — the mode switch must drop highlight parameters."
        )

    session.run(flow)