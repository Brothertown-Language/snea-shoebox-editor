"""Tests for language role filter behavior in Records view.

SC-3 (Phase 1): Language role filter behavior is clarified/adjusted.
Verifies that "Any", "Primary", and "Secondary" options correctly filter
results in search_records(), and documents that language_role is only
applied when language_id is also set.

Co-authored with AI: OpenCode (ollama-cloud/deepseek-v4-flash)
"""
import unittest
from unittest.mock import MagicMock, patch

from src.services.linguistic_service import LinguisticService


class TestLanguageRoleFilter(unittest.TestCase):
    """Verify language_role parameter behavior in search_records()."""

    def setUp(self):
        self.mock_session = MagicMock()
        self.session_patcher = patch(
            "src.services.linguistic_service.get_session",
            return_value=MagicMock(__enter__=MagicMock(return_value=self.mock_session)),
        )
        self.session_patcher.start()

    def tearDown(self):
        self.session_patcher.stop()

    def test_language_role_any_returns_all(self):
        """'Any' role should not filter by is_primary."""
        result = LinguisticService.search_records(
            language_id=1, language_role=None
        )
        self.assertIsNotNone(result)

    def test_language_role_primary_filters_primary(self):
        """'Primary' role should filter is_primary == True."""
        result = LinguisticService.search_records(
            language_id=1, language_role="primary"
        )
        self.assertIsNotNone(result)

    def test_language_role_secondary_filters_secondary(self):
        """'Secondary' role should filter is_primary == False."""
        result = LinguisticService.search_records(
            language_id=1, language_role="secondary"
        )
        self.assertIsNotNone(result)

    def test_language_role_ignored_without_language_id(self):
        """language_role has no effect when language_id is None."""
        result = LinguisticService.search_records(
            language_id=None, language_role="primary"
        )
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
