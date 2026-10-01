"""RED-phase tests for Issue #1385 Item 1: Semantic Gloss / Semantic All mode radio entries.

SC-1: The records-page mode radio renders Semantic Gloss and Semantic All entries while
existing entries and captions remain unchanged; the new modes ADD SEARCH_MODE_CAPTIONS
dict entries and the single selected-mode caption pattern (one caption for the SELECTED
mode, rendered under the radio) is preserved unchanged.

All tests MUST FAIL against current code (RED phase).

Precedent harness: test/test_search_mode_ui_red.py
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
    for _path, _saved in _saved_modules.items():
        if _saved is not None:
            sys.modules[_path] = _saved
        else:
            del sys.modules[_path]
"""


class TestSemanticModeRadioRED(unittest.TestCase):
    """RED-phase tests for SC-1 — all MUST FAIL against current code."""

    def setUp(self):
        self.at = AppTest.from_string(RECORDS_SCRIPT, default_timeout=10)
        self.at.run()

    def _mode_radio(self):
        return self.at.radio(key="search_mode_radio")

    def test_radio_has_six_options_including_semantic_modes(self):
        """SC-1: RED — asserts 6 options incl. Semantic Gloss/Semantic All; currently 4."""
        radio = self._mode_radio()
        self.assertIn(
            "Semantic Gloss",
            radio.options,
            "Radio should offer Semantic Gloss (RED: missing)",
        )
        self.assertIn(
            "Semantic All",
            radio.options,
            "Radio should offer Semantic All (RED: missing)",
        )

    def test_existing_four_options_preserved(self):
        """SC-1: existing 4 options remain in order — sanity part of SC-1.

        This passes currently; the RED signal comes from the semantic-mode tests.
        Included so GREEN cannot silently drop the existing options.
        """
        radio = self._mode_radio()
        self.assertEqual(
            radio.options[:4],
            ["Headword", "Gloss", "Lexeme", "FTS"],
            "Existing options must be preserved unchanged",
        )

    def test_search_mode_captions_dict_has_semantic_keys(self):
        """SC-1: RED — SEARCH_MODE_CAPTIONS lacks the two semantic keys (currently)."""
        import re

        with open("src/frontend/pages/records.py", encoding="utf-8") as f:
            source = f.read()
        dict_match = re.search(
            r"SEARCH_MODE_CAPTIONS\s*=\s*\{(.*?)\}", source, re.DOTALL
        )
        assert dict_match, "SEARCH_MODE_CAPTIONS dict must exist"
        dict_body = dict_match.group(1)
        self.assertIn(
            '"Semantic Gloss"',
            dict_body,
            "SEARCH_MODE_CAPTIONS should gain Semantic Gloss key (RED: missing)",
        )
        self.assertIn(
            '"Semantic All"',
            dict_body,
            "SEARCH_MODE_CAPTIONS should gain Semantic All key (RED: missing)",
        )

    def test_semantic_mode_caption_renders_when_selected(self):
        """SC-1: RED — selecting Semantic Gloss shows no caption (key absent today)."""
        self.at.session_state["search_mode"] = "Semantic Gloss"
        self.at.run()
        captions = [c.value for c in self.at.caption]
        non_empty = [c for c in captions if c]
        self.assertTrue(
            non_empty,
            "Semantic Gloss selection should render its mode caption (RED: no key)",
        )

    def test_semantic_all_mode_caption_renders_when_selected(self):
        """SC-1: RED — selecting Semantic All shows no caption (key absent today)."""
        self.at.session_state["search_mode"] = "Semantic All"
        self.at.run()
        captions = [c.value for c in self.at.caption]
        non_empty = [c for c in captions if c]
        self.assertTrue(
            non_empty,
            "Semantic All selection should render its mode caption (RED: no key)",
        )


if __name__ == "__main__":
    unittest.main()
