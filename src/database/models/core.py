# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from ..base import Base

class Source(Base):
    """
    Lookup table for high-level source collections (e.g., 'Natick/Trumbull').
    Managed via reference data seeding and administrative UI.
    """
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)  # Full name e.g., 'Natick/Trumbull'
    short_name = Column(String)  # Abbreviation for UI display
    description = Column(Text)
    citation_format = Column(Text)  # Rule for generating standard citations
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    records = relationship("Record", back_populates="source")
    matchup_entries = relationship("MatchupQueue", back_populates="source")

class Language(Base):
    """
    Lookup table for valid language codes and display names.
    Ensures consistency across entries and provides dropdown data.
    """
    __tablename__ = 'languages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False)  # ISO or project code
    name = Column(String, nullable=False)  # Display name
    description = Column(Text)
    
    records = relationship("Record", secondary="record_languages", back_populates="language")

class RecordLanguage(Base):
    """
    Auxiliary join table to support 1-record-to-many-languages.
    """
    __tablename__ = 'record_languages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey('records.id', ondelete='CASCADE'), nullable=False)
    language_id = Column(Integer, ForeignKey('languages.id', ondelete='RESTRICT'), nullable=False)
    is_primary = Column(Boolean, nullable=False, default=False)

class Record(Base):
    """
    The source of truth for all linguistic entries.
    Organized for human readability in SQL viewers, prioritizing linguistic fields.
    Linked to raw MDF data via \\nt Record: <id> sync logic.

    Attributes:
        id (int): Primary key, synchronized with \\nt Record: <id> in raw MDF.
        lx (str): Lexeme headword (\\lx).
        hm (int): Homonym number (\\hm), defaults to 1.
        ps (str): Part of Speech (\\ps).
        ge (str): English Gloss (\\ge).
        source_id (int): FK to sources table.
        source_page (str): Specific citation or page number (\\so).
        status (str): Workflow state ('draft', 'edited', 'approved').
        embedding (Vector): 1536-dim semantic vector for cross-reference lookup.
        mdf_data (str): Full raw MDF text block.
        current_version (int): Optimistic locking version number.
        is_deleted (bool): Soft delete flag.
        updated_at (datetime): Automated timestamp of last modification.
        updated_by (str): Email of the last user who edited the record.
        reviewed_at (datetime): Timestamp of the last approval/review.
        reviewed_by (str): Email of the reviewer who approved the record.
    """
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True, autoincrement=True)  # Matches \nt Record: <id>
    lx = Column(String, nullable=False)  # Lexeme (\lx)
    sort_lx = Column(String)  # Normalized headword for sorting
    hm = Column(Integer, default=1)  # Homonym Number (\hm)
    ps = Column(String)  # Part of Speech (\ps)
    ge = Column(String)  # English Gloss (\ge)
    source_id = Column(Integer, ForeignKey('sources.id', ondelete='RESTRICT'), nullable=False)
    source_page = Column(String)  # Specific citation detail (\so)
    status = Column(String, nullable=False, default='draft')  # 'draft', 'edited', 'approved'
    embedding = Column(Vector(1536))  # Semantic cross-reference
    mdf_data = Column(Text, nullable=False)  # Raw MDF body
    
    # Audit & Workflow fields
    current_version = Column(Integer, nullable=False, default=1)
    is_deleted = Column(Boolean, nullable=False, default=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(String, ForeignKey('users.email', ondelete='RESTRICT', onupdate='CASCADE'))  # Identifier (email) of last editor
    reviewed_at = Column(TIMESTAMP(timezone=True))
    reviewed_by = Column(String, ForeignKey('users.email', ondelete='RESTRICT', onupdate='CASCADE'))
    
    language = relationship("Language", secondary="record_languages", back_populates="records")
    source = relationship("Source", back_populates="records")
    history = relationship("EditHistory", back_populates="record")
    search_entries = relationship("SearchEntry", back_populates="record")
    matchup_suggestions = relationship("MatchupQueue", back_populates="suggested_record")

    __mapper_args__ = {
        "version_id_col": current_version,
    }
