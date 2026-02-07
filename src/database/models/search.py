"""
AI Agent Instructions:
- Source of truth for database schema: docs/database/DATABASE_SPECIFICATION.md
- All SQLAlchemy models in this directory MUST reflect the schema defined in that document.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..base import Base

class SearchEntry(Base):
    """
    Consolidated lookup table for instant search across all linguistic forms.
    Indexed using GIN Trigram (pg_trgm) for fragment matching.
    """
    __tablename__ = 'search_entries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey('records.id'), nullable=False)
    term = Column(String, nullable=False)  # The searchable form (\lx, \va, \se, etc.)
    entry_type = Column(String, nullable=False)  # Origin tag: 'lx', 'va', 'se', 'cf', 've'
    
    record = relationship("Record", back_populates="search_entries")
