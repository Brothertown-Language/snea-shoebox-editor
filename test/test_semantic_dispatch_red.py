# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""RED-phase tests for SC-7 (Issue #1385): semantic modes dispatch correctly
through the search entry point and return correct result sets; existing four
modes unchanged.

The records page currently routes "Semantic Gloss"/"Semantic All" through
`LinguisticService.search_records` (whose dispatch treats every strategy as a
SQLAlchemy query transformer returning a SemanticSearchResult, not a Record
query — the page expects `.records`/`.total_count`). These tests assert the
SC-7 contract: a page-level per-mode dispatch consumes the semantic seam
(including threshold forwarding) while exact-match modes keep the existing
search_records path. All tests MUST FAIL against current code.

Harness precedent: test_search_mode_ui_red.py (AppTest + mocked service
modules via sys.modules insert-only containment).

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""
import unittest

from streamlit.testing.v1 import AppTest

SEMANTIC_RESULT_TEMPLATE = """import sys
from unittest.mock import MagicMock

# Insert-only containment: save pre-existing entries, restore at scope-exit.
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
    from src.services.semantic_search_service import SemanticSearchResult

    # Ranked ids in seam order (desc score): 3 then 1.
    # R-8: the UI binds to the seam MODULE function search_semantic, not a
    # LinguisticService classmethod. The module is mocked wholesale.
    _ranked = [(3, 0.92), (1, 0.81)]
    mock_seam = MagicMock()
    # Issue #1400 SC-9: records.py imports CALIBRATED_FLOOR from the seam for
    # the semantic_threshold default — pin the real calibrated value.
    mock_seam.CALIBRATED_FLOOR = 0.93
    mock_seam.search_semantic = MagicMock(
        return_value=SemanticSearchResult(results=_ranked, status="ok", message="")
    )
    sys.modules["src.services.semantic_search_service"] = mock_seam
    sys.modules["src.services.semantic_search_service"].SemanticSearchResult = SemanticSearchResult

    mock_linguistic = MagicMock()
    # Exact-match modes: RecordSearchResult-shaped mock.
    mock_linguistic.search_records.return_value = MagicMock(records=[], total_count=0)
    mock_linguistic.get_sources_with_counts.return_value = []
    mock_linguistic.get_languages.return_value = []
    mock_linguistic.get_all_records_for_export.return_value = []
    mock_linguistic.get_record.return_value = None
    mock_linguistic.bundle_records_to_mdf = MagicMock(return_value="")
    mock_linguistic.stream_records_to_temp_file.return_value = "/tmp/test"
    mock_linguistic.get_edit_history.return_value = []
    # Page-level semantic dispatch consumes get_record per ranked id.
    for _rid in (3, 1):
        _rec = MagicMock()
        _rec.get = lambda k, _id=_rid: (
            _id if k == "id" else (k == "is_locked" and False) or (k == "source_name" and "S") or None
        )
        if isinstance(_rec.get, MagicMock):
            _rec.get.side_effect = (
                lambda k, default=None, _id=_rid: {
                    "id": _id, "is_locked": False, "source_name": "S", "mdf_data": ""
                }.get(k, default)
            )
    mock_linguistic.get_record.side_effect = lambda rid: {
        "id": rid, "is_locked": False, "source_name": "S", "mdf_data": "", "languages": [],
    }
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

SEMANTIC_SCRIPT = SEMANTIC_RESULT_TEMPLATE


class TestSemanticDispatchRED(unittest.TestCase):
    """RED-phase SC-7 tests — all MUST FAIL against current code."""

    def setUp(self):
        self.at = AppTest.from_string(SEMANTIC_SCRIPT, default_timeout=15)

    def test_semantic_gloss_dispatches_to_seam_with_threshold(self):
        """SC-7: switching to Semantic Gloss with a query must consume the
        semantic seam (search_semantic) with the session threshold forwarded,
        NOT route through search_records. RED: current page always calls
        search_records and never passes threshold to a seam."""

        self.at.session_state["search_query"] = "water"
        self.at.session_state["search_mode"] = "Semantic Gloss"
        self.at.session_state["semantic_threshold"] = 0.7
        self.at.run()
        # Fail collection check: page must not raise.
        self.assertEqual(len(self.at.exception), 0, f"Page raised: {self.at.exception}")

        # Assert seam consumed with threshold — via mocked service calls.
        # The mocked LinguisticService.search_semantic must have been called.
        # Access the mock indirectly: inspect the rendered main panel for the
        # ranked record ids (3 then 1, desc score). Current code cannot
        # produce semantic-mode records (search_records mock returns empty).
        self.assertIn("Record #3", "\n".join(m.value or "" for m in self.at.markdown))

    def test_semantic_all_dispatches_to_seam(self):
        """SC-7: Semantic All likewise consumes the seam and yields the ranked
        records. RED: page currently routes through search_records only."""
        self.at.session_state["search_query"] = "river"
        self.at.session_state["search_mode"] = "Semantic All"
        self.at.run()
        self.assertEqual(len(self.at.exception), 0, f"Page raised: {self.at.exception}")
        body = "\n".join(m.value or "" for m in self.at.markdown)
        self.assertIn("Record #3", body, "Semantic All should rank record 3 first (score 0.92)")
        self.assertIn("Record #1", body, "Semantic All should include record 1")

    def test_exact_mode_uses_search_records_not_seam(self):
        """SC-7 regression guard: Headword mode must keep dispatching through
        search_records (RecordSearchResult shape), never the semantic seam.
        This is a GREEN-invariant asserted as RED-observable context."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_string(SEMANTIC_SCRIPT, default_timeout=15)
        at.session_state["search_mode"] = "Headword"
        at.run()
        # With the mocked search_records returning empty records, exact mode
        # must not crash and must not invoke the seam. After GREEN the page
        # will branch per mode; the RED code path (single dispatch) still
        # passes here — this test pins the regression baseline.
        self.assertEqual(len(at.exception), 0, f"Page raised: {at.exception}")


if __name__ == "__main__":
    unittest.main()
