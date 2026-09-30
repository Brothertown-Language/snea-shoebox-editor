"""RED-phase tests for Issue #1385 Item 3 (SC-3): invalid threshold edit rejected.

SC-3 / R-3: The records page rejects a non-numeric or out-of-range threshold
edit and snaps the widget back to the last accepted value; the persisted
preference (PreferenceService `records`/`semantic_threshold`) stays unchanged.

Harness precedent: test/test_semantic_threshold_red.py — the same
RECORDS_SCRIPT AppTree setup, mock services, tree-wide / sidebar queries.
The AppTest number_input cannot express a truly non-numeric or out-of-range
entry (the widget coerces/clamps), so the harness injects an invalid value
into the backing key `st.session_state.semantic_threshold` (a plain,
non-widget session_state entry — safe to write directly) and reruns the page.
With the SC-3 GREEN guard in place the guard must restore the backing key
(and via the pre-instantiation sync block both coupled widget keys) to the
last accepted value and MUST NOT call set_preference with the invalid value.
Without the guard (current state, no validation exists in records.py) the
backing key keeps the invalid value / the page crashes — every assertion
below FAILs, which is the RED terminal state.

Precedent also carries the source-inspection pattern (used here to assert a
validation guard exists in the threshold edit path).
"""

import unittest
from unittest.mock import MagicMock

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
mock_preference.get_preference.return_value = "0.80"

mock_identity = MagicMock()
mock_identity.get_github_username.return_value = "tester"

mock_nav = MagicMock()
mock_nav.PAGE_DIRECT_ENTRY = "/direct_entry"

mock_upload = MagicMock()
mock_upload.generate_mdf_filename.return_value = "test.mdf"

mock_validator = MagicMock()
mock_validator.diagnose_record.return_value = None

import sys

_MOCK_MODULE_PATHS = [
    "src.services.linguistic_service",
    "src.services.preference_service",
    "src.services.identity_service",
    "src.services.navigation_service",
    "src.services.upload_service",
    "src.mdf.validator",
]
_preference_calls = []
_saved_modules = {p: sys.modules.get(p) for p in _MOCK_MODULE_PATHS}
try:
    def _spy_set_preference(user, view, key, value):
        _preference_calls.append((view, key, value))

    _mock_pref_module = MagicMock()
    _mock_pref_module.PreferenceService.get_preference = MagicMock(return_value="0.80")
    _mock_pref_module.PreferenceService.set_preference = _spy_set_preference
    sys.modules["src.services.preference_service"] = _mock_pref_module

    sys.modules["src.services.linguistic_service"] = MagicMock()
    sys.modules["src.services.linguistic_service"].LinguisticService = mock_linguistic
    sys.modules["src.services.identity_service"] = MagicMock()
    sys.modules["src.services.identity_service"].IdentityService = mock_identity
    sys.modules["src.services.navigation_service"] = MagicMock()
    sys.modules["src.services.navigation_service"].NavigationService = mock_nav
    sys.modules["src.services.upload_service"] = MagicMock()
    sys.modules["src.services.upload_service"].UploadService = mock_upload
    sys.modules["src.mdf.validator"] = MagicMock()
    sys.modules["src.mdf.validator"].MDFValidator = mock_validator
    st.session_state["_test_preference_calls"] = _preference_calls

    from src.frontend.pages.records import records
    records()
finally:
    for _path, _saved in _saved_modules.items():
        if _saved is not None:
            sys.modules[_path] = _saved
        else:
            del sys.modules[_path]
"""


class TestSemanticThresholdValidationRED(unittest.TestCase):
    """SC-3 — invalid threshold edits rejected; snap-back; preference unchanged."""

    def setUp(self):
        self.at = AppTest.from_string(RECORDS_SCRIPT, default_timeout=15)
        self.at.run()

    def _threshold_slider(self):
        return self.at.slider(key="semantic_threshold_slider")

    def _threshold_number(self):
        return self.at.number_input(key="semantic_threshold_number")

    def _accept_valid_edit(self, value):
        """Establish a last-accepted value via a valid edit on the coupled pair."""
        self.at.session_state["semantic_threshold"] = value
        self.at.session_state["semantic_threshold_slider"] = value
        self.at.session_state["semantic_threshold_number"] = value
        self.at.run()
        self.assertEqual(
            self._threshold_slider().value,
            value,
            "valid baseline edit must be accepted before invalid-edit scenario",
        )

    def _preference_calls(self):
        return self.at.session_state["_test_preference_calls"]

    def test_out_of_range_high_edit_rejected_and_snaps_back(self):
        """SC-3: backing key set to 1.5 (>1.0) then rerun → widgets and backing
        key snap back to the last accepted value; preference unchanged."""
        self._accept_valid_edit(0.85)
        self.at.session_state["semantic_threshold"] = 1.5
        self.at.run()
        self.assertEqual(
            self.at.session_state["semantic_threshold"],
            0.85,
            "out-of-range (>1.0) edit must be rejected; backing key must snap back to last accepted value",
        )
        self.assertEqual(
            self._threshold_number().value,
            0.85,
            "widget must snap back to last accepted value after out-of-range edit",
        )
        self.assertEqual(
            self._threshold_slider().value,
            0.85,
            "slider must snap back to last accepted value after out-of-range edit",
        )
        self.assertFalse(
            any(c == ("records", "semantic_threshold", "1.5") for c in self._preference_calls()),
            "preference must remain unchanged after out-of-range edit",
        )

    def test_out_of_range_low_edit_rejected_and_snaps_back(self):
        """SC-3: backing key set to -0.2 (<0.0) then rerun → snap back to the
        last accepted value; preference unchanged."""
        self._accept_valid_edit(0.7)
        self.at.session_state["semantic_threshold"] = -0.2
        self.at.run()
        self.assertEqual(
            self.at.session_state["semantic_threshold"],
            0.7,
            "out-of-range (<0.0) edit must be rejected; backing key must snap back",
        )
        self.assertEqual(self._threshold_number().value, 0.7)
        self.assertFalse(
            any(c == ("records", "semantic_threshold", "-0.2") for c in self._preference_calls()),
            "preference must remain unchanged after out-of-range edit",
        )

    def test_non_numeric_edit_rejected_and_snaps_back(self):
        """SC-3: backing key set to the non-numeric string '0.seven' then rerun
        → backing key and widgets snap back to the last accepted value; the
        page must not crash and must not persist the non-numeric value."""
        self._accept_valid_edit(0.9)
        self.at.session_state["semantic_threshold"] = "0.seven"
        self.at.run()
        self.assertFalse(
            self.at.exception,
            "invalid threshold edit must be handled by a validation guard, not crash the page",
        )
        self.assertEqual(
            self.at.session_state["semantic_threshold"],
            0.9,
            "non-numeric edit must be rejected; backing key must snap back to last accepted value",
        )
        self.assertEqual(self._threshold_number().value, 0.9)
        self.assertFalse(
            any(c == ("records", "semantic_threshold", "0.seven") for c in self._preference_calls()),
            "non-numeric value must never be persisted",
        )

    def test_validation_guard_exists_in_threshold_edit_path(self):
        """SC-3: a range/numeric validation guard exists between the raw edit
        capture and the acceptance/persist step (rejects <0.0 and >1.0 and
        non-numeric values, restoring the last accepted value)."""
        with open("src/frontend/pages/records.py", encoding="utf-8") as f:
            source = f.read()
        import re

        guard = re.search(r"_THRESHOLD_MIN|_validate_threshold|reject[_.a-z]*invalid", source)
        self.assertIsNotNone(
            guard,
            "a named threshold validation guard (non-numeric + range rejection / snap-back) must exist in records.py",
        )
        persist_index = source.index('set_preference(user_email, "records", "semantic_threshold"')
        guard_index = guard.start()
        self.assertLess(
            guard_index,
            persist_index,
            "validation guard must run before the set_preference persistence step",
        )


if __name__ == "__main__":
    unittest.main()