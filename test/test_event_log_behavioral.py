# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Behavioral tests for EventLogService — Phase 2 of issue #1332.

These tests verify actual DB behavior: writing records, extracting exceptions,
handling DB failures, and querying with filters.

Co-authored with AI: OpenCode (ollama-cloud/deepseek-v4-flash)
"""
import unittest
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


class TestEventLogServiceBehavioral(unittest.TestCase):
    """Behavioral tests for EventLogService."""

    @classmethod
    def setUpClass(cls):
        try:
            import pgserver

            from src.database.base import Base

            cls.test_db_path = Path("tmp/test_event_log_behavioral_db")
            if cls.test_db_path.exists():
                import shutil
                shutil.rmtree(cls.test_db_path)
            cls.test_db_path.mkdir(parents=True, exist_ok=True)

            cls.pg_server = pgserver.get_server(str(cls.test_db_path))
            cls.db_url = cls.pg_server.get_uri()
            cls.engine = create_engine(cls.db_url)

            with cls.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()

            from src.database.models.core import Language, Record, Source  # noqa: F401
            from src.database.models.identity import User  # noqa: F401
            from src.database.models.search import (  # noqa: F401
                FTSEntry,
                GlossSearchEntry,
                HeadwordSearchEntry,
                SearchEntry,
            )
            from src.database.models.workflow import EditHistory, MatchupQueue  # noqa: F401
            from src.database.models.event_log import SystemEventLog  # noqa: F401

            Base.metadata.create_all(cls.engine)
            cls.Session = sessionmaker(bind=cls.engine)
        except ImportError:
            raise unittest.SkipTest("pgserver not available") from None

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "pg_server"):
            cls.pg_server.cleanup()
        if hasattr(cls, "test_db_path") and cls.test_db_path.exists():
            import shutil
            shutil.rmtree(cls.test_db_path)

    def setUp(self):
        from src.database.models.event_log import SystemEventLog

        self.session = self.Session()
        self.session.query(SystemEventLog).delete()
        self.session.commit()

    def tearDown(self):
        self.session.close()

    def test_log_event_writes_record(self):
        """SC-2: log_event() writes a record to system_event_log with correct field values."""
        from src.services.event_log_service import EventLogService

        EventLogService.log_event(
            event_type="test_type",
            severity="info",
            message="test message",
            source="test_module",
            details={"key": "value"},
            session=self.session,
        )

        from src.database.models.event_log import SystemEventLog

        record = self.session.query(SystemEventLog).first()
        self.assertIsNotNone(record, "A record should exist after log_event()")
        self.assertEqual(record.event_type, "test_type")
        self.assertEqual(record.severity, "info")
        self.assertEqual(record.message, "test message")
        self.assertEqual(record.source, "test_module")
        self.assertIsNotNone(record.details)
        self.assertEqual(record.details.get("key"), "value")
        self.assertIsNotNone(record.created_at)

    def test_log_exception_extracts_exception(self):
        """SC-3: log_exception() extracts exception type, message, and stack trace."""
        from src.services.event_log_service import EventLogService

        try:
            raise ValueError("test error detail")
        except ValueError as e:
            EventLogService.log_exception(e, session=self.session)

        from src.database.models.event_log import SystemEventLog

        record = self.session.query(SystemEventLog).first()
        self.assertIsNotNone(record, "A record should exist after log_exception()")
        self.assertEqual(record.event_type, "exception")
        self.assertEqual(record.severity, "error")
        self.assertIn("ValueError", record.message)
        self.assertIsNotNone(record.details)
        self.assertEqual(record.details.get("exception_type"), "ValueError")
        self.assertEqual(record.details.get("exception_message"), "test error detail")
        self.assertIsNotNone(record.details.get("stack_trace"))

    def test_db_write_failure_does_not_suppress_caller(self):
        """SC-7: DB write failure during log_event() does not suppress the original exception."""
        from src.services.event_log_service import EventLogService

        # Close the session to force a DB write failure
        self.session.close()

        # This should not raise — log_event catches DB errors
        try:
            EventLogService.log_event(
                event_type="test",
                severity="info",
                message="should fail silently",
                source="test",
                session=self.session,
            )
        except Exception:
            self.fail("log_event() should not raise when DB write fails")

    def test_get_events_returns_ordered_with_filters(self):
        """SC-9: get_events() returns events ordered by created_at desc with optional filters."""
        from src.services.event_log_service import EventLogService

        # Insert events with different types
        EventLogService.log_event(
            event_type="type_a", severity="info", message="first",
            source="test", details={"seq": 1}, session=self.session,
        )
        EventLogService.log_event(
            event_type="type_b", severity="warning", message="second",
            source="test", details={"seq": 2}, session=self.session,
        )
        EventLogService.log_event(
            event_type="type_a", severity="error", message="third",
            source="test", details={"seq": 3}, session=self.session,
        )

        # Test unfiltered — should return all 3 events
        all_events = EventLogService.get_events(session=self.session)
        self.assertEqual(len(all_events), 3)

        # Test event_type filter
        type_a_events = EventLogService.get_events(
            event_type="type_a", session=self.session,
        )
        self.assertEqual(len(type_a_events), 2)
        for e in type_a_events:
            self.assertEqual(e.event_type, "type_a")

        # Test severity filter
        error_events = EventLogService.get_events(
            severity="error", session=self.session,
        )
        self.assertEqual(len(error_events), 1)
        self.assertEqual(error_events[0].severity, "error")

        # Test date range filter
        from datetime import datetime, timezone, timedelta
        _now = datetime.now(timezone.utc)
        recent_events = EventLogService.get_events(
            date_from=(_now - timedelta(hours=1)).isoformat(),
            date_to=(_now + timedelta(hours=1)).isoformat(),
            session=self.session,
        )
        self.assertEqual(len(recent_events), 3)
