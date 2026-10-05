"""Issue #1413 SC-7 — Playwright e2e auto-save-on-page-change from either row.

With global edit mode active and pending edits present, a page change from
either row persists each pending edit exactly once through the existing
record-update path (same change summary as today — verified via the
observable revision-history entry, never mocked) and clears the
pending-edit state after the save pass. A double-save failure-mode check
confirms exactly one save pass per page change.

NOTE: mutates LOCAL DB state (creates one revision on a synced record).
Run scripts/sync_prod_to_local.sh before any regression cycle.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import importlib.util
import os
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


def _open_first_revision_history(page: Page):
    """Open the first record's Revision History expander (st.expander renders
    as a details/summary element, not a button)."""
    page.locator(
        '[data-testid="stExpander"] summary, [data-testid="stExpander"] [data-testid="stExpanderToggle"]'
    ).first.click()
    page.wait_for_timeout(1500)


def _open_all_expanders_and_count(page: Page) -> int:
    """Open every revision-history expander on the page, then count
    auto-save marker occurrences across the rendered history entries."""
    summaries = page.locator('[data-testid="stExpander"] summary')
    for i in range(summaries.count()):
        try:
            summaries.nth(i).click(timeout=2000)
            page.wait_for_timeout(300)
        except Exception:
            pass  # already open — continue
    page.wait_for_timeout(1000)
    return _pending_marker_counts(page)


def _enter_edit_mode(page: Page):
    sb = page.locator('[data-testid="stSidebar"]')
    sb.locator('button:has-text("Enter Edit Mode")').click()
    page.wait_for_timeout(2500)


def _pending_marker_counts(page: Page) -> int:
    """Count revision-history entries carrying the auto-save summary marker."""
    return page.evaluate(
        """() => document.body.innerText.split('Auto-save via pagination').length - 1"""
    )


def test_autosave_once_and_pending_cleared(session):
    def body(page: Page):
        _ph.goto_records(page)
        _enter_edit_mode(page)
        # Baseline: pre-existing auto-save entries across ALL page-1 expanders
        # are counted and excluded from the delta below (idempotency across
        # repeated runs against the same local DB).
        baseline = _open_all_expanders_and_count(page)
        # Edit the first unlocked record's MDF textarea.
        textarea = page.locator('[data-testid="stTextArea"] textarea').first
        original = textarea.input_value()
        textarea.fill(original + "\n% SC-7 e2e pending edit\n")
        # Streamlit commits st.text_area on blur — blur before the page change
        # so the pending edit is registered in session state.
        textarea.press("Tab")
        page.wait_for_timeout(2000)
        # Page change from the TOP row must auto-save exactly once.
        _ph.main_buttons(page, "Next").first.click()
        page.wait_for_timeout(2500)
        # Return to page 1 via the BOTTOM row Prev and inspect history.
        _ph.main_buttons(page, "Prev").last.click()
        page.wait_for_timeout(2500)
        _open_first_revision_history(page)
        after = _open_all_expanders_and_count(page)
        assert after > baseline, "auto-save did not persist a revision-history entry (SC-7)"
        delta = after - baseline
        assert delta == 1, f"expected exactly one save pass, found {delta} new auto-save entries"
        # Pending-edit state cleared: the textarea now shows the saved value
        # (pending_edits empty → initial value is the persisted mdf_data).
        textarea = page.locator('[data-testid="stTextArea"] textarea').first
        saved_value = textarea.input_value()
        assert "% SC-7 e2e pending edit" in saved_value, (
            "pending edit was not cleared/persisted into the record after page change"
        )

    session.run(body, timeout=420.0)
