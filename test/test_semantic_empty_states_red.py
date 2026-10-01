# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""RED-phase tests for SC-6 (Issue #1385, R-6): per-status empty-state
rendering for the semantic search seam payloads in the MAIN panel.

Each seam status (empty_query, no_embeddings, stale_model) plus the
zero-results-after-threshold case must render its designated clean empty
state — never a crash:

- empty_query            → st.info with status-specific copy (not the
                           generic empty-batch message)
- zero-results-after-threshold → st.info reusing the empty-batch branch with
                           status-specific copy naming the threshold
- no_embeddings          → st.warning naming the admin backfill remedy
                           "Table Maintenance → Data Reprocessing → Embedding Backfill"
- stale_model            → st.warning naming the same admin backfill remedy
- ok (ranked results)    → regression guard: no empty state, records render

Empty states render as full-width blocks in the MAIN panel — the sidebar
element list must contain none of them. No scenario may raise an exception.

Harness precedent: test_semantic_dispatch_red.py (AppTest + mocked service
modules via sys.modules insert-only containment).

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""
import unittest

from streamlit.testing.v1 import AppTest

BACKFILL_REMEDY = "Table Maintenance → Data Reprocessing → Embedding Backfill"

MOCK_TEMPLATE = """import sys
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

    _payload = SemanticSearchResult(**__PAYLOAD__)

    # R-8: the UI binds to the seam MODULE function search_semantic, not a
    # LinguisticService classmethod. The module is mocked wholesale.
    mock_seam = MagicMock()
    mock_seam.search_semantic = MagicMock(return_value=_payload)
    sys.modules["src.services.semantic_search_service"] = mock_seam
    sys.modules["src.services.semantic_search_service"].SemanticSearchResult = SemanticSearchResult

    mock_linguistic = MagicMock()
    # Exact-match browse (no-query semantic path) and other modes: empty.
    mock_linguistic.search_records.return_value = MagicMock(records=[], total_count=0)
    mock_linguistic.get_sources_with_counts.return_value = []
    mock_linguistic.get_languages.return_value = []
    mock_linguistic.get_all_records_for_export.return_value = []
    mock_linguistic.get_record.side_effect = lambda rid: {
        "id": rid, "is_locked": False, "source_name": "S", "mdf_data": "", "languages": [],
    }
    mock_linguistic.get_edit_history.return_value = []
    mock_linguistic.bundle_records_to_mdf = MagicMock(return_value="")
    mock_linguistic.stream_records_to_temp_file.return_value = "/tmp/test"

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


def _script(payload):
    return MOCK_TEMPLATE.replace("__PAYLOAD__", repr(payload))


def _make_at(payload):
    at = AppTest.from_string(_script(payload), default_timeout=30)
    at.session_state["search_mode"] = "Semantic Gloss"
    at.session_state["_semantic_ranked_cache"] = None
    return at


class TestSemanticEmptyStatesSC6(unittest.TestCase):
    """SC-6 RED: per-status empty-state rendering — all MUST FAIL now."""

    def test_empty_query_renders_status_specific_info_in_main(self):
        """empty_query → st.info with status-specific copy in the MAIN panel,
        not the generic empty-batch message."""
        payload = {"results": [], "status": "empty_query", "message": "No query provided."}
        at = _make_at(payload)
        at.session_state["search_query"] = "   "
        at.run()
        self.assertEqual(len(at.exception), 0, f"Page raised: {at.exception}")
        info_texts = [e.value or "" for e in at.main.info]
        self.assertTrue(
            any("enter a query" in t.lower() for t in info_texts),
            f"empty_query info copy missing in MAIN panel: {info_texts}",
        )
        # Sidebar rendering prohibited
        self.assertFalse(
            any("enter a query" in (e.value or "").lower() for e in at.sidebar.info),
            "empty_query state rendered in the sidebar",
        )

    def test_zero_results_after_threshold_reuses_empty_batch_branch_with_specific_copy(self):
        """ok status + empty results (all below threshold) → st.info in the
        empty-batch branch with copy naming the semantic threshold."""
        payload = {"results": [], "status": "ok", "message": ""}
        at = _make_at(payload)
        at.session_state["search_query"] = "water"
        at.run()
        self.assertEqual(len(at.exception), 0, f"Page raised: {at.exception}")
        info_texts = [e.value or "" for e in at.main.info]
        self.assertTrue(
            any("above the semantic threshold" in t for t in info_texts),
            f"zero-results threshold copy missing: {info_texts}",
        )
        self.assertTrue(
            any("0.80" in t for t in info_texts),
            f"threshold value not named in zero-results copy: {info_texts}",
        )
        self.assertFalse(
            any("above the semantic threshold" in (e.value or "") for e in at.sidebar.info),
            "zero-results state rendered in the sidebar",
        )

    def test_no_embeddings_renders_warning_naming_backfill_remedy(self):
        """no_embeddings → st.warning naming the admin backfill remedy."""
        payload = {"results": [], "status": "no_embeddings", "message": "No embeddings found."}
        at = _make_at(payload)
        at.session_state["search_query"] = "water"
        at.run()
        self.assertEqual(len(at.exception), 0, f"Page raised: {at.exception}")
        warning_texts = [e.value or "" for e in at.main.warning]
        self.assertTrue(
            any(BACKFILL_REMEDY in t for t in warning_texts),
            f"no_embeddings warning missing backfill remedy: {warning_texts}",
        )
        self.assertFalse(
            any(BACKFILL_REMEDY in (e.value or "") for e in at.sidebar.warning),
            "no_embeddings warning rendered in the sidebar",
        )

    def test_stale_model_renders_warning_naming_backfill_remedy(self):
        """stale_model → st.warning naming the admin backfill remedy."""
        payload = {"results": [], "status": "stale_model", "message": "Model pin mismatch."}
        at = _make_at(payload)
        at.session_state["search_query"] = "water"
        at.run()
        self.assertEqual(len(at.exception), 0, f"Page raised: {at.exception}")
        warning_texts = [e.value or "" for e in at.main.warning]
        self.assertTrue(
            any(BACKFILL_REMEDY in t for t in warning_texts),
            f"stale_model warning missing backfill remedy: {warning_texts}",
        )
        self.assertFalse(
            any(BACKFILL_REMEDY in (e.value or "") for e in at.sidebar.warning),
            "stale_model warning rendered in the sidebar",
        )

    def test_no_scenario_crashes(self):
        """None of the four status payloads and the ok-with-results payload
        may raise an exception."""
        payloads = [
            {"results": [], "status": "empty_query", "message": "m"},
            {"results": [], "status": "ok", "message": ""},
            {"results": [], "status": "no_embeddings", "message": "m"},
            {"results": [], "status": "stale_model", "message": "m"},
            {"results": [(3, 0.92), (1, 0.81)], "status": "ok", "message": ""},
        ]
        for payload in payloads:
            with self.subTest(status=payload["status"], results=bool(payload["results"])):
                at = _make_at(payload)
                at.session_state["search_query"] = payload["results"] and "water" or "   "
                at.run()
                self.assertEqual(len(at.exception), 0, f"Page raised: {at.exception}")

    def test_ok_with_results_renders_records_not_empty_state(self):
        """Regression guard: ok status with ranked results renders record
        cards (no zero-results copy)."""
        payload = {"results": [(3, 0.92), (1, 0.81)], "status": "ok", "message": ""}
        at = _make_at(payload)
        at.session_state["search_query"] = "water"
        at.run()
        self.assertEqual(len(at.exception), 0, f"Page raised: {at.exception}")
        body = "\n".join(m.value or "" for m in at.main.markdown)
        self.assertIn("Record #3", body)


if __name__ == "__main__":
    unittest.main()
