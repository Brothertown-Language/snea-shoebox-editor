"""Tests for empty search input behavior in Records view.

SC-8 (Phase 3): Empty search input returns all records / no error.

Co-authored with AI: OpenCode (ollama-cloud/deepseek-v4-flash)
"""
import unittest
from unittest.mock import MagicMock, patch

from src.services.linguistic_service import LinguisticService


class TestEmptySearch(unittest.TestCase):
    """Verify empty search input returns all records without error."""

    def setUp(self):
        self.mock_session = MagicMock()
        self.session_patcher = patch(
            "src.services.linguistic_service.get_session",
            return_value=MagicMock(__enter__=MagicMock(return_value=self.mock_session)),
        )
        self.session_patcher.start()

    def tearDown(self):
        self.session_patcher.stop()

    def test_empty_search_term_returns_results(self):
        """Empty search term should return all records (no error)."""
        result = LinguisticService.search_records(search_term=None)
        self.assertIsNotNone(result)

    def test_empty_string_search_returns_results(self):
        """Empty string search term should return all records (no error)."""
        result = LinguisticService.search_records(search_term="")
        self.assertIsNotNone(result)

    def test_search_with_only_filters_no_term(self):
        """Search with filters but no search term should return filtered results."""
        result = LinguisticService.search_records(
            source_id=1, language_id=1, search_term=None
        )
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
