# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..base import Base

class SearchEntry(Base):
    """
    Consolidated lookup table for instant search across all linguistic forms.
    Indexed for fast lookup; utilizes standard ILIKE matching to remain compatible 
    with the pgserver envelope.
    """
    __tablename__ = 'search_entries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey('records.id', ondelete='RESTRICT'), nullable=False)
    term = Column(String, nullable=False)  # The searchable form (\lx, \va, \se, etc.)
    entry_type = Column(String, nullable=False)  # Origin tag: 'lx', 'va', 'se', 'cf', 've'
    
    record = relationship("Record", back_populates="search_entries")
