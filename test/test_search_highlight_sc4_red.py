"""RED test for SC-4 (issue 1401): pure FTS query-token span helper — no-match empty contract.

Samples per spec item 4: token-free queries (queries containing only
tsquery-unsafe characters), empty queries, and no-match lines — the helper
must return an empty span list for each, not partially highlighted output.

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

from src.frontend.search_highlight import _query_tokens, compute_fts_spans
from src.services.linguistic_service import LinguisticService


def test_sc4_only_tsquery_unsafe_query_returns_empty_spans():
    query = "|&!()"
    assert _query_tokens(query) == []
    assert compute_fts_spans("hog ∞wonk moo", query) == []


def test_sc4_empty_query_returns_empty_spans():
    assert compute_fts_spans("hog moo", "") == []
    assert compute_fts_spans("hog moo", "   ") == []
    assert compute_fts_spans("hog moo", "\t\n") == []


def test_sc4_no_match_line_returns_empty_spans():
    for query, line in [
        ("xyzzy", "kehtakamui wonk"),
        ("zzz |&!", "api apa"),
        ("hogk", "wəkəs ʃiːtəw"),
        ("moo", ""),
    ]:
        assert _query_tokens(query), "sample requires a surviving token"
        assert not any(
            LinguisticService.generate_sort_lx(w).startswith(tok)
            for w in line.split()
            for tok in _query_tokens(query)
        ), "sample requires a disjoint line vocabulary"
        assert compute_fts_spans(line, query) == []
