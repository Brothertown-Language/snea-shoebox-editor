# Copyright (c) 2026 Brothertown Language
# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""
Event Log Service for persisting system-level events to the system_event_log table.

Co-authored with AI: OpenCode (ollama-cloud/deepseek-v4-flash)
"""

import traceback

from sqlalchemy import and_, desc
from sqlalchemy.exc import ProgrammingError

from src.database.connection import get_session
from src.database.models.event_log import SystemEventLog
from src.logging_config import get_logger

logger = get_logger("snea.event_log")


class EventLogService:
    """
    Service for persisting system-level events (exceptions, migration lifecycle,
    application lifecycle, infrastructure notifications) to the system_event_log table.
    """

    @staticmethod
    def log_event(
        event_type: str,
        severity: str,
        message: str,
        source: str,
        details: dict | None = None,
        session=None,
    ) -> None:
        """
        Write a system event to the system_event_log table.

        Args:
            event_type: Discriminator for the event category.
            severity: Severity level ('info', 'warning', 'error', 'critical').
            message: Human-readable summary of the event.
            source: Module or component name that generated the event.
            details: Optional structured context as a dict (stored as JSONB).
            session: Optional existing database session.
        """
        _provided_session = session is not None
        if not _provided_session:
            session = get_session()
        try:
            log = SystemEventLog(
                event_type=event_type,
                severity=severity,
                message=message,
                source=source,
                details=details or {},
            )
            session.add(log)
            if not _provided_session:
                session.commit()
        except ProgrammingError:
            # Table doesn't exist yet (called from a migration that predates
            # the system_event_log table). Rollback to clear session state
            # but don't suppress the caller's exception.
            session.rollback()
            logger.warning("system_event_log table not available yet — event not persisted")
        except Exception as e:
            if not _provided_session:
                session.rollback()
            logger.error("Failed to log system event: %s", e)
        finally:
            if not _provided_session:
                session.close()

    @staticmethod
    def log_exception(e: Exception, source: str | None = None, session=None) -> None:
        """
        Log an exception as a system event.

        Extracts the exception type, message, and stack trace from the exception
        and writes an 'exception'-type event via log_event().

        Args:
            e: The exception to log.
            source: Optional source component name.
            session: Optional existing database session.
        """
        details = {
            "exception_type": type(e).__name__,
            "exception_message": str(e),
            "stack_trace": traceback.format_exc(),
        }
        EventLogService.log_event(
            event_type="exception",
            severity="error",
            message=f"{type(e).__name__}: {str(e)}",
            source=source or "exception_handler",
            details=details,
            session=session,
        )

    @staticmethod
    def get_events(
        event_type: str | None = None,
        severity: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int = 100,
        session=None,
    ) -> list[SystemEventLog]:
        """
        Retrieve system events ordered by created_at descending.

        Args:
            event_type: Optional filter by event type.
            severity: Optional filter by severity level.
            date_from: Optional filter for events on or after this date (ISO 8601).
            date_to: Optional filter for events on or before this date (ISO 8601).
            limit: Maximum number of events to return (default 100).
            session: Optional existing database session.

        Returns:
            List of SystemEventLog instances ordered by created_at descending.
        """
        _provided_session = session is not None
        if not _provided_session:
            session = get_session()
        try:
            query = session.query(SystemEventLog)

            filters = []
            if event_type is not None:
                filters.append(SystemEventLog.event_type == event_type)
            if severity is not None:
                filters.append(SystemEventLog.severity == severity)
            if date_from is not None:
                filters.append(SystemEventLog.created_at >= date_from)
            if date_to is not None:
                filters.append(SystemEventLog.created_at <= date_to)

            if filters:
                query = query.filter(and_(*filters))

            return query.order_by(desc(SystemEventLog.created_at)).limit(limit).all()
        finally:
            if not _provided_session:
                session.close()
