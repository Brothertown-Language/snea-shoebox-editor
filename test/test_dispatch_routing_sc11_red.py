# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN -->
"""RED test for Issue #36 Phase 4 Item 11 (SC-11, behavioral).

Dispatch-routing contract:
- SearchMode Literal widens with 'Semantic Gloss' and 'Semantic All'.
- _search_strategies dispatch map routes both semantic modes to
  src.services.semantic_search_service.search_semantic().
- Existing four modes (Lexeme/FTS/Headword/Gloss) route unchanged.
- search_records signature and RecordSearchResult return type unchanged.

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""

import inspect

import pytest

from src.services import linguistic_service
from src.services.linguistic_service import LinguisticService, RecordSearchResult, SearchMode


def get_search_mode_args():
    """Extract the literal string args of the SearchMode alias."""
    return list(getattr(SearchMode, "__args__", ()))


class TestSearchModeLiteralWidened:
    """SearchMode Literal must include the two semantic modes."""

    def test_semantic_gloss_in_search_mode(self):
        assert "Semantic Gloss" in get_search_mode_args()

    def test_semantic_all_in_search_mode(self):
        assert "Semantic All" in get_search_mode_args()

    def test_existing_modes_unchanged(self):
        for mode in ("Lexeme", "FTS", "Headword", "Gloss"):
            assert mode in get_search_mode_args(), f"existing mode {mode} missing"

    def test_search_mode_arg_count(self):
        assert len(get_search_mode_args()) == 6


class TestDispatchRouting:
    """_search_strategies must route semantic modes to search_semantic()."""

    def _import_search_semantic(self):
        from src.services.semantic_search_service import search_semantic

        return search_semantic

    def test_semantic_gloss_routed_to_search_semantic(self):
        target = self._import_search_semantic()
        assert linguistic_service._search_strategies.get("Semantic Gloss") is target

    def test_semantic_all_routed_to_search_semantic(self):
        target = self._import_search_semantic()
        assert linguistic_service._search_strategies.get("Semantic All") is target

    def test_existing_modes_route_unchanged(self):
        assert linguistic_service._search_strategies["Lexeme"] is linguistic_service._search_lexeme
        assert linguistic_service._search_strategies["FTS"] is linguistic_service._search_fts
        assert linguistic_service._search_strategies["Headword"] is linguistic_service._search_headword
        assert linguistic_service._search_strategies["Gloss"] is linguistic_service._search_gloss


class TestSearchRecordsContractUnchanged:
    """search_records signature and return type must be unchanged."""

    def test_signature_params_unchanged(self):
        sig = inspect.signature(LinguisticService.search_records)
        params = list(sig.parameters.keys())
        assert params == [
            "source_id",
            "language_id",
            "language_role",
            "status",
            "is_locked",
            "search_term",
            "search_mode",
            "record_ids",
            "limit",
            "offset",
        ]
        assert sig.parameters["search_mode"].annotation == SearchMode

    def test_search_mode_default_unchanged(self):
        sig = inspect.signature(LinguisticService.search_records)
        assert sig.parameters["search_mode"].default == "Lexeme"

    def test_return_type_record_search_result(self):
        src = inspect.getsource(LinguisticService.search_records)
        assert "RecordSearchResult" in src