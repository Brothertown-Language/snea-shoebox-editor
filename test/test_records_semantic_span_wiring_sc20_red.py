# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""RED-phase tests for SC-20 (Issue #1401, revised 2026-10-03): the Records
page View-mode wiring must compute highlight spans for semantic modes
(Semantic Gloss / Semantic All) from the per-record matched source-field
terms via ``compute_term_spans`` — the same verbatim whole-term computation
used for stored terms.

Harness precedent: test_semantic_scores_red.py (AppTest + mocked service
modules via sys.modules insert-only containment). ``src.frontend.ui_utils``
is mocked wholesale so ``render_mdf_block`` calls can be captured and the
``highlight_spans`` kwarg inspected at the wiring boundary.

Current implementation state (pre-GREEN): ``src/frontend/pages/records.py``
suppresses span computation for semantic modes — the View-mode condition
reads ``if search_term and not is_semantic_mode:`` — and the semantic seam
path constructs the page-local result container without ``matched_terms``.
Therefore NO highlight spans reach ``render_mdf_block`` under either
semantic mode, and the semantic-mode tests MUST FAIL (RED). The
empty-query boundary test (spans stay ``None`` without a query) is a
regression guard expected to PASS both pre- and post-GREEN.

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""
import sys
import unittest
from types import SimpleNamespace

from streamlit.testing.v1 import AppTest

# The mdf_data is written as a real formatted MDF record; format_mdf_record
# is mocked as identity passthrough so the rendered lines are deterministic.
MDF_DATA = "\\lx wəkəs\n\\ge water"
TERM = "wəkəs"
RECORD_ID = 3

RECORDS_SCRIPT = """
import sys
from types import SimpleNamespace
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
    "src.mdf.parser",
    "src.frontend.ui_utils",
]
_saved_modules = {p: sys.modules.get(p) for p in _MOCK_MODULE_PATHS}
try:
    # R-8: the UI binds to the seam MODULE function search_semantic. The
    # module is mocked wholesale; the pinned CALIBRATED_FLOOR is reproduced.
    # SC-8 (revised): the semantic result carries per-record matched
    # source-field terms; the page must surface them as highlight spans.
    _seam_result = SimpleNamespace(
        results=[(3, 0.97)],
        status="ok",
        message="",
        matched_terms={3: {"wəkəs"}},
    )
    mock_seam = MagicMock()
    mock_seam.CALIBRATED_FLOOR = 0.93
    mock_seam.search_semantic = MagicMock(return_value=_seam_result)
    sys.modules["src.services.semantic_search_service"] = mock_seam

    mock_linguistic = MagicMock()
    # The page imports the CLASS (LinguisticService.get_record(...)), so the
    # mock module must expose itself as the class attribute (template idiom).
    mock_linguistic.LinguisticService = mock_linguistic
    # Browse path (empty query in a semantic mode) goes through
    # search_records with search_term=None — return one real-shaped record
    # so the View-mode render call exists and its spans are inspectable.
    # Export side panel: no export rows — avoids the editor/admin export
    # streaming path, which is outside the span-wiring scope under test.
    mock_linguistic.get_all_records_for_export.return_value = []
    mock_linguistic.search_records = MagicMock(
        return_value=SimpleNamespace(
            records=[
                {
                    "id": 3,
                    "source_name": "Test Source",
                    "mdf_data": "\\\\lx wəkəs\\n\\\\ge water",
                    "is_locked": False,
                }
            ],
            total_count=1,
            limit=25,
            offset=0,
            matched_terms=None,
        )
    )
    mock_linguistic.get_record.return_value = {
        "id": 3,
        "source_name": "Test Source",
        "mdf_data": "\\\\lx wəkəs\\n\\\\ge water",
        "is_locked": False,
    }
    sys.modules["src.services.linguistic_service"] = mock_linguistic

    mock_preference = MagicMock()
    mock_preference.get_preference.return_value = "25"
    sys.modules["src.services.preference_service"] = mock_preference

    mock_identity = MagicMock()
    mock_identity.get_github_username.return_value = "tester"
    sys.modules["src.services.identity_service"] = mock_identity

    mock_nav = MagicMock()
    mock_nav.PAGE_DIRECT_ENTRY = "/direct_entry"
    sys.modules["src.services.navigation_service"] = mock_nav

    mock_upload = MagicMock()
    mock_upload.generate_mdf_filename.return_value = "test.mdf"
    sys.modules["src.services.upload_service"] = mock_upload

    mock_validator = MagicMock()
    mock_validator.diagnose_record.return_value = None
    sys.modules["src.mdf.validator"] = mock_validator

    # Identity passthrough so the rendered MDF lines are exactly the record's
    # lines and the expected compute_term_spans output is deterministic.
    mock_parser = MagicMock()
    mock_parser.format_mdf_record = lambda mdf: mdf
    sys.modules["src.mdf.parser"] = mock_parser

    # ui_utils mocked wholesale to CAPTURE render_mdf_block wiring: the test
    # inspects the highlight_spans kwarg the page threads into View-mode
    # rendering (SC-17 pattern: spans threaded ONLY into the View-mode call).
    mock_ui = MagicMock()
    sys.modules["src.frontend.ui_utils"] = mock_ui

    import src.frontend.pages.records as _records_module
    _records_module._test_ui_mock = mock_ui

    from src.frontend.pages.records import records
    records()
finally:
    for _path, _saved in _saved_modules.items():
        if _saved is not None:
            sys.modules[_path] = _saved
        else:
            del sys.modules[_path]
"""


def _view_render_kwargs(key_suffix):
    """Return the kwargs of the render_mdf_block call whose key carries the
    given suffix (View-mode calls use key=f"render_{record_id}")."""
    from src.frontend.pages import records as records_page

    mock_ui = records_page._test_ui_mock
    calls = [
        c for c in mock_ui.render_mdf_block.call_args_list if str(c.kwargs.get("key", "")).endswith(key_suffix)
    ]
    return calls[0].kwargs if calls else None


class TestSemanticSpanWiringRED(unittest.TestCase):
    """RED-phase SC-20 tests — semantic-mode assertions MUST FAIL pre-GREEN."""

    def _run(self, query, mode="Semantic Gloss"):
        at = AppTest.from_string(RECORDS_SCRIPT, default_timeout=30)
        at.session_state["search_query"] = query
        at.session_state["search_mode"] = mode
        at.session_state["user_email"] = "tester@example.com"
        # Viewer role: the editor/admin-only export path would exercise
        # unmocked file streaming; the View-mode render under test is
        # role-independent.
        at.session_state["user_role"] = "viewer"
        at.run()
        self.assertEqual(len(at.exception), 0, f"Page raised: {at.exception}")
        return at

    def test_semantic_gloss_view_mode_receives_matched_term_spans(self):
        """SC-20: Semantic Gloss View-mode render must receive non-None
        highlight spans computed from the matched source-field term via
        compute_term_spans (verbatim whole-term find)."""
        at = self._run(TERM, "Semantic Gloss")
        kwargs = _view_render_kwargs(f"render_{RECORD_ID}")
        self.assertIsNotNone(
            kwargs,
            "No View-mode render_mdf_block call for Record #3 in Semantic Gloss mode",
        )
        spans = kwargs.get("highlight_spans")
        self.assertIsNotNone(
            spans,
            "SC-20: View-mode render in Semantic Gloss mode received "
            "highlight_spans=None — the wiring suppresses span computation for "
            "semantic modes and must compute spans from matched source-field "
            "terms via compute_term_spans.",
        )
        self.assertIsInstance(spans, list)
        self.assertGreater(len(spans), 0, "highlight_spans must cover the rendered MDF lines")
        self.assertTrue(
            any(span_list for span_list in spans),
            "SC-20: highlight_spans contains no non-empty span list — the matched "
            f"source-field term '{TERM}' occurs in the record's MDF data, so at "
            "least one line must carry spans.",
        )
        # Line 0 is "\\lx wəkəs" — the term occurs at code-point offset 4..9.
        self.assertEqual(
            spans[0],
            [(4, 9)],
            f"SC-20: first-line spans must be the verbatim compute_term_spans "
            f"output for '{TERM}': got {spans[0]!r}",
        )

    def test_semantic_all_view_mode_receives_matched_term_spans(self):
        """SC-20: Semantic All View-mode render must receive non-None
        highlight spans computed from the matched source-field term."""
        at = self._run(TERM, "Semantic All")
        kwargs = _view_render_kwargs(f"render_{RECORD_ID}")
        self.assertIsNotNone(
            kwargs,
            "No View-mode render_mdf_block call for Record #3 in Semantic All mode",
        )
        spans = kwargs.get("highlight_spans")
        self.assertIsNotNone(
            spans,
            "SC-20: View-mode render in Semantic All mode received "
            "highlight_spans=None — the wiring suppresses span computation for "
            "semantic modes and must compute spans from matched source-field "
            "terms via compute_term_spans.",
        )
        self.assertTrue(
            any(span_list for span_list in (spans or [])),
            "SC-20: highlight_spans contains no non-empty span list in Semantic "
            f"All mode — the matched source-field term '{TERM}' occurs in the "
            "record's MDF data.",
        )
        self.assertEqual(spans[0], [(4, 9)])

    def test_empty_query_still_renders_no_spans(self):
        """Boundary guard (expected PASS pre- and post-GREEN): with an empty
        query the View-mode render receives NO highlight spans."""
        at = self._run("", "Semantic Gloss")
        kwargs = _view_render_kwargs(f"render_{RECORD_ID}")
        self.assertIsNotNone(
            kwargs,
            "Browse render (empty semantic query) should still occur for Record #3",
        )
        self.assertIsNone(
            kwargs.get("highlight_spans"),
            "Empty-query boundary: View-mode render must receive NO highlight spans",
        )


if __name__ == "__main__":
    unittest.main()
