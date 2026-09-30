"""RED-phase tests for Issue #1385 SC-8: language filters disabled in semantic modes.

In Semantic Gloss and Semantic All modes, the language selectbox (selectbox[1])
and the language-role radio (radio[1]) are disabled with explanatory help text,
mirroring the FTS-mode disabled-filter idiom. Previously-selected values are
preserved but inert. Existing modes unchanged: Headword/Gloss/Lexeme keep
language filters ENABLED; FTS stays disabled with help text.

All tests MUST FAIL against current code for the semantic-mode assertions;
existing-mode assertions pass already and guard against regression.

Precedent harness: test/test_semantic_mode_radio_red.py,
test/ui/test_records_fts_disable.py, test/ui/test_records_fts_tooltips.py
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
mock_linguistic.get_languages.return_value = [{"id": 1, "name": "English"}]
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


class TestSemanticFiltersDisabledRED(unittest.TestCase):
    """RED-phase tests for SC-8 — semantic-mode assertions MUST FAIL currently."""

    def setUp(self):
        self.at = AppTest.from_string(RECORDS_SCRIPT, default_timeout=10)
        self.at.run()

    def _enter_semantic_mode(self, mode):
        self.at.radio[0].set_value(mode).run()

    # --- RED: disabled state in semantic modes ---

    def test_language_selectbox_disabled_in_semantic_gloss(self):
        """SC-8: Language selectbox disabled in Semantic Gloss mode."""
        self._enter_semantic_mode("Semantic Gloss")
        self.assertTrue(
            self.at.selectbox[1].disabled,
            "Language selectbox should be disabled in Semantic Gloss (RED: currently enabled)",
        )

    def test_language_selectbox_disabled_in_semantic_all(self):
        """SC-8: Language selectbox disabled in Semantic All mode."""
        self._enter_semantic_mode("Semantic All")
        self.assertTrue(
            self.at.selectbox[1].disabled,
            "Language selectbox should be disabled in Semantic All (RED: currently enabled)",
        )

    def test_language_role_radio_disabled_in_semantic_gloss(self):
        """SC-8: Language role radio disabled in Semantic Gloss mode."""
        self._enter_semantic_mode("Semantic Gloss")
        self.assertTrue(
            self.at.radio[1].disabled,
            "Language Role radio should be disabled in Semantic Gloss (RED: currently enabled)",
        )

    def test_language_role_radio_disabled_in_semantic_all(self):
        """SC-8: Language role radio disabled in Semantic All mode."""
        self._enter_semantic_mode("Semantic All")
        self.assertTrue(
            self.at.radio[1].disabled,
            "Language Role radio should be disabled in Semantic All (RED: currently enabled)",
        )

    # --- RED: explanatory help text in semantic modes (mirrors FTS idiom) ---

    def test_language_selectbox_has_help_in_semantic_gloss(self):
        """SC-8: Language selectbox has explanatory help text in Semantic Gloss."""
        self._enter_semantic_mode("Semantic Gloss")
        self.assertNotEqual(
            self.at.selectbox[1].help,
            "",
            "Language selectbox should show help text in Semantic Gloss (RED: empty help)",
        )

    def test_language_selectbox_has_help_in_semantic_all(self):
        """SC-8: Language selectbox has explanatory help text in Semantic All."""
        self._enter_semantic_mode("Semantic All")
        self.assertNotEqual(
            self.at.selectbox[1].help,
            "",
            "Language selectbox should show help text in Semantic All (RED: empty help)",
        )

    def test_language_role_radio_has_help_in_semantic_gloss(self):
        """SC-8: Language role radio has explanatory help text in Semantic Gloss."""
        self._enter_semantic_mode("Semantic Gloss")
        self.assertNotEqual(
            self.at.radio[1].help,
            "",
            "Language Role radio should show help text in Semantic Gloss (RED: empty help)",
        )

    def test_language_role_radio_has_help_in_semantic_all(self):
        """SC-8: Language role radio has explanatory help text in Semantic All."""
        self._enter_semantic_mode("Semantic All")
        self.assertNotEqual(
            self.at.radio[1].help,
            "",
            "Language Role radio should show help text in Semantic All (RED: empty help)",
        )

    def test_help_mentions_semantic_search(self):
        """SC-8: Help text explains the semantic-mode restriction."""
        self._enter_semantic_mode("Semantic Gloss")
        self.assertIn(
            "Semantic",
            self.at.selectbox[1].help,
            "Language help should explain semantic-mode restriction (RED: no help)",
        )

    # --- Regression guards: existing modes' filter behavior unchanged ---

    def test_language_filters_enabled_in_headword_gloss_lexeme(self):
        """SC-8: Headword/Gloss/Lexeme keep language filters ENABLED (no regression)."""
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

    def test_language_filters_disabled_with_help_in_fts_mode(self):
        """SC-8: FTS idiom unchanged — disabled with help text (existing idiom)."""
        self.at.radio[0].set_value("FTS").run()
        self.assertTrue(
            self.at.selectbox[1].disabled,
            "Language selectbox should remain disabled in FTS mode",
        )
        self.assertTrue(
            self.at.radio[1].disabled,
            "Language Role radio should remain disabled in FTS mode",
        )
        self.assertNotEqual(
            self.at.selectbox[1].help,
            "",
            "Language selectbox should keep help text in FTS mode",
        )

    # --- Preserved-but-inert value semantics ---

    def test_preselected_language_value_preserved_in_semantic_mode(self):
        """SC-8: Previously-selected language value is preserved when entering
        a semantic mode (rendered disabled, value unchanged)."""
        # Fixture: mock exposes one language ("English") so a real selection exists.
        self.assertEqual(
            self.at.selectbox[1].set_value("English").value,
            "English",
            "Fixture check: English option must be selectable",
        )
        self.at.radio[0].set_value("Semantic Gloss").run()
        self.assertEqual(
            self.at.selectbox[1].value,
            "English",
            "Language selection should be preserved (inert) in Semantic Gloss",
        )

    def test_source_selectbox_remains_enabled_in_semantic_modes(self):
        """SC-8 (R-9 corollary): source filter stays live in semantic modes."""
        for mode in ["Semantic Gloss", "Semantic All"]:
            self.at.radio[0].set_value(mode).run()
            self.assertFalse(
                self.at.selectbox[0].disabled,
                f"Source selectbox should remain enabled in {mode} mode",
            )


if __name__ == "__main__":
    unittest.main()
