"""Regression guard: the fixed header must not intercept the main panel's
scrollbar track.

Issue found in review (2026-10-05): the 60px fixed stHeader (z-index 999990)
overlays the top of the stMain scrollbar track, so when the page is near the
top the thumb is ungrabbable and hover never fires — the scrollbar appears
"hidden" when the user reaches for it. Fix: pointer-events: none on the
header and its descendants, re-enabled on interactive controls (buttons,
links, inputs, status widget).

Assertions (real-browser DOM):
1. elementFromPoint in the scrollbar's top strip resolves to the main-panel
   content (not the header/toolbar).
2. A mouse wheel at the top strip scrolls the main panel.
3. A header button still receives a real mouse click (Playwright hit-testing
   fails on intercepted clicks, so a completed click proves the event reached
   the control).

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import os
import threading

import pytest
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:8501/records"

pytest.importorskip("playwright.sync_api")

pytestmark = [
    pytest.mark.playwright_e2e,
    pytest.mark.skipif(
        os.environ.get("SNEA_E2E", "") != "1",
        reason="live-app E2E — run with SNEA_E2E=1 while streamlit is up on :8501",
    ),
]


def _run_in_worker(fn, timeout=120.0):
    box: list = []

    def target():
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_context(viewport={"width": 1280, "height": 900}).new_page()
                fn(page)
                browser.close()
                box.append(None)
        except BaseException as e:  # noqa: BLE001 — propagate verbatim
            box.append(e)

    t = threading.Thread(target=target)
    t.start()
    t.join(timeout)
    err = box[0] if box else TimeoutError("worker thread timed out")
    if err is not None:
        raise err


def _goto_records(page):
    page.goto(APP_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)


def _probe_top_strip(page) -> str:
    return page.evaluate(
        """() => {
        const m = document.querySelector('[data-testid="stMain"]');
        const r = m.getBoundingClientRect();
        const el = document.elementFromPoint(r.right - 6, 30);
        return el ? el.tagName + (el.getAttribute('data-testid') ? '#' + el.getAttribute('data-testid') : '') : null;
    }"""
    )


def test_header_does_not_intercept_scrollbar_top_strip():
    def flow(page):
        _goto_records(page)
        scrollable = page.evaluate(
            "() => { const m = document.querySelector('[data-testid=\"stMain\"]');"
            " return m.scrollHeight > m.clientHeight; }"
        )
        assert scrollable, "precondition: the Records page main panel must have scrollable content"
        top = _probe_top_strip(page)
        assert top and "stHeader" not in top and "stToolbar" not in top, (
            f"the header/toolbar still intercepts the scrollbar's top strip (elementFromPoint → {top!r})"
        )
        # Wheel scroll with the pointer at the top strip must scroll the panel.
        page.evaluate("() => { const m = document.querySelector('[data-testid=\"stMain\"]'); m.scrollTop = 0; }")
        page.mouse.move(1274, 30)
        page.mouse.wheel(0, 800)
        page.wait_for_timeout(600)
        assert page.evaluate("() => document.querySelector('[data-testid=\"stMain\"]').scrollTop") > 0, (
            "wheel at the scrollbar's top strip did not scroll the main panel"
        )

    _run_in_worker(flow)


def test_header_buttons_still_receive_clicks():
    def flow(page):
        _goto_records(page)
        # Playwright click performs hit-testing: a completed click proves the
        # event reached the button rather than an overlaying interceptor.
        page.locator('header[data-testid="stHeader"] button').first.click(timeout=10_000)

    _run_in_worker(flow)
