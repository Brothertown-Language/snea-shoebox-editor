"""SC-5 RED: RecordSearchResult must gain an additive optional `matched_terms` field.

The field does not exist yet, so this test FAILS (AttributeError) before GREEN.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import pytest

from src.services.linguistic_service import RecordSearchResult


def test_matched_terms_field_exists_default_none_sc5():
    result = RecordSearchResult(records=[], total_count=0, limit=10, offset=0)
    assert result.matched_terms is None


def test_matched_terms_accepts_value_sc5():
    result = RecordSearchResult(
        records=[], total_count=0, limit=10, offset=0, matched_terms={"foo"}
    )
    assert result.matched_terms == {"foo"}


def test_existing_construction_sites_source_compatible_sc5():
    # All pre-change construction call-sites use positional/keyword args
    # without matched_terms; they must keep working unchanged.
    positional = RecordSearchResult([], 0, 10, 0)
    assert positional.matched_terms is None
    keyword = RecordSearchResult(
        records=[], total_count=0, limit=10, offset=0
    )
    assert keyword.matched_terms is None
    assert keyword.records == []
    assert keyword.total_count == 0
    assert keyword.limit == 10
    assert keyword.offset == 0
