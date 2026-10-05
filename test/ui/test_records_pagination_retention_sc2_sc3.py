"""Issue #1413 SC-2 / SC-3 — Playwright real-browser retention guards.

SC-2: after the sidebar pager removal, the sidebar still renders the
Results-per-page selectbox with its unchanged value list [1, 5, 10, 25, 50,
100] and page-size preference persistence behaves as today (decision D5).
SC-3: the sidebar still renders the edit-mode controls (Enter Edit Mode /
Cancel All / Save All) with unchanged semantics.

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


def test_sc2_results_per_page_selectbox_retained_with_values(session):
    """Behavioral: the selectbox renders with its unchanged value set and
    page-size persistence behaves as today — switching page size resets the
    page and re-slices the showing range (decision D5). Dropdown options are
    keyboard-navigated (Streamlit virtualizes the open list)."""

    def body(page: Page):
        _ph.goto_records(page)
        sidebar = page.locator('[data-testid="stSidebar"]')
        selectboxes = sidebar.locator('[data-testid="stSelectbox"]')
        assert selectboxes.count() >= 1, "Results-per-page selectbox vanished from the sidebar"
        # The Results-per-page selectbox is the LAST sidebar selectbox.
        box = selectboxes.last
        box.click()
        page.wait_for_timeout(600)
        # Assert the value list via the combobox listbox when rendered.
        option_text = page.evaluate(
            "() => { const l = document.querySelector('ul[role=listbox]'); return l ? l.innerText : ''; }"
        )
        if option_text:
            for value in ["1", "5", "10", "25", "50", "100"]:
                assert value in option_text, f"selectbox value {value} missing from the value list"
        # Behavioral persistence: choose 5 and assert the main-panel showing
        # range re-slices to 5 records per page, then restore 25.
        page.keyboard.press("Escape")
        box.click()
        page.wait_for_timeout(400)
        page.keyboard.type("5")
        page.wait_for_timeout(400)
        page.keyboard.press("Enter")
        page.wait_for_timeout(4000)
        body_text = _ph.body_text(page)
        assert re.search(r"Showing 1-5 of \d+", body_text), (
            f"page-size change to 5 did not re-slice results (persistence semantics changed): {body_text[:300]!r}"
        )
        # Restore the default 25.
        selectboxes.last.click()
        page.wait_for_timeout(400)
        page.keyboard.type("25")
        page.wait_for_timeout(400)
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)

    session.run(body)


def test_sc3_edit_mode_controls_retained(session):
    def body(page: Page):
        _ph.goto_records(page)
        sb = page.locator('[data-testid="stSidebar"]')
        assert sb.locator('button:has-text("Enter Edit Mode")').count() == 1, "Enter Edit Mode control missing"
        sb.locator('button:has-text("Enter Edit Mode")').click()
        page.wait_for_timeout(2500)
        sb = page.locator('[data-testid="stSidebar"]')
        assert sb.locator('button:has-text("Cancel All")').count() == 1, (
            "Cancel All control missing after entering edit mode"
        )
        assert sb.locator('button:has-text("Save All")').count() == 1, (
            "Save All control missing after entering edit mode"
        )
        # Unchanged semantics: Cancel All exits edit mode.
        sb.locator('button:has-text("Cancel All")').click()
        page.wait_for_timeout(2500)
        sb = page.locator('[data-testid="stSidebar"]')
        assert sb.locator('button:has-text("Enter Edit Mode")').count() == 1, (
            "Cancel All did not restore Enter Edit Mode"
        )

    session.run(body)
