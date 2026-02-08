"""
AI Agent Instructions:
- **ANTI-"VIBE" CODING:** This is NOT a "VIBE" coding project. Avoid "VIBE" coding with prejudice.
- **Human Review:** ALL code changes MUST be reviewed by the Human Lead.
- Source of truth for database schema: docs/database/DATABASE_SPECIFICATION.md
- All SQLAlchemy models in this directory MUST reflect the schema defined in that document.
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..base import Base

class MatchupQueue(Base):
    """
    Staging area for uploaded MDF data requiring manual matching.
    Isolates sessions by user and source.
    """
    __tablename__ = 'matchup_queue'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String, ForeignKey('users.email', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    suggested_record_id = Column(Integer, ForeignKey('records.id'))  # Potential match
    status = Column(String, nullable=False, default='pending')  # 'pending', 'matched', 'ignored'
    lx = Column(String)  # Uploaded Lexeme
    mdf_data = Column(Text, nullable=False)  # Raw uploaded entry
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    source = relationship("Source", back_populates="matchup_entries")
    suggested_record = relationship("Record", back_populates="matchup_suggestions")
    user = relationship("User", back_populates="matchup_entries")

class EditHistory(Base):
    """
    Versioned audit trail for record changes.
    Tracks snapshot-based history for rollback and accountability.
    """
    __tablename__ = 'edit_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey('records.id', ondelete='RESTRICT'), nullable=False)
    user_email = Column(String, ForeignKey('users.email', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    session_id = Column(String)  # Unique UUID per upload/edit batch
    version = Column(Integer, nullable=False)
    change_summary = Column(Text)
    prev_data = Column(Text)  # MDF snapshot before change
    current_data = Column(Text, nullable=False)  # MDF snapshot after change
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    record = relationship("Record", back_populates="history")
    user = relationship("User", back_populates="edit_history")
