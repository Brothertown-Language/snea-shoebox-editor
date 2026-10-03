"""RED test for SC-10 (issue 1401): search-match highlight wrapping in render_mdf_block.

The renderer (src/frontend/ui_utils.py::render_mdf_block) currently ACCEPTS
highlight_spans (SC-9 signature) but IGNORES them — no ``<mark class="search-token">``
wrapping is emitted even when spans are supplied. This smoke test asserts the
SC-10 behavior and MUST FAIL until the wrapping is implemented (SC-10 GREEN):

1. A supplied highlight span produces ``<mark class="search-token">`` wrapping
   the covered text.
2. Output escaping is preserved inside the wrap — markup-sensitive characters
   (``&``, ``<``, ``>``) in the matched text remain HTML-escaped.
3. No ``mark.search-token`` elements are emitted when highlight_spans is None
   (default rendering unchanged).

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

import streamlit
import pytest

from src.frontend.ui_utils import render_mdf_block

MDF_TEXT = "\\lx wampum\n\\ge ball & <chain>"

# Per-line spans: line 1 unwrapped, line 2 spans offsets 4..18 = "ball & <chain>"
HIGHLIGHT_SPANS = [[], [(4, 18)]]


@pytest.fixture()
def captured_html(monkeypatch):
    """Capture the HTML string render_mdf_block passes to st.html()."""
    chunks = []

    def fake_html(html):
        chunks.append(html)

    monkeypatch.setattr(streamlit, "html", fake_html)
    return chunks


def test_sc10_highlight_span_emits_search_token_wrap(captured_html):
    """SC-10 gate — MUST FAIL while highlight_spans are ignored.

    A supplied span over "ball & <chain>" must emit a
    ``<mark class="search-token">`` element wrapping the covered text, with
    markup-sensitive characters still HTML-escaped inside the wrap.
    """
    render_mdf_block(MDF_TEXT, highlight_spans=HIGHLIGHT_SPANS)
    assert len(captured_html) == 1
    html = captured_html[0]

    assert '<mark class="search-token">' in html, (
        "RED: render_mdf_block emits no mark.search-token even when "
        "highlight_spans are supplied — wrapping not yet implemented (SC-10)."
    )
    assert '<mark class="search-token">ball &amp; &lt;chain&gt;</mark>' in html, (
        "SC-10: the search-token wrap must cover the matched text exactly and "
        "preserve output escaping (& -> &amp;, < -> &lt;, > -> &gt;) inside the mark."
    )


def test_sc10_no_search_token_without_spans(captured_html):
    """Default rendering stays unchanged: no mark.search-token when spans absent."""
    render_mdf_block(MDF_TEXT)
    assert len(captured_html) == 1
    assert "<mark class=\"search-token\"" not in captured_html[0], (
        "mark.search-token must not appear in default (spanless) rendering."
    )