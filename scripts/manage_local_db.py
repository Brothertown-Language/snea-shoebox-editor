# Copyright (c) 2026 Brothertown Language
import pgserver
import os
import sys
import argparse
from pathlib import Path

# Use a directory in the project root for the local database
DB_PATH = Path(__file__).parent.parent / "tmp" / "local_db"

def start_db():
    """Start the local PostgreSQL instance."""
    DB_PATH.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting local PostgreSQL at {DB_PATH}...")
    pg = pgserver.get_server(str(DB_PATH))
    
    # pgserver.get_server() automatically starts the server if it's not running
    conn_uri = pg.get_uri()
    
    print(f"Database is running!")
    print(f"Connection URI: {conn_uri}")
    print("\nTo use this with the app, set the following environment variable:")
    print(f"export DATABASE_URL=\"{conn_uri}\"")
    print("\nOr update your .streamlit/secrets.toml [connections.postgresql] url.")
    
    return pg

def stop_db():
    """Stop the local PostgreSQL instance."""
    if DB_PATH.exists():
        pg = pgserver.get_server(str(DB_PATH))
        pg.cleanup()
        print("Local PostgreSQL stopped and cleaned up.")
    else:
        print("No local database directory found.")

def status_db():
    """Check the status of the local PostgreSQL instance."""
    if DB_PATH.exists():
        pg = pgserver.get_server(str(DB_PATH))
        # pgserver doesn't have a direct 'is_running' but we can check the pid file or try to get uri
        try:
            uri = pg.get_uri()
            print(f"Local PostgreSQL is RUNNING at {uri}")
        except Exception:
            print("Local PostgreSQL is NOT running.")
    else:
        print("Local PostgreSQL directory does not exist.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage local PostgreSQL instance using pgserver.")
    parser.add_argument("action", choices=["start", "stop", "status"], help="Action to perform")
    
    args = parser.parse_args()
    
    if args.action == "start":
        start_db()
        print("\nPress Ctrl+C to exit this script. Note: pgserver may keep the DB running")
        print("in the background until 'stop' is called or the process is cleaned up.")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")
    elif args.action == "stop":
        stop_db()
    elif args.action == "status":
        status_db()
