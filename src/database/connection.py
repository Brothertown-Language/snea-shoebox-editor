"""
Database connection and session management.

AI Agent Instructions:
- Source of truth for database schema: docs/database/DATABASE_SPECIFICATION.md
- Ensure all queries and interactions align with the specified schema.
"""
import os
import streamlit as st
from pathlib import Path
import atexit
import getpass
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .base import Base

# Global variable to hold the pgserver instance if auto-started
_pg_server = None

def _get_local_db_path():
    """Get the path to the local database directory."""
    project_root = Path(__file__).parent.parent.parent
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
        # Create vector extension for semantic cross-reference support
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    
    # Base.metadata.create_all is non-destructive for existing tables
    Base.metadata.create_all(engine)
    
    # Add embedding column if it doesn't exist (manual migration for now)
    # Note: In a full production app, we would use Alembic.
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE records ADD COLUMN IF NOT EXISTS embedding vector(1536);"))
            conn.commit()
        except Exception as e:
            # We log the error but don't stop the whole app from starting, 
            # though the specific feature will be broken.
            if not is_production():
                st.error(f"Failed to add 'embedding' vector column: {e}")
            else:
                # In production, we should probably know about this
                print(f"ERROR: Failed to add 'embedding' vector column: {e}")
            
    return engine

def get_session():
    """Get a new database session."""
    db_url = get_db_url()
    if not db_url:
        raise ValueError("Database URL not found in secrets or environment.")
    
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()
