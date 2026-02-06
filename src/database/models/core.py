# Copyright (c) 2026 Brothertown Language
"""
DATABASE SOURCE OF TRUTH: docs/database/DATABASE_SPECIFICATION.md
"""
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
    
    records = relationship("Record", back_populates="language")

class Record(Base):
    """
    The source of truth for all linguistic entries.
    Organized for human readability in SQL viewers, prioritizing linguistic fields.
    Linked to raw MDF data via \nt Record: <id> sync logic.
    """
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True, autoincrement=True)  # Matches \nt Record: <id>
    lx = Column(String, nullable=False)  # Lexeme (\lx)
    hm = Column(Integer, default=1)  # Homonym Number (\hm)
    ps = Column(String)  # Part of Speech (\ps)
    ge = Column(String)  # English Gloss (\ge)
    language_id = Column(Integer, ForeignKey('languages.id'), nullable=False)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    source_page = Column(String)  # Specific citation detail (\so)
    status = Column(String, nullable=False, default='draft')  # 'draft', 'edited', 'approved'
    embedding = Column(Vector(1536))  # Semantic cross-reference
    mdf_data = Column(Text, nullable=False)  # Raw MDF body
    
    # Audit & Workflow fields
    current_version = Column(Integer, nullable=False, default=1)
    is_deleted = Column(Boolean, nullable=False, default=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(String)  # Identifier (email/ID) of last editor
    reviewed_at = Column(TIMESTAMP(timezone=True))
    reviewed_by = Column(String)
    
    language = relationship("Language", back_populates="records")
    source = relationship("Source", back_populates="records")
    history = relationship("EditHistory", back_populates="record")
    search_entries = relationship("SearchEntry", back_populates="record", cascade="all, delete-orphan")
    matchup_suggestions = relationship("MatchupQueue", back_populates="suggested_record")
