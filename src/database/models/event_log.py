# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""
SystemEventLog model for persistent system event logging.

Co-authored with AI: OpenCode (ollama-cloud/deepseek-v4-flash)
"""
from sqlalchemy import TIMESTAMP, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from ..base import Base


class SystemEventLog(Base):
    """
    Persistent log of system-level events for offline analysis.
    Uses event_type as a discriminator for different event categories.
    """

    __tablename__ = "system_event_log"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=False)
    source = Column(String, nullable=False)
    details = Column(JSONB, nullable=False, server_default="{}")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
