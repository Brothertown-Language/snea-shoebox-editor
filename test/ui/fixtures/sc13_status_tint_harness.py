"""SC-13 RED harness — renders the MDF block renderer twice in a real browser:
once WITHOUT highlight spans (baseline) and once WITH active search-token
highlighting, both with identical status-line diagnostics, so a Playwright
test can compare status-line computed tints between the two states.

Test fixture only — renders src code under test, contains no implementation.

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

import streamlit as st

from src.frontend.ui_utils import render_mdf_block

MDF_TEXT = """\\lx abbamocho
\\ge the devil
\\so Wampanoag [wam]; Wood 1634
\\nt Record: 188
\\lx Aaunchemókaw
\\ge Tell me your newes."""

DIAGNOSTICS = [
    {"status": "ok", "message": ""},
    {"status": "note", "message": ""},
    {"status": "warning", "message": ""},
    {"status": "suggestion", "message": ""},
    {"status": "error", "message": ""},
    {"status": "diff-changed", "message": ""},
]

# Highlighting active: cover the first five characters of every line
# (whole-term coverage of the leading term, as the page would compute).
ACTIVE_SPANS = [[(0, 5)] for _ in range(6)]

st.header("SC13BASELINE")
render_mdf_block(MDF_TEXT, diagnostics=DIAGNOSTICS)

st.header("SC13HIGHLIGHT")
render_mdf_block(MDF_TEXT, diagnostics=DIAGNOSTICS, highlight_spans=ACTIVE_SPANS)