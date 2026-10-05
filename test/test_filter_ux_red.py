
"""RED-phase tests for Records View Left Panel Filter UX Improvements.

SC-1 (Phase 1): Sources dropdown shows "All Sources" instead of "All"
SC-2 (Phase 1): Languages dropdown shows "All Languages" instead of "All"
SC-4 (Phase 3): Search and clear buttons appear side-by-side
SC-5 (Phase 4): Clear button immediately empties search box
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


class TestFilterUXRED(unittest.TestCase):
    """RED-phase tests — all MUST FAIL against current code."""

    def setUp(self):
        self.at = AppTest.from_string(RECORDS_SCRIPT, default_timeout=10)

    # --- Phase 1: Dropdown Labels (SC-1, SC-2) ---
    def test_source_dropdown_shows_all_sources(self):
        """SC-1: RED — source selectbox shows 'All Sources', currently shows 'All'."""
        self.at.run()
        self.assertEqual(
            self.at.selectbox[0].value,
            "All Sources",
            "Source selectbox should show 'All Sources' (RED: currently 'All')",
        )

    def test_language_dropdown_shows_all_languages(self):
        """SC-2: RED — language selectbox shows 'All Languages', currently shows 'All'."""
        self.at.run()
        self.assertEqual(
            self.at.selectbox[1].value,
            "All Languages",
            "Language selectbox should show 'All Languages' (RED: currently 'All')",
        )

    # --- Phase 3: Buttons Side-by-Side (SC-4) ---
    def test_search_clear_buttons_in_columns(self):
        """SC-4: search and clear buttons appear side-by-side in columns.

        Updated for Issue #1413: the sidebar page-level pager (its own two
        button columns) was relocated to twin main-panel navigation rows, so
        the sidebar now renders 5 column groups (search-clear + selection)
        instead of the previous 7 that included the pagination columns."""
        self.at.run()
        self.assertEqual(
            len(self.at.columns),
            5,
            "Should be 5 column groups (search-clear + selection) after the "
            "#1413 pagination relocation removed the sidebar pager columns",
        )

    # --- Phase 4: Clear Behavior (SC-5) ---
    def test_clear_button_empties_text_input(self):
        """SC-5: RED — clear button empties text input after rerun,
        currently text input stays stale."""
        self.at.run()
        self.at.text_input[0].set_value("test").run()
        for b in self.at.button:
            if b.key == "search_clear":
                b.click().run()
                break
        self.assertEqual(
            self.at.text_input[0].value,
            "",
            "Clear button should empty text input immediately (RED: currently stale 'test')",
        )


if __name__ == "__main__":
    unittest.main()
