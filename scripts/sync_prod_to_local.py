# Copyright (c) 2026 Brothertown Language
"""
sync_prod_to_local.py — Production-to-local database sync script.

Purpose
-------
Copies all data from the production PostgreSQL database (Aiven) into the local
development database (pgserver), replacing local data entirely. Intended for
developer onboarding and local debugging against real production data.

Currently-synced tables (maintenance reference snapshot as of 2026-03-09, 13 tables)
-------------------------------------------------------------------------------------
  edit_history, iso_639_3, languages, matchup_queue, permissions,
  record_languages, records, schema_version, search_entries, sources,
  user_activity_log, user_preferences, users

Coverage mechanism
------------------
Table discovery uses ``Base.metadata.sorted_tables``, which performs a
topological sort of all SQLAlchemy ORM-registered tables, respecting foreign-key
dependencies. Tables are registered automatically when their model classes are
imported — see the ``import src.database.models`` statement below.

Maintenance contract
--------------------
- **New ORM table**: add the model class under ``src/database/models/``; it will
  be imported via ``src.database.models`` and covered automatically — no changes
  to this script are required.
- **Raw-SQL table** (created outside the ORM / Base.metadata): it will NOT be
  discovered automatically. You MUST add explicit sync logic for it here.
- **Removed table**: verify ``reset_all_sequences()`` still behaves correctly if
  the table had an integer PK named ``id``.
"""

import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

# Python 3.11+ has tomllib in the standard library
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

# Ensure project root is in path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

LOG_FILE = project_root / "tmp" / "sync_prod_to_local.log"


def log_message(msg, to_console=True, pbar=None):
    """Log a message with a timestamp to the log file and optionally to the console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"

    # Ensure tmp directory exists
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted_msg + "\n")

    if to_console:
        if pbar:
            tqdm.write(msg)
        else:
            print(msg)


from src.database.base import Base

# Critical: this import triggers all ORM model class definitions, which registers
# every table with Base.metadata. Without it, sorted_tables would be empty and
# no data would be synced.
import src.database.models


def _ensure_pgserver() -> str:
    """Start pgserver for local dev and return the TCP connection URI.

    Delegates to _start_pgserver_core() in src.database.connection — the
    single authoritative implementation shared with the Streamlit app.
    Always returns a TCP URI (postgresql://postgres:@localhost:5432/postgres)
    for non-OpenCode contexts, which is what this script requires.
    """
    try:
        from src.database.connection import _get_local_db_path, _start_pgserver_core

        db_path = _get_local_db_path()
        log_message(f"Starting pgserver (db_path={db_path})...")
        uri = _start_pgserver_core(db_path)
        log_message(f"pgserver started: {uri.split('@')[-1]}")
        return uri
    except ImportError:
        log_message("pgserver not installed — skipping auto-start.")
        return "postgresql://postgres:@localhost:5432/postgres"
    except Exception as e:
        log_message(f"Warning: pgserver auto-start failed: {e}")
        return "postgresql://postgres:@localhost:5432/postgres"


def load_secrets():
    """Load database URLs from Streamlit secrets files if environment variables are not set."""
    prod_url = os.getenv("DATABASE_URL")
    local_url = os.getenv("LOCAL_DATABASE_URL")

    # Path to secrets files
    local_secrets_path = project_root / ".streamlit" / "secrets.toml"
    prod_secrets_path = project_root / ".streamlit" / "secrets.toml.production"

    # 1. Try to load Production URL from secrets.toml.production
    if not prod_url and prod_secrets_path.exists():
        try:
            with open(prod_secrets_path, "rb") as f:
                config = tomllib.load(f)
                prod_url = config.get("connections", {}).get("postgresql", {}).get("url")
        except Exception as e:
            log_message(f"Warning: Failed to read production secrets: {e}")

    # 2. Try to load Local URL from secrets.toml
    if not local_url and local_secrets_path.exists():
        try:
            with open(local_secrets_path, "rb") as f:
                config = tomllib.load(f)
                local_url = config.get("connections", {}).get("postgresql", {}).get("url")
        except Exception as e:
            log_message(f"Warning: Failed to read local secrets: {e}")

    # Default fallback for local if still not found
    if not local_url:
        local_url = "postgresql://postgres:@localhost:5432/postgres"

    return prod_url, local_url


def sync_data():
    """
    Orchestrate a full production-to-local data sync.

    Steps
    -----
    1. Load connection secrets (env vars → secrets files → fallback).
    2. Ensure the local pgserver instance is running.
    3. Create any missing local schema objects via ``Base.metadata.create_all``.
    4. Delete all local rows in **reverse** FK-dependency order (children before
       parents) to avoid foreign-key constraint violations.
    5. Insert all production rows in **forward** FK-dependency order (parents
       before children).
    6. Reset all integer-PK sequences so subsequent local INSERTs do not collide
       with the copied row IDs.

    Maintenance contract
    --------------------
    Table coverage is ORM-driven (``Base.metadata.sorted_tables``). New ORM
    tables are covered automatically. Raw-SQL tables outside the ORM must be
    handled explicitly — see module docstring.
    """
    # Start fresh log for each run
    if LOG_FILE.exists():
        LOG_FILE.unlink()
    log_message("Starting Production to Local Sync...")

    prod_url, local_url = load_secrets()

    if not prod_url:
        log_message("Error: Production DATABASE_URL not found in environment or .streamlit/secrets.toml.production")
        sys.exit(1)

    local_url = _ensure_pgserver()

    log_message(f"Connecting to Production: {prod_url.split('@')[-1]}")
    # Scrub local path if it's a socket-based URI for display
    log_message(f"Connecting to Local: {local_url.split('@')[-1]}")

    prod_engine = create_engine(prod_url)
    local_engine = create_engine(local_url)

    # 1. Ensure extensions and schema exist locally
    with local_engine.connect() as conn:
        log_message("Ensuring pgvector extension...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    log_message("Initializing local schema...")
    Base.metadata.create_all(local_engine)

    # 2. Determine Table Order (to respect Foreign Keys)
    # sorted_tables performs a topological sort over all ORM-registered tables
    # using their declared ForeignKey relationships. This guarantees parents come
    # before children on insert and children come before parents on delete.
    # ORM registration depends on the `import src.database.models` above.
    tables = Base.metadata.sorted_tables

    prod_session_factory = sessionmaker(bind=prod_engine)
    local_session_factory = sessionmaker(bind=local_engine)

    try:
        with prod_session_factory() as prod_session, local_session_factory() as local_session:
            log_message("Starting data sync...")

            # 2. Clear local data in reverse dependency order to respect FKs.
            # Reversing the topological sort deletes children before parents,
            # preventing FK constraint violations during DELETE.
            log_message("Clearing local data (reverse order)...")
            for table in reversed(tables):
                log_message(f"Deleting table: {table.name}", to_console=False)
                local_session.execute(table.delete())
            local_session.commit()

            # 3. Iterate in forward dependency order for insertion.
            # Parents are inserted before children, satisfying FK constraints.
            pbar = tqdm(tables, desc="Syncing tables")
            for table in pbar:
                pbar.set_postfix(table=table.name)
                log_message(f"Syncing table: {table.name}", to_console=False)

                # Fetch all from production
                results = prod_session.execute(table.select()).fetchall()
                if results:
                    # Convert results to dicts for insertion
                    data = [dict(row._mapping) for row in results]
                    local_session.execute(table.insert(), data)
                    log_message(f"Synced {table.name}: {len(data)} rows", pbar=pbar)
                else:
                    log_message(f"Synced {table.name}: Empty (skipped)", pbar=pbar)

                local_session.commit()

        log_message("\nSync completed successfully.")
        reset_all_sequences(local_engine)
    except Exception:
        error_trace = traceback.format_exc()
        log_message(f"CRITICAL ERROR during sync:\n{error_trace}")
        sys.exit(1)


def reset_all_sequences(local_engine) -> None:
    """
    Reset all integer-PK sequences to match the current MAX(id) in each table.

    This must be called after any bulk data copy (e.g., prod→local sync) that inserts
    rows with explicit id values, because PostgreSQL sequences are not automatically
    advanced by such inserts. Without this reset, the next INSERT will attempt to use
    a sequence value that already exists, causing a UniqueViolation.

    Implementation: iterates Base.metadata.sorted_tables at runtime and resets only
    tables that have an integer 'id' column with an associated sequence. No table names
    are hardcoded — new ORM tables are covered automatically.

    Maintenance note: if a table is removed from the ORM, or its primary key column is
    renamed away from 'id', verify this function still behaves correctly. If a table
    exists outside Base.metadata (e.g., created via raw SQL), it will NOT be covered
    and must be added explicitly.
    """
    from sqlalchemy import Integer, inspect as sa_inspect

    log_message("Resetting sequences for all integer-PK tables...")
    with local_engine.connect() as conn:
        for table in Base.metadata.sorted_tables:
            id_col = table.c.get("id")
            if id_col is None:
                continue
            if not isinstance(id_col.type, Integer):
                continue
            seq = conn.execute(text("SELECT pg_get_serial_sequence(:tbl, 'id')"), {"tbl": table.name}).scalar()
            if not seq:
                continue
            conn.execute(text(f"SELECT setval('{seq}', COALESCE((SELECT MAX(id) FROM {table.name}), 1))"))
            log_message(f"  Reset sequence for {table.name} ({seq})", to_console=False)
        conn.commit()
    log_message("Sequence reset complete.")


if __name__ == "__main__":
    sync_data()
