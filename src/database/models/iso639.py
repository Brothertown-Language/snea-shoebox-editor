# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
from sqlalchemy import Column, Integer, String, TIMESTAMP, Text
from sqlalchemy.sql import func
from ..base import Base

class ISO639_3(Base):
    """
    Reference table for ISO 639-3 language codes.
    Seeded from https://iso639-3.sil.org/sites/iso639-3/files/downloads/iso-639-3.tab
    """
    __tablename__ = 'iso_639_3'
    
    # The 'Id' column in the tab file is the 3-letter code
    id = Column(String(3), primary_key=True)
    part2b = Column(String(3))
    part2t = Column(String(3))
    part1 = Column(String(2))
    scope = Column(String(1))
    language_type = Column(String(1))
    ref_name = Column(String, nullable=False)
    comment = Column(Text)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
