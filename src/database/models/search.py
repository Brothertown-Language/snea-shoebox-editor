# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship

from ..base import Base


class FTSEntry(Base):
    """
    Full-text search entries for FTS mode.
    Populated by application code using generate_sort_lx() normalization
    and to_tsvector('simple', ...) to avoid English stemming on Algonquian text.
    """

    __tablename__ = "fts_entries"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    record_id = Column(Integer, ForeignKey("records.id", ondelete="CASCADE"), nullable=False, index=True)
    fts_vector = Column(TSVECTOR, nullable=False)

    record = relationship("Record", back_populates="fts_entry")


class SearchEntry(Base):
    """
    Consolidated lookup table for instant search across all linguistic forms.
    Indexed for fast lookup; utilizes standard ILIKE matching to remain compatible
    with the pgserver envelope.
    """

    __tablename__ = "search_entries"
    __table_args__ = {"extend_existing": True}  # Required: prevents re-import errors on Streamlit hot-reload
    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey("records.id", ondelete="RESTRICT"), nullable=False)
    term = Column(String, nullable=False)  # The searchable form (\lx, \va, \se, etc.)
    normalized_term = Column(String, nullable=False)  # Normalized for punctuation-insensitive prefix search
    entry_type = Column(String, nullable=False)  # Origin tag: 'lx', 'va', 'se', 'cf', 've'

    record = relationship("Record", back_populates="search_entries")


class HeadwordSearchEntry(Base):
    """
    Headword-level entries only: PRIMARY lx and PRIMARY va.
    Populated during MDF parsing with state tracking.
    """

    __tablename__ = "headword_search_entries"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey("records.id", ondelete="RESTRICT"), nullable=False)
    entry_type = Column(String, nullable=False)  # 'lx' or 'va' only; enforced by CHECK constraint at DB level
    term = Column(String, nullable=False)
    normalized_term = Column(String, nullable=False)

    record = relationship("Record", back_populates="headword_entries")


class GlossSearchEntry(Base):
    """
    Primary gloss entries only: PRIMARY ge.
    Populated during MDF parsing with state tracking.
    """

    __tablename__ = "gloss_search_entries"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey("records.id", ondelete="RESTRICT"), nullable=False)
    term = Column(String, nullable=False)
    normalized_term = Column(String, nullable=False)

    record = relationship("Record", back_populates="gloss_entries")
