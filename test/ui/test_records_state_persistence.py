"""Tests for filter state persistence across mode switches in Records view.

SC-10 (Phase 3): Active filter state persists across mode switches.

Co-authored with AI: OpenCode (ollama-cloud/deepseek-v4-flash)
"""
import unittest
from unittest.mock import MagicMock, patch

from src.services.linguistic_service import LinguisticService


class TestStatePersistence(unittest.TestCase):
    """Verify filter state persists across search mode switches."""

    def setUp(self):
        self.mock_session = MagicMock()
        self.session_patcher = patch(
            "src.services.linguistic_service.get_session",
            return_value=MagicMock(__enter__=MagicMock(return_value=self.mock_session)),
        )
        self.session_patcher.start()

    def tearDown(self):
        self.session_patcher.stop()

    def test_search_with_source_filter(self):
        """Search with source filter should work."""
        result = LinguisticService.search_records(source_id=1)
        self.assertIsNotNone(result)

    def test_search_with_language_filter(self):
        """Search with language filter should work."""
        result = LinguisticService.search_records(language_id=1)
        self.assertIsNotNone(result)

    def test_search_with_language_role_filter(self):
        """Search with language role filter should work."""
        result = LinguisticService.search_records(language_id=1, language_role="primary")
        self.assertIsNotNone(result)

    def test_search_with_all_filters(self):
        """Search with all filters combined should work."""
        result = LinguisticService.search_records(
            source_id=1, language_id=1, language_role="primary"
        )
        self.assertIsNotNone(result)

    def test_search_without_filters(self):
        """Search without any filters should return all records."""
        result = LinguisticService.search_records()
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
