# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Behavioral tests for issue #1332 — persistent system event logging.

Covers SC-2 (log_event write), SC-3 (log_exception extraction), SC-4
(migration lifecycle events on an isolated DB), SC-5 (handle_ui_error writes
an exception event), SC-6 (stderr logging preserved), SC-7 (DB write failure
never suppresses the caller), SC-8 (handle_ui_error backward compatibility),
SC-9 (get_events ordering and filters).

Local-DB tests run against the prod-synced local database per the regression
protocol; SC-4 runs on an isolated ephemeral pgserver instance.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import unittest
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import text

from src.services.event_log_service import EventLogService


class _LocalDbTestCase(unittest.TestCase):
    """Base for tests against the prod-synced local DB (regression protocol)."""

    @classmethod
    def setUpClass(cls):  # noqa: N802
        from src.database.connection import get_session, init_db

        init_db()
        cls.get_session = staticmethod(get_session)

    @classmethod
    def tearDownClass(cls):
        from src.database.connection import get_session

        session = get_session()
        SystemEventLog = __import__("src.database.models.event_log", fromlist=["SystemEventLog"]).SystemEventLog
        session.query(SystemEventLog).filter(
            (SystemEventLog.event_type.in_(["_sc2_probe", "_sc9_probe"]))
            | (SystemEventLog.source.in_(["_sc3_probe_src", "_sc5_probe_src"]))
        ).delete(synchronize_session=False)
        session.commit()
        session.close()

    def _cleanup(self, event_type: str):
        from src.database.connection import get_session
        from src.database.models.event_log import SystemEventLog

        session = get_session()
        # SC-9 seeds rows of both probe types; 'other' rows must also be
        # removed so range-filter assertions stay stable across runs.
        session.query(SystemEventLog).filter(
            SystemEventLog.event_type.in_([event_type, "other"])
        ).delete(synchronize_session=False)
        session.commit()
        session.close()

    def _cleanup_by_source(self, source: str):
        from src.database.connection import get_session
        from src.database.models.event_log import SystemEventLog

        session = get_session()
        session.query(SystemEventLog).filter_by(source=source).delete(synchronize_session=False)
        session.commit()
        session.close()


class TestLogEventSc2(_LocalDbTestCase):
    """SC-2 (behavioral): log_event() writes a record with correct field values."""

    def test_log_event_persists_row(self):
        self._cleanup("_sc2_probe")
        EventLogService.log_event(
            event_type="_sc2_probe",
            severity="warning",
            message="SC-2 probe message",
            source="test_event_log",
            details={"key": "value", "n": 7},
        )
        from src.database.connection import get_session
        from src.database.models.event_log import SystemEventLog

        session = get_session()
        try:
            row = session.query(SystemEventLog).filter_by(event_type="_sc2_probe").one()
            self.assertEqual(row.severity, "warning")
            self.assertEqual(row.message, "SC-2 probe message")
            self.assertEqual(row.source, "test_event_log")
            self.assertEqual(row.details, {"key": "value", "n": 7})
            self.assertIsNotNone(row.created_at)
        finally:
            session.close()


class TestLogExceptionSc3(_LocalDbTestCase):
    """SC-3 (behavioral): log_exception() extracts type, message, stack trace."""

    def test_log_exception_writes_exception_event(self):
        self._cleanup_by_source("_sc3_probe_src")
        try:
            raise ValueError("SC-3 induced failure")
        except ValueError as e:
            EventLogService.log_exception(e, message="SC-3 context", source="_sc3_probe_src")

        from src.database.connection import get_session
        from src.database.models.event_log import SystemEventLog

        session = get_session()
        try:
            row = (
                session.query(SystemEventLog)
                .filter_by(event_type="exception", source="_sc3_probe_src")
                .one()
            )
            self.assertEqual(row.severity, "error")
            self.assertEqual(row.message, "SC-3 context")
            self.assertEqual(row.details["exception_type"], "ValueError")
            self.assertEqual(row.details["exception_message"], "SC-3 induced failure")
            self.assertIn("Traceback", row.details["traceback"])
            self.assertIn("ValueError", row.details["traceback"])
        finally:
            session.close()


class TestHandleUiErrorSc5Sc6Sc8(_LocalDbTestCase):
    """SC-5/SC-6/SC-8 (behavioral): handle_ui_error persistence + stderr + compat."""

    def test_handle_ui_error_writes_exception_event(self):
        self._cleanup_by_source("_sc5_probe_src")
        from src.database.connection import get_session
        from src.database.models.event_log import SystemEventLog
        from src.frontend.ui_utils import handle_ui_error

        try:
            raise RuntimeError("SC-5 induced UI error")
        except RuntimeError as e:
            handle_ui_error(e, user_message="SC-5 user message", logger_name="_sc5_probe_src")

        session = get_session()
        try:
            row = session.query(SystemEventLog).filter_by(event_type="exception", source="_sc5_probe_src").one()
            self.assertEqual(row.severity, "error")
            self.assertEqual(row.message, "SC-5 user message")
            self.assertEqual(row.details["exception_type"], "RuntimeError")
        finally:
            session.close()

    def test_stderr_logging_preserved_sc6(self):
        """SC-6: stderr/log output still emitted alongside the DB write."""
        import logging

        from src.frontend.ui_utils import handle_ui_error

        records: list[logging.LogRecord] = []

        class _Capture(logging.Handler):
            def emit(self, record):
                records.append(record)

        handler = _Capture(level=logging.ERROR)
        logger = logging.getLogger("_sc5_probe_src")
        logger.addHandler(handler)
        try:
            try:
                raise RuntimeError("SC-6 capture")
            except RuntimeError as e:
                handle_ui_error(e, user_message="SC-6 msg", logger_name="_sc5_probe_src")
        finally:
            logger.removeHandler(handler)

        self.assertTrue(any("SC-6 msg" in r.getMessage() and r.exc_info for r in records), records)

    def test_two_positional_args_backward_compatible_sc8(self):
        """SC-8: callers passing only (e, user_message) continue to work."""
        from src.frontend.ui_utils import handle_ui_error

        try:
            raise ValueError("SC-8 minimal call")
        except ValueError as e:
            result = handle_ui_error(e, "SC-8 user message")
        self.assertIsNone(result)


class TestDbWriteResilienceSc7(_LocalDbTestCase):
    """SC-7 (behavioral): a failed DB write never suppresses the caller."""

    def test_unusable_session_does_not_raise(self):
        class _ExplodingSession:
            def add(self, *_args, **_kwargs):
                raise RuntimeError("simulated DB outage")

            def rollback(self):
                pass

        EventLogService.log_event("exception", "error", "msg", session=_ExplodingSession())

    def test_bad_details_does_not_raise(self):
        # Non-serializable details must not propagate to the caller.
        EventLogService.log_event("exception", "error", "msg", details={"bad": object()})


class TestGetEventsSc9(_LocalDbTestCase):
    """SC-9 (behavioral): get_events ordering and filters."""

    def test_ordering_and_filters(self):
        self._cleanup("_sc9_probe")
        from src.database.connection import get_session
        from src.database.models.event_log import SystemEventLog

        session = get_session()
        try:
            base = datetime(2026, 10, 5, 12, 0, 0)
            session.add_all(
                [
                    SystemEventLog(
                        event_type="_sc9_probe", severity="info", message="old",
                        source="t", created_at=base,
                    ),
                    SystemEventLog(
                        event_type="_sc9_probe", severity="error", message="mid",
                        source="t", created_at=base + timedelta(minutes=5),
                    ),
                    SystemEventLog(
                        event_type="other", severity="info", message="other-type",
                        source="t", created_at=base + timedelta(minutes=9),
                    ),
                    SystemEventLog(
                        event_type="_sc9_probe", severity="error", message="new",
                        source="t", created_at=base + timedelta(minutes=10),
                    ),
                ]
            )
            session.commit()
        finally:
            session.close()

        # Ordering: created_at descending
        rows = EventLogService.get_events()
        created = [r.created_at for r in rows]
        self.assertEqual(created, sorted(created, reverse=True))

        # Filter: event_type
        probe_rows = EventLogService.get_events(event_type="_sc9_probe")
        self.assertEqual(len(probe_rows), 3)
        self.assertTrue(all(r.event_type == "_sc9_probe" for r in probe_rows))

        # Filter: severity
        error_rows = EventLogService.get_events(event_type="_sc9_probe", severity="error")
        self.assertEqual([r.message for r in error_rows], ["new", "mid"])

        # Filter: date range (inclusive bounds)
        range_rows = EventLogService.get_events(start=base + timedelta(minutes=5), end=base + timedelta(minutes=10))
        self.assertEqual([r.message for r in range_rows], ["new", "other-type", "mid"])


class TestMigrationLifecycleSc4(unittest.TestCase):
    """SC-4 (behavioral): migration lifecycle events on an isolated DB.

    A clean run asserts migration_start/migration_complete/migration_skip;
    an induced-failure run asserts migration_error. A single real run cannot
    produce all four (a synced replica has exactly one pending migration).
    """

    @classmethod
    def setUpClass(cls):  # noqa: N802
        try:
            import pgserver
            from sqlalchemy import create_engine
        except ImportError:
            raise unittest.SkipTest("pgserver not available") from None

        cls.test_db_path = Path("tmp/test_event_log_sc4_db")
        if cls.test_db_path.exists():
            import shutil

            shutil.rmtree(cls.test_db_path)
        cls.test_db_path.mkdir(parents=True, exist_ok=True)

        cls.pg_server = pgserver.get_server(str(cls.test_db_path))
        cls.engine = create_engine(cls.pg_server.get_uri())

        # pgvector extension must exist before creating ORM tables that use
        # the Vector type (records.embedding, gloss_search_entries.embedding).
        with cls.engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()

        # Register models (including SystemEventLog) and create the schema,
        # then backdate the applied-version row so one migration is pending.
        from src.database.base import Base
        from src.database.models.core import Record, Source  # noqa: F401
        from src.database.models.event_log import SystemEventLog  # noqa: F401
        from src.database.models.identity import User  # noqa: F401
        from src.database.models.meta import SchemaVersion  # noqa: F401
        from src.database.models.workflow import EditHistory  # noqa: F401

        Base.metadata.create_all(cls.engine)
        with cls.engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO schema_version (version, description) "
                    "VALUES (:v, 'SC-4 isolation baseline') ON CONFLICT DO NOTHING;"
                ),
                {"v": 20261005131326 - 1},
            )
            conn.commit()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "pg_server"):
            cls.pg_server.cleanup()
        if hasattr(cls, "test_db_path") and cls.test_db_path.exists():
            import shutil

            shutil.rmtree(cls.test_db_path)

    def test_clean_run_emits_start_complete_skip(self):
        from src.database.migrations import MigrationManager

        MigrationManager(self.engine).run_all()

        from src.services.event_log_service import EventLogService

        types = {e.event_type for e in EventLogService.get_events()}
        self.assertIn("migration_start", types)
        self.assertIn("migration_complete", types)
        self.assertIn("migration_skip", types)

    def test_induced_failure_emits_error(self):
        """A failing migration emits migration_error (stderr preserved, RISK-3)."""
        from unittest.mock import patch

        from src.database.migrations import MigrationManager

        # Re-open a migration window and make one migration fail.
        with self.engine.connect() as conn:
            conn.execute(text("DELETE FROM schema_version WHERE version > 20260615125509;"))
            conn.commit()

        with patch.object(
            MigrationManager,
            "_migrate_create_semantic_search_entries",
            side_effect=RuntimeError("SC-4 induced migration failure"),
        ):
            manager = MigrationManager(self.engine)
            with self.assertRaisesRegex(Exception, "SC-4 induced migration failure"):
                manager._run_migrations()

        from src.services.event_log_service import EventLogService

        error_events = EventLogService.get_events(event_type="migration_error")
        self.assertTrue(error_events, "expected a migration_error event from the induced failure")
        self.assertIn("SC-4 induced migration failure", error_events[0].details["error_message"])


if __name__ == "__main__":
    unittest.main()
