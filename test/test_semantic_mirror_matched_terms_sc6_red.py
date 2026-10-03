"""SC-6 (Issue #1401) RED test: the page-local mirror container
`_RecordSearchResultLike` in `src/frontend/pages/records.py` — the
duck-typed mirror of the service `RecordSearchResult` used for
seam-consumed semantic results — must gain an additive optional
`matched_terms` field.

Currently the mirror has no `matched_terms` attribute, so this test
FAILS (AttributeError) before GREEN. After GREEN the semantic-seam
mirror construction must:
1. Complete without raising, and
2. Read `matched_terms` as None by default when the service result
   does not supply one.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from src.frontend.pages.records import _RecordSearchResultLike


def test_mirror_has_matched_terms_default_none_sc6():
    # Construction at the semantic seam call-site shape (records.py:301)
    # must complete without raising, and matched_terms must default to
    # None when the service result does not supply one.
    mirror = _RecordSearchResultLike(
        records=[],
        total_count=0,
        limit=10,
        offset=0,
    )
    assert mirror.matched_terms is None


def test_mirror_accepts_matched_terms_value_sc6():
    # After GREEN the mirror must also accept an explicit matched_terms
    # value (service result supplying one), field-additively.
    mirror = _RecordSearchResultLike(
        records=[],
        total_count=0,
        limit=10,
        offset=0,
        matched_terms={"foo": "bar"},
    )
    assert mirror.matched_terms == {"foo": "bar"}


def test_mirror_positional_construction_default_none_sc6():
    # Pre-change positional construction sites must stay source-compatible
    # and read matched_terms as None by default.
    mirror = _RecordSearchResultLike([], 0, 10, 0)
    assert mirror.matched_terms is None
    assert mirror.records == []
    assert mirror.total_count == 0
    assert mirror.limit == 10
    assert mirror.offset == 0


def test_mirror_matches_service_contract_shape_sc6():
    # The mirror must remain duck-type compatible with the service
    # RecordSearchResult contract including the new field's default.
    from src.services.linguistic_service import RecordSearchResult

    service_result = RecordSearchResult(
        records=[], total_count=0, limit=10, offset=0
    )
    mirror = _RecordSearchResultLike(
        records=service_result.records,
        total_count=service_result.total_count,
        limit=service_result.limit,
        offset=service_result.offset,
    )
    assert mirror.matched_terms is None
