"""Issue #1401 SC-21 — Playwright real-browser END-TO-END flow test: a full
user path from search submission through the rendered MDF block on the live
app. Distinct from test_records_auto_activation_dom_sc18.py (which asserts
per-mode auto-activation by mark COUNT only): SC-21 composes the complete
flow — submit search -> results render -> at least one ``mark.search-token``
in the rendered block whose TEXT CONTENT actually contains the searched term
(case-insensitive), proving the marks mark the term, not just any mark.

Verified across all four lexical modes (Lexeme, Headword, Gloss, FTS) with
terms verified against the local DB replica (same terms as SC-18):
- Lexeme   "kekineas"     -> record 3657 (lexeme Shookekineas)
- Headword "Shookekineas" -> headword_search_entries record 3657
- Gloss    "Behold"       -> gloss_search_entries ("Behold here.")
- FTS      "behold"       -> fts_entries hits via to_tsquery('simple','behold:*')

Case-insensitivity rationale: the searched term may be matched case-
insensitively by the backend and rendered with source casing (e.g. gloss
"Behold" for an FTS search of "behold"), so mark text containment is
compared with ``text.lower().find(term.lower())``.

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
    ("Lexeme", "kekineas", "e2e-sc21-lexeme-flow"),
    ("Headword", "Shookekineas", "e2e-sc21-headword-flow"),
    ("Gloss", "Behold", "e2e-sc21-gloss-flow"),
    ("FTS", "behold", "e2e-sc21-fts-flow"),
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
    under a running loop). Each SC-21 flow runs in a FRESH context."""

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

# Collect mark.search-token TEXT CONTENTS from the rendered MDF blocks —
# searched across the main document and all same-origin iframes.
_COLLECT_MARK_TEXTS = """() => {
    const texts = [];
    const collect = (doc) => {
        doc.querySelectorAll('.mdf-wrap-block mark.search-token').forEach(
            (m) => texts.push(m.textContent)
        );
    };
    collect(document);
    for (const frame of document.querySelectorAll('iframe')) {
        try {
            const doc = frame.contentDocument;
            if (doc) collect(doc);
        } catch (e) {}
    }
    return texts;
}"""


def _run_full_search_flow(browser, mode: str, term: str, shot: str):
    """SC-21 full user path: fresh context -> navigate -> select mode ->
    fill search box -> submit -> results render -> return
    (mark count, list of mark text contents)."""
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
        # Step 2: results actually rendered — the "Search: " status line appears.
        page.wait_for_function("() => document.body.textContent.includes('Search: ')", timeout=30_000)
        page.wait_for_timeout(3000)
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(ARTIFACTS_DIR / f"{shot}.png"))
        mark_count = page.evaluate(_COUNT_SEARCH_TOKENS)
        mark_texts = page.evaluate(_COLLECT_MARK_TEXTS)
        return mark_count, mark_texts
    finally:
        context.close()


@pytest.mark.parametrize(("mode", "term", "shot"), MODE_CASES)
def test_sc21_full_flow_marks_contain_searched_term(session, mode, term, shot):
    """SC-21: the full user path — submit search, results render, and the
    rendered block contains mark.search-token elements whose text content
    actually contains the searched term (case-insensitive)."""
    mark_count, mark_texts = session.run(
        lambda browser: _run_full_search_flow(browser, mode, term, shot)
    )
    assert mark_count > 0, (
        f"SC-21: no mark.search-token found in the rendered MDF block after "
        f"submitting a {mode}-mode search for '{term}' — the full search-to-"
        "highlight flow did not produce highlighted marks."
    )
    term_lower = term.lower()
    matching = [t for t in mark_texts if term_lower in t.lower()]
    assert matching, (
        f"SC-21: {mark_count} mark.search-token element(s) rendered after a "
        f"{mode}-mode search for '{term}', but NONE of their text contents "
        f"contain the searched term — marks present: {mark_texts[:10]!r}. "
        "The marks must wrap the searched term itself."
    )
