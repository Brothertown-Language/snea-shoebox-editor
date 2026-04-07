# Copyright (c) 2026 Brothertown Language
"""
reset_schema_to_prod.py — Schema and data reset script for migration testing.

Purpose
-------
Resets the local database schema to match production, enabling safe migration
testing without accumulated local schema drift.

Default Behavior
----------------
Full reset (schema + data): Dumps schema and data from production, then restores
to local database. This is the safest baseline for migration testing.

Optional: --schema-only
-----------------------
Schema reset only, preserving local data. After schema reset, run
`sync_prod_to_local.py` to restore data from production.

Architecture
------------
Uses pgserver bundled PostgreSQL binaries:
- pg_dump: Schema/data dump from production
- psql: Restore to local database

The bundled binaries match pgserver's PostgreSQL version, ensuring compatibility.

Usage
-----
    # Full reset (default - schema + data)
    uv run python scripts/reset_schema_to_prod.py

    # Schema-only reset (preserve local data)
    uv run python scripts/reset_schema_to_prod.py --schema-only

Requirements
------------
- Production DATABASE_URL must be configured in:
  - Environment variable DATABASE_URL, OR
  - .streamlit/secrets.toml.production [connections.postgresql] url
- Local pgserver must be running (or will be started automatically)
- pgserver package with bundled PostgreSQL binaries

Exit Codes
----------
0: Success
1: Configuration error (missing DATABASE_URL)
2: Connection error (cannot reach production database)
3: Dump error (pg_dump failed)
4: Restore error (psql failed)
"""
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Python 3.11+ has tomllib in the standard library
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

# Resolve project root via git rev-parse --show-cdup (per AGENTS.md "Self-Location & Root Resolution")
# This is the authoritative method - git show-toplevel is PROHIBITED (returns absolute paths).
BASE_DIR = Path(__file__).resolve().parent
CDUP = subprocess.check_output(
    ["git", "-C", str(BASE_DIR), "rev-parse", "--show-cdup"],
    text=True
).strip()
project_root = (BASE_DIR / CDUP).resolve()
sys.path.insert(0, str(project_root))

LOG_FILE = project_root / "tmp" / "reset_schema.log"

# pgserver binary paths (version-matched with pgserver's PostgreSQL)
VENV_BIN = project_root / ".venv" / "lib" / "python3.12" / "site-packages" / "pgserver" / "pginstall" / "bin"
PG_DUMP = VENV_BIN / "pg_dump"
PSQL = VENV_BIN / "psql"


def log_message(msg: str, to_console: bool = True) -> None:
    """Log a message with timestamp to file and optionally to console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"

    # Ensure tmp directory exists
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted_msg + "\n")

    if to_console:
        print(msg)


def strip_ssl_params(url: str) -> str:
    """Strip sslmode from URL for pg_dump/psql compatibility.
    
    pgserver's bundled PostgreSQL binaries don't have SSL support compiled in.
    Remove sslmode=require from URL query string before passing to pg_dump/psql.
    
    Parameters
    ----------
    url : str
        PostgreSQL connection URL (may contain sslmode parameter).
    
    Returns
    -------
    str
        URL with sslmode parameter removed.
    """
    if "?" in url:
        base, query = url.split("?", 1)
        params = [p for p in query.split("&") if not p.startswith("sslmode=")]
        if params:
            return f"{base}?{'&'.join(params)}"
        return base
    return url


def load_production_url() -> str:
    """Load production DATABASE_URL from environment or secrets file.

    Raises
    ------
    RuntimeError
        If production DATABASE_URL is not configured.
    """
    prod_url = os.getenv("DATABASE_URL")

    if not prod_url:
        prod_secrets_path = project_root / ".streamlit" / "secrets.toml.production"
        if prod_secrets_path.exists():
            try:
                with open(prod_secrets_path, "rb") as f:
                    config = tomllib.load(f)
                    prod_url = config.get("connections", {}).get("postgresql", {}).get("url")
            except Exception as e:
                log_message(f"Warning: Failed to read production secrets: {e}")

    if not prod_url:
        log_message("ERROR: Production DATABASE_URL not found.")
        log_message("Set DATABASE_URL environment variable or configure .streamlit/secrets.toml.production")
        sys.exit(1)

    # Strip sslmode for pg_dump/psql compatibility (bundled binaries lack SSL support)
    prod_url = strip_ssl_params(prod_url)

    return prod_url


def get_local_url() -> str:
    """Get local database URL, starting pgserver if needed.

    Returns
    -------
    str
        PostgreSQL connection URI for local database.
    """
    local_url = os.getenv("LOCAL_DATABASE_URL")

    if not local_url:
        local_secrets_path = project_root / ".streamlit" / "secrets.toml"
        if local_secrets_path.exists():
            try:
                with open(local_secrets_path, "rb") as f:
                    config = tomllib.load(f)
                    local_url = config.get("connections", {}).get("postgresql", {}).get("url")
            except Exception as e:
                log_message(f"Warning: Failed to read local secrets: {e}")

    if not local_url:
        # Start pgserver if needed
        try:
            from src.database.connection import _get_local_db_path, _start_pgserver_core

            db_path = _get_local_db_path()
            log_message(f"Starting pgserver (db_path={db_path})...")
            local_url = _start_pgserver_core(db_path)
            log_message(f"pgserver started: {local_url.split('@')[-1]}")
        except ImportError:
            log_message("pgserver not installed — using default local URL.")
            local_url = "postgresql://postgres:@localhost:5432/postgres"
        except Exception as e:
            log_message(f"Warning: pgserver auto-start failed: {e}")
            local_url = "postgresql://postgres:@localhost:5432/postgres"

    return local_url


def dump_schema_only(prod_url: str) -> bytes:
    """Dump schema from production database.

    Parameters
    ----------
    prod_url : str
        Production PostgreSQL connection URL.

    Returns
    -------
    bytes
        Schema dump as SQL.

    Raises
    ------
    RuntimeError
        If pg_dump fails.
    """
    log_message("Dumping schema from production...")

    cmd = [
        str(PG_DUMP),
        "--schema-only",
        "--no-owner",
        "--no-acl",
        prod_url
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=False
    )

    if result.returncode != 0:
        error_msg = result.stderr.decode("utf-8", errors="replace")
        log_message(f"ERROR: pg_dump failed:\n{error_msg}")
        sys.exit(3)

    log_message(f"Schema dump complete ({len(result.stdout)} bytes)")
    return result.stdout


def dump_full(prod_url: str) -> bytes:
    """Dump schema and data from production database.

    Parameters
    ----------
    prod_url : str
        Production PostgreSQL connection URL.

    Returns
    -------
    bytes
        Full dump (schema + data) as SQL.

    Raises
    ------
    RuntimeError
        If pg_dump fails.
    """
    log_message("Dumping schema and data from production...")

    cmd = [
        str(PG_DUMP),
        "--no-owner",
        "--no-acl",
        prod_url
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=False
    )

    if result.returncode != 0:
        error_msg = result.stderr.decode("utf-8", errors="replace")
        log_message(f"ERROR: pg_dump failed:\n{error_msg}")
        sys.exit(3)

    log_message(f"Full dump complete ({len(result.stdout)} bytes)")
    return result.stdout


def restore_to_local(local_url: str, dump_data: bytes) -> None:
    """Restore dump to local database.

    This drops all existing objects and recreates them from the dump.
    For schema-only dumps, run sync_prod_to_local.py afterward to restore data.

    Parameters
    ----------
    local_url : str
        Local PostgreSQL connection URL.
    dump_data : bytes
        SQL dump to restore.

    Raises
    ------
    RuntimeError
        If psql fails.
    """
    log_message("Restoring to local database...")

    cmd = [
        str(PSQL),
        local_url
    ]

    result = subprocess.run(
        cmd,
        input=dump_data,
        capture_output=True,
        text=False
    )

    if result.returncode != 0:
        error_msg = result.stderr.decode("utf-8", errors="replace")
        log_message(f"ERROR: psql restore failed:\n{error_msg}")
        sys.exit(4)

    log_message("Restore complete.")


def main():
    """Main entry point for schema reset script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Reset local database schema to match production.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Full reset (default - schema + data)
    uv run python scripts/reset_schema_to_prod.py

    # Schema-only reset (preserve local data)
    uv run python scripts/reset_schema_to_prod.py --schema-only
    # Then restore data:
    # uv run python scripts/sync_prod_to_local.py
        """
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Reset schema only, preserving local data (run sync_prod_to_local.py afterward)"
    )

    args = parser.parse_args()

    # Start fresh log for each run
    if LOG_FILE.exists():
        LOG_FILE.unlink()

    log_message("=" * 60)
    log_message("Schema Reset Script")
    log_message("=" * 60)

    # Verify binaries exist
    if not PG_DUMP.exists():
        log_message(f"ERROR: pg_dump not found at {PG_DUMP}")
        log_message("Install pgserver: uv sync")
        sys.exit(1)

    if not PSQL.exists():
        log_message(f"ERROR: psql not found at {PSQL}")
        log_message("Install pgserver: uv sync")
        sys.exit(1)

    # Load URLs
    prod_url = load_production_url()
    local_url = get_local_url()

    # Log connection info (scrub passwords)
    log_message(f"Production: {prod_url.split('@')[-1]}")
    log_message(f"Local: {local_url.split('@')[-1]}")
    log_message(f"Mode: {'schema-only' if args.schema_only else 'full (schema + data)'}")

    # Perform dump
    if args.schema_only:
        dump_data = dump_schema_only(prod_url)
    else:
        dump_data = dump_full(prod_url)

    # Restore to local
    restore_to_local(local_url, dump_data)

    log_message("=" * 60)
    log_message("Schema reset completed successfully.")

    if args.schema_only:
        log_message("Run sync_prod_to_local.py to restore data from production.")


if __name__ == "__main__":
    main()