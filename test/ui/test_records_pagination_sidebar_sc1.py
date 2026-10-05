"""Issue #1413 SC-1 — Playwright real-browser check: the Records sidebar
renders NO page-level Prev/Next navigation buttons and no "Page N of M" /
"Showing X-Y of Z" captions after the pager relocation to the main panel.

Supplementary source-absence assertion: records.py no longer renders the
sidebar pager block. Behavioral verdict is primary (constraint C-3).

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
BrowserSession, goto_records, require_auth_storage, sidebar_buttons, sidebar_text = (
    _ph.BrowserSession,
    _ph.goto_records,
    _ph.require_auth_storage,
    _ph.sidebar_buttons,
    _ph.sidebar_text,
)

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
    sess = BrowserSession(require_auth_storage())
    yield sess
    sess.close()


def test_sidebar_has_no_pager_buttons_and_no_captions(session):
    def body(page: Page):
        goto_records(page)
        text = sidebar_text(page)
        assert not sidebar_buttons(page, "Prev").count(), "sidebar still renders a page-level Prev button"
        assert not sidebar_buttons(page, "Next").count(), "sidebar still renders a page-level Next button"
        assert not re.search(r"Page \d+ of \d+", text), f"sidebar still renders a Page N of M caption: {text!r}"
        assert not re.search(r"Showing \d+-\d+ of \d+", text), f"sidebar still renders a Showing caption: {text!r}"

    session.run(body)


def test_source_no_longer_contains_sidebar_pager_block():
    source = open("src/frontend/pages/records.py", encoding="utf-8").read()
    assert 'button("Prev", icon="◀️", disabled=(st.session_state.current_page <= 1)' not in source, (
        "records.py still renders the sidebar Prev button"
    )
    assert 'button("Next", icon="▶️", disabled=not has_next' not in source, (
        "records.py still renders the sidebar Next button"
    )
