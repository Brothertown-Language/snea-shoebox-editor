"""RED test for SC-11 (issue 1401): malformed/out-of-range highlight span robustness.

The renderer (src/frontend/ui_utils.py::render_mdf_block) currently CLAMPS
highlight spans to the line bounds in _search_token_wrap (max(0, start) /
min(len(text), end)) — a span ending beyond the line length is clamped to the
line end rather than dropped, and negative-start spans are clamped into range.

This smoke test asserts the SC-11 ignore-not-clamp contract and MUST FAIL
until the drop semantics are implemented (SC-11 GREEN):

1. Malformed spans (non-2-element entries, non-int offsets, start >= end) and
   out-of-range spans (negative offsets, end beyond line length) are DROPPED
   entirely without raising.
2. All other content renders unaffected — well-formed spans on the same text
   still wrap, and surrounding text is HTML-escaped as usual.
3. NO clamping: a span ending beyond the line length is dropped entirely,
   not clamped to the line end (no mark may appear covering the tail).

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

import pytest
import streamlit

from src.frontend.ui_utils import render_mdf_block

MDF_TEXT = "\\lx wampum\n\\ge ball & <chain>"

# Line 2 is "\ge ball & <chain>"; offsets 4..8 cover "ball".
GOOD_SPAN = [(4, 8)]


@pytest.fixture()
def captured_html(monkeypatch):
    """Capture the HTML string render_mdf_block passes to st.html()."""
    chunks = []

    def fake_html(html):
        chunks.append(html)

    monkeypatch.setattr(streamlit, "html", fake_html)
    return chunks


def _html_of(chunks):
    assert len(chunks) == 1
    return chunks[0]


def test_sc11_no_raise_on_malformed_and_out_of_range_spans(captured_html):
    """Malformed/out-of-range spans are dropped without raising."""
    render_mdf_block(
        MDF_TEXT,
        highlight_spans=[
            [(-5, 3), (10, 4), (99, 120)],  # negative, start>=end, end beyond line
            [("a", "b"), (1,), (2, 3, 4)],  # malformed shapes/types
        ],
    )
    # Reaching here without an exception is the primary gate.
    html = _html_of(captured_html)
    assert "<mark class=\"search-token\"" not in html, (
        "SC-11: malformed and out-of-range spans must be dropped entirely — "
        "no mark.search-token may be emitted from invalid spans."
    )


def test_sc11_no_clamp_span_beyond_line_length(captured_html):
    """A span ending beyond the line length is dropped, NOT clamped to the end."""
    # Span (4, 999) would clamp to (4, len(line)) under current behavior and
    # wrap "ball & <chain>" — under SC-11 it must be dropped entirely.
    render_mdf_block(MDF_TEXT, highlight_spans=[[], [(4, 999)]])
    html = _html_of(captured_html)
    assert "<mark class=\"search-token\"" not in html, (
        "RED: a span ending beyond the line length is clamped to the line end "
        "instead of being dropped — clamping, not the ignore-not-clamp "
        "contract (SC-11)."
    )
    # Content itself is unaffected: the tail text must still render escaped.
    assert "ball &amp; &lt;chain&gt;" in html, (
        "SC-11: non-highlighted content must render unaffected (escaped)."
    )


def test_sc11_negative_start_span_dropped_not_clamped(captured_html):
    """A span with a negative start is dropped entirely, not clamped to 0."""
    render_mdf_block(MDF_TEXT, highlight_spans=[[], [(-5, 8)]])
    html = _html_of(captured_html)
    assert "<mark class=\"search-token\"" not in html, (
        "RED: a span with negative start is clamped into range and wraps text "
        "— the ignore-not-clamp contract requires it be dropped (SC-11)."
    )
    assert "ball &amp; &lt;chain&gt;" in html


def test_sc11_start_gte_end_span_dropped(captured_html):
    """A span with start >= end is dropped without raising or wrapping."""
    render_mdf_block(MDF_TEXT, highlight_spans=[[], [(10, 4)]])
    html = _html_of(captured_html)
    assert "<mark class=\"search-token\"" not in html, (
        "SC-11: a degenerate (start >= end) span must be dropped without "
        "wrapping any text."
    )


def test_sc11_well_formed_spans_still_wrap(captured_html):
    """Valid spans on the same text still wrap — dropping is selective only."""
    render_mdf_block(
        MDF_TEXT,
        highlight_spans=[[], [(4, 8), (-5, 3), (99, 120), ("x", 1)]],
    )
    html = _html_of(captured_html)
    assert '<mark class="search-token">ball</mark>' in html, (
        "SC-11: dropping invalid spans must not affect valid spans on the "
        "same line — 'ball' must still be wrapped."
    )
    assert "&amp; &lt;chain&gt;" in html, (
        "SC-11: escaping of surrounding text must be unaffected."
    )
