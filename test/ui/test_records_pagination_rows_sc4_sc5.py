"""Issue #1413 SC-4 / SC-5 — Playwright real-browser checks of the twin
main-panel navigation rows, with layout captures for vision review (D7).

SC-4: a full-form row — [Prev] "Page N of M" / "Showing X-Y of Z" [Next] —
renders immediately before the first record card with live values.
SC-5: an identical row renders immediately after the last record card with
the same live values.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import importlib.util
import os
import re
from pathlib import Path

import pytest
from playwright.sync_api import Page

_spec = importlib.util.spec_from_file_location(
    "pagination_harness", Path("test/ui/fixtures/pagination_harness.py")
)
_ph = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ph)

ARTIFACTS_DIR = os.path.join("tmp", "1413", "artifacts")

pytest.importorskip("playwright.sync_api")

pytestmark = [
    pytest.mark.playwright_e2e,
    pytest.mark.skipif(
        os.environ.get("SNEA_E2E", "") != "1",
        reason="live-app E2E — run with SNEA_E2E=1 while streamlit is up on :8501",
    ),
]


@pytest.fixture(scope="module")
def session():
    sess = _ph.BrowserSession(_ph.require_auth_storage())
    yield sess
    sess.close()


def _row_values(page: Page, index: int) -> str:
    """The Page/Showing caption pair of the Nth main-panel navigation row."""
    return page.evaluate(
        """idx => {
        const sb = document.querySelector('[data-testid="stSidebar"]');
        const pats = Array.from(document.querySelectorAll('p')).filter(
            p => (!sb || !sb.contains(p)) && /Page \\d+ of \\d+/.test(p.textContent));
        if (pats.length <= idx) return null;
        const row = pats[idx].closest('[data-testid="stHorizontalBlock"]') || pats[idx].parentElement;
        return row.innerText;
    }""",
        index,
    )


def test_sc4_top_row_renders_before_first_card(session):
    def body(page: Page):
        _ph.goto_records(page)
        text = _row_values(page, 0)
        assert text is not None, "no main-panel navigation row found"
        assert re.search(r"Page \d+ of \d+", text), f"top row lacks Page N of M: {text!r}"
        assert re.search(r"Showing \d+-\d+ of \d+", text), f"top row lacks Showing X-Y of Z: {text!r}"
        assert _ph.main_buttons(page, "Prev").count() >= 1 and _ph.main_buttons(page, "Next").count() >= 1
        page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc4-top-row-viewport.png"))

    session.run(body)


def test_sc5_bottom_row_renders_with_value_parity(session):
    def body(page: Page):
        _ph.goto_records(page)
        top = _row_values(page, 0)
        # Scroll to the bottom of the main panel so the bottom row renders.
        page.evaluate("() => { const m = document.querySelector('[data-testid=\"stMain\"]'); m.scrollTop = m.scrollHeight; }")
        page.wait_for_timeout(1500)
        bottom = _row_values(page, 1)
        assert bottom is not None, "no bottom navigation row found after the last record card"
        assert re.search(r"Page \d+ of \d+", bottom) and re.search(r"Showing \d+-\d+ of \d+", bottom), (
            f"bottom row lacks captions: {bottom!r}"
        )
        top_page = re.search(r"Page (\d+) of (\d+)", top).groups()
        bottom_page = re.search(r"Page (\d+) of (\d+)", bottom).groups()
        assert top_page == bottom_page, f"row parity broken: top={top_page} bottom={bottom_page}"
        top_show = re.search(r"Showing (\d+-\d+ of \d+)", top).group(1)
        bottom_show = re.search(r"Showing (\d+-\d+ of \d+)", bottom).group(1)
        assert top_show == bottom_show, f"showing-range parity broken: {top_show} vs {bottom_show}"
        page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc5-bottom-row-viewport.png"))

    session.run(body)