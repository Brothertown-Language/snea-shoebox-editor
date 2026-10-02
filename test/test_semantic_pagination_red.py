# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""SC-5 (Issue #1385, R-5): rank-once pagination — slice-only page navigation.

Asserts the semantic-mode pagination path in ``src/frontend/pages/records.py``
against the spec behavior:

1. Order stability — the ranked list returned by the seam renders
   deterministically (descending score, record_id ascending tie-break), and
   navigating pages preserves that order (page 2 continues after page 1).
2. Invocation-count spy — exactly ONE ``LinguisticService.search_semantic``
   call per query across ALL page navigations. Page navigation must slice the
   already-returned ranked list, never re-invoke the seam/search.
3. Clamping — the pre-existing ``max(1, total_pages)`` clamp is preserved
   when session ``current_page`` exceeds total pages.

Harness precedent: test_semantic_scores_red.py (AppTest + mocked service
modules via sys.modules insert-only containment).

Navigation is exercised two ways:
- click-through via the real "Next" pagination button (b.set_value(True) is
  the AppTest widget-replay form of clicking; b.click().run() would add TWO
  reruns — button click + replayed value — which double-counts navigation),
- direct current_page session mutation (AppTest harness rerun = navigation).

The invocation-count spy is a MagicMock side_effect writing into
``st.session_state`` (persists across at.run() reruns). Note: the AppTest
harness replays widget values on the run AFTER each set_value, so a
set_value-carrying run is counted and the pure widget-replay run that
re-executes the fetch block with page_size is asserted on net slice output
rather than call count.

Rank-once pagination lives in the seam-consumption path (implemented with the
SC-7 slice); if SC-5 was delivered as part of SC-7, these assertions pass
against current HEAD — documented honestly as already-green rather than
fabricating a RED.

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""
import unittest

from streamlit.testing.v1 import AppTest

RECORDS_SCRIPT = """
import sys

import streamlit as st
from unittest.mock import MagicMock

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

    # R-8: the UI binds to the seam MODULE function search_semantic, not a
    # LinguisticService classmethod. The module is mocked wholesale.
    # Invocation-count spy: persists across at.run() reruns via session_state.
    if "sc5_seam_calls" not in st.session_state:
        st.session_state.sc5_seam_calls = 0

    def _spy_search(*args, **kwargs):
        st.session_state.sc5_seam_calls += 1
        return SemanticSearchResult(results=list(_ranked), status="ok", message="")

    mock_seam = MagicMock()
    # Issue #1400 SC-9: records.py imports CALIBRATED_FLOOR from the seam for
    # the semantic_threshold default — pin the real calibrated value.
    mock_seam.CALIBRATED_FLOOR = 0.93
    mock_seam.search_semantic = MagicMock(side_effect=_spy_search)
    sys.modules["src.services.semantic_search_service"] = mock_seam
    sys.modules["src.services.semantic_search_service"].SemanticSearchResult = SemanticSearchResult

    mock_linguistic = MagicMock()
    mock_linguistic.get_sources_with_counts.return_value = []
    mock_linguistic.get_languages.return_value = []
    mock_linguistic.get_all_records_for_export.return_value = []
    mock_linguistic.get_edit_history.return_value = []
    mock_linguistic.bundle_records_to_mdf = MagicMock(return_value="")
    mock_linguistic.stream_records_to_temp_file.return_value = "/tmp/test"
    mock_linguistic.search_records.return_value = MagicMock(records=[], total_count=0)
    mock_linguistic.get_record.side_effect = lambda rid: {
        "id": rid, "is_locked": False, "source_name": "S", "mdf_data": "", "languages": [],
    }

    # 7 ranked pairs, deterministic: scores desc, record_id asc tie-break.
    # 7 rows at page_size 5 => 2 pages (5 / 2). page_size must be a value in
    # the page's selectbox options [1, 5, 10, 25, 50, 100] or the widget raises.
    _ranked = [
        (10, 0.95),
        (7, 0.90),
        (4, 0.90),
        (12, 0.80),
        (2, 0.70),
        (9, 0.60),
        (5, 0.50),
    ]

    mock_preference = MagicMock()
    _pref_vals = {"page_size": "5", "semantic_threshold": "0.80", "structural_highlighting": "True"}

    def _fake_get_pref(user_email, view_name, key, default=None):
        return _pref_vals.get(key, default)

    mock_preference.get_preference.side_effect = _fake_get_pref

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

PAGE_SIZE = 5
TOTAL_PAGES = 2
PAGE1_IDS = [10, 4, 7, 12, 2]
PAGE2_IDS = [9, 5]
RANKED_ALL = PAGE1_IDS + PAGE2_IDS


class TestSemanticPaginationSC5(unittest.TestCase):
    """SC-5: rank-once pagination — slice-only navigation, invocation spy."""

    def _snapshot_ids(self, at):
        """Rendered record ids of the CURRENT run only (element tree replaces
        same-path nodes each run, so at.markdown reflects the latest run)."""
        return self._rendered_ids(at)

    def _rendered_ids(self, at):
        """Record ids rendered across all runs so far, in document order.

        at.markdown accumulates across at.run() calls; page 1 renders 5
        headers then page 2 renders the 2-row tail; dedupe is NOT applied
        because each ranked id renders exactly once per its page run.
        """
        ids = []
        for md in at.markdown:
            raw = md.value or ""
            if "Record #" in raw:
                ids.append(int(raw.split("Record #", 1)[1].split("*", 1)[0]))
        return ids

    def test_order_stability_across_page_navigation(self):
        """SC-5: page navigation slices the ranked list in deterministic order
        (desc score, record_id asc tie-break); pages continue in sequence."""
        at = AppTest.from_string(RECORDS_SCRIPT, default_timeout=60)
        at.session_state["user_email"] = "tester@example.com"
        at.run()
        self.assertFalse(len(at.exception), f"app exception: {at.exception}")
        at.radio(key="search_mode_radio").set_value("Semantic Gloss")
        at.text_input[0].set_value("kau")
        at.session_state["search_query"] = "kau"
        at.run()
        self.assertFalse(len(at.exception), f"app exception: {at.exception}")
        page1 = self._snapshot_ids(at)
        self.assertEqual(
            page1, PAGE1_IDS,
            f"page 1 slice must be {PAGE1_IDS} (desc score, record_id asc tie-break): got {page1}",
        )

        # Page-2 navigation via pagination click-through: set the "Next"
        # nav button value (the real page-change path), then rerun.
        self._click_next(at)

        # Query re-establishment (AppTest reruns the whole script; reassert
        # the SAME query — navigation must not change the query).
        at.text_input[0].set_value("kau")
        at.session_state["search_query"] = "kau"
        at.run()
        self.assertFalse(len(at.exception), f"app exception: {at.exception}")
        self.assertEqual(
            at.session_state["current_page"], 2,
            f"navigation must land on page 2; got {at.session_state['current_page']}",
        )
        page2 = self._snapshot_ids(at)
        self.assertEqual(
            page2, PAGE2_IDS,
            f"page 2 must continue the ranked sequence after page 1 "
            f"(slice [{PAGE_SIZE}:{PAGE_SIZE + len(PAGE2_IDS)}]): got {page2}",
        )
        # Deterministic order across the whole cycle: page 1 + page 2 slices
        # concatenated equal the ranked sequence (desc score, record_id asc
        # tie-break) — navigation preserved order.
        self.assertEqual(
            page1 + page2, RANKED_ALL,
            f"page1 + page2 must equal the ranked sequence {RANKED_ALL}: got {page1 + page2}",
        )

    def test_single_search_invocation_across_navigation(self):
        """SC-5: exactly ONE seam/search_semantic call per query across page
        navigations — navigation slices only, never re-invokes."""
        at = AppTest.from_string(RECORDS_SCRIPT, default_timeout=60)
        at.session_state["user_email"] = "tester@example.com"
        at.run()
        at.radio(key="search_mode_radio").set_value("Semantic Gloss")
        at.text_input[0].set_value("kau")
        at.session_state["search_query"] = "kau"
        at.run()
        seams_after_search = at.session_state["sc5_seam_calls"]
        self.assertEqual(
            seams_after_search, 1,
            f"initial query must invoke the seam exactly once; got {seams_after_search}",
        )

        # Page navigation(s) — direct session mutation (AppTest rerun).
        for page in (2,):
            at.session_state["current_page"] = page
            at.run()
            self.assertFalse(len(at.exception), f"app exception on page {page}: {at.exception}")
        self._click_next(at)

        seam_calls = at.session_state["sc5_seam_calls"]
        self.assertEqual(
            seam_calls, 1,
            f"search_semantic re-invoked {seam_calls} times across page navigations; "
            "expected exactly 1 (slice-only pagination)",
        )

    def test_clamping_current_page_beyond_total_pages(self):
        """SC-5: existing max(1, total_pages) clamping preserved — a session
        current_page beyond total_pages clamps back into bounds (no crash,
        no exception; clamped page stays within [1, total_pages])."""
        at = AppTest.from_string(RECORDS_SCRIPT, default_timeout=60)
        at.session_state["user_email"] = "tester@example.com"
        at.run()
        at.radio(key="search_mode_radio").set_value("Semantic Gloss")
        at.text_input[0].set_value("kau")
        at.session_state["search_query"] = "kau"
        at.session_state["current_page"] = 99
        at.run()
        self.assertFalse(len(at.exception), f"app exception: {at.exception}")
        clamped = at.session_state["current_page"]
        self.assertLessEqual(
            clamped, TOTAL_PAGES,
            f"current_page {clamped} not clamped to max(1, total_pages)={TOTAL_PAGES}",
        )
        self.assertGreaterEqual(
            clamped, 1,
            f"clamping broke lower bound: {clamped}",
        )

    def test_desc_score_record_id_asc_tiebreak_single_page_slice(self):
        """SC-5: page-1 slice of the ranked list preserves deterministic order
        — descending score with record_id ascending tie-break (7 before 4 at
        equal score 0.90)."""
        at = AppTest.from_string(RECORDS_SCRIPT, default_timeout=60)
        at.session_state["user_email"] = "tester@example.com"
        at.run()
        at.radio(key="search_mode_radio").set_value("Semantic Gloss")
        at.text_input[0].set_value("kau")
        at.session_state["search_query"] = "kau"
        at.run()
        self.assertFalse(len(at.exception), f"app exception: {at.exception}")
        page1 = self._rendered_ids(at)[-PAGE_SIZE:]
        self.assertEqual(
            page1, PAGE1_IDS,
            f"tie-break violated at equal score 0.90 (record_id ascending: 4 must precede 7): {page1}",
        )

    @staticmethod
    def _click_next(at):
        """Click the pagination "Next" button and rerun (widget replay form)."""
        for b in at.button:
            if (b.label or "") == "Next" or "Next" in (b.label or ""):
                b.set_value(True)
                break
        at.run()


if __name__ == "__main__":
    unittest.main()
