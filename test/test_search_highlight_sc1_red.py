"""RED test for SC-1 (issue 1401): stored-term span helper occurrence contract.

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

import unicodedata

from src.frontend.search_highlight import compute_term_spans


def test_verbatim_whole_term_find_emits_left_to_right_spans():
    line = "panggal panggal api"
    assert compute_term_spans(line, ["panggal"]) == [(0, 7), (8, 15)]


def test_nfd_decomposed_diacritics_match_verbatim_stored_term():
    # Offsets are code-point indices into the line string as given (verbatim find).
    stored = unicodedata.normalize("NFD", "na\u0303wa")
    line = "pre " + stored + " " + stored + " end"
    first = len("pre ")
    assert compute_term_spans(line, [stored]) == [
        (first, first + 5),
        (first + 6, first + 11),
    ]


def test_mixed_terms_emitted_left_to_right():
    line = unicodedata.normalize("NFD", "nãwa") + " " + unicodedata.normalize(
        "NFD", "cinay"
    )
    spans = compute_term_spans(line, ["cinay", "na\u0303wa"])
    assert spans == sorted(spans)
    assert len(spans) == 2


def test_ipa_characters_located_verbatim():
    line = "wəkəs ʃiːtəw"
    assert compute_term_spans(line, ["ʃiːtəw"]) == [(6, 12)]


def test_infinity_symbols_located_verbatim():
    line = "waney ∞êhs ∞êhs"
    assert compute_term_spans(line, ["∞êhs"]) == [(6, 10), (11, 15)]


def test_overlapping_and_adjacent_occurrences_emitted_in_order():
    line = "anana"
    spans = compute_term_spans(line, ["anan", "ana"])
    assert spans == sorted(spans)
    assert len(spans) >= 2
    # Every occurrence of "anan" must appear
    assert (0, 4) in spans


def test_multiple_terms_all_occurrences_collected():
    line = "api apa api"
    spans = compute_term_spans(line, ["api", "apa"])
    assert spans == sorted(spans)
    assert set(spans) == {(0, 3), (4, 7), (8, 11)}
