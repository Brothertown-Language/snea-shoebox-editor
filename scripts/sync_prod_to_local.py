# Copyright (c) 2026 Brothertown Language
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
import src.database.models  # Import models to register them with Base.metadata


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
    # Start fresh log for each run
    if LOG_FILE.exists():
        LOG_FILE.unlink()
    log_message("Starting Production to Local Sync...")

    prod_url, local_url = load_secrets()

    if not prod_url:
        log_message("Error: Production DATABASE_URL not found in environment or .streamlit/secrets.toml.production")
        sys.exit(1)

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
    # sorted_tables uses topological sort based on ForeignKey relationships
    tables = Base.metadata.sorted_tables

    prod_session_factory = sessionmaker(bind=prod_engine)
    local_session_factory = sessionmaker(bind=local_engine)

    try:
        with prod_session_factory() as prod_session, local_session_factory() as local_session:
            log_message("Starting data sync...")

            # 2. Clear local data in reverse dependency order to respect FKs
            log_message("Clearing local data (reverse order)...")
            for table in reversed(tables):
                log_message(f"Deleting table: {table.name}", to_console=False)
                local_session.execute(table.delete())
            local_session.commit()

            # 3. Iterate in dependency order for insertion
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
    except Exception:
        error_trace = traceback.format_exc()
        log_message(f"CRITICAL ERROR during sync:\n{error_trace}")
        sys.exit(1)


if __name__ == "__main__":
    sync_data()
