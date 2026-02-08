# Copyright (c) 2026 Brothertown Language
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
    
    # Junie separation: Use a dedicated path if JUNIE_PRIVATE_DB is set
    if os.getenv("JUNIE_PRIVATE_DB") == "true":
        return project_root / "tmp" / "junie_db"
        
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
        from sqlalchemy import create_engine, text
        engine = create_engine(uri)
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
        
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
    
    # Seed default permissions if table is empty
    seed_default_permissions(engine)
    
    # Seed ISO 639-3 data if table is empty
    seed_iso_639_data(engine)
    
    # Manual migration to add ON UPDATE CASCADE to user_email foreign keys
    # This is necessary because GitHub email addresses can change.
    with engine.connect() as conn:
        # 1. user_activity_log
        conn.execute(text("ALTER TABLE user_activity_log DROP CONSTRAINT IF EXISTS user_activity_log_user_email_fkey;"))
        conn.execute(text("ALTER TABLE user_activity_log ADD CONSTRAINT user_activity_log_user_email_fkey FOREIGN KEY (user_email) REFERENCES users(email) ON UPDATE CASCADE ON DELETE RESTRICT;"))
        
        # 2. matchup_queue
        conn.execute(text("ALTER TABLE matchup_queue DROP CONSTRAINT IF EXISTS matchup_queue_user_email_fkey;"))
        conn.execute(text("ALTER TABLE matchup_queue ADD CONSTRAINT matchup_queue_user_email_fkey FOREIGN KEY (user_email) REFERENCES users(email) ON UPDATE CASCADE ON DELETE RESTRICT;"))
        
        # 3. edit_history
        conn.execute(text("ALTER TABLE edit_history DROP CONSTRAINT IF EXISTS edit_history_user_email_fkey;"))
        conn.execute(text("ALTER TABLE edit_history ADD CONSTRAINT edit_history_user_email_fkey FOREIGN KEY (user_email) REFERENCES users(email) ON UPDATE CASCADE ON DELETE RESTRICT;"))
        
        # 4. records (updated_by)
        conn.execute(text("ALTER TABLE records DROP CONSTRAINT IF EXISTS records_updated_by_fkey;"))
        conn.execute(text("ALTER TABLE records ADD CONSTRAINT records_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES users(email) ON UPDATE CASCADE ON DELETE RESTRICT;"))

        # 5. records (reviewed_by)
        conn.execute(text("ALTER TABLE records DROP CONSTRAINT IF EXISTS records_reviewed_by_fkey;"))
        conn.execute(text("ALTER TABLE records ADD CONSTRAINT records_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES users(email) ON UPDATE CASCADE ON DELETE RESTRICT;"))

        # 6. records (language_id)
        conn.execute(text("ALTER TABLE records DROP CONSTRAINT IF EXISTS records_language_id_fkey;"))
        conn.execute(text("ALTER TABLE records ADD CONSTRAINT records_language_id_fkey FOREIGN KEY (language_id) REFERENCES languages(id) ON DELETE RESTRICT;"))

        # 7. records (source_id)
        conn.execute(text("ALTER TABLE records DROP CONSTRAINT IF EXISTS records_source_id_fkey;"))
        conn.execute(text("ALTER TABLE records ADD CONSTRAINT records_source_id_fkey FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE RESTRICT;"))

        # 8. search_entries (record_id)
        conn.execute(text("ALTER TABLE search_entries DROP CONSTRAINT IF EXISTS search_entries_record_id_fkey;"))
        conn.execute(text("ALTER TABLE search_entries ADD CONSTRAINT search_entries_record_id_fkey FOREIGN KEY (record_id) REFERENCES records(id) ON DELETE RESTRICT;"))

        # 9. matchup_queue (source_id)
        conn.execute(text("ALTER TABLE matchup_queue DROP CONSTRAINT IF EXISTS matchup_queue_source_id_fkey;"))
        conn.execute(text("ALTER TABLE matchup_queue ADD CONSTRAINT matchup_queue_source_id_fkey FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE RESTRICT;"))

        # 10. matchup_queue (suggested_record_id)
        conn.execute(text("ALTER TABLE matchup_queue DROP CONSTRAINT IF EXISTS matchup_queue_suggested_record_id_fkey;"))
        conn.execute(text("ALTER TABLE matchup_queue ADD CONSTRAINT matchup_queue_suggested_record_id_fkey FOREIGN KEY (suggested_record_id) REFERENCES records(id) ON DELETE RESTRICT;"))

        # 11. permissions (source_id)
        conn.execute(text("ALTER TABLE permissions DROP CONSTRAINT IF EXISTS permissions_source_id_fkey;"))
        conn.execute(text("ALTER TABLE permissions ADD CONSTRAINT permissions_source_id_fkey FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE RESTRICT;"))

        conn.commit()

    # Add embedding column if it doesn't exist (manual migration for now)
    # Note: In a full production app, we would use Alembic.
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE records ADD COLUMN IF NOT EXISTS embedding vector(1536);"))
        conn.commit()
            
    return engine

def seed_default_permissions(engine):
    """Seed default permissions if the table is empty."""
    from .models.identity import Permission
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Check if table is empty
        if session.query(Permission).count() == 0:
            # Default permissions for Brothertown-Language
            # Admin role for the proto-SNEA-admin team
            admin_perm = Permission(
                github_org="Brothertown-Language",
                github_team="proto-SNEA-admin",
                role="admin"
            )
            # Editor role for the proto-SNEA team
            editor_perm = Permission(
                github_org="Brothertown-Language",
                github_team="proto-SNEA",
                role="editor"
            )
            # Viewer role for the proto-SNEA-viewer team
            viewer_perm = Permission(
                github_org="Brothertown-Language",
                github_team="proto-SNEA-viewer",
                role="viewer"
            )
            session.add_all([admin_perm, editor_perm, viewer_perm])
            session.commit()
            if not is_production():
                st.info("Seeded default permissions for Brothertown-Language.")
            else:
                print("INFO: Seeded default permissions for Brothertown-Language.")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def seed_iso_639_data(engine):
    """Seed ISO 639-3 data from local project file if the table is empty."""
    from .models.iso639 import ISO639_3
    import csv
    import io

    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Check count before
        count_before = session.query(ISO639_3).count()
        
        if count_before == 0:
            data_file = Path(__file__).parent / "data" / "iso-639-3.tab"
            if not data_file.exists():
                print(f"ERROR: ISO 639-3 data file not found at {data_file}")
                return

            if not is_production():
                st.info(f"Seeding ISO 639-3 data from {data_file}...")
                st.info(f"Records before seeding: {count_before}")
            else:
                print(f"INFO: Seeding ISO 639-3 data from {data_file}...")
                print(f"INFO: Records before seeding: {count_before}")
            
            with open(data_file, encoding='utf-8') as f:
                content = f.read()
            
            reader = csv.DictReader(io.StringIO(content), delimiter='\t')
            
            iso_entries = []
            for row in reader:
                entry = ISO639_3(
                    id=row['Id'],
                    part2b=row.get('Part2b') or None,
                    part2t=row.get('Part2t') or None,
                    part1=row.get('Part1') or None,
                    scope=row['Scope'],
                    language_type=row['Language_Type'],
                    ref_name=row['Ref_Name'],
                    comment=row.get('Comment') or None
                )
                iso_entries.append(entry)
            
            # Use bulk insert for performance
            session.add_all(iso_entries)
            session.commit()
            
            count_after = session.query(ISO639_3).count()
            if not is_production():
                st.info(f"Seeded {len(iso_entries)} ISO 639-3 language records.")
                st.info(f"Records after seeding: {count_after}")
            else:
                print(f"INFO: Seeded {len(iso_entries)} ISO 639-3 language records.")
                print(f"INFO: Records after seeding: {count_after}")
    except Exception as e:
        print(f"ERROR: Failed to seed ISO 639-3 data: {e}")
        session.rollback()
    finally:
        session.close()

def get_session():
    """Get a new database session."""
    db_url = get_db_url()
    if not db_url:
        raise ValueError("Database URL not found in secrets or environment.")
    
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()
