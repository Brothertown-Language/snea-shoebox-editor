# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""RED tests for Phase 3 integration hooks — issue #1332.

These tests fail because migration log functions and handle_ui_error()
do not yet call EventLogService.

Co-authored with AI: OpenCode (ollama-cloud/deepseek-v4-flash)
"""

import unittest
from unittest.mock import patch


class TestMigrationIntegrationRED(unittest.TestCase):
    """RED tests: migration log functions don't call EventLogService yet."""

    def test_migration_start_calls_log_event(self):
        """SC-4: log_migration_start should call EventLogService.log_event()."""
        from src.database.migrations import log_migration_start
        from src.services.event_log_service import EventLogService

        with patch.object(EventLogService, "log_event") as mock_log:
            log_migration_start("test_version", "test_desc")
            mock_log.assert_called_once()

    def test_migration_skip_calls_log_event(self):
        """SC-4: log_migration_skip should call EventLogService.log_event()."""
        from src.database.migrations import log_migration_skip
        from src.services.event_log_service import EventLogService

        with patch.object(EventLogService, "log_event") as mock_log:
            log_migration_skip("test_version", "test_desc", "test_reason")
            mock_log.assert_called_once()

    def test_migration_complete_calls_log_event(self):
        """SC-4: log_migration_complete should call EventLogService.log_event()."""
        from src.database.migrations import log_migration_complete
        from src.services.event_log_service import EventLogService

        with patch.object(EventLogService, "log_event") as mock_log:
            log_migration_complete("test_version", "test_desc")
            mock_log.assert_called_once()

    def test_migration_error_calls_log_event(self):
        """SC-4: log_migration_error should call EventLogService.log_event()."""
        from src.database.migrations import log_migration_error
        from src.services.event_log_service import EventLogService

        with patch.object(EventLogService, "log_event") as mock_log:
            log_migration_error("test_version", "test_desc", "test_error")
            mock_log.assert_called_once()

    def test_handle_ui_error_calls_log_exception(self):
        """SC-5: handle_ui_error should call EventLogService.log_exception()."""
        from src.frontend.ui_utils import handle_ui_error
        from src.services.event_log_service import EventLogService

        with patch.object(EventLogService, "log_exception") as mock_log:
            handle_ui_error(Exception("test"), "user message")
            mock_log.assert_called_once()

    def test_stderr_logging_preserved(self):
        """SC-6: Stderr logging still happens after integration."""
        from src.database.migrations import log_migration_start
        from src.database.migrations import logger as migration_logger

        with patch.object(migration_logger, "info") as mock_info:
            log_migration_start("test_version", "test_desc")
            mock_info.assert_called()

    def test_handle_ui_error_signature_backward_compat(self):
        """SC-8: handle_ui_error accepts (Exception, str) without new required params."""
        import inspect

        from src.frontend.ui_utils import handle_ui_error

        sig = inspect.signature(handle_ui_error)
        params = list(sig.parameters.keys())
        # Must accept at minimum e and user_message
        self.assertIn("e", params)
        self.assertIn("user_message", params)
