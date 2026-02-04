# Copyright (c) 2026 Brothertown Language
"""
AI Coding Defaults:
- Strict Typing: Mandatory for all function signatures and variable declarations.
- Lazy Initialization: Imports inside functions for Streamlit pages to optimize loading.
- Single Responsibility: Each function/method must have one clear purpose.
- Standalone Execution: Page files must include a main execution block.
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, Index, text
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
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    citation_format = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    records = relationship("Record", back_populates="source")

class Record(Base):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    lx = Column(String, nullable=False)
    ps = Column(String)
    ge = Column(String)
    mdf_data = Column(Text, nullable=False)
    status = Column(String, nullable=False, default='draft')
    source_page = Column(String)
    current_version = Column(Integer, nullable=False, default=1)
    is_deleted = Column(Boolean, nullable=False, default=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(String)
    reviewed_at = Column(TIMESTAMP(timezone=True))
    reviewed_by = Column(String)
    
    source = relationship("Source", back_populates="records")
    history = relationship("EditHistory", back_populates="record")

class EditHistory(Base):
    __tablename__ = 'edit_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey('records.id', ondelete='CASCADE'), nullable=False)
    version = Column(Integer, nullable=False)
    prev_data = Column(Text)
    current_data = Column(Text, nullable=False)
    user_id = Column(String, nullable=False)
    change_summary = Column(Text)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    record = relationship("Record", back_populates="history")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    github_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    name = Column(String)
    last_login = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class UserActivityLog(Base):
    __tablename__ = 'user_activity_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    action = Column(String, nullable=False)
    details = Column(Text)
    ip_address = Column(String)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey('sources.id', ondelete='CASCADE'))
    github_org = Column(String, nullable=False)
    github_team = Column(String)
    role = Column(String, nullable=False, default='viewer')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

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
        conn.commit()
    
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
