"""RED-phase tests for Phase 5: Search Mode UI — Vertical Radio with Grouping.

Items 1-5 from plan at .issues/1126/plan.md.
All tests MUST FAIL against current code (RED phase).
"""
import unittest

from streamlit.testing.v1 import AppTest

RECORDS_SCRIPT = """
import streamlit as st
from unittest.mock import MagicMock

# Mock all service dependencies at the module level before records() is called
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

# Patch the actual module paths that records() imports inside its function body.
# Insert-only containment: save any pre-existing entries, then restore them at
# scope-exit so this script never deletes entries owned by other tests that
# installed real modules (or their own mocks) into sys.modules earlier.
import sys

_MOCK_MODULE_PATHS = [
    "src.services.linguistic_service",
    "src.services.preference_service",
    "src.services.identity_service",
    "src.services.navigation_service",
    "src.services.upload_service",
    "src.mdf.validator",
]
_saved_modules = {p: sys.modules.get(p) for p in _MOCK_MODULE_PATHS}
try:
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
finally:
    # Restore only carrier-inserted entries; never delete pre-existing entries.
    for _path, _saved in _saved_modules.items():
        if _saved is not None:
            sys.modules[_path] = _saved
        else:
            del sys.modules[_path]
"""


class TestSearchModeUIRED(unittest.TestCase):
    """RED-phase tests — all MUST FAIL against current code."""

    def setUp(self):
        self.at = AppTest.from_string(RECORDS_SCRIPT, default_timeout=10)

    # --- Item 1: Default mode change (SC-1) ---
    def test_search_defaults_to_headword(self):
        """SC-1: RED — asserts default is 'Headword', but current default is 'Lexeme'."""
        self.at.run()
        self.assertEqual(
            self.at.session_state["search_mode"],
            "Headword",
            "Default search mode should be Headword (RED: currently Lexeme)",
        )

    # --- Item 2: Vertical radio with 4 options + separators (SC-2, SC-8) ---
    def test_vertical_radio_shows_four_options(self):
        """SC-2: RED — asserts 4 radio options, currently 2."""
        self.at.run()
        radio = self.at.radio[0]
        self.assertEqual(
            len(radio.options),
            4,
            "Radio should have 4 options (RED: currently 2)",
        )

    # --- Item 3: Search header shows mode name + count (SC-6) ---
    def test_header_shows_mode_name_and_count(self):
        """SC-6: GREEN — asserts header includes mode name via 'Search:' prefix."""
        self.at.session_state["search_query"] = "test"
        self.at.run()
        header_text = " ".join(md.value or "" for md in self.at.markdown)
        self.assertIn(
            "Search:",
            header_text,
            "Header should contain 'Search:' prefix with mode name",
        )

    # --- Item 5: Search/clear buttons full width below radio (SC-9) ---
    def test_search_buttons_full_width_below_radio(self):
        """SC-9: RED — asserts buttons not in 0.15 columns, currently in 0.15 columns.

        Current code uses st.columns([0.7, 0.15, 0.15]) for the search/clear buttons.
        After GREEN, buttons should be full-width below radio, not in 0.15 columns.
        """
        self.at.run()
        # Current code has 3 columns with specs [0.7, 0.15, 0.15]
        # After GREEN, this column layout should be removed
        col_weights = [col.weight for col in self.at.columns]
        has_015 = any(w == 0.15 for w in col_weights)
        self.assertFalse(
            has_015,
            "Buttons should not be in 0.15-width columns (RED: currently 0.15)",
        )


if __name__ == "__main__":
    unittest.main()
