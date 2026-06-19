# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""RED tests for EventLogService — Phase 2 of issue #1332.

These tests fail because EventLogService doesn't exist yet.

Co-authored with AI: OpenCode (ollama-cloud/deepseek-v4-flash)
"""
import unittest


class TestEventLogServiceRED(unittest.TestCase):
    """RED tests: EventLogService does not exist yet."""

    def test_log_event_writes_record(self):
        """SC-2: EventLogService.log_event() should exist."""
        from src.services.event_log_service import EventLogService  # noqa: F811

        self.assertTrue(hasattr(EventLogService, "log_event"))

    def test_log_exception_extracts_exception(self):
        """SC-3: EventLogService.log_exception() should exist."""
        from src.services.event_log_service import EventLogService  # noqa: F811

        self.assertTrue(hasattr(EventLogService, "log_exception"))

    def test_log_event_has_error_safe_session_pattern(self):
        """SC-7: log_event should accept optional session parameter."""
        from src.services.event_log_service import EventLogService  # noqa: F811

        import inspect

        sig = inspect.signature(EventLogService.log_event)
        self.assertIn("session", sig.parameters)

    def test_get_events_exists(self):
        """SC-9: EventLogService.get_events() should exist."""
        from src.services.event_log_service import EventLogService  # noqa: F811

        self.assertTrue(hasattr(EventLogService, "get_events"))
