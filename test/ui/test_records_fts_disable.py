"""RED-phase tests: FTS mode disables language/language-role filters.

SC-4: Language and Language Role filters are disabled when search mode is FTS.
RED: Language dropdown and Language Role radio are NOT disabled in FTS mode.
"""
import unittest
from streamlit.testing.v1 import AppTest

RECORDS_SCRIPT = """
import streamlit as st
from unittest.mock import MagicMock

mock_linguistic = MagicMock()
mock_linguistic.search_records.return_value = MagicMock(records=[], total_count=0)
mock_linguistic.get_sources_with_counts.return_value = []
mock_linguistic.get_languages.return_value = []
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


class TestFTSDisableRED(unittest.TestCase):
    """RED-phase tests for SC-4 — all MUST FAIL against current code."""

    def setUp(self):
        self.at = AppTest.from_string(RECORDS_SCRIPT, default_timeout=10)

    def test_language_selectbox_disabled_in_fts_mode(self):
        """SC-4: RED — Language selectbox is disabled when FTS mode selected."""
        self.at.run()
        self.at.radio[0].set_value("FTS").run()
        self.assertTrue(
            self.at.selectbox[1].disabled,
            "Language selectbox should be disabled in FTS mode (RED: not yet disabled)",
        )

    def test_language_role_radio_disabled_in_fts_mode(self):
        """SC-4: RED — Language Role radio is disabled when FTS mode selected."""
        self.at.run()
        self.at.radio[0].set_value("FTS").run()
        self.assertTrue(
            self.at.radio[1].disabled,
            "Language Role radio should be disabled in FTS mode (RED: not yet disabled)",
        )

    def test_language_filters_enabled_in_headword_mode(self):
        """SC-4: RED — Language filters remain enabled in non-FTS modes."""
        self.at.run()
        for mode in ["Headword", "Gloss", "Lexeme"]:
            self.at.radio[0].set_value(mode).run()
            self.assertFalse(
                self.at.selectbox[1].disabled,
                f"Language selectbox should be enabled in {mode} mode",
            )
            self.assertFalse(
                self.at.radio[1].disabled,
                f"Language Role radio should be enabled in {mode} mode",
            )


if __name__ == "__main__":
    unittest.main()
