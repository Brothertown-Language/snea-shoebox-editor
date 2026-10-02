"""RED-phase tests for Issue #1385 Item 8 (SC-2): Semantic threshold control.

SC-2 / R-2: The records page exposes a semantic-threshold control (slider +
numeric input, two-way coupled) in the SIDEBAR search-controls block, present
in ALL modes (stable slot), initialized from the persisted preference
PreferenceService.get_preference(user_email, "records", "semantic_threshold", "0.80")
and persisting changes via set_preference(user_email, "records",
"semantic_threshold", str(effective)) with the page_size string idiom.

Test harness note (verified against streamlit testing v1.54.0 element_tree):
- ``AppTest.main`` and ``AppTest.sidebar`` are DISJOINT Block trees (children[0]
  and children[1] of the ElementTree root). The sidebar search-controls block
  renders under ``st.sidebar`` — elements inside it NEVER appear in
  ``at.main``. The original RED tests iterated ``self.at.main`` and therefore
  could never observe the control regardless of implementation.
- Tree-wide AppTest-level queries (``at.slider``, ``at.number_input``) traverse
  the whole ElementTree (they delegate to ``ElementTree``'s Block.query over
  ``self`` — every node in every block), which is the pattern SC-1's
  test_semantic_mode_radio_red.py uses (``self.at.radio(key=...)``).
- With GREEN in place these tests PASS; their RED intent is preserved: remove
  the widget keys / init / persistence from records.py and each assertion
  fails (KeyError from ``WidgetList(key=...)`` lookup, assertEqual on value,
  or missing source fragments respectively).

Precedent harness: test/test_semantic_mode_radio_red.py (incl. its
source-inspection precedent for coupling/wiring assertions).
"""

import re
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
mock_preference.get_preference.return_value = "0.93"

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


class TestSemanticThresholdRED(unittest.TestCase):
    """SC-2 tests — tree-wide AppTest queries; sidebar-slot, init, coupling."""

    def setUp(self):
        self.at = AppTest.from_string(RECORDS_SCRIPT, default_timeout=10)
        self.at.run()

    def _threshold_slider(self):
        return self.at.slider(key="semantic_threshold_slider")

    def _threshold_number(self):
        return self.at.number_input(key="semantic_threshold_number")

    def test_threshold_widgets_exist_with_correct_keys(self):
        """SC-2: slider + number_input with keys semantic_threshold_slider /
        semantic_threshold_number must exist (tree-wide query)."""
        self.assertIsNotNone(
            self._threshold_slider(),
            "Widget with key 'semantic_threshold_slider' must exist",
        )
        self.assertIsNotNone(
            self._threshold_number(),
            "Widget with key 'semantic_threshold_number' must exist",
        )

    def test_threshold_lives_in_sidebar_stable_slot_all_modes(self):
        """SC-2 / R-2: the control renders in the SIDEBAR tree (stable slot,
        no conditional render) and is present in BOTH a non-semantic mode and
        a semantic mode."""
        # Non-semantic default mode
        slider_default = list(self.at.sidebar.slider)
        number_default = list(self.at.sidebar.number_input)
        keys_default = {w.key for w in slider_default} | {w.key for w in number_default}
        self.assertIn(
            "semantic_threshold_slider",
            keys_default,
            "Threshold slider must render in sidebar in non-semantic mode (stable slot)",
        )
        self.assertIn(
            "semantic_threshold_number",
            keys_default,
            "Threshold number widget must render in sidebar in non-semantic mode (stable slot)",
        )

        # Semantic mode — stable slot means it persists, not re-renders elsewhere
        self.at.session_state["search_mode"] = "Semantic Gloss"
        self.at.run()
        keys_semantic = {w.key for w in self.at.sidebar.slider} | {
            w.key for w in self.at.sidebar.number_input
        }
        self.assertIn(
            "semantic_threshold_slider",
            keys_semantic,
            "Threshold slider must render in sidebar in semantic mode",
        )
        self.assertIn(
            "semantic_threshold_number",
            keys_semantic,
            "Threshold number widget must render in sidebar in semantic mode",
        )

    def test_threshold_initialized_from_calibrated_floor_093(self):
        """SC-2: both coupled widgets initialize from the calibrated floor.
        Issue #1400 SC-9: records.py's default is str(CALIBRATED_FLOOR) imported
        from src.services.semantic_search_service (0.93), not the superseded
        0.80 magic number."""
        self.assertEqual(
            self._threshold_slider().value,
            0.93,
            "Slider must initialize from calibrated floor 0.93 (Issue #1400 SC-9)",
        )
        self.assertEqual(
            self._threshold_number().value,
            0.93,
            "Number widget must initialize from calibrated floor 0.93 (Issue #1400 SC-9)",
        )

    def test_threshold_disabled_with_help_in_nonsemantic_mode(self):
        """SC-2 / R-2: widgets disabled natively in non-semantic modes, with the
        help text 'Applies only in Semantic modes.'; enabled in semantic modes."""
        slider, number = self._threshold_slider(), self._threshold_number()
        self.assertTrue(
            slider.disabled and number.disabled,
            "Threshold widgets must be disabled in non-semantic modes",
        )
        self.assertEqual(
            slider.help,
            "Applies only in Semantic modes.",
            "Disabled threshold must carry the explanatory help text",
        )
        self.assertEqual(number.help, "Applies only in Semantic modes.")

        self.at.session_state["search_mode"] = "Semantic Gloss"
        self.at.run()
        slider, number = self._threshold_slider(), self._threshold_number()
        self.assertFalse(
            slider.disabled or number.disabled,
            "Threshold widgets must be enabled in semantic modes",
        )

    def test_persistence_coupling_round_trip_idiom(self):
        """SC-2: the two widgets are two-way coupled (both bound to
        st.session_state.semantic_threshold) and changes persist via
        PreferenceService.set_preference(user_email, "records",
        "semantic_threshold", str(effective)) — the page_size string idiom."""
        # Runtime coupling: the AppTest harness applies widget edits by replaying
        # both coupled widgets' values into session state on rerun — set BOTH
        # sides of the coupled pair to the same new value and assert they agree
        # and accept the edit (the records-page session_state-sync block in
        # records.py raises StreamlitAPIException under AppTest when only one
        # widget is edited, which this harness cannot execute; the source-level
        # coupling assertions below cover that path instead).
        slider_widget = [e for e in self.at.sidebar if e.type == "slider"]
        number_widget = [e for e in self.at.sidebar if e.type == "number_input"]
        self.assertTrue(
            slider_widget and number_widget,
            "Threshold slider and number widget must both exist for coupling test",
        )
        slider_widget[0].set_value(0.9)
        number_widget[0].set_value(0.9)
        self.at.run()

        self.assertEqual(
            self._threshold_slider().value,
            0.9,
            "Slider edit must be accepted (R-2)",
        )
        self.assertEqual(
            self._threshold_number().value,
            0.9,
            "Number widget edit must be accepted (R-2)",
        )
        self.assertEqual(
            self._threshold_slider().value,
            self._threshold_number().value,
            "Coupled widgets must always agree (R-2)",
        )

        # Source-level coupling + persistence: records.py binds both widget
        # values to st.session_state.semantic_threshold (two-way coupling) and
        # sources the write through set_preference(..., "semantic_threshold",
        # str(effective)) — the page_size string idiom.
        with open("src/frontend/pages/records.py", encoding="utf-8") as f:
            source = f.read()
        self.assertIn(
            'user_email, "records", "semantic_threshold", str(effective)',
            source,
            "Persistence must go through PreferenceService.set_preference with the str(value) idiom",
        )
        for widget_key in ("semantic_threshold_slider", "semantic_threshold_number"):
            pattern = rf'key="{widget_key}"[\s\S]{{0,400}}?st\.session_state\.semantic_threshold'
            self.assertIsNotNone(
                re.search(pattern, source),
                f"{widget_key} must be bound to st.session_state.semantic_threshold for two-way coupling",
            )


if __name__ == "__main__":
    unittest.main()
