# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""
Event Log Service for persistent system event logging (issue #1332).

Unified entry point for writing non-user-activity system events (exceptions,
migration lifecycle, application lifecycle, infrastructure notifications) to
the ``system_event_log`` table. Follows the ``AuditService.log_activity()``
pattern: static methods, optional session injection, error-safe commit that
never suppresses the caller's exception (REQ-8 / SC-7).
"""

import traceback

from src.database.connection import get_session
from src.database.models.event_log import SystemEventLog
from src.logging_config import get_logger

logger = get_logger("snea.event_log")


class EventLogService:
    """
    Service for centralizing persistent system event logging.

    All system events (exception, migration_start, migration_skip,
    migration_complete, migration_error, system_startup, system_shutdown,
    infrastructure) should be recorded through this service.
    """

    @staticmethod
    def log_event(
        event_type: str,
        severity: str,
        message: str,
        source: str | None = None,
        details: dict | None = None,
        session=None,
    ) -> None:
        """
        Persist a system event to the ``system_event_log`` table.

        DB write failures are swallowed and logged to stderr — the caller's
        flow is never interrupted by a failed event write (REQ-8).

        Args:
            event_type: Event discriminator (e.g., 'exception', 'migration_start').
            severity: One of 'info', 'warning', 'error', 'critical'.
            message: Human-readable summary.
            source: Optional module or component name.
            details: Optional structured context (stored as JSONB).
            session: Optional existing database session. If provided, the event
                is added to this session and not committed.
        """
        _provided_session = session is not None
        if not _provided_session:
            session = get_session()
        try:
            event = SystemEventLog(
                event_type=event_type,
                severity=severity,
                message=message,
                source=source,
                details=details,
            )
            session.add(event)
            if not _provided_session:
                session.commit()
        except Exception as e:
            if not _provided_session:
                try:
                    session.rollback()
                except Exception:
                    pass
            logger.error("Failed to persist system event '%s': %s", event_type, e)
        finally:
            if not _provided_session:
                try:
                    session.close()
                except Exception:
                    pass

    @staticmethod
    def log_exception(
        e: Exception,
        message: str | None = None,
        source: str | None = None,
        session=None,
    ) -> None:
        """
        Convenience wrapper: record an ``exception``-type event from an
        Exception object. Extracts the exception type, message, and stack
        trace into ``details`` (REQ-5 / SC-3).

        Args:
            e: The exception that occurred.
            message: Optional human-readable summary; defaults to str(e).
            source: Optional module or component name.
            session: Optional existing database session.
        """
        details = {
            "exception_type": type(e).__name__,
            "exception_message": str(e),
            "traceback": "".join(traceback.format_exception(type(e), e, e.__traceback__)),
        }
        EventLogService.log_event(
            event_type="exception",
            severity="error",
            message=message if message is not None else str(e),
            source=source,
            details=details,
            session=session,
        )

    @staticmethod
    def get_events(
        event_type: str | None = None,
        severity: str | None = None,
        start=None,
        end=None,
        session=None,
    ) -> list[SystemEventLog]:
        """
        Query persisted events, ordered by ``created_at`` descending (REQ-13 / SC-9).

        Args:
            event_type: Optional filter on the event discriminator.
            severity: Optional filter on severity.
            start: Optional inclusive lower bound on ``created_at``.
            end: Optional inclusive upper bound on ``created_at``.
            session: Optional existing database session. If provided, the
                caller owns the transaction; results are materialized.
        """
        _provided_session = session is not None
        if not _provided_session:
            session = get_session()
        try:
            query = session.query(SystemEventLog)
            if event_type is not None:
                query = query.filter(SystemEventLog.event_type == event_type)
            if severity is not None:
                query = query.filter(SystemEventLog.severity == severity)
            if start is not None:
                query = query.filter(SystemEventLog.created_at >= start)
            if end is not None:
                query = query.filter(SystemEventLog.created_at <= end)
            return query.order_by(SystemEventLog.created_at.desc()).all()
        finally:
            if not _provided_session:
                session.close()
