"""RED test for SC-3 (issue 1401): pure FTS query-token span helper — match spans.

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

import unicodedata

import pytest

from src.frontend.search_highlight import compute_fts_spans
from src.services.linguistic_service import LinguisticService, _TSQUERY_UNSAFE

normalize = LinguisticService.generate_sort_lx


def _expected_token_set(query: str) -> set[str]:
    """Replicate the FTS strategy's query-token derivation (parity oracle).

    Mirrors _search_fts: normalize via the service normalizer, then strip
    tsquery-unsafe characters per word and drop empties.
    """
    return {
        clean
        for w in normalize(query).split()
        if (clean := _TSQUERY_UNSAFE.sub("", w).strip())
    }


def test_query_tokens_normalized_with_tsquery_unsafe_stripping():
    """Span helper derives query tokens exactly like the FTS strategy."""
    line = "hogk moo"
    query = "hogk |&!(moo"
    assert _expected_token_set(query) == {"hogk", "moo"}
    spans = compute_fts_spans(line, query)
    # Both words match their tokens by prefix (`:*` semantics) and light up whole
    assert spans == [(0, 4), (5, 8)]


@pytest.mark.parametrize(
    ("query", "tokens", "line"),
    [
        ("hogk|&!", {"hogk"}, "hogkwankey hoy"),
        ("(hogk)!", {"hogk"}, "hogkwankey hoy"),
        ("a|b&!c", {"abc"}, "abcak abolina"),
    ],
)
def test_tsquery_operators_stripped_from_query_tokens(query, tokens, line):
    compute_fts_spans(line, query)
    assert _expected_token_set(query) == tokens
    # Every surviving token must still match a line word by its prefix
    for tok in tokens:
        assert any(normalize(w).startswith(tok) for w in line.split())


def test_prefix_smoke():
    line = "hogkwankey hoy"
    assert compute_fts_spans(line, "hogk") == [(0, 10)]


def test_multi_token_query_matches_all_tokens_words():
    line = "api apa api"
    spans = compute_fts_spans(line, "api apa")
    expected_tokens = _expected_token_set("api apa")
    assert expected_tokens == {"api", "apa"}
    # Whole-word spans: each token's occurrences light up in full
    assert spans == [(0, 3), (4, 7), (8, 11)]


def test_unicode_safe_line_tokenization_no_ascii_classes():
    r"""The line is split Unicode-safely (\w-based, not [a-zA-Z]); IPA & diacritics are letters."""
    line = "wəkəs ʃiːtəw ãney"
    tokens = _expected_token_set("ʃiːtəw ãney")
    assert tokens == {"ʃiːtəw", "aney"}  # ã → a via the normalizer
    spans = compute_fts_spans(line, "ʃiːtəw ãney")
    # Neither IPA nor precomposed diacritic words are dropped by tokenizer artifacts
    words = line.split()
    assert ("ʃiːtəw", normalize("ʃiːtəw")) in [(w, normalize(w)) for w in words]
    assert spans == [(6, 12), (13, 17)]


def test_nfd_decomposed_diacritic_line_word_matches_normalized_token():
    line = "pre " + unicodedata.normalize("NFD", "nãwa") + " hoy"
    # Query token "nawa" (normalizer strips diacritics) matches the NFD word
    spans = compute_fts_spans(line, "nawa")
    assert _expected_token_set("nawa") == {"nawa"}
    assert spans == [(4, 9)]


def test_infinity_normalized_form_consistency_query_and_line():
    """Query ∞ and line ∞ normalize identically through generate_sort_lx (∞→oozzz)."""
    assert normalize("∞") == "oozzz"
    line = "*|achm∞wonk| hogk∞"
    assert _expected_token_set("achm∞wonk") == {"achmoozzzwonk"}
    assert _expected_token_set("hogk∞") == {"hogkoozzz"}
    # Unicode-safe tokenization delimits the words at */|; the normalized word
    # forms match the query tokens by prefix and the whole raw words light up
    assert compute_fts_spans(line, "achm∞wonk") == [(2, 11)]
    assert compute_fts_spans(line, "hogk∞") == [(13, 18)]


def test_no_match_query_token_emits_nothing_for_that_token():
    line = "api apa"
    spans = compute_fts_spans(line, "zzz")
    assert spans == []
