# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""RED-phase tests for SC-4 (Issue #1385): semantic-mode result rows display
similarity scores inline in each record card's header line ("Record #id
(Source: X)"), fixed two-decimal format, rendered in the seam's sorted
descending order; exact-match mode rows display NO scores.

Harness precedent: test_semantic_dispatch_red.py (AppTest + mocked service
modules via sys.modules insert-only containment).

The seam mock returns ranked pairs in descending-score order
([(3, 0.92), (1, 0.81)]) so the rendered header lines must show 0.92 on
Record #3 and 0.81 on Record #1, first-in-document-order. Before GREEN, no
score rendering exists in the card header line — these tests MUST FAIL.

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""
import unittest

from streamlit.testing.v1 import AppTest

SEMANTIC_RESULT_TEMPLATE = """import sys
from unittest.mock import MagicMock

# Insert-only containment: save pre-existing entries, restore at scope-exit.
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
    from src.services.semantic_search_service import SemanticSearchResult

    mock_linguistic = MagicMock()
    # Exact-match modes: RecordSearchResult-shaped mock with one real record
    # so the card render loop executes and header lines render.
    _exact_rec = {
        "id": 7, "is_locked": False, "source_name": "S", "mdf_data": "", "languages": [],
    }
    mock_linguistic.search_records.return_value = MagicMock(
        records=[_exact_rec], total_count=1
    )
    mock_linguistic.get_sources_with_counts.return_value = []
    mock_linguistic.get_languages.return_value = []
    mock_linguistic.get_all_records_for_export.return_value = []
    mock_linguistic.get_edit_history.return_value = []
    mock_linguistic.bundle_records_to_mdf = MagicMock(return_value="")
    mock_linguistic.stream_records_to_temp_file.return_value = "/tmp/test"
    # Page-level semantic dispatch consumes get_record per ranked id.
    mock_linguistic.get_record.side_effect = lambda rid: {
        "id": rid, "is_locked": False, "source_name": "S", "mdf_data": "", "languages": [],
    }
    # Ranked ids in seam order (desc score): 3 then 1.
    _ranked = [(3, 0.92), (1, 0.81)]
    mock_linguistic.search_semantic = MagicMock(
        return_value=SemanticSearchResult(results=_ranked, status="ok", message="")
    )

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


def _header_lines(at):
    """Collect rendered markdown lines containing the card-header pattern."""
    body = "\n".join(m.value or "" for m in at.markdown)
    return [line for line in body.split("\n") if "Record #" in line]


class TestSemanticScoresRED(unittest.TestCase):
    """RED-phase SC-4 tests — all MUST FAIL against current code."""

    def setUp(self):
        self.at = AppTest.from_string(SEMANTIC_SCRIPT, default_timeout=30)

    def test_semantic_rows_show_two_decimal_scores_inline_in_header(self):
        """SC-4: semantic-mode card header lines include the row's similarity
        score inline (not behind a disclosure), fixed to two decimals."""
        self.at.session_state["search_query"] = "water"
        self.at.session_state["search_mode"] = "Semantic Gloss"
        self.at.run()
        self.assertEqual(len(self.at.exception), 0, f"Page raised: {self.at.exception}")
        headers = _header_lines(self.at)
        r3 = next((h for h in headers if "Record #3" in h), None)
        r1 = next((h for h in headers if "Record #1" in h), None)
        self.assertIsNotNone(r3, "Record #3 header should render")
        self.assertIsNotNone(r1, "Record #1 header should render")
        # Fixed two-decimal formatting.
        self.assertIn("0.92", r3, f"Score 0.92 missing in header line: {r3!r}")
        self.assertIn("0.81", r1, f"Score 0.81 missing in header line: {r1!r}")
        # Inline in the header line itself, not behind an expander body.
        self.assertEqual(
            len([h for h in self.at.expander if "0.92" in str(getattr(h, "value", ""))]),
            0,
            "Score must not render inside an expander (disclosure)",
        )

    def test_semantic_scores_in_descending_document_order(self):
        """SC-4: rows render in seam (score-descending) order — the header
        line carrying the higher score appears earlier in the DOM."""
        self.at.session_state["search_query"] = "water"
        self.at.session_state["search_mode"] = "Semantic All"
        self.at.run()
        self.assertEqual(len(self.at.exception), 0, f"Page raised: {self.at.exception}")
        headers = [h for h in _header_lines(self.at) if "Record #" in h]
        self.assertGreaterEqual(len(headers), 2)
        first_scored = next((h for h in headers if "0." in h), None)
        self.assertIsNotNone(first_scored, "At least one scored header must render")
        # First scored header belongs to the top-ranked record (#3, 0.92).
        self.assertIn("Record #3", first_scored, f"Top-ranked record must render first: {headers!r}")

    def test_exact_match_modes_show_no_scores(self):
        """SC-4: exact-match modes (Headword/Gloss/Lexeme/FTS) must not
        display similarity scores anywhere in record card headers."""
        for mode in ("Headword", "Gloss", "Lexeme", "FTS"):
            with self.subTest(mode=mode):
                at = AppTest.from_string(SEMANTIC_SCRIPT, default_timeout=30)
                at.session_state["search_query"] = "water"
                at.session_state["search_mode"] = mode
                at.run()
                self.assertEqual(len(at.exception), 0, f"Page raised: {at.exception}")

                for line in at.markdown:
                    if "Record #" in (line.value or ""):
                        self.assertNotIn("0.92", line.value, f"{mode} header must not show a score")

    def test_no_score_leakage_on_exact_rows_with_same_text(self):
        """SC-4 edge: the query string 'water'/'0.' patterns do not conflate
        with scores; the exact-mode header must be the plain header text."""
        at = AppTest.from_string(SEMANTIC_SCRIPT, default_timeout=30)
        at.session_state["search_query"] = "0.92"
        at.session_state["search_mode"] = "Headword"
        at.run()
        self.assertEqual(len(at.exception), 0, f"Page raised: {at.exception}")
        headers = [m.value for m in at.markdown if "Record #" in (m.value or "")]
        for h in headers:
            self.assertNotIn("score", h.lower(), f"Exact-mode header must not surface a score label: {h!r}")


if __name__ == "__main__":
    unittest.main()
