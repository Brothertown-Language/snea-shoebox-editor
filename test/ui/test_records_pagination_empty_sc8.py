"""Issue #1413 SC-8 — Playwright real-browser empty-results suppression check.

On the empty-results path (no records batch), the main panel renders only
the empty-state message — no navigation rows, no "Page 1 of 1", and no
"Showing 1-0 of 0" artifacts anywhere. A supplementary source assertion
confirms both row call sites sit inside the non-empty records branch.

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


def test_empty_results_render_no_pagination_artifacts(session):
    def body(page: Page):
        _ph.goto_records(page)
        # Execute a search guaranteed to return zero records (Enter commits
        # the sidebar text input, firing on_search_change → rerun).
        sidebar = page.locator('[data-testid="stSidebar"]')
        sidebar.locator("input").first.fill("zzqqxxnomatch9999")
        sidebar.locator("input").first.press("Enter")
        page.wait_for_timeout(5000)
        text = _ph.body_text(page)
        assert "No records found matching your criteria." in text, f"empty state not rendered: {text[:400]!r}"
        assert "Page 1 of 1" not in text, "empty path renders a 'Page 1 of 1' artifact"
        assert "Showing 1-0 of 0" not in text, "empty path renders a 'Showing 1-0 of 0' artifact"
        assert not _ph.main_buttons(page, "Prev").count(), "empty path renders a Prev button"
        assert not _ph.main_buttons(page, "Next").count(), "empty path renders a Next button"
        page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc8-empty-results.png"))

    session.run(body)


def test_source_row_call_sites_inside_non_empty_branch():
    """Supplementary structural assertion (never a substitute for the
    behavioral verdict): both helper call sites sit inside the non-empty
    records branch."""
    source = open("src/frontend/pages/records.py", encoding="utf-8").read()
    import ast

    tree = ast.parse(source)

    def find_call_sites(node):
        found = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and getattr(child.func, "id", "") == "_render_pagination_row":
                # Walk ancestors by line: the call must be lexically inside the
                # `else:` branch that follows `elif not records_batch:`.
                found.append(child.lineno)
        return found

    calls = find_call_sites(tree)
    assert len(calls) == 2, f"expected exactly 2 call sites, found {len(calls)}"
    lines = source.splitlines()
    else_line = next(i + 1 for i, ln in enumerate(lines) if "elif not records_batch:" in ln)
    assert all(call > else_line for call in calls), "call site found before the non-empty records branch"
