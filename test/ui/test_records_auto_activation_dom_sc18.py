"""Issue #1401 SC-18 — Playwright real-browser behavioral test: with a
lexical-mode query active, search-token highlighting activates automatically
in the rendered MDF block in a FRESH session — no preference toggle and no
prior configuration. Verified across all four lexical modes (Lexeme, Headword,
Gloss, FTS), each starting from a brand-new browser context (no storage
state, no toggles touched, no prior search state).

Per-mode search terms were verified against the local database replica:
- Lexeme   "kekineas"     -> record 3657 (lexeme Shookekineas)
- Headword "Shookekineas" -> headword_search_entries record 3657
- Gloss    "Behold"       -> gloss_search_entries (e.g. record 3657 "Behold here.")
- FTS      "behold"       -> 82 fts_entries hits via to_tsquery('simple','behold:*')

Each mode asserts ``mark.search-token`` elements exist in the rendered block
DOM — assertions are never weakened.

Gated by the ``playwright_e2e`` marker + ``SNEA_E2E=1`` (live app on :8501,
test-only auth bypass per docs/development/ui_testing_standard.md). Without
the gate the tests record SKIPPED by design — skipping is never a PASS.

Worker-thread pattern per test/ui/AGENTS.md harness conventions.

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

import os
import queue
import threading
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:8501/records"
ARTIFACTS_DIR = Path("tmp") / "issue-1401" / "artifacts"

# (mode radio label, search term, screenshot stem) — terms verified against
# the local DB replica so every mode returns real results with matched terms.
MODE_CASES = [
    ("Lexeme", "kekineas", "e2e-sc18-lexeme-highlighted"),
    ("Headword", "Shookekineas", "e2e-sc18-headword-highlighted"),
    ("Gloss", "Behold", "e2e-sc18-gloss-highlighted"),
    ("FTS", "behold", "e2e-sc18-fts-highlighted"),
]

pytest.importorskip("playwright.sync_api")

pytestmark = [
    pytest.mark.playwright_e2e,
    pytest.mark.skipif(
        os.environ.get("SNEA_E2E", "") != "1",
        reason="live-app E2E — run with SNEA_E2E=1 while streamlit is up on :8501",
    ),
]


class _BrowserSession:
    """Chromium + page inside one worker thread (pytest 9 + anyio keeps an
    asyncio loop on the main thread; the Playwright sync API forbids entering
    under a running loop). Each SC-18 flow creates a FRESH context so session
    state starts clean — no preference toggle, no prior configuration."""

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
                    self._result_box.append(("result", fn(browser)))
                except BaseException as e:  # noqa: BLE001 — propagate verbatim
                    self._result_box.append(("error", e))
                self._done_evt.set()
            browser.close()

    def run(self, fn, timeout: float = 300.0):
        self._done_evt.clear()
        self._jobs.put(fn)
        if not self._done_evt.wait(timeout=timeout):
            raise TimeoutError(f"test body exceeded {timeout}s in worker thread")
        if not self._result_box:
            raise RuntimeError("worker returned no result")
        kind, value = self._result_box[0]
        if kind == "error":
            raise value
        return value

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


def _run_fresh_lexical_search(browser, mode: str, term: str, shot: str):
    """Fresh context (fresh session state) -> navigate -> select mode ->
    search -> return mark.search-token count."""
    context = browser.new_context()  # NO storage_state — fresh session state
    page = context.new_page()
    try:
        page.goto(APP_URL, wait_until="domcontentloaded")
        page.wait_for_selector('[data-testid="stTextInput"] input', state="visible", timeout=45_000)
        page.wait_for_timeout(2500)
        page.locator('[data-testid="stRadio"] label', has_text=mode).first.click()
        page.wait_for_timeout(2500)
        page.locator('[data-testid="stTextInput"] input').fill(term)
        page.locator('[data-testid="stBaseButton-secondary"]:has-text("🔍")').first.click()
        page.wait_for_function("() => document.body.textContent.includes('Search: ')", timeout=30_000)
        page.wait_for_timeout(3000)
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(ARTIFACTS_DIR / f"{shot}.png"))
        return page.evaluate(_COUNT_SEARCH_TOKENS)
    finally:
        context.close()


@pytest.mark.parametrize(("mode", "term", "shot"), MODE_CASES)
def test_sc18_marks_appear_in_fresh_session_per_lexical_mode(session, mode, term, shot):
    """SC-18: with an active lexical-mode query in a fresh session (no
    preference toggle, no prior configuration), the rendered block contains
    mark.search-token elements."""
    counts = session.run(lambda browser: _run_fresh_lexical_search(browser, mode, term, shot))
    assert counts > 0, (
        f"SC-18: no mark.search-token found in the rendered MDF block after a "
        f"fresh-session {mode}-mode search for '{term}' — highlighting did not "
        "auto-activate from the query alone."
    )
