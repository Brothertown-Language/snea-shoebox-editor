# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""
Audit Service for standardizing user activity logging.
"""
from typing import Optional
from src.database import get_session, UserActivityLog
from src.logging_config import get_logger

logger = get_logger("snea.audit")


class AuditService:
    """
    Service for centralizing activity logging across the application.
    All user actions (login, logout, data changes, etc.) should be logged through this service.
    """

    @staticmethod
    def log_activity(user_email: str, action: str, details: Optional[str] = None, session_id: Optional[str] = None, session=None) -> None:
        """
        Log a user activity to the database.

        Args:
            user_email: The email of the user performing the action.
            action: A short action identifier (e.g., 'login', 'logout', 'record_update').
            details: Optional human-readable description of the activity.
            session_id: Optional UUID linking activity to a specific edit/upload batch.
            session: Optional existing database session. If provided, the log will be added to this session and not committed.
        """
        _provided_session = session is not None
        if not _provided_session:
            session = get_session()
        try:
            log = UserActivityLog(
                user_email=user_email,
                session_id=session_id,
                action=action,
                details=details
            )
            session.add(log)
            if not _provided_session:
                session.commit()
        except Exception as e:
            if not _provided_session:
                session.rollback()
            logger.error("Failed to log user activity: %s", e)
        finally:
            if not _provided_session:
                session.close()
