"""Serverless smoke tests for the SC-12 in-context MDF reference hooks
(.issues/1379 Phase 6, R-11).

Unit-tests the pure hook logic without a database or live server: marker
extraction from field text, one-line definition lookup from the committed
``master.json``, the deep-link URL builder, and the marker-tooltip wrap in
``render_mdf_block``'s HTML (escaping preserved, content never rewritten).
Real-browser user-visible behavior is verified by the Playwright E2E suite
(test/ui/test_mdf_hooks_e2e.py) per docs/development/ui_testing_standard.md.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import html as _html
import json
from pathlib import Path

import pytest
import streamlit

from src.frontend.ui_utils import (
    extract_mdf_markers,
    marker_definitions,
    marker_reference_url,
    render_mdf_block,
    wrap_marker_token_html,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MASTER_PATH = REPO_ROOT / "docs" / "mdf" / "build" / "master.json"

# Standard MDF markers as a typed field/record would carry them.
FIELD_TEXT = "\\lx wampum\n\\ge ball & <chain>\ncontinuation line is not a marker\n \\lx indented mention is content"


# ── extract_mdf_markers ────────────────────────────────────────────────


def test_smoke_sc12_extract_markers_from_field_text():
    """Line-initial markers are extracted in first-occurrence order."""
    assert extract_mdf_markers(FIELD_TEXT) == ["lx", "ge"]


def test_smoke_sc12_extract_markers_deduplicates_in_order():
    """Repeated markers collapse to their first occurrence; order is kept."""
    text = "\\ge second\n\\lx first\n\\ge repeat\n\\dt end"
    assert extract_mdf_markers(text) == ["ge", "lx", "dt"]


def test_smoke_sc12_extract_markers_ignores_indented_mentions():
    """Marker-like text on indented (continuation) lines is content, per the
    #1379 Parsing Semantics offset-0 rule."""
    text = "\\lx wampum\n \\ge indented mention\n\t\\ps tab-indented"
    assert extract_mdf_markers(text) == ["lx"]


def test_smoke_sc12_extract_markers_takes_whole_non_space_run():
    """A glued token is one token (\\shd2 is distinct from \\shd and
    \\shd2abc is a single non-member token)."""
    assert extract_mdf_markers("\\shd2 heading") == ["shd2"]
    assert extract_mdf_markers("\\shd2abc glued") == ["shd2abc"]


def test_smoke_sc12_extract_markers_empty_text():
    """Empty or marker-less text yields no markers (and never crashes)."""
    assert extract_mdf_markers("") == []
    assert extract_mdf_markers("plain prose only") == []


def test_smoke_sc12_extract_markers_never_mutates_unicode_content():
    """Extraction must not alter the field text — the linguistic data
    (accented content, IPA) passes through byte-for-byte."""
    original = "\\lx wâpamêw\n\\ge mirror — ə, ʃ, tʃ, ŋ, ã, č preserved"
    snapshot = original
    extract_mdf_markers(original)
    assert original == snapshot, "field text must never be mutated"


# ── marker_definitions ─────────────────────────────────────────────────


def test_smoke_sc12_definitions_lookup_from_master_json():
    """The one-line definition of a marker is its source heading with the
    line-initial marker token dropped."""
    definitions = marker_definitions(REPO_ROOT)
    assert definitions.get("lx") == "lexeme or headword of the lexical entry"
    assert definitions.get("ge") == "gloss (English)"
    assert "zzz" not in definitions, "an unknown marker has no reference entry"


def test_smoke_sc12_definitions_are_byte_exact_source_text():
    """Definitions carry the source text byte-for-byte (no normalization,
    no stripping beyond the marker token and edge whitespace) — the source's
    accented content must survive verbatim."""
    master = json.loads(MASTER_PATH.read_text(encoding="utf-8"))
    from src.frontend.pages.mdf_reference import strip_marker

    for topic in master["topics"]:
        key = topic["key"]
        heading = topic.get("heading") or ""
        if not heading:
            continue
        expected = strip_marker(heading).strip()
        assert marker_definitions(REPO_ROOT)[key] == expected, key


def test_smoke_sc12_definitions_missing_file_degrades_to_empty():
    """A missing master.json yields an empty mapping — every hook degrades to
    its no-definition rendering instead of crashing (missing-artifact edge)."""
    assert marker_definitions(REPO_ROOT / "does" / "not" / "exist") == {}


# ── marker_reference_url ───────────────────────────────────────────────


def test_smoke_sc12_deep_link_url_shape():
    """The deep link targets the MDF Reference page's ``?marker=<key>``
    query parameter — the mechanism the page itself resolves."""
    assert marker_reference_url("lx") == "/mdf-reference?marker=lx"
    assert marker_reference_url("shd2") == "/mdf-reference?marker=shd2"


def test_smoke_sc12_deep_link_url_encodes_arbitrary_tokens():
    """A token that could break the query string is percent-encoded."""
    assert marker_reference_url("a/b") == "/mdf-reference?marker=a%2Fb"


# ── wrap_marker_token_html ─────────────────────────────────────────────


def _definitions():
    return marker_definitions(REPO_ROOT)


def test_smoke_sc12_marker_token_wrapped_with_definition_tooltip():
    """The line-initial marker token is wrapped in a tooltip span carrying
    the marker's one-line definition; the rest of the line is untouched."""
    line = "\\lx wampum"
    inner_html = _html.escape(line)
    wrapped = wrap_marker_token_html(inner_html, line, _definitions())
    assert wrapped == ('<span class="mdf-marker" title="lexeme or headword of the lexical entry">\\lx</span> wampum')


def test_smoke_sc12_tooltip_title_escapes_definition():
    """A definition containing markup-sensitive characters is HTML-escaped in
    the title attribute (quotes included) — attribute injection is impossible."""
    definitions = {"zz": 'gloss & <not markup> "quoted"'}
    line = "\\zz wampum"
    wrapped = wrap_marker_token_html(_html.escape(line), line, definitions)
    assert (
        '<span class="mdf-marker" title="gloss &amp; &lt;not markup&gt; &quot;quoted&quot;">'
        "\\zz</span> wampum" in wrapped
    )


def test_smoke_sc12_unknown_marker_renders_unchanged():
    """A marker with no reference entry renders exactly as before."""
    line = "\\lemma not in the reference"
    inner_html = _html.escape(line)
    assert wrap_marker_token_html(inner_html, line, _definitions()) == inner_html


def test_smoke_sc12_highlight_mark_interrupting_token_blocks_wrap():
    """When highlight markup interrupts the token, the line renders unchanged
    — a tooltip never justifies corrupting search-mark output."""
    line = "\\lx wampum"
    inner_html = '<mark class="search-token">\\lx</mark> wampum'
    assert wrap_marker_token_html(inner_html, line, _definitions()) == inner_html


def test_smoke_sc12_non_marker_line_renders_unchanged():
    """A continuation line with no line-initial marker renders unchanged."""
    line = "plain continuation text"
    inner_html = _html.escape(line)
    assert wrap_marker_token_html(inner_html, line, _definitions()) == inner_html


# ── render_mdf_block integration ───────────────────────────────────────


@pytest.fixture()
def captured_html(monkeypatch):
    """Capture the HTML string render_mdf_block passes to st.html()."""
    chunks = []

    def fake_html(html):
        chunks.append(html)

    monkeypatch.setattr(streamlit, "html", fake_html)
    return chunks


def test_smoke_sc12_render_mdf_block_emits_marker_tooltips(captured_html):
    """render_mdf_block wraps each line-initial marker token with its
    definition tooltip when the caller opts in (marker_tooltips=True);
    display text and escaping stay intact."""
    render_mdf_block("\\lx wampum\n\\ge ball & <chain>", marker_tooltips=True)
    assert len(captured_html) == 1
    html = captured_html[0]
    assert '<span class="mdf-marker" title="lexeme or headword of the lexical entry">\\lx</span>' in html
    assert '<span class="mdf-marker" title="gloss (English)">\\ge</span> ball &amp; &lt;chain&gt;' in html


def test_smoke_sc12_render_mdf_block_without_markers_renders_plain(captured_html):
    """A block whose lines carry no marker tokens renders unchanged (no
    mdf-marker tooltip spans emitted)."""
    render_mdf_block("plain continuation text only", marker_tooltips=True)
    html = captured_html[0]
    assert '<span class="mdf-marker"' not in html


def test_smoke_sc12_render_mdf_block_unicode_content_untouched(captured_html):
    """Accent/IPA-bearing record content renders byte-for-byte — no
    normalization anywhere in the hook path."""
    render_mdf_block("\\lx wâpamêw\n\\ge ə, ʃ, tʃ, ŋ, ã, č", marker_tooltips=True)
    html = captured_html[0]
    assert "wâpamêw" in html
    assert "ə, ʃ, tʃ, ŋ, ã, č" in html
