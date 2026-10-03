"""RED test for SC-12 (issue 1401): diff-token overlap precedence in render_mdf_block.

Contract: where a highlight span overlaps a diff-token span (the
diagnostics-driven diff marks in src/frontend/ui_utils.py::render_mdf_block),
the diff-token span renders UNCHANGED and the overlapping search-token mark is
OMITTED. Currently the changed-span branch calls ``_search_token_wrap`` on the
diff-token text, nesting ``<mark class="search-token">`` inside
``<mark class="diff-token">`` — this smoke test asserts the SC-12 behavior and
MUST FAIL until the precedence rule is implemented (SC-12 GREEN):

1. A highlight span overlapping a changed (diff-token) span leaves the
   diff-token markup unchanged — ``<mark class="diff-token">text</mark>``
   with NO nested ``<mark class="search-token">``.
2. Highlight spans overlapping unchanged (non-diff) spans still get the
   normal search-token wrap — omission applies only inside diff-token spans.

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

import pytest
import streamlit

from src.frontend.ui_utils import render_mdf_block

# Line 1: one changed (diff) token "wampum"; line 2: unchanged text "plain line"
# Per-line spans: line 1 span (0, 6) overlaps the changed span exactly;
# line 2 span (4, 9) covers "plain" in the rendered "\ge plain line".
MDF_TEXT = "\\lx wampum\n\\ge plain line"
DIAGNOSTICS = [
    {
        "status": "diff-changed",
        "spans": [{"text": "wampum", "changed": True}],
    },
    {"status": "ok"},
]
HIGHLIGHT_SPANS = [[(0, 6)], [(4, 9)]]


@pytest.fixture()
def captured_html(monkeypatch):
    """Capture the HTML string render_mdf_block passes to st.html()."""
    chunks = []

    def fake_html(html):
        chunks.append(html)

    monkeypatch.setattr(streamlit, "html", fake_html)
    return chunks


def test_sc12_diff_token_overlap_renders_unchanged(captured_html):
    """SC-12 gate — MUST FAIL while diff-token spans still nest search-token marks.

    Where a highlight span overlaps a changed (diff-token) span, the
    diff-token span must render unchanged:
    ``<mark class="diff-token">wampum</mark>`` — no nested
    ``<mark class="search-token">`` inside it.
    """
    render_mdf_block(MDF_TEXT, diagnostics=DIAGNOSTICS, highlight_spans=HIGHLIGHT_SPANS)
    assert len(captured_html) == 1
    html = captured_html[0]

    assert '<mark class="diff-token">wampum</mark>' in html, (
        "SC-12 RED: the diff-token span must render unchanged when a highlight "
        "span overlaps it — expected exactly "
        "'<mark class=\"diff-token\">wampum</mark>' with no nested search-token "
        "wrap (overlap precedence not yet implemented)."
    )
    # The overlapping search-token mark must be omitted entirely inside the
    # diff-token span: the changed-span branch must not call _search_token_wrap.
    diff_start = html.find('<mark class="diff-token">')
    diff_end = html.find("</mark>", diff_start) if diff_start != -1 else -1
    if diff_start != -1 and diff_end != -1:
        diff_inner = html[diff_start:diff_end]
        assert "search-token" not in diff_inner, (
            "SC-12 RED: the overlapping search-token mark must be omitted — "
            "a mark.search-token must never appear nested inside "
            "mark.diff-token."
        )


def test_sc12_non_overlap_search_token_still_emitted(captured_html):
    """SC-12 companion gate: omission applies ONLY inside diff-token spans.

    A highlight span over unchanged (non-diff) text still gets the normal
    SC-10 search-token wrap; the precedence rule must not suppress it.
    """
    render_mdf_block(MDF_TEXT, diagnostics=DIAGNOSTICS, highlight_spans=HIGHLIGHT_SPANS)
    assert len(captured_html) == 1
    html = captured_html[0]

    assert '<mark class="search-token">plain</mark>' in html, (
        "SC-12 RED: a highlight span over unchanged (non-diff) text must still "
        "emit the normal search-token wrap — the overlap precedence rule must "
        "be scoped to diff-token spans only."
    )
