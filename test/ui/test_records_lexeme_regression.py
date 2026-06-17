"""RED-phase regression tests: Lexeme mode searches with language filters.

SC-5: Existing Lexeme mode searches continue to work with language filters.
RED: Lexeme mode with language filters currently works (baseline regression).
GREEN: Same tests still pass after FTS disable logic is added.
"""
import unittest
from streamlit.testing.v1 import AppTest

RECORDS_SCRIPT = """
import streamlit as st
from unittest.mock import MagicMock

mock_results = MagicMock(records=[], total_count=0)
mock_linguistic = MagicMock()
mock_linguistic.search_records.return_value = mock_results
mock_linguistic.get_sources_with_counts.return_value = []
mock_linguistic.get_languages.return_value = [{"id": 1, "name": "Unami"}, {"id": 2, "name": "Munsee"}]
mock_linguistic.get_all_records_for_export.return_value = []
mock_linguistic.get_record.return_value = None
mock_linguistic.bundle_records_to_mdf.return_value = ""
mock_linguistic.stream_records_to_temp_file.return_value = "/tmp/test"
mock_linguistic.get_edit_history.return_value = []

mock_preference = MagicMock()
mock_preference.get_preference.return_value = "25"

mock_identity = MagicMock()
mock_identity.get_github_username.return_value = "tester"

mock_nav = MagicMock()
mock_nav.PAGE_DIRECT_ENTRY = "/direct_entry"

mock_upload = MagicMock()
mock_upload.generate_mdf_filename.return_value = "test.mdf"

mock_validator = MagicMock()
mock_validator.diagnose_record.return_value = None

import sys
sys.modules["src.services.linguistic_service"] = MagicMock()
sys.modules["src.services.linguistic_service"].LinguisticService = mock_linguistic
sys.modules["src.services.preference_service"] = MagicMock()
sys.modules["src.services.preference_service"].PreferenceService = mock_preference
sys.modules["src.services.identity_service"] = MagicMock()
sys.modules["src.services.identity_service"].IdentityService = mock_identity
sys.modules["src.services.navigation_service"] = MagicMock()
sys.modules["src.services.navigation_service"].NavigationService = mock_nav
sys.modules["src.services.upload_service"] = MagicMock()
sys.modules["src.services.upload_service"].UploadService = mock_upload
sys.modules["src.mdf.validator"] = MagicMock()
sys.modules["src.mdf.validator"].MDFValidator = mock_validator

from src.frontend.pages.records import records
records()
"""


class TestLexemeRegressionRED(unittest.TestCase):
    """RED-phase regression tests for SC-5 — baseline current behavior."""

    def setUp(self):
        self.at = AppTest.from_string(RECORDS_SCRIPT, default_timeout=10)

    def test_lexeme_language_filter_enabled(self):
        """SC-5: RED — Language selectbox is enabled in Lexeme mode."""
        self.at.run()
        self.at.radio[0].set_value("Lexeme").run()
        self.assertFalse(
            self.at.selectbox[1].disabled,
            "Language selectbox should be enabled in Lexeme mode",
        )

    def test_lexeme_language_role_filter_enabled(self):
        """SC-5: RED — Language Role radio is enabled in Lexeme mode."""
        self.at.run()
        self.at.radio[0].set_value("Lexeme").run()
        self.assertFalse(
            self.at.radio[1].disabled,
            "Language Role radio should be enabled in Lexeme mode",
        )

    def test_headword_language_filter_enabled(self):
        """SC-5: RED — Language selectbox is enabled in Headword mode."""
        self.at.run()
        self.at.radio[0].set_value("Headword").run()
        self.assertFalse(
            self.at.selectbox[1].disabled,
            "Language selectbox should be enabled in Headword mode",
        )

    def test_gloss_language_filter_enabled(self):
        """SC-5: RED — Language selectbox is enabled in Gloss mode."""
        self.at.run()
        self.at.radio[0].set_value("Gloss").run()
        self.assertFalse(
            self.at.selectbox[1].disabled,
            "Language selectbox should be enabled in Gloss mode",
        )


if __name__ == "__main__":
    unittest.main()
