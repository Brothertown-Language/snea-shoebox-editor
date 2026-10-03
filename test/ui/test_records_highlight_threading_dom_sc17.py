"""Issue #1401 SC-17 — Playwright real-browser behavioral test: the View-mode
``render_mdf_block`` call on the Records page must be the ONLY call site that
receives highlight context (query, mode, computed spans/matched_terms), and a
lexical search must therefore produce ``mark.search-token`` elements in the
View-mode rendered block DOM — while revision-history and import-diff render
call sites never receive highlight parameters (no search-token in those
renders).

Evidence mix (per SC-17 evidence type = behavioral):
1. Source inspection (ast): the View-mode call (key=f"render_{record_id}") in
   ``src/frontend/pages/records.py`` must thread highlight parameters. RED:
   fails pre-GREEN because the call omits them.
2. Source inspection (ast): the revision-history call (key=f"hist_...") in
   records.py and both import-diff call sites in ``upload_mdf.py`` must NOT
   receive highlight parameters.
3. DOM (Playwright): after a lexical search on the live app, at least one
   ``mark.search-token`` exists in a rendered block iframe. RED: fails
   pre-GREEN (no highlight threading).
4. DOM (Playwright): no ``mark.search-token`` inside any Revision History
   expander render, even post-GREEN.

Gated by the ``playwright_e2e`` marker + ``SNEA_E2E=1`` (live app on :8501,
test-only auth bypass per docs/development/ui_testing_standard.md). Without
the gate the test records SKIPPED by design.

Worker-thread pattern per test/ui/AGENTS.md harness conventions.

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

import ast
import os
import queue
import threading
from pathlib import Path

import pytest
from playwright.sync_api import Page, sync_playwright

APP_URL = "http://localhost:8501/records"
ARTIFACTS_DIR = Path("tmp") / "issue-1401" / "artifacts"
RECORDS_PY = Path("src/frontend/pages/records.py")
UPLOAD_MDF_PY = Path("src/frontend/pages/upload_mdf.py")

SEARCH_TERM = os.environ.get("SNEA_E2E_SEARCH_TERM", "kekineas")

pytest.importorskip("playwright.sync_api")

pytestmark = [
    pytest.mark.playwright_e2e,
    pytest.mark.skipif(
        os.environ.get("SNEA_E2E", "") != "1",
        reason="live-app E2E — run with SNEA_E2E=1 while streamlit is up on :8501",
    ),
]


def _render_mdf_block_calls(tree: ast.AST) -> list[dict]:
    """Extract render_mdf_block call sites: keyword names + a source snippet."""
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "render_mdf_block":
            key_value = ""
            for kw in node.keywords:
                if kw.arg == "key" and kw.value is not None:
                    try:
                        key_value = ast.unparse(kw.value)
                    except Exception:  # noqa: BLE001 — best-effort snippet
                        key_value = ""
            calls.append(
                {
                    "line": node.lineno,
                    "keywords": sorted(kw.arg for kw in node.keywords if kw.arg),
                    "key_value": key_value,
                    "snippet": ast.unparse(node)[:200],
                }
            )
    return calls


HIGHLIGHT_KWARGS = {"highlight_spans", "highlight_query", "highlight_mode", "matched_terms", "highlight_terms"}


def _classify_calls(calls: list[dict], key_substring: str) -> list[dict]:
    return [c for c in calls if key_substring in c.get("key_value", "")]


def test_sc17_view_mode_call_threads_highlight_context():
    """Source inspection RED: the View-mode render call must receive highlight params."""
    tree = ast.parse(RECORDS_PY.read_text(encoding="utf-8"))
    calls = _render_mdf_block_calls(tree)
    assert calls, "no render_mdf_block calls found in records.py"

    view_calls = _classify_calls(calls, "render_")
    assert view_calls, "View-mode render call (key=render_{record_id}) not found in records.py"

    threading_calls = [c for c in view_calls if HIGHLIGHT_KWARGS & set(c["keywords"])]
    assert threading_calls, (
        "SC-17 RED: the View-mode render_mdf_block call in records.py does not thread "
        f"highlight context (query/mode/computed spans). Call sites: {view_calls}"
    )


def test_sc17_revision_history_and_import_diff_calls_omit_highlight():
    """Source inspection: revision-history + import-diff call sites must NOT get highlight params."""
    offenders = []

    records_tree = ast.parse(RECORDS_PY.read_text(encoding="utf-8"))
    for call in _render_mdf_block_calls(records_tree):
        if "hist_" in call.get("key_value", ""):
            if HIGHLIGHT_KWARGS & set(call["keywords"]):
                offenders.append({"file": str(RECORDS_PY), **call})

    upload_tree = ast.parse(UPLOAD_MDF_PY.read_text(encoding="utf-8"))
    for call in _render_mdf_block_calls(upload_tree):
        if HIGHLIGHT_KWARGS & set(call["keywords"]):
            offenders.append({"file": str(UPLOAD_MDF_PY), **call})

    assert not offenders, (
        "SC-17: revision-history/import-diff render call sites must not receive highlight "
        f"parameters, but found: {offenders}"
    )


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
    sess = _BrowserSession()
    yield sess
    sess.close()


def _run_lexical_search(page: Page):
    page.goto(APP_URL, wait_until="domcontentloaded")
    # The SNEA_E2E bypass lands on Records directly (same flow as SC-13).
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


_COUNT_SEARCH_TOKENS = """() => {
    // Streamlit renders st.html blocks inline in the main document (no iframes).
    // Count marks in the main document AND inside same-origin iframes, for both.
    let total = 0;
    const scoped = [];
    const countIn = (doc) => {
        const n = doc.querySelectorAll('.mdf-wrap-block mark.search-token').length;
        total += n;
        if (n > 0) {
            // Walk up to find an enclosing expander labelled Revision History.
            const roots = doc.querySelectorAll('.mdf-wrap-block mark.search-token');
            for (const mark of roots) {
                let el = mark, inHist = false;
                while (el && el !== doc.body) {
                    const isExpander = el.tagName === 'DETAILS' ||
                        (el.hasAttribute && el.getAttribute('data-testid') === 'stExpander');
                    if (isExpander) {
                        // Only the expander's own label counts, not container text.
                        const label = el.querySelector('summary, [data-testid="stExpanderDetails"], [data-testid="stExpanderToggle"]');
                        const text = (label ? label.textContent : el.textContent) || '';
                        if (text.includes('Revision History')) { inHist = true; break; }
                    }
                    el = el.parentElement;
                }
                if (inHist) scoped.push(true);
            }
        }
    };
    countIn(document);
    for (const frame of document.querySelectorAll('iframe')) {
        try {
            const doc = frame.contentDocument;
            if (doc) countIn(doc);
        } catch (e) {}
    }
    // Revision-history renders live inside <details> expanders; count marks there.
    let historyTokens = 0;
    historyTokens += document.querySelectorAll('details .mdf-wrap-block mark.search-token').length;
    for (const frame of document.querySelectorAll('iframe')) {
        try {
            const doc = frame.contentDocument;
            if (doc) historyTokens += doc.querySelectorAll('details .mdf-wrap-block mark.search-token').length;
        } catch (e) {}
    }
    return {total, historyTokens};
}"""


def test_sc17_search_token_in_view_mode_block_dom(session):
    """DOM RED: a lexical search must produce mark.search-token in the rendered block."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    def flow(page: Page):
        _run_lexical_search(page)
        counts = page.evaluate(_COUNT_SEARCH_TOKENS)
        page.screenshot(path=str(ARTIFACTS_DIR / "e2e-sc17-view-mode-search-token.png"))
        assert counts["total"] > 0, (
            "SC-17 RED: no mark.search-token element found in any rendered MDF block "
            f"DOM after searching '{SEARCH_TERM}' — the View-mode render call does not "
            "thread highlight context."
        )

    session.run(flow)


def test_sc17_no_search_token_in_revision_history(session):
    """DOM: no mark.search-token inside any Revision History expander render."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    def flow(page: Page):
        _run_lexical_search(page)
        counts = page.evaluate(_COUNT_SEARCH_TOKENS)
        page.screenshot(path=str(ARTIFACTS_DIR / "e2e-sc17-revision-history-no-tokens.png"))
        assert counts["historyTokens"] == 0, (
            "SC-17: mark.search-token found inside a Revision History expander render — "
            "highlight context must not reach revision-history render call sites."
        )

    session.run(flow)