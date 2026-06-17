"""Tests for Unicode safety in Records view filter values.

SC-9 (Phase 3): Unicode characters in filter values don't crash.

Co-authored with AI: OpenCode (ollama-cloud/deepseek-v4-flash)
"""
import unittest
from unittest.mock import MagicMock, patch

from src.services.linguistic_service import LinguisticService


class TestUnicodeSafety(unittest.TestCase):
    """Verify Unicode characters in filter values don't crash the application."""

    def setUp(self):
        self.mock_session = MagicMock()
        self.session_patcher = patch(
            "src.services.linguistic_service.get_session",
            return_value=MagicMock(__enter__=MagicMock(return_value=self.mock_session)),
        )
        self.session_patcher.start()

    def tearDown(self):
        self.session_patcher.stop()

    def test_accented_chars_in_search_term(self):
        """Accented characters in search term should not crash."""
        result = LinguisticService.search_records(search_term="éàüöñç")
        self.assertIsNotNone(result)

    def test_cjk_chars_in_search_term(self):
        """CJK characters in search term should not crash."""
        result = LinguisticService.search_records(search_term="中文測試")
        self.assertIsNotNone(result)

    def test_special_unicode_in_search_term(self):
        """Special Unicode characters (emoji, symbols) should not crash."""
        result = LinguisticService.search_records(search_term="★♪✓")
        self.assertIsNotNone(result)

    def test_unicode_in_source_filter(self):
        """Unicode characters in source name should not crash."""
        result = LinguisticService.search_records(source_id=1, search_term="test")
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
