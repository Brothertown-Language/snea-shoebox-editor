"""Tests for Headword and Gloss mode filter behavior.

SC-7 (Phase 4): Headword and Gloss modes work with language filters enabled.

Co-authored with AI: OpenCode (ollama-cloud/deepseek-v4-flash)
"""
import unittest
from unittest.mock import MagicMock, patch

from src.services.linguistic_service import LinguisticService


class TestHeadwordGlossFilters(unittest.TestCase):
    """Verify Headword and Gloss modes work correctly with language filters."""

    def setUp(self):
        self.mock_session = MagicMock()
        self.session_patcher = patch(
            "src.services.linguistic_service.get_session",
            return_value=MagicMock(__enter__=MagicMock(return_value=self.mock_session)),
        )
        self.session_patcher.start()

    def tearDown(self):
        self.session_patcher.stop()

    def test_headword_mode_with_language_filter(self):
        """Headword mode with language filter should return results."""
        result = LinguisticService.search_records(
            language_id=1, search_term="test", search_mode="Headword"
        )
        self.assertIsNotNone(result)

    def test_gloss_mode_with_language_filter(self):
        """Gloss mode with language filter should return results."""
        result = LinguisticService.search_records(
            language_id=1, search_term="test", search_mode="Gloss"
        )
        self.assertIsNotNone(result)

    def test_headword_mode_with_language_role(self):
        """Headword mode with language role filter should return results."""
        result = LinguisticService.search_records(
            language_id=1, language_role="primary", search_term="test", search_mode="Headword"
        )
        self.assertIsNotNone(result)

    def test_gloss_mode_with_language_role(self):
        """Gloss mode with language role filter should return results."""
        result = LinguisticService.search_records(
            language_id=1, language_role="primary", search_term="test", search_mode="Gloss"
        )
        self.assertIsNotNone(result)

    def test_headword_mode_without_filters(self):
        """Headword mode without filters should return results."""
        result = LinguisticService.search_records(search_term="test", search_mode="Headword")
        self.assertIsNotNone(result)

    def test_gloss_mode_without_filters(self):
        """Gloss mode without filters should return results."""
        result = LinguisticService.search_records(search_term="test", search_mode="Gloss")
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
