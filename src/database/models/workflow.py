# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..base import Base

class MatchupQueue(Base):
    """
    Staging area for uploaded MDF data requiring manual matching.
    Isolates sessions by user and source.

    Attributes:
        id (int): Primary key.
        user_email (str): FK to users table, session owner.
        source_id (int): FK to sources table, target collection.
        suggested_record_id (int): Optional FK to an existing potential match in records.
        batch_id (str): UUID identifying a specific upload batch.
        filename (str): Name of the original uploaded file.
        status (str): Queue state ('pending', 'matched', 'ignored').
        lx (str): Uploaded lexeme for suggestion logic.
        mdf_data (str): Full raw uploaded MDF entry.
        match_type (str): Logic used for suggestion ('exact', 'base_form').
        created_at (datetime): Timestamp of upload.
    """
    __tablename__ = 'matchup_queue'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String, ForeignKey('users.email', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    source_id = Column(Integer, ForeignKey('sources.id', ondelete='RESTRICT'), nullable=False)
    suggested_record_id = Column(Integer, ForeignKey('records.id', ondelete='RESTRICT'))  # Potential match
    batch_id = Column(String, nullable=False)  # UUID identifying the upload batch
    filename = Column(String)  # Original upload filename for display
    status = Column(String, nullable=False, default='pending')  # 'pending', 'matched', 'ignored'
    lx = Column(String)  # Uploaded Lexeme
    mdf_data = Column(Text, nullable=False)  # Raw uploaded entry
    match_type = Column(String)  # 'exact' or 'base_form'; set by suggest_matches
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
