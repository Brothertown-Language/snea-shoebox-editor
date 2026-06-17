"""RED-phase tests: FTS mode shows tooltips on disabled filters.

SC-6: Clear visual indication when filters are disabled (tooltip explanation).
RED: No tooltips exist for disabled filter state.
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


class TestFTSTooltipsRED(unittest.TestCase):
    """RED-phase tests for SC-6 — all MUST FAIL against current code."""

    def setUp(self):
        self.at = AppTest.from_string(RECORDS_SCRIPT, default_timeout=10)

    def test_language_selectbox_has_help_in_fts_mode(self):
        """SC-6: RED — Language selectbox shows tooltip when disabled in FTS."""
        self.at.run()
        self.at.radio[0].set_value("FTS").run()
        self.assertNotEqual(
            self.at.selectbox[1].help,
            "",
            "Language selectbox should have tooltip in FTS mode (RED: empty help)",
        )

    def test_language_role_radio_has_help_in_fts_mode(self):
        """SC-6: RED — Language Role radio shows tooltip when disabled in FTS."""
        self.at.run()
        self.at.radio[0].set_value("FTS").run()
        self.assertNotEqual(
            self.at.radio[1].help,
            "",
            "Language Role radio should have tooltip in FTS mode (RED: empty help)",
        )

    def test_tooltip_mentions_fts(self):
        """SC-6: RED — Tooltip text mentions Full-Text Search."""
        self.at.run()
        self.at.radio[0].set_value("FTS").run()
        help_text = self.at.selectbox[1].help
        self.assertNotEqual(help_text, "", "Tooltip should not be empty (RED: no tooltip)")
        self.assertIn(
            "Full-Text Search",
            help_text,
            "Tooltip should mention Full-Text Search (RED: no appropriate tooltip text)",
        )


if __name__ == "__main__":
    unittest.main()
