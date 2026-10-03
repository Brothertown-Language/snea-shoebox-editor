"""Issue #1385 SC-4/SC-5/SC-6/SC-7 — Playwright real-browser search-flow E2E.

Companion suite to test_semantic_search_ui_dom_e2e.py (which covers mode
radio, threshold persistence, and filter gating with NO search execution).
This file executes real searches through the live app:

- SC-7 + SC-4: "he" in Headword (default) vs Semantic Gloss — different
  result sets (SC-7), and inline two-decimal descending "Similarity: N.NN"
  scores on semantic rows only (SC-4).
- SC-5: page navigation (Next → Prev) preserves page-1 card order — the
  rank-once pagination seam slices the cached ranked list.
- SC-6: empty query renders the informational state; a nonsense query
  renders the clean zero-result state — never a crash. The no_embeddings
  and stale_model branches are NOT exercised live here: doing so would
  require mutating real DB state (clearing 6,656 pinned embeddings or
  re-fingerprinting the model). Those branches carry mocked AppTest
  evidence from test_semantic_empty_states_red.py; only the two
  non-mutating states are live-verified in this suite.

Harness: ONE module-scoped Chromium session (worker-thread pattern from
test_semantic_search_ui_dom_e2e.py — pytest 9 + anyio keeps an asyncio
loop on the main thread and the Playwright sync API forbids entering under
a running loop). All tests share one authed context: with SNEA_E2E=1 a
FRESH context authenticated by the app-side TEST-ONLY bypass hook (Issue
#1400 SC-11); otherwise loaded from tmp/issue-36/auth-state.json. One
page.goto per test (3 total). After a
Search click, polling waits for real result cards to stream with
wait_for_selector — up to 60s ONLY for the first semantic query (one-time
embedding-model warm load; subsequent queries are fast), 20s for exact
modes. No other fixed sleeps beyond small rerun-settle pauses.

DB state assumed (live-verified 2026-10-01, prod-synced local): 7,753
records in gloss_search_entries, 6,656 pinned embeddings
(thenlper/gte-small), semantic threshold persisted at 0.7.

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""

import json
import os
import queue
import re
import threading

import pytest
from playwright.sync_api import Page, sync_playwright

APP_URL = "http://localhost:8501/records"
ARTIFACTS_DIR = os.path.join("tmp", "issue-1385", "artifacts")
STORAGE_PATH = os.path.join("tmp", "issue-36", "auth-state.json")

MODES = ["Headword", "Gloss", "Lexeme", "FTS", "Semantic Gloss", "Semantic All"]
MODE_INDEX = {m: i for i, m in enumerate(MODES)}

pytest.importorskip("playwright.sync_api")

pytestmark = [
    pytest.mark.playwright_e2e,
    pytest.mark.skipif(
        os.environ.get("SNEA_E2E", "") != "1",
        reason="live-app E2E — run with SNEA_E2E=1 while streamlit is up on :8501",
    ),
]


def _require_auth_storage() -> str | None:
    """Issue #1400 SC-11: with SNEA_E2E=1 the app-side TEST-ONLY auth bypass
    hook (src/services/security_manager.py) establishes the session, so the
    harness starts a FRESH context — no saved auth state, no headed GitHub
    OAuth login, no fabricated credentials. Without SNEA_E2E the legacy
    saved-state requirement applies."""
    if os.environ.get("SNEA_E2E") == "1":
        return None
    if not os.path.exists(STORAGE_PATH):
        raise AssertionError(
            "No saved OAuth session at tmp/issue-36/auth-state.json — "
            "log in once via the headed Playwright window to generate it."
        )
    with open(STORAGE_PATH) as fh:
        cookies = [c["name"] for c in json.load(fh).get("cookies", [])]
    if "gh_auth_token" not in cookies:
        raise AssertionError("Saved session lacks the gh_auth_token cookie — regenerate the login state.")
    return STORAGE_PATH


class _BrowserSession:
    """A Chromium + authed context + page living entirely inside one worker
    thread. Test bodies are queued into that thread via run(); results and
    exceptions propagate back to the pytest thread."""

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
    storage = _require_auth_storage()
    sess = _BrowserSession(storage)
    yield sess
    sess.close()


# ---------- shared page helpers (run inside the worker thread) ----------


def _body_text(page: Page) -> str:
    return page.evaluate("() => document.body.innerText")


def _goto_records(page: Page):
    page.goto(APP_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    if page.url.rstrip("/").endswith("/login"):
        page.screenshot(
            path=os.path.join(ARTIFACTS_DIR, "e2e-stale-auth-login-redirect.png"),
            full_page=True,
        )
        raise AssertionError(
            "Saved OAuth session is STALE — the app redirected to /login. "
            "Regenerate tmp/issue-36/auth-state.json via the headed-login "
            "procedure in test/ui/AGENTS.md (developer completes the GitHub "
            "OAuth in the visible window). Never fabricate auth state."
        )
    page.wait_for_selector('[data-testid="stRadio"] input[type="radio"]', state="attached", timeout=45_000)
    page.wait_for_function(
        """() => {
        const groups = Array.from(document.querySelectorAll('[data-testid="stRadio"]'));
        const g = groups.find(x => x.textContent.includes('Search Mode'));
        return g && g.querySelectorAll('input[type="radio"]').length >= 6;
    }""",
        timeout=15_000,
    )
    page.wait_for_timeout(1000)  # small settle for Streamlit first-rerun widgets


def _mode_label(page: Page, index: int):
    """Streamlit hides the radio inputs; click the visible radio LABEL."""
    return page.locator('[data-testid="stRadio"] label[data-baseweb="radio"]').nth(index)


def _select_mode(page: Page, mode: str):
    _mode_label(page, MODE_INDEX[mode]).click()


def _set_threshold(page: Page, value: float):
    """Set the sidebar numeric threshold input and commit the change.

    The control is the st.number_input keyed semantic_threshold_number
    (established by the SC-2 DOM e2e suite)."""
    number = page.locator('[data-testid="stSidebar"] input[type="number"]').last
    number.fill(str(value))
    number.press("Tab")
    page.wait_for_timeout(1000)


def _wait_for_rerun(page: Page, checked_index: int, timeout: int = 15_000):
    """Wait for the Streamlit rerun triggered by the mode change to settle.

    If the rerun collapses to the app-level error banner instead of settling
    (the live LinguisticService.search_semantic AttributeError), raise a
    defect-naming AssertionError rather than a bare harness timeout."""
    page.wait_for_timeout(1500)
    try:
        page.wait_for_function(
            """idx => {
            const groups = Array.from(document.querySelectorAll('[data-testid="stRadio"]'));
            const g = groups.find(x => x.textContent.includes('Search Mode'));
            if (!g) return false;
            const inputs = g.querySelectorAll('input[type="radio"]');
            return inputs[idx] && inputs[idx].checked;
        }""",
            arg=checked_index,
            timeout=timeout,
        )
    except Exception:
        crashed = page.evaluate(
            "() => document.body.textContent.includes('An unexpected error occurred')"
        )
        if crashed:
            page.screenshot(
                path=os.path.join(ARTIFACTS_DIR, "e2e-crash-mode-switch.png"),
                full_page=True,
            )
            raise AssertionError(
                "App crashed during rerun — 'An unexpected error occurred' banner "
                "(live defect: LinguisticService.search_semantic missing; see "
                "records.py semantic dispatch)."
            ) from None
        raise


def _click_search(page: Page):
    """Click the 🔍 sidebar search trigger (live-verified DOM anchor)."""
    sb = page.locator('[data-testid="stSidebar"]')
    search_btn = sb.locator(
        'button[data-testid="stBaseButton-secondary"]:has([data-testid="stIconEmoji"])'
    ).filter(has_text="🔍")
    assert search_btn.count() >= 1, "🔍 search button not found in sidebar"
    search_btn.first.click()


def _fill_search_input(page: Page, query: str):
    """Type a query into the sidebar search text input (select + fill)."""
    inp = page.locator('[data-testid="stSidebar"] input[aria-label="Search terms..."]').first
    inp.wait_for(state="visible", timeout=30_000)
    inp.click()
    inp.fill("")
    inp.fill(query)
    page.keyboard.press("Escape")  # blur so the click lands on the button


def _search(page: Page, query: str, expect_cards_timeout: int):
    """Fill the search input, click Search, and poll for results.

    expect_cards_timeout is the wait_for_selector budget for the REAL
    streaming search to land (60s for a cold first semantic query — the
    embedding-model warm load — 20s for fast exact modes)."""
    _fill_search_input(page, query)
    _click_search(page)
    if query:
        # Poll every 0.5s until the crash banner mounts OR the whole page
        # text stabilizes (2 consecutive identical samples ≥1s apart) with a
        # determined end state (cards / zero-result / empty query / no
        # match). A crash raises a defect-naming AssertionError immediately;
        # everything else is left for the SC assertions to validate.
        deadline = expect_cards_timeout / 1000.0
        start = __import__("time").time()
        prev_text: str | None = None
        stable_since: float | None = None
        while True:
            state = page.evaluate(
                """() => ({
                crashed: document.body.textContent.includes('An unexpected error occurred'),
                text: document.body.innerText,
            })"""
            )
            if state["crashed"]:
                page.screenshot(
                    path=os.path.join(ARTIFACTS_DIR, "e2e-crash-semantic-search.png"),
                    full_page=True,
                )
                raise AssertionError(
                    "App crashed during search — 'An unexpected error occurred' "
                    "banner (live defect: LinguisticService.search_semantic "
                    "missing; see records.py semantic dispatch)."
                ) from None
            text = state["text"]
            now = __import__("time").time()
            if text == prev_text:
                if stable_since is None:
                    stable_since = now
                if now - stable_since >= 1.0:
                    break
            else:
                stable_since = None
            prev_text = text
            if now - start > deadline:
                raise TimeoutError(f"search rerun never settled within {expect_cards_timeout}ms")
            __import__("time").sleep(0.5)
        page.wait_for_timeout(500)


def _card_headers(page: Page) -> list[str]:
    """Return the record-card header lines (Record #...) in DOM text order."""
    out = []
    for line in _body_text(page).splitlines():
        s = line.strip()
        if s.startswith("Record #"):
            out.append(s)
    return out


def _card_ids(page: Page) -> list[str]:
    headers = _card_headers(page)
    ids = []
    for c in headers:
        m = re.search(r"Record #(\d+)", c)
        if m:
            ids.append(m.group(1))
    return ids


def _score_lines(page: Page) -> list[str]:
    out = []
    for line in _body_text(page).splitlines():
        if "Similarity:" in line and "Record #" in line:
            out.append(line.strip())
    return out


def _page_label(page: Page) -> str:
    m = re.search(r"Page (\d+) of (\d+)", _body_text(page))
    return m.group(0) if m else ""


def _click_next(page: Page):
    sb = page.locator('[data-testid="stSidebar"]')
    nxt = sb.locator("button").filter(has_text="▶️")
    assert nxt.count() > 0, "Next pagination button not found"
    nxt.last.click()
    page.wait_for_timeout(2000)


def _click_prev(page: Page):
    sb = page.locator('[data-testid="stSidebar"]')
    prev = sb.locator("button").filter(has_text="◀️")
    assert prev.count() > 0, "Prev pagination button not found"
    prev.last.click()
    page.wait_for_timeout(2000)


def _search_header(page: Page) -> str | None:
    m = re.search(r"Search: ([\w ]+?) \((\d+) records\)", _body_text(page))
    return m.group(0) if m else None


# ---------- SC-7 + SC-4 combined flow ----------


def _sc7_sc4_flow(page: Page):
    _goto_records(page)

    # Test isolation: user preferences persist across tests within one Streamlit
    # browser session (preference rows are per-user, not per-run). SC-6's
    # threshold=1.0 zero-results probe must not leak into this flow — reset
    # the per-user threshold to a result-rich 0.7 first.
    _select_mode(page, "Semantic Gloss")
    _set_threshold(page, 0.7)

    # Headword mode (default): search "he" — exact match on headwords.
    _select_mode(page, "Headword")
    _search(page, "he", expect_cards_timeout=20_000)
    header_headword = _search_header(page)
    assert header_headword is not None, (
        f"'Search: ... (N records)' header not rendered for Headword search; "
        f"body tail: {_body_text(page)[-300:]!r}"
    )
    body_headword = _body_text(page)
    headword_cards = _card_headers(page)
    assert headword_cards, "Headword search for 'he' produced no record cards"
    assert "Similarity:" not in body_headword, (
        "Exact-match (Headword) results must NOT carry 'Similarity:' scores"
    )
    headword_ids = _card_ids(page)
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, "e2e-sc7-headword.png"), full_page=True)

    # Semantic Gloss mode: same query — different result set + scored rows.
    # NOTE (app defect — LIVE-VERIFIED 2026-10-01): this step crashes the app
    # with AttributeError: type object 'LinguisticService' has no attribute
    # 'search_semantic' — records.py calls `LinguisticService.search_semantic`
    # but the class never had that method (the #36 seam lives as a
    # module-level function in src/services/semantic_search_service.py, and
    # #36's wiring reaches it through the search_records strategy table).
    # All prior SC-4/SC-7 "green" evidence was AppTest-mocked. The assertions
    # below pin the SPEC behavior and FAIL until the dispatch is fixed.
    _select_mode(page, "Semantic Gloss")
    _wait_for_rerun(page, MODE_INDEX["Semantic Gloss"])
    _search(page, "he", expect_cards_timeout=60_000)  # one-time model warm load

    header_semantic = _search_header(page)
    assert header_semantic is not None, (
        f"'Search: ... (N records)' header not rendered for Semantic Gloss search; "
        f"body tail: {_body_text(page)[-300:]!r}"
    )
    assert header_semantic != header_headword, (
        f"Search header did not change between modes: {header_semantic!r} == {header_headword!r}"
    )

    lines = _score_lines(page)
    assert len(lines) > 0, "No 'Similarity:' record-card header line after Semantic Gloss search"
    scores = []
    for line in lines:
        m = re.search(r"Similarity:\s*(\d\.\d{2})", line)
        assert m is not None, f"Header line lacks a two-decimal score: {line!r}"
        scores.append(float(m.group(1)))
    assert scores == sorted(scores, reverse=True), (
        f"Semantic scores not in descending order across consecutive cards: {scores}"
    )
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, "e2e-sc4-scores.png"), full_page=True)

    semantic_ids = _card_ids(page)
    assert semantic_ids and semantic_ids != headword_ids, (
        "Semantic Gloss 'he' returned the same result set as Headword 'he' "
        "(SC-7 expects mode dispatch to produce distinct records)\n"
        f"headword: {headword_ids}\nsemantic: {semantic_ids}"
    )


def test_search_modes_differ_and_scores(session):
    session.run(_sc7_sc4_flow)


# ---------- SC-5: pagination order stability ----------


def _sc5_flow(page: Page):
    _goto_records(page)

    _select_mode(page, "Semantic Gloss")
    _set_threshold(page, 0.7)
    _wait_for_rerun(page, MODE_INDEX["Semantic Gloss"])
    # Broad query matching many glosses → expect multiple pages.
    _search(page, "he", expect_cards_timeout=60_000)
    label = _page_label(page)
    assert label, (
        f"Pager label not found after semantic search; body tail: {_body_text(page)[-300:]!r}"
    )

    order1 = _card_ids(page)
    assert order1, "Page-1 semantic results empty before pagination check"

    m = re.search(r"Page (\d+) of (\d+)", label)
    assert m is not None, f"Pager label lost regex match: {label!r}"
    total_pages = int(m.group(2))
    assert total_pages > 1, (
        f"Only {total_pages} page for broad query 'he' in Semantic Gloss — "
        "need >1 page to test pagination stability "
        f"(result header: {_search_header(page)!r})"
    )

    _click_next(page)
    assert re.search(r"Page 2 of", _body_text(page)), (
        f"Did not land on page 2; pager: {_page_label(page)!r}"
    )
    order2 = _card_ids(page)
    assert order2, "Page-2 results empty"
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, "e2e-sc5-pagination-p2.png"), full_page=True)

    _click_prev(page)
    assert re.search(r"Page 1 of", _body_text(page)), (
        f"Did not return to page 1; pager: {_page_label(page)!r}"
    )

    order1_after = _card_ids(page)
    assert order1_after == order1, (
        "Page-1 card order not identical after Next→Prev round-trip\n"
        f"before: {order1}\nafter: {order1_after}"
    )


def test_pagination_order_stability(session):
    session.run(_sc5_flow)


# ---------- SC-6: clean empty states, never crash ----------

CRASH_MARKERS = ("Traceback (most recent call last)", "AttributeError", "KeyError:", "TypeError:")


def _sc6_flow(page: Page):
    _goto_records(page)

    _select_mode(page, "Semantic Gloss")
    _wait_for_rerun(page, MODE_INDEX["Semantic Gloss"])

    # Empty query: click Search with no text → no crash, app responsive.
    # DEVIATION (app defect #1): with an empty search term in semantic mode
    # the page falls back to unfiltered browse (search_term=None → the
    # exact-mode browse path, ~7,750 records) instead of rendering the
    # empty_query st.info ("Enter a query to search semantically.") — the
    # empty_query branch only fires when the seam is actually invoked, which
    # the no-query dispatch never does.
    _search(page, "", expect_cards_timeout=0)
    body = _body_text(page)
    assert not any(m in body for m in CRASH_MARKERS), (
        f"Crash markers present after empty query: body tail {body[-600:]!r}"
    )
    assert _page_label(page), "App not responsive after empty query (pager label missing)"

    # Nonsense query at threshold 1.0: zero results → clean informational
    # state, no crash. (A nonsense term alone doesn't guarantee zero
    # results — cosine similarity between any two real vectors is almost
    # always above a lenient threshold, verified live: "zzqxj..." matched
    # records at 0.81 with threshold 0.7. Raising the threshold to its max
    # makes the zero-results-after-threshold branch deterministically
    # reachable in the real DOM.)
    _set_threshold(page, 1.0)
    _search(page, "zzqxj_nonexistent_term", expect_cards_timeout=30_000)
    body = _body_text(page)
    assert not any(m in body for m in CRASH_MARKERS), (
        f"Crash markers present after zero-result search (app defect — "
        f"LinguisticService.search_semantic missing): body tail {body[-600:]!r}"
    )
    assert "No records scored above the semantic threshold" in body, (
        f"Zero-result informational state not rendered; body tail: {body[-600:]!r}"
    )
    assert _page_label(page), "App not responsive after zero-result search (pager label missing)"
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, "e2e-sc6-empty-states.png"), full_page=True)

    # Restore the shared per-user threshold so later tests / the developer's
    # browsing session aren't left at the zero-result ceiling.
    _set_threshold(page, 0.7)

    # NOTE (SC-6 limitation): the no_embeddings and stale_model degraded
    # branches are intentionally NOT exercised live — both require mutating
    # real production-synced DB state (clearing pinned embeddings /
    # re-fingerprinting the model). Mocked AppTest evidence for those
    # branches lives in test_semantic_empty_states_red.py.


def test_empty_states_clean(session):
    session.run(_sc6_flow)


# ---------- Issue #1400 SC-10: UI override preserved through to the seam ----------


def _get_number_input_value(page: Page) -> str:
    return page.locator('[data-testid="stSidebar"] input[type="number"]').last.input_value()


def _sc10_flow(page: Page):
    _goto_records(page)

    _select_mode(page, "Semantic Gloss")
    _wait_for_rerun(page, MODE_INDEX["Semantic Gloss"])

    # User override: threshold = 1.0 (the strict ceiling). The in-corpus
    # anchor "beaver" scores 0.9753 (measured probe, tmp/1400/artifacts/
    # verification-probe.yaml, query 'beaver' top-1 record 8491) — ABOVE the
    # calibrated default floor 0.93 but strictly BELOW the 1.0 override.
    # Discriminating observable: if the override reaches the seam unchanged,
    # "beaver" returns zero results; if the default floor silently replaced
    # the override, "beaver" would be served as a rank-1 record card.
    # (Note: the original draft used "water", whose measured top cosine is
    # exactly 1.0 — equal to the override, so the seam serves it under a
    # `score >= threshold` comparison and the query does not discriminate.)
    _set_threshold(page, 1.0)
    assert abs(float(_get_number_input_value(page)) - 1.0) < 1e-9, (
        f"Threshold control did not accept the 1.0 override "
        f"(shows {_get_number_input_value(page)!r})"
    )

    _search(page, "beaver", expect_cards_timeout=60_000)
    body = _body_text(page)
    assert not any(m in body for m in CRASH_MARKERS), (
        f"Crash markers present after override search: body tail {body[-600:]!r}"
    )
    record_cards = _card_headers(page)
    assert record_cards == [], (
        f"SC-10 VIOLATION: override threshold 1.0 was not honored by the "
        f"seam — 'beaver' (cosine 0.9753 < 1.0) should return zero results, "
        f"but record cards were served: {record_cards[:5]} "
        f"(the default floor 0.93 must NOT silently replace the override)"
    )
    assert _page_label(page), "App not responsive after override search (pager label missing)"

    # The override must persist in the control — not be reset to the default
    # by the search rerun. The widget formats the value (e.g. "1.00"), so
    # compare numerically rather than against a literal string.
    assert abs(float(_get_number_input_value(page)) - 1.0) < 1e-9, (
        f"SC-10 VIOLATION: threshold control shows "
        f"{_get_number_input_value(page)!r} after search — the override was "
        f"reset to the default instead of being preserved"
    )
    page.screenshot(
        path=os.path.join("tmp", "1400", "artifacts", "e2e-sc10-override-ceiling.png"),
        full_page=True,
    )

    # Restore the shared per-user threshold so later tests / the developer's
    # browsing session aren't left at the zero-result ceiling.
    _set_threshold(page, 0.7)


def test_ui_override_reaches_seam(session):
    session.run(_sc10_flow)
