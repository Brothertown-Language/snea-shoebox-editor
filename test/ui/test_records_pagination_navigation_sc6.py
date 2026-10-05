"""Issue #1413 SC-6 — Playwright e2e click-through: navigation from either row.

Top-row Next advances the page, bottom-row Prev returns to the previous page,
captions update in both rows with parity for the same page, and boundary
disabling holds in both rows (Prev at page 1, Next at the last page).

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


def _page_caption(page: Page, row_index: int) -> str:
    val = page.evaluate(
        """idx => {
        const sb = document.querySelector('[data-testid="stSidebar"]');
        const pats = Array.from(document.querySelectorAll('p')).filter(
            p => (!sb || !sb.contains(p)) && /Page \\d+ of \\d+/.test(p.textContent));
        return pats.length > idx ? pats[idx].innerText : null;
    }""",
        row_index,
    )
    assert val is not None, f"navigation row {row_index} not found"
    return val


def _click_top_next(page: Page):
    _ph.main_buttons(page, "Next").first.click()
    page.wait_for_timeout(2500)


def _click_bottom_prev(page: Page):
    _ph.main_buttons(page, "Prev").last.click()
    page.wait_for_timeout(2500)


def test_top_next_advances_bottom_prev_returns(session):
    def body(page: Page):
        _ph.goto_records(page)
        start = _page_caption(page, 0)
        _click_top_next(page)
        after = _page_caption(page, 0)
        n_start, n_after = int(re.search(r"Page (\d+)", start).group(1)), int(re.search(r"Page (\d+)", after).group(1))
        assert n_after == n_start + 1, f"top-row Next did not advance: {n_start} -> {n_after}"
        # Row parity after the advance.
        assert _page_caption(page, 0) == _page_caption(page, 1), "rows out of parity after top Next"
        _click_bottom_prev(page)
        back = _page_caption(page, 0)
        assert int(re.search(r"Page (\d+)", back).group(1)) == n_start, (
            f"bottom-row Prev did not return: {after} -> {back}"
        )

    session.run(body)


def test_boundary_disabling_both_rows(session):
    """Boundary disabling scoped to a small source (Edwards 1787: 144 records
    → 6 pages at default size 25) so the last page is reachable in seconds."""

    def body(page: Page):
        _ph.goto_records(page)
        sidebar = page.locator('[data-testid="stSidebar"]')
        # Select the source filter (first selectbox — Select Source).
        selectboxes = sidebar.locator('[data-testid="stSelectbox"]')
        selectboxes.first.click()
        page.wait_for_timeout(500)
        page.keyboard.type("Edwards 1787")
        page.wait_for_timeout(400)
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)
        page1 = _page_caption(page, 0)
        assert re.search(r"Page 1 of 6", page1), f"Edwards 1787 expected Page 1 of 6, got {page1!r}"
        prev_buttons = _ph.main_buttons(page, "Prev")
        next_buttons = _ph.main_buttons(page, "Next")
        assert prev_buttons.count() == 2 and next_buttons.count() == 2, "twin rows not both rendered"
        for i in range(prev_buttons.count()):
            assert prev_buttons.nth(i).is_disabled(), f"Prev enabled at page 1 in row {i}"
        for i in range(next_buttons.count()):
            assert not next_buttons.nth(i).is_disabled(), f"Next wrongly disabled at page 1 in row {i}"
        # Advance to the last page (5 clicks).
        for _ in range(5):
            _click_top_next(page)
        last_caption = _page_caption(page, 0)
        assert re.search(r"Page 6 of 6", last_caption), f"expected last page 6, got {last_caption!r}"
        for i in range(next_buttons.count()):
            assert next_buttons.nth(i).is_disabled(), f"Next enabled at last page in row {i}"
        for i in range(prev_buttons.count()):
            assert not prev_buttons.nth(i).is_disabled(), f"Prev wrongly disabled at last page in row {i}"
        # Bottom-row Prev returns one page.
        _click_bottom_prev(page)
        assert re.search(r"Page 5 of 6", _page_caption(page, 0)), "bottom-row Prev did not return to page 5"

    session.run(body)
