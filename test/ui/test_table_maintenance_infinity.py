# Copyright (c) 2026 Brothertown Language
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""SC-3 RED-phase test — Table Maintenance sidebar includes "∞→ꝏ Remediation".

Issue #1382, plan step 35.
Admin session (user_role="admin" in session_state) renders Table Maintenance
and the sidebar radio includes the "∞→ꝏ Remediation" option. A non-admin
session is blocked by the existing admin guard (permission error).

Test MUST FAIL now (RED): the option is absent from the sidebar radio list.

Co-authored with AI: OpenCode (zai-org/GLM-5.3-Flash)
"""
import unittest

from streamlit.testing.v1 import AppTest


def _make_script(user_role):
    """Build an AppTest script that mocks the services table_maintenance
    imports inside its function bodies, following the established pattern
    in test_table_maintenance_backfill_red.py (insert-only sys.modules
    patching)."""
    return f"""
import streamlit as st
from unittest.mock import MagicMock

st.session_state["user_role"] = {user_role!r}

mock_linguistic = MagicMock()
mock_linguistic.get_deleted_records.return_value = []
mock_linguistic.get_sources_with_counts.return_value = []

mock_upload = MagicMock()
mock_upload.reprocess_all_records.return_value = {{"reprocessed": 0, "total": 0}}

import sys

_MOCK_MODULE_PATHS = [
    "src.services.linguistic_service",
    "src.services.upload_service",
    "src.services.semantic_search_service",
    "src.services.embedding_service",
    "src.services.navigation_service",
    "src.frontend.ui_utils",
]
_saved_modules = {{p: sys.modules.get(p) for p in _MOCK_MODULE_PATHS}}
try:
    sys.modules["src.services.linguistic_service"] = MagicMock()
    sys.modules["src.services.linguistic_service"].LinguisticService = mock_linguistic
    sys.modules["src.services.upload_service"] = MagicMock()
    sys.modules["src.services.upload_service"].UploadService = mock_upload
    sys.modules["src.services.semantic_search_service"] = MagicMock()
    sys.modules["src.services.embedding_service"] = MagicMock()
    sys.modules["src.services.navigation_service"] = MagicMock()

    sys.modules["src.frontend.ui_utils"] = MagicMock()

    from src.frontend.pages.table_maintenance import main
    main()
finally:
    for _path, _saved in _saved_modules.items():
        if _saved is not None:
            sys.modules[_path] = _saved
        else:
            del sys.modules[_path]
"""


class TestTableMaintenanceInfinityRemediationSC3(unittest.TestCase):
    """SC-3 RED — sidebar radio must include "∞→ꝏ Remediation"."""

    def test_admin_sidebar_radio_includes_infinity_remediation(self):
        """SC-3 RED — admin session renders Table Maintenance and the sidebar
        radio includes "∞→ꝏ Remediation" (absent today → RED)."""
        at = AppTest.from_string(_make_script("admin"), default_timeout=15)
        at.run()
        self.assertFalse(at.exception)
        self.assertGreaterEqual(len(at.radio), 1, "Sidebar radio must render")
        options = list(at.radio[0].options)
        self.assertIn(
            "∞→ꝏ Remediation",
            options,
            f'Sidebar radio must include "∞→ꝏ Remediation" '
            f"(RED: options = {options!r})",
        )

    def test_non_admin_blocked_by_admin_guard(self):
        """SC-3 — non-admin session is blocked by the existing admin guard
        (permission error), regardless of the new option."""
        at = AppTest.from_string(_make_script("viewer"), default_timeout=15)
        at.run()
        self.assertFalse(at.exception)
        error_text = " ".join(e.value or "" for e in at.error)
        self.assertIn("permission", error_text.lower())
        # Non-admin never reaches a sidebar radio.
        self.assertEqual(len(at.radio), 0, "Non-admin must not see the sidebar radio")


class TestInfinityRemediationSC4SC12(unittest.TestCase):
    """SC-4 + SC-12 RED — remediation view UI flow (plan step 40).

    GREEN contract (what the implementation must render):
    - On view open with N defective records (remediable R, locked L):
      the page displays "Remediable: R" and "Locked: L" separately,
      and nothing is applied until the confirm-gated Apply All is clicked
      (remediate_all_records() is never called on render).
    - Zero-state (R=0, L=0): an informational message is shown and no
      action buttons render.
    - Apply All is confirm-gated: clicking "Apply All" without the confirm
      checkbox does NOT call the batch; setting the confirm checkbox and
      clicking calls the batch.
    - After Apply All the outcome report states the remediated count and
      the locked (unremediated) count: "2 records remediated" and
      "1 locked" for a {"remediated": 2, "locked": 1} batch outcome.
    """

    def _run_view(self, remediable, locked, remediated=0, batch_locked=0):
        """Run the admin session through the ∞→ꝏ Remediation view with
        mocked services, following the established sys.modules patching
        pattern. Returns the AppTest after the view renders."""
        script = f"""
import streamlit as st
from unittest.mock import MagicMock

st.session_state["user_role"] = "admin"

mock_linguistic = MagicMock()
mock_linguistic.count_infinity_records.return_value = {remediable}
mock_linguistic.list_infinity_records.return_value = [
    {{"id": i, "lx": f"word{{i}}", "preview": "…∞…", "is_locked": False}}
    for i in range({remediable})
] + [
    {{"id": 1000 + j, "lx": f"locked{{j}}", "preview": "…∞…", "is_locked": True}}
    for j in range({locked})
]
mock_linguistic.remediate_all_records.return_value = {{
    "remediated": {remediated}, "locked": {batch_locked}
}}

mock_upload = MagicMock()
mock_upload.reprocess_all_records.return_value = {{"reprocessed": 0, "total": 0}}
mock_upload.populate_search_entries.return_value = None

mock_backfill = MagicMock()
mock_backfill.backfill_embeddings.return_value = {{"backfilled": 0, "total": 0}}

import sys

_MODULE_PATHS = [
    "src.services.linguistic_service",
    "src.services.upload_service",
    "src.services.semantic_search_service",
    "src.services.embedding_service",
    "src.services.navigation_service",
    "src.frontend.ui_utils",
]
_saved = {{p: sys.modules.get(p) for p in _MODULE_PATHS}}
try:
    sys.modules["src.services.linguistic_service"] = MagicMock()
    sys.modules["src.services.linguistic_service"].LinguisticService = mock_linguistic
    sys.modules["src.services.upload_service"] = MagicMock()
    sys.modules["src.services.upload_service"].UploadService = mock_upload
    sys.modules["src.services.semantic_search_service"] = MagicMock()
    sys.modules["src.services.semantic_search_service"].backfill_embeddings = (
        mock_backfill.backfill_embeddings
    )
    sys.modules["src.services.embedding_service"] = MagicMock()
    sys.modules["src.services.navigation_service"] = MagicMock()
    sys.modules["src.frontend.ui_utils"] = MagicMock()

    # Expose the mock for post-run assertions.
    st.session_state["_mock_linguistic"] = mock_linguistic

    from src.frontend.pages.table_maintenance import main
    main()
finally:
    for _path, _saved_mod in _saved.items():
        if _saved_mod is not None:
            sys.modules[_path] = _saved_mod
        else:
            del sys.modules[_path]
"""
        at = AppTest.from_string(script, default_timeout=15)
        at.run()
        self.assertFalse(at.exception, f"App crashed: {at.exception}")
        # Navigate to the ∞→ꝏ Remediation view.
        self.assertGreaterEqual(len(at.radio), 1, "Sidebar radio must render")
        at.radio[0].set_value("∞→ꝏ Remediation").run()
        self.assertFalse(at.exception, f"App crashed on view: {at.exception}")
        return at

    @staticmethod
    def _page_text(at):
        elements = (
            list(at.markdown)
            + list(at.info)
            + list(at.warning)
            + list(at.success)
            + list(at.error)
            + list(at.header)
            + list(at.subheader)
        )
        return " ".join((el.value or "") for el in elements)

    def test_counts_displayed_separately_and_nothing_applied_on_render(self):
        """SC-4 RED — with 3 remediable + 2 locked defective records, the
        view shows both counts separately and applies nothing until the
        confirm-gated Apply All is clicked."""
        at = self._run_view(remediable=3, locked=2)
        text = self._page_text(at)
        self.assertIn("Remediable: 3", text, f"RED: remediable count absent — text={text!r}")
        self.assertIn("Locked: 2", text, f"RED: locked count absent — text={text!r}")
        # Nothing applied on render.
        mock = at.session_state["_mock_linguistic"]
        mock.remediate_all_records.assert_not_called()

    def test_zero_state_shows_info_and_no_action_buttons(self):
        """SC-4 RED — 0 defective records: informational message, no action
        buttons."""
        at = self._run_view(remediable=0, locked=0)
        text = self._page_text(at)
        self.assertTrue(
            any(e.value for e in at.info),
            f"RED: zero-state info absent — text={text!r}",
        )
        buttons = [b for b in at.button if (b.label or "") and "Apply" in b.label]
        self.assertEqual(
            len(buttons), 0, f"RED: zero-state must show no Apply buttons — {[b.label for b in at.button]!r}"
        )

    def test_apply_all_requires_confirm(self):
        """SC-4 RED — clicking Apply All without the confirm checkbox does
        nothing; with the confirm checkbox set the batch runs."""
        at = self._run_view(remediable=2, locked=1)
        apply_buttons = [b for b in at.button if (b.label or "") == "Apply All"]
        self.assertEqual(
            len(apply_buttons), 1, f"RED: no 'Apply All' button — {[b.label for b in at.button]!r}"
        )
        # Click without confirmation — batch must not run.
        apply_buttons[0].click().run()
        self.assertFalse(at.exception, f"App crashed: {at.exception}")
        # AppTest recreates module-level mocks on every .run() — re-fetch
        # the mock AFTER this run so the assertion sees the live object.
        mock = at.session_state["_mock_linguistic"]
        mock.remediate_all_records.assert_not_called()
        # Confirm, then click — batch must run.
        checkboxes = [c for c in at.checkbox if "confirm" in (c.label or "").lower()]
        self.assertGreaterEqual(
            len(checkboxes), 1, f"RED: no confirm checkbox — {[c.label for c in at.checkbox]!r}"
        )
        checkboxes[0].set_value(True).run()
        apply_buttons = [b for b in at.button if (b.label or "") == "Apply All"]
        apply_buttons[0].click().run()
        self.assertFalse(at.exception, f"App crashed after apply: {at.exception}")
        mock = at.session_state["_mock_linguistic"]
        mock.remediate_all_records.assert_called_once()
        _, kwargs = mock.remediate_all_records.call_args
        self.assertIn("progress_callback", kwargs)

    def test_outcome_report_states_remediated_and_locked_counts(self):
        """SC-12 RED — after Apply All the outcome report states the
        remediated count and the locked (unremediated) count."""
        at = self._run_view(remediable=2, locked=1, remediated=2, batch_locked=1)
        checkboxes = [c for c in at.checkbox if "confirm" in (c.label or "").lower()]
        checkboxes[0].set_value(True).run()
        apply_buttons = [b for b in at.button if (b.label or "") == "Apply All"]
        apply_buttons[0].click().run()
        self.assertFalse(at.exception, f"App crashed after apply: {at.exception}")
        text = self._page_text(at)
        self.assertIn(
            "2 records remediated", text, f"RED: remediated count absent from report — text={text!r}"
        )
        self.assertIn(
            "1 locked", text, f"RED: locked (unremediated) count absent from report — text={text!r}"
        )


if __name__ == "__main__":
    unittest.main()
