"""RED test for SC-2 (issue 1401): stored-term span helper no-match empty contract.

No fuzzy or approximate matching: whenever no verbatim occurrence of a term
exists in the rendered line, the helper returns an empty span list. Offsets
are code-point indices into the line as given.

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

import unicodedata

from src.frontend.search_highlight import compute_term_spans


def test_absent_term_returns_empty_span_list():
    assert compute_term_spans("panggal panggal api", ["wəkəs"]) == []


def test_no_term_occurs_in_line_returns_empty():
    assert compute_term_spans("pre na\u0303wa post", ["cinay", "ʃiːtəw"]) == []


def test_empty_term_list_returns_empty():
    assert compute_term_spans("panggal api", []) == []


def test_empty_line_returns_empty():
    assert compute_term_spans("", ["panggal"]) == []


def test_empty_line_and_empty_terms_return_empty():
    assert compute_term_spans("", []) == []


def test_absent_term_among_present_terms_omits_absent_spans():
    line = "panggal api"
    spans = compute_term_spans(line, ["panggal", "nope"])
    assert spans == [(0, 7)]


def test_no_fuzzy_match_for_diacritic_variant():
    # NFD line, NFC term: no verbatim occurrence means no spans — no
    # approximate/fuzzy fallback.
    line = unicodedata.normalize("NFD", "nañwa")
    term = unicodedata.normalize("NFC", "nañwa")
    assert line != term
    assert compute_term_spans(line, [term]) == []


def test_no_substring_fuzzy_partial_match():
    # A term that is a partial/proximate variant must not fuzzy-match.
    assert compute_term_spans("panggal", ["panga"]) == []