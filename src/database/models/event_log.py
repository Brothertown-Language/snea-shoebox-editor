# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""
SystemEventLog model — persistent system event logging (issue #1332).

Unified table for non-user-activity system events (exceptions, migration
lifecycle, application lifecycle, infrastructure notifications) with an
``event_type`` discriminator and structured JSONB context. Deliberately
separate from ``user_activity_log`` (different retention and query patterns).
"""

from sqlalchemy import TIMESTAMP, Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from src.database.base import Base


class SystemEventLog(Base):
    """
    A single system event: exception, migration lifecycle, application
    lifecycle, or infrastructure notification.

    See issue #1332 (spec rev 4) for the requirements this table implements.
    """

    __tablename__ = "system_event_log"
    __table_args__ = {"extend_existing": True}  # Required: prevents re-import errors on Streamlit hot-reload

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String, nullable=False)  # e.g., 'exception', 'migration_start', 'migration_error'
    severity = Column(String, nullable=False)  # e.g., 'info', 'warning', 'error', 'critical'
    message = Column(Text, nullable=False)  # human-readable summary
    source = Column(String)  # module or component name
    details = Column(JSONB)  # structured context (JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
