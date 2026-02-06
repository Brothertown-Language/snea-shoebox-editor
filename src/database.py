# Copyright (c) 2026 Brothertown Language
"""
CRITICAL MAINTENANCE RULES:
1. Tables must NEVER be dropped and recreated in this file. 
2. All schema updates must be non-destructive (use ALTER TABLE via migration logic).
3. Always verify against DATABASE_SPECIFICATION.md before modifying any model.

AI Coding Defaults:
- Strict Typing: Mandatory for all function signatures and variable declarations.
- Lazy Initialization: Imports inside functions for Streamlit pages to optimize loading.
- Single Responsibility: Each function/method must have one clear purpose.
- Standalone Execution: Page files must include a main execution block.
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.sql import func
import os
import streamlit as st
from pathlib import Path
import atexit
import getpass

# Global variable to hold the pgserver instance if auto-started
_pg_server = None

def _get_local_db_path():
    """Get the path to the local database directory."""
    project_root = Path(__file__).parent.parent
    return project_root / "tmp" / "local_db"

def _stop_local_db():
    """Stop the local database if it was auto-started."""
    global _pg_server
    if _pg_server:
        try:
            _pg_server.cleanup()
            _pg_server = None
        except Exception:
            pass

def is_production():
    """Detect if the application is running in the production environment (Streamlit Cloud)."""
    # Streamlit Cloud always runs apps under the Linux user 'appuser'.
    # This is a widely used community workaround for production detection.
    try:
        import getpass
        return getpass.getuser() == "appuser"
    except Exception:
        # Fallback to local if user cannot be determined
        return False

def _auto_start_pgserver():
    """Try to auto-start pgserver for local development."""
    global _pg_server
    
    # Safety check: NEVER start pgserver in production
    if is_production():
        return None

    try:
        import pgserver
        db_path = _get_local_db_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        _pg_server = pgserver.get_server(str(db_path))
        uri = _pg_server.get_uri()
        
        # Ensure pgvector extension is enabled automatically for local dev
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(uri)
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
        except Exception as e:
            # We don't want to block startup if this fails, but it should be logged
            if not is_production():
                st.warning(f"Could not automatically enable pgvector: {e}")
        
        # Register cleanup on exit
        atexit.register(_stop_local_db)
        
        return uri
    except ImportError:
        # pgserver not installed (likely production or not in dev group)
        return None
    except Exception as e:
        # Only warn if not in production and import succeeded but start failed
        if not is_production():
            st.warning(f"Failed to auto-start local PostgreSQL: {e}")
        return None

Base = declarative_base()

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

class SearchEntry(Base):
    """
    Consolidated lookup table for instant search across all linguistic forms.
    Indexed using GIN Trigram (pg_trgm) for fragment matching.
    """
    __tablename__ = 'search_entries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey('records.id', ondelete='CASCADE'), nullable=False)
    term = Column(String, nullable=False)  # The searchable form (\lx, \va, \se, etc.)
    entry_type = Column(String, nullable=False)  # Origin tag: 'lx', 'va', 'se', 'cf', 've'
    
    record = relationship("Record", back_populates="search_entries")

class MatchupQueue(Base):
    """
    Staging area for uploaded MDF data requiring manual matching.
    Isolates sessions by user and source.
    """
    __tablename__ = 'matchup_queue'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String, ForeignKey('users.email'), nullable=False)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    suggested_record_id = Column(Integer, ForeignKey('records.id'))  # Potential match
    status = Column(String, nullable=False, default='pending')  # 'pending', 'matched', 'ignored'
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
    record_id = Column(Integer, ForeignKey('records.id', ondelete='CASCADE'), nullable=False)
    user_email = Column(String, ForeignKey('users.email'), nullable=False)
    session_id = Column(String)  # Unique UUID per upload/edit batch
    version = Column(Integer, nullable=False)
    change_summary = Column(Text)
    prev_data = Column(Text)  # MDF snapshot before change
    current_data = Column(Text, nullable=False)  # MDF snapshot after change
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    record = relationship("Record", back_populates="history")
    user = relationship("User", back_populates="edit_history")

class User(Base):
    """
    User identity and metadata linked to GitHub authentication.
    Uses email as the primary logical identifier for cross-session audit trails.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)  # Primary logic key
    username = Column(String, unique=True, nullable=False)  # GitHub handle
    github_id = Column(Integer, unique=True, nullable=False)
    name = Column(String)  # Full name for attribution
    last_login = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    metadata = Column(JSONB)  # Extended data/preferences
    
    edit_history = relationship("EditHistory", back_populates="user")
    activity_logs = relationship("UserActivityLog", back_populates="user")
    matchup_entries = relationship("MatchupQueue", back_populates="user")

class UserActivityLog(Base):
    """
    General security and usage audit log.
    Tracks logins, sync sessions, and critical administrative actions.
    """
    __tablename__ = 'user_activity_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String, ForeignKey('users.email', ondelete='CASCADE'), nullable=False)
    session_id = Column(String)  # Unique UUID linking activity to a specific edit batch
    action = Column(String, nullable=False)  # e.g., 'login', 'sync_start', 'batch_rollback'
    details = Column(Text)
    ip_address = Column(String)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="activity_logs")

class Permission(Base):
    """
    Access control mapping between GitHub Teams and application roles.
    Defines who can view or edit specific sources.
    """
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey('sources.id', ondelete='CASCADE'))  # NULL = all
    github_org = Column(String, nullable=False)
    github_team = Column(String)  # NULL = all org members
    role = Column(String, nullable=False, default='viewer')  # 'admin', 'editor', 'viewer'
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class SchemaVersion(Base):
    """
    Tracks the current version of the database schema.
    Used to ensure non-destructive updates and manage migrations.
    """
    __tablename__ = 'schema_version'
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(Integer, nullable=False)
    applied_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    description = Column(Text)

def get_db_url():
    """Get database URL from Streamlit secrets or environment variables."""
    # 1. If we are in local dev, prioritize auto-starting pgserver
    # to avoid accidentally using production secrets from .streamlit/secrets.toml
    # or DATABASE_URL environment variable if it happens to be set to prod.
    if not is_production():
        auto_url = _auto_start_pgserver()
        if auto_url:
            # Set environment variable so other parts of the app can use it
            os.environ["DATABASE_URL"] = auto_url
            return auto_url

    # 2. Check environment variable
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    # 3. Check Streamlit secrets (Production fallback)
    try:
        if "connections" in st.secrets and "postgresql" in st.secrets["connections"]:
            url = st.secrets["connections"]["postgresql"]["url"]
            if url:
                return url
    except Exception:
        pass
    
    return None

def init_db():
    """Initialize the database schema."""
    db_url = get_db_url()
    if not db_url:
        raise ValueError("Database URL not found in secrets or environment.")
    
    engine = create_engine(db_url)
    
    # Ensure extensions are enabled
    with engine.connect() as conn:
        # Create vector extension for semantic search support
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        # Create pg_trgm extension for linguistic substring matching
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        conn.commit()
    
    # Base.metadata.create_all is non-destructive for existing tables
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """Get a new database session."""
    db_url = get_db_url()
    if not db_url:
        raise ValueError("Database URL not found in secrets or environment.")
    
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()
