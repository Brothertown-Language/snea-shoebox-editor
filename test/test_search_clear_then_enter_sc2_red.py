# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""SC-2 (Issue #1407): after a clear (❌ button), an Enter-triggered change on
the search text_input with an empty value must NOT re-commit stale search
terms — the empty state persists (search_query stays empty, current_page
resets to 1, no spurious re-search).

Sequence under test (mirrors the user gesture):
1. Run the Records page.
2. Type a search term via the text_input (on_change commits search_query).
3. Click the ❌ clear button (search_clear) — _clear_search is consumed on the
   next run, search_query resets to "", and _search_input_key increments so
   the text_input is re-created under a NEW suffixed key.
4. Trigger a change on the (re-created) text_input ending in an empty value —
   the on_change callback must read the CURRENT suffixed key (holding "") and
   commit "", never the stale term from the pre-clear widget state.

Regression slice: pre-fix, on_search_change read a stale/un-suffixed key, so a
post-clear Enter could resurrect stale search terms. SC-1's GREEN (commit
fe129df) fixed the dynamic suffix read; if this test passes immediately, it
stands as the SC-2 regression slice (ALREADY_GREEN, reported honestly).

Harness precedent: test_search_wiring_sc1_red.py (AppTest + mocked service
modules via sys.modules insert-only containment).

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
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


def _clear_button(at):
    buttons = [b for b in at.button if b.key == "search_clear"]
    if not buttons:
        buttons = [b for b in at.sidebar.button if b.key == "search_clear"]
    return buttons[0] if buttons else None


class TestSearchClearThenEnterSC2(unittest.TestCase):
    """SC-2: empty state persists after clear-then-Enter — no stale re-search."""

    def test_clear_then_empty_enter_persists_empty_state(self):
        """After a search, ❌ clear, and an Enter-change with an empty value,
        search_query must stay empty (no stale-term re-commit) and
        current_page must reset to 1."""
        at = AppTest.from_string(SEARCH_SCRIPT, default_timeout=30)
        at.session_state["search_query"] = ""
        at.session_state["semantic_threshold"] = 0.8
        at.session_state["page_size"] = 25
        at.run()
        self.assertEqual(len(at.exception), 0, f"Page raised: {at.exception}")

        # Step 1: perform a search — the widget change commits "water".
        widget = _search_text_input(at)
        self.assertIsNotNone(
            widget, "Search text_input ('Search terms...') must render in sidebar"
        )
        widget.set_value("water").run()
        self.assertEqual(len(at.exception), 0, f"Search run raised: {at.exception}")
        self.assertEqual(
            _session_get(at, "search_query"),
            "water",
            "Precondition failed: the search term must be committed before the "
            "clear step",
        )

        # Step 2: click the ❌ clear button.
        clear_btn = _clear_button(at)
        self.assertIsNotNone(clear_btn, "❌ clear button (key=search_clear) must render")
        clear_btn.click().run()
        self.assertEqual(len(at.exception), 0, f"Clear run raised: {at.exception}")
        self.assertEqual(
            _session_get(at, "search_query"),
            "",
            "Precondition failed: ❌ clear must reset search_query to empty",
        )
        self.assertEqual(
            _session_get(at, "current_page"),
            1,
            "❌ clear must reset current_page to 1",
        )

        # Step 3: trigger a change on the (re-created, new suffixed key)
        # text_input ending in an empty value — the Enter-on-empty gesture.
        # AppTest fires on_change only on a value transition, so go through a
        # one-character detour and land on "": the FINAL change event carries
        # the empty value, exactly as deleting all text and pressing Enter.
        widget = _search_text_input(at)
        self.assertIsNotNone(
            widget, "Search text_input must re-render after the clear rerun"
        )
        pre_clear_key_value = _session_get(at, "_search_input_key")
        widget.set_value("x").run()
        self.assertEqual(len(at.exception), 0, f"Detour run raised: {at.exception}")
        self.assertEqual(
            _session_get(at, "search_query"),
            "x",
            "Precondition failed: post-clear change must read the CURRENT "
            "suffixed key (detour commit expected)",
        )
        self.assertEqual(
            _session_get(at, "_search_input_key"),
            pre_clear_key_value,
            "No new clear must have occurred during the detour",
        )
        widget.set_value("").run()
        self.assertEqual(len(at.exception), 0, f"Empty-Enter run raised: {at.exception}")

        # SC-2 assertions: empty state persists — no spurious re-search with
        # stale terms ("water" must NOT be resurrected from the pre-clear
        # widget state).
        self.assertEqual(
            _session_get(at, "search_query"),
            "",
            "After clear-then-Enter-on-empty, search_query must stay empty — "
            "a stale-term re-commit leaked through (got "
            f"{_session_get(at, 'search_query')!r})",
        )
        self.assertEqual(
            _session_get(at, "current_page"),
            1,
            "The empty-value Enter change must reset current_page to 1",
        )

    def test_clear_then_empty_enter_does_not_resurrect_original_term(self):
        """The stale-term resurrection guard: after clear + empty Enter, the
        ORIGINAL search term must never reappear in search_query — this is the
        spurious-re-search failure signature of a stale-key callback read."""
        at = AppTest.from_string(SEARCH_SCRIPT, default_timeout=30)
        at.session_state["search_query"] = ""
        at.session_state["semantic_threshold"] = 0.8
        at.session_state["page_size"] = 25
        at.run()
        self.assertEqual(len(at.exception), 0, f"Page raised: {at.exception}")

        widget = _search_text_input(at)
        self.assertIsNotNone(widget, "Search text_input must render in sidebar")
        widget.set_value("k8é").run()  # Unicode IPA term — must pass through unaltered
        self.assertEqual(_session_get(at, "search_query"), "k8é")

        clear_btn = _clear_button(at)
        self.assertIsNotNone(clear_btn, "❌ clear button must render")
        clear_btn.click().run()
        self.assertEqual(_session_get(at, "search_query"), "")

        widget = _search_text_input(at)
        self.assertIsNotNone(widget, "Search text_input must re-render after clear")
        widget.set_value("z").run()
        widget.set_value("").run()
        self.assertEqual(len(at.exception), 0, f"Empty-Enter run raised: {at.exception}")

        committed = _session_get(at, "search_query")
        self.assertNotEqual(
            committed,
            "k8é",
            "Stale-term resurrection: the pre-clear search term leaked back "
            "into search_query after clear-then-Enter-on-empty",
        )
        self.assertEqual(
            committed,
            "",
            "After clear-then-Enter-on-empty, search_query must be empty",
        )


if __name__ == "__main__":
    unittest.main()
