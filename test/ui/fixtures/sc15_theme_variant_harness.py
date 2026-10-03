"""SC-15 RED harness — renders the MDF block renderer in a real browser with
active search-token highlighting PLUS diff-token spans PLUS the full set of
tinted status lines, so a Playwright test can compare the computed
``background-color`` of ``mark.search-token`` against ``mark.diff-token``
marks and the status-line tints, under light and dark color-scheme
emulation.

Test fixture only — renders src code under test, contains no implementation.

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

import streamlit as st

from src.frontend.ui_utils import render_mdf_block

# Lines whose spans mix an unchanged (search-token-eligible) token with a
# changed (diff-token) token, so BOTH mark classes render in every line.
SPANS = [
    [
        {"text": "abbam", "changed": False},
        {"text": "ocho", "changed": True},
        {"text": " rest", "changed": False},
    ],
    [
        {"text": "devil", "changed": False},
        {"text": "ish", "changed": True},
        {"text": " here", "changed": False},
    ],
    [
        {"text": "Wampa", "changed": False},
        {"text": "noag", "changed": True},
        {"text": " Wood", "changed": False},
    ],
    [
        {"text": "Aaunc", "changed": False},
        {"text": "hemokaw", "changed": True},
        {"text": " tail", "changed": False},
    ],
    [
        {"text": "newes", "changed": False},
        {"text": "tell", "changed": True},
        {"text": " more", "changed": False},
    ],
    [
        {"text": "kekin", "changed": False},
        {"text": "eas", "changed": True},
        {"text": " end", "changed": False},
    ],
    [
        {"text": "sachim", "changed": False},
        {"text": "muck", "changed": True},
        {"text": " added", "changed": False},
    ],
    [
        {"text": "wunnea", "changed": False},
        {"text": "uogq", "changed": True},
        {"text": " gone", "changed": False},
    ],
]

# One tinted status per tint class defined in src/frontend/ui_utils.py
# (status-ok is unstyled and excluded).
DIAGNOSTICS = [
    {"status": "suggestion", "message": "", "spans": SPANS[0]},
    {"status": "note", "message": "", "spans": SPANS[1]},
    {"status": "error", "message": "", "spans": SPANS[2]},
    {"status": "warning", "message": "", "spans": SPANS[3]},
    {"status": "diff-changed", "message": "", "spans": SPANS[4]},
    {"status": "diff-added", "message": "", "spans": SPANS[5]},
    {"status": "diff-removed", "message": "", "spans": SPANS[6]},
    {"status": "ok", "message": "", "spans": SPANS[7]},
]

MDF_TEXT = """\\lx abbamocho rest
\\ge devilish here
\\so Wampanoag Wood
\\lx Aaunchemokaw tail
\\ge newestell more
\\lx kekineas end
\\lx sachimmuck added
\\lx wunneauogq gone"""

# Highlighting active: cover the leading term of every line (whole-term
# coverage, as the page would compute). The unchanged leading spans become
# mark.search-token; the changed spans become mark.diff-token.
ACTIVE_SPANS = [[(0, 5)] for _ in range(8)]

st.header("SC15THEMEVARIANT")
render_mdf_block(MDF_TEXT, diagnostics=DIAGNOSTICS, highlight_spans=ACTIVE_SPANS)