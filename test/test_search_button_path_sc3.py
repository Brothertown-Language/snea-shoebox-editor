# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""SC-3 (Issue #1407): the 🔍 search-trigger button still executes the search
exactly once — no double-commit — now that on_change is attached to the search
text_input.

Pinned behavior (per the research note: Streamlit widget callbacks run BEFORE
the script body, so on a 🔍 click both the pending on_change (if the widget
value changed since last run) and the button body may write search_query —
but they write the SAME widget value, so the commit is idempotent):

1. Click 🔍 (key=search_trigger) commits search_query from the CURRENT
   suffixed widget key value (search_query_input_<n>), overwriting any stale
   backing value.
2. current_page is reset to 1.
3. Via a counting session_state wrapper (SC-3 counter instrument): exactly one
   commit write to search_query per 🔍 click — even with on_change attached,
   the writes are idempotent and never desynchronize from the widget value.

This is a REGRESSION GUARD: it is expected to pass BEFORE and AFTER the SC-3
change (guard existence is the deliverable). If it passes immediately, that is
reported honestly as ALREADY_GREEN.

Harness precedent: test_search_clear_then_enter_sc2_red.py (AppTest + mocked
service modules via sys.modules insert-only containment).

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""
import unittest

from streamlit.testing.v1 import AppTest

# The commit counter is installed INSIDE the AppTest script by patching
# streamlit's SessionState.__setitem__/__setattr__ — the actual commit point
# for both item-style and attribute-style session_state writes. The patch is
# applied once per class (guarded) so the count accumulates across script
# runs, and each counted write mirrors the running total into the real
# session state under _sc3_search_writes so the outer test can read it.
COUNTER_WRAPPER = '''
import streamlit as st
from streamlit.runtime.state.session_state import SessionState

if not getattr(SessionState, "_sc3_patched", False):
    _sc3_orig_setitem = SessionState.__setitem__
    _sc3_orig_setattr = SessionState.__setattr__

    def _sc3_bump(state):
        counts = getattr(state, "_sc3_counts", None)
        if counts is None:
            counts = {"n": 0}
            _sc3_orig_setattr(state, "_sc3_counts", counts)
        counts["n"] += 1
        _sc3_orig_setitem(state, "_sc3_search_writes", counts["n"])

    def _sc3_counting_setitem(self, key, value):
        if key == "search_query":
            _sc3_bump(self)
        return _sc3_orig_setitem(self, key, value)

    def _sc3_counting_setattr(self, name, value):
        if name == "search_query":
            _sc3_bump(self)
        return _sc3_orig_setattr(self, name, value)

    SessionState.__setitem__ = _sc3_counting_setitem
    SessionState.__setattr__ = _sc3_counting_setattr
    SessionState._sc3_patched = True
'''

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
""" + COUNTER_WRAPPER + """
try:
    mock_linguistic = MagicMock()
    # Enough records/pages that the total_pages clamp (records.py
    # `current_page > total_pages` guard) does NOT mask the reset assertions.
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


def _search_trigger_button(at):
    buttons = [b for b in at.button if b.key == "search_trigger"]
    if not buttons:
        buttons = [b for b in at.sidebar.button if b.key == "search_trigger"]
    return buttons[0] if buttons else None


class TestSearchButtonPathSC3(unittest.TestCase):
    """SC-3: 🔍 click → one commit of the widget value, current_page → 1."""

    def test_search_button_commits_widget_value_and_resets_page(self):
        """Clicking 🔍 commits search_query from the current suffixed widget
        key (overwriting any stale backing value) and resets current_page."""
        at = AppTest.from_string(SEARCH_SCRIPT, default_timeout=30)
        at.session_state["search_query"] = ""
        at.session_state["semantic_threshold"] = 0.8
        at.session_state["page_size"] = 25
        at.run()
        self.assertEqual(len(at.exception), 0, f"Page raised: {at.exception}")

        # Establish a widget value through the on_change path first, so the
        # suffixed widget key holds "water" in session state.
        widget = _search_text_input(at)
        self.assertIsNotNone(
            widget, "Search text_input ('Search terms...') must render in sidebar"
        )
        widget.set_value("water").run()
        self.assertEqual(len(at.exception), 0, f"Search run raised: {at.exception}")
        self.assertEqual(
            _session_get(at, "search_query"),
            "water",
            "Precondition failed: on_change must commit the widget value before "
            "the 🔍 click step",
        )
        writes_after_change = _session_get(at, "_sc3_search_writes")
        self.assertIsNotNone(
            writes_after_change,
            "Counter wrapper must be active (search_query was written via "
            "on_change yet no write was counted)",
        )

        # Simulate drifted backing state: a stale search_query and a
        # non-first page. The 🔍 click must overwrite both.
        at.session_state["search_query"] = "STALE_SENTINEL"
        at.session_state["current_page"] = 3

        trigger = _search_trigger_button(at)
        self.assertIsNotNone(trigger, "🔍 button (key=search_trigger) must render")
        trigger.click().run()
        self.assertEqual(len(at.exception), 0, f"🔍 click run raised: {at.exception}")

        # SC-3 assertion 1: search_query is the WIDGET value, not the stale
        # backing value.
        self.assertEqual(
            _session_get(at, "search_query"),
            "water",
            "🔍 must commit the current widget-key value; got stale backing "
            f"value {_session_get(at, 'search_query')!r}",
        )
        # SC-3 assertion 2: current_page reset to 1.
        self.assertEqual(
            _session_get(at, "current_page"),
            1,
            "🔍 must reset current_page to 1",
        )

    def test_search_button_exactly_one_commit_per_click(self):
        """Counter-wrapper instrument: exactly ONE write to search_query per
        🔍 click, even with on_change attached (idempotent same-value writes
        are acceptable; the count per click must be 1)."""
        at = AppTest.from_string(SEARCH_SCRIPT, default_timeout=30)
        at.session_state["search_query"] = ""
        at.session_state["semantic_threshold"] = 0.8
        at.session_state["page_size"] = 25
        at.run()
        self.assertEqual(len(at.exception), 0, f"Page raised: {at.exception}")

        widget = _search_text_input(at)
        self.assertIsNotNone(widget, "Search text_input must render in sidebar")
        widget.set_value("water").run()
        self.assertEqual(len(at.exception), 0, f"Search run raised: {at.exception}")
        baseline = _session_get(at, "_sc3_search_writes")
        self.assertIsNotNone(
            baseline,
            "Counter wrapper must be active: search_query was committed via "
            "on_change but no write was counted",
        )

        trigger = _search_trigger_button(at)
        self.assertIsNotNone(trigger, "🔍 button (key=search_trigger) must render")
        trigger.click().run()
        self.assertEqual(len(at.exception), 0, f"🔍 click run raised: {at.exception}")
        after_first = _session_get(at, "_sc3_search_writes")
        self.assertEqual(
            after_first - baseline,
            1,
            f"Expected exactly 1 search_query commit per 🔍 click; observed "
            f"{after_first - baseline} (on_change + button body double-commit "
            "would show 2 unless the writes are the same value on the same "
            "script execution)",
        )
        self.assertEqual(_session_get(at, "search_query"), "water")
        self.assertEqual(_session_get(at, "current_page"), 1)

        # Second click with no intervening change: still exactly one commit,
        # and the committed value/page remain stable.
        trigger.click().run()
        self.assertEqual(len(at.exception), 0, f"Second 🔍 click raised: {at.exception}")
        after_second = _session_get(at, "_sc3_search_writes")
        self.assertEqual(
            after_second - after_first,
            1,
            f"Expected exactly 1 search_query commit for the second 🔍 click; "
            f"observed {after_second - after_first}",
        )
        self.assertEqual(_session_get(at, "search_query"), "water")
        self.assertEqual(_session_get(at, "current_page"), 1)


if __name__ == "__main__":
    unittest.main()
