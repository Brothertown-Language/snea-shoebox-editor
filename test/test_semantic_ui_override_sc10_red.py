# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Issue #1400 SC-10 RED — UI threshold override preserved through to the seam.

SC-10 (spec .issues/1400/spec.md): "A user override in the UI threshold
control is preserved (override value is used by the seam, not silently
replaced by the default)."

These AppTest-tier tests assert service-call wiring (sanctioned AppTest use
per docs/development/ui_testing_standard.md §"AppTest — remaining sanctioned
uses"): the override value st.session_state.semantic_threshold must flow to
the search_semantic() seam call unchanged, and the _validate_threshold guard
must reject non-numeric / out-of-range edits WITHOUT replacing the accepted
override with the default floor.

The seam mock records every `threshold=` kwarg it receives into
tmp/1400/artifacts/sc10-captured-thresholds.jsonl so the tests can observe
the UI → seam boundary value directly.

Harness precedent: test_semantic_dispatch_red.py (AppTest + mocked service
modules via sys.modules insert-only containment).

Co-authored with AI: OpenCode (zai-org/GLM-5.3-Flash)
"""
import json
import os
import unittest

CAPTURE_PATH = os.path.join("tmp", "1400", "artifacts", "sc10-captured-thresholds.jsonl")

OVERRIDE_VALUE = 0.55  # differs from CALIBRATED_FLOOR = 0.93

_SCRIPT_BODY = r"""__CAPTURE_PATH__ = None  # replaced below
import json, os, sys
from unittest.mock import MagicMock

from src.services.semantic_search_service import SemanticSearchResult

_MOCK_MODULE_PATHS = [
    "src.services.linguistic_service",
    "src.services.semantic_search_service",
    "src.services.preference_service",
    "src.services.identity_service",
    "src.services.navigation_service",
    "src.services.upload_service",
    "src.mdf.validator",
]
_saved_modules = {p: sys.modules.get(p) for p in _MOCK_MODULE_PATHS}
try:
    _ranked = [(3, 0.99), (1, 0.81)]
    _CAPTURE_PATH = __CAPTURE_PATH__

    def _recording_seam(**kwargs):
        os.makedirs(os.path.dirname(_CAPTURE_PATH), exist_ok=True)
        with open(_CAPTURE_PATH, "a") as fh:
            fh.write(json.dumps({"threshold": kwargs.get("threshold")}) + "\n")
        return SemanticSearchResult(results=_ranked, status="ok", message="")

    mock_seam = MagicMock()
    mock_seam.CALIBRATED_FLOOR = 0.93
    mock_seam.search_semantic = _recording_seam
    sys.modules["src.services.semantic_search_service"] = mock_seam
    sys.modules["src.services.semantic_search_service"].SemanticSearchResult = SemanticSearchResult

    mock_linguistic = MagicMock()
    mock_linguistic.search_records.return_value = MagicMock(records=[], total_count=0)
    mock_linguistic.get_sources_with_counts.return_value = []
    mock_linguistic.get_languages.return_value = []
    mock_linguistic.get_all_records_for_export.return_value = []
    mock_linguistic.bundle_records_to_mdf = MagicMock(return_value="")
    mock_linguistic.stream_records_to_temp_file.return_value = "/tmp/test"
    mock_linguistic.get_edit_history.return_value = []
    mock_linguistic.get_record.side_effect = lambda rid: {
        "id": rid, "is_locked": False, "source_name": "S", "mdf_data": "", "languages": [],
    }

    mock_preference = MagicMock()
    mock_preference.get_preference.side_effect = lambda _u, _page, key, default=None: {
        "page_size": "25",
        "structural_highlighting": "True",
        "semantic_threshold": "0.93",
    }.get(key, default)
    mock_preference.set_preference.return_value = None

    mock_identity = MagicMock()
    mock_identity.get_github_username.return_value = "tester"

    mock_nav = MagicMock()
    mock_nav.PAGE_DIRECT_ENTRY = "/direct_entry"

    mock_upload = MagicMock()
    mock_upload.generate_mdf_filename.return_value = "test.mdf"

    mock_validator = MagicMock()
    mock_validator.diagnose_record.return_value = None

    sys.modules["src.services.linguistic_service"] = MagicMock()
    sys.modules["src.services.linguistic_service"].LinguisticService = mock_linguistic
    sys.modules["src.services.linguistic_service"].SearchMode = str
    sys.modules["src.services.linguistic_service"].RecordSearchResult = MagicMock
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

SCRIPT_TEMPLATE = _SCRIPT_BODY.replace(
    "_CAPTURE_PATH = __CAPTURE_PATH__", "_CAPTURE_PATH = %r" % CAPTURE_PATH
)


def _read_captured_thresholds():
    if not os.path.exists(CAPTURE_PATH):
        return []
    with open(CAPTURE_PATH) as fh:
        return [json.loads(line)["threshold"] for line in fh if line.strip()]


class TestSemanticUIOverrideSC10(unittest.TestCase):
    """SC-10: UI override reaches the seam unchanged; guard never replaces it."""

    def setUp(self):
        os.makedirs(os.path.dirname(CAPTURE_PATH), exist_ok=True)
        if os.path.exists(CAPTURE_PATH):
            os.remove(CAPTURE_PATH)

    def test_user_override_reaches_seam_unchanged(self):
        """A session override (0.55 ≠ default 0.93) is forwarded verbatim to
        search_semantic(threshold=...) — never silently replaced by the
        calibrated default."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_string(SCRIPT_TEMPLATE, default_timeout=30)
        at.session_state["user_email"] = "tester@example.com"
        at.session_state["search_query"] = "water"
        at.session_state["search_mode"] = "Semantic Gloss"
        at.session_state["semantic_threshold"] = OVERRIDE_VALUE
        at.run()
        self.assertEqual(
            len(at.exception), 0, f"Page raised exceptions: {at.exception}"
        )
        captured = _read_captured_thresholds()
        self.assertTrue(captured, "seam was never invoked — no threshold observed")
        self.assertEqual(
            captured,
            [OVERRIDE_VALUE],
            f"SC-10 VIOLATION: seam received {captured!r} instead of the "
            f"user override {OVERRIDE_VALUE!r} — override silently replaced "
            f"by the default floor",
        )

    def test_guard_rejects_out_of_range_edit_without_replacing_override(self):
        """An out-of-range edit (5.0) is rejected by _validate_threshold: the
        backing value is restored to the last accepted OVERRIDE (0.55), not
        the calibrated default (0.93), and the seam still receives 0.55."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_string(SCRIPT_TEMPLATE, default_timeout=30)
        at.session_state["user_email"] = "tester@example.com"
        at.session_state["search_query"] = "water"
        at.session_state["search_mode"] = "Semantic Gloss"
        at.session_state["semantic_threshold"] = OVERRIDE_VALUE
        at.run()  # first run: accepted override recorded
        captured_first = _read_captured_thresholds()
        self.assertEqual(captured_first, [OVERRIDE_VALUE])

        # Simulate an out-of-range edit landing in the backing value.
        # A changed query forces a fresh seam call (the rank-once cache would
        # otherwise skip re-invocation for an identical digest).
        at.session_state["semantic_threshold"] = 5.0
        at.session_state["search_query"] = "money"
        at.run()
        self.assertEqual(
            len(at.exception), 0, f"Page raised exceptions: {at.exception}"
        )
        restored = at.session_state["semantic_threshold"]
        self.assertEqual(
            restored,
            OVERRIDE_VALUE,
            f"SC-10 VIOLATION: guard replaced the accepted override with "
            f"{restored!r} (expected the override {OVERRIDE_VALUE!r} to "
            f"survive; the default must not silently replace it)",
        )
        captured = _read_captured_thresholds()
        self.assertEqual(
            captured,
            [OVERRIDE_VALUE, OVERRIDE_VALUE],
            f"SC-10 VIOLATION: seam captured {captured!r} — the invalid edit "
            f"must not reach the seam and must not displace the override",
        )

    def test_guard_rejects_non_numeric_edit_without_replacing_override(self):
        """A non-numeric edit ("abc") is rejected: the override survives."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_string(SCRIPT_TEMPLATE, default_timeout=30)
        at.session_state["user_email"] = "tester@example.com"
        at.session_state["search_query"] = "water"
        at.session_state["search_mode"] = "Semantic Gloss"
        at.session_state["semantic_threshold"] = OVERRIDE_VALUE
        at.run()

        at.session_state["semantic_threshold"] = "abc"
        at.session_state["search_query"] = "money"
        at.run()
        self.assertEqual(
            len(at.exception), 0, f"Page raised exceptions: {at.exception}"
        )
        restored = at.session_state["semantic_threshold"]
        self.assertEqual(
            restored,
            OVERRIDE_VALUE,
            f"SC-10 VIOLATION: non-numeric edit displaced the override to "
            f"{restored!r} instead of restoring the accepted override",
        )
        captured = _read_captured_thresholds()
        self.assertEqual(
            captured,
            [OVERRIDE_VALUE, OVERRIDE_VALUE],
            f"SC-10 VIOLATION: seam captured {captured!r} after a "
            f"non-numeric edit",
        )


if __name__ == "__main__":
    unittest.main()
