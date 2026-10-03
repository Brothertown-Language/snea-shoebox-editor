# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""RED-phase tests for SC-1 (Issue #1407): the Records sidebar search
text_input must carry on_change wiring that commits st.session_state.search_query
and resets current_page to 1 when the user edits the query.

Current defect (verified): src/frontend/pages/records.py text_input has NO
on_change callback; the on_search_change handler (records.py on_search_change)
is dead code reading the stale un-suffixed key 'search_query_input' while the
widget key is suffixed search_query_input_{_search_input_key}. These tests
MUST FAIL pre-fix on the wiring absence / stale-key behavior.

Harness precedent: test_semantic_scores_red.py (AppTest + mocked service
modules via sys.modules insert-only containment).

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""
import unittest

from streamlit.testing.v1 import AppTest

SEARCH_WIRING_TEMPLATE = """import sys
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
    mock_linguistic = MagicMock()
    # Enough records/pages that the total_pages clamp (records.py
    # `current_page > total_pages` guard) does NOT mask the on_change reset.
    _recs = [
        {"id": i, "is_locked": False, "source_name": "S", "mdf_data": "", "languages": []}
        for i in range(100)
    ]
    mock_linguistic.search_records.return_value = MagicMock(
        records=_recs, total_count=100
    )
    _exact_rec = _recs[0]
    mock_linguistic.get_sources_with_counts.return_value = []
    mock_linguistic.get_languages.return_value = []
    mock_linguistic.get_all_records_for_export.return_value = []
    mock_linguistic.get_edit_history.return_value = []
    mock_linguistic.bundle_records_to_mdf = MagicMock(return_value="")
    mock_linguistic.stream_records_to_temp_file.return_value = "/tmp/test"
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

SEARCH_SCRIPT = SEARCH_WIRING_TEMPLATE


def _session_get(at, key):
    """AppTest session_state supports __getitem__/__contains__, not .get()."""
    try:
        return at.session_state[key]
    except (KeyError, AttributeError):
        return None


def _search_text_input(at):
    """Locate the sidebar search text_input by its label."""
    inputs = [ti for ti in at.text_input if ti.label == "Search terms..."]
    if not inputs:
        inputs = [ti for ti in at.sidebar.text_input if ti.label == "Search terms..."]
    return inputs[0] if inputs else None


class TestSearchWiringRED(unittest.TestCase):
    """RED-phase SC-1 tests — all MUST FAIL against current code."""

    def test_text_input_change_commits_search_query(self):
        """SC-1: editing the search text_input must trigger on_change and
        commit the typed value into st.session_state.search_query."""
        at = AppTest.from_string(SEARCH_SCRIPT, default_timeout=30)
        at.session_state["search_query"] = ""
        at.run()
        self.assertEqual(len(at.exception), 0, f"Page raised: {at.exception}")

        widget = _search_text_input(at)
        self.assertIsNotNone(
            widget, "Search text_input ('Search terms...') must render in sidebar"
        )
        widget.set_value("water").run()
        self.assertEqual(len(at.exception), 0, f"Change run raised: {at.exception}")

        committed = _session_get(at, "search_query")
        self.assertEqual(
            committed,
            "water",
            "Editing the search input must commit "
            "st.session_state.search_query via on_change "
            f"(got {committed!r} — no on_change wiring / stale-key handler)",
        )

    def test_text_input_change_resets_current_page_to_one(self):
        """SC-1: a search edit must reset current_page to 1 (results page
        restarts for the new query)."""
        at = AppTest.from_string(SEARCH_SCRIPT, default_timeout=30)
        at.session_state["search_query"] = ""
        at.session_state["current_page"] = 3
        at.run()
        self.assertEqual(len(at.exception), 0, f"Page raised: {at.exception}")

        widget = _search_text_input(at)
        self.assertIsNotNone(
            widget, "Search text_input ('Search terms...') must render in sidebar"
        )
        widget.set_value("water").run()
        self.assertEqual(len(at.exception), 0, f"Change run raised: {at.exception}")

        page = _session_get(at, "current_page")
        self.assertEqual(
            page,
            1,
            "A search edit must reset current_page to 1 "
            f"(got {page!r} — no on_change wiring on the text_input)",
        )


if __name__ == "__main__":
    unittest.main()
