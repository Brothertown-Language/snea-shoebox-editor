"""SC-16 RED harness — renders the MDF block renderer in a real browser with
active search-token highlighting only (no diff tokens, no status tints), so a
Playwright test can measure the WCAG contrast ratio of ``mark.search-token``
text against its effective composited background under light and dark
color-scheme emulation.

Test fixture only — renders src code under test, contains no implementation.

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

import streamlit as st

from src.frontend.ui_utils import render_mdf_block

MDF_TEXT = """\\lx abbam rest
\\ge devilish here
\\so Wampanoag Wood
\\lx Aaunchemokaw tail"""

# Highlighting active: cover the leading term of every line, so each line
# carries a mark.search-token.
ACTIVE_SPANS = [[(0, 5)] for _ in range(4)]

st.header("SC16CONTRAST")
render_mdf_block(MDF_TEXT, highlight_spans=ACTIVE_SPANS)
