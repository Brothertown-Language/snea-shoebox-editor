# Copyright (c) 2026 Brothertown Language
"""
Audit Service for standardizing user activity logging.
"""
from typing import Optional
from src.database import get_session, UserActivityLog


class AuditService:
    """
    Service for centralizing activity logging across the application.
    All user actions (login, logout, data changes, etc.) should be logged through this service.
    """

    @staticmethod
    def log_activity(user_email: str, action: str, details: Optional[str] = None) -> None:
        """
        Log a user activity to the database.

        Args:
            user_email: The email of the user performing the action.
            action: A short action identifier (e.g., 'login', 'logout', 'record_update').
            details: Optional human-readable description of the activity.
        """
        session = get_session()
        try:
            log = UserActivityLog(
                user_email=user_email,
                action=action,
                details=details
            )
            session.add(log)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Failed to log user activity: {e}", flush=True)
        finally:
            session.close()
