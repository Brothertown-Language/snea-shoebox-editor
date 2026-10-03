"""RED test for SC-9 (issue 1401): default-off highlight parameters — markup-identical default rendering.

Two layers:
1. Signature gate (FAILS now): render_mdf_block must already accept optional
   highlight parameters — it currently has none, so this fails pre-GREEN.
2. Markup-identity baseline: the renderer's parameterless output for
   representative MDF blocks is compared markup-exactly against an inline
   baseline captured from a pre-CSS render. The CSS block the renderer
   prepends is stripped from the captured output, and the remaining markup
   must be identical to the baseline — i.e. spanless calls produce markup
   identical to the markup produced by the same call with the CSS stripped.
   This protects the revision-history and import-diff call sites
   (upload_mdf.py:1022,1028) and the records.py call sites in later phases,
   without coupling the baseline to volatile CSS bytes.

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

import inspect
import re

import pytest
import streamlit

from src.frontend.ui_utils import render_mdf_block

# Representative MDF blocks: simple record, IPA/diacritics/∞ data,
# subentry/example structure, and a diagnostics-driven call (records.py shape).
MDF_BLOCKS = {
    "single_record": "\\lx wampum\n\\va wampu-\n\\ps N\n\\ge ball\n\\nt Record: 1",
    "ipa_diacritics_infinity": (
        "\\lx waney\n\\ps N\n\\ge raccoon\n"
        "\\xv waney ∞êhs ʃiːtəw na\u0303wa\n\\nt Record: 2"
    ),
    "subentry_example": (
        "   \\lx wampum\n\n\\se\n\\va wampum\n\\ge sphere\n\n"
        "\\xv wampum apu\n\\ge it is a ball\n\\nt Record: 3"
    ),
}
DIAGNOSTICS_BLOCKS = {
    "diagnostics_statuses": "\\lx testword\n\\ge a test word\n\\nt Record: 4",
}
DIAGNOSTICS = {
    "diagnostics_statuses": [
        {"status": "error", "message": "bad line"},
        {"status": "warning", "message": "warn line"},
        {"status": "ok"},
    ],
}

# Markup-only baseline captured from a pre-CSS render of the parameterless
# (spanless) renderer output: the <style> and <script> blocks are stripped,
# leaving exactly the markup the renderer emits for each block.
MARKUP_BASELINE = {
    "single_record": (
        '<div class="mdf-wrap-block" id="mdf-block">'
        '<div class="mdf-line status-ok" >\\lx wampum</div>'
        '<div class="mdf-line status-ok" >\\va wampu-</div>'
        '<div class="mdf-line status-ok" >\\ps N</div>'
        '<div class="mdf-line status-ok" >\\ge ball</div>'
        '<div class="mdf-line status-ok" >&nbsp;</div>'
        '<div class="mdf-line status-ok" >\\nt Record: 1</div>'
        "</div>"
    ),
    "ipa_diacritics_infinity": (
        '<div class="mdf-wrap-block" id="mdf-block">'
        '<div class="mdf-line status-ok" >\\lx waney</div>'
        '<div class="mdf-line status-ok" >\\ps N</div>'
        '<div class="mdf-line status-ok" >\\ge raccoon</div>'
        '<div class="mdf-line status-ok" >&nbsp;</div>'
        '<div class="mdf-line status-ok" >\\xv waney ∞êhs ʃiːtəw na\u0303wa</div>'
        '<div class="mdf-line status-ok" >&nbsp;</div>'
        '<div class="mdf-line status-ok" >\\nt Record: 2</div>'
        "</div>"
    ),
    "subentry_example": (
        '<div class="mdf-wrap-block" id="mdf-block">'
        '<div class="mdf-line status-ok" >\\lx wampum</div>'
        '<div class="mdf-line status-ok" >&nbsp;</div>'
        '<div class="mdf-line status-ok" >\\se</div>'
        '<div class="mdf-line status-ok" >\\va wampum</div>'
        '<div class="mdf-line status-ok" >\\ge sphere</div>'
        '<div class="mdf-line status-ok" >&nbsp;</div>'
        '<div class="mdf-line status-ok" >\\xv wampum apu</div>'
        '<div class="mdf-line status-ok" >\\ge it is a ball</div>'
        '<div class="mdf-line status-ok" >&nbsp;</div>'
        '<div class="mdf-line status-ok" >\\nt Record: 3</div>'
        "</div>"
    ),
    "diagnostics_statuses": (
        '<div class="mdf-wrap-block" id="mdf-block">'
        '<div class="mdf-line status-error" title="bad line">\\lx testword</div>'
        '<div class="mdf-line status-warning" title="warn line">\\ge a test word</div>'
        '<div class="mdf-line status-ok" >&nbsp;</div>'
        '<div class="mdf-line status-ok" >\\nt Record: 4</div>'
        "</div>"
    ),
}


def _strip_css(html: str) -> str:
    """Strip the <style> and <script> blocks from renderer output, leaving markup only."""
    html = re.sub(r"<style>.*?</style>", "", html, flags=re.S)
    html = re.sub(r"<script>.*?</script>", "", html, flags=re.S)
    return html.strip()


@pytest.fixture()
def captured_html(monkeypatch):
    """Capture the HTML string render_mdf_block passes to st.html()."""
    chunks = []

    def fake_html(html):
        chunks.append(html)

    monkeypatch.setattr(streamlit, "html", fake_html)
    return chunks


def test_sc9_renderer_signature_accepts_optional_highlight_params():
    """SC-9 signature gate — MUST FAIL until highlight parameters are added.

    The signature must accept at least one optional parameter beyond the
    current {mdf_text, key, diagnostics} set, so call sites that do not
    supply highlight spans can render markup-identically by default.
    """
    sig = inspect.signature(render_mdf_block)
    known = {"mdf_text", "key", "diagnostics"}
    optional_new = [
        p
        for name, p in sig.parameters.items()
        if name not in known and p.default is not inspect.Parameter.empty
    ]
    assert optional_new, (
        "RED: render_mdf_block has no optional highlight parameters — "
        f"signature is {sig}. This MUST FAIL until optional default-off "
        "highlight span parameters are added (SC-9 GREEN)."
    )


def test_sc9_parameterless_output_matches_baseline(captured_html):
    """Markup-identity baseline: parameterless (spanless) rendering matches the
    markup-only baseline — the same call with the CSS stripped, exactly."""
    for name, mdf in MDF_BLOCKS.items():
        captured_html.clear()
        render_mdf_block(mdf)
        assert len(captured_html) == 1
        assert _strip_css(captured_html[0]) == MARKUP_BASELINE[name], (
            f"Markup-identity drift for '{name}': spanless renderer output "
            "no longer matches the SC-9 markup baseline."
        )


def test_sc9_diagnostics_call_output_matches_baseline(captured_html):
    """Diagnostics-driven call (records.py:917/1027, upload_mdf.py:1022/1028 shape)
    matches the markup baseline — protects those call sites against later-phase drift."""
    for name, mdf in DIAGNOSTICS_BLOCKS.items():
        captured_html.clear()
        render_mdf_block(mdf, diagnostics=DIAGNOSTICS[name])
        assert len(captured_html) == 1
        assert _strip_css(captured_html[0]) == MARKUP_BASELINE[name], (
            f"Markup-identity drift for '{name}' (diagnostics call): renderer "
            "output no longer matches the SC-9 markup baseline."
        )


def test_sc9_markup_baseline_exists():
    """Markup-baseline existence: every representative block has a nonempty
    markup-only baseline entry for the markup-identity checks."""
    for name in list(MDF_BLOCKS) + list(DIAGNOSTICS_BLOCKS):
        assert name in MARKUP_BASELINE
        assert isinstance(MARKUP_BASELINE[name], str) and MARKUP_BASELINE[name]
        assert "<style>" not in MARKUP_BASELINE[name]
        assert "<div" in MARKUP_BASELINE[name]