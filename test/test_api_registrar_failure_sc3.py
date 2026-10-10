# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Registrar failure-mode tests — issue #1420, SC-3.

When the Application or ``wildcard_router.rules`` structure is absent, the
registrar logs a loud error naming the mismatch, reports the API disabled,
and raises nothing — the live UI continues to run normally.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import logging
import unittest
from unittest import mock

from src.api import registrar


def _reset_latch() -> None:
    """Simulate a fresh module import (latch state recreated)."""
    registrar._bolted = False


class _StructurelessApp:
    """An Application-like object without the internal routing structure."""

    wildcard_router = object()  # no .rules attribute


class RegistrarFailureModeTests(unittest.TestCase):
    def setUp(self):
        _reset_latch()

    def tearDown(self):
        _reset_latch()

    def test_no_application_found_logs_loud_error_and_raises_nothing(self):
        with self.assertLogs("src.api.registrar", level="ERROR") as captured:
            # Must not raise even though no Application exists in this process.
            registrar.install_api_routes(lambda: None)
        joined = "\n".join(captured.output)
        self.assertIn("DISABLED", joined)
        self.assertIn("FAILED", joined)

    def test_structureless_application_is_skipped_and_reports_disabled(self):
        with mock.patch.object(registrar, "_find_applications", return_value=[_StructurelessApp()]):
            with self.assertLogs("src.api.registrar", level="ERROR") as captured:
                registrar.install_api_routes(lambda: None)
        joined = "\n".join(captured.output)
        self.assertIn("DISABLED", joined)

    def test_failure_leaves_api_disabled_bolt_flag_unset(self):
        with mock.patch.object(registrar, "_find_applications", return_value=[]):
            with self.assertLogs("src.api.registrar", level="ERROR"):
                registrar.install_api_routes(lambda: None)
        # A failed bolt leaves the latch unset: the next script run may retry.
        self.assertFalse(registrar._bolted)

    def test_no_exception_escapes_for_arbitrary_internal_error(self):
        with mock.patch.object(registrar, "_find_applications", side_effect=RuntimeError("boom")):
            with self.assertLogs("src.api.registrar", level="ERROR") as captured:
                registrar.install_api_routes(lambda: None)
        joined = "\n".join(captured.output)
        self.assertIn("DISABLED", joined)

    def test_loud_log_names_the_structural_mismatch(self):
        with mock.patch.object(registrar, "_find_applications", return_value=[]):
            with self.assertLogs("src.api.registrar", level="ERROR") as captured:
                registrar.install_api_routes(lambda: None)
        joined = "\n".join(captured.output)
        self.assertIn("wildcard_router", joined)
        self.assertIn("tornado.web.Application", joined)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
