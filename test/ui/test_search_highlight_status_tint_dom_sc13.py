"""Issue #1401 SC-13 — Playwright real-browser DOM + computed-style assertion:
status line tints render UNCHANGED when search-token highlighting is active.

Flow (gated by ``playwright_e2e`` marker + ``SNEA_E2E=1``, live app on :8501,
test-only auth bypass per docs/development/ui_testing_standard.md):

1. Baseline render: unfiltered browse (empty query) — records render with
   structural-highlighting status lines (``.mdf-line.status-*`` tints defined
   in ``src/frontend/ui_utils.py``) and, per SC-19, no ``mark.search-token``.
   Capture the computed ``background-color`` of every tinted status line.
2. Highlighted render: execute a lexical search producing
   ``mark.search-token`` elements in the rendered block; capture status tints
   again and compare against the baseline.
3. Assert: ``mark.search-token`` present AND every tinted status class's
   computed background-color set is identical between the two renders.

Pre-GREEN (highlight wiring not yet active on the Records page) the
gate-enabled run MUST FAIL — the assertion cannot yet be satisfied (no
``mark.search-token`` in the rendered block). Without the gate the test
records SKIPPED by design — plain ``pytest test/`` stays green serverless.

Worker-thread pattern per test/ui/AGENTS.md harness conventions.

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

import os
import queue
import threading

import pytest
from playwright.sync_api import Page, sync_playwright

APP_URL = "http://localhost:8501/records"
HEALTH_URL = "http://localhost:8501/_stcore/health"
ARTIFACTS_DIR = os.path.join("tmp", "issue-1401", "artifacts")
STORAGE_PATH = os.path.join("tmp", "issue-36", "auth-state.json")

# Search term executed against the synced local DB (overridable per run).
# Verified live (2026-10-02): Lexeme search for 'kekineas' returns 5 records.
SEARCH_TERM = os.environ.get("SNEA_E2E_SEARCH_TERM", "kekineas")

pytest.importorskip("playwright.sync_api")

pytestmark = [
    pytest.mark.playwright_e2e,
    pytest.mark.skipif(
        os.environ.get("SNEA_E2E", "") != "1",
        reason="live-app E2E — run with SNEA_E2E=1 while streamlit is up on :8501",
    ),
]

# Status classes with defined tint CSS in src/frontend/ui_utils.py
# (status-ok is unstyled and excluded).
TINTED_STATUS_SELECTOR = (
    '.mdf-line.status-suggestion, .mdf-line.status-note, .mdf-line.status-error,'
    ' .mdf-line.status-warning, .mdf-line.status-diff-changed,'
    ' .mdf-line.status-diff-added, .mdf-line.status-diff-removed'
)


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


def _collect_tints(page: Page) -> dict[str, list[str]]:
    """Per status-class computed background-colors from the main document.
    Verified live (Streamlit 1.54): st.html renders INLINE in the main
    document — no iframes — so .mdf-wrap-block and status lines live there."""
    return page.evaluate(
        """sel => {
        const out = {};
        for (const el of document.querySelectorAll(sel)) {
            const cls = [...el.classList].find(c => c.startsWith('status-')) || 'unknown';
            const bg = getComputedStyle(el).backgroundColor;
            (out[cls] = out[cls] || []).push(bg);
        }
        for (const k of Object.keys(out)) out[k].sort();
        return out;
    }""",
        TINTED_STATUS_SELECTOR,
    )


def _has_search_token(page: Page) -> bool:
    return page.evaluate(
        "() => document.querySelectorAll('.mdf-wrap-block mark.search-token').length > 0"
    )


def _sc13_flow(page: Page):
    page.goto(APP_URL, wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="stTextInput"] input', state="visible", timeout=45_000)
    page.wait_for_timeout(2500)

    # Baseline render: unfiltered browse, no highlight active (SC-19).
    baseline = _collect_tints(page)
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, "e2e-sc13-baseline.png"))

    # Execute a lexical search → highlighted render.
    # Search Mode is a radio: select Lexeme (lexical mode, verified live to
    # return records for the default term), then fill the query and submit.
    page.locator('[data-testid="stRadio"] label', has_text="Lexeme").first.click()
    page.wait_for_timeout(2500)
    page.locator('[data-testid="stTextInput"] input').fill(SEARCH_TERM)
    page.wait_for_timeout(500)
    page.locator('[data-testid="stBaseButton-secondary"]:has-text("🔍")').first.click()
    page.wait_for_timeout(3000)
    # Results header: "Search: {mode} (N records)" — mode-dependent, term-free.
    page.wait_for_function(
        """() => /Search: .+\\(\\d+ records\\)/.test(document.body.textContent)""",
        timeout=30_000,
    )
    page.wait_for_timeout(1500)

    highlighted = _collect_tints(page)
    token_found = _has_search_token(page)
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, "e2e-sc13-highlighted.png"))

    # Assertion 1 (RED today): highlight must actually be active.
    assert token_found, (
        "SC-13 RED: no mark.search-token in the rendered MDF block DOM after "
        f"searching '{SEARCH_TERM}' — search highlighting is not yet wired into "
        "the Records View-mode render, so tint non-interference cannot be "
        "asserted yet."
    )

    # Assertion 2: status tint VALUES unchanged between renders. The two
    # phases render different record populations (browse vs filtered search),
    # so compare the distinct value SET per class, not list lengths. A class
    # present in only one phase has nothing to compare — record it only if
    # that phase's values are inconsistent among themselves.
    drift = []
    for cls in sorted(set(baseline) | set(highlighted)):
        base_vals = sorted(set(baseline.get(cls) or []))
        high_vals = sorted(set(highlighted.get(cls) or []))
        if base_vals and high_vals and base_vals != high_vals:
            drift.append(f"{cls}: baseline={base_vals} highlighted={high_vals}")
    assert not drift, (
        "SC-13 RED: status line tints changed when search-token highlighting "
        "is active — search-token styling bleeds into status line rendering: "
        + "; ".join(drift)
    )

    # A tinted status line must exist in at least one render for the
    # comparison to be meaningful (vacuous-pass guard).
    assert baseline or highlighted, (
        "SC-13: no tinted status lines found in either render — the tint "
        "comparison is vacuous; check fixture data and structural highlighting."
    )


def test_sc13_status_tints_unchanged_with_highlight(session):
    session.run(_sc13_flow)


def test_sc13_gate_absent_variant_skips_by_design(session):
    """Gate-absent variant: without SNEA_E2E=1 this test (and the gated SC-13
    suite) is SKIPPED BY DESIGN — never silently treated as a pass. With the
    gate present it verifies the live-app precondition the gated run relies
    on (health endpoint 200)."""
    if os.environ.get("SNEA_E2E", "") != "1":
        pytest.skip(
            "SC-13 gate-absent variant: skipped by design — live-app E2E "
            "requires SNEA_E2E=1 with the app up on :8501"
        )

    def _health(page: Page):
        page.goto(HEALTH_URL, wait_until="domcontentloaded")
        body = page.locator("body").inner_text()
        assert "ok" in body.lower(), f"SC-13: live app health not ok: {body!r}"

    session.run(_health)