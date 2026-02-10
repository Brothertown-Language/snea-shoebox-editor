# Copyright (c) 2026 Brothertown Language
import os
import streamlit as st
from pathlib import Path
import atexit
import getpass
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .base import Base
from src.logging_config import get_logger

_logger = get_logger("snea.database.pgserver")

# Global variable to hold the pgserver instance if auto-started
_pg_server = None
_db_url_cache = None

def _get_local_db_path():
    """Get the path to the local database directory."""
    project_root = Path(__file__).parent.parent.parent
    
    # Junie separation: Use a dedicated path if JUNIE_PRIVATE_DB is set
    if os.getenv("JUNIE_PRIVATE_DB") == "true":
        db_path = project_root / "tmp" / "junie_db"
        _logger.debug("Using Junie-private DB path: %s", db_path)
        return db_path

    db_path = project_root / "tmp" / "local_db"
    _logger.debug("Using local DB path: %s", db_path)
    return db_path

def _stop_local_db():
    """Stop the local database if it was auto-started."""
    global _pg_server
    if _pg_server:
        _logger.debug("Stopping local PostgreSQL (pgdata=%s)…", getattr(_pg_server, 'pgdata', '?'))
        try:
            _pg_server.cleanup()
            _pg_server = None
            _logger.debug("Local PostgreSQL stopped successfully.")
        except Exception as e:
            _logger.debug("Error stopping local PostgreSQL: %s", e)
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

def _write_dbeaver_connection(uri):
    """Write a DBeaver project archive (.dbp) to tmp/ for local dev convenience.

    Reads the template file src/seed_data/snea-local-dev.dbp and replaces
    the connection with the local pgserver connection details, renaming it
    to ``snea-editor-db-local-dev``.

    The output is written to tmp/snea-local-dev.dbp and can be imported via
    File → Import → DBeaver → DBeaver Project (.dbp).
    """
    try:
        import json
        import time
        import zipfile
        import socket
        from urllib.parse import urlparse

        parsed = urlparse(uri)
        project_root = Path(__file__).parent.parent.parent
        tmp_dir = project_root / "tmp"
        template_path = Path(__file__).parent.parent / "seed_data" / "snea-local-dev.dbp"

        if not template_path.exists():
            return

        db_name = parsed.path.lstrip("/") or "postgres"
        timestamp_ms = str(int(time.time() * 1000))
        hostname = socket.gethostname()

        host = parsed.hostname or "localhost"
        port = str(parsed.port or 5432)
        jdbc_url = f"jdbc:postgresql://{host}:{port}/{db_name}"

        # Read all files from the template archive, renaming the project
        # folder from "SNEA" to "SNEA Local Dev"
        old_project = "projects/SNEA/"
        new_project = "projects/SNEA Local Dev/"
        with zipfile.ZipFile(str(template_path), "r") as src:
            template_entries = {}
            for info in src.infolist():
                new_name = info.filename.replace(old_project, new_project)
                template_entries[new_name] = src.read(info.filename)

        # Replace data-sources.json with local dev connection
        ds_key = "projects/SNEA Local Dev/.dbeaver/data-sources.json"
        ds_raw = template_entries[ds_key].decode("utf-8")
        data_sources = json.loads(ds_raw)

        # Remove all existing connections and insert the local dev one
        conn_id = "postgres-jdbc-snea-local-dev"
        connection_entry = {
            "provider": "postgresql",
            "driver": "postgres-jdbc",
            "name": "snea-editor-db-local-dev",
            "save-password": True,
            "configuration": {
                "host": host,
                "port": port,
                "database": db_name,
                "user": "postgres",
                "url": jdbc_url,
                "configurationType": "MANUAL",
                "type": "dev",
                "closeIdleConnection": False,
                "auth-model": "native",
            },
        }
        data_sources["connections"] = {conn_id: connection_entry}
        template_entries[ds_key] = (json.dumps(data_sources, indent="\t") + "\n").encode("utf-8")

        # Update meta.xml timestamp
        meta_key = "meta.xml"
        meta_xml = template_entries[meta_key].decode("utf-8")
        # Replace the timestamp in the source element
        import re
        meta_xml = re.sub(
            r'time="[^"]*"',
            f'time="{timestamp_ms}"',
            meta_xml,
        )
        meta_xml = re.sub(
            r'host="[^"]*"',
            f'host="{hostname}"',
            meta_xml,
        )
        template_entries[meta_key] = meta_xml.encode("utf-8")

        # Update project name in meta.xml
        meta_xml = re.sub(
            r'<project name="[^"]*"',
            '<project name="SNEA Local Dev"',
            meta_xml,
        )
        template_entries[meta_key] = meta_xml.encode("utf-8")

        # Skip credentials-config.json (encrypted, not needed for local dev)
        creds_key = "projects/SNEA Local Dev/.dbeaver/credentials-config.json"

        # Write the output archive
        dbp_path = tmp_dir / "snea-local-dev.dbp"
        with zipfile.ZipFile(str(dbp_path), "w", zipfile.ZIP_DEFLATED) as zf:
            for filename, data in template_entries.items():
                if filename == creds_key:
                    continue
                zf.writestr(filename, data)
    except Exception:
        pass


def _enable_tcp_listening(pg_server):
    """Stop pgserver's socket-only postgres and restart with TCP on localhost:5432.

    pgserver hardcodes ``-h ""`` which disables TCP.  This function stops the
    running postgres, then restarts it with ``-h "localhost"`` so that both
    TCP (port 5432) and the Unix socket remain available.  The pgserver handle
    stays valid because the same pgdata directory is reused.
    """
    from pgserver._commands import pg_ctl

    # Determine the socket directory from the current URI
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(pg_server.get_uri())
    query_params = parse_qs(parsed.query)
    socket_dir = query_params.get("host", [None])[0] or str(pg_server.pgdata)
    _logger.debug("TCP enable: socket_dir=%s, pgdata=%s", socket_dir, pg_server.pgdata)

    # Stop the socket-only instance
    _logger.debug("Stopping socket-only PostgreSQL instance…")
    pg_ctl(['-w', 'stop'], pgdata=pg_server.pgdata, user=pg_server.system_user)
    _logger.debug("Socket-only instance stopped.")

    # Restart with TCP enabled on localhost
    pg_ctl_args = [
        '-w',
        '-o', '-h "localhost"',
        '-o', f'-k {socket_dir}',
        '-l', str(pg_server.log),
        'start',
    ]
    _logger.debug("Restarting PostgreSQL with TCP (args=%s)…", pg_ctl_args)
    pg_ctl(pg_ctl_args, pgdata=pg_server.pgdata, user=pg_server.system_user, timeout=10)
    _logger.debug("PostgreSQL restarted with TCP on localhost:5432.")


def _force_stop_stuck_db(db_path):
    """Detect and force-stop a local DB that is stuck in a 'shutting down' state.

    If postmaster.pid exists and hasn't been touched for 30 seconds, and we 
    are seeing 'shutting down' errors, it's likely stuck.
    """
    pid_file = Path(db_path) / "postmaster.pid"
    if not pid_file.exists():
        return

    import time
    from pgserver._commands import pg_ctl

    last_mod = pid_file.stat().st_mtime
    age = time.time() - last_mod

    if age > 30:
        _logger.warning(
            "Local DB appears stuck in 'shutting down' state (age=%.1fs). "
            "Forcing immediate shutdown of pgdata=%s…", 
            age, db_path
        )
        try:
            # -m immediate forces shutdown without waiting for clients
            # We must pass the arguments as a list to the underlying pg_ctl wrapper
            pg_ctl(['stop', '-m', 'immediate', '-D', str(db_path)], pgdata=str(db_path))
            _logger.info("Force-stop command issued to stuck DB.")
            # Small wait to allow OS to clean up the PID file if pg_ctl succeeded
            time.sleep(1)
            # If the PID file still exists, it might be because the process was 
            # already gone but the file remained. In this case, we should 
            # manually remove it so pgserver can start.
            if pid_file.exists():
                _logger.info("PID file still exists after force-stop, removing manually.")
                pid_file.unlink()
        except Exception as e:
            _logger.debug("Failed to force-stop DB: %s", e)
            # Fallback: try to remove PID file manually if it seems stuck
            if pid_file.exists():
                _logger.info("Removing stuck PID file manually after failed force-stop.")
                pid_file.unlink()


def _auto_start_pgserver():
    """Try to auto-start pgserver for local development."""
    global _pg_server
    
    # Safety check: NEVER start pgserver in production
    if is_production():
        return None

    # Use a persistent empty container for the pgserver warning so we can
    # clear it later if the startup finally succeeds in a subsequent call.
    if "pgserver_warning" not in st.session_state:
        st.session_state.pgserver_warning = st.empty()
    warning_placeholder = st.session_state.pgserver_warning

    # If pgserver is already running, return the cached URI immediately
    # to avoid re-initializing on every Streamlit rerun.
    if _pg_server is not None:
        warning_placeholder.empty()
        is_junie = os.getenv("JUNIE_PRIVATE_DB") == "true"
        if not is_junie:
            uri = "postgresql://postgres:@localhost:5432/postgres"
        else:
            uri = _pg_server.get_uri()
        _logger.debug("pgserver already running, returning cached URI.")
        return uri

    is_junie = os.getenv("JUNIE_PRIVATE_DB") == "true"

    try:
        import pgserver
        import time as _time
        db_path = _get_local_db_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if DB is stuck before attempting to start it
        _force_stop_stuck_db(db_path)

        _logger.debug("Starting pgserver (db_path=%s)…", db_path)
        _pg_server = pgserver.get_server(str(db_path))
        _logger.debug("pgserver started (uri=%s).", _pg_server.get_uri())

        # For non-Junie local dev, enable TCP so DBeaver and Streamlit can
        # connect via localhost:5432.  Junie keeps the default socket-only
        # connection to avoid port conflicts.
        if not is_junie:
            _logger.debug("Enabling TCP listening for local dev…")
            _enable_tcp_listening(_pg_server)
            uri = "postgresql://postgres:@localhost:5432/postgres"
        else:
            uri = _pg_server.get_uri()
        _logger.debug("Connection URI: %s", uri)
        
        # Ensure pgvector extension is enabled automatically for local dev.
        # Retry with backoff — the database may still be recovering from a
        # previous unclean shutdown ("the database system is shutting down").
        from sqlalchemy import create_engine, text
        engine = create_engine(uri)
        max_retries = 5
        for attempt in range(max_retries):
            try:
                _logger.debug("Verifying database connection (attempt %d/%d)…", attempt + 1, max_retries)
                with engine.connect() as conn:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                    conn.commit()
                _logger.debug("Database connection verified; pgvector extension ready.")
                break
            except Exception as conn_err:
                _logger.debug("Connection attempt %d failed: %s", attempt + 1, conn_err)
                if attempt < max_retries - 1:
                    _time.sleep(1 * (attempt + 1))
                else:
                    raise conn_err
        
        # Register cleanup on exit
        atexit.register(_stop_local_db)
        _logger.debug("Registered atexit cleanup handler.")

        # Generate DBeaver connection file for local dev convenience
        _write_dbeaver_connection(uri)

        _logger.debug("Local pgserver fully initialized.")
        warning_placeholder.empty()
        return uri
    except ImportError:
        _logger.debug("pgserver not installed — skipping local DB auto-start.")
        return None
    except Exception as e:
        _logger.debug("pgserver auto-start failed: %s", e)
        # Only warn if not in production and import succeeded but start failed
        if not is_production():
            err_msg = str(e)
            if "shutting down" in err_msg:
                warning_placeholder.warning(
                    "Local PostgreSQL is still shutting down from a previous session. "
                    "Please wait a few seconds and refresh the page."
                )
            else:
                warning_placeholder.warning(f"Failed to auto-start local PostgreSQL: {e}")
        return None

def get_db_url():
    """Get database URL from Streamlit secrets or environment variables."""
    global _db_url_cache
    if _db_url_cache:
        return _db_url_cache

    # 1. If we are in local dev, prioritize auto-starting pgserver
    # to avoid accidentally using production secrets from .streamlit/secrets.toml
    # or DATABASE_URL environment variable if it happens to be set to prod.
    if not is_production():
        auto_url = _auto_start_pgserver()
        if auto_url:
            # Set environment variable so other parts of the app can use it
            os.environ["DATABASE_URL"] = auto_url
            _db_url_cache = auto_url
            return auto_url

    # 2. Check environment variable
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        _db_url_cache = env_url
        return env_url

    # 3. Check Streamlit secrets (Production fallback)
    try:
        if "connections" in st.secrets and "postgresql" in st.secrets["connections"]:
            url = st.secrets["connections"]["postgresql"]["url"]
            if url:
                _db_url_cache = url
                return url
    except Exception:
        pass
    
    return None

def init_db():
    """Initialize the database schema."""
    db_url = get_db_url()
    if not db_url:
        raise ValueError("Database URL not found in secrets or environment.")
    
    # pool_size=0 and pool_recycle=5 ensures that the pool can become empty when idle,
    # and stale connections are removed quickly to preserve limited production resources.
    engine = create_engine(db_url, pool_size=0, max_overflow=20, pool_recycle=5)
    Base.metadata.create_all(engine)
    from .migrations import MigrationManager
    MigrationManager(engine).run_all()
    return engine

def get_session():
    """Get a new database session."""
    db_url = get_db_url()
    if not db_url:
        raise ValueError("Database URL not found in secrets or environment.")
    
    # pool_size=0 and pool_recycle=5 ensures that the pool can become empty when idle,
    # and stale connections are removed quickly to preserve limited production resources.
    engine = create_engine(db_url, pool_size=0, max_overflow=20, pool_recycle=5)
    Session = sessionmaker(bind=engine)
    return Session()
