# Copyright (c) 2026 Brothertown Language
# <!-- Copyright (c) 2026 Brothertown Language -->
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
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
    project_root = Path.cwd()
    
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
            db_path = getattr(_pg_server, 'pgdata', None)
            _pg_server.cleanup()
            _pg_server = None
            _logger.debug("Local PostgreSQL stop command issued.")
            
            # If the PID file still exists, it means shutdown is waiting for clients.
            if db_path:
                pid_file = Path(db_path) / "postmaster.pid"
                if pid_file.exists():
                    _logger.warning("PostgreSQL is waiting for active connections to close before shutting down.")
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
    try:
        from pgserver import pg_ctl
    except ImportError:
        # Fallback for environments where pg_ctl is not directly importable
        def pg_ctl(*args, **kwargs):
            import subprocess
            from pathlib import Path
            import pgserver
            pg_ctl_bin = Path(pgserver.__file__).parent / "pgbin" / "bin" / "pg_ctl"
            if not pg_ctl_bin.exists():
                pg_ctl_bin = "pg_ctl"
            cmd = [str(pg_ctl_bin)] + list(args[0])
            return subprocess.run(cmd, check=True)

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
    """Force-stop a local DB that is stuck in a 'shutting down' state.
    
    Proceeds with an immediate shutdown and PID file cleanup.
    """
    _logger.debug("[DEV] Entering _force_stop_stuck_db(db_path=%s)", db_path)
    pid_file = Path(db_path) / "postmaster.pid"
    if not pid_file.exists():
        _logger.debug("[DEV] No postmaster.pid found at %s. Skipping force-stop.", db_path)
        return

    _logger.debug("[DEV] postmaster.pid exists at %s. Content: %s", pid_file, pid_file.read_text().strip() if pid_file.exists() else "N/A")

    import time
    import signal
    import subprocess
    import os

    _logger.warning(
        "Forcing immediate shutdown of potentially stuck DB (pgdata=%s)…", 
        db_path
    )
    try:
        # Read PID from postmaster.pid
        pid = None
        if pid_file.exists():
            try:
                content = pid_file.read_text().splitlines()
                if content:
                    pid = int(content[0].strip())
                    _logger.debug("[DEV] Found PID %d in %s", pid, pid_file)
            except Exception as e:
                _logger.debug("[DEV] Error reading PID from file: %s", e)

        # 1. Try pg_ctl stop -m immediate
        _logger.debug("[DEV] Calling pg_ctl stop -m immediate...")
        import pgserver
        pg_ctl_path = Path(pgserver.__file__).parent / "pgbin" / "bin" / "pg_ctl"
        
        if pg_ctl_path.exists():
            cmd = [str(pg_ctl_path), 'stop', '-m', 'immediate', '-D', str(db_path)]
        else:
            cmd = ['pg_ctl', 'stop', '-m', 'immediate', '-D', str(db_path)]
            
        subprocess.run(cmd, capture_output=True, text=True)

        # 2. If PID is still alive, use SIGTERM on process group or postmaster
        if pid:
            try:
                os.kill(pid, 0) # Check if alive
                _logger.warning("[DEV] Process %d still alive after pg_ctl. Sending SIGTERM to postmaster/group.", pid)
                
                # SIGTERM to postmaster is a fast shutdown
                _logger.info("[DEV] Sending SIGTERM to postmaster PID %d", pid)
                os.kill(pid, signal.SIGTERM)
                
                try:
                    pgid = os.getpgid(pid)
                    _logger.info("[DEV] Sending SIGTERM to process group %d", pgid)
                    os.killpg(pgid, signal.SIGTERM)
                except Exception as e:
                    _logger.debug("[DEV] Could not kill process group: %s", e)
                
                time.sleep(1)
                
                # 3. Final desperation: SIGKILL
                try:
                    os.kill(pid, 0)
                    _logger.warning("[DEV] Process %d still alive after SIGTERM. Sending SIGKILL.", pid)
                    os.kill(pid, signal.SIGKILL)
                    try:
                        pgid = os.getpgid(pid)
                        os.killpg(pgid, signal.SIGKILL)
                    except Exception:
                        pass
                except ProcessLookupError:
                    _logger.info("[DEV] Process %d terminated successfully after SIGTERM.", pid)
            except ProcessLookupError:
                _logger.debug("[DEV] Process %d is gone.", pid)

        _logger.info("Force-stop sequence completed.")
        time.sleep(1)
        if pid_file.exists():
            _logger.info("Removing stuck PID file manually.")
            pid_file.unlink()
    except Exception as e:
        _logger.error("[DEV] Failed to force-stop DB: %s", e, exc_info=True)
        # Fallback: remove PID file manually
        if pid_file.exists():
            _logger.info("Removing stuck PID file manually after failed force-stop.")
            pid_file.unlink()
            _logger.debug("[DEV] Fallback: Manually unlinked %s", pid_file)


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
        from pgserver import pg_ctl
        import time as _time
        db_path = _get_local_db_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if we should force-stop based on reported failure duration
        pid_file = db_path / "postmaster.pid"
        if "pg_shutdown_first_seen" in st.session_state:
            duration = _time.time() - st.session_state["pg_shutdown_first_seen"]
            _logger.debug("[DEV] pg_shutdown_first_seen duration: %.1fs", duration)
            if duration > 5.0:  # If stuck for > 5 seconds
                _logger.warning("DB stuck in 'shutting down' for %.1fs. Triggering force-stop.", duration)
                _force_stop_stuck_db(db_path)
                st.session_state.pop("pg_shutdown_first_seen", None)
        elif pid_file.exists():
            # If PID file exists but we don't have a handle, check if it responds
            _logger.debug("[DEV] PID file exists at startup. Checking status in postmaster.pid...")
            try:
                content = pid_file.read_text().splitlines()
                if len(content) >= 8 and content[7].strip() == "stopping":
                    _logger.warning("[DEV] DB status is 'stopping' in postmaster.pid. Setting pg_shutdown_first_seen.")
                    if "pg_shutdown_first_seen" not in st.session_state:
                        st.session_state["pg_shutdown_first_seen"] = _time.time()
            except Exception as e:
                _logger.debug("[DEV] Error reading postmaster.pid status: %s", e)

        _logger.debug("Starting pgserver (db_path=%s)…", db_path)
        
        # Retry logic for pgserver.get_server() to handle "shutting down" states
        # by triggering a force-stop.
        max_start_attempts = 5
        for start_attempt in range(1, max_start_attempts + 1):
            if pid_file.exists():
                _logger.warning("[DEV] PID file exists at start of attempt %d. Triggering force-kill.", start_attempt)
                _force_stop_stuck_db(db_path)

            try:
                _pg_server = pgserver.get_server(str(db_path))
                _logger.debug("pgserver started (uri=%s).", _pg_server.get_uri())
                st.session_state.pop("pg_shutdown_first_seen", None)
                break
            except (Exception, AssertionError) as start_err:
                err_type = type(start_err).__name__
                err_msg = str(start_err)
                _logger.debug("[DEV] pgserver.get_server() failed (%s): %s", err_type, err_msg)
                
                # If it failed and PID file exists, it might be "shutting down" or just stuck
                if pid_file.exists():
                    # Treat AssertionError as potential stuck state if it has no message
                    # or if specific phrases match.
                    is_stuck_err = (
                        err_type == "AssertionError" or 
                        any(phrase in err_msg for phrase in ["shutting down", "already running", "lock file", "starting up"])
                    )
                    
                    if is_stuck_err:
                        _logger.debug("[DEV] Detected potential stuck state (%s): %s", err_type, err_msg)
                        if "pg_shutdown_first_seen" not in st.session_state:
                            st.session_state["pg_shutdown_first_seen"] = _time.time()
                            _logger.debug("[DEV] Set pg_shutdown_first_seen in session_state")
                        
                        duration = _time.time() - st.session_state["pg_shutdown_first_seen"]
                        if start_attempt < max_start_attempts:
                            _logger.warning("pgserver failed to start. Attempt %d/%d (duration=%.1fs)…", start_attempt, max_start_attempts, duration)
                            # Be more aggressive: if we failed once and PID exists, try a force stop
                            _logger.warning("[DEV] Triggering force-kill on attempt %d due to stuck state", start_attempt)
                            _force_stop_stuck_db(db_path)
                            st.session_state.pop("pg_shutdown_first_seen", None)
                            _time.sleep(1)
                        else:
                            _logger.error("[DEV] Max start attempts reached for stuck state.")
                            # Final desperation: force stop even on last attempt failure
                            _force_stop_stuck_db(db_path)
                            raise start_err
                    else:
                        raise start_err
                else:
                    raise start_err

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
        max_retries = 10
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
